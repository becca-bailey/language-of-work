# November 2026 refresh — findings review

Status of the two flagged (unpublished) stories after the corpus refresh,
with the checks run before any editorial decision. Data as of commit
`6ede24d`; all numbers reproducible from the current exports.

## 1. Craft × AI: the "no collision" framing is dead

`craft-ai.mdx` currently says neither levels nor three-year changes
correlate (levels ρ = −0.11 p = .66, deltas ρ = +0.09 p = .72) and that no
AI-loud company talks craft. The current export says:

| test | ρ | p | n |
|---|---|---|---|
| levels (craft vs AI share) | +0.00 | .995 | 20 |
| three-year deltas | **+0.45** | **.046** | 20 |
| deltas, dropping the 3 flagged-coverage companies (Meta, Nvidia, Uber) | +0.51 | .037 | 17 |
| deltas, AI share on mission prose only | +0.44 | .054 | 20 |

The robustness rows are the important part: the signal is not a coverage
artifact and not job-listing chrome. Companies that raised AI talk raised
craft talk in the same window — Salesforce (dCraft +0.051 / dAI +0.241),
Google (+0.050/+0.180), GitLab, Shopify, Stripe — while the companies that
cut AI talk (Amazon, Airbnb) sit at the bottom of the craft deltas too.

The corner claims broke separately:

- **Apple is no longer the AI-silent craft pole** by the scatter's own
  definition: its all-labels AI share is 14.1%. But 25 of its 29 recent
  AI chunks are `job_listing` (the "AIML —" org prefix in ML job titles);
  its **mission prose is 5.3% AI** — consistent with the old ~3.5% claim.
  The scatter inherits the tracker's deliberate inclusion of job listings
  (talk-vs-hire contrast), so Apple's position is hiring-composition, not
  register change. Worth deciding whether the scatter should use the
  mission-only share, or keep the wider gate and say so in the caption.
- **Salesforce now sits at the craft pole** (0.112 vs Apple's 0.119)
  while being AI-loud (24.5%). "No AI-loud company talks craft" is false.

Editorial options, in rough order of my read: (a) reframe — the trade-off
didn't materialize, and where AI talk arrived, craft talk thickened
alongside it, which is arguably the more interesting story; (b) hold
unpublished for another capture year — p = .046 on twenty companies is one
borderline result, and the caption's own "what would settle the question"
list still applies; (c) minimal stats-and-corners update keeping the
"too little history" hedge.

## 2. Power story: the wellbeing numbers were stale before the refresh

The flagged "flip" (r_diff −0.25 → +0.45) is not a November-data event.
Recomputing from the exports:

| export | wellbeing r_raw | wellbeing r_diff |
|---|---|---|
| pre-refresh (commit `40fb8c0`) | +0.70 | **+0.54** |
| post-refresh (commit `6ede24d`) | +0.70 | **+0.45** |
| what `power.mdx` quotes | +0.57 | **−0.25** |

The −0.25 comes from the July essay analysis (16-company panel, mission-
chunk embedding axis). The export switched to the fingerprint axis series
(chunk-level top-k from `axis_scores.parquet`) when the story page was
built (`6f7f77d`), and that instrument has shown a positive differenced
correlation all along. The redesign captions carried the July numbers
over without recomputing — that's on the conversion, and the refresh only
moved the value from +0.54 to +0.45.

Consequences for the story's argument:

- "Wellbeing answered the pandemic, not the bargaining table" rested on
  the negative sign. On the current instrument, wellbeing co-moves with
  quits about as much as the counterforces do (r_diff +0.45 vs idealism
  +0.30, DEI +0.33). The contrast case needs rework or removal.
- The z ≈ +2.1 "largest single-axis jump in 2020" is also the old
  instrument; the current panel's 2020 deviation for wellbeing is +0.53.
- What still separates performance is intact and arguably cleaner:
  per-company split 10/20 positive with median 0.00 (a coin flip) against
  idealism 16/20 and DEI 17/20, and the smallest amplitude. Current
  canonical numbers: idealism +0.69/+0.30, DEI +0.75/+0.33, wellbeing
  +0.70/+0.45, performance +0.56/+0.35, locus +0.58/+0.45
  (`data/power_robustness.md`).
- `power_robustness.py`'s static "Reading" prose still describes the old
  instrument (it says wellbeing's r_diff goes negative two paragraphs
  under a table showing +0.45) — needs a text pass whichever way the
  story goes.
- One new texture point from the robustness run: the locus series ticks
  back toward structural in 2026, the first reversal in the record
  (one year — watch it, don't claim it).

## 3. Small items

- `wellbeing.mdx` → "What this can't say": the "only 8 of 15 companies
  have enough enumerated benefits on both sides of 2022" bullet is from
  the old universe and doesn't re-derive on the current one; recompute or
  drop the counts.
- Published-story reconciliation (done in `6ede24d`): wellbeing captions
  updated (20/20 firms, median +0.65, CI [0.57, 0.84]; care peak reads
  2021–22; whole-life benefits peak 2017–18 at ~1 in 10; fertility stated
  as 15 mentions). Verified unchanged: gender concept scores, DEI
  civilizational register (Palantir-only, 3 chunks), netflix captions.
