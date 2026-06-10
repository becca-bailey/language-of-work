"""Post-classification heuristics to fix systematic mislabels."""

from __future__ import annotations

import re

from .chunking import _CHROME_START

# Nav-like tokens common in mislabeled mission_brand chunks.
_NAV_TOKENS = re.compile(
    r"\b(?:sign in|today's deals|gift cards|your account|start here|"
    r"apply now|careers home|browsing history|sponsored by)\b",
    re.I,
)

# City/location pages mislabeled as mission (heading is a place name).
_LOCATION_HEADING = re.compile(
    r"^[A-Z][\w\s.'-]+,\s*(?:Washington|California|Texas|Spain|China|India|"
    r"Kentucky|UK|Germany|France|Ireland|Australia|Japan|Brazil|Mexico|"
    r"Ontario|British Columbia)\s*$",
)

_LOCATION_BODY = re.compile(
    r"\b(?:population|metropolitan area|capital of|located on|"
    r"office is located|great place to (?:work|live))\b",
    re.I,
)

def _nav_token_fraction(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    hits = len(_NAV_TOKENS.findall(text))
    return hits / len(words)


def apply_relabel_heuristics(
    labels: dict[str, str],
    chunks: list[dict],
) -> tuple[dict[str, str], list[dict]]:
    """Return (updated labels, list of {chunk_id, from, to, reason})."""
    by_id = {c["chunk_id"]: c for c in chunks}
    out = dict(labels)
    changes: list[dict] = []

    for cid, label in list(out.items()):
        chunk = by_id.get(cid)
        if not chunk:
            continue
        text = chunk["text"]
        heading = chunk.get("heading") or ""

        new_label = None
        reason = None

        if label == "mission_brand":
            if _CHROME_START.match(text) and _nav_token_fraction(text) > 0.08:
                new_label = "navigation_junk"
                reason = "nav chrome prefix"
            elif _nav_token_fraction(text) > 0.12:
                new_label = "navigation_junk"
                reason = "high nav token fraction"
            elif _LOCATION_HEADING.match(heading.strip()) and _LOCATION_BODY.search(text):
                new_label = "navigation_junk"
                reason = "location page"

        if new_label and new_label != label:
            out[cid] = new_label
            changes.append(
                {"chunk_id": cid, "from": label, "to": new_label, "reason": reason}
            )

    return out, changes
