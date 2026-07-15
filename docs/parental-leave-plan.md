# Parental-leave study — plan (July 2026)

Prompted by Heather Cairns's July 2026 Threads post (Google employee #4, first
HR manager). Her account: the founders wanted a generous maternity precedent
for Google's first employee pregnancy (~six months off, plus cash gifts); she
saw it as a "dangerous precedent" and "favoritism" toward "mama," and says she
felt "deeply resentful" as someone who would never use the benefit herself.

That post contains, in one anecdote, three things this project already
measures separately: a **benefit** (enumerable weeks × pay), the **rhetoric
around it** ("generous"), and a **fairness counter-register** (leave as
zero-sum favoritism rather than infrastructure — the same move as
meritocracy-vs-DEI). This plan turns the anecdote into a study.

## Research questions

1. **What did companies actually say?** Parental-leave language on careers/
   benefits pages across the corpus, 2005–2026: weeks, pay %, who qualifies.
2. **What did "generous" mean, when?** Era benchmarks (pre-FMLA, 1990s, 2000s,
   2010s arms race, 2020s) from external sources, against which each company's
   enumerated policy can be placed.
3. **When did paternity/partner leave appear**, and how did the
   maternity:paternity gap close (or not)?
4. **Who else made the Cairns argument?** Documented cases of tech executives/
   founders/investors framing family leave as unfair to non-parents or a bad
   precedent — the fairness counter-register as a datable discourse.

## What the corpus already contains (inventory, checked 2026-07-15)

- **`data/<co>/wellbeing_benefits.jsonl`** (15 companies; missing netflix —
  zero benefits-page coverage per `data/wellbeing_coverage.md` — and the new
  adds uber/apple/nvidia). Already extracts `parental_leave` items with
  locus/specificity/verbatim/value. ~75 parental-leave rows exist today.
- **The Google specificity collapse is already in hand.** 2005: "12 weeks off
  at 75% pay" + "2 weeks off at 100% pay when your spouse or domestic partner
  has a baby" (chunk `e27c6dcec175ad55`). 2016–2020: "generous parental leave
  policies," no numbers, five years running. The adjective replaced the
  number. This is the wellbeing plan's specificity gradient ("numbers are
  commitments, adjectives are rhetoric") realized in a single benefit — and
  it's the *same word* Cairns's debate was about.
- **The 2005 snapshot is contemporaneous evidence for the Cairns story.**
  It shows what Google's policy actually was in the era she describes:
  12 weeks at 75% for the birthing parent — notably *less* than the ~6 months
  she says the founders floated, and 2 weeks for partners. Whatever was
  granted to employee-pregnancy #1, the codified policy that survived to the
  careers page was far more modest. (External check: Google's documented 2007
  expansion to 18 weeks at full pay and the Laszlo Bock attrition rationale —
  verify via research report.)
- **Tenure/corpus overlap is exactly one year.** Cairns was at Google
  1999–2005 (confirmed 2026-07-15); Google corpus coverage starts 2005. The
  2005 snapshot is therefore the handoff baseline — the codified outcome of
  the debate she describes, photographed as she left, two years before the
  18-week expansion. The corpus documents the post-Cairns era; her account
  (the Threads posts, her memoir *Employee Number Four*, the *Valley of
  Genius* oral history) covers 1999–2004 and is testimony, not archive. The
  story must not imply the corpus witnessed the internal argument.
- **The terminology arc is visible end to end.** salesforce 2008 "Paid
  Maternity/Paternity Programs" → snap 2019 "maternity, paternity, and family
  caregiver leave" → github 2017–24 "five months of paid family leave to all
  new parents" → basecamp 2022 "primary/secondary caregiver" → salesforce
  2025–26 "inclusive family leave." Maternity → maternity+paternity →
  parental → family/caregiver → inclusive: the register de-genders over time.
- **The gender gap is quantified where numbers exist.** google 2005: 12w/75%
  vs 2w/100%. shopify 2010: 30 working days (maternity) vs 15 days
  (parental). amazon 2017: 10w maternity + 6w parental. basecamp 2022: 16w
  primary vs 6w secondary caregiver.
- **Jurisdiction confound (Shopify).** Shopify is Canadian: paid maternity
  leave there is a government EI benefit (~15 weeks at ~55% pay, plus
  shareable parental benefits; ~a year job-protected under Ontario law —
  verify exact figures). Its careers-page numbers ("30 working days" 2010;
  "17 weeks at 85% take-home" 2012, matching Ontario's 17-week statutory
  pregnancy-leave window) are almost certainly **top-ups over the state
  baseline**, not total leave — while US pages enumerate the total because
  the US paid baseline is zero. Raw weeks are not comparable across
  jurisdictions.
- **`track_benefits.py` family_caregiving prevalence** (keyword,
  `data/benefits_trends.md`): first 2011, peak 2019 (10 chunks), **zero in
  2024**, small 2026 recovery. Matches the concession arc's deflation.

## Hypotheses (pre-registered, stated before scoring)

1. **Specificity tracks leverage — with a known complication.** Enumerated
   weeks should be densest in the 2015–2021 arms-race/leverage era and decay
   to adjectives after 2022. The complication we already see: Google went
   numbers→"generous" by 2016, *before* the leverage inversion. If the
   pattern is "numbers disappear as policies improve" (adjectives as
   luxury-brand understatement) rather than "numbers disappear as commitments
   erode," that's a different — and honest — finding. Distinguish via the
   external benchmark table: was the hidden number rising or falling?
2. **The gender gap closes in language before it closes in weeks.**
   Gender-neutral phrasing ("parental," "all new parents") should precede
   parity in enumerated weeks where both are visible.
3. **Family/caregiving mentions follow the concession curve** (rise into
   2019–2021, deflate 2022–2024), like care/DEI in the wellbeing story.
4. **The fairness counter-register is datable and recurrent.** Cairns's
   framing should have documented cousins across eras (verify via research:
   the "childless employees deserve equal perks" discourse, executives on
   leave as unfairness). Prediction: it surfaces publicly when leverage is
   *low* (pre-2010, post-2022) and goes quiet when talent competition makes
   it unsayable — the mirror image of the concession.

## Phases

**Phase 0 — Verify the anchor anecdote.** The Threads post is a 2026 memory
of a ~2000 event. Archive the post itself; check it against Cairns's earlier
tellings (her memoir *Employee Number Four*, Adam Fisher's *Valley of Genius*
oral history, interviews) for drift between versions — noting she is
currently promoting the memoir, which is context for why the story is being
retold now, and how. Also verify the actual policy timeline:
pre-2007 policy, the 2007 18-weeks expansion, the Bock attrition data.
External research report: `docs/research/parental-leave-history.md`
(deep-research run 2026-07-15, cut short before synthesis; hand-synthesized
from 68 verified results). Key Phase-0 outcomes already in hand: the "mama"
is almost certainly Susan Wojcicki (joined 1999 four months pregnant, first
Google maternity leave, no policy existed, her request became the 12-week
policy); the Threads quotes are unverified in any indexed source and the
anecdote appears new with the memoir promotion; Google's 2007 12→18-week
expansion and the (self-reported) 50% attrition drop are well corroborated.
Remaining: consult the memoir and full *Valley of Genius* text; second pass
on the 1990s–2000s fairness discourse (see report §5).

**Phase 0.5 — Pre-2005 Google archaeology.** The corpus's 2005 start was the
pipeline's window, not Wayback's: `cdx_query` defaulted `from_ts="2005"`, so
1998–2004 was never queried. Wayback demonstrably holds a 1999 Google jobs
page (17 openings, "the only Chef job with stock options" — covered in press).
`fetch_snapshots.py` now honors a per-pattern `from_year`, and the Google
profile adds `google.com/jobs.html` (1999-era) plus widened windows on the
`/jobs/` patterns. Run `discover --company google`, review the new report,
then fetch. If any 1999–2004 page enumerates leave, it becomes the earliest
contemporaneous policy record — potentially *inside* the Cairns tenure, which
would upgrade the "handoff baseline" framing to direct overlap. Benefits may
also live on sub-pages (e.g. benefits.html under /jobs/) — check the CDX
prefix results during M1 review rather than guessing URLs now. Extend the wellbeing benefits
taxonomy for parental-leave rows with four fields: `beneficiary`
(birthing/maternity | partner/paternity | neutral/all-parents |
primary-caregiver | secondary-caregiver | adoption), `weeks` (number|null),
`pay_pct` (number|null), and `baseline` (total | topup | unknown — see the
jurisdiction confound; company HQ country becomes a per-company field, and
non-US companies default to `unknown` until the page text settles it). Re-run extraction over `benefits_perks` +
`job_listing` chunks for all 19 companies (adds netflix/uber/apple/nvidia if
their corpus supports it; netflix likely stays empty — say so rather than
patch). Reuse the wellbeing validation pattern: hand-code a sample before
trusting the pass.

**Phase 2 — External timeline layer (annotation, not causation).** Era
benchmark table: FMLA 1993 (12w unpaid, the legal floor), California Paid
Family Leave 2004, Google 2007 (18w paid), the 2015 arms race (Netflix
"unlimited" year, Microsoft/Amazon/Adobe expansions), post-2022 retrenchment
if documented. Each row: weeks, pay, source, date. All dates from the
research report, not memory. Same guardrail as counterforces: overlay and
annotate, never fit.

**Phase 3 — Analysis.**
- Weeks×pay trajectories per company where enumerated (small multiples;
  sparse — plot points, not lines, where gaps are real).
- Specificity composition over time (enumerated / named-no-number / generic),
  pooled and per company. The Google collapse is the case study.
- Terminology arc: first/last corpus appearance of "maternity," "paternity,"
  "parental," "family leave," "caregiver," "primary/secondary" per company —
  a dated register-shift table, like the DEI registers.
- Maternity:partner weeks ratio where both enumerated (H2).
- Company policies placed against the era-benchmark table: who was actually
  above the bar when they said "generous"?

**Phase 4 — Story page.** Working title: *"Generous."* Spine: open on the
Cairns post (the word "generous" as accusation); pivot to the 2005 snapshot
(what the policy actually said); the specificity collapse (the word replacing
the numbers); the terminology de-gendering arc; the era-benchmark reality
check; close on the fairness counter-register as the recurring anti-pole —
what gets said about leave when workers can't walk. Fits the counterforces
thesis as a chapter: parental leave is the stickiest, most quantifiable
concession, and "favoritism" is its meritocracy.

## Guardrails

- Cairns's post is testimony, not record — treat her claims (half-year offer,
  cash gifts, founder favoritism) as *her account*, checked against other
  tellings and the documented policy record. The story is allowed to note
  where memory and archive disagree.
- No causal claims about why numbers vanished from pages (legal review,
  redesign, ATS migration are all live confounds — the wellbeing plan's
  coverage-audit rule applies: check snapshot gaps before coding a removal).
- The fairness counter-register catalog reports *documented public
  statements* only, with dates and sources; no vibes, no paraphrase without a
  citation.
- External anchors: every date/number in Phase 2 must trace to the research
  report or a primary source, not model memory. Anything unverified ships
  with a "(verify)" marker or not at all.

## Relationship to existing workstreams

- **Reuses** the wellbeing extraction machinery + validation pattern;
  **extends** its taxonomy rather than forking it.
- **Feeds** the benefits story (family_caregiving is already a tracked
  category) and the counterforces overlay (leave-policy events join the
  datable-proxy table).
- **Independent of** corpus fill and the craft/AI workstreams — like the
  wellbeing page, it mostly runs on what's already embedded/extracted, plus
  one targeted extraction pass. New capture is optional (benefits subpages
  for uber/apple/nvidia) and shouldn't gate Phases 0–3.
