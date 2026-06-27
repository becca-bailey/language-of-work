# Manual-capture worklist — Meta

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/meta/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/meta/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company meta`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2009 | facebook.com/careers/ | https://web.archive.org/web/20090601000000*/facebook.com/careers/ |
| [ ] | 2010 | facebook.com/careers/ | https://web.archive.org/web/20100601000000*/facebook.com/careers/ |
| [ ] | 2011 | facebook.com/careers/ | https://web.archive.org/web/20110601000000*/facebook.com/careers/ |
| [ ] | 2012 | facebook.com/careers/ | https://web.archive.org/web/20120601000000*/facebook.com/careers/ |
| [ ] | 2013 | facebook.com/careers/ | https://web.archive.org/web/20130601000000*/facebook.com/careers/ |
| [ ] | 2014 | facebook.com/careers/ | https://web.archive.org/web/20140601000000*/facebook.com/careers/ |
| [ ] | 2015 | facebook.com/careers/ | https://web.archive.org/web/20150601000000*/facebook.com/careers/ |
| [ ] | 2016 | facebook.com/careers/ | https://web.archive.org/web/20160601000000*/facebook.com/careers/ |
| [ ] | 2017 | facebook.com/careers/ | https://web.archive.org/web/20170601000000*/facebook.com/careers/ |
| [ ] | 2018 | facebook.com/careers/ | https://web.archive.org/web/20180601000000*/facebook.com/careers/ |
| [ ] | 2019 | facebook.com/careers/ | https://web.archive.org/web/20190601000000*/facebook.com/careers/ |
| [ ] | 2020 | facebook.com/careers/ | https://web.archive.org/web/20200601000000*/facebook.com/careers/ |
| [ ] | 2021 | facebook.com/careers/ | https://web.archive.org/web/20210601000000*/facebook.com/careers/ |
| [ ] | 2022 | facebook.com/careers/ | https://web.archive.org/web/20220601000000*/facebook.com/careers/ |
| [ ] | 2023 | facebook.com/careers/ | https://web.archive.org/web/20230601000000*/facebook.com/careers/ |
| [ ] | 2024 | facebook.com/careers/ | https://web.archive.org/web/20240601000000*/facebook.com/careers/ |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2009_careers.html",
      "url": "https://facebook.com/careers/",
      "capture_date": "20090601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2009: 1, 2010: 1, 2011: 2, 2012: 1, 2015: 1, 2016: 1, 2017: 1, 2018: 1, 2025: 8, 2026: 11}
