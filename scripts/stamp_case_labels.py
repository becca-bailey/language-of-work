#!/usr/bin/env python
"""Stamp every chunk of a case corpus with a single analysis label.

The careers-page register taxonomy (mission_brand / job_listing / ...) is
off-domain for non-careers case corpora (e.g. a founder blog): running
classify_chunks.py on such prose would silently drop chunks from every
downstream stage on inapplicable label calls. Downstream stages only need
classifications.json to exist and to gate on ANALYSIS_LABELS, so the honest
move for a whole-corpus case is a transparent pass-through stamp, recorded
as a caveat in the corpus manifest.

Usage:
  uv run scripts/stamp_case_labels.py --case dhh_blog --label mission_brand
"""

from __future__ import annotations

import argparse

from lowork.config import CHUNK_LABELS, company_dir
from lowork.io import load_all_chunks, read_json, write_json


def main(case: str, label: str) -> None:
    cdir = company_dir(case)
    chunks = load_all_chunks(cdir / "chunks")
    if not chunks:
        raise SystemExit(f"no chunks under {cdir / 'chunks'} — run fetch_case.py first")
    write_json(cdir / "classifications.json", {c["chunk_id"]: label for c in chunks})

    manifest_path = cdir / "corpus_manifest.json"
    caveat = (
        f"classifications.json is a pass-through stamp ({label} on all {len(chunks)} chunks): "
        "careers-page label taxonomy is inapplicable to this corpus; the whole corpus is the "
        "analysis corpus."
    )
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        caveats = [c for c in manifest.get("caveats", []) if "pass-through stamp" not in c]
        manifest["caveats"] = caveats + [caveat]
        write_json(manifest_path, manifest)
    print(f"Stamped {len(chunks)} chunks '{label}' -> {cdir / 'classifications.json'}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    p.add_argument("--label", default="mission_brand", choices=CHUNK_LABELS)
    args = p.parse_args()
    main(args.case, args.label)
