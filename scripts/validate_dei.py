#!/usr/bin/env python
"""DEI validation: correlations and register-vs-intensity consistency.

Writes data/<company>/dei_validation.md and dei_validation.json.
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from lowork.config import company_dir
from lowork.io import read_json, write_json

ABSENT_MAX_SCORE = 0.20


def main(company: str) -> None:
    cdir = company_dir(company)
    yearly = pd.read_parquet(cdir / "dei_scores.parquet")
    registers = read_json(cdir / "dei_registers.json")
    embeddings = pd.read_parquet(cdir / "embeddings.parquet")

    # Correlations on years with data
    inc = yearly["inclusion_topk_mean"]
    mer = yearly["meritocracy_topk_mean"]
    ctrl = yearly["control_raw_topk_mean"].dropna()
    common_years = yearly.dropna(subset=["control_raw_topk_mean"])

    inc_mer_r, inc_mer_p = spearmanr(inc, mer) if len(inc) >= 3 else (None, None)
    inc_ctrl_r, inc_ctrl_p = (
        spearmanr(common_years["inclusion_topk_mean"], common_years["control_raw_topk_mean"])
        if len(common_years) >= 3
        else (None, None)
    )

    # Absent consistency: chunks labeled absent should score low on inclusion
    from lowork.axes import project
    from lowork.config import AXES_DIR

    built = read_json(AXES_DIR / "built" / "inclusion.json")
    inc_vec = np.asarray(built["vector"], dtype=np.float32)
    mission = embeddings[embeddings["label"].isin({"mission_brand", "benefits_perks"})]
    emb = np.stack(mission["embedding"].tolist())
    scores = project(emb, inc_vec)
    mission = mission.copy()
    mission["inclusion"] = scores
    mission["register"] = mission["chunk_id"].map(registers)

    absent = mission[mission["register"] == "absent"]
    disagreements = []
    for _, row in absent.iterrows():
        if row["inclusion"] > ABSENT_MAX_SCORE:
            disagreements.append({
                "chunk_id": row["chunk_id"],
                "year": int(row["year"]),
                "inclusion": round(float(row["inclusion"]), 3),
                "text": row["text"][:160],
            })

    results = {
        "inclusion_meritocracy_spearman": round(float(inc_mer_r), 3) if inc_mer_r is not None else None,
        "inclusion_meritocracy_p": round(float(inc_mer_p), 3) if inc_mer_p is not None else None,
        "inclusion_control_spearman": round(float(inc_ctrl_r), 3) if inc_ctrl_r is not None else None,
        "inclusion_control_p": round(float(inc_ctrl_p), 3) if inc_ctrl_p is not None else None,
        "absent_disagreements": disagreements[:20],
        "absent_disagreement_count": len(disagreements),
    }

    lines = [
        f"# DEI validation: {company}",
        "",
        "## Correlations (year-level Spearman)",
        f"- Inclusion vs meritocracy: {results['inclusion_meritocracy_spearman']} (p={results['inclusion_meritocracy_p']})",
        f"- Inclusion vs control: {results['inclusion_control_spearman']} (p={results['inclusion_control_p']})",
        "",
        "## Register consistency",
        f"- Chunks labeled `absent` scoring above {ABSENT_MAX_SCORE} on inclusion: "
        f"**{results['absent_disagreement_count']}**",
        "",
    ]
    if disagreements:
        lines.append("### Sample disagreements (review, do not auto-fix)")
        lines.append("")
        for d in disagreements[:10]:
            lines.append(f"- [{d['year']}] score={d['inclusion']}: {d['text']}...")
        lines.append("")

    write_json(cdir / "dei_validation.json", results)
    (cdir / "dei_validation.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {cdir / 'dei_validation.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
