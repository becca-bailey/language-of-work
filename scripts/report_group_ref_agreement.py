#!/usr/bin/env python
"""Agreement report: group-reference instrument vs blind hand labels.

POST-LEVEL comparison (matches the post-level analysis unit): each post
reduces to {group: worst frame present}. The model's passage segmentation is
arbitrary and not human-reproducible, so we never pair-match passages.

Reports:
- detection: post has-reference agreement (accuracy + Krippendorff alpha),
  incl. the recall check on unflagged posts (hand-found, model-missed).
- group presence: precision/recall/F1 over (post, group) — did both mark
  group g present in this post.
- worst-frame agreement given an agreed group: of the (post, group) cells
  both flagged, do the worst frames match.

Go thresholds (pre-registered in the pilot memo): detection alpha >= 0.8,
group presence F1 (alpha >= 0.8 equiv), worst-frame agreement >= 0.7,
recall misses <= 1/20. Below threshold: revise the prompt and draw a FRESH
sample — never tune on the sample you report.

Usage:
  uv run scripts/report_group_ref_agreement.py --case dhh_blog
"""

from __future__ import annotations

import argparse
from collections import Counter

import pandas as pd

from lowork.classify import agreement_report
from lowork.config import company_dir
from lowork.group_refs import FRAMES, GROUPS
from lowork.io import read_json, write_json

# Same hostility ordering as the exporter's per-group worst-frame collapse.
FRAME_SEVERITY = {
    "threat_crime_framing": 4,
    "hostile_derogatory": 3,
    "policy_critique": 2,
    "neutral_mention": 1,
    "sympathetic_defense": 0,
}


def parse_pairs(cell: str) -> list[tuple[str, str]]:
    """Parse the `pairs` cell into (group, frame) tuples, tolerating both `;`
    and `,` separators (labelers use either)."""
    pairs = []
    for part in str(cell or "").replace(";", ",").split(","):
        part = part.strip()
        if not part or ":" not in part:
            continue
        group, frame = (t.strip() for t in part.split(":", 1))
        pairs.append((group, frame))
    return pairs


def worst_by_group(pairs: list[tuple[str, str]]) -> dict[str, str]:
    """Collapse (group, frame) pairs to {group: worst frame present}."""
    worst: dict[str, str] = {}
    for g, f in pairs:
        if g not in GROUPS or f not in FRAME_SEVERITY:
            continue
        if g not in worst or FRAME_SEVERITY[f] > FRAME_SEVERITY[worst[g]]:
            worst[g] = f
    return worst


def main(case: str) -> None:
    cdir = company_dir(case)
    results = read_json(cdir / "group_references.json")
    predicted = {p["slug"]: p for p in results["posts"]}
    df = pd.read_csv(cdir / "labels" / "group_ref_sample.csv", dtype="string").fillna("")
    df = df[df["has_reference"].str.strip() != ""]
    if df.empty:
        raise SystemExit("no filled-in rows — complete has_reference in the sample CSV first")

    hand_binary, pred_binary = {}, {}
    bad_codes: Counter = Counter()
    group_tp = group_fp = group_fn = 0
    frame_match_on_group = frame_total_on_group = 0
    recall_misses: list[str] = []
    frame_disagreements: list[dict] = []

    for _, row in df.iterrows():
        slug = row["slug"]
        pred_post = predicted.get(slug)
        if pred_post is None:
            continue
        hand_has = row["has_reference"].strip().lower() in ("y", "yes", "1", "true")
        hand_binary[slug] = "yes" if hand_has else "no"
        pred_binary[slug] = "yes" if pred_post["refs"] else "no"
        if hand_has and not pred_post["refs"]:
            recall_misses.append(slug)

        hand_pairs = parse_pairs(row["pairs"])
        for g, f in hand_pairs:
            if g not in GROUPS:
                bad_codes[f"group:{g}"] += 1
            if f not in FRAMES:
                bad_codes[f"frame:{f}"] += 1
        # Post-level: {group: worst frame} for hand and model.
        hand_wg = worst_by_group(hand_pairs)
        pred_wg = worst_by_group([(r["group"], r["frame"]) for r in pred_post["refs"]])

        # group presence over (post, group)
        group_tp += len(hand_wg.keys() & pred_wg.keys())
        group_fp += len(pred_wg.keys() - hand_wg.keys())
        group_fn += len(hand_wg.keys() - pred_wg.keys())
        # worst-frame agreement on the groups both flagged
        for g in hand_wg.keys() & pred_wg.keys():
            frame_total_on_group += 1
            if hand_wg[g] == pred_wg[g]:
                frame_match_on_group += 1
            else:
                frame_disagreements.append(
                    {"slug": slug, "group": g, "hand": hand_wg[g], "pred": pred_wg[g]}
                )

    detection = agreement_report(pred_binary, hand_binary)

    def prf(tp_, fp_, fn_):
        p_ = tp_ / (tp_ + fp_) if tp_ + fp_ else None
        r_ = tp_ / (tp_ + fn_) if tp_ + fn_ else None
        f_ = 2 * p_ * r_ / (p_ + r_) if p_ and r_ else None
        rnd = lambda x: round(x, 3) if x is not None else None
        return {"precision": rnd(p_), "recall": rnd(r_), "f1": rnd(f_), "tp": tp_, "fp": fp_, "fn": fn_}

    report = {
        "case": case,
        "unit": "post-level (group -> worst frame)",
        "n_labeled": len(hand_binary),
        "detection": {k: detection[k] for k in ("n", "accuracy", "krippendorff_alpha")},
        "detection_recall_misses": recall_misses,
        "group_presence": prf(group_tp, group_fp, group_fn),
        "worst_frame_agreement_given_group": (
            round(frame_match_on_group / frame_total_on_group, 3) if frame_total_on_group else None
        ),
        "worst_frame_n": frame_total_on_group,
        "frame_disagreements": frame_disagreements,
        "invalid_hand_codes": dict(bad_codes),
        "detection_disagreements": detection["disagreements"],
    }
    path = cdir / "group_ref_agreement.json"
    write_json(path, report)
    print(f"n={report['n_labeled']}  detection acc={report['detection']['accuracy']}"
          f"  alpha={report['detection']['krippendorff_alpha']}")
    print(f"group presence: {report['group_presence']}")
    print(f"worst-frame agreement | agreed group: {report['worst_frame_agreement_given_group']}"
          f" (n={frame_total_on_group})")
    if recall_misses:
        print(f"RECALL MISSES (hand found, model empty): {recall_misses}")
    if frame_disagreements:
        print(f"FRAME DISAGREEMENTS ({len(frame_disagreements)}): "
              + ", ".join(f"{d['group']} hand={d['hand']}/pred={d['pred']}" for d in frame_disagreements[:6]))
    if bad_codes:
        print(f"invalid hand codes (typos?): {dict(bad_codes)}")
    print(f"Wrote {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    args = p.parse_args()
    main(args.case)
