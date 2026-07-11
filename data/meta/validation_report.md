# Validation report: Meta

## 1. Ground truth (chunk level)
- Altruism peak year: **2025** (no hypothesis configured)
- Altruism-control correlation: 0.033 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2016** (no hypothesis configured)
- Altruism-control correlation: 0.465

## 2. LLM pairwise tournament
- Skipped (--skip-tournament)

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.976** (PASS)
- Mean: 0.988

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=-0.043 (n=143) — PASS

Disagreements are case studies, not silent overrides.

