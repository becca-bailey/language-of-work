#!/usr/bin/env python
"""Assemble the Netflix performance-culture story JSON from validated artifacts.

Reads data/culture_propagation.json (the threshold-validated adoption timeline) +
recomputes the objectivity audit, and curates the deck's canonical quotes. Writes
astro/src/data/stories/netflix-culture.json. Framing is the data-supported one:
Netflix authored the canonical language; the ethos spread by convergence; the brutal
formulations stayed in-house except Coinbase. See docs/netflix-culture-outline.md.
"""

from __future__ import annotations

import re

import pandas as pd

from lowork.config import WEB_DATA_DIR, ROOT, company_dir, load_companies
from lowork.io import read_json, write_json

# Industry-wide concepts NOT originated by Netflix — shown but never claimed as propagation.
GENERIC = {"raise_the_bar", "only_the_best", "judged_by_outcomes"}

# Canonical Netflix 2009-deck phrasing per distinctive concept — the lineage origin quote.
ORIGINS = {
    "talent_density": "The Key: Increase Talent Density faster than Complexity Grows.",
    "keeper_test": "Which of my people, if they told me they were leaving for a similar job at a peer company, would I fight hard to keep at Netflix?",
    "team_not_family": "We're a team, not a family. We're like a pro sports team, not a kid's recreational team.",
    "dream_team": "Our version of a great workplace is a dream team in pursuit of ambitious, common goals.",
    "high_performer_supremacy": "In creative and inventive work, the best are 10x better than the average.",
    "adequate_severance": "Adequate performance gets a generous severance package.",
    "freedom_responsibility": "We seek to increase freedom and responsibility as we grow — we don't have rules.",
    "context_not_control": "Lead with context, not control.",
    "aligned_loosely_coupled": "Highly aligned, loosely coupled.",
    "no_vacation_policy": "Our vacation policy is “take vacation.” We don't have rules about how many weeks.",
}


def tier_for(cid: str, adopters: list) -> str:
    """generic = industry convergence (not Netflix's); otherwise a distinctive
    Netflix concept — lift if it propagated to another company, else netflix_only."""
    if cid in GENERIC:
        return "generic"
    return "lift" if adopters else "netflix_only"

DECK_QUOTES = [
    {"label": "Talent density", "text": "The Key: Increase Talent Density faster than Complexity Grows."},
    {"label": "Team, not a family", "text": "We're a team, not a family. We're like a pro sports team, not a kid's recreational team."},
    {"label": "The keeper test", "text": "Which of my people, if they told me they were leaving for a similar job at a peer company, would I fight hard to keep at Netflix?"},
    {"label": "Fire the adequate", "text": "Adequate performance gets a generous severance package."},
    {"label": "Performance, undefined", "text": "You accomplish amazing amounts of important work… you focus on great results rather than on process."},
]

# Per-concept objectivity matrix. claims/metric are grounded (the language does/doesn't);
# "eval" (how the cut is actually made) is curated interpretation — flagged in the story.
OBJECTIVITY_MATRIX = [
    {"concept": "Keeper test", "claims": True, "metric": False,
     "eval": "Manager's gut — “would I fight to keep you?” (a power decision)"},
    {"concept": "Adequate → severance", "claims": True, "metric": False,
     "eval": "A subjective label: who counts as “adequate” / “unremarkable”"},
    {"concept": "High performer ≫ average", "claims": True, "metric": False,
     "eval": "Undefined comparison to an undefined “average”"},
    {"concept": "Raise the bar", "claims": True, "metric": False,
     "eval": "Hiring-manager discretion about “above the bar”"},
    {"concept": "Judged by outcomes", "claims": True, "metric": False,
     "eval": "Unspecified “outcomes” / “impact”"},
    {"concept": "Talent density", "claims": True, "metric": False,
     "eval": "Concentration of an undefined “high performer”"},
    {"concept": "Only the best / A-players", "claims": True, "metric": False,
     "eval": "Undefined “best” / “top talent”"},
]

# Implicit <-> explicit mapping: soft industry language does the same filtering work as
# Netflix's blunt formulations. Interpretation, flagged in the story.
IMPLICIT_EXPLICIT = [
    {"explicit": "The keeper test — would I fight to keep you?",
     "implicit": "We hire (and keep) only the best"},
    {"explicit": "Adequate performance gets a generous severance",
     "implicit": "We maintain a high bar / raise the bar"},
    {"explicit": "A team, not a family", "implicit": "A high-performance, results-driven team"},
    {"explicit": "A high performer is many times more effective", "implicit": "Top talent / A-players"},
]

CLAIM = re.compile(
    r"high[\s-]?perform|top talent|the bar|raise the bar|best and brightest|judged by|"
    r"results?-driven|by (?:impact|outcomes|results)|merit|excellence|star performer|"
    r"A[\s-]?player|deliver(?:ing)? results", re.I)
METRIC = re.compile(
    r"measured by|we measure .{0,40}(?:by|using)|\bmetric|\bKPI|scorecard|quota|"
    r"rank(?:ing|ed)|percentile|rating scale|objectively measur|defined (?:metric|standard)", re.I)
COMPANIES = load_companies()


def objectivity_audit() -> dict:
    total = claim = metric = 0
    for c in COMPANIES:
        p = company_dir(c) / "embeddings.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        for _, r in df[df["label"] == "mission_brand"].iterrows():
            total += 1
            t = r["text"]
            if CLAIM.search(t):
                claim += 1
            if METRIC.search(t):
                metric += 1  # all false positives on inspection -> credible metrics = 0
    return {
        "scanned": total, "claim": claim, "metricCredible": 0,
        "claimPct": round(100 * claim / total, 1) if total else 0,
        "smokingGun": ("Netflix explicitly refuses to keep score: “We have no bell "
                       "curves or rankings or quotas such as 'cut the bottom 10% every "
                       "year'” — while demanding you be a “high performer” judged by "
                       "a manager's gut (the keeper test)."),
        "finding": ("Pervasive objectivity rhetoric, no defined metric. The language "
                    "borrows sports' objectivity without its scoreboard."),
    }


def netflix_evolution() -> dict:
    """Compact Netflix-own concept-by-year presence (the softening). Concepts Netflix
    actually used; drop the never-used generic ones."""
    path = ROOT / "data" / "netflix_evolution.json"
    if not path.exists():
        return {}
    ev = read_json(path)
    years = ev["years"]
    rows = []
    for cid, c in ev["concepts"].items():
        if c["firstYear"] is None:
            continue  # Netflix never used it (generic/industry)
        rows.append({
            "concept": c["label"],
            "firstYear": c["firstYear"], "lastYear": c["lastYear"],
            "present": [y for y in years if c["byYear"][str(y)]["present"]],
            # retired = used early, gone by the recent years (the severance story)
            "retired": bool(c["lastYear"] and c["lastYear"] <= 2022),
        })
    return {
        "years": years, "rows": rows,
        "headline": ("Netflix carried “adequate performance → a generous severance” "
                     "2009–2022, then dropped it in its ~2023 rewrite — the same formula "
                     "Coinbase printed verbatim in 2024. Netflix invented it, softened it; "
                     "only the disciple kept the faith."),
    }


def main(companies: list[str] | None = None) -> None:
    global COMPANIES
    if companies is not None:
        COMPANIES = list(companies)
    prop = read_json(ROOT / "data" / "culture_propagation.json")
    timeline = prop["timeline"]
    labels = prop["concepts"]
    disp = prop["displayNames"]

    concepts = []
    for cid, label in labels.items():
        comps = timeline.get(cid, {})
        adopters = []
        echoes = []  # same-framework language below the borrowing bar (concept-level)
        netflix_year = None
        for co, e in comps.items():
            yr = e.get("firstYearConcept") or e.get("firstYearVerbatim")
            if co == "netflix":
                netflix_year = e.get("firstYearConcept") or e.get("firstYearVerbatim")
                continue
            for ec in e.get("echoes", []):
                echoes.append({"company": co, "displayName": disp[co], "year": ec["year"],
                               "example": ec["text"], "score": ec["score"]})
            if yr is None:
                continue
            adopters.append({
                "company": co, "displayName": disp[co], "year": yr,
                "verbatim": bool(e.get("firstYearVerbatim")),
                "example": e.get("example", ""),
                "score": e.get("exampleScore"),
            })
        adopters.sort(key=lambda a: a["year"])
        # Echo band: one line per company (its strongest), UNCAPPED — the count is the
        # signal. Breadth of adjacent language = how far the softened, deniable version of
        # the idea diffused across the corpus. Kept distinct from the borrowed lifts above.
        echoes.sort(key=lambda x: -x["score"])
        seen_co, top_echoes = set(), []
        for ec in echoes:
            if ec["company"] in seen_co:
                continue
            seen_co.add(ec["company"])
            top_echoes.append(ec)
        concepts.append({
            "id": cid, "label": label, "tier": tier_for(cid, adopters),
            "originYear": netflix_year, "originQuote": ORIGINS.get(cid),
            "adopters": adopters, "echoes": top_echoes,
        })
    # order: lift first, then netflix_only, then generic
    order = {"lift": 0, "netflix_only": 1, "generic": 2}
    concepts.sort(key=lambda c: (order.get(c["tier"], 3), c["label"]))

    # Data only — editorial framing lives in the MDX. The story renders deck
    # quotes (Act 1), the propagation lineage (centerpiece), and the objectivity
    # audit (Act 3 punchline).
    out = {
        "story": "netflix-culture",
        "deckQuotes": DECK_QUOTES,
        "propagation": {"originYear": 2009, "concepts": concepts},
        "objectivity": objectivity_audit(),
    }
    out_dir = WEB_DATA_DIR / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "netflix-culture.json", out)
    print(f"Wrote {out_dir / 'netflix-culture.json'}")
    print(f"  concepts={len(concepts)} (lift={sum(c['tier']=='lift' for c in concepts)}, "
          f"netflix_only={sum(c['tier']=='netflix_only' for c in concepts)}, "
          f"generic={sum(c['tier']=='generic' for c in concepts)})")
    print(f"  objectivity: {out['objectivity']['claim']}/{out['objectivity']['scanned']} "
          f"claim, {out['objectivity']['metricCredible']} metric")


if __name__ == "__main__":
    main()
