# Manual-capture worklist — Google

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## Status (2026-06-30)

The 2018–2023 SPA gap is **resolved** — `careers.google.com/` is an app-shell
those years, but `diversity.google/`, `diversity.google/annual-report/`, and
`about.google/belonging/` are server-rendered and were fetched through the normal
pipeline (no manual capture). 2020 and 2021 went from 0 → 42 / 15 mission chunks.

The remaining flagged years are all the **legacy 2006–2013 era** — thin, *not*
shells. `google.com/jobs/` → `intl/en/jobs/` → `about/jobs/` are server-rendered
but short on mission prose. Low priority; a better in-era URL or deeper fetch may
recover them before any hand-capture is warranted.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/google/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/google/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company google`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2006 | google.com/jobs/ | https://web.archive.org/web/20060601000000*/google.com/jobs/ |
| [ ] | 2008 | google.com/jobs/ | https://web.archive.org/web/20080601000000*/google.com/jobs/ |
| [ ] | 2009 | google.com/jobs/ | https://web.archive.org/web/20090601000000*/google.com/jobs/ |
| [ ] | 2010 | google.com/jobs/ | https://web.archive.org/web/20100601000000*/google.com/jobs/ |
| [ ] | 2011 | google.com/jobs/ | https://web.archive.org/web/20110601000000*/google.com/jobs/ |
| [ ] | 2013 | google.com/jobs/ | https://web.archive.org/web/20130601000000*/google.com/jobs/ |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2006_careers.html",
      "url": "https://google.com/jobs/",
      "capture_date": "20060601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2005: 4, 2006: 2, 2007: 5, 2008: 2, 2009: 1, 2010: 2, 2011: 1, 2012: 33, 2013: 2, 2014: 34, 2015: 26, 2016: 15, 2017: 7, 2018: 20, 2019: 54, 2020: 42, 2021: 15, 2022: 34, 2023: 27, 2024: 23, 2025: 46}
