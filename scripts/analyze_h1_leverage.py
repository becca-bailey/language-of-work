#!/usr/bin/env python
"""H1 analysis: coverage-controlled care–DEI co-movement + JOLTS leverage overlay.

Steps 1-2 of the agreed data-quality plan. Everything here uses the DENSE rhetoric
instrument (axis scores on hundreds of chunks), which is where the study has real power;
benefits are illustrative texture elsewhere, not used as a core index here.

1. Care–DEI co-movement, coverage-controlled: the pooled r=0.88 was on raw year-means
   confounded by which companies appear each year. Robust version = WITHIN-company
   correlation of care vs DEI trajectories, across companies with >=6 shared years.
   Report the distribution + a bootstrap CI on the median — kills the coverage confound.

2. Leverage overlay: care & DEI rhetoric vs the JOLTS quits rate (worker bargaining
   power), at lags -1/0/+1 year, to date whether the concession bundle tracks leverage
   and whether talk leads or lags the quits surge.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy import stats

from lowork.config import DATA_DIR, company_dir, load_companies

COS = load_companies()


def company_axis(co, axis):
    try:
        df = pd.read_parquet(company_dir(co) / "axis_scores.parquet")
    except FileNotFoundError:
        return {}
    d = df[(df["axis"] == axis) & (df["level"] == "chunk")][["year", "raw_topk_mean"]]
    return dict(zip(d["year"], d["raw_topk_mean"]))


def within_company_care_dei():
    print("=" * 68)
    print("1. CARE–DEI co-movement, coverage-controlled (within-company)")
    rs = []
    for co in COS:
        care, dei = company_axis(co, "wellbeing"), company_axis(co, "inclusion")
        yrs = sorted(set(care) & set(dei) & set(range(2013, 2027)))
        if len(yrs) >= 6:
            r, _ = stats.pearsonr([care[y] for y in yrs], [dei[y] for y in yrs])
            rs.append((co, r, len(yrs)))
    rs.sort(key=lambda x: -x[1])
    for co, r, n in rs:
        print(f"   {co:11} r={r:+.2f}  (n={n} yrs)")
    vals = [r for _, r, _ in rs]
    rng = np.random.default_rng(7)
    boots = [np.median(rng.choice(vals, len(vals))) for _ in range(5000)]
    pos = sum(1 for v in vals if v > 0)
    print(f"\n   {len(vals)} companies | median within-company r = {np.median(vals):+.2f} "
          f"[95% CI {np.percentile(boots,2.5):+.2f}, {np.percentile(boots,97.5):+.2f}]")
    print(f"   {pos}/{len(vals)} companies show POSITIVE care–DEI co-movement")


def pooled_balanced(axis, panel, lo=2013, hi=2026):
    """Pooled trajectory over a fixed company panel (balanced) — no coverage drift."""
    out = {}
    for y in range(lo, hi + 1):
        vals = [company_axis(co, axis).get(y) for co in panel]
        vals = [v for v in vals if v is not None]
        if len(vals) >= max(4, len(panel) // 2):
            out[y] = float(np.mean(vals))
    return out


def leverage_overlay():
    print("=" * 68)
    print("2. LEVERAGE OVERLAY — care & DEI rhetoric vs JOLTS quits rate")
    quits = {q["year"]: q["quitsRate"] for q in json.load((DATA_DIR / "power_proxies.json").open())["quits"]}
    # balanced panel: companies with rhetoric in >=10 of 2013-2026
    panel = [co for co in COS if len([y for y in range(2013, 2027) if y in company_axis(co, "wellbeing")]) >= 10]
    print(f"   balanced panel: {len(panel)} companies")
    care = pooled_balanced("wellbeing", panel)
    dei = pooled_balanced("inclusion", panel)

    print(f"\n   {'year':4} {'quits':>6} {'care':>7} {'DEI':>7}")
    for y in range(2015, 2025):
        print(f"   {y:4} {quits.get(y,float('nan')):>6.2f} "
              f"{care.get(y,float('nan')):>+7.3f} {dei.get(y,float('nan')):>+7.3f}")

    def lagcorr(series, lag):
        # corr(series[t], quits[t-lag]); lag>0 => rhetoric LAGS quits; lag<0 => LEADS
        ys = [y for y in series if (y - lag) in quits]
        if len(ys) < 6:
            return None
        return stats.pearsonr([series[y] for y in ys], [quits[y - lag] for y in ys])[0], len(ys)

    print("\n   correlation with quits rate (lag>0 = rhetoric lags leverage):")
    for name, s in (("care", care), ("DEI", dei)):
        row = []
        for lag in (-1, 0, 1):
            c = lagcorr(s, lag)
            row.append(f"lag{lag:+d}: r={c[0]:+.2f}" if c else f"lag{lag:+d}: --")
        print(f"     {name:5} " + "  ".join(row))
    print("   (care spikes 2020, quits peak 2021-22 → expect strongest at lag -1: talk leads)")
    print("   CAVEAT: 2020 care spike is COVID-confounded; the cleaner test is the RECEDE "
          "(quits fall 2023-24 → does the concession bundle fall with it).")


def main() -> int:
    within_company_care_dei()
    leverage_overlay()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
