"""Present-day canon (firm register) via live-site fetch + Trafilatura.

Captures the canon as it exists *now* — the current Creed / Menlo Way / about
pages — as the latest point on the canon timeline, complementing the archived
snapshots from `wayback_url`. Trafilatura strips nav/boilerplate to main content;
the cleaned text is split into paragraph-sized chunks so the granularity is
comparable to the DOM chunks the rest of the pipeline produces.

observed_date is today's date — these records are the live endpoint, not archival.
Pages that no longer exist (404 / empty extraction) are skipped, not faked.
"""

from __future__ import annotations

from datetime import date
from typing import Iterator

import httpx
import trafilatura

from .base import ExploreResult, SourceRecord, get

NAME = "live"
REGISTER = "firm"

MIN_CHUNK_WORDS = 20


def _canon_urls(cfg: dict) -> list[str]:
    return cfg.get("canon_urls", [])


def _full_url(url: str) -> str:
    return url if url.startswith("http") else f"https://{url}"


def _extract(client: httpx.Client, url: str) -> str:
    """Fetch live HTML and return main-content text, or '' if unreachable/empty."""
    try:
        resp = get(client, _full_url(url))
        if resp.status_code != 200:
            return ""
    except Exception:
        return ""
    return trafilatura.extract(resp.text, include_comments=False, include_tables=False) or ""


def _chunks(text: str) -> list[str]:
    """Split extracted text into paragraph-sized units; drop too-short fragments."""
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    return [p for p in paras if len(p.split()) >= MIN_CHUNK_WORDS]


def explore(cfg: dict, client: httpx.Client, limit: int = 10) -> list[ExploreResult]:
    """Cheap census: which canon URLs are live and yield extractable text now."""
    results = []
    for url in _canon_urls(cfg):
        text = _extract(client, url)
        chunks = _chunks(text)
        results.append(
            ExploreResult(
                source=NAME,
                register=REGISTER,
                query=url,
                total=len(chunks),
                date_min=date.today().isoformat() if chunks else "",
                date_max=date.today().isoformat() if chunks else "",
                samples=[{"date": date.today().isoformat(), "title": url, "url": _full_url(url),
                          "snippet": chunks[0][:200]}] if chunks else [],
                note="live present-day canon (Trafilatura main-content extraction)" if chunks
                else "no live content (404 / empty extraction / SPA)",
            )
        )
    return results


def fetch(cfg: dict, client: httpx.Client) -> Iterator[SourceRecord]:
    today = date.today().isoformat()
    for url in _canon_urls(cfg):
        text = _extract(client, url)
        for i, chunk in enumerate(_chunks(text)):
            yield SourceRecord(
                source=NAME,
                register=REGISTER,
                url=_full_url(url),
                text=chunk,
                observed_date=today,
                title=url,
                provenance={"canon": True, "canon_url": url, "position": i},
            )
