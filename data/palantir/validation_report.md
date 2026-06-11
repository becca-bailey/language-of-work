# Validation report: Palantir

## 1. Ground truth (chunk level)
- Altruism peak year: **2018** (no hypothesis configured)
- Altruism-control correlation: 0.443 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2018** (no hypothesis configured)
- Altruism-control correlation: 0.22

## 2. LLM pairwise tournament
- Chunk embedding-vs-LLM Spearman: **0.484**
- Sentence embedding-vs-LLM Spearman: **0.747**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- chunk_vs_llm_spearman: 0.8
- sentence_vs_llm_spearman: 0.4

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.944** (PASS)
- Mean: 0.988

Disagreements are case studies, not silent overrides.

