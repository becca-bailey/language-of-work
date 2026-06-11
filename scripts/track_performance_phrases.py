#!/usr/bin/env python
"""Track performance-era phrase lexicons per company (careers corpus)."""

from __future__ import annotations

import argparse
import re

import numpy as np
import pandas as pd

from lowork.axes import project
from lowork.config import AXES_DIR, company_dir
from lowork.io import read_json, write_json
from lowork.sentences import split_sentences

ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}

ERA_LEXICONS: dict[str, list[tuple[str, re.Pattern]]] = {
    "work_hard_play_hard": [
        ("work hard play hard", re.compile(r"\bwork hard(?:,)? play hard\b", re.I)),
        ("crush it", re.compile(r"\bcrush(?:ing)? it\b", re.I)),
        ("rockstar", re.compile(r"\brock\s*stars?\b", re.I)),
        ("hustle", re.compile(r"\bhustl(?:e|ing|er)\b", re.I)),
        ("a-player", re.compile(r"\bA[\s-]?players?\b", re.I)),
    ],
    "hardcore": [
        ("hardcore", re.compile(r"\b(?:extremely\s+)?hard[\s-]?core\b", re.I)),
        ("high performance", re.compile(r"\bhigh[\s-]performance\b", re.I)),
        ("intensity", re.compile(r"\bintensit(?:y|ies)\b", re.I)),
        ("raise the bar", re.compile(r"\braise(?:s|d)? the bar\b", re.I)),
        ("exceptional talent", re.compile(r"\bexceptional talent\b", re.I)),
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
    perf_vec = load_pole_vector("performance")
    store = EmbeddingStore()

    sentences: list[tuple[int, str, float]] = []
    for _, row in mission.iterrows():
        year = int(row["year"])
        for sent in split_sentences(row["text"]):
            if len(sent.split()) < 5:
                continue
            emb = store.embed([sent])[0]
            score = float(project(emb.reshape(1, -1), perf_vec)[0])
            sentences.append((year, sent, score))

    lexicons = {
        era: [
            {"term": t, **v, "max_score": round(float(v["max_score"]), 4)}
            for t, v in sorted(
                track_terms(sentences, patterns).items(),
                key=lambda x: x[1]["first_year"],
            )
        ]
        for era, patterns in ERA_LEXICONS.items()
    }

    write_json(cdir / "performance_phrases.json", {"lexicons": lexicons})
    counts = ", ".join(f"{k}={len(v)}" for k, v in lexicons.items())
    print(f"Wrote {cdir / 'performance_phrases.json'} ({counts})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
