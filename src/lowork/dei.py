"""DEI register classification for mission/brand chunks."""

from __future__ import annotations

import json
import re

from anthropic import Anthropic

from .config import CLASSIFIER_MODEL

DEI_REGISTERS = [
    "explicit_demographic",
    "structural_process",
    "aspirational_vague",
    "belonging_culture",
    "meritocracy",
    "civilizational_mission",
    "absent",
]

# Active DEI registers (pro-inclusion employer rhetoric)
ACTIVE_DEI_REGISTERS = [
    "explicit_demographic",
    "structural_process",
    "aspirational_vague",
    "belonging_culture",
]

# Counter-programming registers (stance opposite to workforce DEI adoption)
COUNTER_DEI_REGISTERS = ["meritocracy", "civilizational_mission"]

CIVILIZATIONAL_PATTERN = re.compile(
    r"\b(?:"
    r"future of the west|the west'?s most important|western (?:tech )?institutions|"
    r"warfighters?|battlefield|build with consequence|tinker at the margins|"
    r"technological republic|most important institutions|"
    r"empower the world'?s most important institutions"
    r")\b",
    re.I,
)

SYSTEM_PROMPT = """You classify text chunks from archived company careers pages by DEI register.

These chunks come from careers/mission pages. Measure what the company says about inclusion AS AN EMPLOYER — who it hires, promotes, and retains — not social impact, product mission, or customer demographics.

Assign exactly one register to each chunk:

- explicit_demographic: company-owned workforce commitments that name groups AND include accountability — representation targets, hiring goals, measurable gaps the company is closing. "We are committed to increasing Black and Latinx representation in leadership to 30% by 2025."
- structural_process: describes systems and processes designed to reduce bias in employment — "We use structured interviews to reduce bias in hiring." / "We audit our pay practices annually for equity."
- aspirational_vague: inclusion values, partnerships, or pride without binding specifics — generic diversity/inclusion claims, lists of "diverse perspectives" without targets, external partnerships (Lean In, ERG spotlights), encouragement without company accountability.
- belonging_culture: focuses on worker experience of inclusion at the company — "Bring your whole self to work." / "You'll find people here who look like you and think differently than you."
- meritocracy: explicitly frames hiring or advancement as purely performance-based IN CONTRAST to identity or background — language that crowds out demographic inclusion. Includes explicit anti-DEI positioning: rejecting identity-based hiring, DEI programs, or "politics" in hiring. "We hire on merit, not identity politics." / "We evaluate everyone on the same criteria regardless of where they come from." Generic "hire the best" or "brightest minds" alone is NOT meritocracy.
- civilizational_mission: employer brand framed around civilizational, geopolitical, or institutional mission rather than workforce inclusion — "future of the West," Western institutions, battlefield/consequence, serving the West's most important institutions. Distinct from generic product mission: this is an explicit civilizational hiring/identity pitch, often counter-programming DEI-era employer branding. Palantir-style "We built Palantir to ensure the future of the West" belongs here, NOT absent.
- absent: no workforce DEI-relevant language — generic mission/innovation copy, customer impact, product features, standard recruiting boilerplate without civilizational employer framing.

Tie-breakers:
1. If a chunk mixes registers, choose the DOMINANT one.
2. Naming a demographic is NOT enough for explicit_demographic — require workforce accountability (targets, programs, commitments). Partnerships, spotlights, and encouragement → aspirational_vague.
3. Generic "diversity" / "inclusion" / "varying backgrounds" without targets → aspirational_vague, not explicit_demographic.
4. Demographics in CUSTOMER, patient, or societal-impact context → absent unless civilizational employer framing dominates.
5. "Hire the best" / engineering excellence WITHOUT civilizational framing → absent or meritocracy only if explicit contrast with identity/DEI.
6. EEO/legal boilerplate alone → absent unless substantive DEI commitments beyond compliance.

Calibration examples (trust these over surface keywords):

→ civilizational_mission (NOT absent):
"We built Palantir to ensure the future of the West, not to tinker at the margins."
"Palantirians deliver mission-critical outcomes for the West's most important institutions."
"If you want to empower the world's most important institutions, you belong here."

→ meritocracy:
"We hire on merit, not identity politics — we don't run DEI programs or set demographic hiring targets."
"You are judged by outcomes. Your work will speak for itself." (when clearly about evaluation/hiring bar)

→ aspirational_vague (NOT explicit_demographic):
"We are proud to partner with Lean In, committed to offering women encouragement and support to achieve their goals."
"Palantir Scholarship for Women in Technology" / Girl Geek Dinner spotlights.

→ absent (NOT civilizational_mission — generic mission):
"We solve hard problems with data." / "We build software that helps organizations make better decisions."

Respond with a JSON array, one object per chunk, in input order:
[{"id": "<chunk id>", "register": "<register>"}]
Use only the registers above. Respond with the JSON array only."""

BATCH_SIZE = 25


def is_civilizational_mission(text: str) -> bool:
    return bool(CIVILIZATIONAL_PATTERN.search(text))


def heuristic_register(text: str) -> str:
    """Keyword fallback for offline bootstrap — not for production scoring."""
    t = text.lower()

    if is_civilizational_mission(text):
        return "civilizational_mission"

    if any(
        w in t
        for w in (
            "judged by outcomes",
            "work will speak for itself",
            "uncompromising engineering",
            "best and the brightest",
            "rigorous hiring standards",
        )
    ):
        return "meritocracy"

    if any(
        w in t
        for w in (
            "social or political activism",
            "refuge from division",
            "unrelated to our mission while at work",
            "don't engage in social",
            "do not engage in social",
        )
    ):
        return "meritocracy"

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
            "women in tech",
            "girl geek",
            "scholarship for women",
        )
    ):
        return "absent"

    if any(w in t for w in ("black", "latinx", "hispanic", "lgbtq", "veteran", "disabilit")):
        if any(w in t for w in ("representation", "target", "percent", "%", "workforce data", "increase")):
            return "explicit_demographic"
        return "aspirational_vague"
    if "women" in t and not any(w in t for w in ("breast cancer", "mammograph", "patient", "screening")):
        if any(w in t for w in ("lean in", "partner", "encouragement", "support to achieve", "scholarship", "girl geek")):
            return "aspirational_vague"
        if any(w in t for w in ("representation", "target", "percent", "%")):
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
        return "meritocracy"
    if any(w in t for w in ("whole self", "bring your", "culture of", "feel welcome")):
        return "belonging_culture"
    return "aspirational_vague"


def classify_registers(chunks: list[dict], model: str = CLASSIFIER_MODEL) -> dict[str, str]:
    """Classify chunks -> {chunk_id: register}. Batched, temperature 0."""
    client = Anthropic()
    results: dict[str, str] = {}

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        payload = [
            {"id": c["chunk_id"], "heading": c["heading"], "text": c["text"]} for c in batch
        ]
        resp = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        )
        text = resp.content[0].text.strip()
        if text.startswith("```"):
            text = text.strip("`").removeprefix("json").strip()
        for item in json.loads(text):
            reg = item["register"]
            if reg not in DEI_REGISTERS:
                reg = "absent"
            results[item["id"]] = reg
        print(f"  classified {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}")

    return results


def agreement_report(predictions: dict[str, str], hand_labels: dict[str, str]) -> dict:
    """Compare register output against hand labels."""
    common = [cid for cid in hand_labels if cid in predictions]
    if not common:
        return {"n": 0, "accuracy": None, "confusion": {}, "disagreements": []}

    correct = 0
    confusion: dict[str, dict[str, int]] = {}
    disagreements = []
    for cid in common:
        truth, pred = hand_labels[cid], predictions[cid]
        confusion.setdefault(truth, {}).setdefault(pred, 0)
        confusion[truth][pred] += 1
        if truth == pred:
            correct += 1
        else:
            disagreements.append({"chunk_id": cid, "hand_label": truth, "predicted": pred})

    return {
        "n": len(common),
        "accuracy": round(correct / len(common), 3),
        "confusion": confusion,
        "disagreements": disagreements,
    }
