#!/usr/bin/env python
"""Generate a manual-capture worklist for a company's thin/SPA years.

When deeper Wayback fetching can't recover a company-year (modern SPA careers pages serve
only an app shell), this lists exactly which year × URL the user needs to copy/paste, with
a Wayback link to view the rendered page, plus the ready-to-run ingest instructions. Never
imputes the gap — surfaces it (see [[corpus-methodology-preferences]]).

Writes data/<company>/manual_todo.md.
"""

from __future__ import annotations

import argparse
from collections import Counter

from lowork.config import company_dir
from lowork.io import read_json, load_all_chunks

THIN = 3  # mission_brand chunks/year below this = needs manual capture


def main(company: str, label_field: str = "mission_brand") -> None:
    cdir = company_dir(company)
    cfg = read_json(cdir / "url_patterns.json")
    urls = [p["url"] for p in cfg.get("patterns", []) if p.get("match_type") == "exact"] \
        or [p["url"] for p in cfg.get("patterns", [])]
    primary = urls[0] if urls else f"{company}.com/careers"

    cls = read_json(cdir / "classifications.json") if (cdir / "classifications.json").exists() else {}
    chunks = load_all_chunks(cdir / "chunks")
    mb = Counter(int(c["year"]) for c in chunks if cls.get(c["chunk_id"]) == label_field)
    if not mb:
        thin_years = list(range(2014, 2027))
    else:
        thin_years = [y for y in range(min(mb), max(mb) + 1) if mb.get(y, 0) < THIN]

    lines = [
        f"# Manual-capture worklist — {cfg.get('display_name', company)}",
        "",
        f"Years with < {THIN} usable mission_brand chunks (SPA app-shell / no archived text).",
        "Wayback can't recover these server-side; capture them by hand.",
        "",
        "## How to capture (per row)",
        "1. Open the Wayback link, pick a snapshot in that year, let the page render.",
        "2. Save the rendered page (Cmd-S → \"Web Page, Complete\" or copy the visible text",
        f"   into a file) as `data/{company}/manual_html/<YYYY>_careers.html`.",
        "3. Add an entry to `data/" + company + "/manual_html/manual_manifest.json` (template below).",
        f"4. Run: `uv run scripts/ingest_manual_html.py --company {company}`",
        f"   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.",
        "",
        "## Worklist",
        "| done | year | url | wayback (pick a snapshot in-year) |",
        "| --- | --- | --- | --- |",
    ]
    for y in thin_years:
        wb = f"https://web.archive.org/web/{y}0601000000*/{primary}"
        lines.append(f"| [ ] | {y} | {primary} | {wb} |")

    lines += [
        "",
        "## manual_manifest.json template",
        "```json",
        "{",
        '  "captures": [',
        "    {",
        f'      "file": "{thin_years[0] if thin_years else 2020}_careers.html",',
        f'      "url": "https://{primary}",',
        f'      "capture_date": "{thin_years[0] if thin_years else 2020}0601",',
        '      "source": "manual"',
        "    }",
        "  ]",
        "}",
        "```",
        "",
        f"Current mission_brand counts by year: {dict(sorted(mb.items()))}",
    ]
    (cdir / "manual_todo.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {cdir / 'manual_todo.md'} — {len(thin_years)} years flagged: {thin_years}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--company", required=True)
    main(p.parse_args().company)
