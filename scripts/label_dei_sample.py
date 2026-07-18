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
Use --stratify-registers N to append rows stratified by PREDICTED register
(N per register, drawn across all companies with dei_registers.json). The
default company-era sampling mirrors the corpus, where `absent` dominates —
fine for measuring the absent boundary, useless for the active registers the
analysis rests on. Predicted-register strata put ~N examples of each register
in front of the labeler. Caveat for the writeup: agreement on a stratified
sample is a per-register measure, not an estimate of corpus-wide agreement.
"""

from __future__ import annotations

import argparse
import random
from collections import defaultdict

import pandas as pd

from lowork.config import ANALYSIS_LABELS, DATA_DIR, company_dir
from lowork.dei import DEI_REGISTERS
from lowork.io import load_all_chunks, read_json

COMPANIES = ["google", "amazon", "meta", "palantir"]


def stratify_by_register(per_register: int, seed: int) -> None:
    """Append rows stratified by predicted register, pooled across companies."""
    rng = random.Random(seed)
    out = DATA_DIR / "dei_labels" / "sample.csv"
    existing_rows: list[dict] = []
    existing_ids: set[str] = set()
    if out.exists():
        prev = pd.read_csv(out, dtype={"register": "string"})
        existing_rows = prev.to_dict("records")
        existing_ids = set(prev["chunk_id"])

    by_register: dict[str, list[dict]] = defaultdict(list)
    for reg_path in sorted(DATA_DIR.glob("*/dei_registers.json")):
        company = reg_path.parent.name
        predictions = read_json(reg_path)
        chunks_dir = reg_path.parent / "chunks"
        if not chunks_dir.exists():
            continue
        for c in load_all_chunks(chunks_dir):
            pred = predictions.get(c["chunk_id"])
            if pred and c["chunk_id"] not in existing_ids:
                by_register[pred].append({**c, "company": company})

    new_rows: list[dict] = []
    for register in sorted(by_register):
        pool = by_register[register]
        take = rng.sample(pool, min(per_register, len(pool)))
        print(f"  {register}: {len(take)} sampled (pool {len(pool)})")
        new_rows.extend(
            {
                "chunk_id": c["chunk_id"],
                "company": c["company"],
                "year": c["year"],
                "heading": c.get("heading", ""),
                "text": c["text"],
                "register": "",
            }
            for c in take
        )

    rng.shuffle(new_rows)  # don't present the labeler with prediction-ordered blocks
    df = pd.DataFrame(existing_rows + new_rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows to {out} ({len(new_rows)} new, stratified by predicted register)")
    print(f"Valid registers: {', '.join(DEI_REGISTERS)}")
    print("Fill in the empty `register` rows, then run report_dei_agreement.py --task register")


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
    parser.add_argument(
        "--stratify-registers",
        type=int,
        metavar="N",
        help="Append N chunks per PREDICTED register (pooled across all companies)",
    )
    args = parser.parse_args()
    if args.stratify_registers:
        stratify_by_register(args.stratify_registers, args.seed)
        raise SystemExit(0)
    main(
        args.n,
        args.seed,
        args.append,
        [c.strip() for c in args.companies.split(",")],
        args.min_year,
        args.refresh_company,
    )
