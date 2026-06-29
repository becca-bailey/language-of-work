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
Status legend: [x] done (≥3 mission_brand chunks) · [~] partial (what Wayback
has, no more recoverable) · [NO] no Wayback coverage (SPA shell only — even a
browser render boots blank because the content loaded via un-archived APIs).

| done | year | url | notes |
| --- | --- | --- | --- |
| [x] | 2009 | facebook.com/careers/ | manual capture ingested |
| [x] | 2010 | facebook.com/careers/ | manual capture ingested |
| [x] | 2011 | facebook.com/careers/ | manual capture ingested |
| [NO] | 2012 | facebook.com/careers/ | no Wayback coverage — SPA-related errors, only 1 thin chunk recoverable |
| [x] | 2013 | facebook.com/careers/ | manual capture ingested |
| [x] | 2014 | facebook.com/careers/ | manual capture ingested |
| [x] | 2015 | facebook.com/careers/ | manual capture ingested |
| [x] | 2016 | facebook.com/careers/ | manual capture ingested |
| [x] | 2017 | facebook.com/careers/ | manual capture ingested |
| [x] | 2018 | facebook.com/careers/ | manual capture ingested |
| [x] | 2019 | facebook.com/careers/ | manual capture ingested |
| [x] | 2020 | facebook.com/careers/facebook-life/{,diversity,benefits} | manual capture ingested |
| [x] | 2021 | facebook.com/careers/facebook-life/{,diversity} | manual capture ingested |
| [x] | 2022 | metacareers.com/facebook-life/{,diversity,benefits} | manual capture ingested |
| [~] | 2023 | metacareers.com/facebook-life/ | mostly SPA shells; per-pattern fetch auto-recovered 2 mission_brand chunks. archive.today for more |
| [~] | 2024 | metacareers.com/facebook-life/ | per-pattern fetch auto-recovered 2 mission_brand chunks; root/diversity snapshots are shells |

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

Current mission_brand counts by year: {2009: 4, 2010: 4, 2011: 5, 2012: 1, 2013: 8, 2014: 7, 2015: 8, 2016: 13, 2017: 9, 2018: 7, 2019: 3, 2020: 16, 2021: 16, 2022: 17, 2023: 2, 2024: 2, 2025: 10, 2026: 11}
(Updated 2026-06-29. 2012 = no coverage (1 chunk); 2023/2024 partial (2 each, auto-recovered by per-pattern subpath fetch).)
