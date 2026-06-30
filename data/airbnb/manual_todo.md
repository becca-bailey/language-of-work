# Manual-capture worklist — Airbnb

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/airbnb/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/airbnb/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company airbnb`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2020_careers.html",
      "url": "https://careers.airbnb.com/",
      "capture_date": "20200601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2015: 10, 2016: 9, 2017: 13, 2018: 7, 2019: 6, 2020: 7, 2021: 10, 2022: 6, 2023: 7, 2024: 3, 2025: 3}
