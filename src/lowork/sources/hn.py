"""Hacker News via the Algolia API — worker-register testimony.

No API key; full corpus; date-filterable. Blessed worker source in the master
plan. "Working at X" stories and comments mentioning the firm.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterator

import httpx

from .base import ExploreResult, SourceRecord, get

NAME = "hn"
REGISTER = "worker"

SEARCH_URL = "https://hn.algolia.com/api/v1/search"
HITS_PER_PAGE = 50


def _queries(cfg: dict) -> list[str]:
    return cfg.get("queries", {}).get(NAME) or [cfg.get("display_name") or cfg["case"]]


def _iso(created_at_i: int) -> str:
    return datetime.fromtimestamp(created_at_i, tz=timezone.utc).date().isoformat()


def _search(client: httpx.Client, query: str, page: int = 0) -> dict:
    params = {"query": query, "tags": "(story,comment)", "page": page, "hitsPerPage": HITS_PER_PAGE}
    return get(client, SEARCH_URL, params=params).json()


def _hit_text(hit: dict) -> str:
    # stories carry title (+ optional story_text); comments carry comment_text
    parts = [hit.get("title") or "", hit.get("story_text") or "", hit.get("comment_text") or ""]
    return " ".join(p for p in parts if p).strip()


def explore(cfg: dict, client: httpx.Client, limit: int = 20) -> list[ExploreResult]:
    results = []
    for q in _queries(cfg):
        data = _search(client, q, page=0)
        hits = data.get("hits", [])
        dates = sorted(_iso(h["created_at_i"]) for h in hits if h.get("created_at_i"))
        samples = []
        for h in hits[:limit]:
            txt = _hit_text(h)
            samples.append(
                {
                    "date": _iso(h["created_at_i"]) if h.get("created_at_i") else "",
                    "title": (h.get("title") or h.get("story_title") or "")[:120],
                    "url": f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                    "snippet": txt[:200],
                    "points": h.get("points"),
                }
            )
        results.append(
            ExploreResult(
                source=NAME,
                register=REGISTER,
                query=q,
                total=data.get("nbHits"),
                date_min=dates[0] if dates else "",
                date_max=dates[-1] if dates else "",
                samples=samples,
            )
        )
    return results


def fetch(cfg: dict, client: httpx.Client) -> Iterator[SourceRecord]:
    max_pages = cfg.get("limits", {}).get(NAME, {}).get("max_pages", 10)
    for q in _queries(cfg):
        for page in range(max_pages):
            data = _search(client, q, page=page)
            hits = data.get("hits", [])
            if not hits:
                break
            for h in hits:
                txt = _hit_text(h)
                if not txt:
                    continue
                yield SourceRecord(
                    source=NAME,
                    register=REGISTER,
                    subtype="community",  # HN is discussion-about, not verified first-person testimony
                    url=f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                    text=txt,
                    observed_date=_iso(h["created_at_i"]) if h.get("created_at_i") else "",
                    title=(h.get("title") or h.get("story_title") or "")[:200],
                    author=h.get("author") or "",
                    provenance={"query": q, "points": h.get("points"), "objectID": h.get("objectID")},
                )
            if page + 1 >= data.get("nbPages", 0):
                break
