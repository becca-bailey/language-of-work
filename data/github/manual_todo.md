# Manual-capture worklist — GitHub

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/github/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/github/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company github`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2011 | github.com/about | https://web.archive.org/web/20110601000000*/github.com/about |
| [ ] | 2012 | github.com/about | https://web.archive.org/web/20120601000000*/github.com/about |
| [ ] | 2013 | github.com/about | https://web.archive.org/web/20130601000000*/github.com/about |
| [ ] | 2014 | github.com/about | https://web.archive.org/web/20140601000000*/github.com/about |
| [ ] | 2015 | github.com/about | https://web.archive.org/web/20150601000000*/github.com/about |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2011_careers.html",
      "url": "https://github.com/about",
      "capture_date": "20110601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2011: 1, 2012: 2, 2013: 1, 2014: 1, 2015: 2, 2016: 3, 2017: 5, 2018: 5, 2019: 3, 2020: 4, 2021: 7, 2022: 8, 2023: 7, 2024: 7, 2025: 7, 2026: 5}
