"""JSONL / JSON / parquet helpers."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable, Iterator


def read_jsonl(path: Path) -> Iterator[dict]:
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: Path, records: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    return n


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _json_safe(obj: object) -> object:
    """Convert non-finite floats (NaN/Infinity) to None so output is valid JSON.

    json.dumps defaults to allow_nan=True, which emits bare `NaN`/`Infinity`
    tokens that browsers' JSON.parse rejects. pandas NaN (e.g. an unclassified
    `register`) flows into exports and silently breaks the charts, so sanitize
    here rather than relying on every call site to coerce.
    """
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_safe(obj), indent=2, ensure_ascii=False, allow_nan=False)
    )


def load_all_chunks(chunks_dir: Path) -> list[dict]:
    chunks: list[dict] = []
    for path in sorted(chunks_dir.glob("*.jsonl")):
        chunks.extend(read_jsonl(path))
    return chunks
