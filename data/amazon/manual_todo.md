# Manual-capture worklist — Amazon

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/amazon/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/amazon/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company amazon`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2007 | amazon.com/careers | https://web.archive.org/web/20070601000000*/amazon.com/careers |
| [ ] | 2008 | amazon.com/careers | https://web.archive.org/web/20080601000000*/amazon.com/careers |
| [ ] | 2009 | amazon.com/careers | https://web.archive.org/web/20090601000000*/amazon.com/careers |
| [ ] | 2010 | amazon.com/careers | https://web.archive.org/web/20100601000000*/amazon.com/careers |
| [ ] | 2011 | amazon.com/careers | https://web.archive.org/web/20110601000000*/amazon.com/careers |
| [ ] | 2012 | amazon.com/careers | https://web.archive.org/web/20120601000000*/amazon.com/careers |
| [ ] | 2013 | amazon.com/careers | https://web.archive.org/web/20130601000000*/amazon.com/careers |
| [ ] | 2014 | amazon.com/careers | https://web.archive.org/web/20140601000000*/amazon.com/careers |
| [ ] | 2015 | amazon.com/careers | https://web.archive.org/web/20150601000000*/amazon.com/careers |
| [ ] | 2022 | amazon.com/careers | https://web.archive.org/web/20220601000000*/amazon.com/careers |
| [ ] | 2024 | amazon.com/careers | https://web.archive.org/web/20240601000000*/amazon.com/careers |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2007_careers.html",
      "url": "https://amazon.com/careers",
      "capture_date": "20070601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2007: 2, 2008: 2, 2011: 2, 2013: 2, 2014: 2, 2016: 17, 2017: 44, 2018: 45, 2019: 18, 2020: 18, 2021: 17, 2022: 1, 2023: 3, 2024: 2, 2025: 4, 2026: 8}
