#!/usr/bin/env python
"""Step 5: embed analysis chunks (mission_brand + benefits_perks) cache-first.

Writes data/<company>/embeddings.parquet with the pinned model recorded on
every row. The embedding cache guarantees no text is ever embedded twice.
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.config import EMBEDDING_MODEL, company_dir
from lowork.embeddings import EmbeddingStore
from lowork.io import load_all_chunks, read_json

ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}


def main(company: str) -> None:
    cdir = company_dir(company)
    chunks = load_all_chunks(cdir / "chunks")
    labels = read_json(cdir / "classifications.json")

    analysis = [c for c in chunks if labels.get(c["chunk_id"]) in ANALYSIS_LABELS]
    print(f"{len(analysis)}/{len(chunks)} chunks in analysis corpus "
          f"({', '.join(sorted(ANALYSIS_LABELS))})")

    store = EmbeddingStore()
    embeddings = store.embed([c["text"] for c in analysis])

    df = pd.DataFrame(
        {
            "chunk_id": [c["chunk_id"] for c in analysis],
            "year": [c["year"] for c in analysis],
            "timestamp": [c["timestamp"] for c in analysis],
            "label": [labels[c["chunk_id"]] for c in analysis],
            "heading": [c["heading"] for c in analysis],
            "text": [c["text"] for c in analysis],
            "model": EMBEDDING_MODEL,
            "embedding": list(embeddings),
        }
    )
    out = cdir / "embeddings.parquet"
    df.to_parquet(out, index=False)
    print(f"Wrote {len(df)} rows to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
