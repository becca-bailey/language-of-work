# Manual Step M1: Google Careers URL Archaeology

**Goal:** confirm which URL patterns hosted Google's careers content in each
era, so the fetch queries the right corpus. Budget ~30–45 minutes.

**Workflow:**

1. Run `uv run scripts/fetch_snapshots.py discover` first — it prints capture
   counts per candidate pattern per year and writes
   `data/google/discovery_report.md`. Patterns with zero captures in their
   expected era are wrong; gaps in the timeline mean a pattern is missing.
2. Use the Wayback calendar links below to eyeball each pattern: when does it
   start serving real careers content? When does it become a redirect?
3. For eras with gaps, open the archived **Google homepage** for that era and
   follow its "Jobs"/"Careers" footer link — that reveals the canonical
   careers URL of the day.
4. Record findings by editing `data/google/url_patterns.json` (add/remove
   patterns, update `era_hint`). Re-run `discover` to confirm.

## Pre-probed findings (already applied to url_patterns.json)

- `google.com/about/jobs/` is the 2012–2014 era home (fills the 2013 gap)
- `google.com/about/careers/lifeatgoogle/` is a content-rich sub-page, 2014+
- `about.google/careers/` has **zero** CDX captures — dropped; if you find an
  about.google careers path with content (e.g. under /intl/), add it
- `jobs.google.com/` only ever served redirects/404s — dropped
- `google.com/about/careers/applications/` is the **2023+** era home

## Candidate patterns

| Pattern | Era hint | Calendar |
|---------|----------|----------|
| google.com/jobs/ | early 2000s | [calendar](https://web.archive.org/web/2005*/google.com/jobs/) |
| google.com/intl/en/jobs/ | early 2000s | [calendar](https://web.archive.org/web/2005*/google.com/intl/en/jobs/) |
| google.com/about/careers/ | ~2012–2018 | [calendar](https://web.archive.org/web/2013*/google.com/about/careers/) |
| careers.google.com/ | ~2015+ | [calendar](https://web.archive.org/web/2016*/careers.google.com/) |
| about.google/careers/ | ~2017+ | [calendar](https://web.archive.org/web/2018*/about.google/careers/) |
| jobs.google.com/ | verify | [calendar](https://web.archive.org/web/2018*/jobs.google.com/) |

Homepage links for step 3 (pick a year, follow the careers link):

- [google.com 2005](https://web.archive.org/web/2005*/google.com)
- [google.com 2010](https://web.archive.org/web/2010*/google.com)
- [google.com 2014](https://web.archive.org/web/2014*/google.com)

## What to look for

- **Redirect shells:** a 200 capture can still be a meta-refresh or JS redirect
  with no content. Note these — the fetch keeps them but extraction will flag
  thin coverage.
- **Era boundaries:** the handoff years (e.g., /about/careers → careers.google.com)
  often have both URLs live with different content. Keep both.
- **Sub-pages worth adding:** the main careers page sometimes thinned out while
  mission copy moved to sub-pages (e.g., "how we hire", "benefits", "students").
  If you see a content-rich sub-page recurring across years, add it.
- **SPA era (~2015+):** if careers.google.com looks blank in the calendar
  preview, that's expected (client-side rendering) — the pipeline probes
  archived JSON endpoints separately.

## Sign-off

When `url_patterns.json` reflects reality, proceed to
`uv run scripts/fetch_snapshots.py fetch`.
