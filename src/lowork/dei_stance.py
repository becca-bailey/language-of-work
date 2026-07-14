"""Discrete DEI stance classification for mission/brand chunks."""

from __future__ import annotations

import json
import re

from anthropic import Anthropic

from .config import CLASSIFIER_MODEL

# Offline-bootstrap keyword net for the civilizational stance. Known weakness:
# these are largely Palantir catchphrases, so the heuristic under-detects other
# companies' civilizational framing — production classification is the LLM below;
# this regex exists only for --heuristic bootstrap runs.
CIVILIZATIONAL_PATTERN = re.compile(
    r"\b(?:"
    r"future of the west|the west'?s most important|western (?:tech )?institutions|"
    r"warfighters?|battlefield|build with consequence|tinker at the margins|"
    r"technological republic|most important institutions|"
    r"empower the world'?s most important institutions"
    r")\b",
    re.I,
)


def is_civilizational_mission(text: str) -> bool:
    return bool(CIVILIZATIONAL_PATTERN.search(text))

DEI_STANCES = [
    "affirming_dei",
    "neutral",
    "mission_focus_apolitical",
    "performance_elite",
    "civilizational_mission",
]

# Counter-programming stances: positions opposite to workforce-DEI employer branding.
# This is the stance-axis successor to the retired COUNTER_DEI_REGISTERS — opposition is
# a stance, not a register. performance_elite is deliberately excluded (evaluation
# intensity, not a position on DEI).
COUNTER_DEI_STANCES = ["mission_focus_apolitical", "civilizational_mission"]

SYSTEM_PROMPT = """You classify text chunks from archived company careers pages by DEI stance.

These chunks come from careers/mission pages. Classify the company's STANCE on workplace inclusion and DEI — not product mission or customer demographics.

Assign exactly one stance to each chunk:

- affirming_dei: the company actively affirms DEI as an employer — belonging CTAs, diversity commitments, representation goals, inclusion programs, "bring your whole self" framing with company accountability. Must be about the company's OWN workforce or workplace.
- neutral: mission, innovation, recruiting, or benefits copy with no discernible stance on workplace DEI — standard product impact, generic engineering culture. ALSO includes CSR / philanthropy / community content (foundation grants, volunteering, youth or education programs, supplier and producer sustainability) — "underserved," "diverse backgrounds," or named groups describing program BENEFICIARIES or the community are not a workplace-DEI stance.
- mission_focus_apolitical: explicitly refuses workplace social/political activism unrelated to mission; apolitical company framing; "refuge from division"; keeps causes out of the workplace.
- performance_elite: high-performance / outcomes-based bar — judged by outcomes, uncompromising engineering standards, stunning colleagues, generous severance, not a family. About evaluation intensity, not geopolitics.
- civilizational_mission: employer identity framed around civilizational or geopolitical mission — "future of the West," Western institutions, battlefield/consequence, serving the West's most important institutions. Counter-programming to DEI-era employer branding without necessarily naming DEI.

Tie-breakers:
1. If a chunk mixes stances, choose the DOMINANT one.
2. Palantir "future of the West" / "West's most important institutions" → civilizational_mission.
3. Coinbase "refuge from division" → mission_focus_apolitical.
4. Netflix "sports team not family" → performance_elite.
5. 2013 women-in-tech scholarships / Girl Geek spotlights → affirming_dei (workforce pipeline programs count).
6. CSR / philanthropy about the community, customers, or supply chain — even when it names demographic groups — → neutral. "Our Foundation funds programs for underserved youth of diverse ethnic and racial backgrounds" is philanthropy, not a workplace-DEI stance.
7. Generic diversity-of-thought recruiting copy ("talented people from diverse backgrounds approach problems from varying perspectives") with no commitment or program → neutral, not affirming_dei.

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


