#!/usr/bin/env python
"""Track when Netflix's performance-culture *concepts* appear across companies.

Concept-level (semantic) matching, not exact phrase: each concept has anchor
sentences (canonical + paraphrases) which we embed; a company's culture sentence
"expresses" the concept when its max cosine similarity to the anchors clears a
tuned threshold. A borrowing that also clears a higher "near-verbatim" band is
flagged as a high-confidence lift (vs. a paraphrase between the two bars) — this
is purely similarity-based, no phrase regex. The 2009 Netflix Culture deck is
seeded as the origin point so Netflix shows as 2009.

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

# The deck's publication year. Adopter sentences from before it are excluded
# from the lineage data — they can't be descent, only convergence.
ORIGIN_YEAR = 2009


def _display(company: str) -> str:
    return CompanyProfile.load(company).display_name

# Concept registry (labels + anchors) lives in src/lowork/netflix_concepts.py —
# the single source of truth shared with export_netflix_story.py. Edit concepts THERE.
from lowork.netflix_concepts import CONCEPTS  # noqa: E402


def _norm(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)


# Careers-page nav menus carry no punctuation, so the sentence splitter can't break them
# off and they glue onto the first real sentence ("Benefits Help How to Apply FAQ We make
# decisions…"). Strip a *leading run* of menu labels — but only when ≥2 of them chain,
# so a sentence that legitimately opens with "Help us…" or "Careers at…" is left alone.
_NAV_LABELS = (
    r"Benefits|Help|How to Apply|FAQ|Home|Careers?|Search|Menu|Log ?in|Sign ?in|Sign ?up|"
    r"Apply(?: Now)?|Jobs|Openings|About(?: Us)?|Contact(?: Us)?|Blog|Press|Newsroom|News|"
    r"Privacy|Terms|Cookies?|Locations?|Investors?|Overview|Students?|Programs?|Events?|Resources?"
)
_NAV_PREFIX = re.compile(rf"^(?:(?:{_NAV_LABELS})\b[\s|·•>\-–—/]*){{2,}}", re.I)


def strip_nav(s: str) -> str:
    m = _NAV_PREFIX.match(s)
    if not m:
        return s
    rest = s[m.end():].lstrip()
    # Only strip if a real sentence remains; otherwise the line was all nav — drop it.
    return rest if len(rest.split()) >= 5 else ""


def company_sentences(company: str) -> list[tuple[int, str]]:
    path = company_dir(company) / "embeddings.parquet"
    if not path.exists():
        return []
    df = pd.read_parquet(path)
    mb = df[df["label"] == "mission_brand"]
    rows: list[tuple[int, str]] = []
    for _, r in mb.iterrows():
        for s in split_sentences(r["text"]):
            s = strip_nav(s)
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


def main(threshold: float, echo_threshold: float, verbatim_threshold: float,
         review_top: int, companies: list[str] | None = None) -> None:
    global COMPANIES
    if companies is not None:
        COMPANIES = list(companies)
    store = EmbeddingStore()
    concept_vecs = {n: _norm(np.stack(store.embed(c["anchors"]))) for n, c in CONCEPTS.items()}
    concept_names = list(CONCEPTS)

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
        sims_by = {n: (E @ concept_vecs[n].T).max(axis=1) for n in CONCEPTS}
        for name in CONCEPTS:  # review: top matches per concept (regardless of cutoff)
            for i in np.argsort(-sims_by[name])[:review_top]:
                review_rows.append((name, company, years[i], round(float(sims_by[name][i]), 3), texts[i][:120]))

        if company == "netflix":
            # Origin detection stays per-concept: Netflix "expresses" a concept if any of
            # its sentences clears the bar. No dedup — the deck legitimately voices several
            # concepts in one breath, and no echo band.
            for name in CONCEPTS:
                sims = sims_by[name]
                matched = [(years[i], texts[i], float(sims[i])) for i in range(len(texts)) if sims[i] >= threshold]
                verb = [(y, t) for y, t, sc in matched if sc >= verbatim_threshold]
                entry: dict = {}
                if matched:
                    best = max(matched, key=lambda x: x[2])
                    entry.update(firstYearConcept=min(y for y, _, _ in matched), nConcept=len(matched),
                                 yearsConcept=sorted({y for y, _, _ in matched}),
                                 example=best[1][:180], exampleScore=round(best[2], 3))
                if verb:
                    entry.update(firstYearVerbatim=min(y for y, _ in verb), nVerbatim=len(verb))
                if entry:
                    timeline[name][company] = entry
            continue

        # Adopters: attribute each sentence to a SINGLE concept (its highest-similarity one)
        # so one line can't count as a borrowing under every concept it grazes. There it's a
        # lift (>= threshold) or an echo (>= echo_threshold): same framework, not necessarily
        # borrowed. A lift that also clears the near-verbatim bar (>= verbatim_threshold) is
        # flagged as a high-confidence, near-verbatim borrowing — purely on similarity.
        lifts: dict[str, list] = {n: [] for n in CONCEPTS}   # (i, score, verbatim)
        echoes: dict[str, list] = {n: [] for n in CONCEPTS}  # (i, score)
        for i in range(len(texts)):
            if years[i] < ORIGIN_YEAR:
                # A sentence that predates the deck can't be descent — that's
                # convergence by definition (e.g. Amazon's 2007 values line),
                # so it's excluded from the lineage data outright (2026-07-23).
                continue
            best_n = max(concept_names, key=lambda n: sims_by[n][i])
            sc = float(sims_by[best_n][i])
            if sc >= threshold:
                lifts[best_n].append((i, sc, sc >= verbatim_threshold))
            elif sc >= echo_threshold:
                echoes[best_n].append((i, sc))
        for name in CONCEPTS:
            entry = {}
            L = lifts[name]
            if L:
                bi, bs, _ = max(L, key=lambda x: x[1])
                entry.update(firstYearConcept=min(years[i] for i, _, _ in L), nConcept=len(L),
                             yearsConcept=sorted({years[i] for i, _, _ in L}),
                             example=texts[bi][:180], exampleScore=round(bs, 3))
                vb = [i for i, _, v in L if v]
                if vb:
                    entry.update(firstYearVerbatim=min(years[i] for i in vb), nVerbatim=len(vb))
            # Dedup echoes by text (the same line recurs across snapshot years), keeping
            # the earliest year it appeared and its best score.
            best_by_text: dict[str, tuple[int, float]] = {}
            for i, sc in echoes[name]:
                t = texts[i][:180]
                yr, prev = best_by_text.get(t, (years[i], -1.0))
                best_by_text[t] = (min(yr, years[i]), max(prev, sc))
            Eh = sorted(best_by_text.items(), key=lambda kv: -kv[1][1])
            if Eh:
                entry["echoes"] = [{"year": yr, "text": t, "score": round(sc, 3)}
                                   for t, (yr, sc) in Eh[:3]]
            if entry:
                timeline[name][company] = entry

    display_names = {c: _display(c) for c in COMPANIES}
    write_json(ROOT / "data" / "culture_propagation.json",
               {"threshold": threshold, "echoThreshold": echo_threshold,
                "verbatimThreshold": verbatim_threshold, "origin": "netflix",
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
            mark = ("V" if sc >= verbatim_threshold else "✓") if sc >= threshold else ("~" if sc >= echo_threshold else " ")
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
    p.add_argument("--threshold", type=float, default=0.64)  # hand-validated borrowing bar
    p.add_argument("--echo-threshold", type=float, default=0.50)  # floor for same-framework echoes
    p.add_argument("--verbatim-threshold", type=float, default=0.85)  # near-verbatim (high-confidence) bar
    p.add_argument("--review-top", type=int, default=3)
    a = p.parse_args()
    main(a.threshold, a.echo_threshold, a.verbatim_threshold, a.review_top)
