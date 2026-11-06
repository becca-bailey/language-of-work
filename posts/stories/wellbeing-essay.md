---
title: Bring Your Own Resilience
subtitle: How companies talked about well-being when workers had leverage — and why the care that survived is the kind you carry yourself.
thesis: When workers had leverage, companies inflated care talk and care benefits together; as leverage returned, the talk deflated — and the care that survived was the kind workers carry themselves.
published: true
study: careers
order: 6
teaser: "Care talk rose and fell with worker leverage; the care that survived is the kind you bring yourself."
---

import ConcessionViz from "@/components/viz/ConcessionViz.astro";
import CompanyConcessionViz from "@/components/viz/CompanyConcessionViz.astro";
import AxisSpikeViz from "@/components/viz/AxisSpikeViz.astro";
import LocusDivergenceViz from "@/components/viz/LocusDivergenceViz.astro";
import MaterialDeiViz from "@/components/viz/MaterialDeiViz.astro";

I set out to test a simple idea: that as employer leverage returns, the well-being budget
migrates from the system to the self. The clean version of that story — a measurable
substitution of individual perks for structural ones — the data could not support; the
enumerated-benefits signal on careers pages is too sparse to carry it. But something else
was there, and it turned out to be more interesting.

## The concession moment

In 2020, companies' **care talk** — language about rest, balance, mental health, sustainable
pace — jumped to roughly 3.7× its prior level. It did not rise alone. **DEI talk** rose in
near-lockstep: within companies, the two move together at a median correlation of +0.53
(95% CI [0.27, 0.70]), positive in 15 of 16 firms. Care and diversity read like two faces of
one concession.

And the concession tracked worker bargaining power. Overlaid on the JOLTS quits rate — how
freely workers were leaving jobs — care and DEI talk rise into the Great Resignation and
recede as quits fall. Standardized so all three sit on one scale:

<ConcessionViz />

The cleanest part of this is the *recede*: as the quits rate fell from 2.8 back to 2.1
(2022→2024), care talk fell with it. The 2020 spike itself is harder to read cleanly —
it coincides with the pandemic, so some of that surge is lockdown wellness-talk rather than
a pure labor-market response. The deflation is the part that isn't confounded.

And the bundling isn't carried by a few firms. Take it one company at a time — each firm's
own care and DEI talk, standardized — and the same paired rise-and-recede shows up in 15 of
16, from Salesforce (r = +0.79) down through GitLab, Amazon, and Palantir. Only HubSpot
breaks the pattern. Pick a company:

<CompanyConcessionViz />

## The performance regime never flinched

If 2020 were simply a year companies got more values-forward across the board, every axis
would have lifted. It didn't. Measuring each theme's 2020 deviation from its own historical
average, only the **worker-concession** axes spiked. Performance, meritocracy, and control
language barely moved.

<AxisSpikeViz />

That's what makes "concession" the right word. The care and DEI surge was targeted — the
language a tight labor market extracts — while the performance regime, the part that serves
the employer, held perfectly steady underneath it.

## Talk is cheap; benefits are slow

The rhetoric was an *event* — a sharp 2020 spike. The actual care **benefits** were a slow
build: their prevalence climbed gradually from 2016 to 2019 and had already plateaued before
the talk spiked. Two different clocks. The volatility lives in the framing, not in the
obligation — a company can re-word a careers page in an afternoon; it cannot re-staff a leave
policy that fast. Talk flexes with the moment; substance moves on its own slower schedule.

## The care that survived

Here is the finding I didn't predict. Not all care benefits behaved alike — they split by
*who absorbs the cost*. **Mental-health** benefits (EAP, therapy stipends, wellness apps —
things the employee uses on their own, coded individual-locus in 19 of 20 cases) climb
steadily, up and to the right, still peaking at the end of the record. **Family and
caregiving** benefits (paid leave, childcare — where the organization absorbs the coverage,
coded structural in 105 of 125 cases) crest around 2019 and recede.

<LocusDivergenceViz />

This is individualization — not as the aggregate ratio I couldn't measure, but as *divergent
survival*. The care that endures is the kind you carry yourself; the care the company has to
absorb is the kind that fades. The well-being budget didn't just shrink. What was left of it
shifted from system to self.

The counts here are modest and this is self-presentation — what firms advertise, not what
they provide. But the shapes are clean and they line up with the locus split almost perfectly,
so I read it as a genuine illustration of the mechanism, not a fragile quantitative claim.

## Whole-life benefits

There's a second family of benefits worth watching: the ones that support your life *outside*
work — the people you care for and the moments that don't fit a calendar. Parental leave,
childcare, elder and dependent care, fertility, lactation, identity-positive coverage,
bereavement. Measured as a *share* of everything companies advertise, they rose through the
mid-2010s, peaked around 2018 at roughly one benefit mention in seven, and have been a
shrinking slice ever since — down to a low near 2024, with only a slight recovery after. That
peak comes *before* the 2020 concession-talk spike: the family-benefits wave crested and began
fading while the care-and-diversity language was still climbing — substance leading talk, and
receding first. Parental leave is the sturdiest thread; lactation, bereavement, and
identity-positive coverage barely register.

<MaterialDeiViz />

## What I can't say

I want to be precise about the limits. The aggregate individualization index — the headline
this study was designed around — is **too sparse to test**: only 8 of 15 companies have enough
enumerated benefits on both sides of 2022, at 2–5 items each. Fertility benefits appear in only
four companies ever, so their trajectory is an anecdote, not a trend. The benefits data
throughout is self-presentation, not provision. The
quits rate is total-nonfarm, not the information sector specifically. And the leverage
correlation rests on about ten annual points, with the 2020 spike confounded by COVID.

So the strong claim here is narrow and it is about *language*: a worker-concession bundle
that inflated with the labor market and deflated as leverage returned, while the performance
regime never moved. The benefits are texture — vivid where the shapes are clean, silent where
the counts run out.

## The care that's left

Resilience, in current careers copy, is a personal skill — something to build with an app, a
stipend, a mindfulness subscription. This record suggests the framing itself is the concession
receding. When workers had the leverage to ask, companies described care as something the
system owed them; when the leverage passed, the care that remained was the kind you were
expected to manage on your own.
