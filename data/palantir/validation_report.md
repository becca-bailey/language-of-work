# Validation report: Palantir

## 1. Ground truth (chunk level)
- Altruism peak year: **2023** (no hypothesis configured)
- Altruism-control correlation: 0.691 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2019** (no hypothesis configured)
- Altruism-control correlation: 0.105

## 2. LLM pairwise tournament
- Duel agreement (PRIMARY): **50%** of 40; confident |Δz|≥1.0: **42% (24 pairs)** — INVESTIGATE; close: 62% (16)
- Spearman is the timeline-shape statistic, secondary (≈6.2 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **-0.091**
- Sentence embedding-vs-LLM Spearman: **0.162**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- chunk_vs_llm_spearman: 0.8
- sentence_vs_llm_spearman: 0.4

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.944** (PASS)
- Mean: 0.988

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.344 (n=207) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.691 | 0.702 | MIX-SHIFT: composition change, read trend cautiously |
| craft | 0.24 | 0.63 | PASS |
| inclusion | 0.31 | 0.375 | PASS |
| meritocracy | 0.379 | 0.534 | PASS |
| performance | 0.23 | 0.419 | PASS |
| techno_optimism | 0.255 | 0.755 | PASS |
| wellbeing | 0.638 | 0.731 | MIX-SHIFT: composition change, read trend cautiously |
| wellbeing_locus | 0.604 | 0.82 | MIX-SHIFT: composition change, read trend cautiously |

Disagreements are case studies, not silent overrides.

