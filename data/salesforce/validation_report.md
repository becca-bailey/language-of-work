# Validation report: Salesforce

## 1. Ground truth (chunk level)
- Altruism peak year: **2017** (no hypothesis configured)
- Altruism-control correlation: 0.736 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2025** (no hypothesis configured)
- Altruism-control correlation: 0.357

## 2. LLM pairwise tournament
- Duel agreement (PRIMARY): **72%** of 40; confident |Δz|≥1.0: **91% (23 pairs)** — PASS; close: 47% (17)
- Spearman is the timeline-shape statistic, secondary (≈4.7 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **0.57**
- Sentence embedding-vs-LLM Spearman: **0.562**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- chunk_vs_llm_spearman: -0.1
- sentence_vs_llm_spearman: 0.6

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.979** (PASS)
- Mean: 0.993

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.276 (n=402) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.736 | 0.724 | POOL-SIZE: top-k inflation, fix estimator |
| craft | 0.712 | 0.784 | POOL-SIZE: top-k inflation, fix estimator |
| inclusion | 0.821 | 0.716 | POOL-SIZE: top-k inflation, fix estimator |
| meritocracy | 0.859 | 0.745 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.842 | 0.813 | POOL-SIZE: top-k inflation, fix estimator |
| techno_optimism | 0.432 | 0.555 | PASS |
| wellbeing | 0.854 | 0.84 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing_locus | 0.806 | 0.899 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

