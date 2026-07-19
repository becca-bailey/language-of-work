"""Discrete DEI stance classification for mission/brand chunks."""

from __future__ import annotations

import json
import re

from anthropic import Anthropic

from .config import CLASSIFIER_MODEL

# Offline-bootstrap keyword net for the civilizational stance (narrowed 2026-07-18:
# explicit West/civilization invocations only — deterrence/battlefield/"important
# institutions" copy is deliberately NOT matched). Production classification is the
# LLM below; this regex exists only for --heuristic bootstrap runs.
CIVILIZATIONAL_PATTERN = re.compile(
    r"\b(?:"
    r"future of the west|the west'?s most important|western (?:tech )?institutions|"
    r"western civili[sz]ation|western values|civili[sz]ational|"
    r"technological republic"
    r")\b",
    re.I,
)


def is_civilizational_mission(text: str) -> bool:
    return bool(CIVILIZATIONAL_PATTERN.search(text))

DEI_STANCES = [
    "affirming_dei",
    "neutral",
    "mission_focus_apolitical",
    "civilizational_mission",
]

# Counter-programming stances: positions opposite to workforce-DEI employer branding.
# This is the stance-axis successor to the retired COUNTER_DEI_REGISTERS — opposition is
# a stance, not a register.
#
# performance_elite was REMOVED 2026-07-18 (Becca's ruling): performance-intensity
# language is not a position on DEI (it is measured in the performance study) and her
# hand labels gave the class zero support — it now classifies as neutral, with an
# explicit prompt guard so it doesn't leak into mission_focus_apolitical. The exception
# is an EXPLICIT merit-vs-DEI contrast ("we hire on merit, not identity politics",
# "no diversity quotas"), which IS a position and belongs in mission_focus_apolitical.
#
# civilizational_mission was NARROWED the same day: explicit invocations of the West /
# Western civilization only. Generic defense/consequence copy (deterrence, battlefield,
# "world's most important institutions") is neutral — worth studying, but not as DEI
# counter-programming.
COUNTER_DEI_STANCES = ["mission_focus_apolitical", "civilizational_mission"]

SYSTEM_PROMPT = """You classify text chunks from archived company careers pages by DEI stance.

These chunks come from careers/mission pages. Classify the company's STANCE on workplace inclusion and DEI — not product mission or customer demographics.

Assign exactly one stance to each chunk:

- affirming_dei: the company actively affirms DEI as an employer — belonging CTAs, diversity commitments, representation goals, inclusion programs, "bring your whole self" framing with company accountability. Must be about the company's OWN workforce or workplace.
- neutral: mission, innovation, recruiting, or benefits copy with no discernible stance on workplace DEI — standard product impact, generic engineering culture. ALSO includes CSR / philanthropy / community content (foundation grants, volunteering, youth or education programs, supplier and producer sustainability) — "underserved," "diverse backgrounds," or named groups describing program BENEFICIARIES or the community are not a workplace-DEI stance.
- mission_focus_apolitical: explicitly refuses workplace social/political activism unrelated to mission; apolitical company framing; "refuge from division"; keeps causes out of the workplace. ALSO includes explicit identity-blind rejection of DEI practice — "we hire on merit, not identity politics", "no diversity quotas or identity-based hiring targets", announcing the wind-down of DEI programs or representation goals. The distinguishing feature is an explicit refusal aimed at DEI/identity/causes, not mere intensity.
- civilizational_mission: employer identity framed around defending or ensuring the future of "the West" / Western civilization — an EXPLICIT civilizational invocation is required. Markers (any company's phrasing counts, not just the famous examples): "the West", "Western civilization", "Western values", "Western institutions", "civilizational" stakes, defense-of-civilization or civilizational-destiny framing, decline-and-renewal rhetoric explicitly about the West or civilization. Counter-programming to DEI-era employer branding without necessarily naming DEI.

Tie-breakers:
1. If a chunk mixes stances, choose the DOMINANT one.
2. civilizational_mission requires the explicit invocation. Generic defense/consequence copy — deterrence, battlefield, warfighters, "the world's most important institutions", national-security product language, US-and-allies framing — WITHOUT a civilizational invocation → neutral.
3. "Refuge from division" / no-politics-at-work framing → mission_focus_apolitical.
4. High-performance-culture language — dream team, keeper test, "not a family", stunning colleagues, uncompromisingly high bar, generous severance — is evaluation intensity, NOT a DEI stance → neutral. But performance language WITH an explicit merit-vs-identity contrast ("merit, not identity politics", "no diversity quotas") → mission_focus_apolitical — the explicit refusal outranks the intensity framing.
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
            # explicit identity-blind rejection of DEI practice (matches the
            # SYSTEM_PROMPT rule: refusal aimed at DEI/identity, not intensity)
            "not identity politics",
            "merit, not",
            "no diversity quotas",
            "identity-based",
        )
    ):
        return "mission_focus_apolitical"

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


