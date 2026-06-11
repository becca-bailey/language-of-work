"""Discrete DEI stance classification for mission/brand chunks."""

from __future__ import annotations

import json

from anthropic import Anthropic

from .config import CLASSIFIER_MODEL
from .dei import is_civilizational_mission

DEI_STANCES = [
    "affirming_dei",
    "neutral",
    "mission_focus_apolitical",
    "performance_elite",
    "civilizational_mission",
]

SYSTEM_PROMPT = """You classify text chunks from archived company careers pages by DEI stance.

These chunks come from careers/mission pages. Classify the company's STANCE on workplace inclusion and DEI — not product mission or customer demographics.

Assign exactly one stance to each chunk:

- affirming_dei: the company actively affirms DEI as an employer — belonging CTAs, diversity commitments, representation goals, inclusion programs, "bring your whole self" framing with company accountability.
- neutral: mission, innovation, recruiting, or benefits copy with no discernible stance on workplace DEI — standard product impact, generic engineering culture.
- mission_focus_apolitical: explicitly refuses workplace social/political activism unrelated to mission; apolitical company framing; "refuge from division"; keeps causes out of the workplace.
- performance_elite: high-performance / outcomes-based bar — judged by outcomes, uncompromising engineering standards, stunning colleagues, generous severance, not a family. About evaluation intensity, not geopolitics.
- civilizational_mission: employer identity framed around civilizational or geopolitical mission — "future of the West," Western institutions, battlefield/consequence, serving the West's most important institutions. Counter-programming to DEI-era employer branding without necessarily naming DEI.

Tie-breakers:
1. If a chunk mixes stances, choose the DOMINANT one.
2. Palantir "future of the West" / "West's most important institutions" → civilizational_mission.
3. Coinbase "refuge from division" → mission_focus_apolitical.
4. Netflix "sports team not family" → performance_elite.
5. 2013 women-in-tech scholarships / Girl Geek spotlights → affirming_dei.

Respond with a JSON array, one object per chunk, in input order:
[{"id": "<chunk id>", "stance": "<stance>"}]
Use only the stances above. Respond with the JSON array only."""

BATCH_SIZE = 25


def heuristic_stance(text: str) -> str:
    """Keyword fallback for offline bootstrap."""
    t = text.lower()

    if is_civilizational_mission(text):
        return "civilizational_mission"

    if any(
        w in t
        for w in (
            "political activism",
            "refuge from division",
            "apolitical",
            "unrelated to our mission while at work",
            "social or political",
            "don't engage in social",
        )
    ):
        return "mission_focus_apolitical"

    if any(
        w in t
        for w in (
            "judged by outcomes",
            "work will speak for itself",
            "uncompromising engineering",
            "championship team",
            "generous severance",
            "not a family",
            "stunning colleagues",
            "high expectations for performance",
            "faint of heart",
            "dream team",
        )
    ):
        return "performance_elite"

    if any(
        w in t
        for w in (
            "scholarship for women",
            "girl geek",
            "women in technology",
            "belonging",
            "whole self",
            "representation",
            "underrepresented",
            "commitment to diversity",
        )
    ) or (
        "inclusion" in t
        and any(w in t for w in ("diversity", "belonging", "equity"))
    ):
        return "affirming_dei"

    return "neutral"


def classify_stances(chunks: list[dict], model: str = CLASSIFIER_MODEL) -> dict[str, str]:
    """Classify chunks -> {chunk_id: stance}. Batched, temperature 0."""
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
            stance = item["stance"]
            if stance not in DEI_STANCES:
                stance = "neutral"
            results[item["id"]] = stance
        print(f"  classified {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}")

    return results


def agreement_report(predictions: dict[str, str], hand_labels: dict[str, str]) -> dict:
    """Compare stance output against hand labels."""
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
