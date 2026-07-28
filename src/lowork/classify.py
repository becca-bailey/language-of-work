"""Chunk classification with a pinned small LLM, validated against hand labels."""

from __future__ import annotations

import json

import krippendorff
from anthropic import Anthropic

from .config import CHUNK_LABELS, CLASSIFIER_MODEL

SYSTEM_PROMPT = """You classify text chunks extracted from archived company careers pages.

Assign exactly one label to each chunk:

- mission_brand: company mission, values, culture, "why work here" brand copy, statements about impact or what the company believes — company voice only, not individual employee narratives
- employee_story: "meet our people" profiles, named-employee career narratives, interview-style spotlights ("When Beryl joined...", "Rich's combat experience..."). Aspirational employee quotes still belong here. NOT mission_brand even when inspiring; NOT job_listing unless describing what a team does rather than one person's story
- job_listing: job postings AND team/department descriptions — what a team does, its responsibilities, the work involved, qualifications. Even when phrased aspirationally ("change the world"), if the subject is what a team/role does, it is job_listing
- benefits_perks: compensation, health benefits, perks, food, offices-as-perk, time off, learning stipends
- process_logistics: how to apply, interview process, application status, hiring timeline, FAQs about applying — including prose that directs applicants where to go ("check out our teams and roles", "connect with us on social media", "still a student? visit our student site")
- legal_boilerplate: EEO statements, privacy notices, accommodation notices, legal disclaimers — substantive legal prose only
- navigation_junk: menus, link lists, button labels, category/department name lists, cookie banners, page chrome, fragments with no real content

Many chunks mix content. Decide by the DOMINANT content, with these tie-breakers:

1. ANY text attached to a specific team, department, or job family is job_listing — descriptions of the team's work AND short aspirational taglines on team cards ("Engineering: Build products used by billions", "Sales: Help businesses grow with our tools"). Aspirational flavor does not make it mission_brand. mission_brand is reserved for text about the company as a whole: its mission, values, culture, offices, or impact — never a specific team or role.
2. A list of department names, locations, or links is navigation_junk even when a legal sentence (e.g. an agency-resume disclaimer) is appended to the end. legal_boilerplate requires the legal text to be the dominant content of the chunk, not a tail.
3. If a chunk contains substantive company-level prose followed by junk fragments (job counts, link labels, calls to action), classify by the prose and ignore the junk — e.g. "each one of our offices is designed to inspire innovation... 329 jobs 246 jobs" or playful brand copy like "Take a self-guided tour of our offices around the globe..." are mission_brand, not navigation_junk.
4. Short full-sentence directives aimed at applicants are process_logistics, not navigation_junk — e.g. "Check out our teams and roles to learn more" or "Still a student? Visit our student careers site." But a single framing stub followed by a list of links or channel names ("Use these social media channels to connect with us: @companyjobs Life at Company channel...") is navigation_junk — the list is the dominant content, not the sentence introducing it.
5. Chunks that open with e-commerce account chrome ("Hello. Sign in", "Today's Deals", "Gift Cards", "Your Account") are navigation_junk — even if mission copy follows. The chrome dominates; mission prose in a separate chunk would be mission_brand.
6. City or office location descriptions ("Seattle is a great place to work...", population, geography) are navigation_junk or benefits_perks, not mission_brand.
7. Statements of hiring STANDARDS or selectivity — who the company hires, how exceptional you must be ("exceptionally stringent hiring criteria", "we only hire the best", "our culture is not for everyone") — are mission_brand culture copy, NOT process_logistics. process_logistics is the mechanics of applying (steps, timelines, portals), never the company's philosophy about who gets in. This holds for early-web single-page careers dumps that mix a why-join pitch or standards prose with discipline lists and apply-instructions: the pitch/standards prose dominates (mission_brand); such a chunk is process_logistics only when it contains NOTHING but apply-mechanics.
8. A recruiting pitch that name-drops employees with one-line accomplishments as evidence ("Sounds intense? It is. Kendall T. built X, Jen Z. shipped Y") is mission_brand — the pitch is the dominant content and the names are illustrations. employee_story requires the individual's narrative to BE the content (a profile, interview, or career story), not a list of trophies inside company-voice copy.

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
    """Compare classifier output against hand labels; returns accuracy, alpha + confusion."""
    common = [cid for cid in hand_labels if cid in predictions]
    if not common:
        return {"n": 0, "accuracy": None, "krippendorff_alpha": None,
                "confusion": {}, "disagreements": []}

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

    labels = sorted({*hand_labels.values(), *predictions.values()})
    idx = {lab: i for i, lab in enumerate(labels)}
    reliability = [
        [idx[hand_labels[cid]] for cid in common],
        [idx[predictions[cid]] for cid in common],
    ]
    try:
        alpha = round(float(krippendorff.alpha(
            reliability_data=reliability, level_of_measurement="nominal")), 3)
    except ValueError:
        # e.g. every pair identical on a single label — alpha is undefined
        alpha = None

    return {
        "n": len(common),
        "accuracy": round(correct / len(common), 3),
        "krippendorff_alpha": alpha,
        "confusion": confusion,
        "disagreements": disagreements,
    }
