# The Language of Work

**A computational study of how tech companies describe themselves as employers — and what that language reveals about power.**

Careers pages are corporate self-presentation at its most deliberate: every word is chosen to attract workers. I treated two decades of them — more than a dozen tech companies, 2005–2026, reconstructed from the Wayback Machine — as a longitudinal record, and asked what the language does over time, when it shifts, and why.

The guiding idea is a counterforces thesis: a workplace culture doesn't stay good because leaders care about it; it stays good while specific counterforces — chiefly workers' bargaining power — hold ordinary decay back. When that leverage erodes, the *language* of values persists as liturgy while the practice reverts. The 2010s bet that a new generation would fix work wasn't so much wrong as **rented, not owned** — the gains tracked the labor market and receded when it inverted.

The data bears this out across several studies:

- **Idealism** ("change the world" copy) peaked in the early-mid 2010s and collapsed — Amazon from a +1.8 within-company z-score in 2013 to neutral by 2026.
- **DEI language** was adopted industry-wide, then quietly retracted after 2023, with some firms actively counter-programming.
- **Care and well-being talk** spiked with the Great Resignation and deflated as quit rates fell — and the care that endured was the kind workers absorb themselves (therapy apps), not the kind the company absorbs (family and caregiving support).
- Throughout, the **management-serving substrate** — performance intensity — barely moves. The worker-serving language is what surges, and what gets cut.

**How it's built.** Each study runs on a shared pipeline: archived pages are chunked, classified by an LLM into registers, and scored on **embedding-based contrast axes** (care↔intensity, idealism↔pragmatism, DEI stance…), each paired with a neutral control axis and a circularity check so an axis measures a *concept*, not a company's own vocabulary. Structured LLM extraction pulls benefits into taxonomies validated against hand-coded samples (Krippendorff's α ≈ 0.9 on the hardest labels). Claims are stress-tested with coverage-controlled statistics — bootstrap confidence intervals, within-company correlations, an external labor-market leverage series — and when the data can't carry a claim, I say so: one of the central hypotheses turned out too sparse to test at the resolution the archive allows, and it's reported as a limit rather than smoothed over.

The results are published as **interactive data stories** (Astro + React + visx), with accessibility-validated color palettes and light/dark support.

The part I'm proudest of is the discipline. Reconstructing the record from primary sources overturned the tidy, secondhand version more than once — a benefit I'd been told "converted from temporary to permanent" turned out, in the version-controlled handbook, to have done no such thing. The honest nulls are as much the point as the findings.

**Stack:** Python (embeddings, LLM pipelines, pandas/scipy), OpenAI + Anthropic APIs, a SQLite embedding cache, a content-hash pipeline DAG for reproducible re-runs, and an Astro / React / visx front end.

---

### Short version (project card)

*The Language of Work* reads two decades of tech companies' careers pages as a record of power: worker-facing language — idealism, DEI, care — surges when workers have leverage and is quietly cut when they don't, while management-facing performance language never moves. Built on an embedding-and-LLM pipeline over Wayback-archived pages, with validated codebooks, coverage-controlled stats, and interactive data stories.
