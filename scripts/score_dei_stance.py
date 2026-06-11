#!/usr/bin/env python
"""Score chunks on the bipolar DEI stance contrast axis per year.

Writes data/<company>/dei_stance_scores.parquet (year aggregates + envelope).
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from lowork.axes import project, topk_mean
from lowork.chunking import dedup_chunks
from lowork.config import AXES_DIR, TOP_K, company_dir
from lowork.io import read_json, write_json
from lowork.text_filter import is_english

ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}


def load_axis_vector(name: str) -> np.ndarray:
    built = read_json(AXES_DIR / "built" / f"{name}.json")
    return np.asarray(built["vector"], dtype=np.float32)


def _quote_row(row: pd.Series) -> dict:
    return {
        "text": str(row["text"])[:400],
        "heading": row.get("heading", ""),
        "register": row.get("register"),
        "stanceProjection": round(float(row["dei_stance"]), 4),
        "score": round(float(row["dei_stance"]), 4),
    }


def main(company: str) -> None:
    cdir = company_dir(company)
    df = pd.read_parquet(cdir / "embeddings.parquet")
    mission = df[df["label"].isin(ANALYSIS_LABELS)].copy()
    registers = read_json(cdir / "dei_registers.json")
    stance_vec = load_axis_vector("dei_stance")

    embeddings = np.stack(mission["embedding"].tolist())
    mission["dei_stance"] = project(embeddings, stance_vec)
    mission["register"] = mission["chunk_id"].map(registers)

    rows = []
    evidence: dict[str, dict] = {}

    for year, raw_group in mission.groupby("year"):
        year = int(year)
        en_mask = raw_group["text"].apply(is_english)
        group = raw_group[en_mask].copy()
        deduped = dedup_chunks(group.to_dict("records"))
        group = pd.DataFrame(deduped)
        if group.empty:
            continue

        scores = group["dei_stance"].to_numpy()
        tk_mean, k_used, top_idx = topk_mean(scores, TOP_K)

        max_idx = int(scores.argmax())
        min_idx = int(scores.argmin())

        rows.append({
            "year": year,
            "n_chunks": len(group),
            "stance_projection_topk_mean": tk_mean,
            "stance_projection_mean": float(scores.mean()),
            "stance_projection_max": float(scores[max_idx]),
            "stance_projection_min": float(scores[min_idx]),
            "stance_projection_k_used": k_used,
            "stance_salience_topk_mean": float(np.abs(scores[top_idx]).mean()),
        })

        evidence[str(year)] = {
            "stanceProjectionTopkMean": round(tk_mean, 4),
            "stanceProjectionMax": round(float(scores[max_idx]), 4),
            "stanceProjectionMin": round(float(scores[min_idx]), 4),
            "stanceMaxQuote": _quote_row(group.iloc[max_idx]),
            "stanceMinQuote": _quote_row(group.iloc[min_idx]),
            "topQuotes": [_quote_row(group.iloc[i]) for i in top_idx],
        }

    out_df = pd.DataFrame(rows).sort_values("year")
    out_df.to_parquet(cdir / "dei_stance_scores.parquet", index=False)
    write_json(cdir / "dei_stance_evidence.json", evidence)
    print(f"Wrote {cdir / 'dei_stance_scores.parquet'} ({len(out_df)} years)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
