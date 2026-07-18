# The Language of Work

Analyzing how companies describe themselves as employers over time, using
archived careers pages from the Wayback Machine and embedding-based semantic
axes. See [docs/counterforces-thesis.md](docs/counterforces-thesis.md) for the
guiding thesis, and the pipeline table below for the methodology.

**Project 1: Careers Page Archaeology** — measures how 19 companies'
careers-page language shifts over time across ten embedding-based semantic
axes (idealism ↔ commercial pragmatism, DEI register, performance intensity,
craft, wellbeing, and more), with a neutral control axis as a semantic control
for altruism. The findings are written up as data-driven stories
(`astro/src/content/stories/`): altruism, craft-ai, dei, power, wellbeing, and
the Netflix culture study. New companies are added by dropping in a per-company
profile — no new scripts.

## Setup

```bash
uv sync
cp .env.example .env   # then fill in OPENAI_API_KEY and ANTHROPIC_API_KEY
```

### Embedding cache

`data/embedding_cache/` is a SQLite store of every embedding we've ever computed,
keyed by `sha256(text)`. It's a pipeline-time artifact — the deployed site never
reads it — and it's too large for git, so it lives in Cloudflare R2 instead of the
repo. Re-embedding from scratch costs real OpenAI money, so:

```bash
./scripts/cache_sync.sh pull   # on a fresh clone, restore the cache from R2
./scripts/cache_sync.sh push   # after any run that embeds new text, back it up
```

Requires an rclone remote named `cloudflare` pointing at the `language-of-work`
R2 bucket. With no cache present the pipeline still works — it just re-embeds
(and re-pays) on first run.

## Pipeline

**Everyday path.** After manually fetching new data (`fetch_snapshots.py
discover` / `fetch`), let the orchestrator run the rest — it detects which
companies changed and runs only the stale stages, in dependency order, for the
stories enabled in `pipeline.yaml`:

```bash
uv run scripts/pipeline.py status     # coverage table + figures to eyeball
uv run scripts/pipeline.py diff        # what would run, and why (no writes)
uv run scripts/pipeline.py run         # run stale stages for enabled stories
uv run scripts/pipeline.py validate    # coverage assertions (warn-only)
uv run scripts/pipeline.py baseline    # run ONCE on adoption: mark current corpus clean
```

The stage DAG and per-stage inputs/outputs live in `src/lowork/pipeline.py`;
story enable/disable and per-story company allow-lists live in `pipeline.yaml`.
Company membership filters exports; per-company analysis runs for the union of
the enabled stories that need it. `validate` catches coverage gaps (e.g. chunks
that were never DEI-register-classified) before they become silent zeros.

The manual stage reference below is what those stages do, in order. Steps marked
MANUAL GATE require human review before continuing.

| # | Command | What it does |
|---|---------|--------------|
| 0 | — | MANUAL (M1): review `docs/manual/M1-url-archaeology.md`, confirm URL patterns in `data/<company>/url_patterns.json` |
| 1 | `uv run scripts/fetch_snapshots.py discover --company <name>` | CDX capture counts per pattern/year (input to M1) |
| 2 | `uv run scripts/fetch_snapshots.py fetch --company <name>` | Download 3–4 snapshots/year of raw HTML |
| 3 | — | MANUAL (M2): spot-check `data/google/spotcheck_links.md` in a browser |
| 4 | `uv run scripts/extract_chunks.py` | DOM-walk chunking + coverage stats |
| 5 | `uv run scripts/label_sample.py` | Emit `data/google/labels/sample.csv` for hand-labeling |
| 6 | — | MANUAL (M3): fill in the `label` column of `sample.csv` |
| 7 | `uv run scripts/classify_chunks.py` | Haiku classification + agreement report vs your labels |
| 8 | — | MANUAL (M4): read mission chunks end to end (`data/google/mission_review.md`); hard gate |
| 9 | `uv run scripts/generate_axis_candidates.py` | LLM candidate sentences per pole |
| 10 | — | MANUAL (M5): curate candidates into `axes/*.yaml` |
| 11 | `uv run scripts/embed_chunks.py` | Cache-first embeddings for analysis chunks |
| 12 | `uv run scripts/build_axes.py` | Build axis vectors + circularity check |
| 13 | `uv run scripts/score_axes.py` | Project, top-k aggregate, z-score, dedup analysis |
| 14 | `uv run scripts/validate_altruism_axes.py` | 2014 check, LLM tournament, perturbation test |
| 15 | — | MANUAL (M6): review `data/google/validation_report.md` |
| 16 | `uv run scripts/export_web.py` | Export per-company JSON for the Astro frontend |
| 17 | `cd astro && npm run dev` | Visualization at `/explore/altruism/google` or `/explore/altruism/compare` |

Pass `--company <name>` on every script (defaults to `google`). After exporting
two or more companies, the home page links to side-by-side comparison views.
(The DEI / craft-ai / power / wellbeing / netflix-culture stories have their
own scorers and exporters; the orchestrator above runs the full set.)

## Adding a new company

Each company is a profile file at `data/<company>/url_patterns.json` — no new
scripts required. Copy an existing profile (e.g. `data/amazon/url_patterns.json`)
and edit these keys:

| Key | Purpose |
|-----|---------|
| `company` / `display_name` | Slug and human label |
| `patterns` | Hub careers URLs to query in the Wayback CDX API |
| `hosts` | Domains allowed during link expansion (`expand_links.py`) |
| `spa_content_paths` | Paths for SPA-era deep sampling (`recover_spa.py deep-sample`) |
| `alt_domains` | Alternate mission-bearing domains (`recover_spa.py probe-domains`) |
| `spa_json_probes` | JSON API endpoints to probe (optional) |
| `validation` | Optional ground-truth hypothesis, e.g. `{"expected_altruism_peak": 2014, "tolerance": 2}` |

Workflow:

1. **M1 archaeology** — draft `patterns` using `docs/manual/M1-url-archaeology.md`
2. **Discover** — `uv run scripts/fetch_snapshots.py discover --company <name>`;
   review `data/<company>/discovery_report.md` and remove zero-capture patterns
3. **Fetch through score** — run steps 2–13 with `--company <name>`, or just add
   the company to `pipeline.yaml` and run `uv run scripts/pipeline.py run`
4. **Export** — `uv run scripts/export_web.py --company <name>` updates
   `astro/src/data/companies.json` for the comparison view

Per-company profiles for the full cohort (the `companies:` list in
`pipeline.yaml` — 19 companies as of 2026-07) live under `data/<name>/`.

## Layout

- `src/lowork/` — shared library (Wayback client, chunking, classification, embedding cache, axis math)
- `scripts/` — thin CLI entry points
- `axes/` — versioned axis definitions (curated sentence sets); `axes/candidates/` holds raw LLM output
- `data/<company>/` — company profile (`url_patterns.json`), raw HTML (gitignored), chunk JSONL, embeddings, scores
- `src/lowork/company.py` — `CompanyProfile` loader for per-company config
- `src/lowork/pipeline.py` — orchestrator: stage DAG, change detection, runner
- `pipeline.yaml` — enabled stories + per-story company allow-lists
- `astro/` — Astro frontend, reads the static JSON exports under `astro/src/data/`
  - The `control` axis is a comparison overlay only: keep it out of all navigation
    (home page, topic pages, compare links). `export_web.py` excludes it from the
    `companies.json` manifest axes, and axis routes 404 on `/.../control` directly.
