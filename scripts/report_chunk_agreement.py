#!/usr/bin/env python
"""Pooled chunk-label agreement across every company with hand labels.

One classifier, one prompt — so the headline is Krippendorff's alpha on the
POOLED sample (each data/<company>/labels/sample.csv vs that company's
classifications.json). Per-company numbers are a breakdown, not standalone
estimates: at ~10 labeled chunks per company they are individually meaningless
but pooled they cover every label class across the whole universe.

No API calls: compares stored predictions against stored hand labels.
Writes data/chunk_label_agreement.json.
"""

from __future__ import annotations

import pandas as pd

from lowork.classify import agreement_report
from lowork.config import DATA_DIR
from lowork.io import read_json, write_json


def main() -> None:
    hand_frames = []
    for sample in sorted(DATA_DIR.glob("*/labels/sample.csv")):
        company = sample.parent.parent.name
        df = pd.read_csv(sample, dtype={"label": "string"}).dropna(subset=["label"])
        df = df[df["label"].str.strip() != ""]
        if df.empty:
            print(f"  {company}: sample.csv present but unlabeled — skipped")
            continue
        df["label"] = df["label"].str.strip()
        df["company"] = company
        hand_frames.append(df[["chunk_id", "company", "label"]])
    if not hand_frames:
        raise SystemExit("No labeled sample.csv found — run label_sample.py and hand-label")
    hand = pd.concat(hand_frames, ignore_index=True)
    print(f"{len(hand)} hand-labeled chunks across {hand['company'].nunique()} companies")

    predictions: dict[str, str] = {}
    for company in sorted(hand["company"].unique()):
        preds = read_json(DATA_DIR / company / "classifications.json")
        predictions.update({cid: preds[cid] for cid in hand["chunk_id"] if cid in preds})

    hand_labels = dict(zip(hand["chunk_id"], hand["label"]))
    unmatched = [cid for cid in hand_labels if cid not in predictions]
    if unmatched:
        print(f"  NOTE: {len(unmatched)} hand-labeled chunks have no stored prediction "
              f"(dropped — likely rechunked since labeling)")
    pooled = agreement_report(predictions, hand_labels)

    by_company = {}
    for company, group in hand.groupby("company"):
        sub_hand = dict(zip(group["chunk_id"], group["label"]))
        by_company[company] = agreement_report(predictions, sub_hand)

    out = DATA_DIR / "chunk_label_agreement.json"
    write_json(out, {"pooled": pooled, "by_company": by_company})

    print(f"\nPooled: accuracy {pooled['accuracy']} on n={pooled['n']}, "
          f"Krippendorff alpha {pooled['krippendorff_alpha']}")
    print("\nBy company (breakdown only):")
    for company, r in by_company.items():
        print(f"  {company}: acc={r['accuracy']} n={r['n']} alpha={r['krippendorff_alpha']}")
    if pooled["disagreements"]:
        print(f"\n{len(pooled['disagreements'])} disagreements:")
        for d in pooled["disagreements"]:
            print(f"  {d['chunk_id']}: hand={d['hand_label']} pred={d['predicted']}")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
