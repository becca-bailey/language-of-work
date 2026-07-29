# Pre-registration: altruism tournament runs, 2026-07-21

Written before launching the runs. Companies: google, salesforce, coinbase,
stripe, basecamp (40 pairs each, seed 42, judge claude-sonnet-4-5).
netflix and palantir already ran; their results stand as-is.

## Gates (unchanged from validate_axes.py)

- Chunk-level embedding-vs-LLM Spearman >= 0.6 → PASS.
- Below 0.6 → INVESTIGATE (case study, not silent override).

## Pre-registered interpretation for flat-series companies

stripe and basecamp are hypothesized *register-refusers*: their altruism
series are near-zero (raw top-k means 0.013 and -0.013) and the story claim
about them is "flat and low," NOT "peaked in year X."

For these two companies only:

- A LOW Spearman is consistent with the flat-series hypothesis (ordering of
  noise is noise) and will NOT be read as a validation failure of the story
  claim. It will be reported as-is with this interpretation attached.
- A HIGH Spearman (>= 0.6) would be a *surprise* requiring investigation:
  it would suggest real year-to-year idealism variation we claimed absent.
- The tournament does not test the "low level" part of the claim at all
  (Spearman is rank-only). The level claim rests on the raw cross-company
  scale and, if pursued, a future absence-check instrument.

For google, salesforce, coinbase: standard gate applies. Google additionally
carries the open ground-truth FAIL (peak 2025 vs expected 2014±2, control
coupled at 0.52); the tournament is the second angle on whether the late
peak reflects real language or axis contamination (e.g. DEI-adjacent
belonging copy scoring as idealism).

## Not validated by these runs

Cross-company level comparisons, magnitudes, flavor taxonomy, and quote
*selection* (the judge re-ranks the axis-selected evidence quotes; it cannot
detect a wrongly omitted quote).
