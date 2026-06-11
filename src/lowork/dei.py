"""DEI register classification for mission/brand chunks."""

from __future__ import annotations

import json

from anthropic import Anthropic

from .config import CLASSIFIER_MODEL

DEI_REGISTERS = [
    "explicit_demographic",
    "structural_process",
    "aspirational_vague",
    "belonging_culture",
    "meritocracy",
    "absent",
]

SYSTEM_PROMPT = """You classify text chunks from archived company careers pages by DEI register.

These chunks come from careers/mission pages. Measure what the company says about inclusion AS AN EMPLOYER — who it hires, promotes, and retains — not social impact, product mission, or customer demographics.

Assign exactly one register to each chunk:

- explicit_demographic: company-owned workforce commitments that name groups AND include accountability — representation targets, hiring goals, measurable gaps the company is closing. "We are committed to increasing Black and Latinx representation in leadership to 30% by 2025."
- structural_process: describes systems and processes designed to reduce bias in employment — "We use structured interviews to reduce bias in hiring." / "We audit our pay practices annually for equity."
- aspirational_vague: inclusion values, partnerships, or pride without binding specifics — generic diversity/inclusion claims, lists of "diverse perspectives" without targets, external partnerships (Lean In, ERG spotlights), encouragement without company accountability.
- belonging_culture: focuses on worker experience of inclusion at the company — "Bring your whole self to work." / "You'll find people here who look like you and think differently than you."
- meritocracy: explicitly frames hiring or advancement as purely performance-based IN CONTRAST to identity or background — language that crowds out demographic inclusion. Includes explicit anti-DEI positioning: rejecting identity-based hiring, DEI programs, or "politics" in hiring. "We hire on merit, not identity politics." / "We don't do DEI — we hire the best." / "We evaluate everyone on the same criteria regardless of where they come from." Generic "hire the best" or "brightest minds" alone is NOT meritocracy.
- absent: no workforce DEI-relevant language — mission/innovation copy, customer impact, patient populations, product features, standard recruiting, leadership principles, EEO boilerplate alone.

Tie-breakers:
1. If a chunk mixes registers, choose the DOMINANT one.
2. Naming a demographic is NOT enough for explicit_demographic — require workforce accountability (targets, programs, commitments). Partnerships, spotlights, and encouragement → aspirational_vague.
3. Generic "diversity" / "inclusion" / "varying backgrounds" without targets → aspirational_vague, not explicit_demographic.
4. Demographics in CUSTOMER, patient, or societal-impact context → absent (e.g. "breast cancer in women" as a patient population is medical, not workforce DEI).
5. Invention culture, shareholder letters, "smart people" / "people like you" recruiting → absent unless clearly DEI-framed.
6. EEO/legal boilerplate alone → absent unless substantive DEI commitments beyond compliance.
7. Employee spotlights mentioning background without company-level DEI framing → usually absent unless primarily about belonging.

Calibration examples (trust these over surface keywords):

→ aspirational_vague (NOT explicit_demographic):
"We are proud to partner with Lean In, committed to offering women encouragement and support to achieve their goals, including stories of Amazonians who Leaned In."
"We are builders who bring varying backgrounds, ideas, and points of view — gender, race, age, sexual orientation, culture, education — to inventing on behalf of customers."

→ absent (NOT meritocracy, NOT explicit_demographic):
"We hire the world's brightest minds and offer them an environment to invent and innovate." / Bezos shareholder letters about invention, platforms, and customer-centricity.
"AI can help detect breast cancer — the most common cancer in women worldwide — through mammography partnerships with hospitals."
"At Amazon, we believe every day is still Day One — your day to join a company that redefines itself every day."

→ explicit_demographic (requires workforce accountability):
"We are working to increase representation of women and Black employees in leadership, and we publish our workforce data annually."

→ meritocracy (requires contrast with identity/background OR explicit anti-DEI):
"We hire the best people regardless of background — we evaluate everyone on the same criteria and don't lower our standards."
"We hire on merit, not identity politics — we don't run DEI programs or set demographic hiring targets."
"Our culture is a meritocracy: excellence is the only criterion that matters in who we hire and promote."

→ absent (NOT meritocracy — mission/idealism without hiring contrast):
"We solve the world's hardest problems with software" / Palantir mission copy about impact and engineering excellence without contrasting merit with identity or rejecting DEI.

Respond with a JSON array, one object per chunk, in input order:
[{"id": "<chunk id>", "register": "<register>"}]
Use only the registers above. Respond with the JSON array only."""

BATCH_SIZE = 25


def heuristic_register(text: str) -> str:
    """Keyword fallback for offline bootstrap — not for production scoring."""
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
        )
    ):
        return "absent"
    if any(w in t for w in ("black", "latinx", "hispanic", "lgbtq", "veteran", "disabilit")):
        if any(w in t for w in ("representation", "target", "percent", "%", "workforce data", "increase")):
            return "explicit_demographic"
        return "aspirational_vague"
    if "women" in t and not any(w in t for w in ("breast cancer", "mammograph", "patient", "screening")):
        if any(w in t for w in ("lean in", "partner", "encouragement", "support to achieve")):
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
