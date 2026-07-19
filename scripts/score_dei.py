#!/usr/bin/env python
"""Score DEI inclusion intensity and aggregate register/stance counts per year.

Writes data/<company>/dei_scores.parquet and dei_evidence.json.
Uses raw cosine scores (not z-scored) — near-zero is meaningful for absence.

Direction (counter-programming) is measured ONLY by the stance classifier
(lowork.dei_stance); the old inclusion−meritocracy diff and the bipolar
dei_stance embedding axis were retired 2026-07-18 — merit-intensity language
is not a position on DEI (it is measured in the performance study), and a
continuous direction score at a ~1% counter-programming base rate was noise.
"""

from __future__ import annotations

import argparse
from collections import Counter

import numpy as np
import pandas as pd

from lowork.axes import load_built_vector, project, topk_mean
from lowork.chunking import dedup_chunks
from lowork.config import ANALYSIS_LABELS, TOP_K, company_dir
from lowork.dei import ACTIVE_DEI_REGISTERS, DEI_REGISTERS
from lowork.dei_stance import COUNTER_DEI_STANCES, DEI_STANCES
from lowork.io import read_json, write_json
from lowork.text_filter import is_english

PRESENCE_THRESHOLD = 0.25  # inclusion cosine; tune after hand-label review


def _quote_row(row: pd.Series) -> dict:
    return {
        "text": str(row["text"])[:400],
        "heading": row.get("heading", ""),
        "register": row.get("register"),
        "stance": row.get("stance"),
        "inclusion": round(float(row["inclusion"]), 4),
        "score": round(float(row["inclusion"]), 4),
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
    stances_path = cdir / "dei_stances.json"
    stances = read_json(stances_path) if stances_path.exists() else {}

    inc_vec = load_built_vector("inclusion")
    embeddings = np.stack(mission["embedding"].tolist())
    mission["inclusion"] = project(embeddings, inc_vec)
    mission["register"] = mission["chunk_id"].map(registers)
    mission["stance"] = mission["chunk_id"].map(stances)

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
    # evidence["inclusion"]: top-k quote lists per year (explore page).
    # evidence["quotes"]: the two label-aware tooltip quotes per year — the
    # most inclusion-salient chunk in an ACTIVE register, and the most
    # inclusion-salient counter-STANCE chunk (inclusion cosine here is topic
    # proximity, which ranks counter chunks sensibly too).
    evidence: dict[str, dict] = {"inclusion": {}, "quotes": {}}
    prior_texts: set[str] | None = None
    # Per-chunk labels for the story highlight curation: every deduped analysis
    # chunk that carries a DEI signal on either axis (register or stance).
    chunk_labels: dict[str, dict] = {}

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
        inc_mean, inc_k, inc_idx = topk_mean(inc_scores, TOP_K)

        inclusion_quote = None
        active_sub = group[group["register"].isin(ACTIVE_DEI_REGISTERS)]
        if not active_sub.empty:
            inclusion_quote = _quote_row(active_sub.loc[active_sub["inclusion"].idxmax()])

        counter_quote = None
        civ = group[group["stance"] == "civilizational_mission"]
        counter_sub = group[group["stance"].isin(COUNTER_DEI_STANCES)]
        if not civ.empty:
            counter_quote = _quote_row(civ.loc[civ["inclusion"].idxmax()])
        elif not counter_sub.empty:
            counter_quote = _quote_row(counter_sub.loc[counter_sub["inclusion"].idxmax()])

        current_texts = set(group["text"].tolist())
        churn = _text_churn(current_texts, prior_texts)
        prior_texts = current_texts

        for row in group.itertuples():
            reg = getattr(row, "register", None)
            stance = getattr(row, "stance", None)
            if (reg and reg != "absent") or (stance and stance != "neutral"):
                chunk_labels[str(row.chunk_id)] = {
                    "year": year,
                    "text": str(row.text)[:400],
                    "heading": getattr(row, "heading", "") or "",
                    "register": reg,
                    "stance": stance,
                    "salience": round(float(row.inclusion), 4),
                }

        reg_counts = Counter(group["register"].dropna())
        reg_dict = {r: int(reg_counts.get(r, 0)) for r in DEI_REGISTERS}
        stance_counts = Counter(group["stance"].dropna())
        stance_dict = {s: int(stance_counts.get(s, 0)) for s in DEI_STANCES}

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
            "control_raw_topk_mean": control_by_year.get(year),
            **{f"register_{r}": reg_dict[r] for r in DEI_REGISTERS},
            **{f"stance_{s}": stance_dict[s] for s in DEI_STANCES},
        })

        evidence["inclusion"][str(year)] = [
            _quote_row(group.iloc[i]) for i in inc_idx
        ]
        quotes: dict[str, dict] = {}
        if inclusion_quote:
            quotes["inclusionQuote"] = inclusion_quote
        if counter_quote:
            quotes["counterQuote"] = counter_quote
        if quotes:
            evidence["quotes"][str(year)] = quotes

    out_df = pd.DataFrame(rows).sort_values("year")
    out_df.to_parquet(cdir / "dei_scores.parquet", index=False)
    write_json(cdir / "dei_evidence.json", evidence)
    write_json(cdir / "dei_chunk_labels.json", chunk_labels)
    print(f"Wrote {cdir / 'dei_scores.parquet'} ({len(out_df)} years)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
