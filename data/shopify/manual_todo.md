# Manual-capture worklist — Shopify

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/shopify/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/shopify/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company shopify`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2011 | shopify.com/careers | https://web.archive.org/web/20110601000000*/shopify.com/careers |
| [ ] | 2013 | shopify.com/careers | https://web.archive.org/web/20130601000000*/shopify.com/careers |
| [ ] | 2014 | shopify.com/careers | https://web.archive.org/web/20140601000000*/shopify.com/careers |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2011_careers.html",
      "url": "https://shopify.com/careers",
      "capture_date": "20110601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2010: 3, 2011: 2, 2012: 5, 2013: 1, 2014: 1, 2015: 6, 2016: 6, 2017: 3, 2018: 7, 2019: 9, 2020: 6, 2021: 9, 2022: 8, 2023: 11, 2024: 11, 2025: 8, 2026: 38}
