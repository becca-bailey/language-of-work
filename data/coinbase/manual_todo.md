# Manual-capture worklist — Coinbase

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/coinbase/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/coinbase/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company coinbase`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2015 | coinbase.com/careers | https://web.archive.org/web/20150601000000*/coinbase.com/careers |
| [ ] | 2016 | coinbase.com/careers | https://web.archive.org/web/20160601000000*/coinbase.com/careers |
| [ ] | 2017 | coinbase.com/careers | https://web.archive.org/web/20170601000000*/coinbase.com/careers |
| [ ] | 2018 | coinbase.com/careers | https://web.archive.org/web/20180601000000*/coinbase.com/careers |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2015_careers.html",
      "url": "https://coinbase.com/careers",
      "capture_date": "20150601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2013: 3, 2014: 3, 2015: 1, 2016: 1, 2017: 1, 2018: 1, 2019: 6, 2020: 6, 2021: 10, 2022: 5, 2023: 3, 2024: 4, 2025: 4, 2026: 6}
