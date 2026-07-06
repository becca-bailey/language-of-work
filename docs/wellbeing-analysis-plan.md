# Well-Being Analysis Plan — The Language of Work

## Purpose and framing

This study tests whether the power-tracking thesis replicates in well-being language, with a substitution twist: as employer leverage returns, the well-being budget migrates from system to self. The design measures two signals with separate instruments — care *rhetoric* (continuous, embedding-based) and enumerated *benefits* (categorical, extraction-based) — plus a locus-of-responsibility dimension (individual vs. structural) applied to both. GitLab serves as the maximum-resolution single case via git history; the cross-company corpus provides breadth.

Three pre-registered hypotheses, stated before looking:

1. **Lag structure (cheap talk first).** Care rhetoric peaks and recedes before enumerated benefits erode. Rhetoric is volatile; benefits are sticky, quasi-contractual commitments.
2. **Substitution (individualization).** The share of well-being content coded individual-locus rises after 2022, even where total well-being volume stays flat.
3. **Rationale asymmetry (GitLab only).** Benefit expansions arrive with verbose, worker-welfare justifications; restrictions arrive terse and procedural — silence as signal operating inside a radical-transparency company.

Writing these down now is the discipline: findings that contradict them are reported, not absorbed.

## Instruments

### Rhetoric (continuous signal)

Semantic axes built from contrast-pair pole sentences in careers-page register, scored via cosine similarity, top-k averaged per company-year to filter boilerplate.

Two axes:

- **Care ↔ intensity.** Poles like "we want you to rest and recharge" vs. "we move fast and expect a lot." Expect the operative negative pole to be silence rather than explicit anti-well-being language, as with DEI — so track absolute care-axis volume alongside the signed score.
- **Individual-locus ↔ structural-locus rhetoric.** Poles like "resources to help you manage stress" / "your well-being journey" vs. "we staff so you can actually disconnect" / "company-wide closure so no one returns to a full inbox." Structural rhetoric may be nearly absent; its rarity is itself a finding.

Normalization: within-company z-scores for trajectory analysis (the primary mode here, since the hypotheses are about change over time); raw cosine scores retained for any cross-company level comparison. Do not pool z-scores across the two purposes.

### Benefits (categorical signal)

Structured LLM extraction, low temperature, from benefits pages/sections into a fixed taxonomy per company-year. Each extracted item gets:

- **Category**: PTO (accrued / unlimited / minimum-enforced), parental leave (weeks), caregiver support, mental health (EAP-only / therapy stipend / dedicated days / company-wide shutdown), wellness perk (app subscription, gym stipend, wellness challenge), sabbatical, remote/flexibility, four-day week, other.
- **Locus**: individual / structural / ambiguous, defined operationally as *who absorbs the adaptation cost when disruption hits*. Codebook rules for known hard cases: unlimited PTO = individual (no coverage guarantee, decision burden on employee); EAP = individual; therapy stipend = individual; company-wide shutdown = structural; minimum-enforced PTO = structural; backup childcare = structural.
- **Specificity**: enumerated-with-number ("16 weeks") vs. named-without-number ("generous parental leave") vs. generic ("great benefits"). Specificity is the falsifiability gradient — numbers are commitments, adjectives are rhetoric wearing a benefits costume.

### GitLab flow data (event-level)

Every commit/MR touching well-being-relevant paths in both repos (www-gitlab-com pre-2023, content-sites/handbook after), coded with: date, benefit category, locus, **change type** (add / expand / restrict / remove / reframe), **rationale type** (worker-welfare / cost / compliance / external event / values-alignment), and MR description word count. Use `git log --follow` across the repo migration; retrieve MR descriptions via the GitLab API.

## Analysis methods

Posture first: with ~13 companies and annual-to-quarterly resolution, this is a descriptive and case-comparative study with directional statistical checks — effect sizes and visualization over p-values. Inferential tests are sanity checks, not the argument.

### Trajectories and composition

- Small-multiple time series per company: care-axis score, benefits count by locus, and the **individualization index** = individual-locus items ÷ total well-being items per company-year. Report raw counts alongside the index; with small denominators the index alone can mislead (2-of-3 vs. 20-of-30 look identical).
- Stacked composition charts (individual / structural / ambiguous share over time) — the substitution hypothesis is a composition claim, so composition visuals carry it.

### Dating the shifts

- **Changepoint detection** (PELT or binary segmentation, whichever the series length supports) on each company's rhetoric series and benefits-count series, to date shifts algorithmically rather than by eyeball. The changepoint dates are the input to the lag test.
- **Lag test**: for each company, compute (rhetoric changepoint date − benefits changepoint date). H1 predicts a negative median. With n≈13, use a sign test or Wilcoxon signed-rank on the offsets and report the full distribution — a strip plot of per-company offsets is more honest and more legible than the test statistic.
- Where changepoints are unstable, fall back to peak-year comparison (year of max care score vs. year of max structural-benefit count).

### Substitution test

- Pre/post-2022 comparison of the individualization index, paired by company (Wilcoxon signed-rank). Complement with the disaggregated version: did structural counts fall while individual counts held or rose? A 2×2 of change direction by locus across companies, tested with Fisher's exact, is the cleanest summary.
- **Benefit survival**: treat each benefit item as an entity with a lifespan (first appearance → last appearance in snapshots). Compare survival curves by locus (Kaplan-Meier, discrete-time given quarterly/annual snapshots). Prediction: post-2022, structural benefits show higher hazard of disappearance than individual perks. This is exploratory garnish, not a headline claim — censoring from archival gaps is real.

### External alignment

- Overlay JOLTS quits rate (information sector) as the leverage series; report correlation of the pooled care-rhetoric trajectory with quits rate at lags 0–4 quarters. This replicates the core-thesis mechanic in the new domain.
- **Event studies** around each company's major layoff announcements: rhetoric and benefits in the 4 quarters before/after, averaged across companies. Layoffs give clean event dates that quit-rate trends don't.

### GitLab rationale asymmetry

- MR description word count by change direction (expand/add vs. restrict/remove): Mann-Whitney U, report medians and a beeswarm plot.
- Rationale-type distribution by change direction: Fisher's exact (counts will be small).
- Qualitative layer: pull the rationale excerpts for every restriction event — these are the human texture for the write-up regardless of what the counts say.

## Validation

- Hand-code a stratified sample (~100 items) of locus labels before trusting the LLM pass; disagreements refine the codebook.
- LLM cross-model consensus on the full extraction; curated hard-case subset (unlimited PTO, EAP variants, "flexible work" phrasings) with Krippendorff's alpha as the reported reliability figure.
- Prompt sensitivity audit on the extraction prompt: rerun with paraphrased prompts, report label stability.
- Axis validation: LLM pairwise judgment on snippet pairs ("which reads as more care-oriented?") correlated with axis scores, as in the DEI work.

## Confounds and data-quality controls

- **Pay transparency laws** (CO 2021, NYC 2022, WA/CA 2023): flag company-years subject to disclosure mandates; run the benefits analyses with and without legally-compelled categories (compensation, insurance). Sabbaticals, mental health days, and shutdown weeks are the law-independent clean signal.
- **Wayback coverage audit** (Phase 0 gate): snapshot density per company per year for benefits subpages specifically, reported as a data-quality table in the appendix. Any apparent benefit disappearance must be checked against snapshot gaps before being coded as removal. Companies whose benefits migrated into an ATS get flagged; the migration itself is coded as an event, not a removal.
- **Vendor supply trend**: wellness-app mentions partly track the corporate wellness market's growth. Note it, and lean on the framing that the substitution claim is about system-level outcomes, not intent.
- **10-K human capital disclosures** (if used): mandate begins late 2020, so no pre-2020 baseline and a mandate-driven volume bump in 2021 — same confound class as pay transparency; date-flag it.

## Phases

**Phase 0 — Feasibility (gate).** Wayback coverage audit; GitLab path inventory across both repos; confirm MR descriptions retrievable via API. Kill criteria: if benefits-page coverage is sparse for >half the corpus, redesign around job postings (HN Who's Hiring) as the enumeration source before proceeding.

**Phase 1 — Instruments.** Draft taxonomy + locus codebook; write axis poles in register; hand-code validation sample; run hard-case reliability. Do not scale until Krippendorff on locus is acceptable (target ≥ 0.8 on the hard-case set).

**Phase 2 — Pilot on known ground truth.** GitLab F&F Day thread end-to-end through the flow pipeline (its arc is already known: May 2020 creation → monthly cadence Oct 2020 → 2023 conversion to permanent benefit); one corpus company (Coinbase, for continuity) through the stock pipeline. Pipeline is validated when it reproduces the known arcs.

**Phase 3 — Extraction at scale.** Full corpus rhetoric + benefits; full GitLab flow coding; human-in-the-loop CSV review pass.

**Phase 4 — Analysis.** Trajectories → changepoints → lag test → substitution tests → event studies → rationale asymmetry, in that order (each step's output feeds the next).

**Phase 5 — Robustness.** Confound sensitivity runs; alternate embedding model; prompt paraphrase audit.

**Phase 6 — Write-up.** Scrollytelling spine: individualization index as the quantitative through-line, GitLab rationale excerpts as human texture, CREDIT retirement as the ending, closing citation to "Resilience Is a Systems Problem."

## Outputs

- Cross-company individualization index chart (headline visual)
- Per-company small multiples (rhetoric + benefits composition)
- Lag-offset strip plot
- GitLab event timeline with rationale annotations
- Data-quality appendix (coverage table, reliability figures, sensitivity runs)
