#!/usr/bin/env python
"""Turn a saved Ashby posting-API JSON into a manual HTML capture.

Several exclusion-cohort companies carry the register in their job-listing
templates, not page prose (rilla's "Don't Work Here" sections). The durable
live capture for them is the Ashby posting API:

    curl "https://api.ashbyhq.com/posting-api/job-board/<board>" -o board.json

This script renders that JSON (listed jobs only: title, location, department,
descriptionHtml) into one plain HTML document under data/<co>/manual_html/,
registers it in manual_manifest.json, and runs ingest_manual_html — so
extract_chunks owns it from then on like any other capture, and re-running
extract never loses it. Boilerplate repeated across listings collapses in
the chunker's per-year near-dup pass.

(Archived jobs.ashbyhq.com captures need none of this: they embed the same
JSON in window.__appData, which chunk_html now parses directly.)

Usage:
    uv run scripts/ingest_ashby.py --company rilla \
        --json data/exclusion_pilot/scout_captures_2026-11/rilla_jobs.json \
        --url https://jobs.ashbyhq.com/rilla --date 20261106
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
from datetime import date
from pathlib import Path

from lowork.config import company_dir
from lowork.io import read_json, write_json

import ingest_manual_html


def render(board_json: dict, board_url: str) -> str:
    jobs = [j for j in board_json.get("jobs", []) if j.get("isListed", True)]
    parts = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'>",
        f"<title>Job board — {html_mod.escape(board_url)}</title></head><body>",
        f"<h1>Job board ({len(jobs)} listed roles)</h1>",
    ]
    for j in jobs:
        meta = " · ".join(
            str(x) for x in (j.get("location"), j.get("department"), j.get("employmentType")) if x
        )
        parts.append("<section>")
        parts.append(f"<h2>{html_mod.escape(j.get('title', 'Untitled role'))}"
                     f"{' — ' + html_mod.escape(meta) if meta else ''}</h2>")
        desc = j.get("descriptionHtml")
        if desc:
            parts.append(desc)
        elif j.get("descriptionPlain"):
            for para in j["descriptionPlain"].split("\n\n"):
                parts.append(f"<p>{html_mod.escape(para)}</p>")
        parts.append("</section>")
    parts.append("</body></html>")
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--company", required=True)
    ap.add_argument("--json", required=True, help="saved posting-API JSON")
    ap.add_argument("--url", required=True, help="the job board URL (provenance)")
    ap.add_argument("--date", default=date.today().strftime("%Y%m%d"),
                    help="capture date YYYYMMDD (default: today)")
    args = ap.parse_args()

    board = json.loads(Path(args.json).read_text())
    if "jobs" not in board:
        raise SystemExit(f"{args.json}: no 'jobs' key — not an Ashby posting-API payload?")

    manual_dir = company_dir(args.company) / "manual_html"
    manual_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{args.date}_ashby-board.html"
    (manual_dir / fname).write_text(render(board, args.url))

    manifest_path = manual_dir / "manual_manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {"captures": []}
    entry = {
        "file": fname,
        "url": args.url,
        "capture_date": args.date,
        "source": f"ashby_posting_api ({Path(args.json).name})",
    }
    if not any(c["file"] == fname for c in manifest["captures"]):
        manifest["captures"].append(entry)
        write_json(manifest_path, manifest)
    print(f"Rendered {len(board['jobs'])} jobs -> {manual_dir / fname}")

    ingest_manual_html.main(args.company)


if __name__ == "__main__":
    main()
