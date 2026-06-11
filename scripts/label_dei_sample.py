#!/usr/bin/env python
"""Emit a stratified DEI register sample across companies for hand-labeling.

Writes data/dei_labels/sample.csv with empty `register` column.
Valid registers: explicit_demographic, structural_process, aspirational_vague,
belonging_culture, meritocracy, absent.

Use --append to keep existing labeled rows and add chunks from new companies only.
Use --refresh-company to add new chunks from one company (e.g. post-2018 era) while
keeping existing rows for that company.
Use --min-year to limit sampling to chunks from that year onward.
Use --companies to limit which companies are sampled (default: all in COMPANIES).
"""

from __future__ import annotations

import argparse
import random
from collections import defaultdict

import pandas as pd

from lowork.config import DATA_DIR, company_dir
from lowork.dei import DEI_REGISTERS
from lowork.io import load_all_chunks, read_json

COMPANIES = ["google", "amazon", "meta", "palantir"]
ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}


def main(
    n: int,
    seed: int,
    append: bool,
    companies: list[str],
    min_year: int | None,
    refresh_company: str | None,
) -> None:
    rng = random.Random(seed)
    out = DATA_DIR / "dei_labels" / "sample.csv"

    existing_ids: set[str] = set()
    existing_rows: list[dict] = []
    if out.exists() and (append or refresh_company):
        prev = pd.read_csv(out, dtype={"register": "string"})
        existing_ids = set(prev["chunk_id"])
        if refresh_company:
            existing_rows = prev[prev["company"] != refresh_company].to_dict("records")
            companies = [refresh_company]
        else:
            existing_rows = prev.to_dict("records")
            already = set(prev["company"].unique())
            companies = [c for c in companies if c not in already]
            if not companies:
                raise SystemExit("All requested companies already in sample.csv — nothing to append")

    by_bucket: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for company in companies:
        cdir = company_dir(company)
        chunks_dir = cdir / "chunks"
        if not chunks_dir.exists():
            print(f"Skipping {company}: no chunks (run extract first)")
            continue
        classifications = read_json(cdir / "classifications.json")
        for c in load_all_chunks(chunks_dir):
            if classifications.get(c["chunk_id"]) not in ANALYSIS_LABELS:
                continue
            if c["chunk_id"] in existing_ids:
                continue
            if min_year is not None and c["year"] < min_year:
                continue
            era = 1 if c["year"] < 2015 else (2 if c["year"] < 2020 else 3)
            by_bucket[(company, era)].append({**c, "company": company})

    if not by_bucket:
        raise SystemExit("No analysis chunks found for sampling")

    per_bucket = max(1, n // len(by_bucket))
    sample: list[dict] = []
    for bucket, pool in sorted(by_bucket.items()):
        sample.extend(rng.sample(pool, min(per_bucket, len(pool))))
    if len(sample) < n:
        remaining = [c for pool in by_bucket.values() for c in pool if c not in sample]
        sample.extend(rng.sample(remaining, min(n - len(sample), len(remaining))))

    new_rows = [
        {
            "chunk_id": c["chunk_id"],
            "company": c["company"],
            "year": c["year"],
            "heading": c.get("heading", ""),
            "text": c["text"],
            "register": "",
        }
        for c in sample
    ]
    df = pd.DataFrame(existing_rows + new_rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} chunks to {out} ({len(new_rows)} new)")
    print(f"Valid registers: {', '.join(DEI_REGISTERS)}")
    print("Fill in the `register` column, then run classify_dei_register.py --validate-only")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", type=int, default=90)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--append",
        action="store_true",
        help="Keep existing sample.csv rows; sample only from companies not yet present",
    )
    parser.add_argument(
        "--refresh-company",
        metavar="COMPANY",
        help="Replace unlabeled rows for one company; keep other companies' rows",
    )
    parser.add_argument(
        "--min-year",
        type=int,
        metavar="YEAR",
        help="Only sample chunks from this year onward",
    )
    parser.add_argument(
        "--companies",
        default=",".join(COMPANIES),
        help="Comma-separated company ids to sample from",
    )
    args = parser.parse_args()
    main(
        args.n,
        args.seed,
        args.append,
        [c.strip() for c in args.companies.split(",")],
        args.min_year,
        args.refresh_company,
    )
