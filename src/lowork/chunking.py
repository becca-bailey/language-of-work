"""Structure-aware chunking: walk the DOM, emit heading+content chunks.

Chunks on document structure, not token windows. Each chunk carries the
nearest heading as context. Targets CHUNK_MIN_WORDS..CHUNK_MAX_WORDS; merges
fragments within a section and splits oversized sections at paragraph
boundaries. Trafilatura runs in parallel as a coverage comparison.
"""

from __future__ import annotations

import difflib
import hashlib
import re
from dataclasses import dataclass

import trafilatura
from bs4 import BeautifulSoup, Tag

from .config import CHUNK_MAX_WORDS, CHUNK_MIN_WORDS

STRIP_TAGS = ["script", "style", "noscript", "iframe", "svg", "template", "form"]
SKIP_CONTAINERS = ["nav", "footer"]
HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]
TEXT_TAGS = ["p", "li", "td", "blockquote", "dd", "dt", "figcaption"]

_ws = re.compile(r"\s+")


def _clean(text: str) -> str:
    return _ws.sub(" ", text).strip()


def _word_count(text: str) -> int:
    return len(text.split())


@dataclass
class Section:
    heading: str
    paragraphs: list[str]


_TERMINAL = re.compile(r"[.!?…]")

# A nav run: 3+ short fragments joined by separators (" - ", "»", "|", "·"),
# e.g. "Mountain View - New York - Ann Arbor - all U.S. locations » International locations »"
_NAV_RUN = re.compile(
    # Ends at the last separator: better to leave a few junk words than eat prose.
    r"(?:[^\s][^|»·]{0,45}?\s*(?:\s[-–—|·]\s|»)\s*){3,}"
)


def strip_nav_runs(text: str) -> str:
    """Remove separator-linked link runs embedded in a paragraph, keep prose."""
    return _ws.sub(" ", _NAV_RUN.sub(" ", text)).strip()


# Inline e-commerce / careers-page chrome merged into body text on older captures.
_LEADING_CHROME = [
    re.compile(r"^Hello\.?\s*Sign in[^.]*\.?\s*", re.I),
    re.compile(r"^Your Amazon Careers Profile\s*Sign in to existing careers profile\s*", re.I),
    re.compile(r"^New customer\?\s*Start here\s*\.?\s*", re.I),
    re.compile(
        r"^FREE (?:Two-Day|2-Day) Shipping[^.]*\.?\s*|"
        r"^Save on everything you need for college[^.]*\.?\s*",
        re.I,
    ),
    re.compile(r"^Sponsored by [^.]+\s*", re.I),
    re.compile(r"^Your Amazon\.com\s+", re.I),
    re.compile(
        r"^(?:Today's Deals|Gifts & Wish Lists|Gift Cards|Your Account)\s*"
        r"(?:\|\s*Help\s*)?",
        re.I,
    ),
]

_CAREERS_MENU_RUN = re.compile(
    r"^(?:Search for Jobs(?:\s+at Amazon)?|Apply Now\s*›|Careers Home|"
    r"About Amazon|Amazon Values|Inside Amazon|Locations|Benefits|"
    r"University Recruiting(?:\s+Home)?|Military Recruiting(?:\s+Home)?|"
    r"How to Apply|FAQ|Disability Accommodations|E-Verify|Code Ninjas|"
    r"Amazonians on Amazon|Careers at Amazon)\s*"
    r"(?:›|\||\s)*",
    re.I,
)

_MISSION_ANCHOR = re.compile(
    r"(?:At Amazon,|Work hard\. Have fun\.|Build your future with Amazon|"
    r"Invent the future with Amazon|Our mission is to be|"
    r"We're a company of pioneers|Come build the future|"
    r"Every Amazonian,|Can one conversation change the world|"
    r"At Google, our strategy|Enjoy what you do|Let's work together|"
    r"Google's mission is)",
    re.I,
)

_CHROME_START = re.compile(
    r"^(?:Hello\.?\s*Sign in|New customer\?|FREE (?:Two-Day|2-Day)|"
    r"Your Amazon\.com|Today's Deals|Sponsored by|com\b)",
    re.I,
)

_NAVISH = re.compile(
    r"\b(?:sign in|today's deals|gift cards|your account|apply now|"
    r"careers home|careers at amazon|university recruiting)\b",
    re.I,
)

_TRAILING_CHROME = [
    re.compile(r"\s*Amazon\.com Home\s*\|\s*Directory of All Stores.*$", re.I),
    re.compile(r"\s*Your Recent History\s*\(.*$", re.I),
    re.compile(r"\s*›\s*View and edit your browsing history.*$", re.I),
    re.compile(
        r"\s*Amazon ranked America's most reputable company!.*$",
        re.I,
    ),
    re.compile(r"\s*After viewing product detail pages.*$", re.I),
    re.compile(r"\s*Conditions of Use Privacy Notice.*$", re.I),
    # International store-directory footer on old amazon.com pages
    re.compile(r"\s*Canada China France Germany Italy Japan United Kingdom.*$", re.I),
]


def _prefix_is_navish(prefix: str) -> bool:
    if not prefix.strip():
        return False
    hits = len(_NAVISH.findall(prefix))
    words = len(prefix.split())
    return hits >= 2 or (hits >= 1 and words >= 8)


def strip_site_chrome(text: str) -> str:
    """Strip leading/trailing site chrome inlined in old careers-page captures."""
    t = text
    for _ in range(12):
        prev = t
        for pat in _LEADING_CHROME:
            t = pat.sub("", t, count=1)
        while _CAREERS_MENU_RUN.match(t):
            t = _CAREERS_MENU_RUN.sub("", t, count=1)
        t = re.sub(r"^com\s+", "", t, flags=re.I)
        t = _ws.sub(" ", t).strip()
        if t == prev:
            break

    m = _MISSION_ANCHOR.search(t)
    if m and m.start() > 0:
        prefix = t[: m.start()]
        has_menu_tail = bool(
            re.search(r"\b(?:How to Apply|FAQ|Careers Home|Help)\b", prefix, re.I)
        )
        if (
            _CHROME_START.match(t)
            or _CAREERS_MENU_RUN.match(t)
            or _prefix_is_navish(prefix)
            or has_menu_tail
        ):
            t = t[m.start() :].strip()

    for pat in _TRAILING_CHROME:
        t = pat.sub("", t).strip()

    return _ws.sub(" ", t).strip()


def _is_pure_link_list(text: str) -> bool:
    """Punctuation-free TitleCase lists like department/location name rows."""
    if _TERMINAL.search(text):
        return False
    words = text.split()
    if len(words) < 6:
        return False
    alpha = [w for w in words if w[0].isalpha()]
    return bool(alpha) and sum(w[0].isupper() for w in alpha) / len(alpha) >= 0.6


def _is_navigation(el: Tag) -> bool:
    if el.name in SKIP_CONTAINERS:
        return True
    role = el.get("role", "")
    if role in ("navigation", "banner", "contentinfo"):
        return True
    classes = " ".join(el.get("class", []) + [el.get("id") or ""]).lower()
    return bool(re.search(r"\b(nav|menu|footer|breadcrumb|cookie|sitemap)\b", classes))


def extract_sections(html: str | bytes) -> list[Section]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(STRIP_TAGS):
        tag.decompose()
    for el in soup.find_all(_is_navigation):
        el.decompose()

    body = soup.body or soup
    sections: list[Section] = [Section(heading="", paragraphs=[])]

    for el in body.find_all(HEADING_TAGS + TEXT_TAGS):
        # Skip text nested inside another text tag (e.g. p inside li) to avoid duplication
        if el.find_parent(TEXT_TAGS):
            continue
        text = _clean(el.get_text(" "))
        if not text:
            continue
        if el.name in HEADING_TAGS:
            sections.append(Section(heading=text, paragraphs=[]))
        else:
            sections[-1].paragraphs.append(text)

    return [s for s in sections if s.paragraphs]


def sections_to_chunks(sections: list[Section]) -> list[dict]:
    """Merge/split section paragraphs into chunks of CHUNK_MIN..CHUNK_MAX words.

    Very short orphan fragments (< 10 words with no sibling content, e.g.
    button labels) are dropped as junk; the classifier catches the rest.
    """
    chunks: list[dict] = []
    for section in sections:
        buf: list[str] = []
        buf_words = 0

        def flush() -> None:
            nonlocal buf, buf_words
            if not buf:
                return
            text = " ".join(buf)
            if _word_count(text) >= 10:
                chunks.append({"heading": section.heading, "text": text})
            buf, buf_words = [], 0

        for para in section.paragraphs:
            if _is_pure_link_list(para):
                continue
            para = strip_site_chrome(strip_nav_runs(para))
            if _word_count(para) < 6:
                continue
            pw = _word_count(para)
            if buf_words + pw > CHUNK_MAX_WORDS and buf_words >= CHUNK_MIN_WORDS:
                flush()
            buf.append(para)
            buf_words += pw
        flush()
    return chunks


def chunk_html(html: str | bytes, *, source_url: str, timestamp: str) -> list[dict]:
    chunks = sections_to_chunks(extract_sections(html))
    out = []
    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        chunk_id = hashlib.sha256(f"{timestamp}|{source_url}|{i}|{text}".encode()).hexdigest()[:16]
        out.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "heading": chunk["heading"],
                "source_url": source_url,
                "timestamp": timestamp,
                "year": int(timestamp[:4]),
                "word_count": _word_count(text),
                "position": i,
            }
        )
    return out


def trafilatura_words(html: str | bytes) -> int:
    """Trafilatura extraction word count, as a coverage comparison."""
    if isinstance(html, bytes):
        html = html.decode("utf-8", errors="replace")
    text = trafilatura.extract(html) or ""
    return _word_count(text)


NEAR_DUP_TEXT_RATIO = 0.92


def dedup_chunks(chunks: list[dict], *, threshold: float = NEAR_DUP_TEXT_RATIO) -> list[dict]:
    """Drop near-duplicate chunks, keeping the longest version of each.

    Exact-text dedup first, then SequenceMatcher ratio for snapshots of the
    same page that differ slightly (nav trimming, whitespace, etc.).
    """
    exact_seen: set[str] = set()
    unique: list[dict] = []
    for c in chunks:
        if c["text"] not in exact_seen:
            exact_seen.add(c["text"])
            unique.append(c)
    # longest first so we keep the fullest capture
    unique.sort(key=lambda c: len(c["text"]), reverse=True)
    kept: list[dict] = []
    for c in unique:
        if any(
            difflib.SequenceMatcher(None, c["text"], k["text"]).ratio() >= threshold
            for k in kept
        ):
            continue
        kept.append(c)
    return kept


def coverage_stats(chunks: list[dict], html: str | bytes) -> dict:
    dom_words = sum(c["word_count"] for c in chunks)
    traf_words = trafilatura_words(html)
    return {
        "chunk_count": len(chunks),
        "dom_words": dom_words,
        "trafilatura_words": traf_words,
        # If trafilatura finds much more text than the DOM walker, extraction is suspect
        "dom_to_trafilatura_ratio": round(dom_words / traf_words, 2) if traf_words else None,
    }
