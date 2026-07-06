# Well-Being Study — Execution Plan

Companion to [wellbeing-analysis-plan.md](wellbeing-analysis-plan.md). That doc is the *why/what* (hypotheses, instruments, methods). This is the *how*: real files, commands, artifacts, and the gates that decide whether we proceed. Each step is written as **command → artifact → gate → branch**.

This document is a plan, not an execution log. Nothing here has been run yet. **Execution state lives in `docs/execution-log.md`** (net-new): every gate read must be recorded there as a timestamped entry with the artifact path and the decision taken (proceed / branch). Gate decisions are recorded, not remembered.

---

## 0. Reconciliation decisions (pin these before touching code)

The repo already has partial machinery. To stay executable (not build parallel systems), these are fixed up front:

| Plan element | Existing asset | Decision |
|---|---|---|
| Care ↔ intensity rhetoric axis | [`axes/wellbeing.yaml`](../axes/wellbeing.yaml) — already the exact axis; already in `FINGERPRINT_AXES`, scored to `data/<co>/axis_scores.parquet` | **Reuse as-is.** Do not rebuild. Only *one* new axis is needed. |
| Individual ↔ structural locus rhetoric axis | none | **New:** `axes/wellbeing_locus.yaml`, built/scored via the existing axis path. |
| Benefits enumeration | [`scripts/track_benefits.py`](../scripts/track_benefits.py) — keyword multi-label, emits `stories/benefits.json` | **Do not extend it.** It stays as the `benefits` story. Write a *new* LLM-extraction module for the well-being taxonomy (category+locus+specificity), because keyword matching can't assign locus/specificity. |
| Story slot | `wellbeing: true` in [`pipeline.yaml`](../pipeline.yaml) — dataset exported, no page; `export_story_wellbeing` stage exists | **Land here.** Extend `stories/wellbeing.json` and write `wellbeing.mdx`. Keep `benefits` story separate. |
| Model calls | `classify.py` / `dei_stance.py` use temp-0 **JSON-array-in-text**, enum-validated. No tool-use anywhere in repo. | **Introduce tool-use structured output for benefits extraction only** (one chunk → N items, each a nested object — JSON-in-text is exactly the malformed-JSON failure mode in the `synthesize_company` memory). Axis/register classifiers keep the existing pattern. |
| Leverage series (JOLTS quits) | [`scripts/fetch_power_proxies.py`](../scripts/fetch_power_proxies.py) → `data/power_proxies.json` (FRED JTSQUR, annual) | **Reuse.** For lag correlation we may need *quarterly* quits — add a quarterly variant to that script rather than a new fetcher. |
| Changepoint / survival stats | none; `scipy>=1.14` present, **`ruptures` and `lifelines` absent** | **New dependency step** (§Phase 4). |
| GitLab flow (git-history + MR API) | only the careers-page corpus in `data/gitlab/`; **no git-log/MR code; handbook repo not cloned** | **Entirely net-new, and a separable track** (§GitLab). Must not block the corpus study. |

Models are pinned in [`src/lowork/config.py`](../src/lowork/config.py): `CLASSIFIER_MODEL`/`REGISTER_MODEL` = Haiku 4.5, `JUDGE_MODEL` = Sonnet 4.5, `EMBEDDING_MODEL` = text-embedding-3-large (3072-d), `TOP_K = 5`. Reuse; don't re-pin.

---

## Net-new components (the build surface)

1. `axes/wellbeing_locus.yaml` — second rhetoric axis (generic poles, circularity-checked).
2. `src/lowork/benefits_extract.py` + `scripts/extract_wellbeing_benefits.py` — tool-use taxonomy extraction (category/locus/specificity), per-item.
3. `data/<co>/wellbeing_observations.parquet` — three-state observation ledger (see Phase 3); the §0.1 coverage audit is its first producer.
4. `data/layoff_events.json` — hand-curated layoff dates (`company`, `announce_date`, `approx_headcount_pct`, `source_url`); prerequisite input for P4.5 event studies only.
5. `src/lowork/wellbeing_stats.py` + `scripts/analyze_wellbeing.py` — changepoints, lag test, substitution tests, survival, event studies, JOLTS overlay.
6. GitLab flow track: `scripts/mine_gitlab_flow.py` (git log across repo migration) + `scripts/fetch_gitlab_mrs.py` (API) + coding module.
7. `astro/src/content/stories/wellbeing.mdx` + charts (`.tsx`) + `viz/*.astro` wrappers.
8. `docs/execution-log.md` — timestamped gate-decision ledger (see header).
9. New pipeline `Stage` entries in [`src/lowork/pipeline.py`](../src/lowork/pipeline.py) (`STAGES`, ~L108–247), tagged `("wellbeing",)`, with declared `inputs`/`outputs` so the fingerprint engine tracks them.

---

## Phase 0 — Feasibility gate (FIRST executable step; has a real branch)

**0.1 Benefits-page Wayback coverage audit.**
- Command: new `scripts/audit_wellbeing_coverage.py` — for each company, count Wayback snapshots per year that hit benefits/careers subpages (reuse `lowork/wayback.py` CDX + the `snapshots.json` already in each `data/<co>/`).
- Artifact: this audit is the **first producer of `data/<co>/wellbeing_observations.parquet`** (the three-state ledger defined in Phase 3), not a standalone appendix table. It writes the fetch_status/observed rows for the benefits/careers pages; the coverage table is derived from that ledger.
- **Gate definition (pinned now, before the script exists):** a company is **"usable"** = ≥1 successful benefits-page snapshot in ≥4 distinct years, with at least one observation on each side of **2022-01-01**. **Gate: ≥8 of 16 companies usable.**
- **Branch:** if <8 usable → **redesign around HN "Who's Hiring" postings** as the enumeration source. The `lowork/sources/hn.py` fetcher + `fetch_case.py` "diverge at fetch, converge at chunk" system already exists — enumeration then reads job-posting chunks instead of benefits pages. Everything downstream is unchanged.

**0.2 GitLab flow feasibility (parallel, non-blocking).**
- Clone both handbook repos locally to a scratch path (not committed): **`gitlab-com/content-sites/handbook`** (post-2023 history) and the archived **`gitlab-com/www-gitlab-com`** (pre-migration history). Both are large — use `git clone --filter=blob:none` plus sparse-checkout limited to handbook content paths only: `total-rewards/benefits`, `company/family-and-friends-day`, `values`.
- Confirm well-being path history is mineable across the www-gitlab-com → handbook migration; confirm MR descriptions are retrievable via the GitLab API (public, token-optional for a public project — verify rate limits).
- **VERIFIED 2026-07-06 (see execution-log):** `git log --follow` does **not** span the migration — history disconnects at the 2023-12-22 seam (`7cf94138a9c` "Remove all the old handbook content"), plus an internal ~2020-06 reorg (`source/handbook/`→`sites/handbook/source/handbook/`) and F&F under a third prefix. **Method is therefore: mine each repo/era separately from pre-seam anchor commits and stitch by path+date at the analysis layer.** Confirmed paths — pre-2023 www-gitlab-com: `sites/handbook/source/handbook/total-rewards/benefits/`, F&F `sites/uncategorized/source/company/family-and-friends-day/`; post-2023 handbook (project `42817607`): `content/handbook/total-rewards/benefits/`, F&F `content/handbook/company/family-and-friends-day.md`. MR API works unauthenticated (500 req/period; use a token for the full mine).
- **Gate:** MR descriptions retrievable AND path history mineable per-era. **PASSED.**
- **Branch:** if not → GitLab track degrades to commit-message-only rationale coding (still runs; §Rationale asymmetry loses the word-count-of-MR-body signal, keeps commit-body). **This never blocks Phases 1–4 on the corpus.**

---

## Phase 1 — Instruments

**1.1 Second rhetoric axis.** Author `axes/wellbeing_locus.yaml` (pole_a = individual-locus: "resources to help you manage stress", "your well-being journey"; pole_b = structural-locus). **Author structural-pole sentences in phrasings not lifted from any corpus company** — "company-wide closure" is near-verbatim GitLab F&F copy and GitLab is in the corpus, so it is disqualified. Use generic-concept paraphrases (e.g. "we adjust staffing so people can genuinely unplug", "the organization absorbs the load rather than the individual"). Run `scripts/build_axes.py` → `axes/built/wellbeing_locus.json`; **`lowork/axes.circularity_check` must pass against the full corpus before the axis is accepted** (no verbatim n-gram overlap with any measured firm — same discipline as the `dei_stance` Palantir/Coinbase fixes). Add to `FINGERPRINT_AXES` or give it a dedicated scorer modeled on `scripts/score_dei_stance.py`.

**1.2 Benefits taxonomy + locus codebook.** Encode the taxonomy from analysis-plan §Benefits as a prompt + enum in `src/lowork/benefits_extract.py`. Codebook hard-cases (unlimited PTO = individual, shutdown = structural, etc.) go verbatim into the system prompt as tie-breaker rules — mirror how `dei_stance.py` embeds tie-breakers.

**1.3 Hand-label validation sample.** Reuse `scripts/label_sample.py` scaffolding to draw a stratified ~100-item sample. **Rebecca hand-codes the sample herself** — this is interpretive reading against the codebook, not delegable labeling; budget it as such.
- **Scaling gate (load-bearing):** Krippendorff's α **≥ 0.8 over the FULL stratified sample**. The headline *individualization index = individual ÷ total items* is only as trustworthy as locus coding.
- **Hard-case subset** (unlimited PTO / EAP variants / "flexible work"): report its α **separately**; iterate the codebook until hard cases clear **0.667** (Krippendorff's tentative floor). Hard-case α informs the codebook; it is not the scaling gate.
- **Branch:** full-sample α < 0.8 after codebook iteration → do **not** scale extraction blindly; the individualization index is demoted from headline to exploratory and the write-up leads on the disaggregated structural-vs-individual counts instead.

---

## Phase 2 — Pilot on known ground truth

- **GitLab F&F Day arc** (May 2020 creation → Oct 2020 monthly cadence → 2023 permanent) through the flow track end-to-end. Pipeline is validated when it reproduces that arc. Hook the expected arc into the `ValidationHypothesis` mechanism in `lowork/company.py` if convenient.
- **Coinbase** through the corpus stock pipeline (rhetoric + benefits extraction) — continuity with prior studies.
- **Gate:** both known arcs reproduced within tolerance. **Branch:** mismatch → fix instrument before scaling (do not proceed to Phase 3).
- **Exit criterion — publishable artifact (release 1).** At Phase 2 exit, the GitLab F&F Day arc ships as a **standalone Substack post**, no statistics layer: 2020 creation → monthly-cadence MR with declining-PTO rationale → 2023 permanent-benefit conversion → 2026 CREDIT retirement as coda, told through the rationale excerpts. The full H1/H2 corpus analysis is **release 2** (Phase 6). Public output does not wait for Phase 6.

---

## Phase 3 — Extraction at scale

- Rhetoric: `score_axes` over full corpus (care axis already scored; add locus). Artifact: `data/<co>/axis_scores.parquet` (extended).
- Benefits: `scripts/extract_wellbeing_benefits.py` over `benefits_perks` + `job_listing` chunks → `data/<co>/wellbeing_benefits.jsonl` (one row per extracted item: company, year, category, locus, specificity, source_chunk, verbatim span).
- **Observation ledger (emitted alongside):** `data/<co>/wellbeing_observations.parquet` — one row per **company-year-page** with `fetch_status`, `final_url`, `extracted_word_count`, `content_sane` (boolean sanity check that the page is real benefits content, not a redirect/404/ATS shell), `observed` (boolean). Seeded by the §0.1 audit, completed here. **This is the three-state model** (observed-present / observed-absent / unobserved) that makes disappearance claims falsifiable — see the Phase 4 absence rule.
- GitLab flow coding: emit `data/gitlab/wellbeing_flow.jsonl` (date, path, category, locus, change_type, rationale_type, mr_word_count).
- Human-in-the-loop CSV review pass on a sampled slice of each artifact before analysis.

---

## Phase 4 — Analysis (each step feeds the next)

Add dependencies first: `ruptures` (changepoints) + `lifelines` (Kaplan-Meier) to `pyproject.toml`; `scipy` already present for sign/Wilcoxon/Fisher/Mann-Whitney. All stats live in `src/lowork/wellbeing_stats.py`, driven by `scripts/analyze_wellbeing.py`, writing tidy tables to `data/wellbeing_analysis/` and chart JSON to `astro/src/data/stories/wellbeing.json`.

**Absence rule (pre-committed).** A benefit's absence is coded **confirmed-absent only where `observed=true` and `content_sane=true`** in `wellbeing_observations.parquet`; otherwise it is **unobserved**. No removal event, survival interval, or disappearance claim may rest on an unobserved cell — an archival gap is not a removal. Every survival curve and disappearance statement requires confirmed observations on **both** sides of the transition.

Order (matches analysis-plan §4):
1. **Trajectories/composition** — small-multiples + individualization index (report raw counts alongside; small denominators mislead).
2. **Changepoints** — PELT/binseg per company on rhetoric + benefits-count series (fall back to peak-year comparison when unstable). **Pre-specified parameter grid (locked before any results are seen; no changes after):** algorithm ∈ {PELT, binary segmentation}; `ruptures` model `l2`; penalty β ∈ {log n, 2·log n, 3·log n} (BIC-family) reported as a sensitivity band, not a single tuned value.
3. **Lag test** — (rhetoric cp − benefits cp) per company; sign test / Wilcoxon; **report the full per-company offset distribution as a strip plot**, not just the statistic.
   - **Resolution-ceiling caveat.** Chunks bin by **year**, so each series is only ~6–10 points and the lag test can only resolve offsets **≥1 year** — which sits right at the edge of the hypothesized ~1-year lead. State this ceiling wherever the lag result appears. **Upgrade path:** for companies with dense snapshot coverage (per the observation ledger), re-bin **semi-annually** if the annual result is suggestive but not clean; the semi-annual re-bin is itself pre-specified here, not a post-hoc reach.
4. **Substitution** — pre/post-2022 individualization index, paired Wilcoxon; 2×2 change-direction × locus via Fisher's exact; Kaplan-Meier survival by locus (flagged exploratory — archival censoring is real). **Report the index WITH and WITHOUT `remote_flexibility`** — it is the most contested locus call (its coding rests on a phrasing rule, not a clean structural/individual fact), so H2 must hold both ways to be robust to that judgment. `remote_flexibility` locus follows the phrasing sub-rule pinned in the codebook (company-operating-model framing = structural; personal-autonomy/onus framing = individual; bare mention = ambiguous).
5. **External alignment** — JOLTS quits overlay (reuse `power_proxies.json`, quarterly variant); correlation at lags 0–4 quarters; layoff event studies (±4 quarters).
6. **GitLab rationale asymmetry** — MR word count by change direction (Mann-Whitney + beeswarm); rationale-type × direction (Fisher's exact); pull every restriction-event rationale excerpt for the write-up.

Posture (from the plan): descriptive/case-comparative; effect sizes + visuals over p-values; inferential tests are sanity checks.

**Pre-committed ambiguity branch (decided now, to foreclose post-hoc tuning).** If changepoints are unstable or the lag-offset distribution straddles zero, the piece **leads with the composition story** — individualization index + disaggregated structural-vs-individual counts — and the GitLab case. The lag result is then reported as *suggestive*, with the resolution ceiling stated plainly. This is the planned outcome for an ambiguous H1, not a failure mode to be tuned away.

---

## Phase 5 — Robustness

Confound sensitivity runs (pay-transparency law flags: CO'21/NYC'22/WA·CA'23 — run benefits analysis with/without legally-compelled categories; 10-K human-capital date-flag); alternate embedding model on the axes; prompt-paraphrase audit on the extraction prompt with label-stability report. Reuse the perturbation logic in `scripts/validate.py`.

---

## Phase 6 — Write-up

`astro/src/content/stories/wellbeing.mdx` (frontmatter per `astro/src/content.config.ts`; start `published: false`). Charts as new `.tsx` in `astro/src/components/` + `viz/*.astro` wrappers reading `stories/wellbeing.json`, following the `BenefitsChart` / `AxisChart` pattern. Scrollytelling spine: individualization index as through-line, GitLab rationale excerpts as human texture, CREDIT retirement as ending, "Resilience Is a Systems Problem" as closing citation.

Outputs (from plan): cross-company individualization index (headline), per-company small multiples, lag-offset strip plot, GitLab event timeline with rationale annotations, data-quality appendix.

---

## Critical path & dependencies

```
Phase 0 gate ─┬─> [corpus track]  P1(axis+taxonomy, α≥0.8 gate) -> P2 pilot -> P3 extract -> P4 analysis -> P5 -> P6
              └─> [gitlab track]   0.2 gate -> flow mining -> P2 F&F pilot ----------------┘ (feeds P4.6 only)
```

The GitLab track is separable: it feeds only the rationale-asymmetry analysis and the timeline visual. If it stalls at its gate, the corpus study still produces H1 (lag) and H2 (substitution) end-to-end.

## First three concrete actions

1. Write `scripts/audit_wellbeing_coverage.py`; seed `data/<co>/wellbeing_observations.parquet`; **read the ≥8-of-16-usable gate** and log the decision to `docs/execution-log.md`.
2. In parallel, sparse-clone the two GitLab handbook repos to scratch (`--filter=blob:none`) and probe `git log --follow` + one MR API call.
3. Draft `axes/wellbeing_locus.yaml` (corpus-free structural poles) and run `build_axes.py` with `circularity_check` (cheap, gates nothing, unblocks Phase 1).
