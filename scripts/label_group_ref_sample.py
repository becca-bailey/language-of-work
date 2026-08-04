#!/usr/bin/env python
"""Emit a blind hand-label sample for the group-reference instrument.

Post-level validation, predictions withheld (same blind convention as
label_stance_sample.py). Two strata:

- flagged: posts the extractor found references in — the ENTIRE flagged set
  when it is <= --census-max (census beats sampling at small N), else a
  random --flagged-n subset.
- unflagged: --unflagged-n posts the extractor found nothing in, read in
  full for the false-negative / recall check.

Writes data/<case>/labels/group_ref_sample.csv with empty `has_reference`
and `pairs` columns. Fill in: has_reference = y/n; pairs = semicolon-
separated `group:frame` codes (taxonomy in prompts/group_references.yaml),
e.g. "migrants_refugees:threat_crime_framing; roma:neutral_mention".
Leave pairs empty when has_reference is n. Then run
report_group_ref_agreement.py.

Usage:
  uv run scripts/label_group_ref_sample.py --case dhh_blog
"""

from __future__ import annotations

import argparse
import random

import pandas as pd

from lowork.config import company_dir
from lowork.io import read_json


def main(case: str, census_max: int, flagged_n: int, unflagged_n: int, seed: int) -> None:
    rng = random.Random(seed)
    cdir = company_dir(case)
    results = read_json(cdir / "group_references.json")
    posts = results["posts"]

    flagged = [p for p in posts if p["refs"]]
    unflagged = [p for p in posts if not p["refs"] and not p["refused"]]
    if len(flagged) <= census_max:
        take_flagged = flagged
        print(f"flagged: census of all {len(flagged)}")
    else:
        take_flagged = rng.sample(flagged, flagged_n)
        print(f"flagged: {flagged_n} sampled of {len(flagged)}")
    take_unflagged = rng.sample(unflagged, min(unflagged_n, len(unflagged)))
    print(f"unflagged (recall check): {len(take_unflagged)} of {len(unflagged)}")

    raw_dir = cdir / "raw_posts"
    rows = []
    sample = [(p, "flagged") for p in take_flagged] + [(p, "unflagged") for p in take_unflagged]
    rng.shuffle(sample)  # don't let strata order leak the prediction
    for p, _stratum in sample:
        text = read_json(raw_dir / f"{p['slug']}.json").get("text", "")
        rows.append(
            {
                "slug": p["slug"],
                "url": p["url"],
                "date": p["date"],
                "title": p["title"],
                "text": text,
                "has_reference": "",
                "pairs": "",
                "notes": "",
            }
        )

    out = cdir / "labels" / "group_ref_sample.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise SystemExit(f"{out} exists — refusing to overwrite hand labels; delete it to regenerate")
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {out} ({len(rows)} posts, strata shuffled, predictions withheld)")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    p.add_argument("--census-max", type=int, default=60)
    p.add_argument("--flagged-n", type=int, default=40)
    p.add_argument("--unflagged-n", type=int, default=20)
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()
    main(args.case, args.census_max, args.flagged_n, args.unflagged_n, args.seed)
