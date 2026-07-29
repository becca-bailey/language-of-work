# Validation report: Apple

## 1. Ground truth (chunk level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.689 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.725

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.977** (PASS)
- Mean: 0.993

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.23 (n=410) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.689 | 0.835 | POOL-SIZE: top-k inflation, fix estimator |
| craft | 0.563 | 0.768 | POOL-SIZE: top-k inflation, fix estimator |
| inclusion | 0.808 | 0.778 | POOL-SIZE: top-k inflation, fix estimator |
| meritocracy | 0.789 | 0.9 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.512 | 0.838 | POOL-SIZE: top-k inflation, fix estimator |
| techno_optimism | 0.36 | 0.741 | PASS |
| wellbeing | 0.701 | 0.684 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing_locus | 0.714 | 0.913 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

