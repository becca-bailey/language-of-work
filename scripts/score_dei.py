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
from lowork.chunking import dedup_chunks
from lowork.config import AXES_DIR, TOP_K, company_dir
from lowork.dei import COUNTER_DEI_REGISTERS, DEI_REGISTERS
from lowork.io import read_json, write_json
from lowork.text_filter import is_english

PRESENCE_THRESHOLD = 0.25  # inclusion cosine; tune after hand-label review
ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}


def load_pole_vector(name: str) -> np.ndarray:
    built = read_json(AXES_DIR / "built" / f"{name}.json")
    return np.asarray(built["vector"], dtype=np.float32)


def _quote_row(row: pd.Series, score_col: str) -> dict:
    return {
        "text": str(row["text"])[:400],
        "heading": row.get("heading", ""),
        "register": row.get("register"),
        "inclusion": round(float(row["inclusion"]), 4),
        "meritocracy": round(float(row["meritocracy"]), 4),
        "stanceDiff": round(float(row["stance_diff"]), 4),
        "salience": round(float(row["salience"]), 4),
        "score": round(float(row[score_col]), 4),
    }


def _text_churn(current_texts: set[str], prior_texts: set[str] | None) -> float:
    if not prior_texts:
        return 1.0 if current_texts else 0.0
    if not current_texts:
        return 0.0
    new = current_texts - prior_texts
    return len(new) / len(current_texts)


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
    mission["stance_diff"] = mission["inclusion"] - mission["meritocracy"]
    mission["salience"] = mission[["inclusion", "meritocracy"]].max(axis=1)
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
    evidence: dict[str, dict] = {"inclusion": {}, "meritocracy": {}, "envelope": {}}
    prior_texts: set[str] | None = None

    for year, raw_group in mission.groupby("year"):
        year = int(year)
        raw_n = len(raw_group)

        # Language filter
        en_mask = raw_group["text"].apply(is_english)
        group = raw_group[en_mask].copy()
        lang_dropped = raw_n - len(group)

        # Per-year dedup
        chunk_dicts = group.to_dict("records")
        deduped = dedup_chunks(chunk_dicts)
        dedup_dropped = len(chunk_dicts) - len(deduped)
        if dedup_dropped or lang_dropped:
            print(f"  {year}: lang_dropped={lang_dropped} dedup_dropped={dedup_dropped}")

        group = pd.DataFrame(deduped)
        if group.empty:
            continue

        inc_scores = group["inclusion"].to_numpy()
        mer_scores = group["meritocracy"].to_numpy()
        diff_scores = group["stance_diff"].to_numpy()
        sal_scores = group["salience"].to_numpy()

        inc_mean, inc_k, inc_idx = topk_mean(inc_scores, TOP_K)
        mer_mean, mer_k, mer_idx = topk_mean(mer_scores, TOP_K)
        sal_mean, sal_k, _ = topk_mean(sal_scores, TOP_K)

        counter_mask = group["register"].isin(COUNTER_DEI_REGISTERS)
        max_idx = int(group["stance_diff"].idxmax())
        min_idx = int(group["stance_diff"].idxmin())

        counter_quote = None
        civ = group[group["register"] == "civilizational_mission"]
        if not civ.empty:
            counter_quote = _quote_row(civ.loc[civ["salience"].idxmax()], "stance_diff")
        elif counter_mask.any():
            counter_sub = group[counter_mask]
            counter_quote = _quote_row(
                counter_sub.loc[counter_sub["salience"].idxmax()], "stance_diff"
            )

        current_texts = set(group["text"].tolist())
        churn = _text_churn(current_texts, prior_texts)
        prior_texts = current_texts

        reg_counts = Counter(group["register"].dropna())
        reg_dict = {r: int(reg_counts.get(r, 0)) for r in DEI_REGISTERS}

        rows.append({
            "year": year,
            "n_chunks": len(group),
            "n_chunks_raw": raw_n,
            "n_unique_texts": len(current_texts),
            "text_churn": round(churn, 4),
            "inclusion_mean": float(inc_scores.mean()),
            "inclusion_topk_mean": inc_mean,
            "inclusion_max": float(inc_scores.max()),
            "inclusion_k_used": inc_k,
            "inclusion_fraction_present": float((inc_scores >= PRESENCE_THRESHOLD).mean()),
            "meritocracy_mean": float(mer_scores.mean()),
            "meritocracy_topk_mean": mer_mean,
            "meritocracy_max": float(mer_scores.max()),
            "meritocracy_k_used": mer_k,
            "stance_max": float(group.loc[max_idx, "stance_diff"]),
            "stance_min": float(group.loc[min_idx, "stance_diff"]),
            "stance_mean": float(diff_scores.mean()),
            "salience_topk_mean": sal_mean,
            "salience_k_used": sal_k,
            "control_raw_topk_mean": control_by_year.get(year),
            **{f"register_{r}": reg_dict[r] for r in DEI_REGISTERS},
        })

        evidence["inclusion"][str(year)] = [
            _quote_row(group.iloc[i], "inclusion") for i in inc_idx
        ]
        evidence["meritocracy"][str(year)] = [
            _quote_row(group.iloc[i], "meritocracy") for i in mer_idx
        ]
        evidence["envelope"][str(year)] = {
            "stanceMax": round(float(group.loc[max_idx, "stance_diff"]), 4),
            "stanceMin": round(float(group.loc[min_idx, "stance_diff"]), 4),
            "stanceMean": round(float(diff_scores.mean()), 4),
            "salienceTopkMean": round(sal_mean, 4),
            "textChurn": round(churn, 4),
            "stanceMaxQuote": _quote_row(group.loc[max_idx], "stance_diff"),
            "stanceMinQuote": _quote_row(group.loc[min_idx], "stance_diff"),
            "stanceCounterQuote": counter_quote,
        }

    out_df = pd.DataFrame(rows).sort_values("year")
    out_df.to_parquet(cdir / "dei_scores.parquet", index=False)
    write_json(cdir / "dei_evidence.json", evidence)
    print(f"Wrote {cdir / 'dei_scores.parquet'} ({len(out_df)} years)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
