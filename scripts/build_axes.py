#!/usr/bin/env python
"""Step 4b/6: build axis vectors from curated YAML + run the circularity check.

Axis vector = mean(pole A embeddings) - mean(pole B embeddings), normalized.
Writes axes/built/<name>.json (sentences + vector + model version — versioned,
reproducible). Circularity flags (axis sentences too close to corpus chunks)
go to axes/built/circularity_flags.json for human adjudication (M5).
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.axes import AxisDef, build_axis, circularity_check
from lowork.config import AXES_DIR, EMBEDDING_MODEL, company_dir
from lowork.embeddings import EmbeddingStore
from lowork.io import write_json


def main(axis_names: list[str], company: str) -> None:
    store = EmbeddingStore()
    built_dir = AXES_DIR / "built"
    built_dir.mkdir(exist_ok=True)

    corpus_texts: list[str] = []
    emb_path = company_dir(company) / "embeddings.parquet"
    if emb_path.exists():
        df = pd.read_parquet(emb_path)
        corpus_texts = df[df["label"] == "mission_brand"]["text"].tolist()
    else:
        print("WARNING: no embeddings.parquet yet — skipping circularity check")

    all_flags = []
    for name in axis_names:
        axis = AxisDef.from_yaml(AXES_DIR / f"{name}.yaml")
        vec = build_axis(store, axis)
        built: dict = {
            "name": axis.name,
            "model": EMBEDDING_MODEL,
            "single_pole": axis.is_single_pole,
            "pole_a": {"label": axis.pole_a_label, "sentences": axis.pole_a},
            "vector": vec.tolist(),
        }
        if axis.pole_b:
            built["pole_b"] = {"label": axis.pole_b_label, "sentences": axis.pole_b}
        write_json(built_dir / f"{name}.json", built)
        if axis.is_single_pole:
            print(f"Built axis '{name}' (single-pole: {axis.pole_a_label})")
        else:
            print(f"Built axis '{name}' ({axis.pole_a_label} <-> {axis.pole_b_label})")

        if corpus_texts:
            flags = circularity_check(store, axis, corpus_texts)
            all_flags.extend(flags)
            for f in flags:
                print(f"  CIRCULARITY FLAG [{f['pole']}]: \"{f['sentence']}\" "
                      f"(cosine {f['max_cosine']}, verbatim={f['verbatim_ngram_overlap']})")

    if corpus_texts:
        write_json(built_dir / "circularity_flags.json", all_flags)
        print(f"\n{len(all_flags)} circularity flags -> {built_dir / 'circularity_flags.json'}")
        if all_flags:
            print("Adjudicate flagged sentences (rephrase or justify) before scoring.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("axes", nargs="*", default=["altruism", "control"])
    parser.add_argument("--company", default="google")
    args = parser.parse_args()
    main(args.axes, args.company)
