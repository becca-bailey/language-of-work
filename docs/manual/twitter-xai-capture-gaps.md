# Manual Step: Twitter + xAI coverage gaps (2026-07-30)

**Goal:** close the missing-years gaps in the two Musk-strand contrast corpora
(post-M3/M4 review; both corpora are standalone, excluded from story exports).
Budget ~45–60 minutes of eyeballing plus one fetch run per finding.

## Twitter (pre-Elon) — `data/twitter/`

Current coverage: 2014–2022, but 2014–2015 are thin (~59 words of real prose —
the Drupal-era `about.twitter.com/careers` carousel) and 2007–2013 are not
covered at all.

1. **2007–2013, `twitter.com/jobs`** — CDX captures exist from 2007 (found in
   discovery, outside the probed scope). This is a *fetch extension*, not a
   manual capture: add the pattern to `data/twitter/url_patterns.json`
   (respect `max_year: 2022`) and re-run
   `fetch_snapshots.py fetch --company twitter` →
   `extract_chunks.py` → `classify_chunks.py`, all standalone. Eyeball the
   Wayback calendar first: when does `/jobs` start serving prose rather than
   a listings shell?
2. **2014–2015 depth** — the `about.twitter.com/careers/locations/*` city
   pages probed as sub-threshold shells. Check archive.today for rendered
   captures of those pages (the manual workflow in
   `docs/manual_capture.md` applies: paste DOM →
   `data/twitter/manual_html/` → `ingest_manual_html.py`). If archive.today
   has nothing, the era is likely irreducibly thin — note that in the
   discovery report and move on.
3. Out of scope by ruling: post-acquisition x.com careers (JS shell;
   the register lives in the ultimatum canon, `data/x/canon/`).

## xAI — `data/xai/`

Current coverage: 2023–2026, but 2023 has only 6 chunks (the July 2023
founding announcement era; `/careers` doesn't appear in CDX until 2024).

1. **2023 depth** — check archive.today for mid/late-2023 renders of
   `x.ai` (the announcement page went through revisions before the Grok
   launch reframed the root). Any render with team/careers prose beyond the
   announcement is worth a manual capture.
2. **Ongoing live captures** — live `x.ai` 403s the default fetcher but
   serves 200 to a browser UA, so periodic capture needs a UA tweak, not
   the paste route. Consider a flock-style periodic capture note if xAI
   stays analytically interesting.
3. **Blocked on Becca's ruling:** the Greenhouse posting-boilerplate
   question (include the shared "About xAI" paragraph as corpus, or keep
   postings excluded per precedent). The deduped 13-posting era-spread
   sample already lives in `data/xai/posting_boilerplate_sample.md` +
   `posting_sample/`; if ruled in, ingest from there rather than
   re-fetching.
