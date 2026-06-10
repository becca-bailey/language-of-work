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
            para = strip_nav_runs(para)
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
