#!/usr/bin/env python
"""Split idealistic language into world-changing vs techno-optimism.

The altruism axis (idealism <-> commercial pragmatism) conflates two kinds of
lofty copy: genuine "we'll change the world" mission, and "we build amazing
technology" product hype. This re-scores each company's mission sentences on BOTH
the altruism and techno_optimism axes, partitions per year, and emits two series:

  - worldChanging : top-k mean altruism projection over NON-techno sentences
  - technoOptimism: top-k mean techno projection over techno sentences (techno > 0)

Each z-scored within company. Writes data/<company>/altruism_split.parquet +
altruism_split_quotes.json so the inflated idealism (e.g. Meta's recent AI-product
copy) drops out of the altruism line and reappears as its own category.
"""

from __future__ import annotations

import argparse
import hashlib

import numpy as np
import pandas as pd

from lowork.axes import project, topk_mean, zscore
from lowork.config import AXES_DIR, EMBEDDING_MODEL, TOP_K, company_dir
from lowork.embeddings import EmbeddingStore
from lowork.io import read_json, write_json
from lowork.sentences import split_sentences

TECHNO_THRESHOLD = 0.0  # techno projection > 0 = product-hype, not world-betterment


def load_vec(name: str) -> np.ndarray:
    return np.asarray(read_json(AXES_DIR / "built" / f"{name}.json")["vector"], dtype=np.float32)


def sentence_frame(company: str) -> pd.DataFrame:
    df = pd.read_parquet(company_dir(company) / "embeddings.parquet")
    mission = df[df["label"] == "mission_brand"]
    store = EmbeddingStore()
    rows = []
    for _, r in mission.iterrows():
        for sent in split_sentences(r["text"]):
            if len(sent.split()) < 5:
                continue
            sid = hashlib.sha256(f"{r['chunk_id']}|{sent}".encode()).hexdigest()[:16]
            rows.append({"sentence_id": sid, "year": int(r["year"]),
                         "heading": r.get("heading", ""), "text": sent})
    sdf = pd.DataFrame(rows).drop_duplicates(subset=["year", "text"]).reset_index(drop=True)
    embs = store.embed(sdf["text"].tolist())
    sdf["alt"] = project(np.stack(embs), load_vec("altruism"))
    sdf["techno"] = project(np.stack(embs), load_vec("techno_optimism"))
    sdf["model"] = EMBEDDING_MODEL
    return sdf


def _series(group: pd.DataFrame, score_col: str) -> tuple[float, int, list[int]]:
    if group.empty:
        return float("nan"), 0, []
    return topk_mean(group[score_col].to_numpy(), TOP_K)


def main(company: str) -> None:
    cdir = company_dir(company)
    sdf = sentence_frame(company)
    sdf["is_techno"] = sdf["techno"] > TECHNO_THRESHOLD

    rows, quotes = [], {"worldChanging": {}, "technoOptimism": {}}
    for year, g in sdf.groupby("year"):
        world = g[~g["is_techno"]]
        techno = g[g["is_techno"]]
        w_mean, w_k, w_idx = _series(world, "alt")
        t_mean, t_k, t_idx = _series(techno, "techno")
        rows.append({
            "year": int(year),
            "world_topk": w_mean, "world_n": len(world),
            "techno_topk": t_mean, "techno_n": len(techno),
            "techno_share": round(len(techno) / len(g), 4) if len(g) else 0.0,
            "n": len(g),
        })
        if len(w_idx):
            top = world.iloc[w_idx]
            quotes["worldChanging"][str(int(year))] = [
                {"text": r["text"], "heading": r["heading"], "score": round(float(r["alt"]), 4)}
                for _, r in top.iterrows()]
        if len(t_idx):
            top = techno.iloc[t_idx]
            quotes["technoOptimism"][str(int(year))] = [
                {"text": r["text"], "heading": r["heading"], "score": round(float(r["techno"]), 4)}
                for _, r in top.iterrows()]

    out = pd.DataFrame(rows).sort_values("year")
    out["world_zscore"] = zscore(out["world_topk"].fillna(out["world_topk"].min()).to_numpy())
    # n==0 is an ABSENCE of world-changing language, not a measured low — leave it
    # NaN so the chart shows a gap rather than imputing a confident low point.
    out.loc[out["world_n"] == 0, "world_zscore"] = float("nan")
    out["techno_zscore"] = zscore(out["techno_topk"].fillna(out["techno_topk"].min()).to_numpy())
    out.to_parquet(cdir / "altruism_split.parquet", index=False)
    write_json(cdir / "altruism_split_quotes.json", quotes)
    print(f"[{company}] wrote altruism_split ({len(out)} years)  "
          f"techno_share mean={out['techno_share'].mean():.2f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--company", default="meta")
    main(p.parse_args().company)
