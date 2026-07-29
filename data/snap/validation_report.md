# Validation report: Snap

## 1. Ground truth (chunk level)
- Altruism peak year: **2019** (no hypothesis configured)
- Altruism-control correlation: -0.621 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2026** (no hypothesis configured)
- Altruism-control correlation: 0.561

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.967** (PASS)
- Mean: 0.988

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.389 (n=64) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | -0.621 | -0.172 | MIX-SHIFT: composition change, read trend cautiously |
| craft | 0.356 | 0.874 | PASS |
| inclusion | -0.012 | 0.727 | PASS |
| meritocracy | -0.004 | 0.674 | PASS |
| performance | -0.094 | 0.495 | PASS |
| techno_optimism | 0.172 | 0.003 | PASS |
| wellbeing | 0.658 | 0.701 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing_locus | 0.171 | 0.092 | PASS |

Disagreements are case studies, not silent overrides.

