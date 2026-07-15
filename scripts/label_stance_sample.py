#!/usr/bin/env python
"""Emit a stance sample stratified by PREDICTED stance for hand-labeling.

Writes data/dei_labels/stance_sample.csv with an empty `stance` column —
the first hand-label validation path for the stance classifier, which until
now was only checked for register↔stance consistency, never against a human.

N chunks per predicted stance, pooled across every company with
dei_stances.json. Same caveat as the register sampler: agreement on a
stratified sample is a per-stance measure, not corpus-wide agreement.
Fill in the `stance` column, then run report_dei_agreement.py --task stance.
"""

from __future__ import annotations

import argparse
import random
from collections import defaultdict

import pandas as pd

from lowork.config import DATA_DIR
from lowork.dei_stance import DEI_STANCES
from lowork.io import load_all_chunks, read_json


def main(per_stance: int, seed: int) -> None:
    rng = random.Random(seed)
    out = DATA_DIR / "dei_labels" / "stance_sample.csv"
    existing_rows: list[dict] = []
    existing_ids: set[str] = set()
    if out.exists():
        prev = pd.read_csv(out, dtype={"stance": "string"})
        existing_rows = prev.to_dict("records")
        existing_ids = set(prev["chunk_id"])

    by_stance: dict[str, list[dict]] = defaultdict(list)
    for stance_path in sorted(DATA_DIR.glob("*/dei_stances.json")):
        company = stance_path.parent.name
        predictions = read_json(stance_path)
        chunks_dir = stance_path.parent / "chunks"
        if not chunks_dir.exists():
            continue
        for c in load_all_chunks(chunks_dir):
            pred = predictions.get(c["chunk_id"])
            if pred and c["chunk_id"] not in existing_ids:
                by_stance[pred].append({**c, "company": company})

    new_rows: list[dict] = []
    for stance in sorted(by_stance):
        pool = by_stance[stance]
        take = rng.sample(pool, min(per_stance, len(pool)))
        print(f"  {stance}: {len(take)} sampled (pool {len(pool)})")
        new_rows.extend(
            {
                "chunk_id": c["chunk_id"],
                "company": c["company"],
                "year": c["year"],
                "heading": c.get("heading", ""),
                "text": c["text"],
                "stance": "",
            }
            for c in take
        )

    rng.shuffle(new_rows)  # don't present the labeler with prediction-ordered blocks
    df = pd.DataFrame(existing_rows + new_rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows to {out} ({len(new_rows)} new)")
    print(f"Valid stances: {', '.join(DEI_STANCES)}")
    print("Fill in the `stance` column, then run report_dei_agreement.py --task stance")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", type=int, default=20, help="Chunks per predicted stance")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    main(args.n, args.seed)
