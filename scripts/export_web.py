#!/usr/bin/env python
"""Step 9b: export sentence-level pipeline output for the Next.js frontend.

Writes web/public/data/<company>/<axis>.json — one year series per axis,
sentence-level only (the default analysis granularity).
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.config import ROOT, TOP_K, company_dir
from lowork.io import read_json, write_json

LEVEL = "sentence"


def main(company: str) -> None:
    cdir = company_dir(company)
    scores = pd.read_parquet(cdir / "axis_scores.parquet")
    quotes = read_json(cdir / "evidence_quotes.json")
    out_dir = ROOT / "web" / "public" / "data" / company

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
        write_json(out_dir / f"{axis}.json", {"company": company, "axis": axis, "years": years})
        print(f"Wrote {out_dir / f'{axis}.json'} ({len(years)} years, {LEVEL})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
