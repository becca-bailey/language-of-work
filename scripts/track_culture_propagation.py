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
        # Seed with Netflix's own canonical deck phrasing so the origin matches by
        # construction; paraphrases fill in the semantic neighborhood. (Anchoring only
        # on paraphrases left Netflix's own "Increase Talent Density" lines below 0.62.)
        "anchors": [
            "The Key: Increase Talent Density faster than Complexity Grows.",
            "Increase talent density — attract and concentrate high-value people.",
            "Our edge is talent density — a high concentration of star performers.",
            "We deliberately keep a dense team of only the highest performers.",
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
        # Seed with Netflix's own phrasing (deck + current culture page); paraphrases
        # alone left even Netflix's canonical line at 0.600, below 0.62.
        "anchors": [
            "In creative and inventive work, the best are 10x better than the average.",
            "A high performer in any role is many times more effective than the average employee.",
            "A star performer is many times more valuable than an average employee.",
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
        # Netflix-distinctive phrasing only. "Unlimited vacation/PTO" is generic HR-speak
        # (everyone uses it) — matching it mislabeled HubSpot as a near-verbatim Netflix lift.
        "regex": re.compile(r"no vacation policy|take vacation|no (?:rules|forms).{0,25}(?:weeks|vacation)", re.I),
    },
}


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


def main(threshold: float, echo_threshold: float, review_top: int,
         companies: list[str] | None = None) -> None:
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
            # its sentences clears the bar (or matches the verbatim regex). No dedup — the
            # deck legitimately voices several concepts in one breath, and no echo band.
            for name, c in CONCEPTS.items():
                sims = sims_by[name]
                matched = [(years[i], texts[i], float(sims[i])) for i in range(len(texts)) if sims[i] >= threshold]
                verb = [(years[i], texts[i]) for i in range(len(texts)) if c["regex"].search(texts[i])]
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

        # Adopters: attribute each sentence to a SINGLE concept so one line can't count as
        # a borrowing under every concept it grazes. A verbatim regex hit is unambiguous
        # and wins outright; otherwise the sentence goes to its highest-similarity concept.
        # There it's a lift (>= threshold) or an echo (>= echo_threshold): same framework,
        # not necessarily borrowed.
        lifts: dict[str, list] = {n: [] for n in CONCEPTS}   # (i, score, verbatim)
        echoes: dict[str, list] = {n: [] for n in CONCEPTS}  # (i, score)
        for i in range(len(texts)):
            hits = [n for n in CONCEPTS if CONCEPTS[n]["regex"].search(texts[i])]
            if hits:
                for n in hits:
                    lifts[n].append((i, float(sims_by[n][i]), True))
                continue
            best_n = max(concept_names, key=lambda n: sims_by[n][i])
            sc = float(sims_by[best_n][i])
            if sc >= threshold:
                lifts[best_n].append((i, sc, False))
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
               {"threshold": threshold, "echoThreshold": echo_threshold, "origin": "netflix",
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
            mark = "✓" if sc >= threshold else ("~" if sc >= echo_threshold else " ")
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
    p.add_argument("--threshold", type=float, default=0.65)  # hand-validated borrowing bar
    p.add_argument("--echo-threshold", type=float, default=0.50)  # floor for same-framework echoes
    p.add_argument("--review-top", type=int, default=3)
    a = p.parse_args()
    main(a.threshold, a.echo_threshold, a.review_top)
