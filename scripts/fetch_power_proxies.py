#!/usr/bin/env python
"""Fetch the worker-power proxy (FRED JOLTS quits rate) + curated power events.

The quits rate is the canonical worker-bargaining-power signal: workers quit freely when
they have leverage (Great Resignation ~3% in 2021–22) and hunker down when they don't
(1.9% now). This is the measured spine of "culture is downstream of power" — the curve the
language trajectories are overlaid against. Economy-wide (not tech-only); tech tracked it.

Writes data/power_proxies.json: annual quits rate + dated power events.
"""

from __future__ import annotations

from collections import defaultdict

import httpx

from lowork.config import ROOT
from lowork.io import write_json

FRED_QUITS = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=JTSQUR"

# Curated, datable power events. kind: power_up (workers gain) / power_down (workers lose)
# / intervention (cultural program) / shift (ownership/control change).
EVENTS = [
    {"date": "2020-03", "label": "COVID shock — mass furloughs/layoffs", "kind": "power_down"},
    {"date": "2021-01", "label": "Alphabet Workers Union forms", "kind": "power_up"},
    {"date": "2021-04", "label": "Basecamp “no politics at work” → ~⅓ of staff quit", "kind": "shift"},
    {"date": "2021-11", "label": "Great Resignation — quits rate peaks (~3%)", "kind": "power_up"},
    {"date": "2022-11", "label": "Musk buys Twitter; “extremely hardcore” ultimatum", "kind": "shift"},
    {"date": "2022-11", "label": "Tech layoff wave begins (Meta, Amazon, Twitter)", "kind": "power_down"},
    {"date": "2023-01", "label": "Google cuts 12,000; layoffs broaden", "kind": "power_down"},
    {"date": "2023-06", "label": "SCOTUS ends affirmative action (DEI pressure)", "kind": "intervention"},
    {"date": "2024-09", "label": "Amazon mandates 5-day return-to-office", "kind": "power_down"},
    {"date": "2025-01", "label": "Meta ends DEI programs", "kind": "intervention"},
]


def annual_quits() -> list[dict]:
    r = httpx.get(FRED_QUITS, timeout=30, follow_redirects=True)
    r.raise_for_status()
    by_year: dict[int, list[float]] = defaultdict(list)
    for line in r.text.strip().splitlines()[1:]:  # skip header
        date, val = line.split(",")
        if not val or val == ".":
            continue
        by_year[int(date[:4])].append(float(val))
    return [
        {"year": y, "quitsRate": round(sum(v) / len(v), 3), "nMonths": len(v)}
        for y, v in sorted(by_year.items())
    ]


def main() -> None:
    quits = annual_quits()
    out = {
        "source": "FRED JOLTS Quits Rate (JTSQUR), annual mean of monthly observations.",
        "metric": "quitsRate",
        "metricLabel": "Worker power — JOLTS quits rate (% / month, annual mean)",
        "caveat": ("Economy-wide quits rate, not tech-only — a proxy for worker bargaining "
                   "power; tech tracked the national swing. Co-movement, not causation."),
        "quits": quits,
        "events": EVENTS,
    }
    write_json(ROOT / "data" / "power_proxies.json", out)
    peak = max(quits, key=lambda q: q["quitsRate"])
    print(f"Wrote data/power_proxies.json: {quits[0]['year']}–{quits[-1]['year']}, "
          f"peak {peak['quitsRate']} in {peak['year']}, latest {quits[-1]['quitsRate']} "
          f"({quits[-1]['year']}); {len(EVENTS)} events")


if __name__ == "__main__":
    main()
