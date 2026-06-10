#!/usr/bin/env python
"""Step 2: extract and chunk archived HTML; log per-snapshot coverage.

Reads data/<company>/snapshots.json + raw_html/, writes chunks/{year}.jsonl
and coverage stats back into the manifest. Thin snapshots get flagged, not
silently absorbed.
"""

from __future__ import annotations

import argparse
from collections import defaultdict

from lowork.chunking import chunk_html, coverage_stats, dedup_chunks
from lowork.config import company_dir
from lowork.io import read_json, write_json, write_jsonl

THIN_WORDS = 150  # snapshots under this extracted-word count get flagged


def main(company: str) -> None:
    cdir = company_dir(company)
    manifest = read_json(cdir / "snapshots.json")
    raw_dir = cdir / "raw_html"
    by_year: dict[int, list[dict]] = defaultdict(list)

    for cap in manifest["captures"]:
        if "html_file" not in cap:
            continue
        html = (raw_dir / cap["html_file"]).read_bytes()
        chunks = chunk_html(html, source_url=cap["original"], timestamp=cap["timestamp"])
        stats = coverage_stats(chunks, html)
        cap["coverage"] = stats
        cap["thin"] = stats["dom_words"] < THIN_WORDS
        flag = " THIN" if cap["thin"] else ""
        print(f"{cap['timestamp']} {cap['original']}: "
              f"{stats['chunk_count']} chunks, {stats['dom_words']} words{flag}")
        by_year[int(cap["timestamp"][:4])].extend(chunks)

    chunks_dir = cdir / "chunks"
    total = 0
    for year, chunks in sorted(by_year.items()):
        unique = dedup_chunks(chunks)
        total += write_jsonl(chunks_dir / f"{year}.jsonl", unique)
        dropped = len(chunks) - len(unique)
        note = f" ({dropped} near-dups dropped)" if dropped else ""
        print(f"{year}: {len(unique)} unique chunks{note}")

    write_json(cdir / "snapshots.json", manifest)
    thin_years = sorted({int(c["timestamp"][:4]) for c in manifest["captures"]
                         if c.get("thin") and "html_file" in c})
    print(f"\nTotal: {total} chunks. Years with thin snapshots: {thin_years or 'none'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
