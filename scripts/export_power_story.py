#!/usr/bin/env python
"""Assemble the keystone "Culture is downstream of power" story (N=11, consistent set).

Joins the worker-power curve (FRED quits, data/power_proxies.json) with three language
trajectories — idealism (cleaned altruism), DEI (active register share), performance
(presence) — each an industry mean over the SAME 11 companies, plus per-company series so
the chart can toggle aggregate ↔ per-company.

Reframe (per the user): idealism is an industry-optimism barometer, not a worker
concession — it co-moves with worker power because both ride the same boom. DEI is the
worker-oriented (conditional) intervention; performance is the management-serving constant.

Writes web/public/data/stories/power.json.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lowork.axes import project
from lowork.company import CompanyProfile
from lowork.config import AXES_DIR, ROOT, TOP_K, company_dir
from lowork.io import read_json, write_json

STORIES = ROOT / "web" / "public" / "data" / "stories"

# ONE set for ALL THREE metrics (no per-metric subsets). Every company is scored on all
# three axes. Basecamp/Twitter are documented cases elsewhere, not in this aggregate.
COHORT = ["google", "amazon", "meta", "palantir", "coinbase", "netflix",
          "shopify", "stripe", "airbnb", "brex", "snap"]

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


def _wellbeing_per_company() -> dict[str, dict[int, float]]:
    """Wellbeing projection (balance↔sacrifice) per company, scored over BOTH mission_brand
    AND benefits_perks chunks — benefits copy is where wellbeing actually lives (81% of it),
    so restricting to mission_brand undercounted it badly. Top-k chunk projection per year."""
    vec = np.asarray(read_json(AXES_DIR / "built" / "wellbeing.json")["vector"], dtype=np.float32)
    out: dict[str, dict[int, float]] = {}
    for c in COHORT:
        p = company_dir(c) / "embeddings.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        sub = df[df["label"].isin(["mission_brand", "benefits_perks"])]
        if sub.empty:
            continue
        proj = project(np.stack(sub["embedding"].tolist()).astype(np.float32), vec)
        sub = sub.assign(_w=proj)
        d = {}
        for y, g in sub.groupby("year"):
            top = sorted(g["_w"].tolist(), reverse=True)[:TOP_K]
            d[int(y)] = sum(top) / len(top)
        if d:
            out[c] = d
    return out


def _per_company_from_story(companies: list[dict], field: str) -> dict[str, dict[int, float]]:
    out: dict[str, dict[int, float]] = {}
    for c in companies:
        if c["id"] not in COHORT:
            continue
        out[c["id"]] = {int(y["year"]): float(y[field])
                        for y in c.get("years", []) if y.get(field) is not None}
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


# Power-shift cases: ownership/control concentrates -> culture hardens immediately.
# Documented primary docs, NOT in the quant aggregate (illustrations).
CASES = [
    {
        "company": "Basecamp", "date": "2021-04", "title": "“Changes at Basecamp”",
        "shift": ("Founders unilaterally banned political talk, scrapped committees and "
                  "“paternalistic” benefits; ~1/3 of staff took buyouts and left."),
        "quotes": [
            "No more societal and political discussions on our company Basecamp account.",
            "No more paternalistic benefits.",
            "No more committees.",
        ],
        "source": "Jason Fried, world.hey.com/jason/changes-at-basecamp-7f32afc5 (Apr 2021)",
    },
    {
        "company": "Twitter / X", "date": "2022-11", "title": "“Extremely hardcore”",
        "shift": ("Days after Musk's takeover, an ultimatum: commit to “extremely "
                  "hardcore” long hours or take severance — after ~50% layoffs and an RTO order."),
        "quotes": [
            "Going forward, to build a breakthrough Twitter 2.0 … we will need to be extremely hardcore. This will mean working long hours at high intensity.",
            "Only exceptional performance will constitute a passing grade.",
        ],
        "source": "Elon Musk, all-staff email, Nov 16 2022 (widely reported)",
    },
]


def _event_year(date: str) -> float:
    y, _, m = date.partition("-")
    return int(y) + ((int(m) - 1) / 12 if m else 0)


def main() -> None:
    dei = read_json(STORIES / "dei.json")["sources"]["careers"]["companies"]
    perf = read_json(STORIES / "performance.json")["sources"]["careers"]["companies"]
    power = read_json(ROOT / "data" / "power_proxies.json")

    metrics = [
        _metric_block(
            "idealism", "Idealism — industry-optimism barometer", "optimism",
            "rises and falls with the boom (not a worker concession)",
            _idealism_per_company()),
        _metric_block(
            "dei", "DEI language — worker-oriented (conditional)", "workers",
            "surged ~2021, rolled back from 2023",
            _per_company_from_story(dei, "activeShare")),
        _metric_block(
            "wellbeing", "Wellbeing / balance — worker concession", "wellbeing",
            "the balance/rest framing — given in the boom, quietly withdrawn",
            _wellbeing_per_company()),
        _metric_block(
            "performance", "Performance / intensity — management-serving (constant)",
            "management", "needs no leverage to survive — the constant substrate",
            _per_company_from_story(perf, "fractionPresent")),
    ]

    pseries = [p for p in power["quits"] if p["year"] >= START_YEAR]
    pvals = [p["quitsRate"] for p in pseries]
    plo, phi = min(pvals), max(pvals)
    prng = (phi - plo) or 1.0
    power_series = [
        {"year": p["year"], "value": p["quitsRate"],
         "norm": round((p["quitsRate"] - plo) / prng, 4)} for p in pseries
    ]

    out = {
        "story": "power",
        "title": "Culture is downstream of power",
        "subtitle": "The language that rises and falls with workers' leverage — and the part that never needed it.",
        "thesis": ("Across 11 companies, the optimism barometer (idealism) and the "
                   "worker-oriented intervention (DEI) both track worker bargaining power "
                   "(the quits rate) — they ride the boom up and recede when it ends. "
                   "Performance/intensity, which serves whoever can hire and fire, is flat "
                   "regardless. The culture that persists is the part that benefits the "
                   "people in power; the rest is rented."),
        "companies": COHORT,
        "companiesNote": (
            f"All three metrics are means over the same {len(COHORT)} companies, each scored "
            "on all three axes — no per-metric subsetting. Basecamp and Twitter/X are "
            "documented as power-shift cases below, not in this aggregate (Basecamp has no "
            "careers corpus; Twitter/X is thin post-2022)."),
        "power": {"label": power["metricLabel"], "caveat": power["caveat"], "series": power_series},
        "metrics": metrics,
        "cases": CASES,
        "events": [
            {"year": round(_event_year(e["date"]), 3), "date": e["date"],
             "label": e["label"], "kind": e["kind"]}
            for e in power["events"]
        ],
    }
    write_json(STORIES / "power.json", out)
    print(f"Wrote power.json (n={len(COHORT)})")
    for m in metrics:
        print(f"  {m['label'][:34]:34s} agg {len(m['series'])}yrs, perCompany={len(m['perCompany'])}")


if __name__ == "__main__":
    main()
