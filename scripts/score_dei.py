#!/usr/bin/env python
"""Score DEI inclusion/meritocracy intensity and aggregate register counts per year.

Writes data/<company>/dei_scores.parquet and dei_evidence.json.
Uses raw cosine scores (not z-scored) — near-zero is meaningful for absence.
"""

from __future__ import annotations

import argparse
from collections import Counter

import numpy as np
import pandas as pd

from lowork.axes import project, topk_mean
from lowork.config import AXES_DIR, TOP_K, company_dir
from lowork.dei import DEI_REGISTERS
from lowork.io import read_json, write_json

PRESENCE_THRESHOLD = 0.25  # inclusion cosine; tune after hand-label review
ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}


def load_pole_vector(name: str) -> np.ndarray:
    built = read_json(AXES_DIR / "built" / f"{name}.json")
    return np.asarray(built["vector"], dtype=np.float32)


def main(company: str) -> None:
    cdir = company_dir(company)
    df = pd.read_parquet(cdir / "embeddings.parquet")
    mission = df[df["label"].isin(ANALYSIS_LABELS)].copy()
    registers = read_json(cdir / "dei_registers.json")

    inc_vec = load_pole_vector("inclusion")
    mer_vec = load_pole_vector("meritocracy")
    embeddings = np.stack(mission["embedding"].tolist())
    mission["inclusion"] = project(embeddings, inc_vec)
    mission["meritocracy"] = project(embeddings, mer_vec)
    mission["register"] = mission["chunk_id"].map(registers)

    # Control overlay from Project 1 sentence-level scores if available
    control_by_year: dict[int, float] = {}
    scores_path = cdir / "axis_scores.parquet"
    if scores_path.exists():
        axis_scores = pd.read_parquet(scores_path)
        ctrl = axis_scores[
            (axis_scores["axis"] == "control") & (axis_scores["level"] == "sentence")
        ]
        control_by_year = {int(r.year): float(r.raw_topk_mean) for r in ctrl.itertuples()}

    rows = []
    evidence: dict[str, dict] = {"inclusion": {}, "meritocracy": {}}

    for year, group in mission.groupby("year"):
        year = int(year)
        inc_scores = group["inclusion"].to_numpy()
        mer_scores = group["meritocracy"].to_numpy()

        inc_mean, inc_k, inc_idx = topk_mean(inc_scores, TOP_K)
        mer_mean, mer_k, mer_idx = topk_mean(mer_scores, TOP_K)

        reg_counts = Counter(group["register"].dropna())
        reg_dict = {r: int(reg_counts.get(r, 0)) for r in DEI_REGISTERS}

        rows.append({
            "year": year,
            "n_chunks": len(group),
            "inclusion_mean": float(inc_scores.mean()),
            "inclusion_topk_mean": inc_mean,
            "inclusion_max": float(inc_scores.max()),
            "inclusion_k_used": inc_k,
            "inclusion_fraction_present": float((inc_scores >= PRESENCE_THRESHOLD).mean()),
            "meritocracy_mean": float(mer_scores.mean()),
            "meritocracy_topk_mean": mer_mean,
            "meritocracy_max": float(mer_scores.max()),
            "meritocracy_k_used": mer_k,
            "control_raw_topk_mean": control_by_year.get(year),
            **{f"register_{r}": reg_dict[r] for r in DEI_REGISTERS},
        })

        evidence["inclusion"][str(year)] = [
            {
                "text": group.iloc[i]["text"][:400],
                "heading": group.iloc[i]["heading"],
                "score": round(float(group.iloc[i]["inclusion"]), 4),
                "register": group.iloc[i]["register"],
            }
            for i in inc_idx
        ]
        evidence["meritocracy"][str(year)] = [
            {
                "text": group.iloc[i]["text"][:400],
                "heading": group.iloc[i]["heading"],
                "score": round(float(group.iloc[i]["meritocracy"]), 4),
                "register": group.iloc[i]["register"],
            }
            for i in mer_idx
        ]

    out_df = pd.DataFrame(rows).sort_values("year")
    out_df.to_parquet(cdir / "dei_scores.parquet", index=False)
    write_json(cdir / "dei_evidence.json", evidence)
    print(f"Wrote {cdir / 'dei_scores.parquet'} ({len(out_df)} years)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
