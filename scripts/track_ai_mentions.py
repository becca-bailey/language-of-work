#!/usr/bin/env python
"""Track AI-term mentions per company: prevalence by year and register label.

Runs over ALL classified chunks (not just analysis labels) — the talk-vs-hire
contrast needs job_listing chunks, which are never embedded. Pure regex, no API
calls. Output: data/<company>/ai_mentions.json.

Per-company timing claims stay embargoed until the SPA/Wayback corpus gaps are
filled; years are thin-flagged so the caveat travels with the data.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from lowork.ai_net import find_ai_terms
from lowork.config import CONTENT_LABELS, company_dir
from lowork.io import load_all_chunks, read_json, write_json

THIN_CHUNKS = 5  # fewer content chunks than this in a year -> thin flag
MAX_EXAMPLES_PER_YEAR = 3


def main(company: str) -> None:
    cdir = company_dir(company)
    chunks = load_all_chunks(cdir / "chunks")
    classifications = read_json(cdir / "classifications.json")

    # A chunk_id can recur across captures within a year; count each once.
    seen: set[tuple[int, str]] = set()
    per_year: dict[int, dict] = defaultdict(
        lambda: {
            "labels": defaultdict(lambda: {"chunks": 0, "ai_chunks": 0, "mentions": 0}),
            "terms": Counter(),
            "examples": [],
        }
    )

    for chunk in chunks:
        label = classifications.get(chunk["chunk_id"])
        if label not in CONTENT_LABELS:
            continue
        year = int(chunk["year"])
        key = (year, chunk["chunk_id"])
        if key in seen:
            continue
        seen.add(key)

        rec = per_year[year]
        lab = rec["labels"][label]
        lab["chunks"] += 1
        terms = find_ai_terms(chunk["text"])
        if terms:
            lab["ai_chunks"] += 1
            lab["mentions"] += len(terms)
            rec["terms"].update(terms)
            if len(rec["examples"]) < MAX_EXAMPLES_PER_YEAR:
                rec["examples"].append({
                    "label": label,
                    "chunk_id": chunk["chunk_id"],
                    "terms": sorted(set(terms)),
                    "text": chunk["text"][:300],
                })

    years = []
    for year in sorted(per_year):
        rec = per_year[year]
        total = sum(v["chunks"] for v in rec["labels"].values())
        ai_total = sum(v["ai_chunks"] for v in rec["labels"].values())
        years.append({
            "year": year,
            "total_chunks": total,
            "ai_chunks": ai_total,
            "prevalence": round(ai_total / total, 4) if total else None,
            "thin": total < THIN_CHUNKS,
            "labels": {k: dict(v) for k, v in sorted(rec["labels"].items())},
            "terms": dict(rec["terms"].most_common()),
            "examples": rec["examples"],
        })

    out = cdir / "ai_mentions.json"
    write_json(out, {"company": company, "content_labels": sorted(CONTENT_LABELS), "years": years})
    grand_ai = sum(y["ai_chunks"] for y in years)
    grand = sum(y["total_chunks"] for y in years)
    print(f"Wrote {out} ({grand_ai}/{grand} AI-mentioning content chunks)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", required=True)
    main(parser.parse_args().company)
