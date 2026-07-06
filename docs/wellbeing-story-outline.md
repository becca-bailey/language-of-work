# Well-Being Story — Write-up Structure

Replaces the existing `benefits` story (a keyword perks chart) with the full well-being
study. Lands in the `wellbeing` story slot (already provisioned in pipeline.yaml). Draft
(`published: false`) until reviewed.

## Spine (one sentence)

When workers had leverage, companies inflated care talk *and* care benefits; as leverage
returned, the talk deflated — and the care that survived was the kind workers absorb
themselves. The well-being budget didn't just shrink; it shifted from system to self.

## What the evidence actually supports (so we don't overclaim)

- **Strong / lead with:** the care+DEI rhetoric "concession bundle," coverage-controlled and
  leverage-dated. Dense instrument, survives controls.
- **Illustrative texture:** the mental-health-vs-caregiving divergence; the GitLab close-up.
  Clean shapes / vivid mechanism, modest counts — framed as illustration, not proof.
- **Honestly retired:** the aggregate individualization index (too sparse); fertility trend
  (4 companies); H2 as a ratio. Named as a limit, not buried.

## Sections

1. **The concession moment.** 2020: care rhetoric ~3.7×'d and DEI rhetoric spiked *together*
   — within-company median r=+0.53 [0.27, 0.70], 15/16 companies. The bundle tracked worker
   leverage (JOLTS quits): rose into the Great Resignation, receded as quits fell
   (2.76→2.07, care +0.054→+0.030). *Visual: care + DEI axes overlaid on the quits rate.*

2. **The performance regime never flinched.** The 2020 spike hit only the worker-concession
   axes (care, DEI). Performance, meritocracy, control stayed flat. It wasn't general values
   inflation — it was a targeted concession. *Visual: all-axis 2020 small-multiple.*

3. **Talk is cheap; benefits are slow.** Rhetoric was a sharp 2020 event; care benefits were
   a slow secular build (2016–19) that never spiked. The two clocks decouple — volatility
   lives in the framing, not the obligation. *Visual: rhetoric spike vs benefit-prevalence
   plateau, same axis.*

4. **The care that survived (the turn).** Among care benefits, the two trajectories split by
   locus: **mental health (individual-locus: EAP/apps/stipends) climbs up-and-to-the-right,
   peak 2026; family/caregiving (structural-locus: paid leave/childcare) crests 2019 and
   recedes.** Individualization shown as divergent survival, not a ratio: the enduring care
   is the kind you carry yourself. *Visual: the two sparklines, recolored by locus
   (individual vs structural), side by side — the centerpiece image.*

5. **GitLab, up close.** F&F Day as the mechanism at one transparent company: the six-day
   "Pandemic Support Day" rename (naming the contingency, then burying it — the
   cheap-talk-vs-commitment seam) and the "coverage requirements" edit (a structural benefit
   privatizing the instant someone has to stay back). Vivid, one company, explicitly a
   close-up not the centerpiece. *Visual: the flow timeline with the two annotated events.*

6. **What we can't say.** The honesty section: aggregate individualization index too sparse
   to test (8/15 companies, 2–5 items); fertility too rare (4 companies); benefits are
   self-presentation, not provision; quits is total-nonfarm not information-sector; ~10
   year-points; 2020 care spike COVID-confounded (the recede is the cleaner signal).

7. **Close.** Counterforces framing — the concession was real but contingent on leverage,
   and what persisted individualized. Closing citation: "Resilience Is a Systems Problem."

## Key visuals to build (React/tsx + viz/*.astro, reading stories/wellbeing.json)

- **Concession overlay** — care + DEI axis trajectories on the quits rate (§1).
- **Locus-divergence sparklines** — mental health (individual) vs caregiving (structural),
  recolored, the centerpiece (§4). Can adapt the existing BenefitsViz sparkline component.
- **All-axis 2020 comparison** (§2) — reuse the fingerprint/axis chart pattern.
- **GitLab flow timeline** (§5) — from wellbeing_flow.jsonl, two events annotated.

## Replacement mechanics (decision needed)

- The existing `benefits` story (`benefits.mdx`, keyword perks chart, `published:false`,
  order 6) is superseded. Options: (a) retire benefits.mdx, build `wellbeing.mdx` fresh in
  the wellbeing slot; (b) rewrite benefits.mdx in place as the wellbeing study. Recommend
  (a) — the wellbeing slot is already provisioned and the benefits chart becomes §4's
  centerpiece rather than a standalone story.
- Data export: extend `scripts/export_story_web.py` (wellbeing) to emit the trajectories,
  the locus-divergence series, and the flow timeline into `stories/wellbeing.json`.
