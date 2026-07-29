# Validation report: Airbnb

## 1. Ground truth (chunk level)
- Altruism peak year: **2019** (no hypothesis configured)
- Altruism-control correlation: -0.626 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: -0.309

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.961** (PASS)
- Mean: 0.993

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=-0.076 (n=88) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | -0.626 | 0.143 | MIX-SHIFT: composition change, read trend cautiously |
| craft | 0.836 | 0.659 | POOL-SIZE: top-k inflation, fix estimator |
| inclusion | -0.313 | 0.497 | PASS |
| meritocracy | 0.134 | 0.802 | PASS |
| performance | 0.413 | 0.906 | PASS |
| techno_optimism | 0.529 | 0.252 | MIX-SHIFT: composition change, read trend cautiously |
| wellbeing | -0.461 | -0.038 | PASS |
| wellbeing_locus | -0.246 | 0.293 | PASS |

Disagreements are case studies, not silent overrides.

