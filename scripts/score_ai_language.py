#!/usr/bin/env python
"""Score AI-mentioning chunks on the ai_tool_mandate axis (tool <-> mandate).

Chunks are gated by the tuned mention net (lowork.ai_net) across ALL content
labels — the talk-vs-hire contrast needs job_listing chunks, which embed_chunks
never embeds, so gated chunks are embedded here cache-first (the gated set is
tiny: ~0 chunks pre-2022, low double digits per company after).

Positive projection = ai_as_tool pole, negative = ai_as_mandate pole. Years are
aggregated as plain means with n (top-k would be theater at these counts) and
thin-flagged below THIN_N. The axis has ~4 years of real signal by
construction; the caveat travels with the data.

Outputs: data/<company>/ai_language_scores.parquet + ai_evidence.json.
"""

from __future__ import annotations

import argparse
from collections import defaultdict

import numpy as np
import pandas as pd

from lowork.ai_net import find_ai_terms
from lowork.axes import load_built_vector, project
from lowork.config import CONTENT_LABELS, company_dir
from lowork.embeddings import EmbeddingStore
from lowork.io import load_all_chunks, read_json, write_json

# talk = company-voice copy about itself; hire = role/team-attached copy.
REGISTER_GROUPS = {
    "mission_brand": "talk", "employee_story": "talk",
    "job_listing": "hire",
    "benefits_perks": "other", "process_logistics": "other",
}
THIN_N = 5
MAX_EVIDENCE_PER_YEAR = 8


def main(company: str) -> None:
    cdir = company_dir(company)
    chunks = load_all_chunks(cdir / "chunks")
    classifications = read_json(cdir / "classifications.json")
    axis_vec = load_built_vector("ai_tool_mandate")

    seen: set[tuple[int, str]] = set()
    gated: list[dict] = []
    for chunk in chunks:
        label = classifications.get(chunk["chunk_id"])
        if label not in CONTENT_LABELS:
            continue
        key = (int(chunk["year"]), chunk["chunk_id"])
        if key in seen:
            continue
        seen.add(key)
        terms = find_ai_terms(chunk["text"])
        if terms:
            gated.append({**chunk, "label": label, "terms": sorted(set(terms))})

    if not gated:
        write_json(cdir / "ai_evidence.json", {"company": company, "years": {}})
        pd.DataFrame(columns=[
            "year", "group", "mean_projection", "n_chunks", "thin",
        ]).to_parquet(cdir / "ai_language_scores.parquet", index=False)
        print(f"{company}: no AI-mentioning content chunks; wrote empty outputs")
        return

    store = EmbeddingStore()
    embeddings = store.embed([c["text"] for c in gated])
    scores = project(embeddings, axis_vec)

    by_year_group: dict[tuple[int, str], list[float]] = defaultdict(list)
    evidence: dict[str, list[dict]] = defaultdict(list)
    for chunk, score in zip(gated, scores):
        year = int(chunk["year"])
        group = REGISTER_GROUPS[chunk["label"]]
        for g in (group, "all"):
            by_year_group[(year, g)].append(float(score))
        evidence[str(year)].append({
            "chunk_id": chunk["chunk_id"],
            "label": chunk["label"],
            "group": group,
            "terms": chunk["terms"],
            "projection": round(float(score), 4),
            "text": chunk["text"][:400],
        })

    rows = []
    for (year, group), vals in sorted(by_year_group.items()):
        rows.append({
            "year": year,
            "group": group,
            "mean_projection": float(np.mean(vals)),
            "n_chunks": len(vals),
            "thin": len(vals) < THIN_N,
        })
    pd.DataFrame(rows).to_parquet(cdir / "ai_language_scores.parquet", index=False)

    for year in evidence:
        evidence[year] = sorted(
            evidence[year], key=lambda e: abs(e["projection"]), reverse=True
        )[:MAX_EVIDENCE_PER_YEAR]
    write_json(cdir / "ai_evidence.json", {"company": company, "years": dict(sorted(evidence.items()))})

    pooled = [s for (y, g), v in by_year_group.items() if g == "all" for s in v]
    print(
        f"{company}: {len(gated)} gated chunks, "
        f"pooled mean projection {np.mean(pooled):+.4f} "
        f"(+ = tool, - = mandate)"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", required=True)
    main(parser.parse_args().company)
