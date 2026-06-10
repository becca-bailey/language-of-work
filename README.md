# The Language of Work

Analyzing how companies describe themselves as employers over time, using
archived careers pages from the Wayback Machine and embedding-based semantic
axes. See [docs/the-language-of-work-plan.md](docs/the-language-of-work-plan.md)
for the full project plan and methodology.

**Project 1: Careers Page Archaeology** — Phase 1 targets Google, 2005–present,
on the altruism (idealism ↔ commercial pragmatism) axis with a neutral control axis.

## Setup

```bash
uv sync
cp .env.example .env   # then fill in OPENAI_API_KEY and ANTHROPIC_API_KEY
```

## Pipeline

Run in order. Steps marked MANUAL GATE require human review before continuing.

| # | Command | What it does |
|---|---------|--------------|
| 0 | — | MANUAL (M1): review `docs/manual/M1-url-archaeology.md`, confirm URL patterns in `data/google/url_patterns.json` |
| 1 | `uv run scripts/fetch_snapshots.py discover` | CDX capture counts per pattern/year (input to M1) |
| 2 | `uv run scripts/fetch_snapshots.py fetch` | Download 3–4 snapshots/year of raw HTML |
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
| 18 | `cd web && npm run dev` | Visualization at `/google/altruism` |

## Layout

- `src/lowork/` — shared library (Wayback client, chunking, classification, embedding cache, axis math)
- `scripts/` — thin CLI entry points
- `axes/` — versioned axis definitions (curated sentence sets); `axes/candidates/` holds raw LLM output
- `data/<company>/` — raw HTML (gitignored), chunk JSONL, embeddings, scores
- `web/` — Next.js frontend, reads static exports
