"""Tuned AI-term mention net, shared by track_ai_mentions and score_ai_language.

Case matters: the acronym patterns are case-SENSITIVE (`\\bAI\\b` not `\\bai\\b`) —
a loose lowercase net produces false positives (verified 2026-06: it gave Netflix
13 pre-tuning mentions vs 0 after). Multi-word content terms are case-insensitive
because they are unambiguous as phrases.
"""

from __future__ import annotations

import re

# Case-sensitive acronyms. \b guards both sides; GPT-4 style suffixes allowed.
AI_ACRONYM_PATTERN = re.compile(r"\b(AI|ML|LLMs?|GPT(?:-\d+\w*)?)\b")

# Case-insensitive multi-word content terms. "agentic" and "agentforce" added
# 2026-07-10 after the first corpus run showed Salesforce/Stripe agent-era copy
# ("your agentic coworkers", "Agentic Commerce") slipping past the acronym net.
AI_PHRASE_PATTERN = re.compile(
    r"\b(machine[ -]learning|artificial[ -]intelligence|large[ -]language[ -]models?|"
    r"deep[ -]learning|generative[ -]ai|foundation[ -]models?|agentic|agentforce)\b",
    re.I,
)


def find_ai_terms(text: str) -> list[str]:
    """All matched terms in a chunk, normalized (acronyms upper, phrases lower)."""
    terms = [m.group(0) for m in AI_ACRONYM_PATTERN.finditer(text)]
    terms += [m.group(0).lower().replace("-", " ") for m in AI_PHRASE_PATTERN.finditer(text)]
    return terms


def has_ai_mention(text: str) -> bool:
    return bool(AI_ACRONYM_PATTERN.search(text) or AI_PHRASE_PATTERN.search(text))
