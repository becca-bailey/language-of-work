# Phase 2 Pilot — Findings Memo: GitLab Family & Friends Day

Status: **pilot findings memo, not Phase 6 write-up material.** This records what the
GitLab F&F Day pilot actually established and — more importantly — the three findings worth
digging. It is a skeleton of *what* and *when*; every claim that matters is a *why*, and
the *why* lives in the MR-description / page-diff layer we have not yet mined. Each
load-bearing claim below is tagged **[pending MR-description confirmation]**.

A note on what this memo is *not*: "improvised → formalized → institutionalized → absorbed"
is a chronology, not a finding. It is the normal life of any surviving policy. Bucketing
commits into five named phases is not yet an argument. The three items below are the
argument; they were buried in clauses in the first pass and are promoted here to claims.

---

## Finding 1 (headline) — The correction is a methodology result, not a GitLab result

We went looking for "COVID measure → permanent benefit," a clean arc handed in as *known
ground truth* for the pilot to validate against. **The commits do not support it.** There is
no conversion commit; the live page still frames F&F Day as pandemic-contingent ("planned
to continue for as long as the majority of the world was dealing with the pandemic").

This matters far beyond one benefit. The Phase 2 design uses this arc as the validation
case — the known-truth the pipeline is checked against. If the "known" arc was partly a
narrative convenience rather than the record, then the pilot's entire job is to catch that
— and it did, by hand, from primary sources. **The finding is: reconstructing from the
primary record overturned the tidy secondhand story.** That is the epistemic pitch of the
whole project in miniature, and it retroactively justifies the version-control methodology.
It belongs at the front of any write-up of this pilot.

*Solid — this one does not depend on the unmined layer; it is an absence (no conversion
commit) plus present-tense page content.*

## Finding 2 (most quotable) — The six-day rename wobble is a revealed preference

For six days in April 2021 the benefit was renamed **"Pandemic Support Day,"** then reverted
to "Family and Friends Day," and the contingency question was never resolved in writing.

Read it for what it is: the company briefly made the benefit's *contingency* explicit in its
name, recoiled, and buried the ambiguity. That is not indecision. It is a revealed
preference for keeping the commitment **legible-as-generous while keeping the actual
obligation deniable** — the exact cheap-talk-vs-commitment seam this study is built to
detect, surfacing as a six-day naming flinch. Potentially the single most quotable moment
in the eventual close-up.

**[pending MR-description confirmation]** — did an MR description or discussion resolve the
naming question? "Never resolved in writing" is currently inferred from commit subjects.

## Finding 3 (structural crux) — "Adds teams with coverage requirements" is the privatization moment

2022-07-26, "Adds teams with coverage requirements to F&F description." The summary walked
past this in a clause; it is the mechanism.

A synchronized company-wide shutdown is *structural* only if nobody has to stay back. The
instant coverage requirements are added, the company has admitted that **some people absorb
the cost so others can rest.** That is the individual-vs-structural distinction stated by
GitLab's own operations, not by our codebook — and it is the mechanism by which even a
structural benefit **partially privatizes under pressure.**

**[pending MR-description confirmation]** — which teams, and the stated rationale, live in
the diff/MR, not the subject line.

---

## The binding constraint on all three

This is reconstructed from **commit subjects.** Findings 2 and 3 each rest on a *why* that
lives in the layer we have not mined (MR descriptions, page-text diffs). Honest status: a
solid skeleton of *what* and *when*; the three actual findings depend on *why*, which is
currently inference. That is not a flaw — it is a stopping point. The pilot has done its job:
it found the seams worth digging.

## Directive — code both events explicitly, as schema test cases

Add the two events to the flow data as explicit, coded events — but for a sharper reason
than completeness:

- **The "Pandemic Support Day" rename is the `change_type: reframe` test case** — the one
  where the *meaning* changes and the *benefit* does not. If the change-type schema cannot
  cleanly represent this, we need to know now.
- **"Coverage requirements" is the first concrete `structural → partially-individual`
  transition** — the locus schema's hardest job. If the locus schema cannot represent a
  benefit that is structural in principle and individual in incidence, better to learn it
  here, on the case we understand best, than at corpus scale.

They are not just events to log; they are the two events that validate whether the
change-type and locus schemas can capture the things that turned out to matter.

## Guardrail — this is a close-up, not the centerpiece

Resist letting F&F Day become the centerpiece merely because it is the case we have spent the
most time in. It is **one company, self-selected for transparency, with a thin external
footprint** — a mechanism illustration. The centerpiece remains the **cross-company
individualization index**; F&F Day is the vivid close-up that shows the mechanism the
aggregate can only imply.
