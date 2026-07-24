# Pilot memo: "You probably don't belong here" (exclusionary language story)

2026-07-23. Becca's hypothesis: an emerging register of *exclusionary /
anti-recruiting* careers copy — companies telling candidates they probably
shouldn't apply, as a flex. Hypothesized cohort: Netflix, Coinbase, Engine,
Flock Safety, Ramp, post-Elon X, DoorDash (maybe). This grew out of the
netflix-culture story's `not_for_everyone` concept (judge-vetted echoes:
Netflix → Shopify 2018 → Engine 2021 → Coinbase).

Pilot artifacts: `data/exclusion_pilot/` (captures + scoring script).
Flock Safety has **zero Wayback coverage** — the 2026-07-23 live capture there
is currently the only archival record of their careers copy.

## Draft construct: six sub-concepts

1. **not_for_everyone** — "not the perfect place for everyone" (already a
   netflix-story concept; this story generalizes it)
2. **intensity_warning** — "we'll be honest, working here is intense" /
   "sounds intense? it is" (warning-as-flex)
3. **anti_pitch** — the *letter persuading you not to apply* device (the genre
   marker; Ramp's founders' letter is the purest specimen)
4. **best_work_fastest_pace** — "the best work of your career, at the fastest
   pace of your career" (CAUTION: overlaps a generic recruiting cliché —
   Meta 2019 "you'll do the best work of your career" has no exclusionary
   turn; the instrument must split cliché from cliché-plus-warning)
5. **elite_misfits** — "brilliant misfits," "hardcore people," "we didn't get
   here by hiring 'normal' people"
6. **earned_seat** — "every seat must be earned," "only exceptional
   performance will constitute a passing grade"

## Pilot result (embedding max-sim / hits ≥0.5 per 100 sentences)

| company | hits/100 | strongest signals |
|---|---|---|
| ramp (live 2026) | **33.3** | anti_pitch 0.70 (only company to hit it), best_work 0.98, misfits 0.72×5, intensity 0.76 |
| flock (live 2026) | **17.4** | intensity 0.96 ("We'll be honest, working here is intense"), best_work 0.76, not_for_everyone 0.56 |
| doordash (2023) | 6.8 | best_work only (the cliché side, ×3) — weak support for cohort inclusion |
| coinbase | 3.9 | intensity 0.66×3 ("most intense place we've ever worked", 2024), earned_seat ×2 |
| engine | 2.1 | not_for_everyone 0.64, earned_seat 0.68, intensity ×2 |
| netflix | 1.3 | not_for_everyone 0.57×2, misfits 0.67×5 |
| …mid-pack (meta/palantir/shopify/stripe) | 1.5–2.4 | mostly best_work cliché + misfits-adjacent |
| **airbnb, snap, gitlab, basecamp, starbucks** | **0.0** | clean zeros — incl. Basecamp (anti-intensity control) ✓ |

X post-Elon probe (the Nov 2022 "extremely hardcore" ultimatum, 3 sentences):
earned_seat 0.61, intensity 0.57. The X careers page itself is a JS shell with
no prose; the exclusionary register lives in the ultimatum, which is
**canon-register, not careers copy** — same treatment as the Coinbase essays
(`data/coinbase/canon/`), if included at all.

**Verdict: the construct separates.** Hypothesized cohort elevated, controls
at zero, and the two newest companies (Ramp, Flock) are 5–15× above the
highest corpus company. This looks like a register that *escalated recently* —
Netflix implied it (2009), Coinbase said it (2020–21), Engine formalized it
(2025), Ramp/Flock now open with it (2026). The story arc may be escalation,
not just diffusion.

Direct borrow candidate for the network: Ramp "pushed to do the best work of
your career — at the fastest pace of your career" ↔ Flock "pushed to do the
best work of your life" ↔ Engine "The best work of your career starts here."

## Company onboarding notes (M1 pre-probes, 2026-07-23)

- **ramp**: ramp.com/careers, CDX 2020–2026 solid (4–12/yr). Clean add.
- **flock** (Flock Safety — NOT "Flock Security"): zero CDX on
  flocksafety.com/careers + all probed variants; live page works. Manual
  live-capture route (like engine/how-we-operate); consider periodic captures.
- **doordash**: careers.doordash.com CDX 2021–2024, 301s after (find the new
  host before adding). Pilot signal weak — Becca to decide inclusion.
- **x / twitter**: pre-Elon corpus rich (careers.twitter.com 2016–2020,
  about.twitter.com/careers 2014–2018) — a natural before/after contrast.
  Post-Elon: x.com/careers has 2024+ CDX 200s but is a JS shell; the register
  lives in the ultimatum (canon question for Becca).

## Visualization recommendation

The ask: show ideas borrowed between companies. Options considered:

- **Company↔company network**: at 7–10 nodes it won't hairball, but edges
  ("shares 3 ideas") lose *which* ideas — the most interesting part.
- **Adjacency matrix** (companies × sub-concepts, cells = strength + first
  year): most legible, least narrative.
- **RECOMMENDED: bipartite idea↔company network with a time axis** — idea
  nodes as hubs, company nodes positioned by first-use year (x = year), edges
  weighted by similarity. Reads as a network (her instinct) while keeping
  which-idea and who-first legible; at 6 ideas × ~9 companies it stays clean.
  Falls back gracefully to the matrix if it gets busy.

## Candidate research (2026-07-23; DoorDash ruled OUT by Becca — weak signal confirmed)

Tier 1 — recommend adding:

- **Anduril** — the purest anti-pitch employer brand in the market: the 2024–25
  "#DontWorkAtAnduril" billboard campaign ("Work at Anduril" with "Don't"
  spray-painted over it), "It's hard work, on hard problems, on hard mode. If
  that isn't for you, then Anduril isn't the place for you," "We don't hire
  engineers. We recruit believers," and — from their VP Marketing — "Anduril is
  not for everybody, that's the point." CDX 2018+ (7/yr). Caveat: current page
  is a JS shell; rely on older captures + treat the campaign as canon. Also
  links the exclusion register to the defense-tech mission register (Palantir
  territory from the DEI study).
- **SpaceX** — elite-selection register in company voice: "SpaceX is like
  Special Forces… we do the missions that others think are impossible." Deep
  archive (2013+). Together with the Nov-2022 X ultimatum this establishes a
  **Musk strand** of the register (SpaceX/Tesla hardcore → "extremely hardcore"
  Twitter 2.0) — a second lineage converging with the Netflix strand, which
  reframes post-Elon X from "new company" to "the strand's oldest carrier."

Tier 2 — genuine intensity register, but no exclusion device in company voice:

- **Scale AI** — "Run Through Walls," "Not all hard work is equal… What we
  reject is effort without impact," "extremely ambitious." The famous "Scale
  is not for everyone" line appears only in employee-voice (reviews), not
  page copy. CDX 2019+ solid. Borderline.
- **Rippling** — intense by reputation (reviews say "not for everyone"), but
  on-page copy is mild ("challenging yourself every day"). Weak in company
  voice; skip unless archived copy turns out sharper.

Not cohort, but valuable data points:

- **Cognition** — live careers page says "Our team is talent-dense" — another
  verbatim Netflix-coinage carrier for the *netflix-culture* story; the rest
  of its copy is standard benefits fare.
- **Snowflake / Slootman's "Amp It Up"** — canon-source candidate, not a
  corpus company: Engine's DNA item "Drivers, Not Passengers" is verbatim a
  Slootman chapter title. A third doctrine strand feeding Engine's hybrid.
- **Palantir** — already in corpus; pilot shows elite_misfits 0.58×4. Karp's
  register may qualify it for the cohort from existing data.
- Ruled out: **Verkada** (1,100 words of copy, zero markers), **DoorDash**
  (best-work cliché only), **Levels** (reported anti-pitch doc lives in
  un-archived Notion — unverifiable).

## Gender-coding axis: plan + first discovery (2026-07-23)

Method per Kozlowski, Taddy & Evans (2019) "The Geometry of Culture", exactly
as Becca specified: the axis is built from 16 PURE gender-term pairs
(man/woman, he/she, father/mother, …) — normalized mean of normalized
difference vectors, in the same embedding space as the corpus. No intuition
words in the poles; "hardcore" is projected, never assumed. What it measures
is cultural coding — how strongly language associates with male-skewed
contexts in the training corpus — and that inherited bias is the phenomenon
under study, not a bug (one careful methods sentence owed in the write-up).

**Known-answer test: PASS.** Male-stereotyped occupation terms (infantry
soldier, lumberjack, …) separate cleanly from female-stereotyped (kindergarten
teacher, nurse, …): male-pole min +0.020 > female-pole max −0.100, neutral
terms ≈ 0, and test sentences separate likewise. Pair coherence 0.38–0.55.

**Lexicon test (the falsifiable-intuition part) — intuition partly falsified:**
- Most masculine-coded term in the set: **"builders"** (+0.059) — Ramp's
  literal headline "We only hire builders." Then aggressive (+0.054),
  high performance (+0.049), hustle, move fast, intense, hardcore, relentless
  (all + but modest).
- **Near-zero, not "feminine" (2026-07-23 correction):** bare "battle" (−0.019)
  and "grind" (−0.027) sit within noise of zero (corpus sentence sd 0.039;
  anchors run ±0.07..0.17) — the earlier sign-sorted list over-read them. The
  real story is **sense mixture**: a bare word projects as the average of its
  usage distribution. Disambiguated probes: "soldiers in battle" +0.065 (as
  masculine as "infantry soldier"), "we battle for every inch on the field"
  +0.049, but "battling cancer" −0.007 — the everyday personal/illness sense
  pulls the bare word back to neutral. Same for grind: "hustle and grind
  mentality" +0.052 vs "the grind of caring for a newborn" −0.106. And bare
  "kind" reads mostly as the type/sort sense ("some kind of error" +0.019),
  not warmth. So the intuition "battle = masculine" imagines one sense; the
  axis reports the distribution — which is exactly what it should do, and why
  the instrument operates at sentence/document level where context
  disambiguates. (Caveat on probes: any probe containing a gendered pronoun,
  e.g. "her battle with illness" −0.236, is trivially contaminated — excluded
  from interpretation.)
- Axis stability: split-half (two disjoint 8-pair axes) agree at 0.73; their
  corpus-sentence projections correlate r = 0.71. Full-16 axis is the
  instrument; more pairs would tighten it further, and the human backstop
  remains the definitive check.
- As expected: nurture (−0.084), empathy (−0.059), care (−0.058),
  collaborative (−0.055), work-life balance (−0.053) all feminine-coded.

**Corpus discovery (mission_brand sentences, per-sentence z vs pooled corpus):**
exclusion cohort elevated — engine +0.48, netflix +0.47, palantir +0.35,
coinbase +0.32 — vs google −0.32, amazon −0.46, starbucks −0.26. Pilot
documents all masculine-coded: X ultimatum +1.37, anduril campaign +0.81,
netflix deck +0.68, ramp +0.59, engine memo +0.53, coinbase essay +0.36,
flock +0.14.

**⚠ The confound, found immediately: Basecamp tops the corpus at +0.54** —
the anti-intensity control is the most masculine-coded company. Reading:
assertive founder-manifesto prose ("we don't do X" declarations) is
masculine-coded *independent of intensity*; Google/Amazon write HR/benefits
copy, Basecamp writes manifestos. This is precisely the register confound the
plan warned about, one level deeper: not culture-memo-vs-benefits-page but
manifesto-voice-vs-HR-voice. Design consequence: **the citable comparison is
within-genre** — exclusion manifestos vs calm manifestos (Basecamp is the
perfect control *because* it shares the voice and rejects the intensity), not
exclusion cohort vs whole corpus.

**Instrument path (when it graduates from discovery):**
1. Pair-based axis builder (word-pair mode alongside the sentence-pole mode in
   build_axes) + axes/gender.yaml with the 16 pairs.
2. Dictionary-count cross-check on the same documents (correlate, inspect
   divergences).
3. Human backstop: stratified sample rated for perceived gender-coding,
   Krippendorff vs axis (the Kozlowski validation).
4. Genre controls: score within mission_brand only; compare manifesto-register
   documents against each other; report Basecamp beside the cohort always.

## Corpus status (2026-07-23, post-fetch)

- **spacex**: 116 captures → 180 chunks, 2013–2026. "SpaceX is like Special
  Forces… missions that others think are impossible" runs **2013–2020** — the
  longest-lived exclusion artifact after the deck itself.
- **anduril**: 67 captures → 1,552 chunks, 2018–2026. Careers-page prose is
  mission-forward ("not a traditional defense contractor"), NOT overtly
  exclusionary — the exclusion artifact is the 2024–25 #DontWorkAtAnduril
  campaign, which is canon-register (billboards/social), same decision class
  as the X ultimatum. Cohort case rests on capturing the campaign as canon.
- **ramp**: 70 captures → 34 chunks (historic pages are JS shells); the
  founders' letter lives in the 2026-07-23 manual capture ("persuading you not
  to apply," "brilliant misfits," "hardcore people" all confirmed in chunks).

## Corpus design ruling (Becca, 2026-07-23): canon documents ARE in scope

The story corpus = careers-page chunks + canon documents, tagged by register.
Canon inventory: netflix deck (data/netflix/canon/), coinbase essays
(data/coinbase/canon/), **X "fork in the road" ultimatum** (data/x/canon/,
verbatim-confirmed passages only; note its exit mechanic is *three months of
severance* — the deck's adequate-severance move at company scale), **Anduril
#DontWorkAtAnduril campaign** (data/anduril/canon/). X added to the universe
and cohort (canon-primary; its careers page is a JS shell; pre-Elon twitter
stays out as a possible future contrast corpus). Slootman's Amp It Up remains
open (copyright — excerpt-level only if used).
Analysis rule: instruments read both registers but comparisons stay
within-register (manifesto-voice confound, see gender-axis section).

## Open (Becca's calls)
- Genre split: anti_pitch (the letter device) vs register (the language) —
  track separately? Ramp is the only letter-genre specimen so far; Flock
  Safety's old page reportedly had one (unverifiable — no archive).
- best_work_fastest_pace needs a cliché/warning split before it's citable.
- Story slug + pipeline.yaml entry, M1 profiles, and whether the exclusion
  instrument reuses the netflix-story judge step (recommended: yes, verbatim).
