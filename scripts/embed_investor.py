#!/usr/bin/env python
"""Embed investor filing chunks (Human Capital, Risk Factors, Business)."""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.config import EMBEDDING_MODEL, company_dir
from lowork.embeddings import EmbeddingStore
from lowork.io import load_all_chunks

INVESTOR_LABEL = "investor_filing"


def main(company: str) -> None:
    cdir = company_dir(company)
    chunks_dir = cdir / "investor" / "chunks"
    if not chunks_dir.exists():
        raise SystemExit(f"No investor chunks for {company} — run fetch_filings.py first")

    chunks = load_all_chunks(chunks_dir)
    if not chunks:
        raise SystemExit(f"No investor chunks found in {chunks_dir}")

    store = EmbeddingStore()
    embeddings = store.embed([c["text"] for c in chunks])

    df = pd.DataFrame({
        "chunk_id": [c["chunk_id"] for c in chunks],
        "year": [c["year"] for c in chunks],
        "timestamp": [c["timestamp"] for c in chunks],
        "label": INVESTOR_LABEL,
        "heading": [c.get("heading", "") for c in chunks],
        "text": [c["text"] for c in chunks],
        "model": EMBEDDING_MODEL,
        "embedding": list(embeddings),
    })
    out = cdir / "investor_embeddings.parquet"
    df.to_parquet(out, index=False)
    print(f"Wrote {len(df)} rows to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", required=True)
    main(parser.parse_args().company)
