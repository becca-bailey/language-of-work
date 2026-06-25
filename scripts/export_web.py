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

    # Altruism is cleaned: techno-optimism (product hype) is split out so the
    # per-company line tracks genuine "change the world" mission, not "we build
    # amazing technology". n==0 years (no world-changing language) are dropped as
    # absences rather than imputed, so the detail chart matches the story line.
    split_path = cdir / "altruism_split.parquet"
    split_df = pd.read_parquet(split_path) if split_path.exists() else None
    split_quotes = (
        read_json(cdir / "altruism_split_quotes.json")
        if (cdir / "altruism_split_quotes.json").exists()
        else {}
    )

    exported_axes: list[str] = []
    for axis in scores["axis"].unique():
        sub = scores[(scores["axis"] == axis) & (scores["level"] == LEVEL)].sort_values("year")
        axis_quotes = quotes.get(axis, {}).get(LEVEL, {})

        if axis == "altruism" and split_df is not None:
            wq = split_quotes.get("worldChanging", {})
            years = [
                {
                    "year": int(r.year),
                    "zscore": round(float(r.world_zscore), 4),
                    "rawTopkMean": round(float(r.world_topk), 4),
                    "nChunks": int(r.world_n),
                    "kUsed": min(int(r.world_n), TOP_K),
                    "thin": int(r.world_n) < TOP_K,
                    "carriedForwardFrac": None,
                    "technoShare": round(float(r.techno_share), 4),
                    "quotes": wq.get(str(int(r.year)), []),
                }
                for r in split_df.sort_values("year").itertuples()
                if int(r.world_n) > 0 and pd.notna(r.world_zscore)
            ]
        else:
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
