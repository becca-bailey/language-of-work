#!/usr/bin/env python
"""Pooled hand-label agreement for the DEI classifiers (register or stance).

The unit under validation is the classifier+prompt, not each company, so the
headline number is Krippendorff's alpha on the POOLED hand-labeled sample
vs each company's stored predictions. Per-company numbers are kept as a
breakdown only — most companies contribute too few labeled chunks for a
standalone estimate.

If the sample was built with the stratified samplers (label_dei_sample.py
--stratify-registers / label_stance_sample.py), report agreement as a
per-class measure, not corpus-wide agreement.

No API calls: compares stored predictions against stored hand labels.

  report_dei_agreement.py --task register   # sample.csv vs dei_registers.json
  report_dei_agreement.py --task stance     # stance_sample.csv vs dei_stances.json
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.classify import agreement_report
from lowork.config import DATA_DIR
from lowork.io import load_hand_labels as _hand_label_rows, read_json, write_json

TASKS = {
    "register": {
        "sample": "sample.csv",
        "column": "register",
        "predictions": "dei_registers.json",
        "out": "agreement.json",
    },
    "stance": {
        "sample": "stance_sample.csv",
        "column": "stance",
        "predictions": "dei_stances.json",
        "out": "stance_agreement.json",
    },
}


def load_hand_labels(sample: str, column: str) -> pd.DataFrame:
    df = _hand_label_rows(DATA_DIR / "dei_labels" / sample, column, missing_ok=False)
    if df.empty:
        raise SystemExit(
            f"No hand labels in {DATA_DIR / 'dei_labels' / sample} yet — "
            f"fill in the `{column}` column"
        )
    return df


def main(task: str) -> None:
    cfg = TASKS[task]
    hand = load_hand_labels(cfg["sample"], cfg["column"])
    print(f"{len(hand)} hand-labeled chunks across {hand['company'].nunique()} companies")

    predictions: dict[str, str] = {}
    for company in sorted(hand["company"].unique()):
        path = DATA_DIR / company / cfg["predictions"]
        if not path.exists():
            print(f"  WARNING: {path} missing — {company} chunks excluded from pool")
            continue
        preds = read_json(path)
        predictions.update({cid: preds[cid] for cid in hand["chunk_id"] if cid in preds})

    hand_labels = dict(zip(hand["chunk_id"], hand[cfg["column"]]))
    unmatched = len(hand_labels) - sum(1 for cid in hand_labels if cid in predictions)
    if unmatched:
        print(f"  NOTE: {unmatched} hand-labeled chunks have no stored prediction (dropped)")
    pooled = agreement_report(predictions, hand_labels)

    by_company = {}
    for company, group in hand.groupby("company"):
        sub_hand = dict(zip(group["chunk_id"], group[cfg["column"]]))
        by_company[company] = agreement_report(predictions, sub_hand)

    out = DATA_DIR / "dei_labels" / cfg["out"]
    write_json(out, {"pooled": pooled, "by_company": by_company})

    print(f"\nPooled: accuracy {pooled['accuracy']} on n={pooled['n']}, "
          f"Krippendorff alpha {pooled['krippendorff_alpha']}")
    print("Hand-label distribution:")
    for label, count in hand[cfg["column"]].value_counts().items():
        print(f"  {label}: {count}")
    print("\nBy company (breakdown only, not standalone estimates):")
    for company, r in by_company.items():
        print(f"  {company}: acc={r['accuracy']} n={r['n']} alpha={r['krippendorff_alpha']}")
    if pooled["disagreements"]:
        print(f"\n{len(pooled['disagreements'])} disagreements:")
        for d in pooled["disagreements"]:
            print(f"  {d['chunk_id']}: hand={d['hand_label']} pred={d['predicted']}")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=list(TASKS), default="register")
    args = parser.parse_args()
    main(args.task)
