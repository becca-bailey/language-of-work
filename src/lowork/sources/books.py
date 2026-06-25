"""Book metadata via Open Library — canon (firm register) + codification dates.

Keyless and reliable. (Google Books was the first choice but Google set the
no-key daily quota to 0 in 2026 — it now 429s for everyone without an API key;
see data/<case>/source_map.md provenance.) Open Library gives publication year
(a codification anchor) and a crowd/publisher description; never full text.
"""

from __future__ import annotations

from typing import Iterator

import httpx

from .base import ExploreResult, SourceRecord, get

NAME = "books"
REGISTER = "firm"

SEARCH_URL = "https://openlibrary.org/search.json"
SEARCH_FIELDS = "title,author_name,first_publish_year,publish_year,key"


def _queries(cfg: dict) -> list[str]:
    return cfg.get("queries", {}).get(NAME) or [cfg.get("display_name") or cfg["case"]]


def _search(client: httpx.Client, query: str, limit: int = 10) -> dict:
    params = {"q": query, "limit": limit, "fields": SEARCH_FIELDS}
    return get(client, SEARCH_URL, params=params).json()


def _matches(query: str, doc: dict) -> bool:
    """Precision gate: Open Library relevance-ranks loosely and returns off-topic
    docs (e.g. 'Joy Inc Sheridan' surfaces A Midsummer Night's Dream). Keep a doc
    only if every meaningful query token appears in its title+author — for
    codification-anchor lookups precision matters far more than recall."""
    hay = f"{doc.get('title', '')} {' '.join(doc.get('author_name', []))}".lower()
    tokens = [t for t in query.lower().split() if len(t) > 2]
    return all(t in hay for t in tokens)


def _work_description(client: httpx.Client, work_key: str) -> str:
    """Fetch the work record for its description (firm/publisher-register copy)."""
    try:
        data = get(client, f"https://openlibrary.org{work_key}.json").json()
    except Exception:
        return ""
    desc = data.get("description")
    if isinstance(desc, dict):
        desc = desc.get("value", "")
    return (desc or "").strip()


def explore(cfg: dict, client: httpx.Client, limit: int = 10) -> list[ExploreResult]:
    results = []
    for q in _queries(cfg):
        data = _search(client, q, limit=limit)
        docs = data.get("docs", [])
        years = sorted(str(d["first_publish_year"]) for d in docs if d.get("first_publish_year"))
        samples = []
        for d in docs[:limit]:
            samples.append(
                {
                    "date": str(d.get("first_publish_year", "")),
                    "title": (d.get("title") or "")[:120],
                    "url": f"https://openlibrary.org{d.get('key', '')}",
                    "snippet": "",
                    "authors": d.get("author_name", []),
                }
            )
        results.append(
            ExploreResult(
                source=NAME,
                register=REGISTER,
                query=q,
                total=data.get("numFound"),
                date_min=years[0] if years else "",
                date_max=years[-1] if years else "",
                samples=samples,
                note="first_publish_year of top hits = codification-date candidates",
            )
        )
    return results


def fetch(cfg: dict, client: httpx.Client) -> Iterator[SourceRecord]:
    max_results = cfg.get("limits", {}).get(NAME, {}).get("max_results", 10)
    for q in _queries(cfg):
        data = _search(client, q, limit=max_results)
        for d in data.get("docs", []):
            if not _matches(q, d):
                continue
            key = d.get("key", "")
            txt = _work_description(client, key) if key else ""
            if not txt:
                continue
            yield SourceRecord(
                source=NAME,
                register=REGISTER,
                url=f"https://openlibrary.org{key}",
                text=txt,
                observed_date=str(d.get("first_publish_year", "")),
                title=d.get("title", ""),
                author=", ".join(d.get("author_name", [])),
                provenance={"query": q, "work_key": key},
            )
