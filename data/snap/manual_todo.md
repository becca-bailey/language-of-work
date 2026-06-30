# Manual-capture worklist — Snap

Years with < 3 usable mission_brand chunks (SPA app-shell / no archived text).
Wayback can't recover these server-side; capture them by hand.

## How to capture (per row)
1. Open the Wayback link, pick a snapshot in that year, let the page render.
2. Save the rendered page (Cmd-S → "Web Page, Complete" or copy the visible text
   into a file) as `data/snap/manual_html/<YYYY>_careers.html`.
3. Add an entry to `data/snap/manual_html/manual_manifest.json` (template below).
4. Run: `uv run scripts/ingest_manual_html.py --company snap`
   then `extract_chunks` → `classify_chunks` → `embed_chunks --labels dei` → re-score.

## Worklist
| done | year | url | wayback (pick a snapshot in-year) |
| --- | --- | --- | --- |
| [ ] | 2018 | careers.snap.com/ | https://web.archive.org/web/20180601000000*/careers.snap.com/ |
| [ ] | 2019 | careers.snap.com/ | https://web.archive.org/web/20190601000000*/careers.snap.com/ |
| [ ] | 2020 | careers.snap.com/ | https://web.archive.org/web/20200601000000*/careers.snap.com/ |
| [ ] | 2022 | careers.snap.com/ | https://web.archive.org/web/20220601000000*/careers.snap.com/ |
| [ ] | 2023 | careers.snap.com/ | https://web.archive.org/web/20230601000000*/careers.snap.com/ |
| [ ] | 2024 | careers.snap.com/ | https://web.archive.org/web/20240601000000*/careers.snap.com/ |

## manual_manifest.json template
```json
{
  "captures": [
    {
      "file": "2018_careers.html",
      "url": "https://careers.snap.com/",
      "capture_date": "20180601",
      "source": "manual"
    }
  ]
}
```

Current mission_brand counts by year: {2018: 2, 2019: 2, 2020: 2, 2021: 7, 2025: 7, 2026: 5}
