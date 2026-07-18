# Labeling TODO — paused 2026-07-15

Status of the hand-labeling workstream at pause. Each CSV's last column is the
label to fill in (blank = not yet labeled).

## Remaining: chunk label samples (160 rows across 13 companies)

- [ ] `data/amazon/labels/sample.csv` — 0/10
- [ ] `data/basecamp/labels/sample.csv` — 0/10
- [ ] `data/coinbase/labels/sample.csv` — 0/10
- [ ] `data/github/labels/sample.csv` — 0/10
- [ ] `data/gitlab/labels/sample.csv` — 0/10
- [ ] `data/google/labels/sample.csv` — 0/30
- [ ] `data/meta/labels/sample.csv` — 0/10
- [ ] `data/netflix/labels/sample.csv` — 0/10
- [ ] `data/palantir/labels/sample.csv` — 0/10
- [ ] `data/salesforce/labels/sample.csv` — 0/10
- [ ] `data/shopify/labels/sample.csv` — 0/10
- [ ] `data/starbucks/labels/sample.csv` — 0/10
- [ ] `data/stripe/labels/sample.csv` — 0/10

## Remaining: stance sample (100 rows)

- [ ] `data/dei_labels/stance_sample.csv` — 0/100 (`stance` column)

## Already complete (for reference)

- `data/airbnb/labels/sample.csv` — 10/10
- `data/apple/labels/sample.csv` — 90/90
- `data/automattic/labels/canon_sample.csv` — 120/120
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
