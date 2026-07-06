#!/usr/bin/env python
"""Phase 4 (b): is H2 (individualization) a real null or underpowered?

Per the advisor's ordering — the discriminator is counts + confidence intervals, not
p-values. On thin data a non-significant test is fail-to-reject, NOT a confirmed null.
This script runs, in order:

  1. POWER TABLE — per company, distinct deduped benefit items pre/post 2022, and how many
     companies are computable on both sides. Gates whether per-company tests are worth it.
  2. AGGREGATE INDEX + bootstrap CI on a COVERAGE-BALANCED panel (same companies both
     periods). Wide CI overlapping the pre value → underpowered; tight CI → real null.
  3. POSITIVE CONTROL — changepoint on the H1 care axis; it MUST find the 2020 spike, else
     any locus null is a method artifact.
  4. H2 ON THE DENSE INSTRUMENT — rhetoric locus axis (hundreds of chunks, not dozens of
     items): z-scored per-company pre/post, Wilcoxon. The powered test.
  5. WITH/WITHOUT REMOTE sensitivity on the benefits index (remote is the contested rule).

Deferred (logged, not silently dropped): Kaplan-Meier survival, per-company benefits
changepoints, Fisher on 2-5-item cells — the per-company-year counts can't support them.
"""

from __future__ import annotations

import json
from collections import defaultdict

import numpy as np
import pandas as pd
import ruptures as rpt
from scipy import stats

from lowork.config import company_dir, load_companies

COS = [c for c in load_companies() if c != "netflix"]
PRE = (2015, 2021)
POST = (2022, 2026)
LOCI = ("individual", "structural")


def load_items(drop_remote=False):
    """{(co, period): {locus: set of distinct (category, verbatim) items}}. Period-level
    dedup so a benefit present across many years counts once per period."""
    d = defaultdict(lambda: defaultdict(set))
    for co in COS:
        p = company_dir(co) / "wellbeing_benefits.jsonl"
        if not p.exists():
            continue
        for line in p.open():
            r = json.loads(line)
            if r["locus"] not in LOCI:
                continue
            if drop_remote and r["category"] == "remote_flexibility":
                continue
            per = "pre" if PRE[0] <= r["year"] <= PRE[1] else ("post" if POST[0] <= r["year"] <= POST[1] else None)
            if per:
                d[(co, per)][r["locus"]].add((r["category"], r["verbatim"][:80]))
    return d


def index_of(counts):
    i, s = len(counts["individual"]), len(counts["structural"])
    return (i, s, i / (i + s)) if (i + s) else (i, s, None)


def power_table(d):
    print("=" * 70)
    print("1. POWER TABLE — distinct deduped benefit items per company/period")
    print(f"{'company':11} {'pre i/s':>9} {'post i/s':>9}  both-sides usable?")
    usable = []
    for co in COS:
        pi, ps, _ = index_of(d[(co, "pre")])
        qi, qs, _ = index_of(d[(co, "post")])
        ok = (pi + ps) >= 3 and (qi + qs) >= 3
        if ok:
            usable.append(co)
        print(f"{co:11} {f'{pi}/{ps}':>9} {f'{qi}/{qs}':>9}  {'YES' if ok else 'no (thin)'}")
    print(f"\n  companies usable on BOTH sides (>=3 items each): {len(usable)}/{len(COS)}")
    print(f"  -> {usable}")
    return usable


def bootstrap_ci(items, n=5000):
    """items: list of 1(individual)/0(structural). Bootstrap CI on the individual share."""
    if not items:
        return (None, None, None)
    arr = np.array(items)
    # deterministic bootstrap (no RNG seeding via Math.random-equivalent): fixed rng
    rng = np.random.default_rng(12345)
    boots = [arr[rng.integers(0, len(arr), len(arr))].mean() for _ in range(n)]
    return arr.mean(), np.percentile(boots, 2.5), np.percentile(boots, 97.5)


def aggregate_ci(d, usable, label=""):
    print("=" * 70)
    print(f"2. AGGREGATE INDEX + bootstrap CI on coverage-balanced panel {label}")
    print(f"   (balanced panel = {len(usable)} companies usable both sides)")
    for per in ("pre", "post"):
        items = []
        for co in usable:
            items += [1] * len(d[(co, per)]["individual"]) + [0] * len(d[(co, per)]["structural"])
        m, lo, hi = bootstrap_ci(items)
        print(f"   {per:4} (2015-21 / 2022-26): index={m:.3f}  95% CI [{lo:.3f}, {hi:.3f}]  n={len(items)}")


def positive_control_care():
    print("=" * 70)
    print("3. POSITIVE CONTROL — changepoint on the H1 care axis (must find ~2020)")
    frames = []
    for co in COS + ["netflix"]:
        try:
            df = pd.read_parquet(company_dir(co) / "axis_scores.parquet")
        except FileNotFoundError:
            continue
        w = df[(df["axis"] == "wellbeing") & (df["level"] == "chunk")][["year", "raw_topk_mean"]]
        frames.append(w)
    allw = pd.concat(frames)
    series = allw[allw["year"].between(2013, 2026)].groupby("year")["raw_topk_mean"].mean()
    years, vals = series.index.to_numpy(), series.to_numpy()
    algo = rpt.Pelt(model="rbf").fit(vals)
    bkps = algo.predict(pen=1.0)
    cp_years = [int(years[b - 1]) for b in bkps if b < len(years)]
    print(f"   pooled care series peak year: {int(years[np.argmax(vals)])} (value {vals.max():+.3f})")
    print(f"   PELT changepoint years: {cp_years}")
    print(f"   -> {'DETECTS the COVID-era shift' if any(2019 <= y <= 2021 for y in cp_years) or int(years[np.argmax(vals)])==2020 else 'FAILS to find 2020 — locus null would be suspect'}")


def h2_dense_rhetoric(drop_remote_note=""):
    print("=" * 70)
    print("4. H2 ON DENSE INSTRUMENT — rhetoric locus axis, per-company pre/post (z-scored)")
    pre_means, post_means, paired = [], [], []
    for co in COS:
        try:
            df = pd.read_parquet(company_dir(co) / "axis_scores.parquet")
        except FileNotFoundError:
            continue
        w = df[(df["axis"] == "wellbeing_locus") & (df["level"] == "chunk")][["year", "zscore"]].dropna()
        pre = w[w["year"].between(*PRE)]["zscore"].mean()
        post = w[w["year"].between(*POST)]["zscore"].mean()
        if np.isfinite(pre) and np.isfinite(post):
            paired.append((co, pre, post))
            pre_means.append(pre); post_means.append(post)
    print(f"   companies with both-period rhetoric: {len(paired)}")
    print(f"   mean z (positive=individual):  pre={np.mean(pre_means):+.3f}  post={np.mean(post_means):+.3f}")
    if len(paired) >= 6:
        w = stats.wilcoxon([p for _, p, _ in paired], [q for _, _, q in paired])
        rose = sum(1 for _, p, q in paired if q > p)
        print(f"   Wilcoxon signed-rank: W={w.statistic:.1f} p={w.pvalue:.3f}  "
              f"({rose}/{len(paired)} companies more individual post-2022)")
    print(f"   NOTE: fail-to-reject on this DENSE instrument is the credible null; "
          f"benefits composition is too sparse to carry it.{drop_remote_note}")


def main() -> int:
    d = load_items()
    usable = power_table(d)
    aggregate_ci(d, usable, "(all categories)")
    # 5. with/without remote sensitivity
    d_nr = load_items(drop_remote=True)
    usable_nr = [co for co in usable if (len(d_nr[(co, "pre")]["individual"]) + len(d_nr[(co, "pre")]["structural"])) >= 3
                 and (len(d_nr[(co, "post")]["individual"]) + len(d_nr[(co, "post")]["structural"])) >= 3]
    aggregate_ci(d_nr, usable_nr, "(EXCLUDING remote_flexibility — sensitivity)")
    positive_control_care()
    h2_dense_rhetoric()
    print("=" * 70)
    print("DEFERRED (data too thin): Kaplan-Meier survival, per-company benefits "
          "changepoints, Fisher on 2-5-item cells.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
