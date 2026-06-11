#!/usr/bin/env python
"""Classify mission/brand chunks by DEI register (Project 2).

Workflow: run label_dei_sample.py, hand-label data/dei_labels/sample.csv (M3),
then --validate-only before the full run.

Manual corrections from the M4 read-through go in
data/<company>/dei_register_overrides.json ({chunk_id: {register, reason}});
they are re-applied on every run so they survive full re-classification.

Writes data/<company>/dei_registers.json and dei_register_review.md.
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.config import company_dir
from lowork.dei import DEI_REGISTERS, agreement_report, classify_registers, heuristic_register
from lowork.io import load_all_chunks, read_json, write_json

ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}


def load_hand_labels() -> dict[str, str]:
    from lowork.config import DATA_DIR

    path = DATA_DIR / "dei_labels" / "sample.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype={"register": "string"}).dropna(subset=["register"])
    df = df[df["register"].str.strip() != ""]
    return dict(zip(df["chunk_id"], df["register"].str.strip()))


def apply_overrides(cdir, predictions: dict[str, str]) -> dict[str, str]:
    path = cdir / "dei_register_overrides.json"
    if not path.exists():
        return predictions
    out = dict(predictions)
    for cid, override in read_json(path).items():
        reg = override["register"]
        if reg not in DEI_REGISTERS:
            raise SystemExit(f"Invalid register '{reg}' in override for {cid}")
        if cid in out and out[cid] != reg:
            print(f"  override {cid}: {out[cid]} -> {reg} ({override.get('reason', '')})")
        out[cid] = reg
    return out


def write_register_review(cdir, chunks: list[dict], registers: dict[str, str]) -> None:
    lines = ["# DEI register review by year", ""]
    by_reg: dict[str, list[dict]] = {}
    for c in chunks:
        reg = registers.get(c["chunk_id"])
        if reg:
            by_reg.setdefault(reg, []).append(c)
    for reg in DEI_REGISTERS:
        items = by_reg.get(reg, [])
        if not items:
            continue
        lines.append(f"## {reg} ({len(items)} chunks)")
        lines.append("")
        for c in sorted(items, key=lambda x: (x["year"], x["chunk_id"])):
            heading = f"**{c['heading']}** — " if c.get("heading") else ""
            src = c.get("source_url", "")
            lines.append(f"- [{c['year']}] {heading}{c['text'][:300]}...")
            if src:
                lines.append(f"  - source: {src}")
        lines.append("")
    path = cdir / "dei_register_review.md"
    path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {path}")


def main(company: str, validate_only: bool, heuristic: bool, reclassify_all: bool) -> None:
    cdir = company_dir(company)
    chunks = load_all_chunks(cdir / "chunks")
    classifications = read_json(cdir / "classifications.json")
    analysis = [
        c for c in chunks if classifications.get(c["chunk_id"]) in ANALYSIS_LABELS
    ]
    hand_labels = load_hand_labels()
    print(f"{len(analysis)} analysis chunks, {len(hand_labels)} hand labels")

    if validate_only:
        if not hand_labels:
            raise SystemExit("No hand labels — fill in data/dei_labels/sample.csv first")
        sample = [c for c in analysis if c["chunk_id"] in hand_labels]
        if heuristic:
            predictions = {c["chunk_id"]: heuristic_register(c["text"]) for c in sample}
        else:
            predictions = classify_registers(sample)
    else:
        reg_path = cdir / "dei_registers.json"
        if reclassify_all:
            print(f"Reclassifying all {len(analysis)} analysis chunks")
            if heuristic:
                predictions = {c["chunk_id"]: heuristic_register(c["text"]) for c in analysis}
            else:
                predictions = classify_registers(analysis)
        else:
            existing: dict[str, str] = {}
            if reg_path.exists():
                existing = read_json(reg_path)
            new_chunks = [c for c in analysis if c["chunk_id"] not in existing]
            print(f"Incremental: {len(new_chunks)} new, {len(existing)} already classified")
            if new_chunks:
                if heuristic:
                    new_preds = {c["chunk_id"]: heuristic_register(c["text"]) for c in new_chunks}
                else:
                    new_preds = classify_registers(new_chunks)
                predictions = {**existing, **new_preds}
            else:
                predictions = existing
        predictions = apply_overrides(cdir, predictions)
        write_json(reg_path, predictions)
        print(f"Wrote {reg_path} ({len(predictions)} total)")
        write_register_review(cdir, analysis, predictions)

    if hand_labels:
        report = agreement_report(predictions, hand_labels)
        write_json(cdir / "dei_register_agreement.json", report)
        print(f"\nAgreement: {report['accuracy']} on {report['n']} hand-labeled chunks")
        for d in report.get("disagreements", [])[:10]:
            print(f"  {d['chunk_id']}: hand={d['hand_label']} pred={d['predicted']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--heuristic",
        action="store_true",
        help="Keyword fallback (offline bootstrap; use API for production)",
    )
    parser.add_argument(
        "--reclassify-all",
        action="store_true",
        help="Ignore existing dei_registers.json and classify every analysis chunk",
    )
    args = parser.parse_args()
    main(args.company, args.validate_only, args.heuristic, args.reclassify_all)
