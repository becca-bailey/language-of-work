# Manual-capture worklist — Stripe

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/stripe/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/stripe/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company stripe`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2012 | stripe.com/jobs | https://web.archive.org/web/20120601000000*/stripe.com/jobs |
| [ ] | 2013 | stripe.com/jobs | https://web.archive.org/web/20130601000000*/stripe.com/jobs |
| [ ] | 2021 | stripe.com/jobs | https://web.archive.org/web/20210601000000*/stripe.com/jobs |
| [ ] | 2022 | stripe.com/jobs | https://web.archive.org/web/20220601000000*/stripe.com/jobs |
| [ ] | 2023 | stripe.com/jobs | https://web.archive.org/web/20230601000000*/stripe.com/jobs |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2012_careers.html",
      "url": "https://stripe.com/jobs",
      "capture_date": "20120601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2012: 2, 2013: 2, 2014: 6, 2015: 3, 2016: 6, 2017: 3, 2018: 5, 2019: 3, 2020: 22, 2022: 1, 2023: 1, 2024: 18, 2025: 18, 2026: 18}
