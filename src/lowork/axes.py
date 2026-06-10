"""Contrast-pair axis construction, projection, aggregation, and checks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml

from .embeddings import EmbeddingStore


@dataclass
class AxisDef:
    name: str
    pole_a_label: str
    pole_a: list[str]
    pole_b_label: str
    pole_b: list[str]

    @classmethod
    def from_yaml(cls, path: Path) -> "AxisDef":
        raw = yaml.safe_load(path.read_text())
        return cls(
            name=raw["name"],
            pole_a_label=raw["pole_a"]["label"],
            pole_a=raw["pole_a"]["sentences"],
            pole_b_label=raw["pole_b"]["label"],
            pole_b=raw["pole_b"]["sentences"],
        )


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def build_axis(
    store: EmbeddingStore,
    axis: AxisDef,
    *,
    drop_a: int | None = None,
    drop_b: int | None = None,
) -> np.ndarray:
    """Axis vector = mean(pole A) - mean(pole B), normalized.

    drop_a/drop_b leave one sentence out of a pole (for perturbation testing).
    """
    pole_a = [s for i, s in enumerate(axis.pole_a) if i != drop_a]
    pole_b = [s for i, s in enumerate(axis.pole_b) if i != drop_b]
    vec_a = store.embed(pole_a).mean(axis=0)
    vec_b = store.embed(pole_b).mean(axis=0)
    return _unit(vec_a - vec_b)


def project(embeddings: np.ndarray, axis_vec: np.ndarray) -> np.ndarray:
    """Signed projection of unit-normalized chunk embeddings onto the axis."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return (embeddings / norms) @ axis_vec


def topk_mean(scores: np.ndarray, k: int) -> tuple[float, int, np.ndarray]:
    """Adaptive top-k mean: k = min(k, n). Returns (mean, k_used, top indices)."""
    k_used = min(k, len(scores))
    idx = np.argsort(scores)[::-1][:k_used]
    return float(scores[idx].mean()), k_used, idx


def zscore(values: np.ndarray) -> np.ndarray:
    std = values.std()
    if std == 0:
        return np.zeros_like(values)
    return (values - values.mean()) / std


def near_duplicates(embeddings: np.ndarray, threshold: float) -> np.ndarray:
    """Pairwise cosine similarity matrix thresholded (for carried-forward detection)."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    unit = embeddings / norms
    return (unit @ unit.T) >= threshold


# --- Circularity check -------------------------------------------------------

_word_re = re.compile(r"[a-z0-9']+")


def _ngrams(text: str, n: int) -> set[tuple[str, ...]]:
    words = _word_re.findall(text.lower())
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def circularity_check(
    store: EmbeddingStore,
    axis: AxisDef,
    corpus_texts: list[str],
    *,
    cosine_threshold: float = 0.85,
    ngram_n: int = 5,
) -> list[dict]:
    """Flag axis sentences that look lifted from the corpus being measured.

    Two signals: high embedding cosine to any corpus chunk, or a shared
    word n-gram (verbatim phrase overlap). Flags are for human adjudication,
    not automatic rejection.
    """
    sentences = [(s, axis.pole_a_label) for s in axis.pole_a] + [
        (s, axis.pole_b_label) for s in axis.pole_b
    ]
    sent_embs = store.embed([s for s, _ in sentences])
    corpus_embs = store.embed(corpus_texts)
    corpus_unit = corpus_embs / np.linalg.norm(corpus_embs, axis=1, keepdims=True)
    corpus_ngrams = [_ngrams(t, ngram_n) for t in corpus_texts]

    flags = []
    for (sentence, pole), emb in zip(sentences, sent_embs):
        sims = corpus_unit @ _unit(emb)
        best = int(np.argmax(sims))
        sent_grams = _ngrams(sentence, ngram_n)
        verbatim_hits = [
            i for i, grams in enumerate(corpus_ngrams) if sent_grams and (sent_grams & grams)
        ]
        if sims[best] >= cosine_threshold or verbatim_hits:
            flags.append(
                {
                    "axis": axis.name,
                    "pole": pole,
                    "sentence": sentence,
                    "max_cosine": round(float(sims[best]), 3),
                    "closest_chunk": corpus_texts[best][:200],
                    "verbatim_ngram_overlap": bool(verbatim_hits),
                }
            )
    return flags
