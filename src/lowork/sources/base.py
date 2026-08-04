"""Common record, register vocabulary, HTTP helper, and source registry."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

import httpx

# The four registers Project 3 measures across. Carried as metadata on every
# record so the converged pipeline stays one code path; only H2 crosses
# registers (see plan §0).
REGISTERS = ("firm", "press", "worker", "legal")

MAX_RETRIES = 4
DEFAULT_TIMEOUT = 30.0


@dataclass
class SourceRecord:
    """One unit of fetched text, normalizable into a pipeline chunk record."""

    source: str  # module NAME, e.g. "hn", "books"
    register: str  # one of REGISTERS
    url: str
    text: str
    observed_date: str = ""  # ISO date the text is *of* (drives the timeline); "" if unknown
    fetched_at: str = ""
    title: str = ""
    author: str = ""  # author or role hint
    subtype: str = ""  # worker sub-register: employee | visitor | community | review (reliability signal)
    provenance: dict = field(default_factory=dict)  # source-specific (points, ids, ...)

    def __post_init__(self) -> None:
        if self.register not in REGISTERS:
            raise ValueError(f"bad register {self.register!r}; expected one of {REGISTERS}")
        if not self.fetched_at:
            self.fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    @property
    def chunk_id(self) -> str:
        h = hashlib.sha1(f"{self.source}|{self.url}|{self.text}".encode()).hexdigest()
        return h[:16]

    def _timestamp(self) -> str:
        """YYYYMMDDhhmmss for the chunk schema; pad an ISO date, else fetched date."""
        d = self.observed_date or self.fetched_at[:10]
        digits = "".join(ch for ch in d if ch.isdigit())
        return (digits + "0" * 14)[:14]

    @property
    def year(self) -> int | None:
        ts = self._timestamp()
        return int(ts[:4]) if ts[:4].isdigit() and ts[:4] != "0000" else None

    def to_chunk(self) -> dict:
        """Normalize into the shared pipeline chunk record (extract_chunks schema)."""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "heading": self.title,
            "source_url": self.url,
            "timestamp": self._timestamp(),
            "year": self.year,
            "word_count": len(self.text.split()),
            "position": 0,
            "extraction_source": self.source,
            # Project-3 metadata the converged pipeline carries but ignores:
            "register": self.register,
            "subtype": self.subtype,
            "observed_date": self.observed_date,
            "author": self.author,
            "provenance": self.provenance,
        }


@dataclass
class ExploreResult:
    """Cheap per-source census for the Phase 1a source map."""

    source: str
    register: str
    query: str
    total: int | None  # reported total hits if the API gives one, else len(samples)
    date_min: str = ""
    date_max: str = ""
    samples: list[dict] = field(default_factory=list)  # [{date, title, url, snippet}]
    note: str = ""


def get(
    client: httpx.Client, url: str, params: dict | None = None, headers: dict | None = None
) -> httpx.Response:
    """GET with retry/backoff on transient errors and 429/503."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.get(url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT)
            if resp.status_code in (429, 503):
                time.sleep(3 * (attempt + 1))
                continue
            return resp
        except httpx.TransportError:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"exhausted retries for {url}")


def registry() -> dict:
    """name -> source module. Imported lazily to avoid import cycles."""
    from . import books, hey_world, hn, live, reddit, wayback_url

    mods = [hn, books, reddit, wayback_url, live, hey_world]
    return {m.NAME: m for m in mods}
