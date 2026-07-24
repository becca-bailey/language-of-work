# Validation report: Netflix

## 1. Ground truth (chunk level)
- Altruism peak year: **2024** (no hypothesis configured)
- Altruism-control correlation: 0.898 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2022** (no hypothesis configured)
- Altruism-control correlation: 0.947

## 2. LLM pairwise tournament
- Duel agreement (PRIMARY): **57%** of 40; confident |Δz|≥1.0: **65% (20 pairs)** — INVESTIGATE; close: 50% (20)
- Spearman is the timeline-shape statistic, secondary (≈5.7 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **0.077**
- Sentence embedding-vs-LLM Spearman: **0.3**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- chunk_vs_llm_spearman: 1.0
- sentence_vs_llm_spearman: 1.0

### performance tournament
- Duel agreement (PRIMARY): **80%** of 40; confident |Δz|≥1.0: **100% (17 pairs)** — PASS; close: 65% (23)
- Spearman is the timeline-shape statistic, secondary (≈5.7 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **0.61**
- Sentence embedding-vs-LLM Spearman: **0.606**
- 40 pairwise judgments

### craft tournament
- Duel agreement (PRIMARY): **50%** of 40; confident |Δz|≥1.0: **38% (21 pairs)** — INVESTIGATE; close: 63% (19)
- Spearman is the timeline-shape statistic, secondary (≈5.7 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **-0.211**
- Sentence embedding-vs-LLM Spearman: **-0.18**
- 40 pairwise judgments

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.956** (PASS)
- Mean: 0.989

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.16 (n=353) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.898 | 0.895 | POOL-SIZE: top-k inflation, fix estimator |
| craft | 0.564 | 0.83 | POOL-SIZE: top-k inflation, fix estimator |
| inclusion | 0.394 | 0.713 | PASS |
| meritocracy | 0.322 | 0.657 | PASS |
| performance | 0.183 | 0.536 | PASS |
| techno_optimism | 0.141 | 0.169 | PASS |
| wellbeing | 0.455 | 0.615 | PASS |
| wellbeing_locus | 0.76 | 0.689 | POOL-SIZE: top-k inflation, fix estimator |

Disagreements are case studies, not silent overrides.

