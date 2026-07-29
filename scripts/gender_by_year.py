#!/usr/bin/env python
"""Gender-axis time series: does careers language de-feminize after 2022?

Presence-based: a sentence counts in every year whose captured page contains
it (what a jobseeker read that year), deduped within company-year. Scores are
z against the story's frozen 20-company baseline, so years are comparable to
the published company numbers.

Composition control: corpus coverage grows over time, so the headline series
is the company-equal-weight mean over companies with >= MIN_N sentences that
year; a balanced panel (companies covering the full window) is reported as a
check, alongside the raw pooled mean.

Writes data/gender_by_year.json (per company-year and per year).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from lowork.config import WEB_DATA_DIR
from lowork.embeddings import EmbeddingStore
from lowork.gender_axis import NEUTRAL_BAND, build_axis, project

from track_culture_propagation import company_sentences

MIN_N = 20          # company-year sentence floor for the equal-weight series
PANEL_START = 2014  # balanced panel: companies with coverage in every year
PANEL_END = 2026    # of [PANEL_START, PANEL_END]


def main() -> None:
    story = json.loads((WEB_DATA_DIR / "stories" / "gender-language.json").read_text())
    mu, sd = story["mu"], story["sd"]
    companies = [c["company"] for c in story["columns"]]
    store = EmbeddingStore()
    axis = build_axis(store)

    per_cy: dict[str, dict[int, dict]] = defaultdict(dict)
    for co in companies:
        by_year: dict[int, dict[str, str]] = defaultdict(dict)
        for y, s in company_sentences(co, english_only=True):
            by_year[y][s.lower().strip()] = s
        for y, sents in sorted(by_year.items()):
            texts = list(sents.values())
            z = (project(store, axis, texts) - mu) / sd
            per_cy[co][y] = {
                "n": len(texts),
                "meanZ": round(float(z.mean()), 3),
                "mascShare": round(float((z >= NEUTRAL_BAND).mean()), 3),
                "femShare": round(float((z <= -NEUTRAL_BAND).mean()), 3),
            }
        print(f"{co}: {len(by_year)} years, "
              f"{min(by_year, default=0)}–{max(by_year, default=0)}")

    years = sorted({y for cy in per_cy.values() for y in cy})
    panel = [co for co in companies
             if all(y in per_cy[co] and per_cy[co][y]["n"] >= MIN_N
                    for y in range(PANEL_START, PANEL_END + 1))]
    print(f"\nbalanced panel {PANEL_START}-{PANEL_END} (n>={MIN_N} every year): {panel}")

    series = []
    for y in years:
        rows = [(co, per_cy[co][y]) for co in companies if y in per_cy[co]]
        eligible = [r for _, r in rows if r["n"] >= MIN_N]
        panel_rows = [per_cy[co][y] for co in panel if y in per_cy[co]]
        entry = {"year": y, "nCompanies": len(eligible),
                 "nSentences": sum(r["n"] for _, r in rows)}
        if eligible:
            entry["meanZ"] = round(float(np.mean([r["meanZ"] for r in eligible])), 3)
            entry["mascShare"] = round(float(np.mean([r["mascShare"] for r in eligible])), 3)
            entry["femShare"] = round(float(np.mean([r["femShare"] for r in eligible])), 3)
        if panel_rows:
            entry["panelMeanZ"] = round(float(np.mean([r["meanZ"] for r in panel_rows])), 3)
            entry["panelFemShare"] = round(float(np.mean([r["femShare"] for r in panel_rows])), 3)
            entry["panelMascShare"] = round(float(np.mean([r["mascShare"] for r in panel_rows])), 3)
        series.append(entry)

    out = {"minN": MIN_N, "panel": panel, "panelWindow": [PANEL_START, PANEL_END],
           "mu": mu, "sd": sd, "series": series,
           "companies": {co: {str(y): v for y, v in cy.items()} for co, cy in per_cy.items()}}
    out_path = Path(__file__).resolve().parent.parent / "data" / "gender_by_year.json"
    out_path.write_text(json.dumps(out, indent=1))
    web_path = WEB_DATA_DIR / "stories" / "gender-language-time.json"
    web_path.write_text(json.dumps(out, indent=1))
    print(f"Wrote {web_path}")

    print(f"\n{'year':<6}{'cos':>4}{'meanZ':>8}{'masc%':>8}{'fem%':>8}{'panelZ':>9}{'panelFem%':>10}")
    for e in series:
        print(f"{e['year']:<6}{e['nCompanies']:>4}"
              f"{e.get('meanZ', float('nan')):>8.2f}"
              f"{100*e.get('mascShare', float('nan')):>8.1f}"
              f"{100*e.get('femShare', float('nan')):>8.1f}"
              f"{e.get('panelMeanZ', float('nan')):>9.2f}"
              f"{100*e.get('panelFemShare', float('nan')):>10.1f}")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    main()
