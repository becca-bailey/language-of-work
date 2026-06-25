"""Reddit — worker-register testimony.

Requires OAuth: the keyless .json endpoints are blocked (Reddit serves the HTML
app shell, not JSON, to unauthenticated/datacenter clients as of 2026). Set
REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET (register a "script"/"web app" at
https://www.reddit.com/prefs/apps) and this uses app-only client-credentials
OAuth against oauth.reddit.com. Without creds it raises a clear setup message.

Reddit is noisier than HN: most hits are *community* discussion-about-the-company,
not verified first-person employee testimony, so every record is tagged
subtype="community" plus full provenance (subreddit, score, num_comments) — the
reliability signal lives in the metadata, to be weighted/filtered downstream, not
in a discard flag.

Config (data/<case>/sources.json):
  queries.reddit : list of search terms
  subreddits     : optional list to scope the search; [] = site-wide search
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Iterator

import httpx

from .base import DEFAULT_TIMEOUT, ExploreResult, SourceRecord, get

NAME = "reddit"
REGISTER = "worker"
SUBTYPE = "community"

UA = "language-of-work:project3:0.1 (research; contact via repo)"
PAGE_LIMIT = 25

_token: str | None = None


class RedditAuthError(RuntimeError):
    pass


def _get_token(client: httpx.Client) -> str:
    """App-only (client-credentials) OAuth bearer token; cached per process."""
    global _token
    if _token:
        return _token
    cid, secret = os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET")
    if not (cid and secret):
        raise RedditAuthError(
            "keyless Reddit is blocked; set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET "
            "(register a script app at https://www.reddit.com/prefs/apps) to enable this source"
        )
    resp = client.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(cid, secret),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": UA},
        timeout=DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()
    _token = resp.json()["access_token"]
    return _token


def _queries(cfg: dict) -> list[str]:
    return cfg.get("queries", {}).get(NAME) or [cfg.get("display_name") or cfg["case"]]


def _subreddits(cfg: dict) -> list[str]:
    return cfg.get("subreddits", [])  # [] => site-wide


def _iso(created_utc: float) -> str:
    return datetime.fromtimestamp(created_utc, tz=timezone.utc).date().isoformat()


def _search(client: httpx.Client, query: str, subreddit: str = "", after: str = "") -> dict:
    token = _get_token(client)  # raises RedditAuthError if no creds
    headers = {"User-Agent": UA, "Authorization": f"bearer {token}"}
    if subreddit:
        url = f"https://oauth.reddit.com/r/{subreddit}/search"
        params = {"q": query, "restrict_sr": 1, "limit": PAGE_LIMIT, "sort": "relevance"}
    else:
        url = "https://oauth.reddit.com/search"
        params = {"q": query, "limit": PAGE_LIMIT, "sort": "relevance", "type": "link"}
    if after:
        params["after"] = after
    return get(client, url, params=params, headers=headers).json()


def _post_text(d: dict) -> str:
    return " ".join(p for p in (d.get("title") or "", d.get("selftext") or "") if p).strip()


def _scopes(cfg: dict) -> list[str]:
    return _subreddits(cfg) or [""]  # "" = site-wide


def explore(cfg: dict, client: httpx.Client, limit: int = 15) -> list[ExploreResult]:
    results = []
    for q in _queries(cfg):
        for sub in _scopes(cfg):
            data = _search(client, q, subreddit=sub)
            children = [c["data"] for c in data.get("data", {}).get("children", [])]
            dates = sorted(_iso(c["created_utc"]) for c in children if c.get("created_utc"))
            samples = []
            for d in children[:limit]:
                samples.append(
                    {
                        "date": _iso(d["created_utc"]) if d.get("created_utc") else "",
                        "title": (d.get("title") or "")[:120],
                        "url": "https://www.reddit.com" + (d.get("permalink") or ""),
                        "snippet": (d.get("selftext") or "")[:200],
                        "subreddit": d.get("subreddit"),
                        "score": d.get("score"),
                    }
                )
            label = f"{q} @ r/{sub}" if sub else f"{q} (site-wide)"
            results.append(
                ExploreResult(
                    source=NAME,
                    register=REGISTER,
                    query=label,
                    total=None,  # Reddit search gives no total; len(samples) is a floor
                    date_min=dates[0] if dates else "",
                    date_max=dates[-1] if dates else "",
                    samples=samples,
                    note="community discussion (subtype=community); Reddit reports no total — counts are a floor",
                )
            )
    return results


def fetch(cfg: dict, client: httpx.Client) -> Iterator[SourceRecord]:
    max_pages = cfg.get("limits", {}).get(NAME, {}).get("max_pages", 5)
    for q in _queries(cfg):
        for sub in _scopes(cfg):
            after = ""
            for _ in range(max_pages):
                data = _search(client, q, subreddit=sub, after=after)
                children = [c["data"] for c in data.get("data", {}).get("children", [])]
                if not children:
                    break
                for d in children:
                    txt = _post_text(d)
                    if not txt:
                        continue
                    yield SourceRecord(
                        source=NAME,
                        register=REGISTER,
                        subtype=SUBTYPE,
                        url="https://www.reddit.com" + (d.get("permalink") or ""),
                        text=txt,
                        observed_date=_iso(d["created_utc"]) if d.get("created_utc") else "",
                        title=(d.get("title") or "")[:200],
                        author=d.get("author") or "",
                        provenance={
                            "query": q,
                            "subreddit": d.get("subreddit"),
                            "score": d.get("score"),
                            "num_comments": d.get("num_comments"),
                            "id": d.get("id"),
                        },
                    )
                after = data.get("data", {}).get("after") or ""
                if not after:
                    break
