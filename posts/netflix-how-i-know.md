# A Team, Not a Family — and How I Know I'm Not Making It Up

*Draft. Everything here is editable — numbers are pulled from `data/netflix/validation_report.md`, so if you re-run the pipeline, re-check them.*

## The claim

In 2009, Netflix published a 125-slide deck on how it ran its culture. Sheryl Sandberg called it the most important document ever to come out of Silicon Valley. It defined a *performance-filter* culture in unusually blunt terms — "a team, not a family," the keeper test, talent density — and it defined "performance" with no metric at all.

My claim about Netflix is really two claims:

1. **The language traveled, but only the soft parts.** The harsh mechanics — the keeper test, "a team, not a family" — mostly stayed on Netflix's own page. What diffused to other companies was the deniable version: "we don't have rules," "dream team," "an amazing team." Coinbase lifted the severance line almost verbatim; Meta paraphrased the "no rules" ethos. The sharp idea decays into ambient HR boilerplate.

2. **The performance it all worships is never measured.** Across roughly 2,600 culture chunks in my corpus, the copy invokes merit again and again and never once names a metric. A basketball player has a hoop and a scoreboard. A company deciding it has the "best" talent has the keeper test — a manager's gut with a name.

That second claim is an argument, and you can take it or leave it. The first claim is a measurement, and a measurement can be wrong. This post is about the part I can actually be held to: **how do I know the performance-culture ranking I'm putting on a chart reflects the language, and not just my own prompt engineering talking back to me?**

## The thing I was afraid of

Here's the honest anxiety. To track how "performance-filter" language rose and fell over the years, I build an *axis* — a direction in embedding space defined by pole phrases I wrote — and I score each year's careers copy against it. Out comes a number per year, and therefore a ranking: this year was more performance-obsessed than that one.

But I chose the pole phrases. I chose how many top chunks to average. I chose the embedding model. A skeptic — including me at 3am — can reasonably ask whether the ranking measures *the concept* or measures *my choices*. If I only ever checked my method against my own method, I'd never find out. So I check it three ways that fail differently, and I decided the pass/fail thresholds **before** I looked at the numbers, so I couldn't move the goalposts.

### Check 1: Does a reader agree with the geometry?

The embedding ranks years by cosine geometry — cold vector math. So I built a completely different ranker that doesn't use the axis at all: an LLM that *reads the actual quotes and judges*.

It works as a tournament. I sample pairs of years, and for each pair I show the LLM two sets of real quotes — Year A and Year B — and ask a single either/or question:

> "Which set describes a more demanding, high-pressure work culture — one that stresses elite talent, relentless effort, and tough performance expectations?"

Three details matter, and each is a place the check could have been rigged:

- **The question paraphrases the concept without reusing my pole phrases.** If I'd fed the judge the same words I used to build the axis, of course they'd agree — they'd be reading the same text. By restating the idea in fresh language, I force the judge to rank on understanding, not word-matching. This is the whole ballgame; without it the agreement is circular and meaningless.
- **I randomize which year is shown as "A."** LLMs have a known bias toward the first option. If I didn't flip the order, part of my result would just be "the judge likes slot A."
- **Pairwise, not holistic.** I never ask the model to rank twenty years at once — it's unreliable at that. Binary comparisons it can do well, and a bit of chess-rating math (Bradley-Terry) turns a pile of "A beat B" outcomes into one strength score per year.

Now I have two rankings of the same years from two mechanisms that share no failure mode, and I compare them with **Spearman rank correlation** — a measure of whether two lists sort things the same way, ignoring scale. I set the bar at 0.6 in advance.

**Netflix's performance axis scored 0.616.** A pass — but a modest one, so I didn't stop there. The sentence-level version of the same test came in at **0.766**, which is what convinced me the 0.616 wasn't a fluke. The reader and the geometry are looking at the same rise and fall.

### Check 2: Is the ranking hostage to any single phrase I wrote?

I defined the axis with a handful of pole sentences. What if the whole result rests on one lucky phrase? So I drop each pole sentence, one at a time, rebuild the axis, re-rank the years, and check how much the ranking moves. If pulling any single brick collapses the wall, the wall was never solid.

**Netflix's worst-case leave-one-out correlation was 0.956** (average 0.989). The ranking barely flinches no matter which phrase I remove. That's robust.

### Check 3: Am I measuring two things, or the same thing twice?

I have a separate "craft" axis. If "craft" and "performance" secretly point the same direction, then treating them as different findings is self-deception. So I check the angle between the two axis vectors directly. **They're nearly perpendicular** (cosine 0.093). Distinct concepts.

## The part that makes me trust it: the same method told me *no*

Here's what I'd want a skeptical reader to sit with. On the *exact same* Netflix corpus, same judge, same 40 comparisons, same settings, I ran the tournament for the **craft** axis instead of performance.

It scored **−0.09**. A flat fail. The reader and the geometry didn't just disagree on the margins — they were unrelated. So I don't publish a craft-over-time claim for Netflix.

That's the point. If my pipeline just rubber-stamped whatever I built, performance and craft would both have passed. One passed and one failed under identical conditions. **The failure is the evidence that the passing grade means something.** A validation suite that never fails isn't validating anything — it's decoration.

And it's not the only thing the checks caught. Netflix's *altruism* tournament came out weak overall (0.09), even though the early years agreed perfectly. That's why I validate one axis at a time, not one company at a time: the pipeline earns my trust for performance without earning it for altruism on the very same company.

## What I'm *not* claiming

Rigor includes saying where the edges are:

- **One judge, not a jury.** I use a single LLM at temperature 0 (deterministic). A more paranoid version would poll several models or several runs and keep only what they agree on.
- **Forty comparisons is not a census.** I sample year-pairs; a bigger sample would tighten the estimate.
- **Netflix's performance pass is real but marginal at the chunk level** (0.616 against a 0.6 bar). I lean on the stronger sentence-level number (0.766) to believe it, and I'd rather tell you that than round it up.
- **This measures the language, not the workplace.** Everything here is about what companies *wrote*, not what it was like to work there. The scoreboard critique is my argument; the rankings are the measurement. Keep them separate.

None of this proves Netflix's culture is good or bad. It means that when I say the performance-filter language rose, softened after the 2022–23 layoffs, and returned to its earlier highs in 2024, three independent checks agree on the shape — and when they *don't* agree, I don't make the claim.
