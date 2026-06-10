#!/usr/bin/env python
"""Step 9a: Plotly validation chart — altruism + control z-scores over time,
coverage flags on thin years, hover shows top evidence quote.

Writes data/<company>/chart.html (open in a browser).
"""

from __future__ import annotations

import argparse

import pandas as pd
import plotly.graph_objects as go

from lowork.config import company_dir
from lowork.io import read_json


def main(company: str) -> None:
    cdir = company_dir(company)
    scores = pd.read_parquet(cdir / "axis_scores.parquet")
    quotes = read_json(cdir / "evidence_quotes.json")

    fig = go.Figure()
    for axis, style in [("altruism", {}), ("control", {"dash": "dot"})]:
        sub = scores[scores["axis"] == axis].sort_values("year")
        hover = [
            f"{int(r.year)}: z={r.zscore:.2f}, n={r.n_chunks} (k={r.k_used})<br>"
            + quotes[axis][str(int(r.year))][0]["text"][:160]
            for r in sub.itertuples()
        ]
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["zscore"], name=axis, mode="lines+markers",
            line=style, hovertext=hover, hoverinfo="text",
        ))

    thin = scores[(scores["axis"] == "altruism") & (scores["n_chunks"] < scores["k_used"].max())]
    if len(thin):
        fig.add_trace(go.Scatter(
            x=thin["year"], y=thin["zscore"], mode="markers", name="thin coverage",
            marker=dict(symbol="x", size=12),
        ))

    fig.update_layout(
        title=f"{company.title()} careers page: altruism axis over time (z-scored)",
        xaxis_title="Year", yaxis_title="z-score (within company)",
        template="plotly_white",
    )
    out = cdir / "chart.html"
    fig.write_html(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
