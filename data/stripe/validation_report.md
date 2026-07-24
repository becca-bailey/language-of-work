# Validation report: Stripe

## 1. Ground truth (chunk level)
- Altruism peak year: **2019** (no hypothesis configured)
- Altruism-control correlation: 0.58 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2022** (no hypothesis configured)
- Altruism-control correlation: 0.835

## 2. LLM pairwise tournament
- Duel agreement (PRIMARY): **57%** of 40; confident |Δz|≥1.0: **52% (23 pairs)** — INVESTIGATE; close: 65% (17)
- Spearman is the timeline-shape statistic, secondary (≈5.7 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **0.075**
- Sentence embedding-vs-LLM Spearman: **-0.062**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- note: insufficient early-year tournament coverage

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.832** (PASS)
- Mean: 0.966

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.15 (n=274) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.58 | 0.661 | POOL-SIZE: top-k inflation, fix estimator |
| craft | 0.913 | 0.637 | POOL-SIZE: top-k inflation, fix estimator |
| inclusion | 0.753 | 0.784 | POOL-SIZE: top-k inflation, fix estimator |
| meritocracy | 0.934 | 0.765 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.902 | 0.671 | POOL-SIZE: top-k inflation, fix estimator |
| techno_optimism | 0.919 | 0.858 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing | 0.627 | 0.884 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing_locus | 0.938 | 0.96 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

