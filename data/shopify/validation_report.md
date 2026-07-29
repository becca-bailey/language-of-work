# Validation report: Shopify

## 1. Ground truth (chunk level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.383 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2026** (no hypothesis configured)
- Altruism-control correlation: 0.468

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.983** (PASS)
- Mean: 0.991

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.122 (n=178) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.383 | 0.681 | PASS |
| craft | 0.672 | 0.51 | POOL-SIZE: top-k inflation, fix estimator |
| inclusion | 0.292 | 0.415 | PASS |
| meritocracy | 0.422 | 0.456 | PASS |
| performance | 0.614 | 0.561 | POOL-SIZE: top-k inflation, fix estimator |
| techno_optimism | 0.322 | 0.427 | PASS |
| wellbeing | 0.247 | 0.05 | PASS |
| wellbeing_locus | 0.711 | 0.857 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

