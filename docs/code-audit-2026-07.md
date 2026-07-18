# Code audit — quality, repetition, naming, dead code (2026-07-17)

Three sweeps (duplication, naming accuracy, unused code) plus git housekeeping,
consolidated and ranked. Items marked ✓ were independently re-verified, not
just reported.

**Status 2026-07-17 (same day):** sections 1–3 applied in full, §4 items 1–8
applied, plus the validate.py rename (to `validate_altruism_axes.py`) and full
Menlo corpus/reference removal. Note: score_axes.py turned out to be the real
untruncated quote producer (the ~8 scorer copies attribution below was partly
wrong) — fixed there too, so evidence_quotes.json text will cap at 400 chars
on the next score run. Still open: §5 larger refactors, the `"dei"` label-set
key rename in embed_chunks/pipeline, and the export_ai_web manifest question
(checked: astro derives axes from data files, so not a live bug).

---

## 1. Fix soon — duplicates that have ALREADY drifted (behavioral differences)

These are the only findings where the code currently does two different things
that were meant to be the same.

1. ✓ **Evidence-quote truncation.** Every scorer builds quote dicts as
   `{"text": str(row["text"])[:400], ...}` — except
   [score_altruism_split.py:85,90](../scripts/score_altruism_split.py#L85),
   which emits **untruncated** text. ~8 copies of the same dict shape across
   `score_performance/score_dei/score_dei_stance/score_ai_language/score_axes/score_altruism_split`.
   Fix: one `quote_dict(row, score, *, max_chars=400)` helper in `lowork.io`.
2. ✓ **Wellbeing mental-health regex net.** `_WB_MH` in
   [export_story_web.py:868-869](../scripts/export_story_web.py#L868) includes
   `burnout`; the parallel `mental_health` net in
   [track_benefits.py:30-38](../scripts/track_benefits.py#L30) does not. A term
   added to one detector silently never reaches the other view. (The
   fertility split in track_benefits is purpose-driven — keep it.) Fix: shared
   alternation constants.
3. **`load_hand_labels` — three divergent copies.**
   [classify_chunks.py:24](../scripts/classify_chunks.py#L24) (hardcoded
   path/column) vs [classify_dei_register.py:27](../scripts/classify_dei_register.py#L27)
   (different hardcoded path/column) vs
   [report_dei_agreement.py:46](../scripts/report_dei_agreement.py#L46) (already
   the general `(sample, column)` form). Fix: promote the parameterized one to
   `lowork.io`.

## 2. Fix soon — actively misleading names/docs

1. ✓ **`validate.py` name collision.** [scripts/validate_altruism_axes.py](../scripts/validate_altruism_axes.py)
   docstring says "Step 8: validation", but it is not a DAG stage at all — and
   `scripts/pipeline.py validate` is a *different* tool (config/coverage
   assertions in `src/lowork/pipeline.py::validate`). A newcomer running
   `pipeline.py validate` expecting the tournament gets the wrong thing.
   Suggest renaming the script (e.g. `validate_axes.py` or
   `validation_report.py`) and fixing the docstring.
2. ✓ **"Next.js frontend" ×3.** Docstrings of
   [export_web.py:2](../scripts/export_web.py#L2),
   [export_dei_web.py:2](../scripts/export_dei_web.py#L2),
   [export_story_web.py:2](../scripts/export_story_web.py#L2) claim Next.js;
   the frontend is Astro (README says so). (`chunking.py`'s `__NEXT_DATA__`
   mention is about scraped sites — correct, leave it.)
3. **"wellbeing has no story page yet" is false.** `pipeline.yaml` stories
   comment + `src/lowork/pipeline.py:238-239` — but
   `astro/src/content/stories/wellbeing.mdx` is published ("The Care That
   Survived"). The similar `ai: no story page yet` comment is borderline
   (craft-ai.mdx serves the ai axis).
4. **README drift (public-facing, worth a pass):** says "~11 tech companies"
   (pipeline.yaml has 19); the "full cohort" roster is the pre-expansion
   11-company list including Brex (not in pipeline.yaml); story list names a
   phantom "culture-fit" story and omits the real wellbeing + craft-ai;
   "each with a neutral control axis" overstates (one `control` axis, used
   only for altruism).
5. **Stale "Step N" docstring scheme.** ~9 scripts carry step numbers matching
   neither the DAG (unnumbered) nor the README's 0–17 table — including an
   internal contradiction (`build_axes` "Step 4b/6" vs `embed_chunks` "Step 5",
   though embed must precede build). Suggest deleting step numbers from
   docstrings entirely and letting README + STAGES be the only ordering.
6. **Misnamed general-purpose things:** `embed_chunks.py`'s
   `DEI_ANALYSIS_LABELS` / `"dei"` label-set key is now the universal analysis
   corpus, not DEI-specific; `export_web.py` is actually the *altruism* story
   exporter (one of 6+ `export_*` scripts) and also computes the fingerprint,
   overlapping conceptually with `export_fingerprints.py`.
7. **Menlo H3/H5 references** linger in `src/lowork/sources/wayback_url.py:4,14`
   and `scripts/fetch_case.py:151` — hypotheses from the pre-pivot study.

## 3. Dead code — safe deletions (verified: zero references repo-wide)

**Orphan scripts** (no importer, no STAGES entry, no README/docs/yaml/astro
reference; date = last touch):

| Script | Last touch | Note |
|---|---|---|
| `scripts/clean_manual_html.py` | 2026-06-27 | superseded by ingest_manual_html flow |
| `scripts/gen_manual_todo.py` | 2026-06-26 | older manual-capture workflow |
| `scripts/explore_sources.py` | 2026-06-24 | Menlo explorer (story removed 06-29) |
| `scripts/fetch_filings.py` | 2026-06-10 | zero references anywhere |
| `scripts/track_netflix_evolution.py` | 2026-06-26 | superseded by track_culture_propagation |
| `scripts/validate_dei.py` | 2026-06-10 | superseded by validate_altruism_axes.py + report_dei_agreement |

**Dead symbols:** `lowork/ai_net.py::has_ai_mention` (live one is
`find_ai_terms`); `lowork/wayback.py::representative_capture`; ✓
`config.py:17 DOCS_DIR`. **Dead-import clusters:** `recover_spa.py` (`json`,
`Counter`); stale `ROOT` import copied across all three `export_*_web.py`.

**Git housekeeping (259 MB):** `.claude/worktrees/agent-a1e72c3d9ee29d84c` is a
leftover agent worktree — branch fully merged into main, clean tree. Branches
`astro-phase4-cutover` and `netflix-lineage-echoes` are also fully merged.
`git worktree remove` + `git branch -d` all three.

**Deleted-feature check (clean):** the P3 canon/on_topic/junk classifier
removal left no dangling imports; remaining "canon" strings are the live
canon-corpus concept.

## 4. Consolidation backlog — identical today, drift would be a bug

Ordered by blast radius:

1. **`ANALYSIS_LABELS = {"mission_brand","benefits_perks"}` — 11 copies**
   (lib pipeline.py + 9 scripts + embed_chunks' renamed `DEI_ANALYSIS_LABELS`).
   This is the gate deciding which chunks feed every analysis; one divergent
   copy silently forks the corpus. → single `lowork.config.ANALYSIS_LABELS`.
2. **`load_pole_vector`/`load_axis_vector` — 6 named + 5 inline copies** of the
   same 3-line built-axis loader; the name has already forked. →
   `lowork.axes.load_built_vector(name)`.
3. **`CONTENT_LABELS` (5-label AI gate) — 2 copies** in track_ai_mentions +
   score_ai_language. Deliberately wider than ANALYSIS_LABELS — consolidate the
   pair only, do not merge the two sets.
4. **`ACTIVE_DEI_REGISTERS`** — canonical in `lowork.dei`, reimplemented in
   export_story_web.py:25-30 and export_power_story.py:82 (score_dei already
   imports it correctly). → import in both exporters.
5. **`BENEFITS_LABELS = {"benefits_perks","job_listing"}`** — same set under 4
   names across 4 scripts. → one config constant.
6. **Manifest updater** — `export_web.update_companies_manifest` vs
   `export_dei_web.update_manifest`, ~90% identical. → shared helper taking
   `axes_to_add`. Side-finding: **export_ai_web writes no manifest entry at
   all** — check whether that's a bug.
7. **Locus review values** — identical 4-value list in make_locus_review /
   verify_locus_alpha (the 3- and 2-value LOCI elsewhere are purpose-different;
   leave those).
8. **`is_english` ×2** — `lowork/langgate.py` (used only by extract_chunks) vs
   `lowork/text_filter.py` (used by everything else). Two same-named
   implementations; pick one.

## 5. Larger refactors — optional, structural

- **`score_*.py` family:** all six share the load→filter→groupby(year)→
  project+topk_mean→rows+evidence→parquet+json skeleton (~50% shared shape).
  A `lowork.axes.aggregate_by_year(...)` helper would shrink each script to its
  axis-specific logic. Worth doing next time one of them changes, not before.
- **LLM call plumbing:** 7 bespoke Anthropic call/parse loops; the
  code-fence-strip idiom is copy-pasted 4× (classify.py, dei.py, dei_stance.py,
  synthesize_company.py). A `lowork.llm.call_json(...)` would also be the
  natural home for the structured-output fix in the synthesize-company memory.
- **Agreement reports:** report_chunk_agreement.py is the unparameterized ~70%
  twin of report_dei_agreement.py — fold in as a third `--task`.
- **argparse boilerplate** (`--company default="google"` ×20) — cosmetic; skip.

## 6. Checked, deliberately not flagged

- `fetch_power_proxies.py` — alive (feeds export_power_story stage).
- `score_axes.py` `register`/`exclude_subtype` params — dead for the current
  corpus but the manual escape hatch for the dormant Menlo/Automattic study;
  keep while that study is dormant-not-deleted.
- `relabel.py::apply_relabel_heuristics` — alive only via relabel_locus_sample
  (docs-referenced); dies if that script goes.
- Wellbeing/analysis one-off scripts (analyze_wellbeing, verify_locus_alpha,
  mine_gitlab_flow, …) — unwired but referenced by execution docs; not orphans.
- The `*_story.py` narrative exporters are genuinely one-off; not worth merging.
