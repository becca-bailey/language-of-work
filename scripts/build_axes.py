#!/usr/bin/env python
"""Build axis vectors from curated YAML + run the circularity check.

Axis vector = mean(pole A embeddings) - mean(pole B embeddings), normalized.
Writes axes/built/<name>.json (sentences + vector + model version — versioned,
reproducible). Circularity flags (axis sentences too close to corpus chunks)
go to axes/built/circularity_flags.json for human adjudication (M5).

By default the circularity check sweeps EVERY company in pipeline.yaml — a
pole sentence lifted from any measured firm's copy is a leak (the dei_stance
Palantir leak survived a google-only check). Pass --company to restrict.
"""

from __future__ import annotations

import argparse

import pandas as pd
import yaml

from lowork.axes import AxisDef, build_axis, circularity_check
from lowork.config import AXES_DIR, EMBEDDING_MODEL, ROOT, company_dir
from lowork.embeddings import EmbeddingStore
from lowork.io import load_all_chunks, write_json


def _corpus_texts(company: str) -> list[str]:
    """Circularity corpus for one company: the chunks the axes will actually
    score, so leakage of those chunks' wording into a pole is what we want to
    catch. Prefer the classified mission_brand subset; fall back to firm/canon
    chunks (register=="firm"). circularity_check embeds these cache-first."""
    emb_path = company_dir(company) / "embeddings.parquet"
    if emb_path.exists():
        df = pd.read_parquet(emb_path)
        if "label" in df.columns and (df["label"] == "mission_brand").any():
            return df[df["label"] == "mission_brand"]["text"].tolist()
        if "register" in df.columns:
            return df[df["register"] == "firm"]["text"].tolist()
        return []
    chunks_dir = company_dir(company) / "chunks"
    if chunks_dir.exists():
        chunks = load_all_chunks(chunks_dir)
        return [c["text"] for c in chunks if c.get("register") == "firm"]
    return []


def _universe() -> list[str]:
    return yaml.safe_load((ROOT / "pipeline.yaml").read_text())["companies"]


def main(axis_names: list[str], companies: list[str]) -> None:
    store = EmbeddingStore()
    built_dir = AXES_DIR / "built"
    built_dir.mkdir(exist_ok=True)

    corpora = {co: _corpus_texts(co) for co in companies}
    corpora = {co: texts for co, texts in corpora.items() if texts}
    for co, texts in corpora.items():
        print(f"Circularity corpus: {len(texts)} firm/canon chunks from '{co}'")
    if not corpora:
        print("WARNING: no circularity corpus found — skipping circularity check")

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

        for co, texts in corpora.items():
            flags = circularity_check(store, axis, texts)
            for f in flags:
                f["company"] = co
                print(f"  CIRCULARITY FLAG [{co}/{f['pole']}]: \"{f['sentence']}\" "
                      f"(cosine {f['max_cosine']}, verbatim={f['verbatim_ngram_overlap']})")
            all_flags.extend(flags)

    if corpora:
        write_json(built_dir / "circularity_flags.json", all_flags)
        print(f"\n{len(all_flags)} circularity flags -> {built_dir / 'circularity_flags.json'}")
        if all_flags:
            print("Adjudicate flagged sentences (rephrase or justify) before scoring.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("axes", nargs="*", default=["altruism", "control"])
    parser.add_argument("--company", default=None,
                        help="restrict circularity check to one company "
                             "(default: sweep every company in pipeline.yaml)")
    args = parser.parse_args()
    main(args.axes, [args.company] if args.company else _universe())
