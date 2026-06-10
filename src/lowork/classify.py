"""Chunk classification with a pinned small LLM, validated against hand labels."""

from __future__ import annotations

import json

from anthropic import Anthropic

from .config import CHUNK_LABELS, CLASSIFIER_MODEL

SYSTEM_PROMPT = """You classify text chunks extracted from archived company careers pages.

Assign exactly one label to each chunk:

- mission_brand: company mission, values, culture, "why work here" brand copy, statements about impact or what the company believes
- job_listing: job postings AND team/department descriptions — what a team does, its responsibilities, the work involved, qualifications. Even when phrased aspirationally ("change the world"), if the subject is what a team/role does, it is job_listing
- benefits_perks: compensation, health benefits, perks, food, offices-as-perk, time off, learning stipends
- process_logistics: how to apply, interview process, application status, hiring timeline, FAQs about applying — including prose that directs applicants where to go ("check out our teams and roles", "connect with us on social media", "still a student? visit our student site")
- legal_boilerplate: EEO statements, privacy notices, accommodation notices, legal disclaimers — substantive legal prose only
- navigation_junk: menus, link lists, button labels, category/department name lists, cookie banners, page chrome, fragments with no real content

Many chunks mix content. Decide by the DOMINANT content, with these tie-breakers:

1. ANY text attached to a specific team, department, or job family is job_listing — descriptions of the team's work AND short aspirational taglines on team cards ("Engineering & Technology: Develop the products and tools of the future for billions of users", "Sales, Service & Support: Equip businesses with the right tools to help them grow"). Aspirational flavor does not make it mission_brand. mission_brand is reserved for text about the company as a whole: its mission, values, culture, offices, or impact — never a specific team or role.
2. A list of department names, locations, or links is navigation_junk even when a legal sentence (e.g. an agency-resume disclaimer) is appended to the end. legal_boilerplate requires the legal text to be the dominant content of the chunk, not a tail.
3. If a chunk contains substantive company-level prose followed by junk fragments (job counts, link labels, calls to action), classify by the prose and ignore the junk — "each one of our offices is designed to inspire innovation... 329 jobs 246 jobs" and playful brand copy like "Take a ride on the Google self-guided tour. Stop by our offices around the globe..." are mission_brand, not navigation_junk.
4. Short full-sentence directives aimed at applicants are process_logistics, not navigation_junk — e.g. "Check out our teams and roles to learn more" or "Still a student? This way to our student site." But a single framing stub followed by a list of links or channel names ("Use these social media channels to connect with us: @googlejobs Life at Google channel...") is navigation_junk — the list is the dominant content, not the sentence introducing it.

Respond with a JSON array, one object per chunk, in input order:
[{"id": "<chunk id>", "label": "<label>"}]
Use only the labels above. Respond with the JSON array only."""

BATCH_SIZE = 25


def classify_chunks(chunks: list[dict], model: str = CLASSIFIER_MODEL) -> dict[str, str]:
    """Classify chunks -> {chunk_id: label}. Batched, temperature 0."""
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
            label = item["label"]
            if label not in CHUNK_LABELS:
                label = "navigation_junk"
            results[item["id"]] = label
        print(f"  classified {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}")

    return results


def agreement_report(predictions: dict[str, str], hand_labels: dict[str, str]) -> dict:
    """Compare classifier output against hand labels; returns accuracy + confusion."""
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
