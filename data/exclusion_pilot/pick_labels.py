"""Pick a VERBATIM quote fragment as each concept's display label.

The chart's material is language, so concepts are labeled with what companies
actually say, not HR-taxonomy nouns; the taxonomic name demotes to a
descriptor line. The judge must return a fragment copied verbatim from one of
the concept's central example sentences (<=8 words) — validated by substring
check, so every label is a real published sentence fragment. Falls back to no
quote (component shows the name) if validation fails.
Adds "quote": {t, co} to astro/src/data/stories/gender-concepts.json.
"""
import json
import re
import sys

sys.path.insert(0, "src")

from anthropic import Anthropic

from lowork.config import CLASSIFIER_MODEL

PATHS = ("astro/src/data/stories/gender-concepts.json",
         "data/exclusion_pilot/concept_viz.json")
doc = json.load(open(PATHS[0]))

SYSTEM = """You choose a display label for a concept found across several companies' careers pages. You get the concept's name and its most representative sentences (with company).

Return a fragment of 3-8 words COPIED EXACTLY, character for character, from ONE of the sentences — the fragment that best voices the shared idea in the companies' own words. Prefer a complete clause with a verb over a noun pile. Do not paraphrase, do not change case or punctuation inside the fragment, do not add quotes. Also return the company whose sentence you took it from."""

TOOL = {
    "name": "record_label",
    "input_schema": {
        "type": "object",
        "properties": {
            "fragment": {"type": "string"},
            "company": {"type": "string"},
        },
        "required": ["fragment", "company"],
    },
}

norm = lambda s: re.sub(r"\s+", " ", s).strip()

client = Anthropic()
for c in doc["concepts"]:
    resp = client.messages.create(
        model=CLASSIFIER_MODEL, max_tokens=200, temperature=0,
        system=SYSTEM, tools=[TOOL],
        tool_choice={"type": "tool", "name": "record_label"},
        messages=[{"role": "user", "content": json.dumps({
            "concept": c["name"],
            "sentences": [{"company": x["co"], "sentence": x["t"]} for x in c["examples"]],
        }, ensure_ascii=False)}],
    )
    j = next(b for b in resp.content if b.type == "tool_use").input
    frag = norm(j["fragment"])
    src = next((x for x in c["examples"] if frag.lower() in norm(x["t"]).lower()), None)
    if src is None or not 2 <= len(frag.split()) <= 9:
        print(f"  ! not verbatim / bad length, no quote: {c['name']} — got {frag!r}")
        continue
    c["quote"] = {"t": frag, "co": src["co"]}
    print(f"  {c['z']:+.2f}  “{frag}”  ({src['co']})  · {c['name']}")

for p in PATHS:
    json.dump(doc, open(p, "w"), ensure_ascii=False, indent=1)
print("labels written")
