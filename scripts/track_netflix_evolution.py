#!/usr/bin/env python
"""Track Netflix's OWN performance-culture language over time (intra-Netflix evolution).

The headline: Netflix carried "adequate performance -> a generous severance" every year
2009-2022, then dropped it in its ~2023 culture rewrite (2024-2026 keep only keeper-test /
dream-team / "high performer") -- the same formula Coinbase lifted verbatim in 2024.
Netflix invented it, softened it; only the disciple kept the faith.

Verbatim regex (Netflix's own wording, not paraphrase) over the 2009 deck + the
jobs.netflix.com/culture chunks 2017-2026. Writes data/netflix_evolution.json.
"""

from __future__ import annotations

import glob
import json
import re

from lowork.config import ROOT, company_dir
from lowork.io import write_json

# Reuse the concept verbatim regexes (single source of truth).
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from track_culture_propagation import CONCEPTS  # noqa: E402


def netflix_text_by_year() -> dict[int, str]:
    out: dict[int, str] = {}
    deck = company_dir("netflix") / "canon" / "culture_deck_2009.md"
    if deck.exists():
        out[2009] = deck.read_text()
    for f in sorted(glob.glob(str(company_dir("netflix") / "chunks" / "*.jsonl"))):
        yr = int(f.split("/")[-1].split(".")[0])
        text = []
        for line in open(f):
            try:
                text.append(re.sub(r"<[^>]+>", " ", json.loads(line).get("text", "")))
            except Exception:
                pass
        if text:
            out[yr] = out.get(yr, "") + " " + " ".join(text)
    return out


def first_match(rx: re.Pattern, text: str) -> str | None:
    m = rx.search(text)
    if not m:
        return None
    i = m.start()
    return re.sub(r"\s+", " ", text[max(0, i - 30): i + 90]).strip()


def main() -> None:
    by_year = netflix_text_by_year()
    years = sorted(by_year)
    concepts = {}
    for cid, c in CONCEPTS.items():
        rx = c["regex"]
        per_year = {}
        for y in years:
            ex = first_match(rx, by_year[y])
            per_year[str(y)] = {"present": ex is not None, "example": ex or ""}
        present_years = [y for y in years if per_year[str(y)]["present"]]
        concepts[cid] = {
            "label": c["label"],
            "firstYear": min(present_years) if present_years else None,
            "lastYear": max(present_years) if present_years else None,
            "byYear": per_year,
        }
    write_json(ROOT / "data" / "netflix_evolution.json",
               {"years": years, "concepts": concepts})

    # console summary (the softening should be visible)
    print(f"years: {years}")
    for cid, e in concepts.items():
        row = "".join("█" if e["byYear"][str(y)]["present"] else "·" for y in years)
        span = f"{e['firstYear']}–{e['lastYear']}" if e["firstYear"] else "absent"
        print(f"  {e['label']:26s} {row}  {span}")
    print("  (columns = " + " ".join(str(y)[2:] for y in years) + ")")


if __name__ == "__main__":
    main()
