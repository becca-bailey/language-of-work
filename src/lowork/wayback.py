"""Wayback Machine CDX client and rate-limited raw-content fetcher."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import httpx

CDX_URL = "https://web.archive.org/cdx/search/cdx"
REQUEST_INTERVAL_S = 1.0  # polite rate limit
MAX_RETRIES = 4

_last_request_at = 0.0


def _throttle() -> None:
    global _last_request_at
    wait = REQUEST_INTERVAL_S - (time.monotonic() - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


@dataclass
class Capture:
    urlkey: str
    timestamp: str  # YYYYMMDDhhmmss
    original: str
    mimetype: str
    statuscode: str
    digest: str
    length: int

    @property
    def year(self) -> int:
        return int(self.timestamp[:4])

    @property
    def raw_url(self) -> str:
        """Original bytes, no Wayback toolbar/rewriting (id_ flag)."""
        return f"https://web.archive.org/web/{self.timestamp}id_/{self.original}"

    @property
    def replay_url(self) -> str:
        """Human-viewable replay URL for manual spot-checks."""
        return f"https://web.archive.org/web/{self.timestamp}/{self.original}"

    def to_dict(self) -> dict:
        return asdict(self)


def _get(client: httpx.Client, url: str, params: dict | None = None) -> httpx.Response:
    for attempt in range(MAX_RETRIES):
        _throttle()
        try:
            resp = client.get(url, params=params, timeout=60)
            if resp.status_code in (429, 503):
                time.sleep(5 * (attempt + 1))
                continue
            return resp
        except httpx.TransportError:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"exhausted retries for {url}")


def cdx_query(
    client: httpx.Client,
    url_pattern: str,
    *,
    match_type: str = "exact",
    from_ts: str = "2005",
    to_ts: str | None = None,
    filters: list[str] | None = None,
    collapse: str | None = "timestamp:6",  # ~monthly
) -> list[Capture]:
    if filters is None:
        filters = ["statuscode:200"]
    params: dict = {
        "url": url_pattern,
        "matchType": match_type,
        "output": "json",
        "from": from_ts,
        "fl": "urlkey,timestamp,original,mimetype,statuscode,digest,length",
    }
    if to_ts:
        params["to"] = to_ts
    if filters:
        params["filter"] = filters
    if collapse:
        params["collapse"] = collapse

    resp = _get(client, CDX_URL, params)
    resp.raise_for_status()
    rows = resp.json()
    if not rows:
        return []
    header, *data = rows
    captures = []
    for row in data:
        rec = dict(zip(header, row))
        captures.append(
            Capture(
                urlkey=rec["urlkey"],
                timestamp=rec["timestamp"],
                original=rec["original"],
                mimetype=rec["mimetype"],
                statuscode=rec["statuscode"],
                digest=rec["digest"],
                length=int(rec["length"] or 0),
            )
        )
    return captures


def dedup_by_digest(captures: list[Capture]) -> tuple[list[Capture], dict[str, list[str]]]:
    """Keep the first capture per content digest.

    Returns (unique_captures, digest -> all timestamps map). The timestamp map
    preserves the "page unchanged from X to Y" signal for later analysis.
    """
    seen: dict[str, list[str]] = {}
    unique: list[Capture] = []
    for cap in sorted(captures, key=lambda c: c.timestamp):
        if cap.digest not in seen:
            unique.append(cap)
        seen.setdefault(cap.digest, []).append(cap.timestamp)
    return unique, seen


def select_per_year(captures: list[Capture], per_year: int = 4) -> dict[int, list[Capture]]:
    """Pick up to `per_year` captures spread across each year.

    Targets evenly spaced months (Feb/May/Aug/Nov for 4) and picks the capture
    closest to each target, without reusing a capture.
    """
    by_year: dict[int, list[Capture]] = {}
    for cap in captures:
        by_year.setdefault(cap.year, []).append(cap)

    selected: dict[int, list[Capture]] = {}
    for year, caps in sorted(by_year.items()):
        caps = sorted(caps, key=lambda c: c.timestamp)
        if len(caps) <= per_year:
            selected[year] = caps
            continue
        target_months = [round((i + 0.5) * 12 / per_year) for i in range(per_year)]
        chosen: list[Capture] = []
        pool = caps.copy()
        for month in target_months:
            best = min(pool, key=lambda c: abs(int(c.timestamp[4:6]) - month))
            chosen.append(best)
            pool.remove(best)
        selected[year] = sorted(chosen, key=lambda c: c.timestamp)
    return selected


def html_path(raw_dir: Path, cap: Capture) -> Path:
    url_hash = hashlib.sha256(cap.original.encode()).hexdigest()[:12]
    return raw_dir / f"{cap.timestamp}_{url_hash}.html"


def fetch_capture(client: httpx.Client, cap: Capture, raw_dir: Path) -> tuple[Path, int]:
    """Download original bytes for a capture. Skips if already on disk."""
    path = html_path(raw_dir, cap)
    if path.exists():
        return path, 0
    resp = _get(client, cap.raw_url)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} for {cap.raw_url}")
    path.write_bytes(resp.content)
    return path, len(resp.content)
