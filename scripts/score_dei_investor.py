#!/usr/bin/env python
"""Score DEI inclusion intensity on investor filing chunks per year."""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from lowork.axes import project, topk_mean
from lowork.config import AXES_DIR, TOP_K, company_dir
from lowork.io import read_json, write_json

PRESENCE_THRESHOLD = 0.25


def load_pole_vector(name: str) -> np.ndarray:
    built = read_json(AXES_DIR / "built" / f"{name}.json")
    return np.asarray(built["vector"], dtype=np.float32)


def main(company: str) -> None:
    cdir = company_dir(company)
    inv_path = cdir / "investor_embeddings.parquet"
    if not inv_path.exists():
        raise SystemExit(f"No investor embeddings for {company}")

    inv = pd.read_parquet(inv_path)
    inc_vec = load_pole_vector("inclusion")
    mer_vec = load_pole_vector("meritocracy")
    embeddings = np.stack(inv["embedding"].tolist())
    inv = inv.copy()
    inv["inclusion"] = project(embeddings, inc_vec)
    inv["meritocracy"] = project(embeddings, mer_vec)

    rows = []
    evidence: dict[str, list] = {}
    for year, group in inv.groupby("year"):
        year = int(year)
        scores = group["inclusion"].to_numpy()
        mer_scores = group["meritocracy"].to_numpy()
        mean, k_used, top_idx = topk_mean(scores, TOP_K)
        mer_mean, _, _ = topk_mean(mer_scores, TOP_K)
        rows.append({
            "year": year,
            "source": "investor",
            "n_chunks": len(group),
            "inclusion_mean": float(scores.mean()),
            "inclusion_topk_mean": mean,
            "inclusion_max": float(scores.max()),
            "inclusion_k_used": k_used,
            "inclusion_fraction_present": float((scores >= PRESENCE_THRESHOLD).mean()),
            "meritocracy_topk_mean": mer_mean,
            "meritocracy_mean": float(mer_scores.mean()),
            "thin": len(group) < TOP_K,
        })
        evidence[str(year)] = [
            {
                "text": group.iloc[i]["text"][:400],
                "heading": group.iloc[i].get("heading", ""),
                "score": round(float(group.iloc[i]["inclusion"]), 4),
            }
            for i in top_idx
        ]

    out = cdir / "dei_investor_scores.parquet"
    pd.DataFrame(rows).to_parquet(out, index=False)
    write_json(cdir / "dei_investor_evidence.json", evidence)
    print(f"Wrote {out} ({len(rows)} years)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
