#!/usr/bin/env python
"""Track Menlo's branded/proprietary vocabulary over time (firm corpus).

Mirrors track_performance_phrases.py: scan the firm mission sentences for each
branded term, record when it first/last appears and its peak idealism projection
+ a representative quote. The point is diachronic — when does "the Menlo Way"
enter the copy, when does "High-Tech Anthropology" pick up its ®, when does the
mission line get rewritten — so the story can show the brand vocabulary forming,
hardening (trademark marks), and persisting.

Writes data/<company>/menlo_phrases.json with a `lexicons` block in the same shape
export_story_web._aggregate_lexicons consumes.
"""

from __future__ import annotations

import argparse
import re

import numpy as np
import pandas as pd

from lowork.axes import project
from lowork.config import AXES_DIR, company_dir
from lowork.io import read_json, write_json
from lowork.sentences import split_sentences

# Firm self-description is the corpus; for Menlo nearly all firm text is brand copy.
ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}

# Branded vocabulary grouped by kind. Patterns are deliberately surface-form so we
# can see the *literal* brand language appear/persist; the ® / TM variants are
# tracked as their own terms because the mark itself is the codification signal.
BRAND_LEXICONS: dict[str, list[tuple[str, re.Pattern]]] = {
    "trademarks": [
        ("the Menlo Way", re.compile(r"\bthe Menlo Way\b", re.I)),
        ("Menlo Way ™/®", re.compile(r"\bMenlo Way\s*(?:™|®|TM|\(R\))", re.I)),
        ("High-Tech Anthropology", re.compile(r"\bHigh[\s-]?Tech Anthropolog(?:y|ist)\b", re.I)),
        ("High-Tech Anthropology ®", re.compile(r"\bHigh[\s-]?Tech Anthropolog(?:y|ist)\s*(?:®|™|\(R\))", re.I)),
        ("High-Speed Voice Technology", re.compile(r"\bHigh[\s-]?Speed Voice Technology\b", re.I)),
        ("Joy, Inc.", re.compile(r"\bJoy,?\s*Inc\.?\b", re.I)),
        ("Chief Joy Officer", re.compile(r"\bChief Joy Officer\b", re.I)),
    ],
    "joy_mission": [
        ("joy", re.compile(r"\bjoy(?:ful|fully)?\b", re.I)),
        ("business value of joy", re.compile(r"\bbusiness value of joy\b", re.I)),
        ("end human suffering", re.compile(r"\bend(?:ing)? human suffering\b", re.I)),
        ("return joy", re.compile(r"\breturn(?:ing)? joy\b", re.I)),
        ("intentional culture", re.compile(r"\bintentional(?:ly)? cultur\w*\b", re.I)),
        ("delight", re.compile(r"\bdelight(?:ed|ful)?\b", re.I)),
    ],
    "method": [
        ("pair programming / pairing", re.compile(r"\bpair(?:ing|ed|s)?(?:\s+programming)?\b", re.I)),
        ("factory tour", re.compile(r"\bfactory tour\b", re.I)),
        ("Show & Tell", re.compile(r"\bShow\s*&?\s*Tell\b", re.I)),
        ("storytelling", re.compile(r"\bstory[\s-]?telling\b", re.I)),
    ],
}


def load_pole_vector(name: str) -> np.ndarray:
    built = read_json(AXES_DIR / "built" / f"{name}.json")
    return np.asarray(built["vector"], dtype=np.float32)


def track_terms(
    sentences: list[tuple[int, str, float]],
    patterns: list[tuple[str, re.Pattern]],
) -> dict[str, dict]:
    terms: dict[str, dict] = {}
    for year, sent, score in sentences:
        for label, pat in patterns:
            if not pat.search(sent):
                continue
            rec = terms.setdefault(
                label,
                {
                    "first_year": year,
                    "last_year": year,
                    "count": 0,
                    "max_score": score,
                    "example": sent[:240],
                },
            )
            rec["first_year"] = min(rec["first_year"], year)
            rec["last_year"] = max(rec["last_year"], year)
            rec["count"] += 1
            if score > rec["max_score"]:
                rec["max_score"] = round(float(score), 4)
                rec["example"] = sent[:240]
    return terms


def main(company: str, axis: str) -> None:
    from lowork.embeddings import EmbeddingStore

    cdir = company_dir(company)
    df = pd.read_parquet(cdir / "embeddings.parquet")
    mission = df[df["label"].isin(ANALYSIS_LABELS)]
    axis_vec = load_pole_vector(axis)
    store = EmbeddingStore()

    sentences: list[tuple[int, str, float]] = []
    for _, row in mission.iterrows():
        year = int(row["year"])
        for sent in split_sentences(row["text"]):
            if len(sent.split()) < 5:
                continue
            emb = store.embed([sent])[0]
            score = float(project(emb.reshape(1, -1), axis_vec)[0])
            sentences.append((year, sent, score))

    lexicons = {
        kind: [
            {"term": t, **v, "max_score": round(float(v["max_score"]), 4)}
            for t, v in sorted(
                track_terms(sentences, patterns).items(),
                key=lambda x: (x[1]["first_year"], -x[1]["count"]),
            )
        ]
        for kind, patterns in BRAND_LEXICONS.items()
    }

    write_json(cdir / "menlo_phrases.json", {"lexicons": lexicons})
    counts = ", ".join(f"{k}={len(v)}" for k, v in lexicons.items())
    print(f"Wrote {cdir / 'menlo_phrases.json'} ({counts})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="menlo")
    parser.add_argument("--axis", default="altruism")
    main(parser.parse_args().company, parser.parse_args().axis)
