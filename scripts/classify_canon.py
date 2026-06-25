#!/usr/bin/env python
"""Project-3 step: classify chunks canon/on_topic/junk with pinned Haiku.

Workflow mirrors classify_chunks.py: first run with --validate-only to check
agreement against the hand-labeled sample (labels/canon_sample.csv); iterate the
prompt in src/lowork/canon.py until accuracy ~0.90; then run without the flag to
classify the full corpus. Writes data/<case>/classifications.json and
canon_agreement.json, plus a canon_review.md digest of what was tagged canon.
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.canon import agreement_report, classify_canon
from lowork.config import company_dir
from lowork.io import load_all_chunks, write_json


def load_hand_labels(cdir) -> dict[str, str]:
    path = cdir / "labels" / "canon_sample.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype={"label": "string"}).dropna(subset=["label"])
    df = df[df["label"].str.strip() != ""]
    return dict(zip(df["chunk_id"], df["label"].str.strip()))


def write_canon_review(cdir, chunks: list[dict], labels: dict[str, str]) -> None:
    by_year: dict[int, list[dict]] = {}
    for c in chunks:
        if labels.get(c["chunk_id"]) == "canon":
            by_year.setdefault(c["year"], []).append(c)
    lines = ["# Canon chunks (classified)", "",
             f"{sum(len(v) for v in by_year.values())} chunks tagged canon.", ""]
    for year, year_chunks in sorted(by_year.items()):
        lines.append(f"## {year} ({len(year_chunks)} chunks)")
        lines.append("")
        for c in year_chunks:
            url = c.get("provenance", {}).get("canon_url", "")
            head = f"**{c['heading']}** — " if c["heading"] else ""
            lines.append(f"- {head}{c['text'][:200].strip()}  \n  _{url}_")
        lines.append("")
    (cdir / "canon_review.md").write_text("\n".join(lines) + "\n")


def main(case: str, validate_only: bool) -> None:
    cdir = company_dir(case)
    chunks = load_all_chunks(cdir / "chunks")
    hand = load_hand_labels(cdir)

    if validate_only:
        if not hand:
            raise SystemExit("No hand labels — run sample_canon_labels.py and fill in canon_sample.csv")
        labeled = [c for c in chunks if c["chunk_id"] in hand]
        print(f"Validating on {len(labeled)} hand-labeled chunks ...")
        preds = classify_canon(labeled)
        report = agreement_report(preds, hand)
        write_json(cdir / "canon_agreement.json", report)
        print(f"\nAccuracy: {report['accuracy']} on n={report['n']}")
        print("Confusion (truth -> predicted):")
        for truth, row in sorted(report["confusion"].items()):
            print(f"  {truth}: {row}")
        if report["disagreements"]:
            print(f"\n{len(report['disagreements'])} disagreements — inspect before full run.")
        return

    print(f"Classifying {len(chunks)} chunks ...")
    labels = classify_canon(chunks)
    write_json(cdir / "classifications.json", labels)
    counts: dict[str, int] = {}
    for v in labels.values():
        counts[v] = counts.get(v, 0) + 1
    print(f"\nLabel counts: {counts}")
    if hand:  # report agreement on the sample as a sanity check even on the full run
        report = agreement_report(labels, hand)
        print(f"Agreement vs hand sample: {report['accuracy']} (n={report['n']})")
    write_canon_review(cdir, chunks, labels)
    print(f"Wrote {cdir / 'classifications.json'} and canon_review.md")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    p.add_argument("--validate-only", action="store_true")
    args = p.parse_args()
    main(args.case, args.validate_only)
