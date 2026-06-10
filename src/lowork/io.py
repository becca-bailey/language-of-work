"""JSONL / JSON / parquet helpers."""

from __future__ import annotations

import json
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


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def load_all_chunks(chunks_dir: Path) -> list[dict]:
    chunks: list[dict] = []
    for path in sorted(chunks_dir.glob("*.jsonl")):
        chunks.extend(read_jsonl(path))
    return chunks
