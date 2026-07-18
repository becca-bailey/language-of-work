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

## Remaining: stance sample (100 rows)

- [ ] `data/dei_labels/stance_sample.csv` — 0/100 (`stance` column)

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
