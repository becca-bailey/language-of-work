# Validation report: GitLab

## 1. Ground truth (chunk level)
- Altruism peak year: **2026** (no hypothesis configured)
- Altruism-control correlation: 0.719 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2022** (no hypothesis configured)
- Altruism-control correlation: 0.165

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.97** (PASS)
- Mean: 0.994

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.086 (n=114) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.719 | 0.873 | POOL-SIZE: top-k inflation, fix estimator |
| craft | 0.334 | 0.882 | PASS |
| inclusion | 0.586 | 0.952 | POOL-SIZE: top-k inflation, fix estimator |
| meritocracy | 0.603 | 0.98 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.528 | 0.901 | POOL-SIZE: top-k inflation, fix estimator |
| techno_optimism | 0.27 | -0.195 | PASS |
| wellbeing | 0.576 | 0.976 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing_locus | 0.302 | 0.496 | PASS |

Disagreements are case studies, not silent overrides.

