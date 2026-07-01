# Manual-capture worklist — GitLab

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/gitlab/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/gitlab/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company gitlab`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2015 | about.gitlab.com/jobs | https://web.archive.org/web/20150601000000*/about.gitlab.com/jobs |
| [ ] | 2016 | about.gitlab.com/jobs | https://web.archive.org/web/20160601000000*/about.gitlab.com/jobs |
| [ ] | 2017 | about.gitlab.com/jobs | https://web.archive.org/web/20170601000000*/about.gitlab.com/jobs |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2015_careers.html",
      "url": "https://about.gitlab.com/jobs",
      "capture_date": "20150601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2015: 2, 2016: 2, 2017: 2, 2018: 4, 2019: 10, 2020: 12, 2021: 13, 2022: 21, 2023: 18, 2024: 8, 2025: 10, 2026: 12}
