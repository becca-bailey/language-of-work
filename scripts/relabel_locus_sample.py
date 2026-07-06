#!/usr/bin/env python
"""Relabel the hand-coded review items under the FROZEN codebook, for the α verify.

The held-out model labels were generated during extraction across progressively-updated
prompts, so they don't reflect the frozen codebook. To isolate locus-codebook reliability
from extraction recall, this relabels exactly the items in wellbeing_locus_review.csv
(fixed item set) using the same codebook rules (imported from benefits_extract), then
writes model labels aligned to the hand sheet by id.

Reads  data/wellbeing_locus_review.csv (the coded sheet)
Writes data/wellbeing_locus_review_model.csv (id, model_locus, model_specificity)
"""

from __future__ import annotations

import csv
import json

from anthropic import Anthropic

from lowork.benefits_extract import CATEGORIES, LOCI, SPECIFICITIES, SYSTEM_PROMPT
from lowork.config import DATA_DIR, JUDGE_MODEL

# Reuse the exact codebook rules from the extractor prompt, but reframe the task as
# "label these given items" instead of "extract items from chunks".
RELABEL_SYSTEM = (
    SYSTEM_PROMPT.split("You are given a batch")[0]
    + "You are given a list of already-extracted benefit items (category + verbatim). "
    "Assign locus and specificity to EACH item using the rules below. Do not add, drop, "
    "or merge items; label every item exactly once, in input order.\n\n"
    + SYSTEM_PROMPT.split("locus — ", 1)[1].split("Call the record_benefits", 1)[0]
)

TOOL = {
    "name": "label_items",
    "description": "Assign locus and specificity to every given item, in input order.",
    "input_schema": {
        "type": "object",
        "properties": {
            "labels": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "locus": {"type": "string", "enum": LOCI + ["exclude"]},
                        "specificity": {"type": "string", "enum": SPECIFICITIES},
                    },
                    "required": ["id", "locus", "specificity"],
                },
            }
        },
        "required": ["labels"],
    },
}
BATCH = 20


def main() -> int:
    src = list(csv.DictReader((DATA_DIR / "wellbeing_locus_review.csv").open()))
    client = Anthropic()
    out: dict[str, dict] = {}

    for i in range(0, len(src), BATCH):
        batch = src[i : i + BATCH]
        payload = [{"id": r["id"], "category": r["category"], "verbatim": r["verbatim"]}
                   for r in batch]
        resp = client.messages.create(
            model=JUDGE_MODEL, max_tokens=3000, temperature=0,
            system=RELABEL_SYSTEM
            + "\n\nAn item that is NOT a well-being benefit (compensation, equity, "
              "insurance, retirement) gets locus 'exclude'. Call the label_items tool once.",
            tools=[TOOL], tool_choice={"type": "tool", "name": "label_items"},
            messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        )
        block = next((b for b in resp.content if b.type == "tool_use"), None)
        for lab in (block.input.get("labels", []) if block else []):
            out[lab["id"]] = lab
        print(f"  labeled {min(i + BATCH, len(src))}/{len(src)}")

    with open(DATA_DIR / "wellbeing_locus_review_model.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "model_locus", "model_specificity"])
        for r in src:
            m = out.get(r["id"], {})
            w.writerow([r["id"], m.get("locus", ""), m.get("specificity", "")])
    print(f"wrote model labels for {len(out)}/{len(src)} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
