#!/usr/bin/env python
"""Track how benefit descriptions changed over time (multi-label, keyword-based).

Benefits live in job_listing + benefits_perks chunks as concrete, multi-valued lists (a
listing names gym AND fertility AND 401k AND PTO at once), so this is multi-label keyword
matching — each chunk can hit several categories — not a single-register classifier.
Family/caregiving is a standard benefit; fertility is split out and dual-flagged as a DEI
signal (the more DEI-coded reproductive perk). Reports per-year prevalence (share of
benefit-bearing chunks mentioning a category) + 3-yr smoothing; self-presentation only.

Writes web/public/data/stories/benefits.json + data/benefits_trends.md (review).
"""

from __future__ import annotations

import re
from collections import defaultdict

from lowork.config import ROOT, company_dir
from lowork.io import read_json, load_all_chunks, write_json

COMPANIES = ["google", "amazon", "meta", "palantir", "coinbase", "netflix",
             "shopify", "stripe", "airbnb", "brex", "snap"]
SCAN_LABELS = {"job_listing", "benefits_perks"}
START_YEAR = 2011

# (id, label, deiSignal, pattern)
CATEGORIES = [
    ("health", "Health insurance", False,
     r"health(?:care)?|medical|dental|vision|\binsurance\b"),
    ("mental_health", "Mental health / wellness", False,
     r"mental health|well[- ]?being|wellness|therapy|counsel|meditation|headspace|\bEAP\b"),
    ("fitness", "Fitness", False,
     r"\bgym\b|fitness|peloton|wellness stipend"),
    ("family_caregiving", "Family / caregiving", False,
     r"parental leave|maternity|paternity|childcare|child care|adoption|family leave|"
     r"caregiv|nursing (?:room|mother)|baby bonding"),
    ("fertility", "Fertility", True,
     r"fertilit|\bIVF\b|egg freezing|surrogacy|family planning|reproductive (?:health|benefit)"),
    ("time_off", "Time off", False,
     r"\bPTO\b|paid time off|unlimited (?:vacation|pto|time off)|sabbatical|paid leave"),
    ("flexibility", "Flexibility / remote", False,
     r"\bremote\b|work from (?:home|anywhere)|hybrid|flexible (?:schedule|work|hours)|"
     r"work[- ]life"),
    ("financial", "Financial / equity", False,
     r"401\(?k\)?|\bequity\b|stock options?|\bRSUs?\b|retirement|\bbonus\b|matching"),
    ("food", "Food / perks", False,
     r"free (?:lunch|food|meals?|snacks)|catered|on[- ]site (?:cafe|meals|kitchen)|snacks"),
    ("learning", "Learning / development", False,
     r"tuition|learning (?:budget|stipend)|professional development|conference budget|"
     r"education(?:al)? (?:budget|stipend|reimbursement)"),
]


def _smooth(series: dict[int, float]) -> dict[int, float]:
    ys = sorted(series)
    out = {}
    for i, y in enumerate(ys):
        w = [series[ys[j]] for j in range(max(0, i - 1), min(len(ys), i + 2))]
        out[y] = sum(w) / len(w)
    return out


def main() -> None:
    pats = [(cid, label, dei, re.compile(p, re.I)) for cid, label, dei, p in CATEGORIES]
    total_by_year: dict[int, int] = defaultdict(int)
    hits_by_year: dict[str, dict[int, int]] = {cid: defaultdict(int) for cid, *_ in CATEGORIES}

    for c in COMPANIES:
        clsp = company_dir(c) / "classifications.json"
        if not clsp.exists():
            continue
        cls = read_json(clsp)
        for ch in load_all_chunks(company_dir(c) / "chunks"):
            if cls.get(ch["chunk_id"]) not in SCAN_LABELS:
                continue
            y = int(ch["year"])
            if y < START_YEAR:
                continue
            total_by_year[y] += 1
            t = re.sub(r"<[^>]+>", " ", ch["text"])
            for cid, _label, _dei, rx in pats:
                if rx.search(t):
                    hits_by_year[cid][y] += 1

    years = sorted(total_by_year)
    categories = []
    for cid, label, dei, _rx in pats:
        share = {y: hits_by_year[cid].get(y, 0) / total_by_year[y] for y in years if total_by_year[y]}
        sm = _smooth(share)
        series = [{"year": y, "share": round(share[y], 4), "count": hits_by_year[cid].get(y, 0),
                   "smoothed": round(sm[y], 4)} for y in years]
        nonzero = [y for y in years if share.get(y, 0) > 0]
        categories.append({
            "id": cid, "label": label, "deiSignal": dei,
            "series": series,
            "total": sum(hits_by_year[cid].values()),
            "firstYear": min(nonzero) if nonzero else None,
            "peakYear": max(share, key=share.get) if share else None,
        })
    categories.sort(key=lambda c: -c["total"])

    out = {
        "story": "benefits",
        "title": "How the perks changed",
        "subtitle": "Which benefits companies advertised, and how the list shifted over time.",
        "intro": ("Benefit categories mentioned in job listings and benefits copy across 11 "
                  "companies, as a share of postings per year. Multi-label (a listing names "
                  "several). Fertility is also a DEI signal. Keyword-based and uneven "
                  "year to year — read the shapes, not the exact values."),
        "caveat": ("Self-presentation (what's advertised, not provided); keyword presence "
                   "misses paraphrase; coverage is thin/uneven per year (n shown). Trends, "
                   "not precise counts."),
        "years": years,
        "totalsByYear": {str(y): total_by_year[y] for y in years},
        "categories": categories,
    }
    out_dir = ROOT / "web" / "public" / "data" / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "benefits.json", out)

    # review md
    lines = [f"# Benefits trends ({years[0]}–{years[-1]}, n={sum(total_by_year.values())} job/benefits chunks)", ""]
    for c in categories:
        flag = " [DEI]" if c["deiSignal"] else ""
        spark = " ".join(f"{s['year']%100:02d}:{int(s['share']*100)}" for s in c["series"] if s["count"])
        lines.append(f"- **{c['label']}**{flag} (n={c['total']}, first {c['firstYear']}, peak {c['peakYear']}): {spark}")
    (ROOT / "data" / "benefits_trends.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote benefits.json + benefits_trends.md ({len(categories)} categories, {years[0]}–{years[-1]})")
    for c in categories:
        print(f"  {c['label']:26s}{'[DEI]' if c['deiSignal'] else '     '} n={c['total']:3d} first={c['firstYear']} peak={c['peakYear']}")


if __name__ == "__main__":
    main()
