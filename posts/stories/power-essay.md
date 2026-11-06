---
title: Culture is downstream of power
subtitle: The language that surges when workers have leverage — and gets cut once they don't.
thesis: >-
  Across 19 companies, DEI language crested in 2021, at the height of the Great Resignation,
  when workers had the most leverage in a generation. It held for four years, then — once that
  leverage had drained away and the 2024 election shifted the political winds — it was cut
  nearly in half in a single year. Idealism rode the same cycle with a smaller swing.
  Performance, which serves whoever can hire and fire, never moved. And the one concession
  that wasn't cut — wellbeing — was converted instead: the care that endured is the kind
  workers absorb themselves. The culture companies keep is the part that benefits the people
  in power; the rest, it turns out, was rented.
published: false
study: careers
order: 1
teaser: "Worker-serving language (DEI) surged when workers had leverage and was cut once they lost it; the management-serving substrate (performance) never moves; the care that survived was converted into the worker's own homework."
---

import PowerChart from "@/components/viz/PowerChart.astro";

All of this raises a harder question. If careers-page language is mostly a reflection of the
labor market, what does it say about worker power?

To find out, I overlaid four language trajectories — idealism, DEI, wellbeing, and performance —
against the JOLTS quit rate from the U.S. Bureau of Labor Statistics, a rough proxy for when
workers had the leverage to walk. It's not an exact science, but the patterns are there.

<PowerChart />

The clearest signal is **DEI**. Worker-oriented language climbed through the late 2010s and
crested in 2021, right on the 2021–22 generational peak in the quits rate, when workers had
the most leverage to walk. It stayed elevated for four more years. Then, in 2026, after that
leverage had drained back below pre-pandemic levels and the 2024 election turned the political
winds, it was pulled back hard: the industry average nearly halved in a single year, to its
lowest level in a decade. Meta's DEI-register share went from near-saturation at the peak to
zero; Starbucks's went to zero too; Salesforce's fell to less than half its peak. (Not universally —
Apple's held.) The language companies adopted when workers had power was unwound once they
didn't.

That retreat is the heart of it. The concessions weren't immediate — DEI stayed high for years
after the quits rate began falling — but they were sticky, not permanent, and the moment
leverage was gone and the politics gave cover, they snapped back. **Idealism** rode the same
cycle with a smaller swing; its crest also lands on the 2021–22 worker-power peak, for all that
workers were always a little cynical about billionaires promising to change the world. **Performance**,
which serves whoever can hire and fire, stays flat near the top no matter what.

There's a fourth line now, and it's the one that doesn't follow the script. **Wellbeing** — the
care language of balance, rest, and mental health — looks at first like another worker
concession riding the same cycle. It isn't. It spiked in 2020, with the pandemic, a year
*before* the quits rate peaked — care language answered the emergency, not the bargaining
table. And where DEI was pulled back hard once leverage was gone, wellbeing never was: it
deflated slowly as the emergency faded, and in 2026 it still sits at roughly double its
pre-pandemic average, a little over half its 2020 peak.

What got cut instead is quieter, and you can only see it if you ask *who absorbs the care*. The
bottom panel tracks a second axis — individual versus structural locus of care, the difference
between "here's a meditation app, manage your own energy" and "we staff so no one returns to a
backlog." It drifts toward the individual across the decade, peaks right after the leverage
peak, and stays there through 2025. The keyword record in benefits copy says the same thing
more bluntly: mental-health and therapy-app language roughly tripled between 2019 and 2025
(from about 3% to 9% of benefit chunks) while family and caregiving language — the kind that
costs the company staffing and coverage — collapsed from about 11% of benefit chunks in 2019
to about 1% by 2024. (2026 shows a partial caregiving rebound; that's one year of data, too
early to call.) The care that survived is the kind the worker performs on themselves. That's
not a concession being revoked; it's a concession being converted into homework.

In 2026 you can't trust what a company says about itself. But you can trust the pattern of when
it stops saying it: the worker-serving language is the part that gets cut when leverage is gone.
Cultural signaling doesn't give workers power — it reflects the power they already have.

## How this was measured

Each line is an industry mean over the same nineteen companies (2013–2026), every one scored on
all four axes — no per-metric subsetting; the locus panel is a companion measure, not a fifth
counterforce. (The three companies added in mid-2026 — Uber, Apple, and Nvidia — have thinner
historical coverage, Uber especially.) The quits rate is economy-wide, a proxy for tech
bargaining power; read this as co-movement, not causation.

Both counterforces track the quits rate strongly in raw terms (idealism r ≈ +0.72, DEI
r ≈ +0.76), and both keep some of that under first-differencing, which strips out shared trend
(idealism r ≈ +0.39, DEI r ≈ +0.44) — suggestive, not decisive, on thirteen year-pairs. Which
of the two tracks the cycle *more* closely is not a stable result: DEI led in an eleven-company
draft, idealism led at thirteen, and DEI leads again at nineteen — so I won't hang anything on
it. What the differencing understates for DEI is the lag: it peaked with worker power in 2021
but didn't retreat until 2026, so the year-over-year ticks miss how well the overall shape —
surge at the peak, collapse once leverage is gone — follows the cycle. (An earlier draft
reported a much starker DEI number that turned out to be an artifact of incomplete data — one
company's mid-decade DEI language was unclassified and counted as zero — which is part of why I
treat these correlations as supporting texture, not the finding.)

Performance is the line whose story got more complicated as the dataset grew. Its raw
correlation (r ≈ +0.41) used to disappear entirely under differencing; at nineteen companies it
doesn't (r ≈ +0.39), so I can no longer say its wiggles carry no year-over-year co-movement.
What still separates it from the counterforces is amplitude and unanimity: its total swing is a
sliver — a relative range three to six times smaller than idealism's or DEI's — and firm by
firm it's a coin flip (10 of 19 positive, median ≈ 0), where idealism and DEI lean clearly
positive (16 and 15 of 19). Performance never surged and never got cut; there was no concession
there to revoke. And one honest confound runs through all of it: the 2026 DEI retreat coincides
with *both* fading worker leverage and a political backlash, and this data can't separate the
two. What it can show is that the worker-serving language is the part that got cut.

Wellbeing is measured differently from the other three, and more cautiously. It's an embedding
axis (balance-and-rest against intensity-and-sacrifice) scored on the same mission-page chunks
as the values fingerprint, so it shares whatever blind spots that corpus has; an earlier draft
dropped it entirely because benefits copy is where most care language lives, but the
mission-page signal turned out to be readable after all — the 2020 spike is the largest
single-axis jump in the fingerprint set (z ≈ +2.1, ahead of inclusion's +1.1). Its correlation
with the quits rate is the weakest case on this page and I want to be plain about that: raw
r ≈ +0.57, but under first-differencing it goes *negative* (r ≈ −0.25) — driven by 2020, when
quits fell and care language exploded. So I'm not claiming wellbeing tracks leverage; I'm
claiming the opposite, and that's the point of including it. The locus shift rests on 78–194
benefit chunks a year, and nearly half of the wellbeing company-years sit on fewer than five
mission chunks; the individual-locus axis and the keyword split are two imperfect instruments
pointing the same direction, not one clean measurement. The fuller version of this argument,
with the receipts, lives in [the wellbeing story](/stories/wellbeing).
