# Validation report: Google

## 1. Ground truth (chunk level)
- Altruism peak year: **2025** (FAIL vs 2014 +/- 2)
- Altruism-control correlation: 0.322 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2014** (PASS vs 2014 +/- 2)
- Altruism-control correlation: 0.699

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.959** (PASS)
- Mean: 0.987

## 4. Data expansion notes

- Link expansion added sub-page captures (teams, belonging, etc.)
- SPA deep-sample found no rendered 2018-2022 HTML (JS shells only)
- JSON API samples are job-listing payloads — parser skipped

Disagreements are case studies, not silent overrides.

