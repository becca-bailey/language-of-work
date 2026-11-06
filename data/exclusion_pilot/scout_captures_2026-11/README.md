# Scout captures — 2026-11-06 recapture round

Second capture round for the exclusion cohort (first: `../scout_captures_2026-08-06/`).
Live fetches via curl with a browser UA; Ashby boards via the public posting API.
Companion HTML captures went to each company's `data/<co>/manual_html/` and were
merged into `snapshots.json` via `ingest_manual_html.py` the same day.

| File | Source | Notes |
|---|---|---|
| `rilla_jobs.json` | Ashby posting API `job-board/rilla` (live, 2026-11-06) | 26 listings; "Don't Work Here" section still present. |
| `cluely_jobs.json` | Ashby posting API `job-board/cluely` (live, 2026-11-06) | 4 listings (was ~dozens in scout notes) — board thinned. |
| `corgi_jobs.json` | Ashby posting API `job-board/corgi` (live, 2026-11-06) | **"Not Found" — the public Ashby board is gone.** The 2026-08-06 capture is now the only record of it. See Corgi finding below. |
| `bendingspoons_controversial_principles_2026-11-06.pdf` | bendingspoons.com/documents | Current version for diffing against 2026-08-06 copy. |
| `bendingspoons_pay_benefits_2026-11-06.pdf` | same | Same. |
| `bendingspoons_a_great_spooner_2026-11-06.pdf` | same | Not captured in August; adds the third culture PDF. |

## Findings from this round (perishable-change log)

- **Scale rewrote its careers credos.** The live 2026-11-06 page has a new set
  ("Earn Customer Love", "Team Flow", "Quality is Our Cheat Code", "Find the
  20%", …). "Run Through Walls" and "Ambition Shapes Reality" — verified
  present in the 2024-01-01 and 2026-01-01 snapshots per url_patterns.json —
  are gone. The replacement window is 2026-01 → 2026-11; CDX captures in
  between should narrow it. Candidate beat for the escalation-arc / post-Meta-
  deal framing.
- **Corgi moved hiring in-house and softened the template.** careers page now
  renders 67 listings itself ("Most people are not a fit." headline retained);
  the public Ashby board 404s. Three role pages sampled 2026-11-06 (saved in
  `data/corgi/manual_html/`, full descriptions in embedded ld+json JobPosting):
  none carries the August "6-7 days a week… you'll get cut… talent density"
  boilerplate; the sales listing uses softer always-on phrasing ("work harder
  than you ever have before"). Register softening is datable Aug→Nov 2026 if
  it holds across more listings — sample wider before citing.
- **Rilla's register persists** ("Don't Work Here" still in the live board JSON).
- **Bending Spoons careers page copy changed** since the scout notes ("The
  challenge of your lifetime" headline; "The pace can be a lot… you're going
  to love it here"), and the jobs FAQ leads with "Is it true that Bending
  Spoons is a demanding workplace? Yes." — both captured to manual_html.
