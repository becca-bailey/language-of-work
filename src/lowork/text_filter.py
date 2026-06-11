"""Lightweight text filters for scoring pipelines."""

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
