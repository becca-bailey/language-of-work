#!/usr/bin/env python
"""Assemble the Menlo case-study story JSON from computed artifacts.

Reuses what the pipeline already produced — axis_scores.parquet + evidence_quotes.json
(canon idealism line + top quotes), menlo_phrases.json (branded vocabulary), and
sources.json (events) — and recomputes the impact-claim denominator audit. Writes
astro/src/data/stories/menlo.json.

Three-act story (see docs/menlo-story-outline.md):
  Act 1 the belief · Act 2 the megaphone · Act 3 the echo that never came.
"""

from __future__ import annotations

import glob
import json
import re

import pandas as pd

from lowork.config import WEB_DATA_DIR, ROOT, company_dir
from lowork.io import read_json, write_json

ERAS = [
    (2006, 2012, "Founding"),
    (2013, 2018, "Books era"),
    (2019, 2023, "Mature / COVID"),
    (2024, 2026, "Recent"),
]

# Impact-claim denominator audit — how Menlo counts "impact" (see impact_audit.md).
AUDIT_PATTERNS = {
    "books / speaking / teaching": re.compile(
        r"\b(book|keynote|speak|workshop|teach|class|conference|stage)\b", re.I),
    "tours / visitors": re.compile(r"\b(visitor|tour|came to visit|toured|guests?)\b", re.I),
    "reach / ripple / influence": re.compile(
        r"\b(ripple|influenc|inspir|movement|share our|spread|change the world|reach)\b", re.I),
    "named adopter (the test)": re.compile(
        r"\b(other compan\w+ (?:that )?(?:adopted|use|rebuilt)|replicat\w*|"
        r"rolled out the menlo|implemented the menlo way)\b", re.I),
}


def era_of(year: int) -> str:
    for lo, hi, name in ERAS:
        if lo <= year <= hi:
            return name
    return "Recent"


def load_firm_chunks() -> list[dict]:
    rows = []
    for f in glob.glob(str(company_dir("menlo") / "chunks" / "*.jsonl")):
        for line in open(f):
            rows.append(json.loads(line))
    return rows


def idealism_series(cdir) -> tuple[list[dict], dict]:
    """Per-year canon idealism (raw projection + z), with top quote, era-tagged."""
    df = pd.read_parquet(cdir / "axis_scores.parquet")
    a = df[(df.axis == "altruism") & (df.level == "sentence")].sort_values("year")
    quotes = read_json(cdir / "evidence_quotes.json").get("altruism", {}).get("sentence", {})
    series = []
    for r in a.itertuples():
        yr = int(r.year)
        top = (quotes.get(str(yr)) or [{}])[0]
        series.append({
            "year": yr,
            "era": era_of(yr),
            "idealism": round(float(r.raw_topk_mean), 4),  # peak idealism (top-k mean)
            "zscore": round(float(r.zscore), 4),
            "nSentences": int(r.n_chunks),
            "thin": int(r.n_chunks) < 5,
            "topQuote": {"text": top.get("text", ""), "heading": top.get("heading", "")},
        })
    # era summary (mean of per-year peak idealism, robust years weighted by N)
    era_rows = []
    for lo, hi, name in ERAS:
        pts = [s for s in series if lo <= s["year"] <= hi]
        if not pts:
            continue
        n = sum(p["nSentences"] for p in pts)
        wmean = sum(p["idealism"] * p["nSentences"] for p in pts) / n if n else 0
        era_rows.append({
            "era": name, "fromYear": lo, "toYear": hi,
            "idealism": round(wmean, 4), "nSentences": n,
            "years": [p["year"] for p in pts],
        })
    return series, {"eras": era_rows}


def cohort_series() -> list[dict]:
    """Cohort idealism z-trajectories from the altruism story, for the overlay.

    Uses the same cleaned "world-changing" series the other idealism pages show
    (techno-optimism removed), so the cohort here matches those pages exactly.
    Z within company, so the comparison is of shape and timing, not absolute level.
    """
    path = WEB_DATA_DIR / "stories" / "altruism.json"
    if not path.exists():
        return []
    alt = read_json(path)
    out = []
    for c in alt.get("sources", {}).get("careers", {}).get("companies", []):
        # Prefer the cleaned world-changing series (what the other pages render).
        source = c.get("worldChanging") or c.get("years", [])
        years = [
            {"year": int(y["year"]), "zscore": round(float(y["zscore"]), 4)}
            for y in source
            if y.get("zscore") is not None
        ]
        if len(years) >= 2:
            out.append({"id": c["id"], "displayName": c["displayName"], "years": years})
    return out


def impact_audit(firm: list[dict]) -> dict:
    counts = {k: 0 for k in AUDIT_PATTERNS}
    raw_named = []
    for r in firm:
        for k, p in AUDIT_PATTERNS.items():
            if p.search(r["text"]):
                counts[k] += 1
                if k == "named adopter (the test)":
                    raw_named.append({"year": r["year"], "text": r["text"][:200]})
    # Manual review (see impact_audit.md): every raw "adopter" match is a false
    # positive — Menlo's own inspiration from Edison's Menlo Park, or end-users
    # adopting clients' software. 0 credible named-adopter claims.
    return {
        "counts": counts,
        "namedAdopterCredible": 0,
        "namedAdopterRawMatches": raw_named,
        "namedAdopterNote": (
            "Raw regex matches are all false positives on inspection (self-reference to "
            "Edison's Menlo Park; end-users adopting clients' software) — 0 credible "
            "claims of an organization that rebuilt its workplace on the Menlo Way."
        ),
        "finding": (
            "Across the full firm corpus, 0 credible claims of an organization that "
            "rebuilt its workplace on the Menlo Way. Impact is counted in tour visitors, "
            "book/keynote reach, and clients' product adoption — story-consumption, not "
            "practice-adoption. The replication market does not visibly clear."
        ),
        "guardrail": (
            "Absence of a documented/claimed adopter, not proof of zero influence. "
            "Claim stays: the replication market did not visibly clear."
        ),
    }


def outsider_view(firm_and_worker: list[dict]) -> list[dict]:
    """HN worker-register quotes — the 'admired rarity, paid curiosity' outside view."""
    keys = re.compile(
        r"few (?:companies )?(?:that |who )?get it|paying to learn|pay to learn|"
        r"Pivotal and Menlo|companies that get it|one of the few|pair", re.I)
    out = []
    seen = set()
    for r in firm_and_worker:
        if r.get("register") != "worker":
            continue
        t = r["text"]
        if not keys.search(t):
            continue
        clean = re.sub(r"<[^>]+>", "", t)  # strip HN HTML tags
        clean = clean.replace("&#x27;", "'").replace("&gt;", ">").replace("&quot;", '"')
        snippet = re.sub(r"\s+", " ", clean).strip()[:240]
        if snippet[:60] in seen:
            continue
        seen.add(snippet[:60])
        out.append({"year": r["year"], "text": snippet,
                    "url": r.get("source_url", "")})
    out.sort(key=lambda x: x["year"])
    return out[:8]


def main() -> None:
    cdir = company_dir("menlo")
    cfg = read_json(cdir / "sources.json")
    firm = [r for r in load_firm_chunks()]

    series, era_summary = idealism_series(cdir)
    phrases = read_json(cdir / "menlo_phrases.json").get("lexicons", {})

    out = {
        "story": "menlo",
        "title": "The Menlo Way",
        "subtitle": "A company that codified joy — and the influence that never came",
        "thesis": (
            "Menlo codified and broadcast a humane work culture more thoroughly than "
            "almost anyone — and that very codification (books, trademarks, paid tours) "
            "became the impact, a substitute for the propagation that never happened. "
            "The language is durable; the influence is boutique."
        ),
        "idealism": {
            "metricLabel": "Idealism (top-k mean projection onto idealism↔pragmatism)",
            "note": (
                "Canon register only (homepage + values pages + careers); blog excluded "
                "so the line tracks changing idealism, not a changing voice. Positive in "
                "every era and rising as the joy/'end human suffering' mission "
                "consolidated onto the homepage — it never collapses (unlike the cohort's "
                "idealism) and never hardens into performance/intensity language."
            ),
            "series": series,
            "eraSummary": era_summary["eras"],
            "cohort": cohort_series(),
        },
        "brandedLanguage": phrases,
        "events": cfg.get("events", []),
        "annotations": cfg.get("annotations", []),
        "impactAudit": impact_audit(firm),
        "outsiderView": outsider_view(firm),
    }
    out_dir = WEB_DATA_DIR / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "menlo.json", out)
    print(f"Wrote {out_dir / 'menlo.json'}")
    print(f"  idealism years={len(series)}  era summary={len(era_summary['eras'])}")
    print(f"  branded groups={list(phrases)}  events={len(out['events'])}")
    print(f"  audit named-adopters(credible)={out['impactAudit']['namedAdopterCredible']}  "
          f"outsider quotes={len(out['outsiderView'])}")


if __name__ == "__main__":
    main()
