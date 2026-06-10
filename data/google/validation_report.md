# Validation report (M6 redux)

## 1. Ground truth (chunk level)
- Altruism peak year: **2025** (FAIL vs 2014 +/- 2)
- Altruism-control correlation: 0.499 (decoupled: PASS)

## 1b. Ground truth (sentence level)
- Altruism peak year: **2007**
- Altruism-control correlation: 0.64

## 2. LLM pairwise tournament
- Chunk embedding-vs-LLM Spearman: **0.673**
- Sentence embedding-vs-LLM Spearman: **0.707**
- 40 pairwise judgments

### Early-year agreement (2005-2013)

- chunk_vs_llm_spearman: 0.373
- sentence_vs_llm_spearman: 0.678

## 3. Axis-sentence perturbation
- Min Spearman across leave-one-out: **0.962** (PASS)
- Mean: 0.985

## 4. Data expansion notes
- Link expansion added sub-page captures (teams, belonging, etc.)
- SPA deep-sample found no rendered 2018-2022 HTML (JS shells only)
- JSON API samples are job-listing payloads — parser skipped

Disagreements are case studies, not silent overrides.
