# Validation report: Meta

## 1. Ground truth (chunk level)
- Altruism peak year: **2025** (no hypothesis configured)
- Altruism-control correlation: 0.345 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2016** (no hypothesis configured)
- Altruism-control correlation: 0.427

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.976** (PASS)
- Mean: 0.988

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=-0.043 (n=143) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.345 | 0.651 | PASS |
| craft | 0.127 | 0.483 | PASS |
| inclusion | 0.392 | 0.351 | PASS |
| meritocracy | 0.214 | 0.127 | PASS |
| performance | 0.005 | -0.151 | PASS |
| techno_optimism | -0.285 | 0.156 | PASS |
| wellbeing | 0.381 | 0.634 | PASS |
| wellbeing_locus | 0.272 | 0.634 | PASS |

Disagreements are case studies, not silent overrides.

