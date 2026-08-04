# Pilot memo: Basecamp founder speech vs. the non-political workplace

2026-08-01. Question: Basecamp's April 2021 policy removed "societal and
political discussions" from the workplace
(`data/basecamp/canon/changes_at_basecamp_2021.md`). What did co-founder
DHH publish on his personal blog (world.hey.com/dhh) over the same period,
measured with the project's instruments rather than screenshots? Grew out of
the gender story's Basecamp anomaly (#2 masculine-coded company, attributed
to founder voice). Feeds `posts/non-political-workplace.md`.

**Claim discipline** (governs everything below): counts + verbatim quotes +
dates. No motive attribution, no "hypocrisy" framing. The disanalogy is
stated up front: a workplace-speech policy is not a promise of founder
silence — Fried's memo never pledged that. All LLM-coded numbers are
**pre-validation** until the hand-label gate below passes.

## Corpus census

- **512 posts**, March 2021 → July 2026, all dated, fetched live (0 Wayback
  fallbacks) via the new `hey_world` source (`data/dhh_blog/`, case corpus,
  NOT in pipeline.yaml). Raw cache with `fetched_at` on every post is the
  evidence record; DHH edits/deletes, so quotes cite capture date.
- Posts/year: 2021: 72 · 2022: 115 · 2023: 115 · 2024: 102 · 2025: 86 ·
  2026: 22 (through Jul). Chunk corpus: 5,485 paragraphs.
- Known gaps: posts deleted before 2026-08-01 are invisible (CDX sweep is a
  flagged follow-up); date parser initially missed 156 posts (HEY pads
  single-digit days) — fixed and refetched, all 512 now dated.
- High near-dup drop rate in the chunk layer (e.g. 851 dropped in 2023) is
  unexplained — investigate before trusting chunk-level counts; the
  group-reference instrument reads full post text and is unaffected.

## Instruments

Three independent instruments, reported side by side; divergence gets
investigated, not averaged.

1. **Group-reference extractor** (`prompts/group_references.yaml` v1,
   claude-sonnet-4-5-20250929, one post per request): extracts references to
   marginalized groups (9 group codes) and codes the frame (neutral_mention /
   sympathetic_defense / policy_critique / threat_crime_framing). Guards:
   100% machine quote-containment check (4 extractions dropped), taxonomy
   validation (0 dropped), refusal log (69 initial → 6 after reinforced
   retry; all 6 are tech posts with zero group terms by regex scan —
   treated as no-reference pending hand confirmation).
2. **Regex lexicon** (`analyze_dhh_contrast.py`): transparent term counts,
   the sanity anchor.
3. **Embedding probes** (`track_group_concepts.py`, exclusion-pilot method):
   8 concepts, hits ≥ 0.5 per year.

## Findings (pre-validation)

### The trajectory

**Unit = the post, not the passage.** The model's passage segmentation is
arbitrary (it split one post into six near-identical threat entries), so each
post collapses to one worst frame per group, and every count below is posts.
A post's frame is its most-hostile frame present ("worst frame"). Raw passage
count is retained only as a secondary field (`nMentions`), never a headline.

| year | posts | posts w/ ref | migrant posts | threat-framed posts |
|---|---|---|---|---|
| 2021 | 72 | **0** | 0 | 0 |
| 2022 | 115 | 8 | 2 | 0 |
| 2023 | 115 | 4 | 1 | 0 |
| 2024 | 102 | 9 | 3 | 2 (22%) |
| 2025 | 86 | 15 | 8 | 9 (60%) |
| 2026 | 22 | 4 | 2 | **4 (100%)** |

Three separate movements: volume rises (0 → 15 referencing posts/year against
a *shrinking* denominator), migrants become the dominant subject (2 → 8
posts, 2022→2025; Roma appear only in 2026), and the frame flips — no post
frames a group as a threat through 2023, then the share of referencing posts
that are threat-framed runs 22% → 60% → 100% across 2024–2026.

Convergence: the regex lexicon independently shows migration terms jumping
to 9 posts in 2025 (2–3/yr before) and roma/deportation terms 2026-only.
Embedding probes concentrate in the same 2025–26 posts (deportation_removal
max-sim 0.85 on the wolves post). All three instruments agree on shape.

### Anchor quotes (verbatim, machine-checked, capture 2026-08-01)

- First threat-framed post, 2024-01-04 ("The reality of the Danish
  fairytale"): Sweden "went with an open-door policy on immigration for far
  longer, ended up taking many more (about 3x Denmark)..."
- 2026-06-17 ("The Rape of Britain"): "industrial-scale sexual atrocities
  committed by predominantly Pakistani Muslims against mostly White British
  girls..."
- 2026-07-16 ("Three sacred cows that must die so Europe can live"):
  "millions who are already in Europe must go. Remigration has gone from a
  fringe concept to the mainstream discourse..." — "remigration" is an
  identitarian-movement term; its appearance is datable to this post.
- 2026-07-21 ("Wolves, sheep, and gypsies"): "When wolves get out of
  control, you shoot them. When gypsies take over public spaces, you deport
  them."
- Contrast, 2023-03-30 (coded sympathetic, about the US): "by far and away
  the most welcoming, open, and integratable country I've ever spent serious
  time in."

### Off-label instrument results (validated on careers copy, not blog prose)

- **Gender axis** (frozen story baseline): blog pooled meanZ **+0.618**
  (57.1% masc / 4.6% fem, n=16,738 sentences) — *above* Basecamp careers
  (+0.562, rank #2/23), between Basecamp and Anduril (+0.769). Flat across
  years (0.57–0.66): the register was masculine-coded from month one; the
  *content* is what escalated. Direct evidence on the gender story's
  house-voice question.
- **DEI stance classifier** (5,485 chunks): 5,221 neutral ·
  234 mission_focus_apolitical · 29 civilizational_mission · 1 affirming_dei.
  Two-phase structure: mission_focus_apolitical peaks 2021–22 (34, 100 —
  the blog defending the no-politics decision), civilizational_mission is
  2025–26 (1 → 14 → 14 — explicit-West framing arriving exactly when the
  group-reference frames flip to threat). Independent dating of the same
  shift by an instrument built for a different corpus. Contrast: basecamp
  careers chunks are 100% neutral on this axis.

### The company-side contrast (read from existing artifacts, not recomputed)

Basecamp careers corpus: DEI stances all-neutral, inclusion rank 18,
altruism 20/20 flat. The policy held on company surfaces; the political
speech lives entirely on the founder's platform.

## Validation gate (OPEN — Becca)

**Post-level validation** (matches the post-level unit): each labeled post
reduces to a set of (group → worst frame). Comparison is post-level, not
passage pair-matching — the model's passage segmentation is not something a
human can reproduce, so validating it is neither possible nor needed.

- `data/dhh_blog/labels/group_ref_sample.csv`: 60 posts, blind (census of
  all 40 flagged + 20 unflagged recall check, shuffled, predictions
  withheld). Per post fill `has_reference` (y/n) and `pairs`
  (`group:frame; group:frame` — one frame per group, the worst present),
  then `uv run scripts/report_group_ref_agreement.py --case dhh_blog`.
- **Pre-registered thresholds**: post-level detection α ≥ 0.8; group
  presence (post,group) F1 with α ≥ 0.8 equivalent; worst-frame agreement
  given an agreed group ≥ 0.7; recall misses ≤ 1/20. Below threshold →
  revise prompt, re-run, **fresh sample** (never report α from the sample
  the prompt was tuned on).
- **Known open rubric question (blocks a clean run):** the
  `policy_critique` vs `threat_crime_framing` boundary is contested and the
  model applies it inconsistently (over-calls threat on passages describing
  *hostility toward* a group, e.g. "Danish hostility to foreigners"). The
  first 8 hand-labels became rubric-development examples (no longer blind
  once predictions were shown). Resolve in prompt v2 or by collapsing the
  two into one "hostile" frame, THEN draw a fresh blind sample.
- Hand-confirm the 6 refusal posts as no-reference (term-scan says yes).

## Go/no-go for publishing the post's corpus section (pre-registered)

**GO** if: validation passes AND ≥15 referencing posts post-April-2021
survive hand-labeling. Current pre-validation count is 40, so the margin is
wide, but the number that publishes is the post-validation number.
**NO-GO** → this memo is the terminal artifact and the post's corpus section
shrinks to hand-verified quotes only.

## Limitations (also for the post)

Single blog, single founder — nothing here generalizes beyond DHH without
building the Lütke/Armstrong capture (proposed, not built). Off-label
instruments as flagged. Deleted posts invisible. Single hand-labeler.
LLM coder + refusal retries on charged text: the direction of any residual
bias is unknown; the quote-containment check bounds hallucination but not
frame-coding error — that's what the hand-label gate measures.

**Known frame-target ambiguity** (found 2026-08-01 while cross-checking a
community-sourced timeline): the extractor coded the Graham Linehan arrest
passage (as-i-remember-london, 2025-09-15) as trans_people /
sympathetic_defense — but the sympathy is directed at Linehan (an anti-trans
figure), not at trans people. "Sympathetic toward whom" is underspecified in
prompt v1; watch for this class of error in the hand-label pass and fix in
v2 if it recurs.

**External cross-check**: a community timeline (r/rails, shared by Becca
2026-08-01) cites five specific HEY posts; all five exist in our capture
with matching dates, and its strongest claim ("demographic replacement",
Sept 2025) is confirmed verbatim by our extraction. Its 2022 "anti-woke
phase" posts contain zero group references — independently consistent with
our two-phase stance finding (apolitical-defense peak 2022, civilizational
2025-26). Its psychological narrative (grievance, Andreessen influence) is
NOT corpus-checkable and stays out of our claims. Pre-2021 baseline now
anchored by The Politic interview (2020-02-16, wealth-tax/oligarchy quotes
verified): the corpus's own economic vocabulary declines 33→7 mentions
2021→2025, then flips valence ("Denmark desperately needs more inequality",
2026-03-23).

## Story-phase sketch (later, not this pilot)

Exporter modeled on `export_gender_story.py` → frame-composition-by-year
chart + the company/founder contrast panel; MDX in
`astro/src/content/stories/`. Only after the validation gate and Becca's
read of the full flagged set.
