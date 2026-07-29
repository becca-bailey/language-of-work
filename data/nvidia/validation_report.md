# Validation report: NVIDIA

## 1. Ground truth (chunk level)
- Altruism peak year: **2015** (no hypothesis configured)
- Altruism-control correlation: -0.737 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2025** (no hypothesis configured)
- Altruism-control correlation: -0.719

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.969** (PASS)
- Mean: 0.986

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.461 (n=57) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | -0.737 | 0.333 | MIX-SHIFT: composition change, read trend cautiously |
| craft | 0.879 | -0.382 | MIX-SHIFT: composition change, read trend cautiously |
| inclusion | -0.213 | 0.057 | PASS |
| meritocracy | -0.17 | -0.059 | PASS |
| performance | -0.248 | -0.081 | PASS |
| techno_optimism | 0.007 | 0.36 | PASS |
| wellbeing | 0.14 | 0.107 | PASS |
| wellbeing_locus | -0.72 | 0.643 | MIX-SHIFT: composition change, read trend cautiously |

Disagreements are case studies, not silent overrides.

