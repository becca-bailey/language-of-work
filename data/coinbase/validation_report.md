# Validation report: Coinbase

## 1. Ground truth (chunk level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.381 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2021** (no hypothesis configured)
- Altruism-control correlation: 0.656

## 2. LLM pairwise tournament
- Duel agreement (PRIMARY): **75%** of 40; confident |Δz|≥1.0: **95% (19 pairs)** — PASS; close: 57% (21)
- Spearman is the timeline-shape statistic, secondary (≈6.7 games/yr; BT ranking needs ~10 to be stable)
- Chunk embedding-vs-LLM Spearman: **0.643**
- Sentence embedding-vs-LLM Spearman: **0.753**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- note: insufficient early-year tournament coverage

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.968** (PASS)
- Mean: 0.986

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.08 (n=67) — PASS

## 5. Control decoupling (all axes, chunk level)

| axis | r vs control | r(topk, log n) | diagnosis |
|---|---|---|---|
| altruism | 0.381 | 0.593 | PASS |
| craft | 0.769 | 0.394 | MIX-SHIFT: composition change, read trend cautiously |
| inclusion | 0.506 | 0.932 | MIX-SHIFT: composition change, read trend cautiously |
| meritocracy | 0.63 | 0.916 | MIX-SHIFT: composition change, read trend cautiously |
| performance | 0.64 | 0.895 | MIX-SHIFT: composition change, read trend cautiously |
| techno_optimism | -0.027 | -0.445 | PASS |
| wellbeing | 0.592 | 0.62 | MIX-SHIFT: composition change, read trend cautiously |
| wellbeing_locus | -0.052 | -0.281 | PASS |

Disagreements are case studies, not silent overrides.

