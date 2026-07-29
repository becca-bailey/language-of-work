"""Lightweight text filters for scoring pipelines.

NOTE: `langgate.is_english` is a DIFFERENT, deliberate implementation
(stopword-vote, no external deps) that gates chunk extraction; this one
filters at scoring time. Same name, different tradeoffs — don't swap.
"""

from __future__ import annotations

MIN_ENGLISH_CHARS = 40


def _ascii_ratio(text: str) -> float:
    if not text:
        return 1.0
    return sum(1 for ch in text if ord(ch) < 128) / len(text)


def is_english(text: str, *, min_chars: int = MIN_ENGLISH_CHARS) -> bool:
    """Return True if text is likely English careers-page prose."""
    t = text.strip()
    if len(t) < min_chars:
        return True  # too short to classify reliably; keep
    if _ascii_ratio(t) < 0.85:
        return False
    try:
        from langdetect import DetectorFactory, detect

        DetectorFactory.seed = 0
        return detect(t) == "en"
    except Exception:
        return _ascii_ratio(t) >= 0.92


def is_english_sentence(text: str) -> bool:
    """Precision-first English check for a SINGLE sentence.

    langdetect is confidently wrong on short English marketing prose ("Silent
    disagreement is unacceptable and unproductive." → fr @ 0.99), so at sentence
    length its non-English verdict counts only when corroborated by independent
    evidence: non-ASCII letters, or ≥2 distinctive foreign function words
    (langgate's per-language stopword sets). Chunk-level `is_english` stays the
    primary gate — this only catches foreign strays inside majority-English
    chunks (e.g. Coinbase's multi-language GDPR appendix). Uncorroborated → keep.
    """
    t = text.strip()
    if not t:
        return True
    try:
        from langdetect import DetectorFactory, detect

        DetectorFactory.seed = 0
        if detect(t) == "en":
            return True
    except Exception:
        return True
    nonascii_letters = sum(1 for ch in t if ord(ch) > 127 and ch.isalpha())
    if nonascii_letters >= 2:
        return False
    from .langgate import _STOPWORDS

    words = {w.strip(".,;:!?()\"'«»„“”") for w in t.lower().split()}
    return not any(len(words & sw) >= 2 for lang, sw in _STOPWORDS.items() if lang != "en")
