#!/usr/bin/env python
"""Extract enumerated well-being benefits into a per-item taxonomy (Phase 1.2 pilot / 3).

Scans the benefits-bearing chunks (classified benefits_perks or job_listing) for one or
more companies and runs the tool-use extractor in lowork.benefits_extract. Writes one row
per extracted item to data/<co>/wellbeing_benefits.jsonl.

Pilot usage (cheap, for hand-validation in Phase 1.3):
    python scripts/extract_wellbeing_benefits.py coinbase --limit 40

Full usage (Phase 3):
    python scripts/extract_wellbeing_benefits.py            # all companies
"""

from __future__ import annotations

import argparse
from collections import Counter

from lowork.benefits_extract import extract_benefits
from lowork.config import BENEFITS_LABELS, JUDGE_MODEL, company_dir, load_companies
from lowork.io import load_all_chunks, read_json, write_jsonl



def benefits_chunks(company: str, limit: int | None) -> list[dict]:
    labels = read_json(company_dir(company) / "classifications.json")
    chunks = load_all_chunks(company_dir(company) / "chunks")
    keep = []
    for c in chunks:
        if labels.get(c.get("chunk_id")) in BENEFITS_LABELS:
            c["company"] = company
            keep.append(c)
    keep.sort(key=lambda c: (c.get("year", 0), c.get("chunk_id", "")))
    return keep[:limit] if limit else keep


def run_company(company: str, limit: int | None, model: str) -> list[dict]:
    chunks = benefits_chunks(company, limit)
    print(f"[{company}] {len(chunks)} benefits-bearing chunks -> extracting ({model})")
    if not chunks:
        return []
    items = extract_benefits(chunks, model=model)
    out = company_dir(company) / "wellbeing_benefits.jsonl"
    write_jsonl(out, items)
    cats = Counter(i["category"] for i in items)
    loci = Counter(i["locus"] for i in items)
    spec = Counter(i["specificity"] for i in items)
    print(f"[{company}] {len(items)} items -> {out}")
    print(f"   locus: {dict(loci)}")
    print(f"   specificity: {dict(spec)}")
    print(f"   top categories: {dict(cats.most_common(6))}")
    return items


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("companies", nargs="*", help="default: all in pipeline.yaml")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap chunks per company (pilot mode)")
    ap.add_argument("--model", default=JUDGE_MODEL)
    args = ap.parse_args()

    companies = args.companies or load_companies()
    for co in companies:
        run_company(co, args.limit, args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
