# Scout captures — 2026-08-06

Raw artifacts saved during exclusion-story candidate research (web scouts,
2026-08-05/06). Staging only — none of these are pipeline corpus yet; promote
via the normal canon/capture route when a company is onboarded.

| File | Source | Why it matters |
|---|---|---|
| `bendingspoons_controversial_principles_2026-08-06.pdf` | bendingspoons.com/documents (linked from /careers) | "isn't for everybody" + uncompromising-excellence register verbatim. **Zero Wayback coverage of the modern site** — this copy may be the only archival record. |
| `bendingspoons_pay_benefits_2026-08-06.pdf` | same | "We give generous separation packages" — the Netflix severance move in company voice. Same zero-Wayback caveat. |
| `palantir_karp_annual_letter_2022-02-14.pdf` | palantir.com/assets/... (newsroom/letters hub) | Karp 2022 annual letter; letters hub pages are JS shells, PDFs are the durable artifact. Candidate exclusion-canon doc. |
| `rilla_jobs.json` | Ashby posting API `job-board/rilla` (live, 2026-08-05) | Full job-listing JSON; 16/30 listings carry a literal "Don't Work Here" section (~60–70 hrs/week, 6-day weeks). |
| `corgi_jobs.json` | Ashby posting API `job-board/corgi` (live, 2026-08-06) | Listing boilerplate: "6-7 days a week... If you don't meet them, you'll get cut... talent density". |

Method notes (from the scout run):
- Ashby boards: `https://api.ashbyhq.com/posting-api/job-board/{slug}` returns
  clean JSON live; Wayback captures of Ashby pages are JS shells BUT embed the
  full job JSON in `window.__appData` (`descriptionHtml`) — archived listings
  are recoverable by parsing. Verified on a Jan 2025 Rilla capture (which did
  NOT yet have the "Don't Work Here" section — first appearance is datable).
- Scale AI careers credos are server-rendered in raw snapshot HTML (2019–2026
  yearly) even though a live summarizer fetch misses them — capture raw HTML.
