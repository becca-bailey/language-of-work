# Labeling TODO — updated 2026-07-18 (paused 2026-07-15)

Status of the hand-labeling workstream. Each CSV's last column is the
label to fill in (blank = not yet labeled).

## Remaining: chunk label samples (10 of 150 rows left across 1 company)

- [x] `data/palantir/labels/sample.csv` — 10/10
- [x] `data/amazon/labels/sample.csv` — 10/10
- [x] `data/basecamp/labels/sample.csv` — 10/10
- [x] `data/coinbase/labels/sample.csv` — 10/10
- [x] `data/github/labels/sample.csv` — 10/10
- [x] `data/gitlab/labels/sample.csv` — 10/10
- [x] `data/google/labels/sample.csv` — 30/30
- [x] `data/meta/labels/sample.csv` — 10/10
- [x] `data/netflix/labels/sample.csv` — 10/10
- [x] `data/salesforce/labels/sample.csv` — 10/10
- [x] `data/shopify/labels/sample.csv` — 10/10
- [x] `data/starbucks/labels/sample.csv` — 10/10
- [x] `data/stripe/labels/sample.csv` — 10/10

## Remaining: stance sample (verification pass)

- [ ] `data/dei_labels/stance_sample.csv` — 100/100 filled, but only rows 1–63
  are Becca's own labels (2026-07-18; `apolotical` typo fixed in place, 14 rows).
  Rows 64–100 are an **AI first-pass** (Claude, following Becca's demonstrated
  conventions) awaiting her verification — verify each rather than skim;
  pre-filled labels anchor the reader, so agreement computed from a
  rubber-stamped sheet would be inflated.
- Preview vs stored classifier predictions (partially-verified sheet, NOT the
  official number): 60/100 agree, α ≈ 0.47. The misses are definitional, not
  noise: all 20 classifier `performance_elite` rows hand-labeled neutral-ish
  (matches Becca's ruling that intensity ≠ DEI stance), and 17 of ~20
  classifier `civilizational_mission` rows hand-labeled neutral (Becca's
  convention: explicit West/geopolitical framing only, not generic
  "world's most important institutions" copy).
- Both codebook decisions DECIDED and applied 2026-07-18:
  1. `performance_elite` REMOVED from the stance taxonomy (Becca's ruling:
     intensity ≠ DEI stance). Prompt now routes pure performance language to
     neutral; stored predictions remapped (258 chunks → neutral).
  2. `civilizational_mission` NARROWED to explicit West/Western-civilization
     invocations (generic institutions/deterrence copy → neutral). Stored
     predictions re-judged: 3 kept (2025–26 "future of the West" family),
     28 demoted — every demotion matches Becca's hand label where sampled.
  Open naming question: Becca proposed renaming the class `white_supremacy`;
  recommendation pending discussion (see conversation 2026-07-18).
- After the verification pass, run
  `python scripts/report_dei_agreement.py --task stance` for the official α.
  Expect the two old definitional-gap patterns to be gone; residual
  disagreements should be genuine classifier error.

## Already complete (for reference)

- `data/airbnb/labels/sample.csv` — 10/10
- `data/apple/labels/sample.csv` — 90/90
- `data/brex/labels/sample.csv` — 10/10
- `data/hubspot/labels/sample.csv` — 10/10
- `data/nvidia/labels/sample.csv` — 90/90
- `data/snap/labels/sample.csv` — 10/10
- `data/uber/labels/sample.csv` — 90/90
- `data/dei_labels/sample.csv` — 203/203 (`register` column)

## When resuming

- After chunk labels are filled: `python scripts/report_chunk_agreement.py`
  (writes `data/chunk_label_agreement.json`).
- After stance labels are filled: `python scripts/report_dei_agreement.py --task stance`
  (writes `data/dei_labels/agreement.json`).
- Full-corpus re-classify with the rewritten register prompt is still gated on
  the validation numbers above.
