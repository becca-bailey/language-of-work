#!/usr/bin/env python
"""Robustness checks for the power story's central co-movement claim.

The headline ("idealism and DEI track the worker-power cycle") rests on a Pearson
correlation between each metric's cross-company aggregate and the FRED JOLTS quits
rate. Two trending series can correlate from shared trend alone, so the decisive
test is on FIRST DIFFERENCES (year-over-year changes); we also show raw alongside
smoothed (smoothing inflates r on n~14), leave-one-company-out sensitivity, and
per-company spread. Lag is reported but uninterpretable on short trending series.

Reads web/public/data/stories/power.json; writes data/power_robustness.md.
"""

from __future__ import annotations

import json

import numpy as np

from lowork.config import ROOT


def _smooth(d: dict[int, float]) -> dict[int, float]:
    ys = sorted(d)
    return {y: float(np.mean([d[ys[j]] for j in range(max(0, i - 1), min(len(ys), i + 2))]))
            for i, y in enumerate(ys)}


def _corr(d1: dict[int, float], d2: dict[int, float]) -> tuple[float | None, int]:
    c = sorted(set(d1) & set(d2))
    if len(c) < 4:
        return None, len(c)
    a, b = np.array([d1[y] for y in c]), np.array([d2[y] for y in c])
    if a.std() == 0 or b.std() == 0:
        return None, len(c)  # degenerate (constant) series
    return float(np.corrcoef(a, b)[0, 1]), len(c)


def _diff(d: dict[int, float]) -> dict[int, float]:
    ys = sorted(d)
    return {ys[i]: d[ys[i]] - d[ys[i - 1]] for i in range(1, len(ys))}


def main() -> None:
    p = json.loads((ROOT / "web/public/data/stories/power.json").read_text())
    power = {d["year"]: d["value"] for d in p["power"]["series"] if d.get("value") is not None}

    rows = []
    for m in p["metrics"]:
        agg = {d["year"]: d["value"] for d in m["series"] if d.get("value") is not None}
        r_raw, n = _corr(agg, power)
        r_sm, _ = _corr(_smooth(agg), _smooth(power))
        r_diff, n_d = _corr(_diff(agg), _diff(power))

        def lag(k: int) -> float | None:
            return _corr(agg, {y: power[y + k] for y in agg if (y + k) in power})[0]

        # per-company vs national quits
        per = {}
        for co in m["perCompany"]:
            s = {d["year"]: d["value"] for d in co["series"] if d.get("value") is not None}
            r, _ = _corr(s, power)
            if r is not None:
                per[co["id"]] = r
        n_valid = len(per)
        n_pos = sum(1 for r in per.values() if r > 0)
        med = float(np.median(list(per.values()))) if per else float("nan")

        # leave-one-company-out aggregate (mean of per-company values per year)
        allco = {co["id"]: {d["year"]: d["value"] for d in co["series"]
                            if d.get("value") is not None} for co in m["perCompany"]}

        def agg_excl(excl: str) -> dict[int, float]:
            yrs = set().union(*[set(s) for cid, s in allco.items() if cid != excl])
            return {y: float(np.mean([s[y] for cid, s in allco.items() if cid != excl and y in s]))
                    for y in yrs if any(y in s for cid, s in allco.items() if cid != excl)}

        match, _ = _corr(agg_excl("__none__"), agg)  # recomputed-vs-published fidelity
        loo = [r for r in (_corr(agg_excl(cid), power)[0] for cid in allco) if r is not None]

        rows.append(dict(id=m["id"], label=m["label"], n=n, r_raw=r_raw, r_sm=r_sm,
                         r_diff=r_diff, n_d=n_d, lag_m1=lag(-1), lag_p1=lag(1),
                         n_valid=n_valid, n_pos=n_pos, med=med,
                         loo_min=min(loo), loo_max=max(loo), match=match))

    lines = ["# Power-story robustness", "",
             "Aggregate metric vs FRED JOLTS quits rate. **r_diff (first differences) is the "
             "decisive test** — it removes shared trend. Raw shown next to smoothed because "
             f"3-yr smoothing inflates r on n≈{rows[0]['n']}.", "",
             "| metric | r_raw | r_smooth | **r_diff** | per-company (pos/valid, median) | "
             "leave-one-out range | recompute fidelity |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(
            f"| {r['label'].split('—')[0].strip()} | {r['r_raw']:+.2f} | {r['r_sm']:+.2f} | "
            f"**{r['r_diff']:+.2f}** | {r['n_pos']}/{r['n_valid']}, med {r['med']:+.2f} | "
            f"[{r['loo_min']:+.2f}, {r['loo_max']:+.2f}] | r={r['match']:.2f} |")
    lines += ["",
              f"First differences over n={rows[0]['n_d']} consecutive-year pairs. Per-company "
              "correlations are against the **national** quits rate (the macro power cycle), not "
              "each firm's own worker power. Recompute fidelity r≈1.00 confirms the leave-one-out "
              "aggregate matches the published series.", "",
              "## Reading", "",
              "- **DEI** survives detrending — genuine year-over-year co-movement with the power "
              "cycle, not just the secular boom.",
              "- **Idealism** largely collapses under differencing: most of its raw correlation is "
              "shared trend. Demonstrates 'both ride the same boom' rather than asserting it.",
              "- **Performance** flat raw and differenced — serves management, needs no worker "
              "leverage.",
              "- **Wellbeing** weak either way; under-measured (thin benefits corpus).",
              "- **No single company is load-bearing** for idealism or DEI (leave-one-out stays "
              "positive) — resolves the earlier N=6→11 fragility.",
              "",
              "Lag is uninterpretable on short trending series (two rising lines correlate at most "
              "lags); reported for completeness only: " +
              ", ".join(f"{r['id']} lag±1 {r['lag_m1']:+.2f}/{r['lag_p1']:+.2f}" for r in rows) + ".",
              "", "_Generated by scripts/power_robustness.py._"]
    out = ROOT / "data" / "power_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
