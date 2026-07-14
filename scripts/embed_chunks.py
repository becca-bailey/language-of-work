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

# DEI (Project 2) analysis corpus
DEI_ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}
LABEL_SETS = {"dei": DEI_ANALYSIS_LABELS}


def main(company: str, label_set: str) -> None:
    cdir = company_dir(company)
    chunks = load_all_chunks(cdir / "chunks")
    labels = read_json(cdir / "classifications.json")
    analysis_labels = LABEL_SETS[label_set]

    analysis = [c for c in chunks if labels.get(c["chunk_id"]) in analysis_labels]
    print(f"{len(analysis)}/{len(chunks)} chunks in analysis corpus "
          f"({', '.join(sorted(analysis_labels))})")

    store = EmbeddingStore()
    embeddings = store.embed([c["text"] for c in analysis])

    # register/subtype/observed_date carried so downstream scoring can filter by
    # register (firm vs worker) without reloading the chunk records (P3 H2 lane).
    df = pd.DataFrame(
        {
            "chunk_id": [c["chunk_id"] for c in analysis],
            "year": [c["year"] for c in analysis],
            "timestamp": [c["timestamp"] for c in analysis],
            "register": [c.get("register") for c in analysis],
            "subtype": [c.get("subtype") for c in analysis],
            "observed_date": [c.get("observed_date") for c in analysis],
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
    parser.add_argument("--labels", choices=list(LABEL_SETS), default="dei",
                        help="dei = mission_brand+benefits_perks (P2)")
    args = parser.parse_args()
    main(args.company, args.labels)
