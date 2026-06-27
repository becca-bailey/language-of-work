# Netflix performance-culture: propagation findings (validated)

**Method.** Concept-level semantic matching: each Netflix concept has anchor sentences
(canonical + paraphrases), embedded; a company's culture sentence "expresses" a concept
when max cosine similarity ≥ **0.62** (tuned against `culture_propagation_review.md` —
0.55 over-matched generic "great team / hire the best" copy). A verbatim regex runs
alongside as a high-confidence overlay. Netflix 2009 deck seeded as origin. Corpus =
careers/culture mission_brand text, cohort + adopters. **N small; this is
self-presentation, not practice.**

## The honest result: narrow verbatim propagation + broad convergence

### Tier 1 — Distinctively-Netflix language that propagated (the real signal)
- **"Adequate/unremarkable performance → a generous severance"** — the cleanest case.
  Netflix deck 2009: *"adequate performance gets a generous severance package."*
  **Coinbase 2024 (near-verbatim, sim 0.86): "Unremarkable performance gets a generous
  severance package."** A one-word edit. **Coinbase is Netflix's clear disciple** — it is
  the one company that put the brutal formulation on its own page.

### Tier 2 — Distinctively-Netflix mechanics that did NOT propagate (stayed Netflix-only)
In public careers copy, these remained essentially Netflix-only (next-best non-Netflix
match well below threshold):
- **Keeper test** (Netflix 0.80; next non-Netflix 0.47).
- **"High performer ≫ average employee"** (Netflix only).
- **"A team, not a family / pro sports team"** (Netflix verbatim 0.80; the lone other
  hit was a false positive about "star performers," dropped at 0.62).
- **Dream team / "stunning colleagues"** (Netflix only; generic "amazing team" copy
  dropped at 0.62).
- **Reading:** companies adopted the *ethos* but were unwilling to print the harshest
  mechanics — except Coinbase. The brutal logic stays mostly in-house at Netflix.

### Tier 3 — Generic vocabulary that is NOT Netflix-originated (do not attribute)
Industry-wide, convergent, predating/parallel to the deck — **excluded from the Netflix
propagation claim:**
- **"Raise the bar / relentlessly high standards"** — this is **Amazon's** Leadership
  Principle (Amazon 2017), not Netflix's; also Stripe, Brex, Shopify.
- **"Best and brightest / A-players / top talent"** — Palantir 2010, Amazon 2011,
  Coinbase 2024, Shopify, Brex. Generic elite-hiring language.
- **"Judged by outcomes"** — Palantir's civilizational-mission framing (2026), not a
  Netflix lift.

## Headline
Netflix authored the **canonical language** of the performance-filter culture. Its
*ethos* (high performance, only-the-best) is now industry-wide — but largely by
**convergence**, not traceable lift. Its *distinctive, brutal formulations* (keeper test,
fire-the-adequate, not-a-family) stayed almost entirely on Netflix's own page — with
**one striking exception, Coinbase**, which copied the severance line nearly verbatim.

## Connection to the thesis
The objectivity-claiming vocabulary ("the bar," "top talent," "high performer,"
"results") is everywhere — but only Netflix (and its disciple Coinbase) state the
underlying logic plainly: *we cut the people we judge merely adequate.* The softer,
ubiquitous language implies the same filter while hiding the subjectivity of who counts
as "adequate." See the objectivity audit + thesis layer.

## Guardrails honored
- Threshold validated on hand-inspected matches; matches inspectable (concept-echo vs.
  verbatim-lift) in `culture_propagation.json` / `_review.md`.
- Generic vs. distinctively-Netflix concepts separated; generic ones NOT claimed as
  propagation.
- Self-presentation, not practice; vocabulary adoption ≠ running the keeper test.
- Timing/precedence, not causation.
