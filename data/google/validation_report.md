# Validation report: Google

## 1. Ground truth (chunk level)
- Altruism peak year: **2025** (FAIL vs 2014 +/- 2)
- Altruism-control correlation: 0.52 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2021** (FAIL vs 2014 +/- 2)
- Altruism-control correlation: 0.745

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.988** (PASS)
- Mean: 0.994

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.192 (n=424) — PASS

## 5. Data expansion notes

- Link expansion added sub-page captures (teams, belonging, etc.)
- SPA deep-sample found no rendered 2018-2022 HTML (JS shells only)
- JSON API samples are job-listing payloads — parser skipped

Disagreements are case studies, not silent overrides.

