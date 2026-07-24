# Validation report: Basecamp

## 1. Ground truth (chunk level)
- Altruism peak year: **2023** (no hypothesis configured)
- Altruism-control correlation: 0.839 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.744

## 2. LLM pairwise tournament
- Duel agreement (PRIMARY): **48%** of 40; confident |Δz|≥1.0: **32% (22 pairs)** — INVESTIGATE; close: 67% (18)
- Spearman is the timeline-shape statistic, secondary (≈4.7 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **-0.064**
- Sentence embedding-vs-LLM Spearman: **-0.15**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- note: insufficient early-year tournament coverage

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.979** (PASS)
- Mean: 0.994

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.646 (n=385) — OVERLAP: INVESTIGATE

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.839 | 0.917 | POOL-SIZE: top-k inflation, fix estimator |
| craft | 0.722 | 0.558 | POOL-SIZE: top-k inflation, fix estimator |
| inclusion | 0.748 | 0.819 | POOL-SIZE: top-k inflation, fix estimator |
| meritocracy | 0.785 | 0.813 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.704 | 0.763 | POOL-SIZE: top-k inflation, fix estimator |
| techno_optimism | 0.787 | 0.633 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing | 0.966 | 0.921 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing_locus | 0.813 | 0.782 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

