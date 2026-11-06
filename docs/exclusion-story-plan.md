# Plan: exclusion story as the flagship pudding-style piece

2026-08-06. Decision (Becca, 2026-08-05): the exclusion register is the story.
Throughline: a genealogy of one sentence — the Netflix deck's severance line —
traced through its documented propagation chain, with the leverage/counterforces
material as the "why now" act. Audience: job seekers and burned-out tech
workers. This memo covers cohort, corpus robustness, new-candidate research
results, instrument work, and the build list. Prior art:
[exclusion-story-pilot.md](exclusion-story-pilot.md) (construct, pilot scores,
gender axis), [counterforces-thesis.md](counterforces-thesis.md).

## 1. Story spine (agreed 2026-08-05)

1. Cold open: "which year is this job ad from?" quiz from the scored corpus.
2. The sentence: text-diff scroller, Netflix 2009 → Coinbase 2021 (one-word
   edit, cosine 0.86) → Engine 2025 → the 2026 cohort.
3. The braid: bipartite idea↔company network (pilot memo's recommended viz) —
   Netflix strand, Musk strand (SpaceX → X ultimatum), Slootman strand.
   Include the negative result (keeper test didn't spread) for credibility.
4. Why now: leverage overlay (quit-rate/layoffs annotation vs DEI/idealism
   lines; performance flat). Absorbs unpublished power.mdx material.
5. Reader turn: the page as audience-selection device; exclusion copy as
   information; one gender-axis beat (within-genre comparison only).
6. Coda: the unarchived (Flock, Bending Spoons) — our captures as the only
   record. Upgraded 2026-08-06: the CDX API 403s on flocksafety.com
   specifically (other domains 200; reproduced) — the Wayback Machine's
   response for an excluded domain, i.e. Flock appears actively excluded from
   the archive, not merely uncrawled. Phrase carefully (exclusion mechanism —
   owner request vs robots — is not observable from outside).

## 2. Cohort roster

### In cohort (existing corpus)
| Company | Corpus | Status |
|---|---|---|
| netflix | 416 chunks 2003–26 + deck/HBR canon | solid |
| coinbase | 283 chunks + 2 canon essays | solid |
| engine | 219 chunks | promote the how-we-operate memo into `canon/` for register-tagging consistency |
| ramp | 45 chunks; founders' letter only in 2026-07-23 manual capture | THIN — see work list |
| anduril | 1,552 chunks + #DontWorkAtAnduril canon | solid (job-posting heavy; note in methods) |
| spacex | 408 chunks 2003–25; "Special Forces" copy 2013–20 | solid |
| x | canon-only (ultimatum) | per 2026-07-23 ruling |
| flock | ONE pilot live capture, no data/flock dir | needs full onboarding |
| palantir | 411 chunks; elite_misfits 0.58×4 in pilot | cohort membership = Becca's call; Karp 2022 letter PDF now captured as candidate canon |

### Recommended additions (scout research 2026-08-05/06; all quotes verified in company voice unless marked)

**Tier 1 — add:**
- **Rilla** — 16/30 Ashby listings end with a literal "Don't Work Here"
  section: "Please don't join if you're not excited about … Working ~60
  hrs/week in person" (ops roles: ~70); values blurb "We work 6 days a week,
  12 hour days". Register lives in job-listing template, not page prose.
  Ashby JSON saved (`data/exclusion_pilot/scout_captures_2026-08-06/`).
  Wayback: ~80 Ashby captures 2024–26 with JSON embedded in `window.__appData`
  — a Jan 2025 capture predates the section, so first appearance is datable.
- **Icon** (icon.com) — careers page, server-rendered, founder-voice: "No
  work-life-separation. Ping at 2am or on weekends." / "No bad fits. We part
  ways if it's not a good fit (with respect)." ~30 Wayback captures Apr 2025 →
  Jun 2026 of directly usable prose. Best archive quality of the new wave.
- **Corgi** (YC S24) — careers headline "Most people are not a fit."; listing
  boilerplate "We are in the office 6-7 days a week… If you don't meet them,
  you'll get cut… talent density". Both the not_for_everyone move and the
  Netflix vocabulary in one paragraph. Archive thin (~21 shell captures + 3
  Ashby) but live corpus captured.
- **Cluely** — listings: "six days a week in-person… You are expected to live
  within a block of the office (housing provided)" / "This will likely be the
  most intense job of your life." ~58 Ashby captures 2025–26.
- **Scale AI** — two artifacts: the MEI memo (scale.com/blog, 2024-06-13, "we
  unapologetically prefer people who are very smart", "Hiring on merit will be
  a permanent policy") as canon; careers credos ("Run Through Walls") in
  server-rendered snapshot HTML, yearly Wayback 2019–2026. NOTE: live
  summarizer fetches miss the credos — capture raw HTML.
- **Bending Spoons** — Culture & Policies PDFs: "isn't for everybody"
  (verbatim construct), "We give generous separation packages" (the severance
  move), "a few fantastic people can make a far greater difference than a lot
  of ordinary ones". **Zero Wayback coverage of the modern site** — our
  2026-08-06 PDF captures may be the only record. European carrier —
  broadens the story beyond SV.

**Tier 2 — data points / canon only, Becca's call:**
- Greptile — canonical founder-speech specimen (Gupta's Nov 2024 "no
  work-life-balance… 9am to 11pm" post; X-hosted, needs manual capture) but
  company surfaces are clean. Founder-canon only, like the DHH treatment.
- Mercor — systematic hours disclosure in listings ("we operate six days a
  week"), framed as a trade, not exclusion.
- Traba — "We work harder, longer, and smarter, not just two out of three"
  (careers values); intensity flex without the exclusionary turn.
- Cognition — "Our team is talent-dense" = lineage marker for the network
  viz, not cohort.
- Snowflake/Slootman — doctrine source confirmed (Jan 2022 press release
  distributes "hire drivers, not passengers"; wording needs spot-check);
  careers copy mild. Strand anchor, not cohort.
- Arrowster — reportedly "This role isn't for everyone. It's almost for no
  one." + 7-day weeks (Forbes 2025-05) but careers page 404s; include only if
  the original listing can be recovered manually.

**Contrast cases (valuable, keep out of cohort):**
- Tesla — yearly Wayback 2016–26, and the copy is *welcoming* ("It doesn't
  matter where you come from…"). The most famous hardcore employer never put
  the register in careers copy; sharpens the Musk-strand claim that the
  register lived in ultimatum documents.
- Rippling — "Hard days exist at Rippling. Boring ones do not." Intensity-
  adjacent without exclusion.
- Rejected: Kalshi (only Glassdoor employee voice — a trap worth a methods
  note), Latchbio, Decagon, Autotab (unverifiable/press-only).

### Story beat unlocked by the scouts
The register migrated genres: careers-page manifesto (Netflix→Coinbase era) →
job-listing boilerplate template (Rilla/Corgi/Cluely/Mercor, 2025–26), and the
flex changed from abstract ("talent density") to numeric ("~70 hrs/week",
"6-7 days"). Corgi uses both vocabularies in one paragraph. This gives the
escalation arc a measurable third stage and belongs in the piece.

## 2b. Scoping ruling (Becca, 2026-08-06): new companies are exclusion-only

The 2026-08 additions were scouted BECAUSE they speak the register — a
purposive sample. Including them in any other story or cross-company
aggregate would skew it by construction, so they enter the universe gated to
the exclusion allow-list only (pipeline.yaml enforces this; every legacy
story pins an explicit list). Consequence for the piece itself: the new wave
supports cohort and specimen claims ("here is the register, here is who
speaks it, here is when each artifact appeared"), never prevalence claims
("X% of startups now talk like this") — prevalence comparisons stay within
the pre-existing, non-purposively-selected universe.

DONE 2026-08-06: pipeline.yaml universe + exclusion list updated; profiles
created for flock, rilla, icon, corgi, cluely, scale, bendingspoons (scout
findings and domain-history traps recorded in each profile comment); CDX
discovery run — review each data/<company>/discovery_report.md (M1 gate).

## 3. Corpus robustness work list

1. **Flock onboarding** — create data/flock profile; manual live-capture route
   (like engine); start periodic recapture (zero Wayback: our copies are the
   record). Migrate the pilot's flock_live.html into the proper structure.
2. **Ramp deepening** — manual capture of remaining live pages beyond the
   founders' letter; parse archived Ashby/careers JS-shell captures where
   possible; recapture cadence.
3. **New Tier 1 onboarding** — rilla, icon, corgi, cluely, scale,
   bendingspoons profiles. Ashby-board companies: capture via posting API
   (live) + `window.__appData` parsing (archived) — consider a small shared
   `ashby` helper in the fetch path since four companies need it.
4. **Canon registrations** — scale MEI memo; bendingspoons PDFs (already
   staged in `data/exclusion_pilot/scout_captures_2026-08-06/`); engine
   how-we-operate → canon/; palantir Karp letter(s) if Becca rules Palantir
   into the cohort (2020 S-1 letter is the sharper candidate-facing text —
   unverified, fetch from SEC); greptile founder post (manual, X-hosted);
   snowflake press release (strand anchor; verify wording).
5. **Recapture cadence** — the no-Wayback set (flock, bendingspoons, ramp,
   corgi live pages) needs a periodic manual/live capture habit; worth a
   lightweight script + calendar reminder rather than ad-hoc.
6. **Twitter contrast (optional)** — pre-Elon corpus (282 chunks 2014–22)
   as before/after for the X ultimatum beat.

## 4. Instrument & analysis work (carried from pilot + new)

- best_work_fastest_pace cliché/warning split (pilot open item) — required
  before that concept is citable.
- New sub-concept candidate: **hours_disclosure** (numeric workload in
  listings) — cleanly countable, dates the genre shift.
- Genre tag: careers_page vs job_listing vs canon — comparisons stay
  within-genre (manifesto-voice confound; Basecamp stays the calm-manifesto
  control in every gender-coding chart).
- Rerun the pilot scorer over the expanded cohort; reuse the netflix-story
  judge step verbatim (pilot recommendation).
- Story slug + pipeline.yaml entry + M1 profiles for new companies.
- Shopify downstream scores are stale post-backfill (2026-08-05) — refresh
  before citing Shopify anywhere in the piece.

## 5. Build list (piece-specific)

1. Sentence text-diff scroller (new component).
2. Bipartite idea↔company network with time axis (pilot-recommended; new).
3. "Which year is this job ad from?" quiz (new, corpus-fed).
4. Leverage overlay chart (extends existing story-chart patterns; JOLTS
   quit-rate + layoffs as annotation, never fitted).
5. Exclusion-register unit chart (extend pilot's gender_unit_chart).
6. Reuse: gender pole scatter (within-genre framing), netflix_evolution
   concept timeline.

## 6. Risks / methods caveats

- Small-n for the 2026 wave (Ramp 45 chunks; Corgi/Cluely young) — present
  rates with n; frame the new wave as specimens, not trends.
- Company-voice bar: Glassdoor/press quotes never cite as company copy
  (Kalshi trap). Founder posts = founder-canon register, tagged like DHH.
- Anduril corpus is job-posting heavy (966 chunks in 2025) — normalize by
  genre before any per-company rate.
- Craft axis stays out (failed validation). DHH numbers stay out of
  load-bearing acts until the hand-label gate passes.
- Verbatim-propagation claims only where judge-vetted (existing
  culture_propagation pipeline); "best and brightest"-class generic phrases
  stay excluded.

## 7. Suggested sequencing

1. Corpus work (§3) — capture the perishable stuff first (flock,
   bendingspoons, live Ashby boards), then onboarding + pipeline runs.
2. Instrument work (§4) and rerun pilot scoring on the full cohort.
3. Hand-label gate on the exclusion instrument (same pattern as other axes).
4. Build the four new components against exported data.
5. Draft the piece; power.mdx cannibalization decision at that point.
