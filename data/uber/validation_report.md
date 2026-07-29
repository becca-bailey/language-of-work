# Validation report: Uber

## 1. Ground truth (chunk level)
- Altruism peak year: **2016** (no hypothesis configured)
- Altruism-control correlation: 0.091 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2018** (no hypothesis configured)
- Altruism-control correlation: 0.61

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.903** (PASS)
- Mean: 0.942

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.17 (n=94) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.091 | 0.551 | PASS |
| craft | 0.244 | 0.664 | PASS |
| inclusion | 0.043 | 0.621 | PASS |
| meritocracy | -0.315 | 0.27 | PASS |
| performance | -0.395 | -0.103 | PASS |
| techno_optimism | 0.548 | 0.007 | MIX-SHIFT: composition change, read trend cautiously |
| wellbeing | 0.592 | 0.915 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing_locus | 0.67 | 0.587 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

