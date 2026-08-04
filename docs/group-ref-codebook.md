# Group-reference coding codebook

The shared rules for coding references to marginalized groups in a founder-blog
corpus — used by **both** the human labeler and the LLM prompt
(`prompts/group_references.yaml`). When the two disagree, the fix is almost
always to sharpen a rule here first, then re-run and re-label a fresh sample.

Developed 2026-08-01/02 from the first 8 hand-labels of `dhh_blog` (Becca +
model). Those 8 are **codebook-development examples, not validation** — they
were revised after the model's predictions were seen, so they can't measure
blind agreement. The real α comes from a fresh, cold sample labeled against
this document.

## Unit of analysis: the post

Code at the **post** level, not the passage. A post reduces to a set of
`(group → worst frame present)`. The model emits one entry per passage and
segments arbitrarily (it split one post into six near-identical entries); we
never rely on that segmentation. Raw passage counts survive only as a
secondary field (`nMentions`), never a headline.

- `has_reference`: does the post reference any marginalized group at all (y/n).
- `pairs`: for each group referenced, its **worst** frame — `group:frame`,
  separated by `;` or `,`. One frame per group (the most hostile present).

## Groups

Full definitions in `prompts/group_references.yaml`. Codes:
`migrants_refugees`, `roma`, `muslims`, `jews`, `black_people`,
`trans_people`, `lgbtq_other`, `women`, `other_minoritized` (name it in
`group_name`). A brief or sympathetic mention still counts — there is no
salience floor (see Ruling 4).

## Frames (severity order, worst wins)

Ordered most-hostile-toward-the-group to least. In a post that references a
group several ways, the **worst** frame present is the post's frame for that
group.

1. **`threat_crime_framing`** — the group itself is characterized as a danger:
   crime, violence, disease, demographic threat, cultural incompatibility,
   animalizing comparison paired with harm, or a call for removal /
   deportation / exclusion.
2. **`hostile_derogatory`** — open hostility toward the group that stops short
   of threat: contempt, mockery, ridicule, dehumanizing put-downs, slurs, or
   denial of the group's identity, with no danger/crime/removal asserted.
3. **`policy_critique`** — argues for/against policy (immigration, asylum,
   housing, integration, policing) where the criticism targets governments,
   laws, or institutions rather than characterizing the group.
4. **`neutral_mention`** — no evaluative framing: incidental mention, history,
   statistics reported without a group-level conclusion, third-party quote
   without endorsement.
5. **`sympathetic_defense`** — defends, humanizes, or advocates for the group,
   or criticizes their mistreatment.

## Rulings (the decisions that resolve the hard cases)

**1. Worst-frame collapse.** A post is threat-framed if it contains even one
group-as-threat passage, even when the rest is policy talk or observation.
*Danish fairytale* is a threat post on the strength of its murder-rate
call-out alone, though much of it is dry political observation.

**2. A calm, analytical register does not downgrade a threat.** "Poison for
national unity," "some cultures are outright impossible to integrate,"
delivered with citations and statistics, is `threat_crime_framing`, not
`policy_critique`. The measured tone is not evidence of neutrality — it is
often the register in which the strongest claims are made.

**3. Direction of hostility.** The frame is about hostility directed *at* the
group. Describing *others'* hostility toward the group ("the broad Danish
hostility to foreigners") or the *state's treatment of* the group ("hunted by
the culture and the state") is **not** threat — code it `neutral_mention` or
`policy_critique` or `sympathetic_defense` by what is actually argued. Threat
is when the group is cast as the source of danger.

**4. Hostility is not threat; code only what is literally present.** Contempt,
mockery, or identity-denial ("men who said they were women") is
`hostile_derogatory` — real hostility, but not threat, because no
danger/crime/removal is asserted. Do **not** upgrade to threat because the
rhetoric is the kind that "leads to" threat elsewhere; code the words on the
page. (This is why the fifth frame exists — without it such passages
wrongly fall to `neutral`.)

*But the reverse also holds:* if the passage asserts the group **commits
violence or crime** (killing, stabbing, assault, rape, bombing), it is
`threat_crime_framing` even when wrapped in contempt or a slur ("crazy
Muslims killing or stabbing…"). The violence/crime assertion controls; the
derogatory wording does not downgrade it to `hostile_derogatory`. Hostile is
only for contempt/mockery/identity-denial with **no** violence/crime/removal
claim.

**5. Sympathy target (the "Linehan rule").** `sympathetic_defense` requires
the sympathy to be directed at the marginalized group itself. Sympathy for a
figure *hostile* to the group (e.g. defending an anti-trans campaigner's
arrest) is not `sympathetic_defense` toward that group — code the passage by
how the group itself is treated, which is often `hostile_derogatory` or
`neutral_mention`.

**6. No salience floor.** A brief or passing reference counts, including a
sympathetic aside (Ukrainian refugees "welcomed without visas" is a
`migrants_refugees` reference — coded `policy_critique` there for the
double-standard argument it sets up).

## Worked examples (from the corpus, post-level)

| post | group:frame | why |
|---|---|---|
| Failed integration (2025) | migrants_refugees:threat | "poison," "impossible to integrate" — Ruling 2 |
| Danish fairytale (2024) | migrants_refugees:threat | murder-rate/crime call-out (R1); "Danish hostility to foreigners" alone would be neutral (R3) |
| Europeans don't understand free speech (2025) | muslims:threat; trans_people:hostile_derogatory; migrants_refugees:threat | "crazy Muslims killing or stabbing" = threat; "men who said they were women" = hostile not threat (R4) |
| America is never getting to Denmark (2023) | migrants_refugees:sympathetic | "most welcoming, open, integratable country" |
| The other side of social media (2022) | migrants_refugees:policy_critique | Ukrainian-refugee double standard (R6) |

## Status / open decisions

- **Fifth frame `hostile_derogatory` adopted 2026-08-02** — live in the prompt
  (`group_references.yaml`, now **v3**), the exporter, the validation script,
  and the chart (5 frames; hostile + threat as adjacent warm colors). v3 adds
  the "violence/crime assertion controls" clause to boundary rule 1, after v2
  wrongly downgraded "crazy Muslims killing or stabbing" to hostile.
- Next: label a **fresh, unseen** sample cold against this codebook — that is
  the α that counts (pre-registered thresholds in
  `docs/basecamp-founder-speech-pilot.md`). The pre-v2 sample CSV is stale
  (coded against the four-frame set) and should be regenerated after the
  re-run.
