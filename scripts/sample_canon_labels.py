#!/usr/bin/env python
"""Project-3 step: emit a register-stratified chunk sample for hand-labeling.

Canon lives only in firm text, which is far outnumbered by worker chunks
(~565 vs ~1469 for Automattic), so a flat random sample would barely test canon
detection. This stratifies *equally* across the registers present, capped at
availability, so the validation gate actually exercises the canon/on_topic/junk
boundary. Writes data/<case>/labels/canon_sample.csv with an empty `label`
column to fill in by hand, then run classify_canon.py --validate-only.
"""

from __future__ import annotations

import argparse
import random
from collections import defaultdict

import pandas as pd

from lowork.config import CANON_LABELS, company_dir
from lowork.io import load_all_chunks


def main(case: str, n: int, seed: int) -> None:
    cdir = company_dir(case)
    chunks = load_all_chunks(cdir / "chunks")
    if not chunks:
        raise SystemExit("No chunks found — run fetch_case.py first")

    by_reg: dict[str, list[dict]] = defaultdict(list)
    for c in chunks:
        by_reg[c.get("register", "?")].append(c)

    rng = random.Random(seed)
    per_reg = max(1, n // len(by_reg))
    sample: list[dict] = []
    for reg, items in sorted(by_reg.items()):
        take = min(per_reg, len(items))
        sample.extend(rng.sample(items, take))
        print(f"  {reg}: {take}/{len(items)} sampled")

    rng.shuffle(sample)
    df = pd.DataFrame(
        [
            {
                "chunk_id": c["chunk_id"],
                "register": c.get("register", ""),
                "year": c["year"],
                "canon_url": c.get("provenance", {}).get("canon_url", ""),
                "heading": c["heading"],
                "text": c["text"],
                "label": "",
            }
            for c in sample
        ]
    )
    out = cdir / "labels" / "canon_sample.csv"
    out.parent.mkdir(exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\nWrote {len(df)} chunks to {out}")
    print(f"Valid labels: {', '.join(CANON_LABELS)}")
    print("Fill in the `label` column, then run classify_canon.py --validate-only")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    p.add_argument("-n", type=int, default=120)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    main(args.case, args.n, args.seed)
