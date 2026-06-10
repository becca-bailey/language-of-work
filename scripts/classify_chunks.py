#!/usr/bin/env python
"""Step 3b: classify all chunks with pinned Haiku; report agreement vs hand labels.

Workflow: first run with --validate-only to check agreement on the hand-labeled
sample (M3). Iterate the prompt in src/lowork/classify.py until accuracy ~0.90,
then run without the flag to classify the full corpus.

Writes data/<company>/classifications.json and agreement_report.json, and a
mission_review.md digest for the M4 read-through gate.
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.classify import agreement_report, classify_chunks
from lowork.config import company_dir
from lowork.io import load_all_chunks, read_json, write_json
from lowork.relabel import apply_relabel_heuristics


def load_hand_labels(cdir) -> dict[str, str]:
    path = cdir / "labels" / "sample.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype={"label": "string"}).dropna(subset=["label"])
    df = df[df["label"].str.strip() != ""]
    return dict(zip(df["chunk_id"], df["label"].str.strip()))


def write_label_review(
    cdir,
    chunks: list[dict],
    labels: dict[str, str],
    label: str,
    filename: str,
    title: str,
) -> None:
    lines = [f"# {title}", ""]
    by_year: dict[int, list[dict]] = {}
    for c in chunks:
        if labels.get(c["chunk_id"]) == label:
            by_year.setdefault(c["year"], []).append(c)
    for year, year_chunks in sorted(by_year.items()):
        lines.append(f"## {year} ({len(year_chunks)} chunks)")
        lines.append("")
        for c in year_chunks:
            heading = f"**{c['heading']}** — " if c["heading"] else ""
            lines.append(f"- {heading}{c['text']}")
        lines.append("")
    path = cdir / filename
    path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {path} ({sum(len(v) for v in by_year.values())} chunks)")


def write_mission_review(cdir, chunks: list[dict], labels: dict[str, str]) -> None:
    write_label_review(
        cdir, chunks, labels, "mission_brand",
        "mission_review.md", "M4 read-through: mission_brand chunks by year",
    )
    write_label_review(
        cdir, chunks, labels, "employee_story",
        "employee_stories_review.md", "M4 read-through: employee_story chunks by year",
    )


def main(company: str, validate_only: bool) -> None:
    cdir = company_dir(company)
    chunks = load_all_chunks(cdir / "chunks")
    hand_labels = load_hand_labels(cdir)
    print(f"{len(chunks)} chunks, {len(hand_labels)} hand labels")

    if validate_only:
        if not hand_labels:
            raise SystemExit("No hand labels found — fill in labels/sample.csv first (M3)")
        sample_chunks = [c for c in chunks if c["chunk_id"] in hand_labels]
        predictions = classify_chunks(sample_chunks)
    else:
        existing: dict[str, str] = {}
        cls_path = cdir / "classifications.json"
        if cls_path.exists():
            existing = read_json(cls_path)
        chunk_ids = {c["chunk_id"] for c in chunks}
        existing = {k: v for k, v in existing.items() if k in chunk_ids}
        new_chunks = [c for c in chunks if c["chunk_id"] not in existing]
        print(f"Incremental: {len(new_chunks)} new, {len(existing)} already classified")
        if new_chunks:
            predictions = {**existing, **classify_chunks(new_chunks)}
        else:
            predictions = existing
        predictions, relabels = apply_relabel_heuristics(predictions, chunks)
        if relabels:
            print(f"Heuristic relabel: {len(relabels)} chunks")
            for r in relabels[:10]:
                print(f"  {r['chunk_id']}: {r['from']} -> {r['to']} ({r['reason']})")
            if len(relabels) > 10:
                print(f"  ... and {len(relabels) - 10} more")
        write_json(cls_path, predictions)
        write_json(cdir / "relabel_log.json", relabels)
        print(f"Wrote {cls_path} ({len(predictions)} total)")
        write_mission_review(cdir, chunks, predictions)

    if hand_labels:
        report = agreement_report(predictions, hand_labels)
        write_json(cdir / "agreement_report.json", report)
        print(f"\nAgreement: {report['accuracy']} on {report['n']} hand-labeled chunks")
        if report["accuracy"] is not None and report["accuracy"] < 0.9:
            print("Below 0.90 — iterate the prompt in src/lowork/classify.py and re-run")
        for d in report["disagreements"]:
            print(f"  {d['chunk_id']}: hand={d['hand_label']} pred={d['predicted']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("--validate-only", action="store_true",
                        help="classify only the hand-labeled sample and report agreement")
    args = parser.parse_args()
    main(args.company, args.validate_only)
