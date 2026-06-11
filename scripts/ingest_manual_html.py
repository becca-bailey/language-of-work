#!/usr/bin/env python
"""Ingest manually captured HTML into snapshots.json for pipeline processing.

Expects data/<company>/manual_html/<file>.html and manual_manifest.json:

  {
    "captures": [
      {
        "file": "20250401_careers.html",
        "url": "https://www.example.com/careers/",
        "capture_date": "20250401",
        "source": "archive.today"
      }
    ]
  }
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from lowork.config import company_dir
from lowork.io import read_json, write_json


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:24]


def main(company: str) -> None:
    cdir = company_dir(company)
    manual_dir = cdir / "manual_html"
    manifest_path = manual_dir / "manual_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing {manifest_path}")

    manual = read_json(manifest_path)
    snapshots_path = cdir / "snapshots.json"
    if snapshots_path.exists():
        manifest = read_json(snapshots_path)
    else:
        manifest = {"company": company, "captures": []}

    existing_keys = {
        (c.get("original"), c.get("timestamp"))
        for c in manifest["captures"]
    }
    existing_digests = {c.get("digest") for c in manifest["captures"] if c.get("digest")}

    raw_dir = cdir / "raw_html"
    raw_dir.mkdir(exist_ok=True)
    added = 0

    for cap in manual.get("captures", []):
        src = manual_dir / cap["file"]
        if not src.exists():
            print(f"SKIP missing file: {src}")
            continue
        data = src.read_bytes()
        d = digest(data)
        ts = cap["capture_date"]
        if len(ts) == 8:
            ts = f"{ts}120000"
        url = cap["url"]
        key = (url, ts)
        if key in existing_keys or d in existing_digests:
            print(f"SKIP dup {ts} {url}")
            continue
        html_file = f"{ts}_{d}.html"
        (raw_dir / html_file).write_bytes(data)
        manifest["captures"].append({
            "timestamp": ts,
            "original": url,
            "digest": d,
            "html_file": html_file,
            "source": cap.get("source", "manual"),
        })
        existing_keys.add(key)
        existing_digests.add(d)
        added += 1
        print(f"Added {ts} {url} ({len(data)} bytes)")

    write_json(snapshots_path, manifest)
    print(f"Merged {added} manual captures into {snapshots_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", required=True)
    main(parser.parse_args().company)
