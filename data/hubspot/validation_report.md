# Validation report: HubSpot

## 1. Ground truth (chunk level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.713 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.725

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.955** (PASS)
- Mean: 0.982

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.048 (n=148) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.713 | 0.812 | POOL-SIZE: top-k inflation, fix estimator |
| craft | 0.758 | 0.955 | POOL-SIZE: top-k inflation, fix estimator |
| inclusion | 0.773 | 0.73 | POOL-SIZE: top-k inflation, fix estimator |
| meritocracy | 0.716 | 0.537 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.599 | 0.432 | MIX-SHIFT: composition change, read trend cautiously |
| techno_optimism | 0.21 | 0.451 | PASS |
| wellbeing | 0.496 | 0.813 | PASS |
| wellbeing_locus | 0.606 | 0.787 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

