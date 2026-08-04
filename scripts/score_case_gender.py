#!/usr/bin/env python
"""Kozlowski gender-axis score for a case corpus (founder blog etc.).

Sentences from the raw post cache, projected on the same axis and z-scored
against the SAME frozen 20-company baseline (mu/sd from the published
gender-language story), so the number is directly comparable to the
published company scores (e.g. basecamp careers pooled meanZ +0.562).

Off-label caveat: the axis was validated on careers copy; a personal-blog
genre difference is a real confound (the house-voice problem, inverted).
This is a memo footnote instrument, not a headline.

Writes data/<case>/gender_score.json.

Usage:
  uv run scripts/score_case_gender.py --case dhh_blog
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

from lowork.config import WEB_DATA_DIR, company_dir
from lowork.embeddings import EmbeddingStore
from lowork.gender_axis import NEUTRAL_BAND, build_axis, project
from lowork.io import write_json
from lowork.sentences import split_sentences

MIN_SENT_WORDS = 5


def main(case: str) -> None:
    story = json.loads((WEB_DATA_DIR / "stories" / "gender-language.json").read_text())
    mu, sd = story["mu"], story["sd"]

    raw_dir = company_dir(case) / "raw_posts"
    by_year: dict[str, dict[str, str]] = defaultdict(dict)
    for p in sorted(raw_dir.glob("*.json")):
        post = json.loads(p.read_text())
        year = (post.get("date") or "")[:4] or "undated"
        for s in split_sentences(post.get("text", "")):
            s = s.strip()
            if len(s.split()) >= MIN_SENT_WORDS:
                by_year[year][s.lower()] = s  # dedup within year, like gender_by_year
    if not by_year:
        raise SystemExit(f"no raw posts under {raw_dir}")

    store = EmbeddingStore()
    axis = build_axis(store)

    all_sents: list[str] = []
    years_out = {}
    for year, sents in sorted(by_year.items()):
        texts = list(sents.values())
        z = (project(store, axis, texts) - mu) / sd
        years_out[year] = {
            "n": len(texts),
            "meanZ": round(float(z.mean()), 3),
            "mascShare": round(float((z >= NEUTRAL_BAND).mean()), 3),
            "femShare": round(float((z <= -NEUTRAL_BAND).mean()), 3),
        }
        all_sents.extend(texts)

    z_all = (project(store, axis, all_sents) - mu) / sd
    out = {
        "case": case,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "baseline": "frozen story mu/sd (gender-language.json)",
        "mu": mu,
        "sd": sd,
        "pooled": {
            "n": len(all_sents),
            "meanZ": round(float(z_all.mean()), 3),
            "mascShare": round(float((z_all >= NEUTRAL_BAND).mean()), 3),
            "femShare": round(float((z_all <= -NEUTRAL_BAND).mean()), 3),
        },
        "by_year": years_out,
        "caveat": "off-label: axis validated on careers copy; blog genre difference is a confound",
    }
    path = company_dir(case) / "gender_score.json"
    write_json(path, out)
    print(f"pooled meanZ {out['pooled']['meanZ']} (n={out['pooled']['n']}) "
          f"masc {out['pooled']['mascShare']} fem {out['pooled']['femShare']}")
    print(f"Wrote {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    args = p.parse_args()
    main(args.case)
