"""Cache-first embedding store.

Every unique text is embedded exactly once, keyed by sha256(text) + model
version, and stored permanently in a local SQLite cache. Re-runs read the cache;
nothing is ever re-embedded. This is where determinism comes from — the API
itself is not strictly bit-deterministic across calls.

The cache is SQLite (not parquet) so that adding embeddings is an O(new-rows)
upsert instead of rewriting the whole file on every batch. It's a pipeline-time
artifact only — the deployed site never reads it — so it is gitignored and backed
up out-of-band (see README). A legacy `<model>.parquet` cache is migrated in
automatically on first use.
"""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import numpy as np
from openai import OpenAI

from .config import DATA_DIR, EMBEDDING_DIMENSIONS, EMBEDDING_MODEL

BATCH_SIZE = 100
# SQLite caps host parameters per statement (SQLITE_MAX_VARIABLE_NUMBER, 999 on
# older builds); chunk IN-clause lookups well under that.
_SELECT_CHUNK = 500


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class EmbeddingStore:
    def __init__(self, model: str = EMBEDDING_MODEL, cache_dir: Path | None = None):
        self.model = model
        cache_dir = cache_dir or (DATA_DIR / "embedding_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = cache_dir / f"{model}.sqlite"
        self._cache: dict[str, np.ndarray] = {}
        self._client: OpenAI | None = None

        self._db = sqlite3.connect(self.cache_path)
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS embeddings ("
            "  hash TEXT PRIMARY KEY,"
            "  text TEXT NOT NULL,"
            "  model TEXT NOT NULL,"
            "  embedding BLOB NOT NULL"
            ")"
        )
        self._db.commit()
        self._migrate_legacy_parquet(cache_dir / f"{model}.parquet")

    def _migrate_legacy_parquet(self, parquet_path: Path) -> None:
        """One-time import of the old monolithic parquet cache into SQLite."""
        if not parquet_path.exists():
            return
        (count,) = self._db.execute("SELECT COUNT(*) FROM embeddings").fetchone()
        if count:
            return  # already migrated / populated
        import pandas as pd  # local import: only needed for the one-time migration

        df = pd.read_parquet(parquet_path)
        rows = (
            (
                h,
                t,
                self.model,
                np.asarray(emb, dtype=np.float32).tobytes(),
            )
            for h, t, emb in zip(df["hash"], df["text"], df["embedding"])
        )
        self._db.executemany(
            "INSERT OR IGNORE INTO embeddings (hash, text, model, embedding) VALUES (?, ?, ?, ?)",
            rows,
        )
        self._db.commit()
        print(f"  migrated {len(df)} embeddings from {parquet_path.name} into SQLite cache")

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI()
        return self._client

    def _load_from_db(self, hashes: set[str]) -> None:
        """Populate the in-memory cache with any of `hashes` already in SQLite."""
        wanted = [h for h in hashes if h not in self._cache]
        for i in range(0, len(wanted), _SELECT_CHUNK):
            chunk = wanted[i : i + _SELECT_CHUNK]
            placeholders = ",".join("?" * len(chunk))
            rows = self._db.execute(
                f"SELECT hash, embedding FROM embeddings WHERE hash IN ({placeholders})",
                chunk,
            )
            for h, blob in rows:
                self._cache[h] = np.frombuffer(blob, dtype=np.float32)

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return embeddings for texts (n, dim), embedding only cache misses."""
        hashes = [text_hash(t) for t in texts]
        self._load_from_db(set(hashes))
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
                    new_rows.append((h, t, self.model, vec.tobytes()))
                print(f"  embedded {min(i + BATCH_SIZE, len(items))}/{len(items)} new texts")
            self._write_to_cache(new_rows)

        return np.stack([self._cache[h] for h in hashes])

    def _write_to_cache(self, rows: list[tuple]) -> None:
        if not rows:
            return
        self._db.executemany(
            "INSERT OR IGNORE INTO embeddings (hash, text, model, embedding) VALUES (?, ?, ?, ?)",
            rows,
        )
        self._db.commit()
