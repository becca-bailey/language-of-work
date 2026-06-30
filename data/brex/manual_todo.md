# Manual-capture worklist — Brex

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/brex/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/brex/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company brex`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2019 | brex.com/careers | https://web.archive.org/web/20190601000000*/brex.com/careers |
| [ ] | 2020 | brex.com/careers | https://web.archive.org/web/20200601000000*/brex.com/careers |
| [ ] | 2022 | brex.com/careers | https://web.archive.org/web/20220601000000*/brex.com/careers |
| [ ] | 2023 | brex.com/careers | https://web.archive.org/web/20230601000000*/brex.com/careers |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2019_careers.html",
      "url": "https://brex.com/careers",
      "capture_date": "20190601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2019: 1, 2020: 1, 2021: 11, 2022: 2, 2023: 2, 2024: 17, 2025: 10, 2026: 8}
