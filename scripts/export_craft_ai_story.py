#!/usr/bin/env python
"""Export the craft-ai story dataset: does craft language trade off against AI language?

Combines per-company craft axis scores (axis_scores.parquet, chunk level) with the AI
mention tracker (ai_mentions.json) into astro/src/data/stories/craft-ai.json.

The headline stats (Spearman on deltas and on levels) are computed here so the story
copy cites reproducible numbers. Pre/post windows: 2015-2021 (pre-surge) vs 2024-2026
(surge era). Coverage-hole companies carry a coverageNote that the charts surface.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from lowork.company import CompanyProfile
from lowork.config import WEB_DATA_DIR, company_dir, load_companies
from lowork.io import read_json, write_json

PRE_YEARS = range(2015, 2022)
POST_YEARS = range(2024, 2027)

# Coverage caveats that must travel with the data (charts render these).
COVERAGE_NOTES = {
    "nvidia": "2019 and 2021-23 have no captured pages — the deep-learning boom years "
              "are a coverage hole, so trend deltas are unreliable.",
    "meta": "Recent years are thinly captured (2026: 11 chunks); the high AI share is "
            "real for the captured pages but rests on small n.",
    "uber": "2020-23 and 2025-26 are SPA-era coverage holes; post-2019 trends are "
            "unmeasurable until manual capture.",
}


def company_block(company: str) -> dict | None:
    cdir = company_dir(company)
    ax_path = cdir / "axis_scores.parquet"
    ai_path = cdir / "ai_mentions.json"
    if not ax_path.exists() or not ai_path.exists():
        return None
    ax = pd.read_parquet(ax_path)
    craft = ax[(ax["axis"] == "craft") & (ax["level"] == "chunk")].sort_values("year")
    if craft.empty:
        return None
    ai_years = {y["year"]: y for y in read_json(ai_path)["years"]}

    craft_series = [
        {
            "year": int(r.year),
            "zscore": round(float(r.zscore), 4),
            "raw": round(float(r.raw_topk_mean), 4),
            "nChunks": int(r.n_chunks),
            "thin": bool(r.n_chunks < 5),
        }
        for r in craft.itertuples()
    ]
    ai_series = [
        {
            "year": y["year"],
            "prevalence": y["prevalence"],
            "aiChunks": y["ai_chunks"],
            "thin": y["thin"],
        }
        for y in sorted(ai_years.values(), key=lambda y: y["year"])
    ]

    craft_by_year = craft.set_index("year")["raw_topk_mean"]

    def craft_mean(years) -> float | None:
        v = craft_by_year.reindex(years).dropna()
        return round(float(v.mean()), 4) if len(v) else None

    def ai_prev(years) -> float | None:
        ai = sum(ai_years[y]["ai_chunks"] for y in years if y in ai_years)
        total = sum(ai_years[y]["total_chunks"] for y in years if y in ai_years)
        return round(ai / total, 4) if total else None

    craft_pre, craft_post = craft_mean(PRE_YEARS), craft_mean(POST_YEARS)
    ai_pre, ai_post = ai_prev(PRE_YEARS), ai_prev(POST_YEARS)
    return {
        "id": company,
        "displayName": CompanyProfile.load(company).display_name,
        "craftSeries": craft_series,
        "aiSeries": ai_series,
        "craftPre": craft_pre,
        "craftPost": craft_post,
        "aiPost": ai_post,
        "dCraft": round(craft_post - craft_pre, 4)
        if craft_pre is not None and craft_post is not None else None,
        "dAi": round(ai_post - ai_pre, 4)
        if ai_pre is not None and ai_post is not None else None,
        "coverageNote": COVERAGE_NOTES.get(company),
    }


def main(companies: list[str]) -> None:
    pairs = [b for b in (company_block(c) for c in companies) if b]

    scatter = [
        {
            "id": p["id"],
            "displayName": p["displayName"],
            "craft": p["craftPost"],
            "ai": p["aiPost"],
            "flagged": p["coverageNote"] is not None,
            "note": p["coverageNote"],
        }
        for p in pairs
        if p["craftPost"] is not None and p["aiPost"] is not None
    ]

    # Industry overview: unweighted company-mean craft + pooled AI prevalence per year.
    craft_by_year: dict[int, list[float]] = {}
    for p in pairs:
        for r in p["craftSeries"]:
            craft_by_year.setdefault(r["year"], []).append(r["raw"])
    ai_totals: dict[int, list[int]] = {}
    for c in companies:
        path = company_dir(c) / "ai_mentions.json"
        if not path.exists():
            continue
        for y in read_json(path)["years"]:
            t = ai_totals.setdefault(y["year"], [0, 0])
            t[0] += y["ai_chunks"]
            t[1] += y["total_chunks"]
    pooled = [
        {
            "year": year,
            "craftMean": round(float(np.mean(craft_by_year[year])), 4)
            if year in craft_by_year else None,
            "aiPrevalence": round(ai / total, 4) if total else None,
            "nCompanies": len(craft_by_year.get(year, [])),
        }
        for year, (ai, total) in sorted(ai_totals.items())
    ]

    deltas = [(p["dCraft"], p["dAi"]) for p in pairs
              if p["dCraft"] is not None and p["dAi"] is not None]
    levels = [(s["craft"], s["ai"]) for s in scatter]
    rho_d, p_d = spearmanr([d[0] for d in deltas], [d[1] for d in deltas])
    rho_l, p_l = spearmanr([l[0] for l in levels], [l[1] for l in levels])

    out = WEB_DATA_DIR / "stories" / "craft-ai.json"
    write_json(out, {
        "story": "craft-ai",
        "windows": {"pre": [2015, 2021], "post": [2024, 2026]},
        "stats": {
            "deltas": {"rho": round(float(rho_d), 3), "p": round(float(p_d), 3), "n": len(deltas)},
            "levels": {"rho": round(float(rho_l), 3), "p": round(float(p_l), 3), "n": len(levels)},
        },
        "pairs": pairs,
        "scatter": scatter,
        "pooled": pooled,
    })
    print(f"Wrote {out} ({len(pairs)} companies; "
          f"deltas rho={rho_d:+.2f} p={p_d:.2f}, levels rho={rho_l:+.2f} p={p_l:.2f})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--companies", default="")
    args = parser.parse_args()
    companies = [c.strip() for c in args.companies.split(",") if c.strip()] or load_companies()
    main(companies)
