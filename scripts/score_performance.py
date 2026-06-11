#!/usr/bin/env python
"""Score performance-intensity language per year for careers and investor corpora.

Writes data/<company>/performance_scores.parquet and performance_evidence.json.
Uses raw cosine (single-pole) — near-zero means absent.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from lowork.axes import project, topk_mean
from lowork.config import AXES_DIR, TOP_K, company_dir
from lowork.io import read_json, write_json

PRESENCE_THRESHOLD = 0.25
ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}
INVESTOR_LABEL = "investor_filing"


def load_pole_vector(name: str) -> np.ndarray:
    built = read_json(AXES_DIR / "built" / f"{name}.json")
    return np.asarray(built["vector"], dtype=np.float32)


def score_corpus(
    df: pd.DataFrame,
    perf_vec: np.ndarray,
    source: str,
) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    evidence: dict[str, list] = {}

    for year, group in df.groupby("year"):
        year = int(year)
        embeddings = np.stack(group["embedding"].tolist())
        scores = project(embeddings, perf_vec)
        mean, k_used, top_idx = topk_mean(scores, TOP_K)

        rows.append({
            "year": year,
            "source": source,
            "n_chunks": len(group),
            "performance_mean": float(scores.mean()),
            "performance_topk_mean": mean,
            "performance_max": float(scores.max()),
            "performance_k_used": k_used,
            "performance_fraction_present": float((scores >= PRESENCE_THRESHOLD).mean()),
            "thin": len(group) < TOP_K,
        })

        evidence[str(year)] = [
            {
                "text": group.iloc[i]["text"][:400],
                "heading": group.iloc[i].get("heading", ""),
                "score": round(float(scores[i]), 4),
            }
            for i in top_idx
        ]

    return rows, evidence


def main(company: str) -> None:
    cdir = company_dir(company)
    perf_vec = load_pole_vector("performance")
    all_rows: list[dict] = []
    all_evidence: dict[str, dict] = {"careers": {}, "investor": {}}

    careers_path = cdir / "embeddings.parquet"
    if careers_path.exists():
        df = pd.read_parquet(careers_path)
        mission = df[df["label"].isin(ANALYSIS_LABELS)].copy()
        if len(mission):
            rows, evidence = score_corpus(mission, perf_vec, "careers")
            all_rows.extend(rows)
            all_evidence["careers"] = evidence
            print(f"Careers: {len(rows)} years, {len(mission)} chunks")

    investor_path = cdir / "investor_embeddings.parquet"
    if investor_path.exists():
        inv = pd.read_parquet(investor_path)
        if len(inv):
            rows, evidence = score_corpus(inv, perf_vec, "investor")
            all_rows.extend(rows)
            all_evidence["investor"] = evidence
            print(f"Investor: {len(rows)} years, {len(inv)} chunks")

    if not all_rows:
        raise SystemExit(f"No embeddings found for {company}")

    out = cdir / "performance_scores.parquet"
    pd.DataFrame(all_rows).to_parquet(out, index=False)
    write_json(cdir / "performance_evidence.json", all_evidence)
    print(f"Wrote {out} ({len(all_rows)} rows)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
