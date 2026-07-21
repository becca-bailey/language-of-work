# Well-Being Study — Execution Log

Timestamped gate decisions for [wellbeing-execution-plan.md](wellbeing-execution-plan.md). One entry per gate read: what was run, the artifact, the number, the decision. Decisions are recorded here, not remembered.

---

## 2026-07-06 13:47 PDT — Phase 0.1 benefits-page coverage gate — **PASS**

- **Ran:** `scripts/audit_wellbeing_coverage.py` (read-only; no network).
- **Artifacts:** `data/wellbeing_coverage.md` (summary) + `data/<co>/wellbeing_observations.parquet` (16 ledgers).
- **Result:** **15 / 16 usable** (gate = ≥8). "Usable" = ≥1 benefits-page observation in ≥4 distinct years spanning 2022-01-01.
- **Only fail:** `netflix` — 3 thin job-landing fragments (`jobs.netflix.com`, flagged `thin`), all pre-2022, no benefits_perks content. Genuine thin corpus, not a bug (verified against classifications).
- **Decision:** Proceed with benefits-page enumeration. Netflix carries the rhetoric axes only; it is excluded from the benefits/individualization analysis (no enumerable content). Note in the write-up, do not impute.
- **Method note:** observation = a page whose chunks were classified `benefits_perks`/`job_listing`; `content_sane` is content-first (word volume + not-`thin`), with snapshot `statuscode` vetoing only on an explicit 3xx/4xx/5xx. An initial version keyed `content_sane` on `statuscode == "200"` and wrongly zeroed meta (empty statuscode field despite 500-word perks pages) — fixed before this gate read.
- **Caveat carried forward:** this ledger records observed-present pages only. Observed-absent vs unobserved (the full three-state model) is completed in Phase 3 against a target-page list; the Phase 4 absence rule applies there.

## 2026-07-06 13:47 PDT — Phase 0.2 GitLab flow feasibility gate — **PASS (with method correction)**

- **Ran:** MR API probes (unauthenticated); blobless clone of `www-gitlab-com` (`--filter=blob:none --no-checkout`, 27s); history + tree probes; API tree probes of the handbook repo.
- **MR API:** retrievable unauthenticated; `description` field present (the word-count signal). Rate limit **500 req / period** unauthenticated (`throttle_unauthenticated_api`) → a token is recommended for the full mine, not required for feasibility.
- **History mining works:** `git log` on a benefits path from a pre-migration anchor (2021 commit) returns 82 commits; tree objects present in the blobless clone.
- **Both eras present & mineable:**
  - Pre-2023 (`www-gitlab-com`): benefits at `sites/handbook/source/handbook/total-rewards/benefits/`; PTO at `.../paid-time-off/index.html.md`; **F&F Day** at `sites/uncategorized/source/company/family-and-friends-day/index.html.md`.
  - Post-2023 (handbook repo, project `42817607`): benefits at `content/handbook/total-rewards/benefits/`; **F&F Day** at `content/handbook/company/family-and-friends-day.md`.
- **Migration seam:** commit `7cf94138a9c` "Remove all the old handbook content", **2023-12-22**, on `www-gitlab-com`.
- **CORRECTION (plan was wrong):** `git log --follow` **cannot span the migration** — the file's history is disconnected from `www-gitlab-com` HEAD by the 2023 removal (0 commits from HEAD vs 82 from a pre-migration anchor). There is also an internal ~2020-06 reorg (`source/handbook/` → `sites/handbook/source/handbook/`) and F&F content under a third prefix (`sites/uncategorized/...`). **Correct method: mine each repo/era separately, anchored at pre-seam commits, and stitch by path+date at the analysis layer** — not one `git log --follow` across the seam. Plan §0.2 / Phase-3 updated to reflect this.
- **Decision:** GitLab track cleared to proceed as a separable track; adopt the stitch-by-path method.

## 2026-07-06 — Phase 1.2 benefits extractor built + piloted

- **Built:** `src/lowork/benefits_extract.py` (Anthropic tool-use, forced structured output; leaf-category + locus + specificity taxonomy; codebook hard-cases in the system prompt) + `scripts/extract_wellbeing_benefits.py`. Default model = Sonnet (JUDGE_MODEL) — validate the stronger model first so 1.3 measures the *codebook*, not model capacity.
- **Piloted:** Coinbase (24 items) and GitLab (15 items), 40-chunk cap each. Output faithful to source (verbatims are real copy). Extractor is not degenerate — Coinbase came back all-individual (genuine: unlimited PTO + flexible hours), GitLab produced structural + ambiguous.
- **Findings feeding validation (1.3):**
  1. **`remote_flexibility` locus is unruled and model-inconsistent** — individual (Coinbase "work whenever you work best") vs structural (GitLab "fully distributed") vs ambiguous (GitLab "flexibility in schedule"). This is the load-bearing hard case; the codebook needs an explicit rule before scaling.
  2. **Near-duplicate rows** — the same page re-snapshotted yields repeated items across/within years; counts need dedup by (company, year, category, verbatim-similarity) in Phase 3.
  3. **`enumerated_number` is near-absent by corpus property, not extractor error** — verified: Stripe 6/419, Google 2/122 benefits chunks carry numbers; Starbucks is the exception (15/121, "12 weeks"). The specificity/falsifiability gradient lives mainly in the GitLab handbook flow track + Starbucks; likely a supporting signal, not a headline, in the stock corpus.
- **Artifacts:** `data/<co>/wellbeing_benefits.jsonl` (coinbase, gitlab); blind coding sheet `data/wellbeing_locus_review.csv` (39 items, model labels withheld to avoid anchoring); model labels held for the join in `data/wellbeing_locus_review_model.csv`.
- **STATUS: awaiting Becca** — (a) codebook decisions on the three findings above, (b) hand-code locus/specificity on the blind sheet. Full α needs a stratified ~100-item sample across more companies; expand the extraction on her go.

**Codebook rule added (compensation out of scope).** Pay/equity/bonus/crypto, retirement/401(k)/financial-planning, and insurance (health/dental/vision/life/disability) are OUT OF SCOPE for the well-being locus taxonomy — they are the pay-transparency confound category (plan §Confounds), handled separately, not given a locus. The extractor prompt now skips them (was leaking "meaningful equity", "paid in Bitcoin" into `other`); `other` is reserved for genuine well-being benefits only. The hand-coding sheet gains a fourth value `exclude` (distinct from `ambiguous`) for out-of-scope rows; excluded rows drop from α and from the individualization index. Sheet is now generated by `scripts/make_locus_review.py` (CSV + XLSX with dropdown constraints on the hand columns). openpyxl added as a dependency. The current 39-item sheet retains the two comp leaks on purpose — coding them `exclude` validates that the scope boundary is codeable; the tightened prompt takes effect on the next extraction run.

**Codebook decision (remote_flexibility locus) — resolved by Becca 2026-07-06.** Remote work cuts both ways (restructures the company vs. shifts overhead onto the worker), so locus is decided by PHRASING, not a flat rule: company-operating-model framing ("distributed", "remote-first", "async by design") = structural; personal-autonomy/onus framing ("work whenever you work best", "flexibility in your schedule") = individual; bare mention = ambiguous. Encoded in the extractor prompt. **Sensitivity requirement:** the individualization index is reported WITH and WITHOUT remote_flexibility (plan §Phase 4.4) — H2 must hold both ways, since this is the contested category. Applied to the 39-item hand sheet: final locus = individual 27 / structural 10 / exclude 2; all rows coded.

## 2026-07-06 — Validation sample expanded to 8 companies (91 items)

- **Ran** the tightened extractor on 6 more companies (salesforce, starbucks, google, stripe, meta, hubspot) → 52 new items. Total blind sheet = **91 items** (coinbase 24, gitlab 15, hubspot 13, meta 12, salesforce 11, google 8, starbucks 7, stripe 1).
- **Tightened prompt verified:** 0 compensation leaks across the 6 new companies (was leaking equity/Bitcoin before).
- **Specificity now varies:** 19 `enumerated_number` items appear (meta 9, google 4, salesforce 3, hubspot 2, starbucks 1) — the earlier all-`named_no_number` was a two-company artifact, not a dead instrument. More structural cases too (meta 5, hubspot 3, salesforce/starbucks 2 each).
- **`make_locus_review.py` now carries forward existing hand labels** (match on company+category+verbatim) so regenerating to add companies never wipes prior coding — the 39 coded rows survived; 52 new rows are blank.
- **Sampling caveat:** `--limit 40` takes the earliest-sorted chunks, biasing toward early years; for chunk-rich companies this misses benefits pages (stripe: 1 item from its first 40 of 419 chunks). Acceptable for a *diversity* sample, but the Phase 3 full run must NOT use `--limit`.
- **STATUS: awaiting Becca** — hand-code the 52 blank rows (all in google/hubspot/meta/salesforce/starbucks/stripe), then I compute Krippendorff's α (hand vs. model) — full-sample gate ≥0.8 to scale, hard-case subset to ≥0.667.

**Codebook decision (parental_leave locus) — resolved by Becca 2026-07-06.** Follows the same guarantee logic as PTO: paid / job-protected / enumerated leave = structural (a guaranteed entitlement the org absorbs — the mirror of unlimited PTO); named-but-no-pay-or-duration ("generous parental leave") = ambiguous; explicitly unpaid or merely "available" = individual. Encoded in the extractor prompt. Prompted by model inconsistency on the same benefit (google individual / meta structural / salesforce ambiguous).

**Codebook decision (VTO / discretionary leave) — Becca 2026-07-06.** Volunteer time-off and similar discretionary leave stay `ambiguous`, NOT reclassified by a protected-vs-unprotected rule. Rationale (Becca): whether such time is *culturally protected* (staffed-around vs. crushed by deadlines) determines its true locus, but careers copy never states this — "we offer volunteer time AND make sure you have time to take it" is not a sentence companies write. So the distinction is systematically unobservable from self-presentation text; forcing individual/structural would be inventing signal the source doesn't carry.
- **Methodological limit to state in the write-up:** the locus instrument reads the *framing* of a benefit, not its lived usability. Unprotected-but-generous benefits (VTO, unlimited PTO, "flexible time") individualize in practice — the benefit exists but the surrounding system makes it unusable — yet the page shows only the offer. This gap between *offered* and *absorbable* is the H2 individualization mechanism in miniature.
- **Write-up hook (Phase 6):** a first-person version of exactly this — "I had volunteer time off but never used it because of tight deadlines" — carries the "budget migrates from system to self" thesis more vividly than the index does. Flagged as candidate narrative texture.

**Codebook decisions (sabbatical + work/life-balance) — Becca 2026-07-06.**
- **sabbatical = structural** — same category as paid parental leave: time for well-being that the company absorbs. Added to the structural hard rules.
- **work/life-balance framing = individual** — any benefit presented as helping the employee achieve work/life balance ("balance", "work/life", "be there for life's moments") individualizes it: balance is framed as the worker's to manage. Governs flexibility/perk items.
- Both already applied consistently in the 91-item sheet (all sabbatical rows structural, all balance-framed rows individual) before encoding. Encoded in the extractor prompt.
- **Precedence clause I added (flag for Becca):** the work/life-balance rule does NOT override the explicit structural categories (paid/enumerated parental leave, min-enforced PTO, shutdown, backup childcare, sabbatical) — so a "balance"-mentioning paid parental leave stays structural. No such conflict exists in the current sheet; this only matters at scale. Revisit if you'd rather balance-framing win outright.

**Codebook decision (accrued PTO) + FREEZE — Becca 2026-07-06.** accrued PTO = individual, by the same rationale as unlimited PTO: a defined number of days but still discretionary — no coverage guarantee, the burden to take it against workload is on the worker. Organizing principle for time-off locus: enforcement/guaranteed-coverage = structural (min-enforced, shutdown, paid parental leave, sabbatical); discretionary = individual (unlimited PTO, accrued PTO). Flipped 5 accrued rows to individual. Encoded in the prompt.
- **Data-quality note:** "6 paid days a year to volunteer" (#79) was extracted as pto_accrued but is VTO — reverted to `ambiguous` per the VTO rule, and the prompt now says paid volunteer time is `other`, not pto_accrued.
- **CODEBOOK FROZEN** — seven decisions pinned: remote (phrasing), parental (paid=structural), comp (exclude), VTO (ambiguous), sabbatical (structural), work/life-balance (individual), accrued PTO (individual). Final hand-sheet locus: individual 56 / structural 25 / ambiguous 5 / exclude 5.

**SEQUENCING — next: relabel the 91 hand items under the frozen codebook, then compute α.** The held-out model labels in wellbeing_locus_review_model.csv are stale (generated across progressively-updated prompts, before most rules). Plan: relabel exactly the 91 coded items under the frozen codebook (fixed item set → isolates locus-codebook reliability from extraction recall), then Krippendorff's α (hand vs model) on locus — full-sample gate ≥0.8, hard-case subset ≥0.667.

## 2026-07-06 — Phase 1.3 locus validation — **BOTH GATES PASS**

- **Ran:** `scripts/relabel_locus_sample.py` (relabel 91 items under frozen codebook) → `scripts/verify_locus_alpha.py`. Report: `data/wellbeing_locus_validation.md`.
- **Locus Krippendorff α = 0.818** (nominal, hand vs model) — gate ≥0.80 **PASS**. Raw agreement 90.1% (82/91).
- **Hard-case subset α = 0.837** (69 items in judgment categories) — gate ≥0.667 **PASS**.
- Specificity agreement 78.7% (secondary, ungated).
- **9 disagreements**, all in hard corners: #73/#79 (VTO) diverge *by design* (we chose ambiguous knowing the model reads discretionary=individual); #52/#58 bare/borderline remote; #74 paid-but-no-duration parental; #82/#85 on-site perks (model structural, hand individual).
- **Coding inconsistency to reconcile (not a model error):** #33 GitLab "Learn in-demand skills" coded individual (in-scope) vs Starbucks tuition #88/#89 coded exclude (out-of-scope) — both are learning/development. The learning/dev boundary is unpinned; decide before Phase 3 scale.
- **α is a thin pass (0.818 vs 0.80).** Reliable enough to scale, but note that 2 of the 9 disagreements are the deliberate VTO ambiguity, so the "true" codebook disagreement is smaller. Do NOT retune to inflate; reported as-is.
- **STATUS:** Phase 1.3 gate cleared → codebook validated for Phase 3 scale extraction (drop `--limit`, all companies, no comp, frozen locus rules).

## 2026-07-06 — Two scope exclusions added; α re-verified 0.903

- **Becca decisions:** (a) learning & development (tuition, professional development, skills platforms) = out of scope/exclude — reconciles the #33-vs-#88/#89 inconsistency; (b) food/beverage/snack amenities (free coffee, snacks, catered meals) = exclude, EXCEPT meals targeted at a life event (meals for new parents = caregiver_support). Both encoded in the extractor prompt and the relabel exclude-instruction.
- Flipped #33 (learning) and #85 (beverages) to exclude in the hand sheet; #72 (meals for new parents) kept as caregiver_support.
- **Re-ran relabel + verify under the updated codebook:** locus α **0.903** (was 0.818), raw agreement 94.5% (86/91); hard-case subset α **0.870**. Both gates comfortably PASS now — the exclusions removed genuine noise (wellness_perk and caregiver_support both hit 100% agreement).
- Remaining 5 disagreements are all by-design/borderline: 2 VTO (deliberate ambiguity), 2 bare/borderline remote, 1 paid-but-no-duration parental. **CODEBOOK FULLY FROZEN.**

## 2026-07-06 — Phase 2 GitLab flow pilot (F&F Day) — QUALIFIED PASS + arc correction

- **Built** `scripts/mine_gitlab_flow.py`: stitches commits from the pre-migration www-gitlab-com clone (3 historical path patterns) + the post-migration handbook repo (API), dedups by sha, sorts, coarse-classifies change_type from the subject. Output `data/gitlab/wellbeing_flow.jsonl` — **160 unique commits, 2020-04-20 .. 2026-04-09**.
- **The lineage is a 5-hop chain** (verified): `source/handbook/ceo/family-friends-day/` (2020-04 creation) → `sites/handbook/.../ceo/family-friends-day/` (2020-06 reorg) → `sites/marketing/.../company/family-and-friends-day/` → `sites/uncategorized/...` (2021-05) → handbook repo `content/handbook/company/family-and-friends-day.md` (2023-08). Slug change (family-friends → family-and-friends), section move (ceo → company), dir reorg, and repo migration — `git log --follow` CANNOT trace this; stitching is mandatory. (There was also a brief 2021-04 "Pandemic Support Day" rename flip-flop.)
- **Dated milestones reproduced exactly:** creation 2020-04-20 ("Add Family and Friends Day to the handbook"); monthly cadence 2020-10-30 ("update-family-friends-monthly-day-covid19"). These are the hardest, most specific facts and the pipeline nails them → the git-stitch approach is validated.
- **Ground-truth ARC CORRECTION:** the assumed "2023 conversion to permanent benefit" is NOT supported. No titled commit converts it, and the current live page frames F&F as pandemic-contingent ("planned to continue for as long as the majority of the world was dealing with the pandemic"). F&F Day did outlast the acute pandemic (commits through 2026) but is not framed as a deliberate permanent benefit. **Do not assert "permanent conversion" in the write-up without content-diff evidence.** (The Phase 6 spine referenced this milestone — revisit.)
- **Instrument requirement surfaced:** semantic transitions (temporary→permanent reframing) are CONTENT-level, invisible to commit-subject mining. The plan's content/rationale-diff layer (MR descriptions, page-text diffs) is therefore REQUIRED, not optional. The subject-only change_type classifier is coarse: it misclassified the 2023 migration commit as `remove` (false positive for benefit-removal) and the monthly-cadence commit as `update`. Dates are reliable; semantic change_type needs the content layer.
- **Verdict:** pipeline validated for dated structural events; content-diff layer needed for semantic events; one assumed milestone corrected. Coinbase stock-pipeline pilot (the other Phase 2 leg) still pending.
- **Findings memo written up (Becca's guidance):** `docs/phase2-ff-pilot-memo.md`. Reframed — this is the **pilot's findings memo, NOT Phase 6 write-up material** (correcting my earlier "Phase 6 material" framing). Three findings promoted from buried clauses to claims: (1) *headline is the methodology result* — reconstructing from the primary record overturned the tidy secondhand arc I'd handed in as known-truth; the pilot caught it, which is the project's epistemic pitch in miniature; (2) the six-day "Pandemic Support Day" rename = a revealed preference for keeping the commitment legible-as-generous while keeping the obligation deniable (the cheap-talk-vs-commitment seam); (3) "adds coverage requirements" = the moment a structural benefit partially privatizes under pressure. Findings 2–3 are **[pending MR-description confirmation]** — they depend on the *why*, which is in the unmined MR/diff layer. Directive: code the rename (change_type:reframe test) and coverage-requirements (first structural→partially-individual locus test) as explicit events — they validate whether the change-type/locus schemas capture what matters, on the best-understood case. Guardrail: F&F stays a close-up, NOT the centerpiece (one transparency-selected company, thin footprint); centerpiece remains the cross-company individualization index.

## 2026-07-06 — PIVOT: GitLab case story moves off F&F Day to parental leave (Becca)

- **Decision:** F&F Day is too low-stakes to carry the GitLab deep-dive ("a few extra days off per year, just above free coffee"). The story spine refocuses on a *substantial* benefit — parental leave (or caregiver support). F&F still served its purpose: it validated `mine_gitlab_flow.py` (the stitch-mining pipeline), which re-points at any benefit by swapping path patterns — no rework.
- **Scout (parental leave — promising):** GitLab documents **16 weeks paid Parental Leave** (enumerated, quasi-contractual — the specificity gradient the plan wants). Policy now lives at `content/handbook/people-group/time-off-and-absence/leave-types.md`; a `parental-leave-toolkit` (reentry buddies/logistics) has history back to **2019** (older + richer than F&F's 2020 start). Recent commits show **expansion** events: adding Parentaly and Tilt vendor benefits (2026), "clarify no work during parental leave" (2025). A real change-stream exists → viable H3 (rationale-asymmetry) case.
- **Open question before committing:** does the 16-week figure have a *change arc* (e.g. 12→16 weeks, or any restriction)? That requires tracing the policy across its historical paths (pre-2023 `total-rewards/benefits/...` + toolkit + current leave-types.md), same 5-hop stitch method as F&F. A benefit that never changed is a weaker story than one that expanded or was cut.
- **STATUS: awaiting Becca** — confirm parental leave vs caregiver support as the spine, then mine the full policy arc (trace the weeks over time + expansion/restriction events + rationale). F&F flow data (`wellbeing_flow.jsonl`) retained as pipeline-validation evidence, not story material.

## 2026-07-06 — Phase 3 scale extraction (started)

- **Rhetoric axes — DONE.** Ran `score_axes` with the full FINGERPRINT set (incl. `wellbeing_locus`) across all 16 companies → `data/<co>/axis_scores.parquet` (gitignored, regenerable). Both wellbeing axes (care↔intensity + individual↔structural locus) now scored corpus-wide. Sanity: wellbeing_locus means are small-positive (slightly individual-leaning careers copy), plausible. NB: `score_axes` positional axes must be passed as separate words — zsh does not word-split unquoted `$VAR` (bit me once).
- **Benefits extraction — RUNNING** (bg `be2qsxu1i`). Full corpus, no `--limit`, frozen codebook, Sonnet (the model α=0.90 validated). 15 companies (netflix excluded per Phase 0), ~1458 benefits-bearing chunks, ~145 batches. Overwrites the pilot jsonls so all companies are consistent under the frozen codebook. Within-year chunk dedup was considered but barely helps (1458→1432 — chunks genuinely differ); the duplicate-*item* problem is cross-year and handled at the Phase 4 counting stage, not by dropping chunks.
- Next after it lands: per-company sanity pass + human-in-the-loop review, then Phase 4 analysis.

## TODO (deferred) — language filter on scoring/extraction

**Finding (2026-07-06):** `careers.snap.com` serves locale-localized content at the same URLs, so a handful of Snap's 2024–2025 Wayback captures came back non-English (Vietnamese; also `lang=nl-NL`/`lang=es` params seen). Scope: Snap only confirmed so far — 2024 (2/8 chunks) and 2025 (8/19) non-English; all other Snap years and the rest of the corpus check English via `is_english`. Impact: Snap's 2024–25 axis scores are mildly contaminated (non-English chunks embedded + scored against English-worded poles). The wellbeing story's benefit-example tooltips already filter with `is_english`, so the published quotes are clean.

**To do later:**
1. Scope corpus-wide — check every company for localized/non-English chunks (global careers sites often localize), not just Snap.
2. Add an `is_english` filter before embedding/scoring (and extraction), so localized captures can't contaminate any company's scores. One clean corpus-wide fix.
3. Treat Snap single-company signals (fertility tail, therapy-stipend) with extra skepticism until done — some recent Snap captures are localized noise.

## 2026-07-06 — Phase 6: wellbeing story page built ("The Care That Survived")

Built `astro/src/content/stories/wellbeing.mdx` (published, in the wellbeing slot) with four interactive visx charts, following the dataviz skill (palette validated with the script, not eyeballed; no dual-axis; emphasis form). Supersedes the old `benefits` story (still present as `published:false` draft — retain or delete is Becca's call).

- **Data:** extended `export_story_web.py` `export_wellbeing()` with four datasets → `stories/wellbeing.json`: `concession` (care/DEI z + JOLTS quits), `axes2020` (per-axis 2020 z — Care +2.2, DEI +1.8 top), `locusDivergence` (mental-health vs family/caregiving keyword prevalence), `flow` (F&F commit density + 5 annotated events).
- **Charts** (`astro/src/components/*.tsx` + `viz/*.astro`, visx islands, `useThemeColors`, `client:only`): `ConcessionChart` (care+DEI+quits, z-scored to one axis), `AxisSpikeChart` (emphasis bars — concession axes colored, rest gray), `LocusDivergenceChart` (the centerpiece — mental-health=individual/halt-orange vs caregiving=structural/arcade-purple, CVD ΔE 137, direct-labeled), `FlowTimeline` (tiered event annotations).
- **Verified:** prod build clean (23 pages, wellbeing built); headless-Chrome render check = 31 SVGs, 0 console errors, both light and dark (body bg rgb(10,10,10)). Screenshot reviewed — all four charts render with correct shapes; timeline label crowding fixed with per-event vertical tiers.
- **Palette:** care=arcade `#5e1af4`, DEI=slate-blue `#7669e9` (CVD 33 ✓), quits=muted dashed reference; locus split arcade-purple(system) vs halt-orange(self). Contrast WARNs resolved via mandatory direct labels.

## 2026-07-06 — H1 coverage-controlled + JOLTS leverage overlay (fork resolved: lead with rhetoric)

`scripts/analyze_h1_leverage.py` → `data/wellbeing_h1_leverage.txt`. Agreed plan: strengthen the dense rhetoric findings, use benefits as illustrative texture only, do NOT pull in job listings (adds cross-company comparability confounds).

- **Care–DEI co-movement survives coverage control.** The pooled r=0.88 was inflated by coverage drift; the robust WITHIN-company version is median **r=+0.53, 95% CI [+0.27, +0.70], 15/16 companies positive** (only hubspot −0.13). The concession bundle (care + DEI rhetoric moving together) is real and broad, not a pooling artifact.
- **The concession bundle tracks worker leverage (JOLTS quits).** care vs quits r≈+0.64 (lag0), +0.71 (rhetoric leads quits by 1yr); DEI vs quits +0.54 / +0.75. Both strongest at lag −1 (talk leads the quits surge). BUT: pre-2020 care was flat while quits rose 2015-19, so the correlation is really a **2020–2024 spike-and-recede phenomenon**, and the 2020 onset is **COVID-confounded** (pandemic wellbeing talk ≠ pure labor-market response). The cleaner evidence is the RECEDE: quits fell 2022→2024 (2.76→2.07) and care rhetoric fell with it (+0.054→+0.030). The concession deflated as leverage fell.
- **Verdict / fork resolved:** the rhetoric story is solid enough to LEAD with — coverage-controlled co-movement + a leverage-linked spike-and-recede. No need for the HN job-listings investment (user also declined it on comparability grounds). Benefits stay illustrative texture (GitLab close-up; fertility-as-expensive-signal; care-benefits secular build).
- **Step 3 (instrument hygiene):** standardize — KEYWORD prevalence for trajectories (dense, full-corpus), LLM extraction for locus/specificity only (validated but sparse). The crude benefits dedup is demoted with the index and not worth fixing now. Logged, not silently dropped.
- **Open caveats for write-up:** quits is total-nonfarm not information-sector (plan wanted sector-specific); ~10 year-points; 2020 COVID confound on the spike onset.

## 2026-07-06 — Phase 4(b) rigorous H2 test: NOT a null, but UNDERPOWERED on substance

Built `scripts/analyze_wellbeing.py` (power-table-first, per advisor). Report: `data/wellbeing_analysis_phase4b.txt`. This overturns the earlier hasty "H2 not supported" read.

- **1. Power table:** only **8/15 companies** have ≥3 deduped benefit items on both sides of 2022; most cells are 2–5 items. Per-company benefits tests are dead — stated, not run.
- **2. Aggregate index + bootstrap CI (balanced 8-co panel):** pre **0.571 [0.468, 0.675]**, post **0.500 [0.390, 0.610]**. **CIs overlap heavily; post-CI contains the pre point estimate → FAIL-TO-REJECT, not a confirmed null.** The benefits-composition index is simply too sparse to adjudicate H2. Without-remote sensitivity (5 co): same story, wider CIs. **The individualization index cannot be the robust headline the plan assumed.**
- **3. Positive control (care/H1 axis):** pooled care series peaks cleanly at **2020 (+0.077, ~3.7× baseline)** — the signal is real and trajectory-detectable. Caveat: PELT (rbf, pen=1.0) flagged 2017, not 2020 — **the changepoint config is not yet calibrated**; trajectory/peak works, PELT needs tuning before any changepoint-dated claim (Phase 5 robustness item).
- **4. H2 on the DENSE instrument (rhetoric locus axis, 15 co):** within-company z mean **pre +0.016 → post +0.296** (toward individual), **10/15 companies more individual post-2022**, Wilcoxon **p=0.229**. So: **directionally consistent with H2, suggestive, but not significant at n=15.** This is the powered instrument and it says "suggestive individualization drift," NOT "null."

**VERDICT:** H2 is neither confirmed nor refuted. Benefits substance = underpowered (can't tell). Rhetoric locus = suggestive-but-inconclusive individualization drift. H1 care-rhetoric spike-and-recede = the one robust finding. The honest framing is "can't confirm substitution from the substance; the rhetoric hints at it," NOT "no substitution." Deferred (logged): Kaplan-Meier, per-company benefits changepoints, Fisher on tiny cells. **Next: PELT calibration; then the spine conversation with this evidence in hand.**

## 2026-07-06 — Parental-leave arc exploration (findings)

Traced GitLab's paid parental leave across the pre-2023 handbook (blobless clone). Findings:
- **Headline number looks STABLE at 16 weeks** across 2021–2023 (confirmed by reading the full policy text at 2021-11, 2022-06, 2023-06; current handbook still 16). Pre-2021 origin sits behind multiple page renames (benefits/ → total-rewards/benefits/general-and-entity-benefits/ → people-group/.../leave-types.md) that the blobless clone can't cheaply resolve; a definitive "when did 16 weeks start / was it ever different" needs a full (non-blobless) history trace or Wayback. The dramatic 4→16 expansion I first suspected was a MISREAD — the "4 weeks" is a secondary *unpaid extension* clause, not the headline.
- **The interesting data is qualitative, not the number:**
  1. **Individualization language embedded INSIDE the structural benefit.** The 16-week policy itself says team members are "encouraged to decide for themselves the appropriate amount of time to take and how to take it." A generous structural benefit, framed in individual-responsibility language — the individualization thesis operating inside the benefit, not just around it.
  2. **Peripheral accretion of individual-locus perks around a flat structural core.** Recent additions (2025–26) are vendor stipends — Parentaly, Tilt (fertility/parenting support) — i.e. individual-locus add-ons bolted onto the stable structural leave. Structural core flat; individual periphery grows. That IS the substitution pattern, in one benefit.
- **Editorial read:** there is interesting data, but it's a *framing/composition* story (individual rhetoric + individual-perk accretion around a stable structural commitment), NOT a dramatic weeks-changed arc — at least none found so far. Whether that clears Becca's "interesting enough" bar is her call. A full non-blobless weeks-trace could still surface an early expansion/restriction; not yet done. Two locus rules (remote_flexibility, parental_leave) were added to the prompt *after* the model labels in `wellbeing_locus_review_model.csv` were generated, so those model labels don't yet reflect the final codebook. Plan: let Becca finish hand-coding (she may surface more hard cases), FREEZE the codebook, then do ONE final extraction re-run across all 8 companies so model labels match the codebook the human coded against — only then compute α. This avoids conflating "model is wrong" with "model didn't have the rule," and avoids repeated re-runs.

---

## 2026-07-18 — Validation Phase 0.2: stance hand-label agreement — **PASS (provisional)**

Ran `report_dei_agreement.py --task stance` → `data/dei_labels/stance_agreement.json`.
**Pooled α = 0.932, accuracy 0.96, n = 100** against the migrated 4-class stance data
(gate: α ≥ 0.80). Up from a 0.47 preview before the same-day taxonomy revision
(performance_elite removed, civilizational_mission narrowed to explicit-West) — the old
disagreements were definitional, and the revision eliminated them.

Two honesty qualifiers on the 0.932:
1. **Provisional**: sample rows 64–100 are an AI first-pass awaiting Becca's
   verification (rows 1–63 are hers). Re-run after verification for the final number.
2. **It validates the shipped data, not the new prompt.** Stored stance predictions
   were migrated deterministically, with the 31 civilizational chunks re-judged under
   Becca's explicit-West rule — agreement on those rows is partly by construction.
   The classifier-under-the-new-prompt α requires a fresh API re-classify (batch it
   with the pending register re-classify), then re-run this report.

Disagreements (4): google `d12f7193` (hand neutral / pred affirming — Becca's, arguable),
palantir `787fee89` (hand apolitical / pred neutral — Becca's), shopify `b30003e0` and
starbucks `7e8fa2af` (AI rows, both flagged as judgment calls).

## 2026-07-18 (later) — Phase 0.2 follow-up: post-adjudication stance agreement

Becca verified all 37 AI-prefilled rows and resolved the 4 disagreements
(rows 13, 51, 66, 81), each toward the classifier. Re-run: **α = 1.0,
accuracy 100/100**. Verification pass COMPLETE — the provisional qualifier is
dropped; the citable pair is final: **blind α 0.932** (reliability figure) /
**adjudicated α 1.0** (gold set and shipped stance data fully consistent).
Standing qualifiers on the 0.932: prefilled-label anchoring, and migrated data
partly matched-by-construction on civilizational rows. Classifier-under-
new-prompt α still pending a fresh API re-classify.

## 2026-07-19 — Phase 0.3: full-corpus re-classify under current prompts + agreement gates

Ran the batched API re-classify across all 19 companies: `classify_dei_register.py
--reclassify-all` (rewritten register prompt) + `classify_dei_stance.py
--reclassify-all` (4-class taxonomy). 4,694 analysis chunks per task, verified
register/stance counts match per company. Two crash-and-resume cycles along the way,
both hardened in code: (1) strict `json.loads` on batch output died on
newline-delimited JSON → tolerant `parse_json_items()` in `lowork/dei.py`, shared by
both classifiers; (2) a transient connection error killed polling on an
already-billed batch → poll loop now retries; salesforce's completed batch was
recovered by ID with no re-spend.

Gate reads (classifier-under-current-prompt, the citable numbers):

- **Register**: `report_dei_agreement.py --task register` →
  `data/dei_labels/agreement.json`. **Pooled α = 0.802, accuracy 0.876, n = 201**
  (gate α ≥ 0.80: PASS, at the line). Largest confusions: explicit_demographic →
  structural_process (6), absent → aspirational_vague (5) — both adjacent-register
  leaks, no absent↔explicit flips beyond 2.
- **Stance**: `report_dei_agreement.py --task stance` →
  `data/dei_labels/stance_agreement.json`. **Pooled α = 0.877, accuracy 0.93,
  n = 100** (gate α ≥ 0.80: PASS). Down from 0.932 vs the migrated data, as
  expected — this is the honest number for the prompt we ship. All 7 disagreements
  are one-directional: classifier says neutral where the hand label is a stance
  (6× mission_focus_apolitical, 1× affirming_dei). mission_focus_apolitical recall
  vs hand labels = 14/20; civilizational 3/3; affirming 19/20. Counter-stance
  counts in the DEI story are therefore floors — the classifier under-detects
  apolitical counter-programming, it does not invent it.

Phase 0 of the validation-reassurance plan is closed. Downstream re-score
(score_dei → exports → synthesize) re-run after these labels landed.

## 2026-07-20 — Validation-reassurance Phase 1: axis tournaments, Google + Netflix

Ran `validate_axes.py --company google --axes performance,craft` and
`--company netflix --axes altruism,performance,craft` (Sonnet judge, 40 pairs
per axis, seed 42; merges preserved Google's existing altruism section).
Gate: embedding-vs-LLM Spearman ≥ 0.6. Pair-level localization computed from
the logged judgments (agreement = LLM winner also has the higher chunk zscore).

- **netflix/performance: PASS** — Spearman 0.616 chunk / 0.766 sentence;
  judge-pair agreement 0.78, consistent across eras (1.00 early / 0.67 late /
  0.78 cross). The published Netflix story's intensity-trend claim now has
  two-instrument support.
- **google/performance: MISS, localized** — 0.518 chunk / 0.349 sentence.
  Disagreement concentrates in early-era pairs (both years ≤2015: 0.61, n=18);
  cross-era pairs agree 0.80 (n=20), both-recent 1.00 (n=2). Read: the
  early-year *ordering* (thin years, incl. the pre-2005 archaeology era) is not
  reliable; the rise into the modern era is supported. Branch taken: hedge any
  Google early-year performance ordering; trend-level contrast OK.
- **craft: FAIL, broad — both companies.** google −0.063 chunk / −0.451
  sentence (pair agreement 0.53 ≈ coin flip in every era); netflix −0.09 /
  −0.095 (0.50 overall; 0.87 both-recent but 0.14 early, 0.33 cross-era).
  Axis separation from performance PASSES (cosine 0.093, chunk r≈0.16–0.19),
  so craft is not duplicating performance — but an independent reader does not
  reproduce its year ranking at all. Per the plan branch: craft trends must not
  be presented as trends; the axis needs rework (inspect craft evidence quotes
  first — thin/noisy quotes vs wrong direction not yet distinguished) before
  any craft story. First human-independent check on the newest axis; this is
  what the check is for.
- netflix/altruism: weak (0.09 chunk / 0.402 sentence; pair agreement 0.55) —
  no story leans on Netflix altruism; noted, not actioned.
- Google ground-truth altruism check re-confirmed FAIL (peak 2025 vs expected
  2014±2; control coupled r=0.52) — the open corpus-composition question,
  unchanged by this run. Netflix has no expected-peak hypothesis (informational).
- Perturbation (min Spearman 0.988 google / 0.956 netflix) and craft-vs-
  performance axis separation pass at both companies.

## 2026-07-20 — Stance prompt v2 (tie-breaker 8) + dedup + full-corpus re-classify

Error analysis of the 6 stance disagreements (all hand=mission_focus_apolitical /
pred=neutral) showed they were 3 recurring passages — Stripe "The Stripe service"
(2019–22), Netflix "Artistic Expression" (2024–26), Shopify "Accept our mission"
(2024–26) — all one genre: viewpoint-neutrality about customers/content *demanded
of employees*. The prompt's product/customer guard pushed these to neutral; the
under-detection was definitional, not model error. Becca's ruling: this genre IS
discouraging workplace activism → extend the codebook.

Changes ([src/lowork/dei_stance.py](../src/lowork/dei_stance.py)):
- Tie-breaker 8 + definition extension: employee-directed product/content
  neutrality demands ("you'll serve customers / work on content you disagree
  with, or work elsewhere") → mission_focus_apolitical; the same neutrality as
  pure company/product policy stays neutral. Calibration examples paraphrased,
  not quoted from the sample.
- Exact-(heading,text) dedup in `classify_stances`: classify each unique text
  once, fan the label out to every chunk_id (per-year counts unchanged).
  Motivated by Shopify 2024 vs 2026: byte-identical text, different labels —
  batch composition sways borderline calls at temperature 0. Full corpus:
  4,694 chunks → 2,796 unique API classifications (~40% saved).

Gate reads:
- **Validate-only (new prompt vs 100-row sample, before any overwrite): α 0.932 /
  acc 0.96; mission_focus_apolitical recall 20/20 (was 14/20), zero new false
  positives into the class.** 4 residual disagreements all sit on the soft
  affirming/neutral boundary (borderline copy; batch-composition variance).
- **Full-corpus re-classify (19 companies) then `report_dei_agreement.py --task
  stance`: pooled α 0.967 / acc 0.98, n=100 — PASSES 0.80 gate.** CAVEAT: partly
  in-sample — the prompt revision was driven by this sample's errors; treat 0.967
  with that qualifier (homepage says so).
- Corpus impact: 149/4,693 labels changed — 17 neutral→mission_focus_apolitical
  (the fix; incl. an earlier Netflix "Not everyone will like—or agree with—"
  variant the rule found beyond the sample), 0 civilizational changes, and
  70/62 neutral↔affirming churn (soft-boundary instability, net +8).
- **Out-of-sample spot-check pending (Becca):**
  [data/dei_labels/stance_new_apolitical_review.md](../data/dei_labels/stance_new_apolitical_review.md)
  lists all 17 new counter-stance calls. Two questionable families flagged:
  Stripe "Think rigorously" ×4 (heterodox-speakers/epistemic-culture copy, not a
  service-neutrality demand) and Palantir 2026 "shallow consumerism" (decline
  rhetoric; also the sample's one new false positive, hand=neutral). If ruled
  false positives: tighten the rule's wording (debate-welcoming ≠ demand) and
  re-classify those chunks.

Downstream: score_dei + export_dei_web re-run for all 19; export_story_web
--story dei re-run. The DEI story now surfaces Netflix's Artistic Expression
clause as counterQuotes (2022–26). dei.mdx floors caveat kept (out-of-sample
under-detection still possible); homepage stance α updated 0.88 → 0.97 with
the in-sample qualifier. Everything uncommitted, pending Becca's spot-check.

## 2026-07-21 — Stance v2 spot-check adjudicated; FINAL gate read α 0.983

Becca reviewed all 17 new mission_focus_apolitical calls
(stance_new_apolitical_review.md): 16 confirmed (incl. Stripe "Think
rigorously" — heterodoxy copy IS in-scope, her ruling), palantir 2026
`66b9df96` ruled false positive on text-based grounds (her blind gold-set
label was already neutral; company priors don't label chunks). Prompt guard 9
added to dei_stance.py (cultural-decline / purpose-critique rhetoric without
an explicit refusal or employee-directed neutrality demand → neutral); the
single affected chunk re-classified → neutral (corpus-wide grep confirmed no
other chunk carries the passage); palantir score_dei + export_dei_web +
export_story_web --story dei re-run.

**Final citable stance numbers: pooled α 0.983 / accuracy 0.99 (n=100).**
Standing qualifier unchanged: partly in-sample (prompt v2 was driven by this
sample's errors; the 17 new calls were the out-of-sample check, now fully
hand-reviewed). Sole remaining disagreement: apple `95ead68a` partner-org
list (hand affirming_dei / pred neutral). Homepage updated to α 0.98.

## 2026-07-21 — Altruism construct investigation; story UNPUBLISHED pending reshape

Becca's hypothesis confirmed: her altruism construct (naive "we're changing the
world" tech-idealism) is narrower than the embedding axis, which conflates it
with belonging/DEI idealism and CSR philanthropy. Evidence: google's shipped
worldChanging series peaked 2022 (z 1.32) on the belonging interview ("Can we
create a world where we all belong?") — the live story's headline quote WAS the
leak. Root cause is surface form: belonging copy is phrased in world-language,
so embedding fixes fail — the inclusion-axis partition (mirror of the techno
strip) cannot separate them (leak sentences score LOWER on inclusion, 0.36-0.41,
than "making the world a better place" does, 0.45; peaks unmoved at any
threshold).

Fix piloted: LLM sentence-genre classifier (Haiku), v2 codebook from Becca's
four boundary rulings — (1) bare mission restatements → mission_scope, world_
changing only when moralized; (2) techno-solutionism split by frame (humanity-
broadly → world_changing, concrete feature → product_hype); (3) structural-
inequity framing → belonging_dei without needing DEI vocabulary; (4) product
accessibility/benefit copy → product_hype. Full google non-techno pool
classified (1,735 sentence-years, 876 unique) with chunk-heading context.
Review file: data/altruism_labels/genre_review_google.{md,csv}.

Findings: world_changing = 44 sentence-years TOTAL (several years zero; the
2014-16 value is one canonical sentence) → an intensity trend (topk z) is not
a valid instrument for this construct; prevalence is. Prevalence: ~14-23% of
mission copy in 2004-07 → ~3% by 2014 → <1% 2018-22. **The 2014-peak
hypothesis does not hold under the corrected construct — the naive-idealism
peak is 2004-2007 (pre-registered by Becca as a real finding, not a
measurement issue).** Genre mix (google, full pool): belonging_dei 644 / csr
176 / product_hype 141 / world_changing 44 / mission_scope 41 — idealism
changed genre, not volume. Caveat: 2018+ corpus includes diversity-report page
fills, inflating belonging's share (within-page-family mix is the clean
comparison, not yet computed).

Decision pending (Becca reshaping claims): genre instrument story-wide vs
google-only rewrite. Meanwhile altruism.mdx set published:false — prod build
verified 26 pages, /stories/altruism no longer built. Pilot scripts + genre
cache in session scratchpad; nothing merged into score_altruism_split.py yet.
