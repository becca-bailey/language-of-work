"""Founder blog (firm register, subtype=founder_blog) via HEY World.

world.hey.com/<handle> is a server-rendered paginated index (25 posts/page,
cursor-based `?page=` next link). Post pages are plain HTML with the
publication date as visible text ("July 21, 2026") and clean Trafilatura
extraction (byline/footer boilerplate is stripped automatically).

Every post is cached raw at data/<case>/raw_posts/{slug}.json before any
chunking — HEY World posts get edited and deleted, so the cache plus
fetched_at is the evidence record quotes are anchored to. Downstream,
paragraph-sized chunks feed the shared pipeline, but post-level analyses
(the group-reference classifier) read the raw cache's full text, not chunks,
so sub-20-word paragraphs are only absent from the chunk corpus.

Wayback availability fallback per post covers pages that 404 between index
enumeration and fetch. Deleted posts absent from the index entirely are NOT
recovered here (a CDX sweep is a flagged follow-up, not part of this module).
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from typing import Iterator
from urllib.parse import urlparse

import httpx
import trafilatura

from ..config import company_dir
from .base import ExploreResult, SourceRecord, get

NAME = "hey_world"
REGISTER = "firm"

MIN_CHUNK_WORDS = 20
MAX_INDEX_PAGES = 200  # loop backstop; ~25 posts/page
REQUEST_INTERVAL_S = 1.5
AVAIL_URL = "https://archive.org/wayback/available"

_last_request_at = 0.0

# Visible publication date, e.g. <p class="txt--x-small ...">July 21, 2026</p>.
# Single-digit days are space-padded ("March  7, 2024"), hence \s+.
_DATE_RE = re.compile(r">\s*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})\s*<")
_TITLE_RE = re.compile(r"<title>([^<]*)</title>")
# Post slugs end in an 8-hex code; the avatar link (/handle/avatar-<40hex>) must not match.
_SLUG_TAIL = re.compile(r"-[0-9a-f]{8}$")


def _throttle() -> None:
    global _last_request_at
    wait = REQUEST_INTERVAL_S - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _cfg(cfg: dict) -> dict:
    return cfg.get("hey_world", {})


def _handle(cfg: dict) -> str:
    return urlparse(_cfg(cfg)["index_url"]).path.strip("/")


def _enumerate_posts(cfg: dict, client: httpx.Client) -> list[str]:
    """Walk the paginated index; return post slugs, newest first."""
    index_url = _cfg(cfg)["index_url"]
    handle = _handle(cfg)
    post_re = re.compile(rf'href="/{re.escape(handle)}/([a-z0-9\-]+)"')
    next_re = re.compile(
        rf'href="(https://world\.hey\.com/{re.escape(handle)}\?page=[^"]+)"'
    )
    slugs: list[str] = []
    seen: set[str] = set()
    url = index_url
    for _ in range(MAX_INDEX_PAGES):
        _throttle()
        resp = get(client, url)
        if resp.status_code != 200:
            break
        page_new = 0
        for slug in post_re.findall(resp.text):
            if slug.startswith("avatar-") or not _SLUG_TAIL.search(slug):
                continue
            if slug not in seen:
                seen.add(slug)
                slugs.append(slug)
                page_new += 1
        nxt = next_re.search(resp.text)
        if not nxt or page_new == 0:
            break
        url = nxt.group(1)
    return slugs


def _parse_post(html: str) -> tuple[str, str, str]:
    """(title, iso_date, text) from a post page; empty strings where absent."""
    title_m = _TITLE_RE.search(html)
    title = title_m.group(1).strip() if title_m else ""
    date_iso = ""
    date_m = _DATE_RE.search(html)
    if date_m:
        try:
            normalized = " ".join(date_m.group(1).split())
            date_iso = datetime.strptime(normalized, "%B %d, %Y").date().isoformat()
        except ValueError:
            pass
    text = trafilatura.extract(html, include_comments=False, include_tables=False) or ""
    return title, date_iso, text


def _wayback_html(client: httpx.Client, url: str) -> str:
    """Nearest archived copy of a post that 404s live, or ''."""
    _throttle()
    try:
        resp = get(client, AVAIL_URL, params={"url": url})
        snap = (resp.json().get("archived_snapshots") or {}).get("closest")
        if not (snap and snap.get("available") and snap.get("status") == "200"):
            return ""
        ts = snap["timestamp"]
        raw_url = snap["url"].replace(f"/web/{ts}/", f"/web/{ts}id_/", 1)
        _throttle()
        raw = get(client, raw_url)
        return raw.text if raw.status_code == 200 else ""
    except Exception:
        return ""


def _fetch_post(cfg: dict, client: httpx.Client, slug: str) -> dict | None:
    """Cache-first raw post record; None if unreachable live and in Wayback."""
    cache_dir = company_dir(cfg["case"]) / "raw_posts"
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{slug}.json"
    if path.exists() and not _cfg(cfg).get("refresh"):
        return json.loads(path.read_text())

    url = f"https://world.hey.com/{_handle(cfg)}/{slug}"
    via_wayback = False
    _throttle()
    try:
        resp = get(client, url)
        html = resp.text if resp.status_code == 200 else ""
    except Exception:
        html = ""
    if not html.strip():
        html = _wayback_html(client, url)
        via_wayback = bool(html.strip())
    if not html.strip():
        print(f"    ! {slug}: unreachable live and in Wayback, skipped")
        return None

    title, date_iso, text = _parse_post(html)
    record = {
        "slug": slug,
        "url": url,
        "title": title,
        "date": date_iso,
        "text": text,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "via_wayback": via_wayback,
        "html_sha1": hashlib.sha1(html.encode()).hexdigest(),
    }
    path.write_text(json.dumps(record, ensure_ascii=False, indent=1))
    return record


def _paragraphs(text: str) -> list[str]:
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    return [p for p in paras if len(p.split()) >= MIN_CHUNK_WORDS]


def explore(cfg: dict, client: httpx.Client, limit: int = 10) -> list[ExploreResult]:
    """Census: enumerate the full index without fetching post bodies."""
    slugs = _enumerate_posts(cfg, client)
    samples = [
        {"date": "", "title": slug, "url": f"https://world.hey.com/{_handle(cfg)}/{slug}", "snippet": ""}
        for slug in slugs[:limit]
    ]
    return [
        ExploreResult(
            source=NAME,
            register=REGISTER,
            query=_cfg(cfg)["index_url"],
            total=len(slugs),
            samples=samples,
            note="post slugs enumerated from paginated index (newest first); dates resolved at fetch",
        )
    ]


def fetch(cfg: dict, client: httpx.Client) -> Iterator[SourceRecord]:
    author = _cfg(cfg).get("author", _handle(cfg))
    subtype = _cfg(cfg).get("subtype", "founder_blog")
    slugs = _enumerate_posts(cfg, client)
    print(f"    index: {len(slugs)} posts enumerated")
    for slug in slugs:
        rec = _fetch_post(cfg, client, slug)
        if rec is None:
            continue
        for i, para in enumerate(_paragraphs(rec["text"])):
            yield SourceRecord(
                source=NAME,
                register=REGISTER,
                url=rec["url"],
                text=para,
                observed_date=rec["date"],
                title=rec["title"],
                author=author,
                subtype=subtype,
                provenance={
                    "post_slug": slug,
                    "post_url": rec["url"],
                    "post_title": rec["title"],
                    "position": i,
                    "via_wayback": rec["via_wayback"],
                },
            )
