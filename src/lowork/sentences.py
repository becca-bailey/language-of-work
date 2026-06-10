"""Sentence splitting for sentence-level axis scoring."""

from __future__ import annotations

import re

MIN_WORDS = 6

# Split on sentence boundaries; keep abbreviations simple
_SENTENCE_END = re.compile(r'(?<=[.!?…])\s+(?=[A-Z"\'(])')


def split_sentences(text: str, *, min_words: int = MIN_WORDS) -> list[str]:
    """Split text into sentences; drop fragments under min_words."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = _SENTENCE_END.split(text)
    out = []
    for part in parts:
        part = part.strip()
        if len(part.split()) >= min_words:
            out.append(part)
    # if no splits (single block), return whole text if long enough
    if not out and len(text.split()) >= min_words:
        out = [text]
    return out
