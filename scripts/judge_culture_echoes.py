#!/usr/bin/env python
"""LLM judge pass over the propagation tracker's matches (echoes AND lifts).

Embedding similarity finds candidates; it cannot tell a genuine conceptual echo
from overlapping vocabulary ("values align with your own" is culture-fit talk,
not the deck's "values are shown by who gets rewarded"). This step judges every
match in data/culture_propagation.json against its concept's definition:

  genuine   the sentence makes the same specific claim about how the company
            runs its work/performance culture as the Netflix concept
  adjacent  related territory — a softened, partial, or implicit version of
            the idea (the honest reading of most of the echo band)
  spurious  shared vocabulary but a different or opposite meaning, a generic
            HR pleasantry, or about products/customers rather than the
            employment culture

Writes data/culture_echo_judgments.json (keyed by concept|company|year|text-hash,
so judgments survive tracker re-runs and only NEW sentences get judged) and
data/culture_echo_review.md (spurious first — Becca's spot-check surface).
export_netflix_story.py drops judged-spurious echoes and flags any disputed
lift loudly; unjudged matches pass through (the export warns about them).

Model: pinned CLASSIFIER_MODEL (Haiku), temperature 0, forced tool-use
structured output (see synthesize-company JSON-bug lesson).
"""

from __future__ import annotations

import argparse
import hashlib
import json

from anthropic import Anthropic

from lowork.config import CLASSIFIER_MODEL, ROOT
from lowork.io import read_json, write_json
from lowork.netflix_concepts import CONCEPTS, match_key

JUDGMENTS_PATH = ROOT / "data" / "culture_echo_judgments.json"
REVIEW_PATH = ROOT / "data" / "culture_echo_review.md"

VERDICTS = ("genuine", "adjacent", "spurious")

SYSTEM = """You judge whether a company's careers-page sentence genuinely expresses a specific concept from Netflix's 2009 culture deck, or merely shares vocabulary with it.

You are given the concept (its label, Netflix's own phrasing, and paraphrase anchors) and candidate sentences from other companies. For each sentence return one verdict:

- "genuine": the sentence makes the SAME specific claim about how the company runs its work/performance culture. The idea matches, not just the words.
- "adjacent": related territory — a softened, partial, or implicit version of the concept. The sentence gestures at the idea without committing to it.
- "spurious": the similarity is superficial — shared vocabulary with a different or opposite meaning, a generic HR pleasantry any company could write, or a sentence about products/customers/business strategy rather than the employment culture.

Judge the idea, not the vocabulary. A sentence can be genuine with none of the concept's words, and spurious while quoting half of them. Be strict: when in doubt between adjacent and spurious, ask whether a careful reader would recognize the Netflix idea in it — if not, it is spurious."""

TOOL = {
    "name": "record_verdicts",
    "description": "Record one verdict per candidate sentence.",
    "input_schema": {
        "type": "object",
        "properties": {
            "verdicts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "verdict": {"type": "string", "enum": list(VERDICTS)},
                        "reason": {"type": "string", "description": "one short sentence"},
                    },
                    "required": ["id", "verdict", "reason"],
                },
            }
        },
        "required": ["verdicts"],
    },
}


def collect_matches() -> list[dict]:
    """Every echo and every lift example in the tracker output, flattened."""
    prop = read_json(ROOT / "data" / "culture_propagation.json")
    out = []
    for cid, companies in prop["timeline"].items():
        if cid not in CONCEPTS:
            continue
        for co, e in companies.items():
            if co == "netflix":
                continue
            for ec in e.get("echoes", []):
                out.append({"key": match_key(cid, co, ec["year"], ec["text"]),
                            "cid": cid, "company": co, "year": ec["year"],
                            "kind": "echo", "score": ec["score"], "text": ec["text"]})
            if e.get("nConcept"):
                out.append({"key": match_key(cid, co, e["firstYearConcept"], e["example"]),
                            "cid": cid, "company": co, "year": e["firstYearConcept"],
                            "kind": "lift", "score": e.get("exampleScore"),
                            "text": e["example"]})
    return out


def judge(matches: list[dict], judgments: dict, client: Anthropic) -> None:
    todo = [m for m in matches if m["key"] not in judgments]
    if not todo:
        print("  nothing new to judge")
        return
    by_cid: dict[str, list[dict]] = {}
    for m in todo:
        by_cid.setdefault(m["cid"], []).append(m)
    for cid, ms in by_cid.items():
        c = CONCEPTS[cid]
        concept_block = {
            "concept": c["label"],
            "netflix_original": c["deck_quote"] or c["anchors"][0],
            "paraphrase_anchors": c["anchors"],
        }
        payload = [{"id": m["key"], "company": m["company"], "sentence": m["text"]} for m in ms]
        resp = client.messages.create(
            model=CLASSIFIER_MODEL,
            max_tokens=4000,
            temperature=0,
            system=SYSTEM,
            tools=[TOOL],
            tool_choice={"type": "tool", "name": "record_verdicts"},
            messages=[{"role": "user", "content": json.dumps(
                {"concept": concept_block, "candidates": payload}, ensure_ascii=False)}],
        )
        block = next(b for b in resp.content if b.type == "tool_use")
        got = {v["id"]: v for v in block.input["verdicts"]}
        for m in ms:
            v = got.get(m["key"])
            if v is None or v["verdict"] not in VERDICTS:
                print(f"  ! no/invalid verdict for {m['key']} — left unjudged")
                continue
            judgments[m["key"]] = {"verdict": v["verdict"], "reason": v["reason"],
                                   "concept": cid, "company": m["company"],
                                   "year": m["year"], "kind": m["kind"],
                                   "score": m["score"], "text": m["text"]}
        print(f"  {cid}: judged {len(ms)}")


def write_review(judgments: dict) -> None:
    rows = sorted(judgments.values(),
                  key=lambda j: ({"spurious": 0, "adjacent": 1, "genuine": 2}[j["verdict"]],
                                 j["concept"], -(j["score"] or 0)))
    counts: dict[str, int] = {}
    for j in judgments.values():
        counts[j["verdict"]] = counts.get(j["verdict"], 0) + 1
    lines = [
        "# Echo/lift judge review",
        "",
        f"Model {CLASSIFIER_MODEL}, temperature 0. {len(judgments)} matches: "
        + ", ".join(f"{v} {counts.get(v, 0)}" for v in VERDICTS) + ".",
        "Spot-check the spurious block (dropped from the story export) and any",
        "disputed lift before trusting the charts. Re-runs only judge new sentences;",
        "delete a key from culture_echo_judgments.json to re-judge it.",
        "",
    ]
    for j in rows:
        flag = " **⚠ LIFT**" if j["kind"] == "lift" and j["verdict"] == "spurious" else ""
        lines.append(f"- `{j['verdict']}`{flag} [{j['concept']}] {j['company']} {j['year']} "
                     f"({j['kind']} {j['score']}): “{j['text'][:140]}” — {j['reason']}")
    REVIEW_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REVIEW_PATH}")


def main() -> None:
    matches = collect_matches()
    judgments = read_json(JUDGMENTS_PATH) if JUDGMENTS_PATH.exists() else {}
    # prune judgments for matches that no longer exist (concept removed, corpus changed)
    live = {m["key"] for m in matches}
    judgments = {k: v for k, v in judgments.items() if k in live}
    print(f"{len(matches)} matches ({sum(1 for m in matches if m['kind'] == 'echo')} echoes, "
          f"{sum(1 for m in matches if m['kind'] == 'lift')} lifts); "
          f"{len(matches) - len(judgments)} unjudged")
    judge(matches, judgments, Anthropic())
    write_json(JUDGMENTS_PATH, judgments)
    write_review(judgments)
    counts: dict[str, int] = {}
    for j in judgments.values():
        counts[j["verdict"]] = counts.get(j["verdict"], 0) + 1
    print("verdicts:", counts)


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    main()
