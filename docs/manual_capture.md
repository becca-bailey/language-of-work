# Manual HTML capture workflow

For SPA-era pages where Wayback returns thin shells, paste rendered HTML manually.

## Steps

1. Open the page on [archive.today](https://archive.today) or in your browser.
2. Copy the rendered DOM: in DevTools console, run:
   ```js
   copy(document.documentElement.outerHTML)
   ```
3. Save to `data/<company>/manual_html/<YYYYMMDD>_<slug>.html`.
4. Add an entry to `data/<company>/manual_html/manual_manifest.json`:
   ```json
   {
     "captures": [
       {
         "file": "20250401_careers.html",
         "url": "https://www.example.com/careers/",
         "capture_date": "20250401",
         "source": "archive.today"
       }
     ]
   }
   ```
5. Merge into the snapshot manifest:
   ```bash
   uv run python scripts/ingest_manual_html.py --company <company>
   ```
6. Re-run the pipeline from `extract_chunks.py` onward.

The `__NEXT_DATA__` extractor in `chunk_html` handles pasted SPA HTML the same as Wayback captures.
