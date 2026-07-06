#!/usr/bin/env python
"""Phase-0 feasibility audit for the well-being study — benefits-page coverage.

First producer of the three-state observation ledger (docs/wellbeing-execution-plan.md
Phase 3): data/<co>/wellbeing_observations.parquet, one row per company-year-page.

An "observation" here is a page that was fetched and yielded extractable benefits
content — i.e. a page whose chunks were classified benefits_perks or job_listing (the
two enumeration-bearing labels). Fetch metadata (status, thin flag, dom words) is joined
from snapshots.json where a capture matches the chunk's source_url + timestamp.

Ledger columns: company, year, final_url, fetch_status, extracted_word_count,
content_sane (bool), observed (bool). `observed` = content_sane AND the page carried
benefits/job content. Absence is NOT coded here — this audit records observed-present
pages only; observed-absent vs unobserved is resolved in Phase 3/4 against a target list.

Gate (pinned in the plan, §0.1): a company is USABLE = >=1 benefits-page observation in
>=4 distinct years, with >=1 observation on each side of 2022-01-01. Overall gate: >=8 of
16 companies usable, else redesign around HN "Who's Hiring".

Writes:
  data/<co>/wellbeing_observations.parquet   (per company)
  data/wellbeing_coverage.md                 (summary table + gate read, review artifact)

Read-only w.r.t. corpus; makes no network calls. Nothing downstream is triggered.
"""

from __future__ import annotations

import pandas as pd

from lowork.config import DATA_DIR, company_dir, load_companies
from lowork.io import load_all_chunks, read_json

BENEFITS_LABELS = {"benefits_perks", "job_listing"}
WORD_FLOOR = 20          # a page below this yielded no real content
PIVOT_YEAR = 2022        # substitution hypothesis boundary
MIN_YEARS = 4            # >=4 distinct observed years
GATE_N = 8               # >=8 of 16 usable


def _snapshot_index(company: str) -> dict[tuple[str, str], dict]:
    """(original_url, timestamp) -> capture, for joining fetch metadata onto chunks."""
    path = company_dir(company) / "snapshots.json"
    if not path.exists():
        return {}
    data = read_json(path)
    caps = data.get("captures", []) if isinstance(data, dict) else data
    idx = {}
    for c in caps:
        idx[(c.get("original", ""), str(c.get("timestamp", "")))] = c
    return idx


def audit_company(company: str) -> pd.DataFrame:
    chunks = load_all_chunks(company_dir(company) / "chunks")
    labels = read_json(company_dir(company) / "classifications.json")
    snaps = _snapshot_index(company)

    # Aggregate chunk-grain up to page grain: (year, source_url).
    pages: dict[tuple[int, str], dict] = {}
    for ch in chunks:
        cid = ch.get("chunk_id")
        label = labels.get(cid)
        if label not in BENEFITS_LABELS:
            continue
        year = ch.get("year")
        url = ch.get("source_url", "")
        if year is None:
            continue
        key = (int(year), url)
        p = pages.setdefault(key, {"words": 0, "timestamp": str(ch.get("timestamp", ""))})
        p["words"] += int(ch.get("word_count", 0) or 0)

    rows = []
    for (year, url), p in pages.items():
        cap = snaps.get((url, p["timestamp"]))
        if cap is not None:
            status = str(cap.get("statuscode", ""))
            thin = bool(cap.get("thin", False))
            dom_words = cap.get("coverage", {}).get("dom_words")
            words = int(dom_words) if dom_words is not None else p["words"]
        else:
            status = "chunked"   # produced chunks but no matched capture row
            thin = False
            words = p["words"]
        # Content-first: the page produced classified benefits chunks, so the fetch
        # succeeded. An empty/"chunked" status is a metadata gap, not a bad fetch — only
        # an explicit 3xx/4xx/5xx status vetoes. Sanity then rests on real word volume.
        is_error = status[:1] in ("3", "4", "5")
        content_sane = (not thin) and (words >= WORD_FLOOR) and not is_error
        rows.append({
            "company": company,
            "year": year,
            "final_url": url,
            "fetch_status": status,
            "extracted_word_count": words,
            "content_sane": content_sane,
            "observed": content_sane,
        })

    df = pd.DataFrame(rows).sort_values(["year", "final_url"]).reset_index(drop=True)
    out = company_dir(company) / "wellbeing_observations.parquet"
    df.to_parquet(out, index=False)
    return df


def gate_for(df: pd.DataFrame) -> dict:
    obs = df[df["observed"]] if not df.empty else df
    years = sorted(set(obs["year"].tolist())) if not obs.empty else []
    n_years = len(years)
    pre = any(y < PIVOT_YEAR for y in years)
    post = any(y >= PIVOT_YEAR for y in years)
    usable = (n_years >= MIN_YEARS) and pre and post
    return {
        "obs_pages": int(len(obs)),
        "n_years": n_years,
        "years": years,
        "pre_2022": pre,
        "post_2022": post,
        "usable": usable,
    }


def main() -> int:
    companies = load_companies()
    summary = []
    for co in companies:
        try:
            df = audit_company(co)
        except FileNotFoundError:
            df = pd.DataFrame()
            (company_dir(co) / "wellbeing_observations.parquet")  # noqa: no write on missing
        g = gate_for(df)
        g["company"] = co
        summary.append(g)

    usable_n = sum(1 for s in summary if s["usable"])
    gate_pass = usable_n >= GATE_N

    lines = [
        "# Well-Being Study — Phase 0 Coverage Audit",
        "",
        f"Universe: {len(companies)} companies. **Usable: {usable_n} / {len(companies)}** "
        f"(gate = >={GATE_N}).",
        "",
        f"**GATE {'PASS' if gate_pass else 'FAIL'}** — "
        + ("proceed with benefits-page enumeration."
           if gate_pass else "redesign around HN \"Who's Hiring\" postings (plan §0.1 branch)."),
        "",
        "Usable = >=1 benefits-page observation in >=4 distinct years, spanning 2022-01-01.",
        "Observation = page yielding benefits_perks/job_listing content, content_sane=true.",
        "",
        "| company | obs pages | years | span | pre-2022 | post-2022 | usable |",
        "|---|--:|--:|---|:--:|:--:|:--:|",
    ]
    for s in sorted(summary, key=lambda x: (not x["usable"], -x["n_years"])):
        yrs = s["years"]
        span = f"{yrs[0]}–{yrs[-1]}" if yrs else "—"
        lines.append(
            f"| {s['company']} | {s['obs_pages']} | {s['n_years']} | {span} "
            f"| {'✓' if s['pre_2022'] else '·'} | {'✓' if s['post_2022'] else '·'} "
            f"| {'**✓**' if s['usable'] else '✗'} |"
        )
    lines += ["", "_Per-company ledger: data/<co>/wellbeing_observations.parquet._", ""]

    out = DATA_DIR / "wellbeing_coverage.md"
    out.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
