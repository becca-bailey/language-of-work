# The Language of Work

Analyzing how companies describe themselves as employers over time, using
archived careers pages from the Wayback Machine and embedding-based semantic
axes. See [docs/the-language-of-work-plan.md](docs/the-language-of-work-plan.md)
for the full project plan and methodology.

**Project 1: Careers Page Archaeology** — Phase 1 proved the pipeline on Google;
Phase 2 adds Amazon and Meta using the same scripts with per-company profiles.
All companies are measured on the altruism (idealism ↔ commercial pragmatism) axis
with a neutral control axis.

## Setup

```bash
uv sync
cp .env.example .env   # then fill in OPENAI_API_KEY and ANTHROPIC_API_KEY
```

## Pipeline

Run in order. Steps marked MANUAL GATE require human review before continuing.

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
| 14 | `uv run scripts/validate.py` | 2014 check, LLM tournament, perturbation test |
| 15 | — | MANUAL (M6): review `data/google/validation_report.md` |
| 16 | `uv run scripts/make_chart.py` | Plotly validation chart |
| 17 | `uv run scripts/export_web.py` | Export JSON for the Next.js frontend |
| 18 | `cd web && npm run dev` | Visualization at `/google/altruism` or `/compare/altruism` |

Pass `--company <name>` on every script (defaults to `google`). After exporting
two or more companies, the home page links to side-by-side comparison views.

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
3. **Fetch through score** — run steps 2–13 with `--company <name>`
4. **Export** — `uv run scripts/export_web.py --company <name>` updates
   `web/public/data/companies.json` for the comparison view

Draft profiles for Amazon and Meta are in `data/amazon/` and `data/meta/` with
CDX discovery reports already generated.

## Layout

- `src/lowork/` — shared library (Wayback client, chunking, classification, embedding cache, axis math)
- `scripts/` — thin CLI entry points
- `axes/` — versioned axis definitions (curated sentence sets); `axes/candidates/` holds raw LLM output
- `data/<company>/` — company profile (`url_patterns.json`), raw HTML (gitignored), chunk JSONL, embeddings, scores
- `src/lowork/company.py` — `CompanyProfile` loader for per-company config
- `web/` — Next.js frontend, reads static exports
  - The `control` axis is a comparison overlay only: keep it out of all navigation
    (home page, topic pages, compare links). `export_web.py` excludes it from the
    `companies.json` manifest axes, and axis routes 404 on `/.../control` directly.
