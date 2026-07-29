# Validation report: Brex

## 1. Ground truth (chunk level)
- Altruism peak year: **2024** (no hypothesis configured)
- Altruism-control correlation: 0.206 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.409

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.778** (FRAGILE)
- Mean: 0.932

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.127 (n=52) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.206 | 0.689 | PASS |
| craft | 0.594 | 0.797 | POOL-SIZE: top-k inflation, fix estimator |
| inclusion | 0.317 | 0.672 | PASS |
| meritocracy | 0.669 | 0.94 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.787 | 0.927 | POOL-SIZE: top-k inflation, fix estimator |
| techno_optimism | 0.145 | 0.114 | PASS |
| wellbeing | -0.02 | 0.428 | PASS |
| wellbeing_locus | 0.811 | 0.883 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

