#!/usr/bin/env python
"""Export AI mention + framing data for the web frontend.

Per company: astro/src/data/<company>/ai.json (mention prevalence by year and
label, tool<->mandate projections by register group, evidence chunks).
With --aggregate: astro/src/data/stories/ai.json (pooled prevalence timeline +
per-company series + pooled talk-vs-hire balance) across all companies that
have ai_mentions.json.

No story page consumes these yet (wellbeing precedent: dataset first); the
explore page and a future story both read from here.
"""

from __future__ import annotations

import argparse
from collections import defaultdict

import pandas as pd

from lowork.company import CompanyProfile
from lowork.config import DATA_DIR, WEB_DATA_DIR, company_dir
from lowork.io import read_json, write_json


def export_company(company: str) -> None:
    profile = CompanyProfile.load(company)
    cdir = company_dir(company)
    mentions = read_json(cdir / "ai_mentions.json")

    scores_path = cdir / "ai_language_scores.parquet"
    projections: dict[int, list[dict]] = defaultdict(list)
    if scores_path.exists():
        df = pd.read_parquet(scores_path)
        for r in df.itertuples():
            projections[int(r.year)].append({
                "group": r.group,
                "meanProjection": round(float(r.mean_projection), 4),
                "nChunks": int(r.n_chunks),
                "thin": bool(r.thin),
            })
    evidence_path = cdir / "ai_evidence.json"
    evidence = read_json(evidence_path).get("years", {}) if evidence_path.exists() else {}

    years = []
    for y in mentions["years"]:
        years.append({
            "year": y["year"],
            "totalChunks": y["total_chunks"],
            "aiChunks": y["ai_chunks"],
            "prevalence": y["prevalence"],
            "thin": y["thin"],
            "labels": y["labels"],
            "terms": y["terms"],
            "projections": projections.get(y["year"], []),
            "quotes": evidence.get(str(y["year"]), []),
        })

    out = WEB_DATA_DIR / company / "ai.json"
    write_json(out, {
        "company": company,
        "displayName": profile.display_name,
        "axis": "ai",
        "caveat": (
            "Framing projections have ~4 years of real signal by construction; "
            "per-company timing is not comparable until corpus gaps are filled."
        ),
        "years": years,
    })
    print(f"Wrote {out} ({len(years)} years)")


def export_aggregate() -> None:
    pooled: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    balance: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # group -> [ai, total]
    companies = []
    for path in sorted(DATA_DIR.glob("*/ai_mentions.json")):
        data = read_json(path)
        company = data["company"]
        series = []
        for y in data["years"]:
            pooled[y["year"]][0] += y["ai_chunks"]
            pooled[y["year"]][1] += y["total_chunks"]
            for label, counts in y["labels"].items():
                group = "talk" if label in ("mission_brand", "employee_story") else (
                    "hire" if label == "job_listing" else "other")
                balance[group][0] += counts["ai_chunks"]
                balance[group][1] += counts["chunks"]
            series.append({
                "year": y["year"], "prevalence": y["prevalence"],
                "aiChunks": y["ai_chunks"], "thin": y["thin"],
            })
        companies.append({"id": company, "years": series})

    out = WEB_DATA_DIR / "stories" / "ai.json"
    write_json(out, {
        "story": "ai",
        "pooled": [
            {"year": year, "aiChunks": ai, "totalChunks": total,
             "prevalence": round(ai / total, 4) if total else None}
            for year, (ai, total) in sorted(pooled.items())
        ],
        "talkVsHire": {
            group: {"aiChunks": ai, "totalChunks": total,
                    "prevalence": round(ai / total, 4) if total else None}
            for group, (ai, total) in sorted(balance.items())
        },
        "companies": companies,
    })
    print(f"Wrote {out} ({len(companies)} companies)")


def main(company: str | None = None, aggregate: bool = False) -> None:
    """Pipeline entry point: per-company export and/or the global aggregate."""
    if company:
        export_company(company)
    if aggregate:
        export_aggregate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company")
    parser.add_argument("--aggregate", action="store_true")
    args = parser.parse_args()
    if not args.company and not args.aggregate:
        parser.error("pass --company and/or --aggregate")
    main(args.company, args.aggregate)
