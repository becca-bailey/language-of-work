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
