#!/usr/bin/env python
"""Step 9b: export pipeline output as static JSON for the Next.js frontend.

Writes web/public/data/<company>/<axis>.json with the year series, coverage
flags, carried-forward fractions, and evidence quotes.
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.config import ROOT, TOP_K, company_dir
from lowork.io import read_json, write_json


def main(company: str) -> None:
    cdir = company_dir(company)
    scores = pd.read_parquet(cdir / "axis_scores.parquet")
    quotes = read_json(cdir / "evidence_quotes.json")
    out_dir = ROOT / "web" / "public" / "data" / company

    for axis in scores["axis"].unique():
        sub = scores[scores["axis"] == axis].sort_values("year")
        years = [
            {
                "year": int(r.year),
                "zscore": round(float(r.zscore), 4),
                "rawTopkMean": round(float(r.raw_topk_mean), 4),
                "nChunks": int(r.n_chunks),
                "kUsed": int(r.k_used),
                "thin": int(r.n_chunks) < TOP_K,
                "carriedForwardFrac": None if pd.isna(r.carried_forward_frac)
                else float(r.carried_forward_frac),
                "quotes": quotes[axis][str(int(r.year))],
            }
            for r in sub.itertuples()
        ]
        write_json(out_dir / f"{axis}.json", {"company": company, "axis": axis, "years": years})
        print(f"Wrote {out_dir / f'{axis}.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
