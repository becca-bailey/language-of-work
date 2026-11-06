---
title: Masculine Energy
subtitle: Scoring twenty-three companies' careers copy on a gender-coding axis.
thesis: >-
  If a company's job postings sound like they aren't for you, there's a
  reason for that: careers-page language is measurably gender-coded, and
  the exclusionary register is among the most masculine-coded language in
  the corpus.
published: true
study: careers
order: 8
teaser: "Gender-coded language across every careers page in the corpus."
---

import GenderUnitChart from "@/components/viz/GenderUnitChart.astro";
import ConceptGenderPlot from "@/components/viz/ConceptGenderPlot.astro";
import ExclusionQuotes from "@/components/viz/ExclusionQuotes.astro";
import TimeGenderDivergingBars from "@/components/viz/TimeGenderDivergingBars.astro";
import GenderShiftBars from "@/components/viz/GenderShiftBars.astro";

In January 2025, Mark Zuckerberg went on Joe Rogan's podcast and said that the
workplace has become "culturally neutered" and that he wants to bring
"masculine energy" back to it. But what does "masculine energy" mean, exactly?
It turns out you can measure it.

A lot of this project runs on AI embeddings — models that turn a piece of text
into a point in a space with hundreds of dimensions, where text with similar
meanings lands close together. But *directions* in that space carry meaning
too. The classic party trick is that if you take the vector for "king,"
subtract "man," and add "woman," you land near "queen." A
[study from 2019](https://journals.sagepub.com/doi/full/10.1177/0003122419877135)
by Kozlowski, Taddy, and Evans called "The Geometry of Culture" turned that
party trick into a measurement instrument: take many word pairs that differ
*only* in gender — man/woman, he/she, father/mother — draw the arrow for each
pair, and average them into a single, stable **gender axis**. Then any
sentence can be projected onto that axis and scored: how strongly does this
language associate with the masculine or feminine pole of the space?

This story does the same thing with the careers corpus. The axis is built
from sixteen pure gender-term pairs — and, very importantly, **there are no
intuition words in the poles**. I never told the model that "hardcore" or
"relentless" is masculine. The axis is built entirely from words like he/she
and father/mother; everything else is projected onto it and scored. If
"hardcore" comes out masculine-coded, that's the training data talking, not
me.

The good news about biased training data is that it can reflect our biases
back to us. When this story says "masculine-coded" or "feminine-coded," that
isn't a personal judgment — not "direct communication is for men, therefore
companies shouldn't talk about direct communication." It is a computed
proximity to masculinity: if decades of English text have these concepts
mapped to statements made by men, for men, or about men, the embedding shows
that. In this particular study, gender bias is the feature, not a bug.

Every sentence of careers-page copy in this corpus is scored on that axis.
One square per sentence.

<GenderUnitChart />

Four notes on trusting this measurement. First, it passes the tests where
the answer is known: occupation terms with heavily male-skewed workforces
(infantry soldier, lumberjack) land cleanly on the masculine side, heavily
female-skewed ones (kindergarten teacher, nurse) land on the feminine side,
and genuinely neutral terms land near zero — that's also why scores inside
the ±0.5z band are shown as neutral rather than over-read. Second, the axis
isn't hostage to any particular word pair: splitting the sixteen pairs into
two independent eight-pair axes ranks the corpus nearly the same way. Third,
the ranking agrees with an instrument that shares none of its machinery:
scoring the same corpus with the published masculine/feminine word dictionary
from the job-ads study cited at the end of this story reproduces the company
ordering (Spearman 0.66) — a word-counting method and a geometry method, with
no shared failure mode, seeing the same pattern. Fourth — deliberately —
there is no human-rating backstop here. Asking a human judge
whether "bias for action" sounds masculine would re-import the very
intuitions this method is designed to bypass; the coding lives in the corpus
statistics, so validation is known-answer anchors and split-half reliability,
not human agreement.

One caveat belongs next to the chart rather than in a footnote: the coding
partly tracks *who is doing the talking*. Basecamp — famously anti-hustle —
sits near the top of the ranking, because assertive founder-manifesto prose
("we don't do X") is masculine-coded independent of intensity, while
HR-authored benefits copy pulls feminine. Companies whose pages are written
in a founder's voice read more masculine than companies whose pages are
written by a communications team, so the fair comparisons in this story are
within a register, not across registers. Relatedly, sentences that mention
people by name score masculine for a boring reason — "Eric" is a gendered
word, the same as "he" — and this story is trying to measure the register,
not the roster, so every sentence quoted below is free of names and pronouns.
The company numbers don't depend on this either: dropping every sentence that
contains an explicit gender term, and then also every sentence with a likely
personal name, reproduces the company ordering almost exactly (rank
correlations 0.99 and 0.94).

## If it sounds like it isn't for you

Some careers pages say it almost outright. The register runs from SpaceX's
2003 hiring criteria to Ramp's 2026 letter persuading you not to apply — it
predates the Netflix deck, which didn't invent this language so much as make
it quotable — and on the gender axis, its sharpest specimens are among the
most masculine-coded sentences in the corpus. Coinbase's homage to the
Netflix severance line, "Unremarkable performance gets a generous severance
package," scores 1.8 standard deviations toward the masculine pole. Engine's
culture memo is a fountain of these: "Comfort is a signal to probe, not
rest" (+1.7), "Silence is not humility here; it is abdication" (+1.6).

Meanwhile, the one nearly neutral card below is the plainest statement of
the idea: Netflix's "But Netflix is not for everyone, so please read on"
scores almost exactly zero. It's not the sentiment that's masculine-coded.
You can tell people your company isn't for everyone in neutral language.
It's the *performance* of it — the hardcore, the hard mode, the not for the
faint of heart — that carries the gender coding.

<ExclusionQuotes />

That 2003 SpaceX page, the oldest artifact in this register, also contains
the line "SpaceX does not discriminate on the basis of anything but skill."
The axis measures what else the page's language sorts on: who feels
addressed by it.

## The ideas companies share, ranked

It isn't just companies that are gender-coded — the *ideas* they borrow from
each other are. Clustering every sentence in the corpus into recurring
concepts and keeping only the genuinely shared ones (at least three companies,
two-plus sentences each, no company over 40%) puts the performance canon at
the masculine pole — speed, flat structure, rejecting conventional norms —
and the inclusion vocabulary at the feminine pole. Each concept is labeled
with its own words.

<ConceptGenderPlot />

The two poles earn their coding differently, and the asymmetry is worth
saying plainly. The masculine-coded concepts are *style*-driven: speed and
iteration, flat organization, learning from difficulty rarely mention men at
all. The feminine-coded concepts are often *subject*-driven: employee
resource groups, pay equity, diversity-and-inclusion copy frequently talks
explicitly about women. To separate the two, concept scores here exclude
sentences with explicit gender mentions — and the feminine pole survives the
exclusion. Employee resource groups barely move (−0.80 to −0.76), and
diversity-and-inclusion culture holds at −0.56. Pay equity is the exception
that shows the filter working: it softens from −0.95 to −0.66 once the
sentences that literally say "women" are set aside, meaning a real share of
its coding was lexical rather than stylistic.

One absence from this chart is deliberate: concepts dominated by a single
company are excluded (twenty fell to the 40% cap). The most masculine-coded
concept in the whole corpus — the severance-and-high-bar-hiring cluster — is
one of them: it's still 74% Netflix's own voice, so it lives in the Netflix
story rather than here, where the subject is the ideas companies actually
share.

## The turn, over time

Scoring each company's pages year by year adds the missing axis. In the
aggregate, feminine-coded share peaks near one sentence in five across
2019–2021 — the same window in which careers pages inflated care and
diversity language — and falls to 14% by 2023, while masculine-coded share
reaches its modern peak. Read the curve with one caveat: part of the swing
is composition. Ramp and Anduril enter the record in 2021–22 already
sounding masculine. The cohort founded into the tight-money era arrives
pre-coded, which is a finding about selection, on top of the one about
editing.

<TimeGenderDivergingBars />

Holding the roster fixed sharpens the picture. Among the sixteen companies
with enough coverage on both sides of 2022, the median shift is close to
zero — most companies did not rewrite their registers. The movement is
concentrated: feminine-coded share fell where DEI copy was retracted (Meta,
HubSpot, GitLab, Shopify, Google), and masculine-coded share jumped at
exactly two companies, Meta and Coinbase, each up roughly 21 points. Meta's
is the largest masculine shift in the corpus — the "masculine energy"
pivot, measurable in the careers pages of the company whose CEO asked for
it. The companies already at the masculine end — Netflix, Engine, SpaceX,
Basecamp — held steady or softened slightly.

<GenderShiftBars />

---

This corpus measures language, not outcomes — no promotion rates or pay gaps
here. The downstream effect has been measured elsewhere: in
[a series of experiments published in 2011](https://doi.org/10.1037/a0022530),
women shown job ads that were identical except for gendered wording rated
the masculine-coded jobs as less appealing and reported a lower sense of
belonging, while their assessment of their own *ability to do the job didn't
change*. (Men showed no such effect.) Self-selection is a quiet filter:
no one is rejected, nothing shows up in the hiring statistics, and qualified
people don't apply.

The complaint that opens this story described a workplace drained of
masculine energy. The corpus records something else: this register has been
on careers pages since SpaceX's 2003 hiring criteria, and the companies that
lead with exclusion carry the most of it.
