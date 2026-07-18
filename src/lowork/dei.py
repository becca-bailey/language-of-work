"""DEI register classification for mission/brand chunks."""

from __future__ import annotations

import json
import time

from anthropic import Anthropic

from .config import REGISTER_MODEL

# Registers are purely the PRO-INCLUSION intensity scale (+ absent). Opposition /
# counter-programming (meritocracy-as-contrast, civilizational framing) is a STANCE,
# owned by dei_stance.py — it was removed from this taxonomy because a single-label
# classifier mixing the two dimensions had to drop one whenever a chunk carried both.
DEI_REGISTERS = [
    "explicit_demographic",
    "structural_process",
    "aspirational_vague",
    "belonging_culture",
    "absent",
]

# Active DEI registers (pro-inclusion employer rhetoric)
ACTIVE_DEI_REGISTERS = [
    "explicit_demographic",
    "structural_process",
    "aspirational_vague",
    "belonging_culture",
]

SYSTEM_PROMPT = """You classify text chunks from archived company careers pages by DEI register — a scale of PRO-INCLUSION employer rhetoric.

These chunks come from careers/mission pages. Measure what the company says about inclusion AS AN EMPLOYER — who it hires, promotes, and retains — not social impact, product mission, or customer demographics. This axis measures only the PRESENCE and KIND of pro-inclusion language; opposition or counter-programming (meritocracy-vs-identity framing, apolitical or civilizational employer branding) is measured on a separate stance axis and is NOT a register — such chunks are `absent` here unless they also carry pro-inclusion language.

Assign exactly one register to each chunk:

- explicit_demographic: names one or more specific demographic groups (by race/ethnicity, gender, LGBTQ+, veteran status, disability, age, etc.) as the SUBJECT of affinity, celebration, support, or aspiration in the company's own workforce — employee resource groups (BLACKHub, Outforce, women's networks), spotlights, support statements ("Salesforce stands with the Black community"), and representation targets or callouts ("increasing Black and Latinx representation in leadership to 30% by 2025" — a stated goal is a callout, not a mechanism). The distinguishing feature is a NAMED group as the object of rhetoric, not the presence of a metric.
- structural_process: describes a CONCRETE, OPERATING mechanism for reducing bias or enforcing accountability in employment — structured interviews, pay-equity audits ("we audit our pay practices annually"), mandatory inclusive-hiring training, published workforce-diversity measurement and reporting, compensation tied to inclusion outcomes. The mechanism wins even when a demographic group is named as its object ("achieved and maintained gender pay equity" → structural_process). Commitments or initiatives WITHOUT a described mechanism ("initiatives to break down systemic barriers") are aspirational_vague, not structural_process.
- aspirational_vague: GENERIC inclusion/diversity language that does NOT name a specific demographic group — "diverse perspectives," "varying backgrounds," "an inclusive workplace," broad pride or partnerships without naming who. If a specific group is named in a workforce context, prefer explicit_demographic.
- belonging_culture: worker experience of inclusion stated generically, WITHOUT naming a specific group — "Bring your whole self to work." / "Everyone feels they belong here."
- absent: no pro-inclusion employer language — generic mission/innovation copy, customer impact, product features, standard recruiting boilerplate. ALSO includes anti-DEI or counter-programming framing ("we hire on merit, not identity politics", civilizational/geopolitical employer branding like "the future of the West") — that is a stance, not a register, and is classified elsewhere.

Tie-breakers:
1. If a chunk mixes registers, choose the DOMINANT one.
2. STRUCTURE BEATS NAMING: if the substance of the chunk is an operating mechanism (audit, mandatory training, measurement/reporting system, comp linkage), it is structural_process even if a demographic group is named as the mechanism's object. Naming a group is enough for explicit_demographic only when the group is the subject of affinity/support/target rhetoric (ERGs, spotlights, support statements, representation callouts) rather than a mechanism.
3. Generic "diversity" / "inclusion" / "varying backgrounds" that names NO specific group → aspirational_vague, not explicit_demographic. Measurement/accountability machinery that names no group ("we publish an annual diversity report and share representation data with senior leaders") → structural_process, not aspirational_vague.
4. Demographics purely in CUSTOMER, patient, or societal-impact context (not the company's own workforce) → absent. This includes CSR / philanthropy / community content: foundation grants, community volunteering, youth or education programs, supplier and producer sustainability. Words like "underserved," "diverse backgrounds," or even named groups describing program BENEFICIARIES or the surrounding community are NOT employer inclusion language.
5. "Hire the best" / engineering excellence / merit-vs-identity contrast / civilizational framing → absent (measured on the stance axis, not here).
6. EEO/legal boilerplate alone → absent unless substantive DEI commitments beyond compliance.
7. belonging_culture requires a described worker EXPERIENCE of inclusion ("bring your whole self to work", "everyone feels they belong here", "a place for every kind of brilliant"). Belonging/representation stated as a company goal, program, or brand identity ("we're building belonging through...", "a team that reflects the world") → aspirational_vague. Belonging language about remote-work logistics, culture-doc meta-commentary, or navigation stubs → absent.
8. Enumerating demographic CATEGORIES without naming a group ("...including gender, race, age, national origin, sexual orientation, culture, education") → aspirational_vague — it is the "diversity of all kinds" move. But a named employee COMMUNITY is explicit_demographic even for a non-protected group (a Parents and Families ERG counts, like any ERG). Employee spotlights, displayed workplace awards, and page headlines naming a group ("A great workplace for women", "100 Best Workplace for Women") → explicit_demographic even when the surrounding body copy is generic.

Calibration examples (trust these over surface keywords):

→ absent (counter-programming is a STANCE, not a register):
"We built Palantir to ensure the future of the West, not to tinker at the margins."
"We hire on merit, not identity politics — we don't run DEI programs or set demographic hiring targets."

→ explicit_demographic (names a specific group in a workforce context — target NOT required):
"We are proud to partner with Lean In, offering women encouragement and support to achieve their goals."
"Palantir Scholarship for Women in Technology" / Girl Geek Dinner spotlights.
"BLACKHub is our community of Black employees." / "Outforce, our LGBTQ+ employee resource group."
"Salesforce stands with the Black community against racism."

→ structural_process (an operating mechanism — even when a group is named as its object):
"Since 2017, Apple has achieved and maintained gender pay equity. In the United States, we have also achieved pay equity with respect to race and ethnicity."
"All of our hiring managers and recruiters are trained in inclusive hiring practices. These mandatory trainings help eliminate inherent biases."
"We publish this report. We share departmental representation data with our most senior leaders to provide insight into hiring, progression, and retention."
"100% of executives have compensation tied to the building of inclusive and diverse teams."

→ explicit_demographic, NOT structural_process (a target/callout is rhetoric, not a mechanism):
"Increasing Black and Latinx representation in leadership to 30% by 2025."

→ aspirational_vague, NOT structural_process (commitment language without a described mechanism):
"We have several ongoing and upcoming initiatives to help break down systemic barriers and bias."
"The work that we're doing is structural, and when you stand in the work you get closer to the root cause."

→ aspirational_vague (generic inclusion, NO specific group named):
"We celebrate diverse perspectives and varying backgrounds."
"We're building an inclusive workplace where everyone can do their best work."

→ absent (generic mission):
"We solve hard problems with data." / "We build software that helps organizations make better decisions."

→ absent (CSR / philanthropy / community — about beneficiaries, not the workforce):
"Contributing positively to our communities and environment is a guiding principle of our mission. We encourage and reward volunteerism and participation in organizations that are important to our partners."
"Our Foundation funds programs for underserved youth that embrace diversity and build bridges of understanding among youth of diverse ethnic, racial and socio-economic backgrounds."
"We have a strong commitment to coffee producers, their families and communities."

→ aspirational_vague, NOT explicit_demographic (generic diversity of thought, no group named):
"The sort of creativity that only comes about when talented people from diverse backgrounds approach problems from varying perspectives."
"Our diverse perspectives come from many sources including gender, race, age, national origin, sexual orientation, culture, and education." (categories enumerated, no group named)

→ aspirational_vague, NOT belonging_culture (belonging as goal/brand, not described experience):
"We're building belonging through: a more inclusive workplace, co-creation in our products, unlocking opportunity in society."
"We are dedicated to building a community and team that reflects the world we live in."

→ explicit_demographic (spotlights, awards, and group-titled pages are deliberate signaling):
"Googler Shaun Aukland gained international attention when he asked his boyfriend..." (employee spotlight)
"A 100 Best Workplace for Women and Best Workplace in Tech by Fortune."

Respond with a JSON array, one object per chunk, in input order:
[{"id": "<chunk id>", "register": "<register>"}]
Use only the registers above. Respond with the JSON array only."""

BATCH_SIZE = 12


def heuristic_register(text: str) -> str:
    """Keyword fallback for offline bootstrap — not for production scoring.

    Counter-programming (civilizational framing, merit-vs-identity) is a STANCE
    (see dei_stance.py) — on the register axis it reads as absent, which the
    keyword flow below produces naturally (no inclusion vocabulary).
    """
    t = text.lower()

    if not any(
        w in t
        for w in (
            "divers",
            "inclus",
            "belong",
            "equity",
            "represent",
            "underrepresented",
            "bias",
            "merit",
            "whole self",
            "girl geek",
            # named demographic groups count on their own (softened
            # explicit_demographic rule) — the gate must let them through
            "black",
            "latinx",
            "hispanic",
            "lgbtq",
            "veteran",
            "disabilit",
            "women",
        )
    ):
        return "absent"

    # Naming a specific demographic group in a workforce context is enough (no target
    # required) — matches the softened explicit_demographic rule in SYSTEM_PROMPT.
    if any(w in t for w in ("black", "latinx", "hispanic", "lgbtq", "veteran", "disabilit")):
        return "explicit_demographic"
    if "women" in t and not any(w in t for w in ("breast cancer", "mammograph", "patient", "screening")):
        return "explicit_demographic"
    if any(w in t for w in ("audit", "structured interview", "pay gap", "promotion process", "bias training")):
        return "structural_process"
    if any(
        w in t
        for w in (
            "regardless of background",
            "same criteria",
            "don't lower our standards",
            "best people, period",
            "identity politics",
            "don't do dei",
            "not identity",
            "meritocracy",
            "merit, not",
        )
    ):
        return "absent"  # merit-vs-identity contrast is a stance, not a register
    if any(w in t for w in ("whole self", "bring your", "culture of", "feel welcome")):
        return "belonging_culture"
    return "aspirational_vague"


def _parse_batch_text(text: str, results: dict[str, str]) -> None:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    for item in json.loads(text):
        reg = item["register"]
        if reg not in DEI_REGISTERS:
            reg = "absent"
        results[item["id"]] = reg


def _request_params(batch: list[dict], model: str) -> dict:
    payload = [{"id": c["chunk_id"], "heading": c["heading"], "text": c["text"]} for c in batch]
    return {
        "model": model,
        "max_tokens": 3000,
        # A 7-way label doesn't need reasoning tokens; Sonnet-5 runs adaptive
        # thinking by default when the field is omitted, which bills thinking
        # on every call — disable explicitly to keep cost down.
        "thinking": {"type": "disabled"},
        # Shared prompt prefix: cache-eligible when it clears the model minimum.
        "system": [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
    }


# Below this many chunks the polling overhead of the Batches API isn't worth it.
SYNC_THRESHOLD = 50


def classify_registers(chunks: list[dict], model: str = REGISTER_MODEL) -> dict[str, str]:
    """Classify chunks -> {chunk_id: register}.

    Large runs go through the Message Batches API (50% price, async, poll to
    completion); small runs stay synchronous.
    """
    client = Anthropic()
    results: dict[str, str] = {}
    groups = [chunks[i : i + BATCH_SIZE] for i in range(0, len(chunks), BATCH_SIZE)]

    if len(chunks) <= SYNC_THRESHOLD:
        done = 0
        for batch in groups:
            resp = client.messages.create(**_request_params(batch, model))
            text = next((b.text for b in resp.content if getattr(b, "type", None) == "text"), "")
            _parse_batch_text(text, results)
            done += len(batch)
            print(f"  classified {done}/{len(chunks)}")
        return results

    # Batches API: half price; most batches finish well within the hour.
    mb = client.messages.batches.create(
        requests=[
            {"custom_id": f"grp-{gi}", "params": _request_params(batch, model)}
            for gi, batch in enumerate(groups)
        ]
    )
    print(f"  batch {mb.id}: {len(groups)} requests ({len(chunks)} chunks), polling...")
    while True:
        mb = client.messages.batches.retrieve(mb.id)
        if mb.processing_status == "ended":
            break
        time.sleep(20)

    errors = 0
    for result in client.messages.batches.results(mb.id):
        if result.result.type == "succeeded":
            msg = result.result.message
            text = next((b.text for b in msg.content if getattr(b, "type", None) == "text"), "")
            _parse_batch_text(text, results)
        else:
            errors += 1
            print(f"  batch item {result.custom_id}: {result.result.type}")
    if errors:
        print(f"  WARNING: {errors} batch item(s) failed; {len(results)}/{len(chunks)} classified")
    return results


