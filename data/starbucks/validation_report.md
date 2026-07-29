# Validation report: Starbucks

## 1. Ground truth (chunk level)
- Altruism peak year: **2023** (no hypothesis configured)
- Altruism-control correlation: 0.612 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2017** (no hypothesis configured)
- Altruism-control correlation: -0.068

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.979** (PASS)
- Mean: 0.991

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.313 (n=450) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.612 | 0.877 | POOL-SIZE: top-k inflation, fix estimator |
| craft | 0.419 | 0.728 | PASS |
| inclusion | 0.546 | 0.893 | POOL-SIZE: top-k inflation, fix estimator |
| meritocracy | 0.513 | 0.909 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.483 | 0.895 | PASS |
| techno_optimism | 0.604 | 0.787 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing | 0.638 | 0.752 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing_locus | 0.857 | 0.855 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

