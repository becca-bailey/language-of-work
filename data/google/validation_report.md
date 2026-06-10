# Validation report (M6 review gate)

## 1. Ground truth

- Altruism peak year: **2014** (PASS vs 2014 +/- 2)
- Altruism-control correlation: -0.005 (decoupled: PASS)

## 2. LLM pairwise tournament

- Embedding-vs-LLM ranking agreement (Spearman): **0.532**
- 40 pairwise judgments (see validation.json)

## 3. Axis-sentence perturbation

- Min Spearman across leave-one-out: **0.938** (PASS)
- Mean: 0.974

Disagreements between checks are case studies, not silent overrides — investigate the chunks before believing or discarding the finding.

## Case study: the 2005-2006 embedding-vs-LLM disagreement (M6 adjudication)

The pairwise tournament rated 2005/2006 highly idealistic; the embedding axis
scored 2005 below baseline. Human review (M6) sided with the judge: the early
copy ("Can one conversation change the world?") reads genuinely idealistic.

Diagnosis (sentence- vs chunk-level projection):

- "Can one conversation change the world?" projects at +0.25 as a sentence —
  comparable to 2014's flagship copy (+0.34)
- The 400-word chunk containing it projects at only +0.13-0.19: on 2005-2007
  single-page sites, idealistic sentences are averaged down by surrounding
  operational text
- Register is a minor factor: a modern-voice restatement moves the projection
  only +0.25 -> +0.28

Conclusion: this is the genre-drift confound from the risk register,
materialized. Chunk-level projection partly measures page architecture
(mission-copy purity per block), not just stance. The 2014 peak finding
stands — its chunks are both pure AND strongly idealistic — but early-era
years are systematically under-credited at the chunk level. Any claim about
2005-2013 levels should cite the LLM tournament ranking alongside the
embedding series, or use sentence-level scoring (see below).

Possible methodological response (not yet implemented): project at the
sentence level within mission chunks and aggregate top-k sentences per year.
This makes scores comparable across page-architecture eras at the cost of
more embedding calls and a noisier unit of measurement.
