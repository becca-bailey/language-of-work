# Validation report: GitHub

## 1. Ground truth (chunk level)
- Altruism peak year: **2022** (no hypothesis configured)
- Altruism-control correlation: 0.04 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2022** (no hypothesis configured)
- Altruism-control correlation: 0.087

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.973** (PASS)
- Mean: 0.985

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.759 (n=68) — OVERLAP: INVESTIGATE

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.04 | 0.932 | PASS |
| craft | -0.244 | 0.923 | PASS |
| inclusion | -0.273 | 0.904 | PASS |
| meritocracy | -0.245 | 0.928 | PASS |
| performance | -0.22 | 0.936 | PASS |
| techno_optimism | 0.575 | -0.376 | MIX-SHIFT: composition change, read trend cautiously |
| wellbeing | -0.066 | 0.832 | PASS |
| wellbeing_locus | 0.5 | 0.752 | PASS |

Disagreements are case studies, not silent overrides.

