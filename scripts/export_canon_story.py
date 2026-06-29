#!/usr/bin/env python
"""Export the Project-3 (values-as-IP) story JSON for the Next.js story page.

The Automattic thesis (Pathway B / H5) is two *separable* firm-register series on
the `mission_rights` axis: the codified **canon** holds at the mission pole while
**conduct** language (other firm text) erupts toward the rights/enforcement pole
under stress (the 2024 WP Engine rupture). A single blended line would be
uninterpretable, so canon and conduct are scored separately. Worker-register text
is excluded — H2's cross-register confound is out of scope for this view.

Reads data/<case>/embeddings.parquet (canon label set) and the built axis, writes
astro/src/data/stories/values-as-ip.json.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from lowork.axes import project
from lowork.company import CompanyProfile
from lowork.config import WEB_DATA_DIR, AXES_DIR, ROOT, company_dir
from lowork.io import read_json, write_json

AXIS = "mission_rights"
POLE_HIGH, POLE_LOW = "mission", "rights"  # project = mission − rights (positive = mission)
THIN_N = 3  # a year's mean is "thin" below this many chunks
MAX_QUOTE_CHARS = 260


def _year_series(sub: pd.DataFrame) -> list[dict]:
    rows = []
    for year, g in sub.groupby("year"):
        rows.append({
            "year": int(year),
            "value": round(float(g[AXIS].mean()), 4),
            "n": int(len(g)),
            "thin": bool(len(g) < THIN_N),
        })
    return sorted(rows, key=lambda r: r["year"])


def _quotes(sub: pd.DataFrame, *, toward: str, k: int = 4) -> list[dict]:
    """Top-k chunks toward a pole (rights = most negative, mission = most positive)."""
    ordered = sub.sort_values(AXIS, ascending=(toward == "rights")).head(k)
    return [
        {
            "year": int(r["year"]),
            "text": r["text"].strip()[:MAX_QUOTE_CHARS],
            "heading": r["heading"] or "",
            "score": round(float(r[AXIS]), 4),
        }
        for _, r in ordered.iterrows()
    ]


def build_case(case: str) -> dict | None:
    cdir = company_dir(case)
    emb_path = cdir / "embeddings.parquet"
    if not emb_path.exists():
        print(f"  {case}: no embeddings.parquet — skipping")
        return None

    df = pd.read_parquet(emb_path)
    firm = df[df["register"] == "firm"].copy()
    if firm.empty:
        print(f"  {case}: no firm-register chunks — skipping")
        return None

    axis_vec = np.asarray(read_json(AXES_DIR / "built" / f"{AXIS}.json")["vector"], dtype=np.float32)
    firm[AXIS] = project(np.stack(firm["embedding"].tolist()), axis_vec)

    canon = firm[firm["label"] == "canon"]
    conduct = firm[firm["label"] == "on_topic"]

    # Pooled canon reference band (the "frozen" values position): mean ± 1 std.
    canon_vals = canon[AXIS].to_numpy()
    band = {
        "mean": round(float(canon_vals.mean()), 4),
        "lo": round(float(canon_vals.mean() - canon_vals.std()), 4),
        "hi": round(float(canon_vals.mean() + canon_vals.std()), 4),
        "n": int(len(canon_vals)),
    }

    profile = CompanyProfile.load(case)
    return {
        "company": case,
        "displayName": profile.display_name,
        "canonBand": band,
        "series": [
            {"id": "canon", "label": "Canon (codified values)", "years": _year_series(canon)},
            {"id": "conduct", "label": "Conduct (other firm text)", "years": _year_series(conduct)},
        ],
        "rightsQuotes": _quotes(conduct, toward="rights"),
        "missionQuotes": _quotes(canon, toward="mission"),
    }


# Per-case external events (the dated ruptures the timeline reads against).
CASE_EVENTS: dict[str, list[dict]] = {
    "automattic": [
        {
            "id": "wpengine",
            "label": "WP Engine rupture",
            "year": 2024 + 9 / 12,
            "description": "September 2024 — Automattic/Matt Mullenweg move against WP Engine: "
                           "trademark demands, an 8% license-fee claim, and control of the "
                           "WordPress.org login — the mission canon turned into enforced rights.",
        },
    ],
}


def main(cases: list[str]) -> None:
    series = []
    for case in cases:
        built = build_case(case)
        if built:
            built["events"] = CASE_EVENTS.get(case, [])
            series.append(built)

    if not series:
        print("No cases with data — nothing written.")
        return

    out = {
        "story": "values-as-ip",
        "title": "When Values Become Intellectual Property",
        "axis": AXIS,
        "poleHigh": POLE_HIGH,
        "poleLow": POLE_LOW,
        "metricLabel": "mission ←→ rights (firm-register projection)",
        "cases": series,
    }
    out_dir = WEB_DATA_DIR / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "values-as-ip.json", out)
    print(f"Wrote {out_dir / 'values-as-ip.json'} ({len(series)} case(s))")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="automattic")
    main([c.strip() for c in parser.parse_args().cases.split(",")])
