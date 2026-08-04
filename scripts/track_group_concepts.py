#!/usr/bin/env python
"""Embedding probes for group-reference concepts over a founder-blog corpus.

Secondary instrument for convergent validity next to the LLM extractor
(classify_group_refs.py) and the regex lexicon (analyze_dhh_contrast.py):
probe sentences per concept, max cosine sim per corpus sentence, hits >= 0.5
per 100 sentences per year (the exclusion-pilot method). The three
instruments are reported side by side in the pilot memo; divergence is
investigated, not averaged.

Reads the raw post cache (full text). Writes data/<case>/group_concepts.json.

Usage:
  uv run scripts/track_group_concepts.py --case dhh_blog
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

from lowork.config import company_dir
from lowork.embeddings import EmbeddingStore
from lowork.io import write_json
from lowork.sentences import split_sentences

HIT_THRESHOLD = 0.5
MIN_SENT_WORDS = 5

CONCEPTS = {
    "migrant_threat": [
        "Migrants are responsible for the rising crime in our cities.",
        "Mass immigration is destroying the fabric of our society.",
        "Asylum seekers are a burden and a danger to the native population.",
    ],
    "migrant_sympathy": [
        "Refugees deserve protection and compassion.",
        "Immigrants enrich our society and our economy.",
    ],
    "roma_reference": [
        "The gypsies have taken over the public parks.",
        "Roma people face discrimination across Europe.",
    ],
    "islam_threat": [
        "Islam is incompatible with Western values.",
        "Muslim immigration threatens European culture.",
    ],
    "crime_ethnicity": [
        "The crime statistics show which ethnic groups are responsible.",
        "Immigrant background explains the violence in our streets.",
    ],
    "deportation_removal": [
        "Deport them all and close the borders.",
        "When they take over public spaces, you deport them.",
    ],
    "trans_gender_ideology": [
        "Gender ideology is being forced on our children.",
        "Trans activism has gone too far.",
    ],
    "western_decline": [
        "The West is committing civilizational suicide.",
        "Europe is too weak and delusional to defend its own culture.",
    ],
}


def _norm(m: np.ndarray) -> np.ndarray:
    return m / np.linalg.norm(m, axis=1, keepdims=True)


def corpus_sentences(case: str) -> list[tuple[str, str, str]]:
    """(year, slug, sentence) from the raw post cache."""
    raw_dir = company_dir(case) / "raw_posts"
    out = []
    for p in sorted(raw_dir.glob("*.json")):
        post = json.loads(p.read_text())
        year = (post.get("date") or "")[:4] or "undated"
        for s in split_sentences(post.get("text", "")):
            s = s.strip()
            if len(s.split()) >= MIN_SENT_WORDS:
                out.append((year, post["slug"], s))
    if not out:
        raise SystemExit(f"no raw posts under {raw_dir} — run fetch_case.py first")
    return out


def main(case: str) -> None:
    sents = corpus_sentences(case)
    print(f"{len(sents)} sentences from {case}")
    store = EmbeddingStore()
    probe_vecs = {name: _norm(np.stack(store.embed(probes))) for name, probes in CONCEPTS.items()}
    E = _norm(np.stack(store.embed([s for _, _, s in sents])))

    by_year_sent_count: dict[str, int] = defaultdict(int)
    for year, _, _ in sents:
        by_year_sent_count[year] += 1

    concepts_out = {}
    for name, A in probe_vecs.items():
        sims = (A @ E.T).max(axis=0)
        hits_by_year: dict[str, int] = defaultdict(int)
        top: list[dict] = []
        for i, (year, slug, s) in enumerate(sents):
            if sims[i] >= HIT_THRESHOLD:
                hits_by_year[year] += 1
        for i in np.argsort(-sims)[:8]:
            year, slug, s = sents[i]
            top.append({"sim": round(float(sims[i]), 3), "year": year, "slug": slug, "sentence": s[:220]})
        concepts_out[name] = {
            "max_sim": round(float(sims.max()), 3),
            "hits": int((sims >= HIT_THRESHOLD).sum()),
            "hits_per_100_by_year": {
                y: round(100 * hits_by_year[y] / by_year_sent_count[y], 2)
                for y in sorted(by_year_sent_count)
            },
            "hits_by_year": dict(sorted(hits_by_year.items())),
            "top_sentences": [t for t in top if t["sim"] >= HIT_THRESHOLD],
        }
        print(f"  {name:24s} max {concepts_out[name]['max_sim']:.2f}  hits {concepts_out[name]['hits']}")

    out = {
        "case": case,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": f"probe max-sim, hit threshold {HIT_THRESHOLD}, min {MIN_SENT_WORDS} words/sentence",
        "n_sentences": len(sents),
        "sentences_by_year": dict(sorted(by_year_sent_count.items())),
        "probes": CONCEPTS,
        "concepts": concepts_out,
    }
    path = company_dir(case) / "group_concepts.json"
    write_json(path, out)
    print(f"Wrote {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    args = p.parse_args()
    main(args.case)
