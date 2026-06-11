#!/usr/bin/env python
"""Track first/last appearance of inclusion and civilizational phrases per company."""

from __future__ import annotations

import argparse
import hashlib
import re

import numpy as np
import pandas as pd

from lowork.axes import project
from lowork.config import AXES_DIR, company_dir
from lowork.io import read_json, write_json
from lowork.sentences import split_sentences

ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}
SCORE_THRESHOLD = 0.30

INCLUSION_TERM_PATTERN = re.compile(
    r"\b(diversity|inclusion|belonging|equity|underrepresented|"
    r"black|latinx|hispanic|women|lgbtq|disability|accessibility|"
    r"bias|representation|affirmative)\w*\b",
    re.I,
)

# Civilizational framing lexicon (descriptive tracking, not register classification)
CIVILIZATIONAL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("the west", re.compile(r"\bthe west(?:ern)?(?:\'s|\s+(?:most|important|values|institutions))?\b", re.I)),
    ("western institutions", re.compile(r"\bwestern\s+(?:tech\s+)?institutions\b", re.I)),
    ("civilization", re.compile(r"\bcivilization(?:al)?\b", re.I)),
    ("warfighter", re.compile(r"\bwarfighters?\b", re.I)),
]


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
                    "max_score": score,
                    "example": sent[:200],
                },
            )
            rec["first_year"] = min(rec["first_year"], year)
            rec["last_year"] = max(rec["last_year"], year)
            if score > rec["max_score"]:
                rec["max_score"] = round(float(score), 4)
                rec["example"] = sent[:200]
    return terms


def main(company: str) -> None:
    from lowork.embeddings import EmbeddingStore

    cdir = company_dir(company)
    df = pd.read_parquet(cdir / "embeddings.parquet")
    mission = df[df["label"].isin(ANALYSIS_LABELS)]
    inc_vec = load_pole_vector("inclusion")
    store = EmbeddingStore()

    inclusion_terms: dict[str, dict] = {}
    high_scoring: list[dict] = []
    all_sentences: list[tuple[int, str, float]] = []

    for _, row in mission.iterrows():
        year = int(row["year"])
        for sent in split_sentences(row["text"]):
            if len(sent.split()) < 5:
                continue
            emb = store.embed([sent])[0]
            score = float(project(emb.reshape(1, -1), inc_vec)[0])
            all_sentences.append((year, sent, score))
            if score >= SCORE_THRESHOLD:
                sid = hashlib.sha256(sent.encode()).hexdigest()[:12]
                high_scoring.append({
                    "id": sid,
                    "year": year,
                    "text": sent,
                    "score": round(score, 4),
                })
            for m in INCLUSION_TERM_PATTERN.finditer(sent):
                term = m.group(0).lower()
                rec = inclusion_terms.setdefault(
                    term,
                    {"first_year": year, "last_year": year, "max_score": score, "example": sent[:200]},
                )
                rec["first_year"] = min(rec["first_year"], year)
                rec["last_year"] = max(rec["last_year"], year)
                if score > rec["max_score"]:
                    rec["max_score"] = round(float(score), 4)
                    rec["example"] = sent[:200]

    civilizational = track_terms(all_sentences, CIVILIZATIONAL_PATTERNS)

    by_text_year: dict[tuple[str, int], dict] = {}
    for s in high_scoring:
        key = (s["text"], s["year"])
        if key not in by_text_year or s["score"] > by_text_year[key]["score"]:
            by_text_year[key] = s

    write_json(
        cdir / "dei_phrases.json",
        {
            "terms": [
                {"term": t, **v, "max_score": round(float(v["max_score"]), 4)}
                for t, v in sorted(inclusion_terms.items(), key=lambda x: x[1]["first_year"])
            ],
            "high_scoring_sentences": sorted(
                by_text_year.values(), key=lambda x: (x["year"], -x["score"])
            ),
            "lexicons": {
                "inclusion": [
                    {"term": t, **v, "max_score": round(float(v["max_score"]), 4)}
                    for t, v in sorted(inclusion_terms.items(), key=lambda x: x[1]["first_year"])
                ],
                "civilizational": [
                    {"term": t, **v, "max_score": round(float(v["max_score"]), 4)}
                    for t, v in sorted(civilizational.items(), key=lambda x: x[1]["first_year"])
                ],
            },
        },
    )
    print(
        f"Wrote {cdir / 'dei_phrases.json'} "
        f"({len(inclusion_terms)} inclusion terms, {len(civilizational)} civilizational, "
        f"{len(by_text_year)} sentences)"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
