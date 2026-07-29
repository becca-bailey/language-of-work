#!/usr/bin/env python
"""Export the gender-language story data (unit-chart JSON).

Per-company careers-register sentences (mission_brand, English-only, deduped,
first-capture year), each projected onto the gender axis and z-scored against a
FROZEN baseline: the 20 pre-story companies' pooled sentences — so adding cohort
companies never moves the yardstick. Non-English sentences (localized careers
captures) are excluded: gendered function words in other languages ("on" =
Polish "he") otherwise produce spurious axis extremes. Canon documents are excluded by design
(they belong to the exclusion story). Writes
astro/src/data/stories/gender-language.json, score-ordered per company.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from lowork.company import CompanyProfile
from lowork.config import WEB_DATA_DIR, load_companies
from lowork.embeddings import EmbeddingStore
from lowork.gender_axis import GENDER_PAIRS, NEUTRAL_BAND, build_axis, project
from lowork.io import write_json

from track_culture_propagation import company_sentences  # careers-register sentence source

# Frozen z-score baseline (see docstring). Do not extend when companies join.
BASELINE = ["google", "amazon", "meta", "palantir", "coinbase", "netflix", "shopify",
            "stripe", "airbnb", "snap", "hubspot", "gitlab", "github", "basecamp",
            "salesforce", "starbucks", "uber", "apple", "nvidia", "engine"]


def unique_sentences(co: str) -> list[tuple[int, str]]:
    seen: dict[str, tuple[int, str]] = {}
    # english_only: localized careers captures (Polish/Italian Coinbase pages)
    # otherwise leak in, and gendered function words in other languages ("on"
    # = Polish "he") produce spurious axis extremes.
    for y, s in company_sentences(co, english_only=True):
        k = s.lower().strip()
        if k not in seen or y < seen[k][0]:
            seen[k] = (y, s)
    return sorted(seen.values())


def main(companies: list[str] | None = None) -> None:
    cohort = companies if companies is not None else load_companies()
    store = EmbeddingStore()
    axis = build_axis(store)

    all_sents = {co: unique_sentences(co) for co in set(cohort) | set(BASELINE)}
    pool = np.concatenate([project(store, axis, [s for _, s in all_sents[co]])
                           for co in BASELINE if all_sents.get(co)])
    mu, sd = float(pool.mean()), float(pool.std())

    cols = []
    for co in cohort:
        sents = all_sents.get(co) or []
        if not sents:
            print(f"  {co}: no careers sentences — skipped")
            continue
        z = (project(store, axis, [s for _, s in sents]) - mu) / sd
        order = np.argsort(-z)
        items = [{"z": round(float(z[i]), 2), "y": sents[i][0], "t": sents[i][1][:200]}
                 for i in order]
        nm = sum(1 for i in items if i["z"] >= NEUTRAL_BAND)
        nf = sum(1 for i in items if i["z"] <= -NEUTRAL_BAND)
        cols.append({
            "company": co, "name": CompanyProfile.load(co).display_name,
            "n": len(items), "mascPct": round(100 * nm / len(items)),
            "femPct": round(100 * nf / len(items)),
            "meanZ": round(float(z.mean()), 2), "items": items,
        })

    out = {
        "story": "gender-language", "englishOnly": True,
        "axisPairs": len(GENDER_PAIRS), "neutralBand": NEUTRAL_BAND,
        "baselineN": int(len(pool)), "mu": round(mu, 4), "sd": round(sd, 4),
        "columns": cols,
    }
    out_dir = WEB_DATA_DIR / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "gender-language.json", out)
    print(f"Wrote {out_dir / 'gender-language.json'}: {len(cols)} companies, "
          f"{sum(c['n'] for c in cols)} sentences")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.parse_args()
    main()
