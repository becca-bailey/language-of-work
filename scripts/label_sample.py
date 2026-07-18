#!/usr/bin/env python
"""Emit a chunk sample for hand-labeling (manual step M3).

Writes data/<company>/labels/sample.csv with an empty `label` column.
Fill it in with one of: mission_brand, job_listing, benefits_perks,
process_logistics, legal_boilerplate, navigation_junk.

Default is a uniform random sample. --by-predicted stratifies by the model's
predicted label (requires classifications.json): ~70% is an even quota per
predicted class, so rare classes — the ones agreement stats are most sensitive
to — actually show up instead of being swamped by the majority class; the
remaining ~30% is uniform, since pure prediction-strata can never surface
chunks the model mislabels INTO a majority class.
"""

from __future__ import annotations

import argparse
import random

import pandas as pd

from lowork.config import CHUNK_LABELS, company_dir
from lowork.io import load_all_chunks, read_json


def stratified_sample(chunks: list[dict], predictions: dict[str, str],
                      n: int, rng: random.Random) -> list[dict]:
    by_pred: dict[str, list[dict]] = {}
    for c in chunks:
        pred = predictions.get(c["chunk_id"])
        if pred:
            by_pred.setdefault(pred, []).append(c)
    # ~70% even quota per predicted class, ~30% uniform: pure prediction-strata
    # can never surface chunks the model mislabels INTO the majority class.
    quota = max(1, int(n * 0.7) // len(by_pred))
    sample: list[dict] = []
    for label in sorted(by_pred):
        sample.extend(rng.sample(by_pred[label], min(quota, len(by_pred[label]))))
    if len(sample) < n:
        seen = {c["chunk_id"] for c in sample}
        rest = [c for pool in by_pred.values() for c in pool if c["chunk_id"] not in seen]
        sample.extend(rng.sample(rest, min(n - len(sample), len(rest))))
    return sample


def main(company: str, n: int, seed: int, by_predicted: bool, force: bool) -> None:
    cdir = company_dir(company)
    out = cdir / "labels" / "sample.csv"
    if out.exists() and not force:
        raise SystemExit(f"{out} exists — refusing to overwrite hand labels (use --force)")
    chunks = load_all_chunks(cdir / "chunks")
    if not chunks:
        raise SystemExit("No chunks found — run extract_chunks.py first")

    rng = random.Random(seed)
    if by_predicted:
        predictions = read_json(cdir / "classifications.json")
        sample = stratified_sample(chunks, predictions, n, rng)
    else:
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
    out.parent.mkdir(exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} chunks to {out}"
          + (" (stratified by predicted label)" if by_predicted else ""))
    print(f"Valid labels: {', '.join(CHUNK_LABELS)}")
    print("Fill in the `label` column (manual step M3), then run classify_chunks.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("-n", type=int, default=90)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--by-predicted", action="store_true",
                        help="Stratify by predicted label (even quota per class)")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite an existing labels/sample.csv")
    args = parser.parse_args()
    main(args.company, args.n, args.seed, args.by_predicted, args.force)
