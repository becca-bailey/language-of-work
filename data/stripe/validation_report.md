# Validation report: Stripe

## 1. Ground truth (chunk level)
- Altruism peak year: **2013** (no hypothesis configured)
- Altruism-control correlation: 0.187 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2019** (no hypothesis configured)
- Altruism-control correlation: 0.762

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.832** (PASS)
- Mean: 0.966

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.15 (n=274) — PASS

Disagreements are case studies, not silent overrides.

