#!/usr/bin/env python
"""Step 7: project mission chunks/sentences onto axes, aggregate per year, z-score.

- Chunk level (default): signed projection of each mission_brand chunk
- Sentence level: split mission chunks into sentences, project each, top-k
  sentences per year (addresses dense-page dilution in early eras)
- Near-duplicate detection across adjacent years at chunk level

Writes data/<company>/axis_scores.parquet (level column) and evidence_quotes.json.
"""

from __future__ import annotations

import argparse
import hashlib

import numpy as np
import pandas as pd

from lowork.axes import near_duplicates, project, topk_mean, zscore
from lowork.config import AXES_DIR, EMBEDDING_MODEL, NEAR_DUP_COSINE, TOP_K, company_dir
from lowork.embeddings import EmbeddingStore
from lowork.io import read_json, write_json
from lowork.sentences import split_sentences


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


def score_chunk_level(mission: pd.DataFrame, axis_names: list[str]) -> tuple[pd.DataFrame, dict]:
    embeddings = np.stack(mission["embedding"].tolist())
    rows = []
    quotes: dict[str, dict[str, dict]] = {}  # axis -> level -> year -> quotes

    for name in axis_names:
        built = read_json(AXES_DIR / "built" / f"{name}.json")
        axis_vec = np.asarray(built["vector"], dtype=np.float32)
        scores = project(embeddings, axis_vec)
        mission = mission.copy()
        mission[f"score_{name}"] = scores

        year_rows = []
        quotes.setdefault(name, {}).setdefault("chunk", {})
        for year, group in mission.groupby("year"):
            mean, k_used, top_idx = topk_mean(group[f"score_{name}"].to_numpy(), TOP_K)
            top_chunks = group.iloc[top_idx]
            quotes[name]["chunk"][str(year)] = [
                {"text": r["text"], "heading": r["heading"],
                 "score": round(float(r[f"score_{name}"]), 4)}
                for _, r in top_chunks.iterrows()
            ]
            year_rows.append({
                "axis": name, "level": "chunk", "year": int(year),
                "raw_topk_mean": mean, "k_used": k_used, "n_chunks": len(group),
            })

        year_df = pd.DataFrame(year_rows)
        year_df["zscore"] = zscore(year_df["raw_topk_mean"].to_numpy())
        rows.append(year_df)

    cf = carried_forward(mission)
    scores_df = pd.concat(rows, ignore_index=True)
    scores_df["carried_forward_frac"] = scores_df["year"].map(cf)
    return scores_df, quotes


def score_sentence_level(mission: pd.DataFrame, axis_names: list[str]) -> tuple[pd.DataFrame, dict]:
    store = EmbeddingStore()
    records = []
    for _, row in mission.iterrows():
        for i, sent in enumerate(split_sentences(row["text"])):
            sid = hashlib.sha256(f"{row['chunk_id']}|{i}|{sent}".encode()).hexdigest()[:16]
            records.append({
                "sentence_id": sid,
                "chunk_id": row["chunk_id"],
                "year": row["year"],
                "heading": row["heading"],
                "text": sent,
            })
    if not records:
        return pd.DataFrame(), {}

    sent_df = pd.DataFrame(records)
    embs = store.embed(sent_df["text"].tolist())
    sent_df["embedding"] = list(embs)
    sent_df["model"] = EMBEDDING_MODEL

    rows = []
    quotes: dict[str, dict[str, dict]] = {}
    for name in axis_names:
        built = read_json(AXES_DIR / "built" / f"{name}.json")
        axis_vec = np.asarray(built["vector"], dtype=np.float32)
        scores = project(np.stack(sent_df["embedding"].tolist()), axis_vec)
        sent_df[f"score_{name}"] = scores

        year_rows = []
        quotes.setdefault(name, {}).setdefault("sentence", {})
        for year, group in sent_df.groupby("year"):
            mean, k_used, top_idx = topk_mean(group[f"score_{name}"].to_numpy(), TOP_K)
            top = group.iloc[top_idx]
            quotes[name]["sentence"][str(year)] = [
                {"text": r["text"], "heading": r["heading"],
                 "score": round(float(r[f"score_{name}"]), 4)}
                for _, r in top.iterrows()
            ]
            year_rows.append({
                "axis": name, "level": "sentence", "year": int(year),
                "raw_topk_mean": mean, "k_used": k_used, "n_chunks": len(group),
            })

        year_df = pd.DataFrame(year_rows)
        year_df["zscore"] = zscore(year_df["raw_topk_mean"].to_numpy())
        rows.append(year_df)

    return pd.concat(rows, ignore_index=True), quotes


def main(company: str, axis_names: list[str]) -> None:
    cdir = company_dir(company)
    df = pd.read_parquet(cdir / "embeddings.parquet")
    mission = df[df["label"] == "mission_brand"].reset_index(drop=True)
    print(f"{len(mission)} mission chunks across {mission['year'].nunique()} years")

    chunk_scores, chunk_quotes = score_chunk_level(mission, axis_names)
    sent_scores, sent_quotes = score_sentence_level(mission, axis_names)

    scores_df = pd.concat([chunk_scores, sent_scores], ignore_index=True)
    # carried_forward only on chunk level; sentence rows get NaN
    scores_df.loc[scores_df["level"] == "sentence", "carried_forward_frac"] = np.nan

    # merge quotes: {axis: {chunk: {year: [...]}, sentence: {year: [...]}}}
    quotes = {}
    for name in axis_names:
        quotes[name] = {
            "chunk": chunk_quotes.get(name, {}).get("chunk", {}),
            "sentence": sent_quotes.get(name, {}).get("sentence", {}),
        }

    scores_df.to_parquet(cdir / "axis_scores.parquet", index=False)
    write_json(cdir / "evidence_quotes.json", quotes)
    print(f"Wrote axis_scores ({len(chunk_scores)} chunk + {len(sent_scores)} sentence rows)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("axes", nargs="*", default=["altruism", "control"])
    args = parser.parse_args()
    main(args.company, args.axes)
