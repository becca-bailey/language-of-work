#!/usr/bin/env python
"""Step 7: project mission chunks onto axes, aggregate per year, z-score.

- Signed projection of each mission_brand chunk onto each built axis
- Per-year adaptive top-k mean (k = min(5, n)); n recorded for coverage flags
- Z-score within company across years (raw projections are not comparable
  across axes)
- Near-duplicate detection across adjacent years -> carried-forward fractions

Writes data/<company>/axis_scores.parquet and evidence_quotes.json.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from lowork.axes import near_duplicates, project, topk_mean, zscore
from lowork.config import AXES_DIR, NEAR_DUP_COSINE, TOP_K, company_dir
from lowork.io import read_json, write_json


def carried_forward(df: pd.DataFrame) -> dict[int, float]:
    """Fraction of each year's mission chunks near-duplicated in the prior year."""
    years = sorted(df["year"].unique())
    result: dict[int, float] = {}
    for prev, curr in zip(years, years[1:]):
        prev_emb = np.stack(df[df["year"] == prev]["embedding"].tolist())
        curr_emb = np.stack(df[df["year"] == curr]["embedding"].tolist())
        combined = np.concatenate([curr_emb, prev_emb])
        dup = near_duplicates(combined, NEAR_DUP_COSINE)
        n_curr = len(curr_emb)
        carried = sum(dup[i, n_curr:].any() for i in range(n_curr))
        result[int(curr)] = round(carried / n_curr, 3)
    return result


def main(company: str, axis_names: list[str]) -> None:
    cdir = company_dir(company)
    df = pd.read_parquet(cdir / "embeddings.parquet")
    mission = df[df["label"] == "mission_brand"].reset_index(drop=True)
    print(f"{len(mission)} mission chunks across {mission['year'].nunique()} years")
    embeddings = np.stack(mission["embedding"].tolist())

    rows = []
    quotes: dict[str, dict] = {}
    for name in axis_names:
        built = read_json(AXES_DIR / "built" / f"{name}.json")
        assert built["model"] == mission["model"].iloc[0], "axis/chunk model mismatch"
        axis_vec = np.asarray(built["vector"], dtype=np.float32)
        scores = project(embeddings, axis_vec)
        mission[f"score_{name}"] = scores

        year_rows = []
        for year, group in mission.groupby("year"):
            mean, k_used, top_idx = topk_mean(group[f"score_{name}"].to_numpy(), TOP_K)
            top_chunks = group.iloc[top_idx]
            quotes.setdefault(name, {})[str(year)] = [
                {"text": r["text"], "heading": r["heading"],
                 "score": round(float(r[f"score_{name}"]), 4)}
                for _, r in top_chunks.iterrows()
            ]
            year_rows.append({"axis": name, "year": int(year),
                              "raw_topk_mean": mean, "k_used": k_used, "n_chunks": len(group)})

        year_df = pd.DataFrame(year_rows)
        year_df["zscore"] = zscore(year_df["raw_topk_mean"].to_numpy())
        rows.append(year_df)
        print(f"Axis '{name}': scored {len(year_df)} years")

    scores_df = pd.concat(rows, ignore_index=True)
    cf = carried_forward(mission)
    scores_df["carried_forward_frac"] = scores_df["year"].map(cf)

    scores_df.to_parquet(cdir / "axis_scores.parquet", index=False)
    write_json(cdir / "evidence_quotes.json", quotes)
    print(f"Wrote {cdir / 'axis_scores.parquet'} and {cdir / 'evidence_quotes.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("axes", nargs="*", default=["altruism", "control"])
    args = parser.parse_args()
    main(args.company, args.axes)
