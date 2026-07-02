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

# Non-prose captures slip in via broad prefix patterns (a book/report PDF, fonts,
# images, robots.txt). They aren't careers-page language, and PDFs in particular
# have no DOM structure so their whole text collapses into one giant chunk that
# overflows the downstream classifier. Skip by mimetype and by URL extension —
# Wayback sometimes mislabels a binary as text/html, so we check both.
_NON_PROSE_MIME_PREFIXES = ("image/", "font/", "audio/", "video/")
_NON_PROSE_MIMES = {
    "application/pdf", "application/octet-stream", "application/javascript",
    "application/x-javascript", "text/plain", "text/xml", "text/css",
}
_NON_PROSE_EXTS = (
    ".pdf", ".xml", ".jpg", ".jpeg", ".png", ".gif", ".ico", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".css", ".js", ".txt", ".zip", ".doc", ".docx",
)


def _is_prose_capture(cap: dict) -> bool:
    mt = (cap.get("mimetype") or "").lower()
    if mt in _NON_PROSE_MIMES or mt.startswith(_NON_PROSE_MIME_PREFIXES):
        return False
    url = cap["original"].split("?")[0].split("#")[0].lower()
    return not url.endswith(_NON_PROSE_EXTS)


def main(company: str) -> None:
    cdir = company_dir(company)
    manifest = read_json(cdir / "snapshots.json")
    raw_dir = cdir / "raw_html"
    by_year: dict[int, list[dict]] = defaultdict(list)

    for cap in manifest["captures"]:
        if "html_file" not in cap:
            continue
        if not _is_prose_capture(cap):
            cap["skipped_nonprose"] = True
            print(f"{cap['timestamp']} {cap['original']}: skipped (non-prose {cap.get('mimetype', '?')})")
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
