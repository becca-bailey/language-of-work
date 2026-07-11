# Expansion plan — July 2026

Two new research directions (craft↔velocity axis, AI language evolution), the
company adds that serve them, and a backlog of other expansion ideas. Sequenced
against the current active focus (manual-capture corpus fill) so paid API steps
stay batched.

---

## 1. Axis: craft/quality ↔ "move fast and break things"

### Concept

Does the company present engineering work as *craft* (quality, durability,
taking time to do it right) or as *velocity* (shipping fast, iterating,
tolerating breakage)? Two-pole contrast axis, built through the standard
candidate workflow (`axes/candidates/craft.md` → curate → YAML → build →
circularity check).

### Design hazards (check before building)

1. **Overlap with the `performance` axis.** The current performance pool
   already includes "move fast" phrasing ("who want to move fast", "move fast
   and work with intensity"). Craft↔velocity is *not* the same dimension as
   intensity — Stripe is high-craft *and* high-intensity; Basecamp is
   low-both — but the embedding may not separate them. Validation gate:
   after building, correlate craft↔velocity scores against performance scores
   on the existing corpus. If |r| is high (say > 0.6), the axis is measuring
   intensity again and needs redesign (or honest reporting as a facet of it).
   Consider also whether the "move fast" sentences should come *out* of the
   performance pool if this axis takes over that concept.
2. **Circularity.** "Move fast and break things" is literally Meta's motto;
   "bias for action" is an Amazon Leadership Principle; "ship it" is
   GitHub-coded. Same trap as the Palantir/dei_stance rebuild — candidate
   sentences must paraphrase the *concept* without lifting any company's
   vocabulary. Expect circularity flags on Meta/Amazon and verify the check
   catches them.
3. **Register scope.** Craft talk may live more in culture_values /
   who_we_want chunks than mission_brand. Decide the register slice before
   scoring, not after.

### Candidate pole sketches (to curate, 6–10 each)

- **craft**: "We take the time to build things properly, even when it's
  slower." / "Quality is not negotiable here — we sweat the details others
  skip." / "We build software meant to last for decades." / "Polish and care
  in the small things is how we show respect for our users."
- **velocity**: "We ship quickly, learn from real users, and iterate." /
  "Speed is our advantage — a good decision today beats a perfect one next
  quarter." / "We'd rather launch rough and improve than wait for perfect." /
  "Breaking things occasionally is the cost of moving at our pace."

### Thesis hooks (predictions to register before scoring)

- **Meta's 2014 motto change** ("move fast with stable infrastructure",
  announced at F8 2014) — does the careers copy actually shift, or was the
  motto change PR-only? A within-company before/after test with a known date.
- **Counterforces prediction:** craft language is worker-attracting (autonomy,
  time, standards) — if the thesis holds, it should behave like care/DEI:
  surge with worker leverage, deflate post-2022 as "efficiency era" velocity
  language rises. If instead it's flat like performance, that's an honest and
  interesting null: craft talk is brand identity, not a labor-market lever.
- Basecamp as the fixed anti-velocity pole; Stripe as the craft+intensity
  case that stress-tests the axis separation.

### Steps

1. Draft `axes/candidates/craft.md` (both poles + rationale).
2. Curate into `axes/craft.yaml` + control pairing; build; run circularity.
3. Validate: performance-axis correlation check + spot-read top/bottom scored
   chunks (the usual smell test).
4. Score existing 16-company corpus (no new capture needed — this axis works
   on what's already embedded).
5. Only then decide whether the story needs new companies (§3).

---

## 2. AI language evolution

### Status: designed, deferred — unblock rather than redesign

The verified design from June stands: tuned case-sensitive net (`\bAI\b`,
`\bML\b`, `\bLLM\b`, `\bGPT\b` + CI content terms — loose lowercase matching
gives false positives), robust aggregate finding (≈0–2% of chunks pre-2022 →
~11% in 2026), and the on-thesis finding: **talk-vs-hire balance** (mission ≈
job_listing mentions), the opposite shape from DEI where talk ≫ substance.
Blocker was honest per-company timing: not defensible until the SPA/Wayback
gaps are filled. That's the same gate as the current corpus-fill focus, so
this unblocks itself when capture finishes.

### Extensions beyond mention-counting (the actual story)

1. **AI framing axis** (embedding contrast, same machinery as everything
   else): *AI as tool the worker wields* ("you'll use AI to do your best
   work") ↔ *AI as expectation/substitute* ("AI fluency is a baseline
   requirement", "we ask whether AI can do it before we hire"). The second
   pole is management-side language rising exactly as worker-side language
   recedes — this is the counterforces thesis with AI as the leverage-
   inverting force, which makes it the natural sequel chapter to the
   idealism/DEI/care arc.
2. **Named natural experiments already in the universe:**
   - **Shopify** — Tobi Lütke's April 2025 memo making AI usage a baseline
     expectation ("teams must demonstrate why they cannot get what they want
     done using AI" before asking for headcount). Did careers copy follow?
   - **Salesforce** — "digital labor"/Agentforce era framing vs the Ohana
     years.
   (Verify the exact memo texts/dates during capture — cited from memory.)
3. **who_we_want drift:** when do job listings start *requiring* AI-tool
   experience, and does it displace other requirements?

### Steps

1. Finish the existing corpus-fill worklists (already the active focus).
2. Re-run the tuned mention net; publish the aggregate inflection + talk-vs-
   hire contrast with DEI as the comparison anchor. Caveat the 2026 n.
3. Draft the AI-framing axis through the candidate workflow (hazard: young
   concept, thin pre-2022 corpus by construction — the axis only has ~4 years
   of signal, say so).
4. Decide on AI-native company adds (§3) only if the framing story needs a
   pure-play contrast.

---

## 3. Company adds

Mechanism already exists: per-story allow-lists in `pipeline.yaml`, so new
companies can join *only* the story they serve without joining whole-timeline
studies. Brex lesson applies throughout: young-company thinness is real, not
fixable — a company founded in 2016 can join an AI story (2020+ window) or a
craft story, but never the 2005–2026 arc.

### For craft↔velocity

| Company | Case type | Risk / note |
|---|---|---|
| **Apple** | The canonical craft employer, long history | Highest value add. Check Wayback coverage of jobs.apple.com — likely SPA in recent years, old apple.com/jobs eras may be rich. |
| **Uber** | The canonical hustle case **with a documented values rewrite**: "always be hustlin'"-era norms replaced under Khosrowshahi in late 2017 after the Fowler post | The single best natural experiment available — a dated, forced language change. Founded 2009, so decent runway. Verify old careers URLs. |
| **Figma** | Design-craft identity | Founded 2012, careers copy mostly 2016+. Story-scoped only. |
| **Etsy** | Craft as literal product identity + "keep commerce human" | Mid-2000s founding, real timeline depth, non-pure-tech contrast like Starbucks. |
| **Linear** | The current craft-discourse standard-bearer | Founded 2019 — Brex-grade thinness for anything but a 2020+ window. Only add if the story wants a "craft revival" coda. |

Recommendation: **Uber and Apple first** (both serve the axis *and* deepen the
main universe), Etsy second, Figma/Linear only if the story needs them.

### For AI evolution

| Company | Case type | Risk / note |
|---|---|---|
| **Nvidia** | Old company (1993) transformed by the AI era — the one AI case with a real pre-history | Best structural fit with the longitudinal method. |
| **Duolingo** | "AI-first" announcement (≈May 2025), public backlash, partial walk-back | A language *reversal* to track. Founded 2011, workable depth. |
| **Klarna** | CEO claimed AI replaced hundreds of roles (2024), then publicly re-hired humans (2025) | Sharpest talk-vs-reality case. European company — check Wayback coverage of careers pages. |
| **OpenAI / Anthropic** | Pure-play AI labs | Careers pages young + sui generis; useful as a framing yardstick, weak as longitudinal cases. Lowest priority. |

Recommendation: **Nvidia first**, Duolingo/Klarna as story-scoped reversal
cases. (Verify the Duolingo/Klarna event details during capture — cited from
memory.)

### Process per add (unchanged)

discover → refine url_patterns.json (probe for server-rendered siblings
*before* manual capture — the Amazon/Google lesson) → fetch → extract →
classify → embed → score → export → synthesize. Batch the paid steps.

---

## 4. Other expansion ideas (backlog, roughly ordered)

1. **Wellbeing story page** — dataset exported, page unwritten. Cheapest
   finished-work-to-published-story win on the board.
2. **Remote-work arc** — "remote-first" surge 2020–22 → RTO mandates 2023+.
   Possibly the *cleanest* rented-not-owned case in the whole project: a
   worker-serving benefit granted at peak leverage and revoked on a schedule.
   Could start as a keyword tracker (like AI) before deciding if it earns an
   axis. GitLab (all-remote identity) and Amazon (5-day RTO) are the poles
   and both are already in the universe.
3. **Efficiency-era euphemism register** — "do more with less", "Year of
   Efficiency", layoff-adjacent careers copy 2022–24. Pairs with the AI story
   (same era, same management-side turn).
4. **Founder/shareholder letters as a second corpus** — same companies,
   management-facing register. The worker-facing vs management-facing gap
   *within* a company is a direct counterforces measurement.
5. **GitLab handbook canon study** — already deliberately deferred; the
   16k-word values page as operational (not recruiting) prose. Natural
   companion to the founder-letters idea.
6. **External validation joins** — Glassdoor ratings, layoffs.fyi, the
   existing labor-leverage series extended. Strengthens causal framing
   without overclaiming (correlational, say so).
7. **Per-company page content** for the 10 companies whose exports exist but
   whose pages aren't designed (pipeline.yaml TODO).

---

## 5. Sequencing

```
now ──────────────► corpus fill finishes ──────────────►
[corpus fill (active)]
[craft axis: candidates → build → validate → score]   ← no new capture needed
                    [AI tracker: re-run net + publish aggregate]
                    [adds: Uber, Apple, Nvidia → full pipeline]
                                        [AI framing axis]
                                        [craft story page]
[wellbeing story page — independent, anytime]
```

The craft axis and the wellbeing page are the two workstreams that need
nothing from capture — they can start immediately without splitting focus on
paid re-runs. Everything AI-timing-related stays gated behind corpus fill, as
already decided in June.

## Open questions

- Should the "move fast" sentences migrate out of the performance pool once
  craft↔velocity exists, or stay (accepting the axes share a facet)?
- Is the AI work one story (mentions + framing + natural experiments) or two
  (a short "inflection" piece now, a framing piece after new adds)?
- Universe cap: 16 → ~19-21 with the recommended adds. Each add carries
  permanent re-score/export cost. Is there a number where the universe stops
  growing and story-scoped subsets become the only mechanism?
