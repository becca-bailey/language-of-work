# Validation report: Netflix

## 1. Ground truth (chunk level)
- Altruism peak year: **2022** (no hypothesis configured)
- Altruism-control correlation: 0.615 (coupled: INVESTIGATE)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2020** (no hypothesis configured)
- Altruism-control correlation: 0.839

## 2. LLM pairwise tournament
- Chunk embedding-vs-LLM Spearman: **0.09**
- Sentence embedding-vs-LLM Spearman: **0.402**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- chunk_vs_llm_spearman: 1.0
- sentence_vs_llm_spearman: 1.0

### performance tournament
- Chunk embedding-vs-LLM Spearman: **0.616** — PASS
- Sentence embedding-vs-LLM Spearman: **0.766**
- 40 pairwise judgments

### craft tournament
- Chunk embedding-vs-LLM Spearman: **-0.09** — BELOW GATE (0.6): INVESTIGATE
- Sentence embedding-vs-LLM Spearman: **-0.095**
- 40 pairwise judgments

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.956** (PASS)
- Mean: 0.989

## 4. Axis separation

- craft vs performance: vector cosine 0.093, chunk-level r=0.16 (n=353) — PASS

Disagreements are case studies, not silent overrides.

