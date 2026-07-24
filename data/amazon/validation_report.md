# Validation report: Amazon

## 1. Ground truth (chunk level)
- Altruism peak year: **2017** (no hypothesis configured)
- Altruism-control correlation: 0.41 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2013** (no hypothesis configured)
- Altruism-control correlation: 0.33

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.934** (PASS)
- Mean: 0.97

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.058 (n=189) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.41 | 0.655 | PASS |
| craft | 0.451 | 0.841 | PASS |
| inclusion | 0.371 | 0.915 | PASS |
| meritocracy | 0.582 | 0.942 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.606 | 0.899 | POOL-SIZE: top-k inflation, fix estimator |
| techno_optimism | 0.379 | 0.367 | PASS |
| wellbeing | -0.113 | 0.469 | PASS |
| wellbeing_locus | 0.811 | 0.583 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

