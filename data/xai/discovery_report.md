# CDX discovery report: xai

Captures per pattern per year (status 200, ~monthly collapse).
Use this during manual step M1 to confirm/extend `url_patterns.json`.

| Pattern | signal | 23 | 24 | 25 | 26 |
|---|---|---|---|---|---|
| x.ai/ | 235w (M1-corrected; auto-probe said 48w ⚠shell) | 8 | 11 | 12 | 7 |
| x.ai/careers | 280w |  | 10 | 12 | 7 |
| x.ai/about | 391w | 2 | 12 | 2 |  |
| x.ai/company | 216w |  |  | 10 | 7 |

## Shell patterns (skipped by fetch)

None after M1 correction. The auto-probe flagged `x.ai/` as a shell because its
earliest/median/latest sampling landed on the pre-announcement parked page
(2023-02) and the 2025/2026 product-page shell eras. The pattern exists for the
Jul–Nov 2023 founding-announcement era only (`max_year: 2023`); a re-probe on
those captures measures 230–235 DOM words, so `discovery_signals.json` was
corrected by hand (see its `note` field) and fetch does NOT skip the pattern.

## Gaps to investigate

Years with no coverage from any pattern: none that matter — the company was
founded July 2023, so the 2005–2022 "gap" is pre-company. (The x.ai domain
2011–2021 belonged to the unrelated "Amy Ingram" scheduling-assistant startup;
`min_year: 2023` on every pattern hard-excludes it.)

2023 is thin by construction: no /careers page existed; the founding
announcement on the root is the only culture copy (plus /about from Nov 2023).
Root captures from 2023-11-15 onward are the Grok product-launch blog (product
content, out of scope) and are pruned post-fetch (`pruned_product_blog` in
snapshots.json).

## Hosts probed beyond url_patterns.json (2026-07-29)

CDX hit counts (status 200, ~monthly collapse unless noted):

| Host/path | match | captures | years | verdict |
|---|---|---|---|---|
| x.ai/ | exact | 128 (from 2005) | 2011–2026 | pre-2023 = scheduling startup; xAI era kept 2023-only |
| x.ai/careers | exact | 29 | 2024–2026 | KEPT — culture prose |
| x.ai/careers/ | prefix | 356 (8 distinct URLs) | 2024–2026 | mostly query-string dupes of /careers + og images |
| x.ai/careers/open-roles | exact | 43 | 2025–2026 | EXCLUDED — listing index, JS shell (15–102w, role titles) |
| x.ai/about | exact | 53 (from 2005) | 2014–2025 | KEPT from 2023 |
| x.ai/company | exact | 17 | 2025–2026 | KEPT — successor to /about, values prose |
| x.ai/grok | exact | 20 | 2024–2026 | product page, out of scope |
| x.ai/blog | exact | 13 | 2024–2025 | product blog, out of scope |
| careers.x.ai | exact+prefix | 0 | — | no such host |
| jobs.ashbyhq.com/xai | exact+prefix | 0 | — | not their board |
| jobs.lever.co/xai | exact+prefix | 0 | — | not their board |
| boards.greenhouse.io/xai | exact | 12 | 2023–2025 | board root, JS shell (0w) |
| boards.greenhouse.io/xai/ | prefix | 479 (121 distinct /jobs/ URLs) | 2023–2025 | job postings — see boilerplate flag below |
| job-boards.greenhouse.io/xai | exact | 17 | 2025–2026 | board root, near-shell (13w) |
| job-boards.greenhouse.io/xai/ | prefix | 4117 (976 distinct /jobs/ URLs) | 2024–2026 | job postings — see boilerplate flag below |

grok.x.ai / accounts.x.ai were not probed: nothing in the main probes suggests
careers content ever lived there (they are the product login/app hosts).

Live-capture note: live x.ai returns 403 to the pipeline's default-UA httpx
fetcher but 200 with a browser User-Agent, and Wayback coverage runs through
Jul 2026 — so neither the browser-UA route nor the manual copy/paste fallback
(flock/engine precedent) is needed for now.

## DECISION FLAGGED FOR BECCA: Greenhouse posting boilerplate

Repo precedent excludes job listings (twitter/spacex/ramp), and this run
follows it: no posting URLs are fetched into the corpus. BUT xAI is unusual —
every Greenhouse posting opens with a shared "About xAI" culture paragraph that
is *denser* culture copy than anything on x.ai itself:

> "Our team is small, highly motivated, and focused on engineering
> excellence... We operate with a flat organizational structure. All employees
> are expected to be hands-on and to contribute directly to the company's
> mission. Leadership is given to those who show initiative and consistently
> deliver excellence."

The x.ai culture pages do exist (careers/about/company, ~1,300 words of prose
across eras), so the boilerplate is NOT the only culture copy — but it carries
distinct constructs (flatness, meritocratic leadership, work ethic) that the
pages soft-pedal. A small deduped sample of the boilerplate across eras is
preserved in `posting_boilerplate_sample.md` (raw HTML in `posting_sample/`),
kept OUT of chunks/ and classifications so the corpus stays listing-free until
Becca rules.

Options: (a) keep excluded (precedent); (b) admit the deduped boilerplate
paragraph only, as a single recurring pseudo-page per era; (c) admit a small
posting sample with job_listing labels. Not decided here.
