# The Language of Work

## Project 1: Careers Page Archaeology

## Project Goal

Analyze how companies describe themselves as employers over time by extracting historical careers-page content from the Internet Archive and measuring movement along interpretable value dimensions such as altruism, community, innovation, ownership, urgency, stability, inclusion, performance, and efficiency.

Example questions:

- When was Google's careers page most aligned with altruism?
- When did Amazon's language become more performance-oriented?
- How has AI-related language spread through tech recruiting?
- How does company self-description diverge from worker narratives?

## Measurement Philosophy

Three principles shape the methodology:

1. **Embeddings are the primary measurement instrument.** They are geometric and don't form opinions. This avoids the inconsistency problem of asking an LLM "which text is more altruistic?" when the honest answer may be "neither" or "both." Note: embedding APIs are not strictly bit-deterministic across calls, so determinism comes from a **cache-first design** — every unique text is embedded exactly once (keyed by text hash + model version) and stored permanently; re-runs read the cache and nothing is ever re-embedded.
2. **Semantic axes via contrast pairs, not single descriptor vectors.** A lone "altruism" descriptor mostly measures topic overlap. Defining each dimension as the _difference_ between two opposed descriptor embeddings (idealism ↔ commercial pragmatism) cancels out the shared careers-page register and gets closer to measuring stance. Scores are signed projections onto the axis.
3. **LLMs are used where they're strong and validated where they're weak.** A small LLM classifies chunks by type (cheap, easy to validate against a hand-labeled set). LLM pairwise judgment is used only as a _cross-check_ on embedding findings — agreement strengthens a claim; disagreement becomes a documented case study, not a silent override.

A neutral control axis (e.g., application logistics ↔ office locations) runs through every analysis. If a values axis and the control axis move together, the signal is page composition, not values.

---

## Phase 1: Proof of Concept

**Goal:** Analyze a single company across time and validate the full pipeline against a known ground truth: the hypothesis that Google's idealism peaked around 2014. If the method can't recover an effect we can see by eye, it isn't ready for claims we can't.

**Target company:** Google

**Target URL patterns (query all; treat as one corpus):**

- google.com/jobs and google.com/intl/\*/jobs (early era)
- google.com/about/careers (canonical careers home for much of ~2012–2018)
- careers.google.com
- about.google/careers
- jobs.google.com

The full pattern list is confirmed by manual URL archaeology before fetching (see manual steps).

**Time range:** 2005–present

**Sampling:** 3–4 snapshots per year (not one — single captures are brittle). Select the snapshot with the best extraction coverage per year; record the others as fallbacks.

**Deliverable:** A chart showing the altruism axis over time, with a control axis, per-year coverage flags, and the top-matching chunks displayed as evidence quotes — validated against the 2014 hypothesis.

### Step 1: Fetch Wayback Snapshots

`scripts/fetch_snapshots.py`

- Query the Wayback CDX API across all URL patterns (filter to status 200; collapse to ~monthly granularity)
- **Dedup by CDX digest:** the CDX API returns a content digest per capture, so byte-identical captures are skipped before download — this also surfaces "the page was untouched for N years" for free
- Retrieve 3–4 candidate snapshots per year, spread across the year
- **Fetch raw content via the `id_` flag** (`https://web.archive.org/web/{timestamp}id_/{url}`) — returns original bytes without the Wayback toolbar/URL-rewriting that would pollute extraction
- Rate-limit politely (~1 req/sec with retries)
- For SPA-era pages (~2015+), also check CDX for archived JSON/API responses near the same timestamps — rendered content often lives there
- Store metadata: timestamp, URL pattern, HTTP status, digest, capture quality notes

**Output:** `data/google/snapshots.json`

### Step 2: Extract and Chunk

`scripts/extract_chunks.py`

- Download archived HTML (store raw HTML permanently — re-extraction should never require re-fetching)
- Chunk on **document structure, not token windows**: walk the DOM, emit one chunk per heading-plus-content block or substantial paragraph, carrying the nearest heading as context
- Target 50–300 words per chunk; merge fragments, split oversized blocks at paragraph boundaries
- Run Trafilatura in parallel as a comparison/fallback for malformed pages
- Log **extraction coverage** per snapshot: chunk count, total words. Thin years get flagged on the final chart, not silently absorbed

**Output:** `data/google/chunks/{year}.jsonl` — one record per chunk with text, heading context, source URL, timestamp

### Step 3: Classify Chunks (AI-assisted, human-validated)

`scripts/classify_chunks.py`

- Small LLM (Haiku-class, pinned version, temperature 0) labels every chunk: `mission_brand`, `job_listing`, `benefits_perks`, `process_logistics`, `legal_boilerplate`, `navigation_junk`
- **Validation loop:** hand-label a random sample of 75–100 chunks first; iterate the prompt until classifier agreement reaches ~90%; then trust with spot-checks
- Analysis corpus = `mission_brand` chunks (keep `benefits_perks` as a secondary track — benefits language has its own drift story)

### Step 4: Inspect the Data

Manual gate before any embedding work:

- Read the mission chunks for several years end to end
- Is extraction quality acceptable? Is mission language preserved? Are menus gone?
- Do the SPA-era years have enough text, or do they need the archived-JSON fallback?
- Run **near-duplicate detection** across adjacent years (embedding cosine or shingling) to identify which chunks are new each year — "the mission copy was untouched 2016–2019, then rewritten in 2020" is itself a finding, and new-text years deserve extra reading

Do not proceed until extraction quality is validated.

### Step 5: Generate Embeddings

`scripts/embed_chunks.py`

- Embed at the **chunk level**, never whole pages
- **Model:** OpenAI `text-embedding-3-large`, pinned; record model version on every row (mixed-model embeddings are not comparable)
- **Cache-first:** embeddings keyed by text hash + model version; a text is never embedded twice
- **Storage for POC:** parquet files (`data/google/embeddings.parquet`). Defer Supabase/pgvector until Phase 3 multiplies the data

### Step 6: Build Semantic Axes

`scripts/build_axes.py`

Each dimension is a contrast pair. Embed 6–10 sentences per pole, average per pole, axis = pole A minus pole B (normalized).

**Descriptor construction rules:**

1. **Write in the register of the corpus, not as abstract concepts.** Careers pages never say "altruism" — they say "we want to make the world a better place." Embedding similarity is heavily influenced by register and style, so a single-word or dictionary-style descriptor partly measures how academic a chunk sounds rather than what stance it takes. Descriptors are full sentences in first-person corporate careers-page voice.
2. **Vary surface form, hold stance constant.** Each pole is a set of 6–10 sentences with different structures and vocabulary but the same underlying value. Averaging cancels idiosyncratic phrasing and leaves the shared meaning. One stylized sentence per pole would measure similarity to that phrasing, not the concept.
3. **Write both poles in the same voice.** When both poles share the careers-page register, the register cancels in the subtraction and the axis isolates stance.
4. **Keep each pole conceptually tight.** "We want to make the world a better place" (company impact on the world) and "working here makes you a better person" (the job's effect on the worker) are different concepts. Mixing related-but-distinct ideas in one pole blurs the axis — genuinely different ideas become genuinely different axes.
5. **Avoid circularity.** Don't lift phrases verbatim from the corpus being measured — if the altruism pole is built from Google's 2014 copy, Google 2014 winning is circular, not a finding. Paraphrase, or borrow phrasing styles from companies outside the comparison set.

**Workflow:** have an LLM generate 15–20 candidate sentences per pole ("write sentences a tech careers page might use that express X"), hand-curate down to the 6–10 that are on-concept and varied in form.

**Altruism axis (Phase 1), illustrative poles:**

- Pole A (idealism): "We want to make the world a better place." / "Our work improves people's lives." / "Come do work that matters to society." / "Everything we build is in service of a greater social good." / "Join us in empowering communities everywhere." / "Do work you believe in."
- Pole B (commercial pragmatism): "We are focused on delivering results for our customers." / "Our teams drive growth and win in the market." / "We hold ourselves to the highest standards of operational excellence." / "Join us in building a category-leading business." / "We execute with discipline to stay ahead of the competition."

**Control axis:** application logistics ("Here's how to apply for a role." / "Our interview process has four stages." / "Submit your resume through our portal.") ↔ office facts ("We have offices in twelve cities." / "Visit our headquarters campus." / "Our locations span three continents."). Movement here means page composition changed, not values.

Store axis definitions (sentence sets + embeddings + model version) in version control — axes are part of the experiment and must be reproducible.

### Step 7: Score and Aggregate

`scripts/score_axes.py`

- Project every mission chunk onto each axis (signed scalar)
- Aggregate per year with **adaptive top-k mean** (`k = min(5, n)`, recording `n` per year) rather than averaging all chunks — mission language shouldn't be diluted by the rest, and thin years stay honest in coverage flags
- **Z-score within company** across years; never compare raw projections across different axes
- Output: `data/google/axis_scores.parquet` plus the top-scoring chunks per year (these are the evidence quotes)

### Step 8: Validate

Three checks before believing anything:

1. **Ground truth:** does the altruism axis peak near 2014 for Google? Does the control axis stay flat while it moves?
2. **LLM cross-check:** run a small pairwise tournament — "here are mission chunks from Google {year A} and {year B}; which expresses more idealistic, world-improving framing?" with randomized presentation order, temperature 0, pinned model. Fit win rates (or Bradley-Terry) into a ranking. Compare against the embedding ranking. Agreement → finding. Disagreement → investigate the chunks; usually it's a vocabulary shift without a stance shift, which is itself worth writing up.
3. **Axis-sentence robustness:** perturb the axis definitions (leave-one-sentence-out per pole) and confirm the year ranking holds (high rank correlation across perturbations). Cheap, and validates the methodology before any claims — promoted here from the risks list.

### Step 9: Build Visualization

Next.js frontend (visualization only — the entire data pipeline stays in Python; the frontend reads pipeline output as static JSON/parquet exports).

Page: `/google/altruism`

- Yearly trend line (z-scored axis projection) with the control axis overlaid
- Coverage flags on thin/lossy years
- Top-matching chunks per year displayed as quotes — the WHY, not just the THAT
- New-vs-carried-forward indicator per year from the dedup analysis

### Phase 1 deferred refinements

Identified during Phase 1 validation; park until after the Phase 1 writeup:

1. **Sentence-level scoring.** The 2005–2006 embedding-vs-LLM disagreement
   (see `data/google/validation_report.md` case study) showed chunk-level
   projection under-credits idealism on dense single-page-era sites: the
   idealistic sentence projects at 2014-peak levels, but the 400-word chunk
   averaging dilutes it. Refinement: project sentences within mission chunks
   and aggregate top-k sentences per year, making scores comparable across
   page-architecture eras. Show both series on the chart.
2. **SPA-era archived JSON fallback.** 2018–2022 has no extractable mission
   text (client-rendered careers.google.com). The fetch already recorded
   2,275 archived JSON candidates in `snapshots.json`; build a parser that
   pulls rendered copy out of the most promising endpoints and feeds it into
   the same chunk → classify → embed pipeline.

---

## Phase 2: Full Axis Set

Add contrast-pair axes (all built under the Step 6 descriptor rules — full sentences, careers-page voice, conceptually tight poles):

- Community ↔ individual performance
- Innovation ↔ proven practices
- Stability ↔ urgency/velocity
- Ownership ↔ direction-following
- Efficiency ↔ craft/thoroughness
- Inclusion ↔ elite selectivity
- **Work as calling ↔ work as job** — "Working here makes you a better person." / "This is more than a job — it's a mission." vs. "We offer competitive pay for skilled work." / "Great work, reasonable hours, real life outside the office." This is distinct from the altruism axis (the job's effect on the worker, not the company's effect on the world) and tracks one of the most loaded shifts in tech recruiting language.

Each axis gets the same treatment: sentence sets in version control, control comparison, top-k aggregation, within-company z-scoring.

**Visualization:** company radar chart by year (built from z-scores, since raw projections aren't comparable across axes).

**Validation carries forward:** spot-check 2–3 axes with LLM pairwise tournaments.

## Phase 3: Multiple Companies

Companies: Google, Microsoft, Amazon, Meta, OpenAI, Shopify, Stripe.

- Re-run the pipeline per company; expect per-company URL archaeology (each has its own careers-domain history)
- For cross-company comparison, z-score within the **pooled corpus** per axis (within-company z-scores answer "how has Google changed"; pooled scores answer "who sounds most efficiency-oriented in 2020")
- Migrate storage to Supabase/pgvector here if useful for the frontend

**Deliverables:** cross-company comparisons — most idealistic company language by year, most performance-oriented by year, convergence/divergence of the field over time.

## Phase 4: Worker Narrative Comparison

Compare company rhetoric against worker narratives, with realistic data sourcing:

- **Hacker News:** primary source — full corpus available via BigQuery and the Algolia API; "working at X" threads are abundant
- **Reddit:** limited since the 2023 API changes; treat as supplementary where data is accessible
- **Glassdoor:** scraping violates ToS; use existing academic datasets if available, otherwise drop. Do not build the phase around it
- Possible additions: archived Blind discussions, levels.fyi reviews, engineering-blog "why I joined/left" posts

Method: same chunk → classify → embed → project pipeline on worker text, then measure rhetoric–experience divergence per axis per year (e.g., careers-page community score rising while worker-narrative community score falls).

## Future Research Directions

The open-ended discovery track — where embeddings do what LLM scoring can't:

- **Theme emergence:** cluster all mission chunks across companies and years (HDBSCAN / BERTopic-style), LLM-label the clusters, track which themes grow, shrink, appear, and die
- **Drift maps:** UMAP trajectories of companies moving through embedding space over time
- AI language diffusion through recruiting copy
- Hiring expectation inflation
- Corporate euphemism tracking
- Comparison across economic cycles (does idealism language track the funding environment?)

## Tech Stack Summary

- **Pipeline:** Python end to end (fetch, extract, chunk, classify, embed, score), structured as a shared library (`src/lowork/`) with thin script entry points — fetch client, chunking, embedding cache, and axis math are reused across steps
- **Storage:** raw HTML on disk + parquet/JSONL through Phase 2; pgvector in Phase 3 if needed
- **Models:** one pinned embedding model recorded on every row; one pinned small LLM for classification; one pinned LLM for pairwise validation; temperature 0 everywhere
- **Frontend:** Next.js, reads static pipeline exports

## Known Risks and Confounds

- **Genre drift:** a 2008 careers page and a 2022 careers page are different kinds of artifact (brand copy vs. product surface). Partially controlled by chunk classification and the control axis; name it explicitly in the writeup
- **SPA-era extraction loss:** some years will be thin; flag, don't interpolate
- **Embedding topic-dominance:** mitigated but not eliminated by contrast pairs; the LLM cross-check exists for this reason
- **Axis phrase sensitivity:** results may shift with descriptor wording; test robustness by perturbing phrase sets and confirming rankings hold
- **Model deprecation:** pinned models get retired; raw text + stored embeddings + versioned axis definitions make re-runs possible

## Naming

**The Language of Work** is the umbrella for this and related projects over time (worker-story clustering, careers-page archaeology, rhetoric-vs-experience divergence, future explorations). Individual projects keep descriptive subtitles — this one is **Careers Page Archaeology**; "semantic drift" remains available as the name of the technique/measurement within it.
