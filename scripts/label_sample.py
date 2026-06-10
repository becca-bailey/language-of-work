#!/usr/bin/env python
"""Step 3a: emit a random chunk sample for hand-labeling (manual step M3).

Writes data/<company>/labels/sample.csv with an empty `label` column.
Fill it in with one of: mission_brand, job_listing, benefits_perks,
process_logistics, legal_boilerplate, navigation_junk.
"""

from __future__ import annotations

import argparse
import random

import pandas as pd

from lowork.config import CHUNK_LABELS, company_dir
from lowork.io import load_all_chunks


def main(company: str, n: int, seed: int) -> None:
    cdir = company_dir(company)
    chunks = load_all_chunks(cdir / "chunks")
    if not chunks:
        raise SystemExit("No chunks found — run extract_chunks.py first")

    rng = random.Random(seed)
    sample = rng.sample(chunks, min(n, len(chunks)))
    df = pd.DataFrame(
        [
            {
                "chunk_id": c["chunk_id"],
                "year": c["year"],
                "heading": c["heading"],
                "text": c["text"],
                "label": "",
            }
            for c in sample
        ]
    )
    out = cdir / "labels" / "sample.csv"
    out.parent.mkdir(exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} chunks to {out}")
    print(f"Valid labels: {', '.join(CHUNK_LABELS)}")
    print("Fill in the `label` column (manual step M3), then run classify_chunks.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("-n", type=int, default=90)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    main(args.company, args.n, args.seed)
