"""Cache-first embedding store.

Every unique text is embedded exactly once, keyed by sha256(text) + model
version, and stored permanently in a parquet cache. Re-runs read the cache;
nothing is ever re-embedded. This is where determinism comes from — the API
itself is not strictly bit-deterministic across calls.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from openai import OpenAI

from .config import DATA_DIR, EMBEDDING_DIMENSIONS, EMBEDDING_MODEL

BATCH_SIZE = 100


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class EmbeddingStore:
    def __init__(self, model: str = EMBEDDING_MODEL, cache_dir: Path | None = None):
        self.model = model
        cache_dir = cache_dir or (DATA_DIR / "embedding_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = cache_dir / f"{model}.parquet"
        self._cache: dict[str, np.ndarray] = {}
        self._client: OpenAI | None = None
        if self.cache_path.exists():
            df = pd.read_parquet(self.cache_path)
            for h, emb in zip(df["hash"], df["embedding"]):
                self._cache[h] = np.asarray(emb, dtype=np.float32)

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI()
        return self._client

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return embeddings for texts (n, dim), embedding only cache misses."""
        hashes = [text_hash(t) for t in texts]
        missing: dict[str, str] = {h: t for h, t in zip(hashes, texts) if h not in self._cache}

        if missing:
            new_rows = []
            items = list(missing.items())
            for i in range(0, len(items), BATCH_SIZE):
                batch = items[i : i + BATCH_SIZE]
                resp = self.client.embeddings.create(
                    model=self.model,
                    input=[t for _, t in batch],
                    dimensions=EMBEDDING_DIMENSIONS,
                )
                for (h, t), datum in zip(batch, resp.data):
                    vec = np.asarray(datum.embedding, dtype=np.float32)
                    self._cache[h] = vec
                    new_rows.append({"hash": h, "text": t, "model": self.model, "embedding": vec})
                print(f"  embedded {min(i + BATCH_SIZE, len(items))}/{len(items)} new texts")
            self._append_to_cache(new_rows)

        return np.stack([self._cache[h] for h in hashes])

    def _append_to_cache(self, rows: list[dict]) -> None:
        if not rows:
            return
        new_df = pd.DataFrame(rows)
        if self.cache_path.exists():
            new_df = pd.concat([pd.read_parquet(self.cache_path), new_df], ignore_index=True)
        new_df.to_parquet(self.cache_path, index=False)
