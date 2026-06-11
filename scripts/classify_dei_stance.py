#!/usr/bin/env python
"""Classify mission/brand chunks by discrete DEI stance.

Writes data/<company>/dei_stances.json and optional agreement report.
Use --heuristic for offline bootstrap without API calls.
"""

from __future__ import annotations

import argparse
from collections import Counter

import pandas as pd

from lowork.config import company_dir
from lowork.dei import DEI_REGISTERS
from lowork.dei_stance import DEI_STANCES, agreement_report, classify_stances, heuristic_stance
from lowork.io import load_all_chunks, read_json, write_json

ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}

REGISTER_TO_STANCE_HINT = {
    "explicit_demographic": "affirming_dei",
    "structural_process": "affirming_dei",
    "aspirational_vague": "affirming_dei",
    "belonging_culture": "affirming_dei",
    "meritocracy": "mission_focus_apolitical",
    "civilizational_mission": "civilizational_mission",
    "absent": "neutral",
}


def main(company: str, *, heuristic: bool, validate_only: bool, reclassify_all: bool) -> None:
    cdir = company_dir(company)
    chunks = load_all_chunks(cdir / "chunks")
    classifications_path = cdir / "classifications.json"
    if classifications_path.exists():
        classifications = read_json(classifications_path)
        chunks = [c for c in chunks if classifications.get(c["chunk_id"]) in ANALYSIS_LABELS]
    else:
        chunks = [c for c in chunks if c.get("label") in ANALYSIS_LABELS]
    if not chunks:
        raise SystemExit(f"No mission/benefits chunks for {company}")

    registers = read_json(cdir / "dei_registers.json") if (cdir / "dei_registers.json").exists() else {}

    if validate_only:
        # Cross-validate against register labels as proxy
        preds = read_json(cdir / "dei_stances.json") if (cdir / "dei_stances.json").exists() else {}
        if not preds:
            raise SystemExit("No dei_stances.json — run classification first")
        hints = {cid: REGISTER_TO_STANCE_HINT.get(reg, "neutral") for cid, reg in registers.items()}
        common = [cid for cid in hints if cid in preds]
        agree = sum(1 for cid in common if preds[cid] == hints[cid])
        print(f"Register→stance agreement: {agree}/{len(common)} = {agree/len(common):.1%}")
        disagreements = [
            {"chunk_id": cid, "register": registers[cid], "stance": preds[cid], "hint": hints[cid]}
            for cid in common
            if preds[cid] != hints[cid]
        ][:20]
        write_json(cdir / "dei_stance_agreement.json", {
            "n": len(common),
            "agreement": round(agree / len(common), 3) if common else None,
            "disagreements": disagreements,
        })
        return

    stances_path = cdir / "dei_stances.json"
    if not reclassify_all and stances_path.exists():
        existing = read_json(stances_path)
        new_chunks = [c for c in chunks if c["chunk_id"] not in existing]
        print(f"Incremental: {len(new_chunks)} new, {len(existing)} already classified")
        if new_chunks:
            if heuristic:
                new_stances = {c["chunk_id"]: heuristic_stance(c["text"]) for c in new_chunks}
            else:
                new_stances = classify_stances(new_chunks)
            stances = {**existing, **new_stances}
        else:
            stances = existing
    else:
        if heuristic:
            stances = {c["chunk_id"]: heuristic_stance(c["text"]) for c in chunks}
        else:
            stances = classify_stances(chunks)

    write_json(cdir / "dei_stances.json", stances)

    by_year: dict[str, Counter] = {}
    for c in chunks:
        y = str(c["year"])
        s = stances.get(c["chunk_id"], "neutral")
        by_year.setdefault(y, Counter())[s] += 1

    lines = ["# DEI stance by year", ""]
    for year in sorted(by_year, key=int):
        lines.append(f"## {year}")
        for stance in DEI_STANCES:
            n = by_year[year].get(stance, 0)
            if n:
                lines.append(f"- {stance}: {n}")
        lines.append("")

    (cdir / "dei_stance_review.md").write_text("\n".join(lines))
    print(f"Wrote {cdir / 'dei_stances.json'} ({len(stances)} chunks)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("--heuristic", action="store_true", help="Keyword fallback, no API")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--reclassify-all",
        action="store_true",
        help="Ignore existing dei_stances.json and classify every analysis chunk",
    )
    args = parser.parse_args()
    main(
        args.company,
        heuristic=args.heuristic,
        validate_only=args.validate_only,
        reclassify_all=args.reclassify_all,
    )
