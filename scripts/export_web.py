#!/usr/bin/env python
"""Step 9b: export sentence-level pipeline output for the Next.js frontend.

Writes web/public/data/<company>/<axis>.json — one year series per axis,
sentence-level only (the default analysis granularity).
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.company import CompanyProfile
from lowork.config import ROOT, TOP_K, company_dir
from lowork.io import read_json, write_json

LEVEL = "sentence"


def update_companies_manifest(company: str, axes: list[str]) -> None:
    """Merge this company's export into web/public/data/companies.json."""
    manifest_path = ROOT / "web" / "public" / "data" / "companies.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
    else:
        manifest = {"companies": []}

    profile = CompanyProfile.load(company)
    entry = {
        "id": company,
        "displayName": profile.display_name,
        # control is an overlay on other axes, not a standalone analysis
        "axes": sorted(a for a in axes if a != "control"),
    }
    companies = [c for c in manifest["companies"] if c["id"] != company]
    companies.append(entry)
    companies.sort(key=lambda c: c["displayName"])
    write_json(manifest_path, {"companies": companies})
    print(f"Updated {manifest_path}")


def main(company: str) -> None:
    profile = CompanyProfile.load(company)
    cdir = company_dir(company)
    scores = pd.read_parquet(cdir / "axis_scores.parquet")
    quotes = read_json(cdir / "evidence_quotes.json")
    out_dir = ROOT / "web" / "public" / "data" / company

    exported_axes: list[str] = []
    for axis in scores["axis"].unique():
        sub = scores[(scores["axis"] == axis) & (scores["level"] == LEVEL)].sort_values("year")
        axis_quotes = quotes.get(axis, {}).get(LEVEL, {})
        years = [
            {
                "year": int(r.year),
                "zscore": round(float(r.zscore), 4),
                "rawTopkMean": round(float(r.raw_topk_mean), 4),
                "nChunks": int(r.n_chunks),
                "kUsed": int(r.k_used),
                "thin": int(r.n_chunks) < TOP_K,
                "carriedForwardFrac": None,
                "quotes": axis_quotes.get(str(int(r.year)), []),
            }
            for r in sub.itertuples()
        ]
        write_json(
            out_dir / f"{axis}.json",
            {"company": company, "displayName": profile.display_name, "axis": axis, "years": years},
        )
        exported_axes.append(axis)
        print(f"Wrote {out_dir / f'{axis}.json'} ({len(years)} years, {LEVEL})")

    update_companies_manifest(company, exported_axes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
