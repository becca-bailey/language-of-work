# Validation report: Basecamp

## 1. Ground truth (chunk level)
- Altruism peak year: **2023** (no hypothesis configured)
- Altruism-control correlation: 0.329 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.453

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.975** (PASS)
- Mean: 0.99

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.657 (n=374) — OVERLAP: INVESTIGATE

Disagreements are case studies, not silent overrides.

