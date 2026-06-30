#!/usr/bin/env python
"""Track when Netflix's performance-culture *concepts* appear across companies.

Concept-level (semantic) matching, not exact phrase: each concept has anchor
sentences (canonical + paraphrases) which we embed; a company's culture sentence
"expresses" the concept when its max cosine similarity to the anchors clears a
tuned threshold. A verbatim regex runs alongside as a high-confidence overlay
(concept-echo vs. verbatim-lift). The 2009 Netflix Culture deck is seeded as the
origin point so Netflix shows as 2009.

Writes data/culture_propagation.json (the adoption timeline) and
data/culture_propagation_review.md (top matches per concept for threshold tuning /
hand validation — inspect before trusting the timeline).
"""

from __future__ import annotations

import argparse
import re

import numpy as np
import pandas as pd

from lowork.company import CompanyProfile
from lowork.config import ROOT, company_dir, load_companies
from lowork.embeddings import EmbeddingStore
from lowork.io import write_json
from lowork.sentences import split_sentences

# Netflix is the origin; the rest (the rest of the universe) are potential
# adopters. The universe and display names come from pipeline.yaml / each
# company's profile — no company is hardcoded here.
COMPANIES = load_companies()
if "netflix" in COMPANIES:  # ensure the origin sorts first
    COMPANIES = ["netflix"] + [c for c in COMPANIES if c != "netflix"]


def _display(company: str) -> str:
    return CompanyProfile.load(company).display_name

CONCEPTS: dict[str, dict] = {
    "talent_density": {
        "label": "Talent density",
        "anchors": [
            "We deliberately keep a dense team of only the highest performers.",
            "Our edge is talent density — a high concentration of star performers.",
            "We concentrate top talent and keep the bar extremely high.",
        ],
        "regex": re.compile(r"talent density|density of talent|concentration of (?:top )?talent", re.I),
    },
    "keeper_test": {
        "label": "Keeper test",
        "anchors": [
            "If this person told us they were leaving for a similar job, would we fight to keep them?",
            "We apply the keeper test: managers keep only the people they would fight to retain.",
        ],
        "regex": re.compile(r"keeper test|fight (?:hard )?to keep", re.I),
    },
    "team_not_family": {
        "label": "Team, not a family",
        "anchors": [
            "We are a high-performance team, not a family.",
            "We are like a professional sports team, not a recreational team.",
        ],
        "regex": re.compile(r"not a family|sports team|pro(?:fessional)? team, not", re.I),
    },
    "dream_team": {
        "label": "Dream team / stunning colleagues",
        "anchors": [
            "We build a dream team of exceptional, stunning colleagues.",
            "Your reward is working alongside stunningly talented teammates.",
        ],
        "regex": re.compile(r"dream team|stunning colleagues|stunningly (?:talented|capable)", re.I),
    },
    "high_performer_supremacy": {
        "label": "High performer ≫ average",
        "anchors": [
            "A star performer is many times more valuable than an average employee.",
            "One exceptional employee outperforms several adequate ones.",
        ],
        # bare "10x" was too loose (matched "10x return", "10x learning
        # environment"); require it to qualify a person to count as supremacy.
        "regex": re.compile(r"many times more|times more (?:effective|valuable|productive)|10x\s+(?:engineer|performer|employee|developer|talent)", re.I),
    },
    "adequate_severance": {
        "label": "Adequate → severance",
        "anchors": [
            "Merely adequate performance earns a generous severance package.",
            "If your work is only solid, we part ways with a generous severance.",
        ],
        "regex": re.compile(r"generous severance|adequate performance", re.I),
    },
    "raise_the_bar": {
        "label": "Raise the bar",
        "anchors": [
            "We hold relentlessly high standards and keep raising the bar.",
            "Every new hire must raise the average and lift the whole team's bar.",
        ],
        "regex": re.compile(r"raise[sd]? the bar|relentlessly high|high(?:er)? bar|unreasonably high", re.I),
    },
    "judged_by_outcomes": {
        "label": "Judged by outcomes/results",
        "anchors": [
            "You are judged by your results and outcomes, not your effort or hours.",
            "We measure people by impact and results, not activity.",
        ],
        "regex": re.compile(r"judged by (?:outcomes|results)|results?-driven|measured by (?:impact|results)", re.I),
    },
    "only_the_best": {
        "label": "Only the best / A-players",
        "anchors": [
            "We hire only the best and the brightest — A-players, top talent.",
            "We recruit only elite, top-tier people and accept nothing less.",
        ],
        "regex": re.compile(r"best and (?:the )?brightest|A[\s-]?players?|top talent|only the best", re.I),
    },
    "freedom_responsibility": {
        "label": "Freedom & responsibility / no rules",
        "anchors": [
            "We don't have rules; we rely on people's good judgment.",
            "We run on freedom and responsibility, not rules and process.",
            "We have values, not rules — we trust people to act in the company's interest.",
        ],
        "regex": re.compile(r"freedom and responsibility|don'?t have rules|values,? not rules|no rules,? (?:just|but|we|only)", re.I),
    },
    "context_not_control": {
        "label": "Context, not control",
        "anchors": [
            "Leaders lead with context, not control.",
            "Managers set context and let teams make the decisions rather than controlling them.",
        ],
        "regex": re.compile(r"context,? not control|lead(?:ing)? with context", re.I),
    },
    "aligned_loosely_coupled": {
        "label": "Highly aligned, loosely coupled",
        "anchors": [
            "We stay highly aligned and loosely coupled.",
            "Teams are loosely coupled but highly aligned on strategy and goals.",
        ],
        "regex": re.compile(r"highly aligned|loosely coupled", re.I),
    },
    "no_vacation_policy": {
        "label": "No vacation policy / unlimited time off",
        "anchors": [
            "We have no vacation policy; take time off as you see fit.",
            "There is no formal vacation tracking — take the time you need.",
        ],
        "regex": re.compile(r"no vacation policy|unlimited (?:vacation|pto|time off|paid time)", re.I),
    },
}


def _norm(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)


def company_sentences(company: str) -> list[tuple[int, str]]:
    path = company_dir(company) / "embeddings.parquet"
    if not path.exists():
        return []
    df = pd.read_parquet(path)
    mb = df[df["label"] == "mission_brand"]
    rows: list[tuple[int, str]] = []
    for _, r in mb.iterrows():
        for s in split_sentences(r["text"]):
            if len(s.split()) >= 5:
                rows.append((int(r["year"]), s))
    if company == "netflix":  # seed the 2009 deck as the origin
        deck = company_dir("netflix") / "canon" / "culture_deck_2009.md"
        if deck.exists():
            for line in deck.read_text().splitlines():
                line = re.sub(r"\s*\d+\s*$", "", line).strip()
                for s in split_sentences(line):
                    if len(s.split()) >= 5:
                        rows.append((2009, s))
    # dedup identical (year, text)
    seen, out = set(), []
    for y, s in rows:
        if (y, s) not in seen:
            seen.add((y, s))
            out.append((y, s))
    return out


def main(threshold: float, review_top: int, companies: list[str] | None = None) -> None:
    global COMPANIES
    if companies is not None:
        COMPANIES = list(companies)
    store = EmbeddingStore()
    concept_vecs = {n: _norm(np.stack(store.embed(c["anchors"]))) for n, c in CONCEPTS.items()}

    timeline: dict[str, dict] = {n: {} for n in CONCEPTS}
    review_rows: list[tuple] = []

    for company in COMPANIES:
        sents = company_sentences(company)
        if not sents:
            print(f"  {company}: no sentences")
            continue
        years = [y for y, _ in sents]
        texts = [s for _, s in sents]
        E = _norm(np.stack(store.embed(texts)))
        for name, c in CONCEPTS.items():
            sims = (E @ concept_vecs[name].T).max(axis=1)
            matched = [(years[i], texts[i], float(sims[i])) for i in range(len(texts)) if sims[i] >= threshold]
            verb = [(years[i], texts[i]) for i in range(len(texts)) if c["regex"].search(texts[i])]
            entry: dict = {}
            if matched:
                best = max(matched, key=lambda x: x[2])
                entry.update(
                    firstYearConcept=min(y for y, _, _ in matched),
                    nConcept=len(matched),
                    yearsConcept=sorted({y for y, _, _ in matched}),
                    example=best[1][:180],
                    exampleScore=round(best[2], 3),
                )
            if verb:
                entry.update(firstYearVerbatim=min(y for y, _ in verb), nVerbatim=len(verb))
            if entry:
                timeline[name][company] = entry
            # review: top matches for threshold tuning (regardless of cutoff)
            for i in np.argsort(-sims)[:review_top]:
                review_rows.append((name, company, years[i], round(float(sims[i]), 3), texts[i][:120]))

    display_names = {c: _display(c) for c in COMPANIES}
    write_json(ROOT / "data" / "culture_propagation.json",
               {"threshold": threshold, "origin": "netflix",
                "concepts": {n: CONCEPTS[n]["label"] for n in CONCEPTS},
                "displayNames": display_names, "timeline": timeline})

    # review file: sorted by score within concept, for hand validation
    lines = [f"# Culture-propagation match review (threshold={threshold})", "",
             "Top matches per concept across companies, by cosine similarity. Use this to",
             "tune the threshold: matches above it should genuinely express the concept.", ""]
    for name in CONCEPTS:
        lines.append(f"## {CONCEPTS[name]['label']}")
        rows = sorted([r for r in review_rows if r[0] == name], key=lambda r: -r[3])[:12]
        for _, comp, yr, sc, txt in rows:
            mark = "✓" if sc >= threshold else " "
            lines.append(f"- [{mark}] {sc:.3f} {display_names.get(comp, comp):9s} {yr}  {txt}")
        lines.append("")
    (ROOT / "data" / "culture_propagation_review.md").write_text("\n".join(lines))

    # quick origin-check print
    print(f"threshold={threshold}")
    for name in CONCEPTS:
        adopters = sorted(
            ((e.get("firstYearConcept"), display_names.get(c, c)) for c, e in timeline[name].items()
             if e.get("firstYearConcept")),
        )
        if adopters:
            print(f"  {CONCEPTS[name]['label']:26s} " +
                  " ".join(f"{co}:{yr}" for yr, co in adopters))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--threshold", type=float, default=0.62)  # hand-validated
    p.add_argument("--review-top", type=int, default=3)
    main(p.parse_args().threshold, p.parse_args().review_top)
