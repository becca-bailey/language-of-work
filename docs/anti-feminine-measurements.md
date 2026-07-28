# Is "anti-feminine" different from "masculine"? — discovery memo

2026-07-24. Motivated by Becca's journal question (docs/journal/2026-07-24.md):
exclusionary careers copy ("we aren't for everyone") sits in stark contrast
with feminine-coded inclusion language — can we measure not just which
concepts are masculine-coded, but which are *anti-feminine*, and is that a
different measurement?

Answer: **yes, it's a different measurement, and both versions of it return
findings — one confirming, one falsifying, and the falsification is the
better story.** Scripts and data in `data/exclusion_pilot/`
(`decompose_poles.py`, `disavowals.py`, `pole_decomposition.json`,
`disavowals.json`, `disavowal_judgments.json`).

## Measurement A: pole decomposition (geometry)

The Kozlowski axis is bipolar — one number where "close to masculinity" and
"far from femininity" are the same direction by construction. Decomposition:
score every gender-mention-free sentence (n=9,896) separately against the
masculine-pole centroid and the feminine-pole centroid, z-score each over the
corpus. A register can then be masculine-coded two ways:

- **approach** — unusually close to the masculine pole (high mz)
- **avoidance** — unusually far from the feminine pole (low fz)

The two raw similarities correlate 0.84 (both partly measure "how much this
sentence lives in gendered semantic territory at all"), which is why the
decomposition is informative: position *along* the m=f diagonal is
gender-domain-ness; distance *off* the diagonal is the bipolar score.

| register (anchor-matched) | n | bipolar z | masc-pole mz | fem-pole fz |
|---|---|---|---|---|
| exclusion register | 61 | +0.46 | +0.30 | +0.05 |
| intensity / high-bar | 109 | +0.33 | **+0.66** | **+0.49** |
| boldness / ambition | 97 | +0.32 | +0.49 | +0.35 |
| **candor / feedback** | 39 | **+0.61** | **+0.12** | **−0.19** |
| belonging / inclusion | 233 | −0.44 | +0.29 | +0.74 |
| care / wellbeing | 43 | −0.32 | +0.65 | +0.98 |
| all masc-coded (z≥+0.5) | 3,266 | +0.92 | +0.22 | −0.36 |
| all fem-coded (z≤−0.5) | 1,663 | −0.95 | −0.13 | +0.71 |

Readings (register level, anchor-matched):

1. **Intensity and care copy are both gender-saturated.** "We work hard /
   we take care of each other" both sit close to BOTH poles — personal,
   embodied, people-language. Their bipolar scores come from which pole wins,
   not from avoidance.
2. **Masc-coded copy in aggregate skews avoidance** (mz +0.22 vs fz −0.36):
   across the whole corpus, sounding masculine is more about distance from
   femininity than proximity to masculinity. Becca's "anti-feminine"
   intuition is real at corpus level.
3. **The exclusion register itself is mid** — moderate approach, neutral
   avoidance. Its masc-coding is not the strongest signature here; the
   original hypothesis ("exclusion = anti-feminine geometry") is at best
   weakly supported. Small n throughout; anchor-matched groups, not judged.

### Concept-level decomposition (judged clusters — the citable version)

2026-07-24, later same day: per-concept mz/fz added to the story export
(`gender-concepts.json`); story chart `GenderPoleScatter.astro`.

**CORRECTION to the first draft of this memo:** the anchor-matched candor
register (n=39) showed an avoidance signature (mz +0.12 / fz −0.19), but the
*judged candor cluster* (n≈130, "direct feedback and candor") shows the
opposite — **approach** (mz +0.76 / fz +0.44). Netflix's candor definitions
are people-heavy (courage, vulnerability, feedback verbs), and the narrow
anchor set had selected terse imperative sentences. The judged cluster is
the better-verified population; prefer it. The narrow-register result stands
only as a hint that a terse-feedback *sub-register* may exist.

Concept-level pattern (23 shared concepts):

- **Masculine by approach** (people-heavy, above diagonal, both poles high):
  direct feedback and candor (+0.76/+0.44), core values (+0.49/+0.30), bold
  innovation (+0.47/+0.23), action-oriented execution (+0.51/+0.35).
- **Masculine by avoidance** (impersonal, both poles low, fem lower):
  transparent/accessible communication (−0.35/−0.68), rapid growth and scale
  (−0.30/−0.53), deliberate effort and discipline (+0.09/−0.25), culture
  transparency, continuous improvement.
- **Feminine by approach — with no avoidance counterpart:** every strongly
  feminine-coded concept is close to the feminine pole (ERG programs
  +0.19/+1.11, identity communities +0.58/+1.01, collaborative culture
  +0.66/+0.85). The weakly-feminine concepts (pay equity −0.56/−0.30,
  remote work −0.48/−0.20) avoid the masculine pole but never reach strong
  feminine coding that way.
- **The asymmetry:** femininity in this corpus is *approached*; masculinity
  is often just what remains when copy moves away from the feminine pole
  while staying impersonal.

## Measurement B: disavowal analysis (rhetoric) — "what companies say no to"

Method: 1,049 corpus sentences with negation markers → Haiku judge (temp 0,
forced tool, cached by sentence hash) decides whether each *disavows a way of
working / kind of workplace / kind of person* and extracts the disavowed
thing as a neutral phrase ("we are not a family" → "being a family") →
each rejected phrase is scored on the gender axis (frozen baseline z).
245 disavowals extracted.

**Prediction: disavowed content skews feminine-coded. FALSIFIED — and the
truth is better.**

- Rejected content averages **+0.56z — more masculine-coded than the corpus
  itself** (+0.17). 56% of rejected things are masc-coded; **only 6% are
  fem-coded.**
- What gets rejected: brilliant jerks (+2.36, the most masc-coded rejection
  in the corpus), silence-as-humility (+1.80), vesting handcuffs (+1.73),
  the status quo (+1.63), hiring jerks (+1.60), hands-off management,
  bureaucracy, rules, convention.
- What almost never gets rejected: care, flexibility, belonging, support —
  with one legendary exception: **"being a family" (−0.81), rejected five
  times, by exactly the Netflix lineage** (Netflix ×4, Coinbase ×1). The
  other fem-coded rejections are scattered (Snap rejecting "pressure to be
  popular, pretty, or perfect"; Shopify rejecting "prescriptive roles").
- The disavowing sentences are themselves masc-coded on average (+0.42):
  **disavowal is a masculine-coded speech act**, near-independent of target.
- Exclusion-register disavowals (n=8, tiny) also mostly reject masc-coded
  targets (+0.72 mean) — the "we're not for everyone" family mostly rejects
  comfort-adjacent and convention-adjacent things phrased in masc register.

The story sentence this supports: *in a thousand negations across
twenty-three companies, almost nothing feminine-coded is ever rejected —
except the family.* Companies define themselves against masculine-coded
vices (jerks, ego, bureaucracy, the status quo); the Netflix lineage is
nearly alone in defining itself against a feminine-coded frame, and it does
so by swapping family for a professional sports team.

## Caveats before any of this is published

- Measurement A groups are anchor-matched (embedding similarity ≥0.5 to 2–3
  anchor sentences), not judge-verified; ns are small (39–109).
- Measurement B phrases are judge-authored paraphrases; their gender scores
  inherit Haiku's word choices. Mitigation: the prompt demands neutral,
  defender's-voice phrasing; spot-check `disavowals.json` (sorted by z).
  A robustness pass could score the *original sentence with negation
  stripped* instead of the paraphrase.
- Single extraction pass, temp 0, no second judge; ~5 near-duplicate deck
  variants inflate the "being a family" count (they are real corpus
  captures across years, consistent with how the propagation tracker counts).
- Pole centroids average 16 term embeddings; fem-pole similarity partly
  tracks person-words generally. The decomposition table should be read as
  registers relative to each other, not absolute effect sizes.

## Recommended next steps

1. The disavowal beeswarm ("What companies say no to") is in the draft story
   (`DisavowalStrip.astro`, data `gender-disavowals.json`) — Becca's
   editorial call on whether it stays.
2. If Measurement A goes in the story, judge-verify the register groups
   first (same pattern as the concept judge).
3. Robustness: re-score disavowals via negation-stripped originals;
   dedupe deck variants; second-judge a 50-item sample.
