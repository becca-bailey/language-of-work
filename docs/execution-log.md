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
