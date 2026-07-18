#!/usr/bin/env python
"""Assemble the keystone "Culture is downstream of power" story (one consistent set).

Joins the worker-power curve (FRED quits, data/power_proxies.json) with four language
trajectories — idealism (cleaned altruism), DEI (active register share), wellbeing
(care axis, chunk-level top-k from axis_scores.parquet), performance (presence) — each
an industry mean over the SAME companies, plus per-company series so the chart can
toggle aggregate ↔ per-company. A fifth exported series, wellbeing_locus (individual ↔
structural care), carries the "the care that survived was worker-absorbed" panel.

Reframe (per the user): idealism is an industry-optimism barometer, not a worker
concession — it co-moves with worker power because both ride the same boom. DEI is the
worker-oriented (conditional) intervention; performance is the management-serving constant.
Wellbeing is the contrast case: it spikes with the 2020 emergency (not the 2021-22
leverage peak), deflates afterward without ever being cut the way DEI was, and what
shifts instead is the locus — the surviving care drifts onto the individual worker.

Writes astro/src/data/stories/power.json.
"""

from __future__ import annotations

import pandas as pd

from lowork.company import CompanyProfile
from lowork.dei import ACTIVE_DEI_REGISTERS as _ACTIVE_DEI
from lowork.config import WEB_DATA_DIR, ROOT, company_dir, load_companies
from lowork.io import read_json, write_json

STORIES = WEB_DATA_DIR / "stories"

# ONE set for ALL metrics (no per-metric subsets). Every company is scored on
# every axis. Basecamp/Twitter are documented cases elsewhere, not in this aggregate.
COHORT = load_companies()

# Normalize/display within the window of real multi-company coverage.
START_YEAR = 2013


def _idealism_per_company() -> dict[str, dict[int, float]]:
    """Raw world-changing projection (techno removed) per company from the split parquet."""
    out: dict[str, dict[int, float]] = {}
    for c in COHORT:
        p = company_dir(c) / "altruism_split.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        out[c] = {int(r.year): float(r.world_topk) for r in df.itertuples()
                  if int(r.world_n) > 0 and pd.notna(r.world_topk)}
    return out


def _axis_per_company(axis: str) -> dict[str, dict[int, float]]:
    """Chunk-level raw top-k axis projection per company-year, read straight from
    axis_scores.parquet (score_axes over FINGERPRINT_AXES) — the same series the
    wellbeing story pools, so the power panel and the wellbeing page tell one
    story from one source. Supersedes the old ad-hoc embeddings projection."""
    out: dict[str, dict[int, float]] = {}
    for c in COHORT:
        p = company_dir(c) / "axis_scores.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        sub = df[(df["axis"] == axis) & (df["level"] == "chunk")]
        series = {int(r.year): float(r.raw_topk_mean)
                  for r in sub.itertuples() if pd.notna(r.raw_topk_mean)}
        if series:
            out[c] = series
    return out


def _per_company_from_story(companies: list[dict], field: str) -> dict[str, dict[int, float]]:
    out: dict[str, dict[int, float]] = {}
    for c in companies:
        if c["id"] not in COHORT:
            continue
        out[c["id"]] = {int(y["year"]): float(y[field])
                        for y in c.get("years", []) if y.get(field) is not None}
    return out


# Active (pro-inclusion) DEI registers — must match StoryRegisterChart.


def _dei_active_share() -> dict[str, dict[int, float]]:
    """Per company-year active-DEI-register share, read straight from each
    company's dei_scores.parquet — power owns its data, no dei.json dependency."""
    out: dict[str, dict[int, float]] = {}
    for c in COHORT:
        p = company_dir(c) / "dei_scores.parquet"
        if not p.exists():
            continue
        series: dict[int, float] = {}
        for r in pd.read_parquet(p).itertuples():
            n = int(getattr(r, "n_chunks", 0) or 0)
            active = sum(int(getattr(r, f"register_{reg}", 0)) for reg in _ACTIVE_DEI)
            series[int(r.year)] = (active / n) if n > 0 else 0.0
        out[c] = series
    return out


def _performance_per_company() -> dict[str, dict[int, float]]:
    """Careers performance presence per company from performance_scores.parquet —
    read from source, not the performance story JSON."""
    out: dict[str, dict[int, float]] = {}
    for c in COHORT:
        p = company_dir(c) / "performance_scores.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        sub = df[df["source"] == "careers"]
        out[c] = {int(r.year): float(r.performance_fraction_present)
                  for r in sub.itertuples() if pd.notna(r.performance_fraction_present)}
    return out


def _metric_block(mid: str, label: str, benefits: str, note: str,
                  per_company: dict[str, dict[int, float]]) -> dict:
    years = sorted({y for d in per_company.values() for y in d if y >= START_YEAR})
    mean = {}
    for y in years:
        vals = [d[y] for d in per_company.values() if y in d]
        mean[y] = sum(vals) / len(vals)
    allvals = [v for d in per_company.values() for (y, v) in d.items() if y >= START_YEAR]
    lo, hi = (min(allvals), max(allvals)) if allvals else (0.0, 1.0)
    rng = (hi - lo) or 1.0
    nm = lambda v: round((v - lo) / rng, 4)  # noqa: E731
    agg = [{"year": y, "value": round(mean[y], 4), "norm": nm(mean[y])} for y in years]
    comps = []
    for c, d in per_company.items():
        s = [{"year": y, "value": round(d[y], 4), "norm": nm(d[y])}
             for y in sorted(d) if y >= START_YEAR]
        if s:
            comps.append({"id": c, "displayName": CompanyProfile.load(c).display_name, "series": s})
    return {"id": mid, "label": label, "benefits": benefits, "note": note,
            "series": agg, "perCompany": comps}


def _event_year(date: str) -> float:
    y, _, m = date.partition("-")
    return int(y) + ((int(m) - 1) / 12 if m else 0)


def main(companies: list[str] | None = None) -> None:
    # The pipeline orchestrator passes the power story's effective company set;
    # standalone CLI use keeps the default COHORT.
    global COHORT
    if companies is not None:
        COHORT = list(companies)
    # Every metric is read from source parquet — power.json is self-contained and
    # does not depend on the dei/performance story JSONs being regenerated first.
    power = read_json(ROOT / "data" / "power_proxies.json")

    metrics = [
        _metric_block(
            "idealism", "Idealism — industry-optimism barometer", "optimism",
            "rises and falls with the boom (not a worker concession)",
            _idealism_per_company()),
        _metric_block(
            "dei", "DEI language — worker-oriented (conditional)", "workers",
            "surged ~2021, rolled back from 2023",
            _dei_active_share()),
        _metric_block(
            "wellbeing", "Care / wellbeing — tracks the emergency, not the leverage",
            "wellbeing", "spiked in 2020, deflated after — never cut the way DEI was",
            _axis_per_company("wellbeing")),
        _metric_block(
            "performance", "Performance / intensity — management-serving (constant)",
            "management", "needs no leverage to survive — the constant substrate",
            _performance_per_company()),
        # Locus of care (individual ↔ structural): + = worker-absorbed (therapy
        # apps, resilience), − = organization-absorbed (staffing, coverage).
        # Exported last so the chart can treat it as a companion panel rather
        # than a fourth counterforce line.
        _metric_block(
            "wellbeing_locus", "Locus of care — individual (+) vs structural (−)",
            "wellbeing", "the care that endured shifted onto the individual worker",
            _axis_per_company("wellbeing_locus")),
    ]

    pseries = [p for p in power["quits"] if p["year"] >= START_YEAR]
    pvals = [p["quitsRate"] for p in pseries]
    plo, phi = min(pvals), max(pvals)
    prng = (phi - plo) or 1.0
    power_series = [
        {"year": p["year"], "value": p["quitsRate"],
         "norm": round((p["quitsRate"] - plo) / prng, 4)} for p in pseries
    ]

    # Editorial framing (title, subtitle, thesis, the cohort note) lives in the
    # MDX. Basecamp/Twitter were illustrative "shift" cases outside the 11-company
    # dataset — drop the cases block and their chart annotations (kind=="shift").
    out = {
        "story": "power",
        "companies": COHORT,
        "power": {"label": power["metricLabel"], "caveat": power["caveat"], "series": power_series},
        "metrics": metrics,
        "events": [
            {"year": round(_event_year(e["date"]), 3), "date": e["date"],
             "label": e["label"], "kind": e["kind"]}
            for e in power["events"]
            if e["kind"] != "shift"
        ],
    }
    write_json(STORIES / "power.json", out)
    print(f"Wrote power.json (n={len(COHORT)})")
    for m in metrics:
        print(f"  {m['label'][:34]:34s} agg {len(m['series'])}yrs, perCompany={len(m['perCompany'])}")


if __name__ == "__main__":
    main()
