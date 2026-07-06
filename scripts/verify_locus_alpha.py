#!/usr/bin/env python
"""Phase 1.3 verify: hand labels vs frozen-codebook model labels on the locus sample.

Joins data/wellbeing_locus_review.csv (hand) with wellbeing_locus_review_model.csv
(model, relabeled under the frozen codebook) by id and reports, for locus:
  - raw agreement, Krippendorff's alpha (nominal)
  - confusion matrix + every disagreement (for adjudication)
  - per-category agreement
  - hard-case-subset alpha (the judgment categories)
Gates: full-sample alpha >= 0.8 to scale; hard-case subset >= 0.667.
Also reports specificity agreement as a secondary check.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict

import krippendorff

from lowork.config import DATA_DIR

HARD_CATEGORIES = {"remote_flexibility", "parental_leave", "pto_accrued",
                   "pto_unlimited", "sabbatical", "other"}
LABELS = ["individual", "structural", "ambiguous", "exclude"]


def load_pairs():
    hand = {r["id"]: r for r in csv.DictReader((DATA_DIR / "wellbeing_locus_review.csv").open())}
    model = {r["id"]: r for r in csv.DictReader((DATA_DIR / "wellbeing_locus_review_model.csv").open())}
    rows = []
    for i, h in hand.items():
        m = model.get(i, {})
        rows.append({
            "id": i, "company": h["company"], "category": h["category"],
            "verbatim": h["verbatim"],
            "h_loc": h["hand_locus"].strip(), "m_loc": (m.get("model_locus") or "").strip(),
            "h_spec": h["hand_specificity"].strip(),
            "m_spec": (m.get("model_specificity") or "").strip(),
        })
    return rows


def alpha(pairs, key_h, key_m):
    idx = {lab: i for i, lab in enumerate(LABELS)}
    data = [[], []]
    for p in pairs:
        a, b = p[key_h], p[key_m]
        if a in idx and b in idx:
            data[0].append(idx[a]); data[1].append(idx[b])
    if not data[0]:
        return None, 0
    return krippendorff.alpha(reliability_data=data,
                              level_of_measurement="nominal"), len(data[0])


def agreement(pairs, key_h, key_m):
    common = [p for p in pairs if p[key_h] and p[key_m]]
    agree = sum(1 for p in common if p[key_h] == p[key_m])
    return agree, len(common)


def main() -> int:
    pairs = load_pairs()

    print("=" * 66)
    print("LOCUS — hand vs frozen-codebook model")
    a, n = agreement(pairs, "h_loc", "m_loc")
    al, naln = alpha(pairs, "h_loc", "m_loc")
    print(f"  raw agreement: {a}/{n} = {a/n:.1%}")
    print(f"  Krippendorff alpha (nominal): {al:.3f}   [gate >= 0.80]  "
          f"{'PASS' if al >= 0.8 else 'FAIL'}")

    hard = [p for p in pairs if p["category"] in HARD_CATEGORIES]
    ah, nh = agreement(hard, "h_loc", "m_loc")
    alh, _ = alpha(hard, "h_loc", "m_loc")
    print(f"  hard-case subset ({nh} items): agreement {ah/nh:.1%}, "
          f"alpha {alh:.3f}   [gate >= 0.667]  {'PASS' if alh >= 0.667 else 'FAIL'}")

    print("\n  confusion (hand → model):")
    conf = defaultdict(Counter)
    for p in pairs:
        conf[p["h_loc"]][p["m_loc"]] += 1
    for h in LABELS:
        if conf[h]:
            print(f"    {h:11} -> " + ", ".join(f"{m}:{c}" for m, c in conf[h].most_common()))

    print("\n  per-category agreement:")
    bycat = defaultdict(lambda: [0, 0])
    for p in pairs:
        bycat[p["category"]][1] += 1
        if p["h_loc"] == p["m_loc"]:
            bycat[p["category"]][0] += 1
    for cat, (ok, tot) in sorted(bycat.items(), key=lambda x: x[1][0] / x[1][1]):
        print(f"    {cat:22} {ok}/{tot} = {ok/tot:.0%}")

    print("\n  DISAGREEMENTS (adjudicate):")
    for p in pairs:
        if p["h_loc"] != p["m_loc"]:
            print(f"    #{p['id']:>2} {p['company']:10} {p['category']:18} "
                  f"hand={p['h_loc']:10} model={p['m_loc']:10} | {p['verbatim'][:44]}")

    print("\n" + "=" * 66)
    print("SPECIFICITY — secondary check")
    sa, sn = agreement(pairs, "h_spec", "m_spec")
    print(f"  raw agreement: {sa}/{sn} = {sa/sn:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
