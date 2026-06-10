"""Harvest careers-page links from archived HTML for one-hop expansion."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

# Content sub-pages worth fetching (case-insensitive path match)
CONTENT_PATTERNS = re.compile(
    r"(teams?|students?|benefits|culture|life|locations?|how-we|diversity|"
    r"belonging|perks|values|mission|students|intern|grad|veterans|"
    r"disability|accessibility|care-for|hiring|about)",
    re.I,
)

# Individual job listings and search surfaces — not mission corpus
JOB_PATTERNS = re.compile(
    r"(/jobs/results|/jobs/\d|/job/\d|/positions?/|joblisting|"
    r"search\?|/api/|\.pdf$|\.jpg$|\.png$|\.css$|\.js$|mailto:|javascript:)",
    re.I,
)

def _normalize_url(href: str, base: str, *, hosts: tuple[str, ...]) -> str | None:
    if not href or href.startswith(("#", "mailto:", "javascript:")):
        return None
    full = urljoin(base, href)
    parsed = urlparse(full)
    if parsed.scheme not in ("http", "https"):
        return None
    host = parsed.netloc.lower().removeprefix("www.")
    if not any(host == h or host.endswith("." + h) for h in hosts):
        return None
    path = parsed.path.rstrip("/") + ("/" if parsed.path.endswith("/") else "")
    if not path:
        path = "/"
    # Rebuild without query/fragment for dedup
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def is_content_url(url: str) -> bool:
    if JOB_PATTERNS.search(url):
        return False
    return bool(CONTENT_PATTERNS.search(url))


def extract_links(
    html: str | bytes, base_url: str, *, hosts: tuple[str, ...], cap: int = 10
) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    seen: set[str] = set()
    out: list[str] = []
    for a in soup.find_all("a", href=True):
        norm = _normalize_url(a["href"], base_url, hosts=hosts)
        if not norm or norm in seen:
            continue
        if not is_content_url(norm):
            continue
        seen.add(norm)
        out.append(norm)
        if len(out) >= cap:
            break
    return out


def harvest_from_manifest(
    raw_dir: Path,
    captures: list[dict],
    *,
    hosts: tuple[str, ...],
    cap_per_page: int = 10,
) -> dict[str, list[dict]]:
    """Return {discovered_url: [{parent_timestamp, parent_url, html_file}, ...]}."""
    by_url: dict[str, list[dict]] = defaultdict(list)
    for cap in captures:
        if "html_file" not in cap:
            continue
        path = raw_dir / cap["html_file"]
        if not path.exists():
            continue
        html = path.read_bytes()
        base = cap["original"]
        if not base.startswith("http"):
            base = "https://" + base.lstrip("/")
        for link in extract_links(html, base, hosts=hosts, cap=cap_per_page):
            by_url[link].append(
                {
                    "parent_timestamp": cap["timestamp"],
                    "parent_url": cap["original"],
                    "html_file": cap["html_file"],
                }
            )
    return dict(by_url)
