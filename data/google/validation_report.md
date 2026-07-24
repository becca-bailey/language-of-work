# Validation report: Google

## 1. Ground truth (chunk level)
- Altruism peak year: **2025** (FAIL vs 2014 +/- 2)
- Altruism-control correlation: 0.743 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2022** (FAIL vs 2014 +/- 2)
- Altruism-control correlation: 0.828

## 2. LLM pairwise tournament
- Duel agreement (PRIMARY): **88%** of 40; confident |Δz|≥1.0: **95% (19 pairs)** — PASS; close: 81% (21)
- Spearman is the timeline-shape statistic, secondary (≈3.3 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **0.514**
- Sentence embedding-vs-LLM Spearman: **0.507**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- chunk_vs_llm_spearman: -0.33
- sentence_vs_llm_spearman: 0.304

### performance tournament
- Duel agreement (PRIMARY): **68%** of 40; confident |Δz|≥1.0: **71% (21 pairs)** — INVESTIGATE; close: 63% (19)
- Spearman is the timeline-shape statistic, secondary (≈3.3 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **0.302**
- Sentence embedding-vs-LLM Spearman: **0.592**
- 40 pairwise judgments

### craft tournament
- Duel agreement (PRIMARY): **52%** of 40; confident |Δz|≥1.0: **50% (24 pairs)** — INVESTIGATE; close: 56% (16)
- Spearman is the timeline-shape statistic, secondary (≈3.3 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **0.052**
- Sentence embedding-vs-LLM Spearman: **-0.392**
- 40 pairwise judgments

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.988** (PASS)
- Mean: 0.994

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.225 (n=471) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.743 | 0.86 | POOL-SIZE: top-k inflation, fix estimator |
| craft | 0.478 | 0.437 | PASS |
| inclusion | 0.687 | 0.697 | POOL-SIZE: top-k inflation, fix estimator |
| meritocracy | 0.616 | 0.612 | POOL-SIZE: top-k inflation, fix estimator |
| performance | 0.338 | 0.219 | PASS |
| techno_optimism | -0.025 | 0.105 | PASS |
| wellbeing | 0.702 | 0.785 | POOL-SIZE: top-k inflation, fix estimator |
| wellbeing_locus | 0.728 | 0.707 | POOL-SIZE: top-k inflation, fix estimator |

## 6. Data expansion notes

- Link expansion added sub-page captures (teams, belonging, etc.)
- SPA deep-sample found no rendered 2018-2022 HTML (JS shells only)
- JSON API samples are job-listing payloads — parser skipped

Disagreements are case studies, not silent overrides.

