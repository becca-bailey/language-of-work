"""Longitudinal canon (firm register) via the Wayback **Availability API**.

The canon — the Automattic Creed, the Menlo Way / about pages — is the spine of
the study: H3/H5 measure how much it drifts (or doesn't) over time. This resolves
*known* canon URLs (cfg["canon_urls"]) to their nearest archived snapshot per
target year, then fetches the original bytes (id_ flag) and runs them through the
same `chunk_html` the rest of the pipeline uses, so canon text converges into the
shared chunk record.

Per-URL, cheap, retried — the resilient path (plan §0): the CDX domain sweep timed
out from this environment (290–485 s), while the Availability API answers per-URL
in ~0.1 s. Snapshots are deduped by resolved timestamp, so target years that map to
the same archived capture (nothing newer exists yet) collapse to one record set —
which is itself the "canon unchanged across these years" signal H3 wants.
"""

from __future__ import annotations

import gzip
import re
import time
from typing import Iterator

import httpx

from ..chunking import chunk_html
from ..config import company_dir
from ..wayback import (
    Capture,
    cdx_query,
    dedup_by_digest,
    fetch_capture,
    select_per_year,
)
from .base import ExploreResult, SourceRecord, get

NAME = "wayback"
REGISTER = "firm"

AVAIL_URL = "https://archive.org/wayback/available"
DEFAULT_FROM_YEAR = 2008
DEFAULT_PER_YEAR = 3  # CDX multi-snapshot: captures per canon URL per year
REQUEST_INTERVAL_S = 2.0  # polite rate limit; archive.org throttles sustained bursts
_last_request_at = 0.0

_BLOG_DATE = re.compile(r"/(\d{4})/(\d{2})/")
# Blog listing/navigation paths to skip when enumerating posts (we want articles only).
_SKIP_POST = re.compile(
    r"/(?:author|tag|category|page)/|comment-page|/feed|/blog/?$|/blog/\d{4}/?$|/blog/\d{4}/\d{2}/?$",
    re.I,
)


def _throttle() -> None:
    global _last_request_at
    wait = REQUEST_INTERVAL_S - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _canon_urls(cfg: dict) -> list[str]:
    return cfg.get("canon_urls", [])


def _canon_prefixes(cfg: dict) -> list[str]:
    """URL prefixes (e.g. a blog root) to enumerate into individual dated pages."""
    return cfg.get("canon_prefixes", [])


def _deep(cfg: dict) -> bool:
    """CDX multi-snapshot mode: thicker per-year coverage + prefix enumeration.

    Opt-in (canon_deep / canon_per_year / canon_prefixes) so the cheaper
    Availability path stays the default for cases that don't need the depth.
    """
    return bool(
        cfg.get("canon_deep")
        or cfg.get("canon_per_year")
        or cfg.get("canon_prefixes")
    )


def _post_date(original: str) -> str:
    """ISO date parsed from a dated blog path (/YYYY/MM/slug), else ''."""
    m = _BLOG_DATE.search(original)
    return f"{m.group(1)}-{m.group(2)}-01" if m else ""


def _target_years(cfg: dict) -> list[int]:
    from datetime import date

    frm = cfg.get("canon_from_year", DEFAULT_FROM_YEAR)
    return list(range(frm, date.today().year + 1))


def _closest(client: httpx.Client, url: str, timestamp: str) -> dict | None:
    """Availability API: nearest archived snapshot to `timestamp` for `url`."""
    _throttle()
    resp = get(client, AVAIL_URL, params={"url": url, "timestamp": timestamp})
    snap = (resp.json().get("archived_snapshots") or {}).get("closest")
    if snap and snap.get("available") and snap.get("status") == "200":
        return snap  # {url, timestamp, status, available}
    return None


def _raw_url(snap: dict) -> str:
    """The Availability `url` is a replay URL (…/web/TS/ORIGINAL); insert the id_
    flag after the timestamp to get the un-rewritten original bytes."""
    ts = snap["timestamp"]
    return snap["url"].replace(f"/web/{ts}/", f"/web/{ts}id_/", 1)


def _raw_bytes(client: httpx.Client, snap: dict) -> bytes:
    """Original capture bytes, no Wayback rewriting (id_ flag); gzip-tolerant."""
    _throttle()
    resp = get(client, _raw_url(snap), headers={"Accept-Encoding": "identity"})
    resp.raise_for_status()
    body = resp.content
    if "gzip" in resp.headers.get("content-encoding", "").lower():
        try:
            body = gzip.decompress(body)
        except OSError:
            pass
    return body


def _iso(ts: str) -> str:
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"


def explore(cfg: dict, client: httpx.Client, limit: int = 10) -> list[ExploreResult]:
    """Cheap census: which canon URLs are archived, and over what span."""
    results = []
    for url in _canon_urls(cfg):
        seen: dict[str, str] = {}  # snapshot_ts -> target year
        for year in _target_years(cfg):
            snap = _closest(client, url, str(year))
            if snap:
                seen.setdefault(snap["timestamp"], str(year))
        tss = sorted(seen)
        samples = [
            {"date": _iso(ts), "title": url, "url": f"https://web.archive.org/web/{ts}/{url}", "snippet": ""}
            for ts in tss[:limit]
        ]
        results.append(
            ExploreResult(
                source=NAME,
                register=REGISTER,
                query=url,
                total=len(tss),
                date_min=_iso(tss[0]) if tss else "",
                date_max=_iso(tss[-1]) if tss else "",
                samples=samples,
                note="distinct archived canon snapshots (deduped by resolved timestamp)",
            )
        )
    return results


def fetch(cfg: dict, client: httpx.Client) -> Iterator[SourceRecord]:
    if _deep(cfg):
        yield from _fetch_cdx(cfg, client)
    else:
        yield from _fetch_availability(cfg, client)


def _fetch_availability(cfg: dict, client: httpx.Client) -> Iterator[SourceRecord]:
    """One nearest snapshot per canon URL per year (cheap, resilient default)."""
    for url in _canon_urls(cfg):
        seen_ts: set[str] = set()
        for year in _target_years(cfg):
            snap = _closest(client, url, str(year))
            if not snap or snap["timestamp"] in seen_ts:
                continue
            seen_ts.add(snap["timestamp"])
            ts = snap["timestamp"]
            try:
                html = _raw_bytes(client, snap)
            except Exception as e:
                print(f"    ! {url}@{ts} fetch failed: {e}")
                continue
            for ch in chunk_html(html, source_url=url, timestamp=ts):
                if not ch["text"].strip():
                    continue
                yield SourceRecord(
                    source=NAME,
                    register=REGISTER,
                    url=f"https://web.archive.org/web/{ts}/{url}",
                    text=ch["text"],
                    observed_date=_iso(ts),
                    title=ch["heading"] or url,
                    provenance={
                        "canon": True,
                        "canon_url": url,
                        "snapshot_ts": ts,
                        "resolved_from_year": year,
                        "position": ch["position"],
                    },
                )


def _records_from_capture(
    client: httpx.Client,
    cap: Capture,
    raw_dir,
    *,
    canon_url: str,
    observed_date: str,
    subtype: str,
    canon: bool,
) -> Iterator[SourceRecord]:
    """Fetch one capture's bytes and yield a record per non-empty chunk."""
    ts = cap.timestamp
    try:
        path, _ = fetch_capture(client, cap, raw_dir)
        html = path.read_bytes()
    except Exception as e:
        print(f"    ! {cap.original}@{ts} fetch failed: {e}")
        return
    for ch in chunk_html(html, source_url=canon_url, timestamp=ts):
        if not ch["text"].strip():
            continue
        yield SourceRecord(
            source=NAME,
            register=REGISTER,
            url=f"https://web.archive.org/web/{ts}/{cap.original}",
            text=ch["text"],
            observed_date=observed_date or _iso(ts),
            title=ch["heading"] or canon_url,
            subtype=subtype,
            provenance={
                "canon": canon,
                "canon_url": canon_url,
                "snapshot_ts": ts,
                "position": ch["position"],
            },
        )


def _fetch_cdx(cfg: dict, client: httpx.Client) -> Iterator[SourceRecord]:
    """Deep firm corpus via CDX: multi-snapshot canon pages + prefix-enumerated
    sub-pages (e.g. the blog). Reuses the Project-2 CDX/raw-fetch helpers."""
    raw_dir = company_dir(cfg["case"]) / "raw_html"
    raw_dir.mkdir(parents=True, exist_ok=True)
    per_year = int(cfg.get("canon_per_year", DEFAULT_PER_YEAR))

    # 1) Canon pages: up to `per_year` distinct-content snapshots per year, so the
    #    same page's wording is sampled as it evolves across the timeline.
    for url in _canon_urls(cfg):
        try:
            caps = cdx_query(client, url, match_type="exact")
        except Exception as e:
            print(f"    ! cdx {url} failed: {e}")
            continue
        uniq, _ = dedup_by_digest(caps)
        selected = select_per_year(uniq, per_year=per_year)
        n = sum(len(v) for v in selected.values())
        print(f"    {url}: {len(caps)} caps -> {len(uniq)} uniq -> {n} sampled")
        for caps_in_year in selected.values():
            for cap in caps_in_year:
                yield from _records_from_capture(
                    client, cap, raw_dir,
                    canon_url=url, observed_date="", subtype="", canon=True,
                )

    # 2) Prefix enumeration (the blog): one earliest distinct-content capture per
    #    article, dated from its path (/YYYY/MM/) so each post sits on the timeline
    #    at publication, not at archive time.
    for prefix in _canon_prefixes(cfg):
        try:
            caps = cdx_query(client, prefix, match_type="prefix")
        except Exception as e:
            print(f"    ! cdx prefix {prefix} failed: {e}")
            continue
        by_post: dict[str, list[Capture]] = {}
        for cap in caps:
            path_only = cap.original.split("?", 1)[0]
            if _SKIP_POST.search(path_only):
                continue
            key = path_only.split("//", 1)[-1].split("/", 1)[-1].rstrip("/")
            by_post.setdefault(key, []).append(cap)
        print(f"    {prefix}*: {len(caps)} caps -> {len(by_post)} posts")
        for caps_for_post in by_post.values():
            uniq, _ = dedup_by_digest(caps_for_post)
            cap = uniq[0]  # earliest distinct-content capture ≈ as-published
            yield from _records_from_capture(
                client, cap, raw_dir,
                canon_url=cap.original.split("?", 1)[0],
                observed_date=_post_date(cap.original),
                subtype="blog", canon=False,
            )
