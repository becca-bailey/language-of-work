#!/usr/bin/env python
"""Cross-company 'values fingerprint' export.

Thin wrapper around export_web.export_fingerprints: standardizes each axis
ACROSS the cohort and writes per-company astro/src/data/<company>/fingerprint.json.
Must run over the whole set at once — a single company has no peer baseline.
"""

from __future__ import annotations

import argparse

from lowork.config import load_companies

try:  # works whether `scripts` is a package (CLI) or on sys.path (pipeline _call)
    from scripts.export_web import export_fingerprints
except ModuleNotFoundError:
    from export_web import export_fingerprints


def main(companies: list[str] | None = None) -> None:
    export_fingerprints(list(companies) if companies else load_companies())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--companies", default="")
    args = parser.parse_args()
    main([c for c in args.companies.split(",") if c] or None)
