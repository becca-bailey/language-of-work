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
- **Verdict:** pipeline validated for dated structural events; content-diff layer needed for semantic events; one assumed milestone corrected. Coinbase stock-pipeline pilot (the other Phase 2 leg) still pending. Two locus rules (remote_flexibility, parental_leave) were added to the prompt *after* the model labels in `wellbeing_locus_review_model.csv` were generated, so those model labels don't yet reflect the final codebook. Plan: let Becca finish hand-coding (she may surface more hard cases), FREEZE the codebook, then do ONE final extraction re-run across all 8 companies so model labels match the codebook the human coded against — only then compute α. This avoids conflating "model is wrong" with "model didn't have the rule," and avoids repeated re-runs.
