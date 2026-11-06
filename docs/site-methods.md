# How the site is built — methods prose

Moved verbatim from the homepage "How it's built" section during the
2026-11 viz-first redesign; the homepage now carries a one-paragraph
summary. Source of truth for reliability numbers remains the validation
docs and pipeline outputs.

A shared pipeline chunks archived pages, uses an LLM to classify them
into registers, and scores them on embedding-based contrast axes —
each paired with a neutral control and a circularity check, so the
measure is stance rather than mere topical proximity. Structured
extraction pulls benefits into taxonomies validated against
hand-coded samples (Krippendorff's α = 0.90 for the well-being
locus codebook). Classifier agreement is measured the same way,
against blind hand-labeled samples spanning every company:
α = 0.81 for page-type classification as used in analysis
(0.76 over the full seven-way taxonomy, n = 440), α = 0.80 for
the finer-grained DEI registers (n = 201), and α = 0.98 for
DEI stance (n = 100; partly in-sample — the stance prompt was
refined against this sample's errors). The register number sits right at the
conventional 0.80 reliability bar — a caveat the DEI story
carries.


The embedding rankings are checked against instruments that fail
differently. An LLM judge re-ranks the same years by reading the
actual quotes — pairwise, order-randomized, with the concept
paraphrased so the judge never sees the axis's own pole phrases —
and an axis publishes only where the two rankings agree (Spearman
≥ 0.6; Netflix's performance axis passes at 0.62 by year and 0.77
by sentence, while the craft axis fails the same bar and stays
unpublished). The gender-coding axis carries its own battery:
known-answer occupation anchors, split-half reliability across its
sixteen word pairs, agreement with the published Gaucher gendered-word
dictionary (Spearman 0.66), and a masking test showing the company
ranking survives removal of every sentence containing gendered terms
or personal names (rank correlations 0.99 and 0.94).


Where the data can't carry a claim, the story says so rather than
reaching — the honest nulls matter as much as the findings. Story
prose is an AI-assisted synthesis of my drafts and the data,
reviewed and edited by me before publishing. Published as
interactive data stories built with Astro, React, and visx; the
pipeline is Python (embeddings, LLM APIs, pandas/scipy) over a
content-hash DAG.
