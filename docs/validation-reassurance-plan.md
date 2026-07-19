# Validation Reassurance Plan — post-hand-labeling

Follow-on to the validation overhaul. That workstream measured classifier
agreement; this one closes the remaining "we think it's right" gaps in
categorization that no α number covers.
**Hand-labeling is DONE (2026-07-18; the labeling-todo checklist is retired —
gate reads live in [execution-log.md](execution-log.md)):** chunk labels
460/460, blind pooled α 0.759 7-way / 0.805 analysis view; stance sample
100/100 fully verified, blind α 0.932 / adjudicated 1.0 (cite the blind number;
standing qualifier: 37 rows were AI-prefilled before Becca verified them).

Instrument change 2026-07-18: the bipolar `dei_stance` embedding axis and the
inclusion−meritocracy `stance_diff` were **retired** (output was unconsumed;
merit-intensity is not a DEI position — Becca's ruling). Direction claims now
rest solely on the stance classifier, so the Phase 0 stance gate below is the
only validation the DEI story's direction claims depend on; no dei_stance
tournament is needed in Phase 1.

Each step is **command → artifact → gate → branch**. Gate reads are recorded in
[execution-log.md](execution-log.md) with timestamp, artifact path, and
decision — recorded, not remembered.

Scope discipline: phases 2–4 are hour-scale hand audits, not new systems. The
deliverable of each is a *citable number* (precision, recall, agreement) plus
any caveat language it forces. Nothing here builds new pipeline machinery
except the tournament parameterization in Phase 1.

---

## Phase 0 — CLOSED 2026-07-19 (all three gates passed; reads in execution-log.md)

1. ~~Chunk agreement~~ **PASSED**: `report_chunk_agreement.py` → blind pooled α
   0.759 7-way / 0.805 analysis view (n=440); gold set adjudicated clean.
2. ~~Stance agreement~~ **PASSED**: `report_dei_agreement.py --task stance` →
   blind α 0.932 / acc 0.96 (n=100), adjudicated α 1.0. Note: this validates
   the migrated stance data; the classifier-under-new-prompt α comes from
   re-running the report after step 3's stance re-classify.
3. ~~Batched API re-classify~~ **PASSED 2026-07-19**: full-corpus register +
   stance re-classify under the current prompts (all 19 companies, 4,694
   analysis chunks each task). Classifier-under-current-prompt numbers:
   register pooled α **0.802** / acc 0.876 (n=201); stance pooled α **0.877** /
   acc 0.93 (n=100). Both clear the α ≥ 0.80 gate. Stance misses are
   one-directional (classifier under-detects mission_focus_apolitical, recall
   14/20) — counter-stance counts in the story are floors, stated as such.

## Phase 1 — Extend the LLM tournament beyond altruism (the only code phase)

The pairwise-tournament cross-check in [validate_axes.py](../scripts/validate_axes.py)
(`tournament`, `embedding_vs_llm`, `early_year_agreement`) hardcodes
`"altruism"`. `quotes_text()` already takes an axis parameter and
`evidence_quotes.json` already contains quotes for **all nine scored axes**, so
this is parameter-threading, not new machinery.

Build:

- Add an `AXIS_TOURNAMENTS` table to validate_axes.py: `{axis: question_text}`.
  Each axis needs its own `TOURNAMENT_QUESTION` phrasing (the judge question
  must name the concept without leaking the axis's pole phrases — same
  circularity discipline as axis construction). Start with:
  - `performance` — "which set expresses more high-performance / up-or-out
    intensity" (backs the Netflix story).
  - `craft` — newest axis, M5/M6 still open, no human check yet.
  - Optionally `control` (it partners altruism in the ground-truth decoupling
    check, so a direct ranking check is nearly free).
- Parameterize `tournament(quotes, years, axis, question, ...)`,
  `embedding_vs_llm(..., axis)`, `early_year_agreement(..., axis)`. Leave
  `ground_truth_check` and `perturbation_check` altruism-only — their expected-
  peak hypotheses don't transfer.
- Extend `validation.json` / `validation_report.md` with a per-axis tournament
  section; keep the existing altruism output shape unchanged (M6 review gate
  reads it).
- Cost control: `JUDGE_MODEL` (Sonnet) at ~n_pairs calls per axis per company,
  max_tokens=5 — cheap, but run per-company deliberately, not in a loop over
  the universe. Mind the spend cap; surface any API limit error rather than
  degrading silently.

Run: Google + Netflix first (largest corpus; the published story), then any
company whose story cites the axis.

**Artifact:** per-company `validation_report.md` §2 with per-axis Spearman.
**Gate:** embedding-vs-LLM Spearman ≥ 0.6 per axis (altruism's existing
informal bar).
**Branch:** below 0.6 → inspect the tournament judgments (they're logged) to
see *which years* disagree; a low score localized to thin years is a caveat, a
broad disagreement means the axis ranking shouldn't be presented as a trend
without hedging. Disagreements are case studies, not silent overrides.

## Phase 2 — Culture-propagation precision pass (hand audit)

The adoption timeline in `data/culture_propagation.json` currently has **13
entries**; the review file marks only top-N matches per concept. Close the
loop:

- Extend [track_culture_propagation.py](../scripts/track_culture_propagation.py)'s
  review output (or a one-off CSV) so **every match that enters the timeline**
  — including the paraphrase band between `threshold` (0.64) and
  `verbatimThreshold` — gets a hand verdict column: expresses the concept
  yes/no.
- Becca verdicts all 13 (minutes, not hours). Compute precision overall and
  for the paraphrase band separately — the Coinbase ~0.565-0.59 lines are the
  ones the "verbatim disciple" claim leans on.
- False-negative eyeball: re-read the review file's *below*-threshold rows
  (e.g. Stripe keeper-test-flavored lines at ~0.48) and note any real borrows
  the threshold misses. Misses understate propagation — that's a caveat for
  the story, not a threshold change (don't retune the threshold to chase
  individual lines).

**Artifact:** `data/culture_propagation_verdicts.csv` + precision numbers
appended to `data/culture_propagation_review.md`.
**Gate:** paraphrase-band precision ≥ 0.8.
**Branch:** below → either raise `threshold` (re-run, re-verdict) or demote
paraphrase-band matches to a "possible echo" tier in the story/export; the
Netflix-story propagation section states the precision number either way.

## Phase 3 — Wellbeing extraction recall audit (hand audit)

`verify_locus_alpha.py` isolates codebook reliability *from* extraction recall
by design — so recall is unmeasured: nobody has checked the extractor finds
all benefits in a chunk, only that it labels found ones consistently.

- Sample ~20 benefits-bearing chunks stratified across companies/years
  (reuse the sampling pattern from `make_locus_review.py`; seed pinned).
- Becca reads each chunk and enumerates every benefit item she sees (category
  + verbatim span), *before* looking at extractor output.
- Compare to `extract_benefits` output for the same chunks: recall = hand
  items matched by the extractor / hand items total (match on category +
  overlapping span; the `verbatim` field exists exactly for this).

**Artifact:** `data/wellbeing_recall_audit.csv` + recall number in
`docs/wellbeing-analysis-plan.md`'s caveats section.
**Gate:** recall ≥ 0.85.
**Branch:** below → characterize what's missed (a category? terse
list-formatted items?) and either fix the extraction prompt and re-run the
audit, or state the recall number as a coverage caveat on the wellbeing
findings (enumeration counts are floors, not totals).

## Phase 4 — Threshold spot-checks (two small hand audits)

**4a. `PRESENCE_THRESHOLD = 0.25`** in
[score_performance.py](../scripts/score_performance.py) — single-pole raw
cosine, so this constant *is* the present/absent call, and the Netflix story's
claim-vs-metric contrast sits on it.

- Sample ~15 chunks just above the threshold (0.25–0.35) and ~15 just below
  (0.15–0.25); Becca marks each: does it actually contain performance-intensity
  language?
- **Artifact:** `data/performance_threshold_audit.csv` with agreement rate per
  side. **Gate:** ≥ 0.8 both sides. **Branch:** poor separation → report
  scores as a continuous intensity (drop the present/absent framing) rather
  than tuning the constant to the audit sample.

**4b. ai_tool_mandate direction check** — n is low double digits per company,
so this is a full read, not a sample.

- Dump every gated chunk with its projection sign from
  `ai_language_scores.parquet` / `ai_evidence.json`; Becca marks each: does a
  positive chunk read as "AI as tool for employees" and negative as "AI use as
  mandate/expectation"?
- **Artifact:** `data/ai_direction_audit.csv` + agreement rate.
  **Gate:** ≥ 0.8 directional agreement. **Branch:** below → the axis poles
  need rework before the craft-ai story leans on direction (prevalence claims
  from `track_ai_mentions.py` are regex-based and unaffected).

---

## Sequencing & effort

| Phase | Depends on | Becca's time | Code time |
|---|---|---|---|
| 0 | hand labels done | — (labels already counted) | none (scripts exist) |
| 1 | 0 (re-classified corpus) | review reports | half a day |
| 2 | — | ~30 min verdicts | small review-output tweak |
| 3 | — | ~1–2 h reading | small audit script |
| 4a/4b | — | ~1 h total | tiny dump scripts |

Phases 2–4 are independent of each other and of Phase 1; only Phase 0 → 1 is
ordered (validate the corpus we keep). If time is short, priority is
0 → 1(performance) → 2 → 3 → 4 — ordered by how much published-story weight
rests on each.

The payoff, stated plainly: after this plan every categorical claim in a
published story is backed by either an agreement coefficient or a hand-audited
precision/recall number, and every place we fall short has a stated caveat
instead of silence.
