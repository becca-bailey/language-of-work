"""Gender-coding axis (Kozlowski, Taddy & Evans 2019 method).

Axis = normalized mean of normalized difference vectors over PURE gender-term
pairs, built in the same embedding space as the corpus. The poles contain no
intuition words — "hardcore" is projected, never assumed. Positive = the
masculine-coded direction (male terms are first in each pair).

What it measures is cultural coding — how strongly language associates with
male-skewed contexts in the embedding model's training corpus. That inherited
association is the phenomenon under study, not a bug.

Validation status (2026-07-23, docs/exclusion-story-pilot.md): known-answer
test passes (stereotyped occupations separate cleanly, neutral terms ≈ 0);
split-half reliability r=0.71 on corpus sentences. NOT yet human-backstopped.
Word-level projections are noisy in sentence-embedding space (sense mixture:
bare "battle" averages its military and illness senses) — operate at
sentence/document level.
"""

from __future__ import annotations

import numpy as np

GENDER_PAIRS: list[tuple[str, str]] = [
    ("man", "woman"), ("men", "women"), ("he", "she"), ("him", "her"),
    ("his", "hers"), ("himself", "herself"), ("male", "female"),
    ("boy", "girl"), ("father", "mother"), ("son", "daughter"),
    ("brother", "sister"), ("husband", "wife"), ("uncle", "aunt"),
    ("king", "queen"), ("grandfather", "grandmother"), ("gentleman", "lady"),
]

# |z| below this band is treated as neutral everywhere (axis noise floor).
NEUTRAL_BAND = 0.5


def _norm(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)


def build_axis(store) -> np.ndarray:
    """Unit axis vector from the gender pairs, using the given EmbeddingStore."""
    male = _norm(np.stack(store.embed([m for m, _ in GENDER_PAIRS])))
    female = _norm(np.stack(store.embed([f for _, f in GENDER_PAIRS])))
    return _norm(_norm(male - female).mean(axis=0))


def project(store, axis: np.ndarray, texts: list[str]) -> np.ndarray:
    """Cosine projection of each text onto the axis (positive = masculine-coded)."""
    return _norm(np.stack(store.embed(texts))) @ axis
