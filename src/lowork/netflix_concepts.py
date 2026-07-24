"""Single source of truth for the Netflix-deck concept registry.

Every section of the netflix-culture story reads from HERE — the propagation
tracker (labels + anchors), the deck-quote cards, the lineage vizzes' origin
quotes, and the objectivity matrix. Before 2026-07-23 these lived as four
hand-maintained parallel maps (tracker CONCEPTS + export ORIGINS/DECK_QUOTES/
OBJECTIVITY_MATRIX) and drifted every time a concept changed: new concepts
never got an ORIGINS entry, so their rows were silently dropped from both
charts (originQuote null → filtered in lineage.ts).

Per-concept fields:
  label       shown everywhere (viz rows, quote cards, matrices) — one string.
  anchors     tracker embedding anchors. CONVENTION: the FIRST anchor must be
              the deck's own phrasing, or Netflix's origin year lands wrong
              (paraphrase-only anchors put F&R at 2013, vacation at 2017).
  deck_quote  the deck's own line — the quote card text AND the origin-marker
              tooltip. Required for non-generic concepts.
  generic     True = industry convergence (Amazon's register, not Netflix's);
              tracked for the record but excluded from the lineage vizzes and
              quote cards.
  objectivity None, or {"claims": bool, "metric": bool, "eval": str} for the
              scoreboard section's matrix. "eval" is curated interpretation,
              flagged as such in the story.

Removed concepts (kept here so the reasoning survives):
  dream_team REMOVED 2026-07-23 (Becca): of 29 catches, 23 were generic
  "amazing team" boilerplate below any other concept's floor and 6 re-route to
  only_the_best — it tracked HR mush, not lineage (data/culture_deck_clusters.md).
  aligned_loosely_coupled REMOVED 2026-07-23 (Becca): zero lifts, zero echoes
  across the whole cohort, never introduced in the story — a dead row.
"""

import hashlib


def match_key(cid: str, company: str, year: int, text: str) -> str:
    """Stable identity for one tracker match — shared by the judge step
    (writes data/culture_echo_judgments.json) and the story export (reads it),
    so judgments survive tracker re-runs and only new sentences get judged."""
    return f"{cid}|{company}|{year}|{hashlib.sha1(text.encode()).hexdigest()[:16]}"


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
        "deck_quote": "The Key: Increase Talent Density faster than Complexity Grows.",
        "generic": False,
        "objectivity": {"claims": True, "metric": False,
                        "eval": "Concentration of an undefined “high performer”"},
    },
    "minimize_complexity": {
        "label": "Minimize complexity",
        # The other half of deck s55's key equation (s57); coinbase lifted it
        # nearly verbatim in 2014-2016 ("ruthless about cutting out complexity").
        "anchors": [
            "Minimize complexity growth — few big products versus many small ones, eliminate distracting complexity.",
            "We avoid chaos as we grow by eliminating complexity rather than adding rules and process.",
            "We stay effective by ruthlessly eliminating complexity and keeping things simple as we grow.",
        ],
        "deck_quote": "Minimize complexity growth: few big products vs many small ones — eliminate distracting complexity (barnacles).",
        "generic": False,
        "objectivity": None,
    },
    "keeper_test": {
        "label": "Keeper test",
        "anchors": [
            "If this person told us they were leaving for a similar job, would we fight to keep them?",
            "We apply the keeper test: managers keep only the people they would fight to retain.",
        ],
        "deck_quote": "Which of my people, if they told me they were leaving for a similar job at a peer company, would I fight hard to keep at Netflix?",
        "generic": False,
        "objectivity": {"claims": True, "metric": False,
                        "eval": "Manager's gut — “would I fight to keep you?” (a power decision)"},
    },
    "team_not_family": {
        "label": "Team, not a family",
        "anchors": [
            "We are a high-performance team, not a family.",
            "We are like a professional sports team, not a recreational team.",
        ],
        "deck_quote": "We're a team, not a family. We're like a pro sports team, not a kid's recreational team. Netflix leaders hire, develop and cut smartly, so we have stars in every position.",
        "generic": False,
        "objectivity": None,
    },
    "adequate_severance": {
        "label": "Adequate → severance",
        # Third anchor (2026-07-23) makes the exit explicit without the severance
        # noun, so euphemized descendants ("underperformance is addressed
        # quickly") land in the echo band instead of vanishing below the floor.
        # Cohort-tested: catches exactly engine 0.57 / stripe 0.51 — no HR-noise.
        "anchors": [
            "Merely adequate performance earns a generous severance package.",
            "If your work is only solid, we part ways with a generous severance.",
            "People who are only performing adequately are let go quickly.",
        ],
        "deck_quote": "Adequate performance gets a generous severance package.",
        "generic": False,
        "objectivity": {"claims": True, "metric": False,
                        "eval": "A subjective label: who counts as “adequate” / “unremarkable”"},
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
        "deck_quote": "In procedural work, the best are 2x better than the average. In creative/inventive work, the best are 10x better than the average.",
        "generic": False,
        "objectivity": {"claims": True, "metric": False,
                        "eval": "Undefined comparison to an undefined “average”"},
    },
    "not_for_everyone": {
        "label": "Not right for everyone",
        # Deck s38: self-selection as a feature. Echoed by shopify 2018,
        # engine 2021+, coinbase, stripe.
        "anchors": [
            "Our high performance culture is not right for everyone.",
            "We are not for everyone — some people value job security and stability over performance and do not like our culture.",
            "We attract people who thrive here and help the others realize we are not right for them.",
        ],
        "deck_quote": "Our high performance culture is not right for everyone… some people value job security and stability over performance, and don't like our culture.",
        "generic": False,
        "objectivity": None,
    },
    "candor_directness": {
        "label": "Candor / honesty always",
        # Deck s16 + s26-27. Distinct from transparency-of-information: this is
        # interpersonal directness and hard conversations.
        "anchors": [
            "You are known for candor and directness; you only say things about fellow employees you will say to their face.",
            "Honesty always — as a leader, no one in your group should be materially surprised of your views.",
            "We give each other direct feedback and have hard conversations instead of comfortable silence.",
        ],
        "deck_quote": "You are known for candor and directness… you only say things about fellow employees you will say to their face.",
        "generic": False,
        "objectivity": None,
    },
    "values_not_wall": {
        "label": "Values ≠ words on the wall",
        # The deck's Enron-lobby slide: espoused values vs. what actually gets
        # rewarded. Seed with the deck's own phrasing (see talent_density note).
        "anchors": [
            "The actual company values, as opposed to the nice-sounding values, are shown by who gets rewarded, promoted, or let go.",
            "Enron had their values displayed in the lobby — integrity, communication, respect, excellence — but those were not what was really valued.",
            "Real values are not the nice-sounding statements on the wall; they are the behaviors and skills we reward and promote.",
        ],
        "deck_quote": "The actual company values, as opposed to the nice-sounding values, are shown by who gets rewarded, promoted, or let go.",
        "generic": False,
        "objectivity": None,
    },
    "freedom_responsibility": {
        "label": "Freedom & responsibility / no rules",
        # First anchor is the deck's own s41/s42 phrasing so the 2009 origin
        # matches by construction (see talent_density note) — paraphrase-only
        # anchors left Netflix's origin at 2013.
        "anchors": [
            "Responsible people thrive on freedom, and are worthy of freedom — our model is to increase employee freedom as we grow, rather than limit it.",
            "We don't have rules; we rely on people's good judgment.",
            "We run on freedom and responsibility, not rules and process.",
            "We have values, not rules — we trust people to act in the company's interest.",
        ],
        "deck_quote": "Our model is to increase employee freedom as we grow, rather than limit it, to continue to attract and nourish innovative people.",
        "generic": False,
        "objectivity": None,
    },
    "context_not_control": {
        "label": "Context, not control",
        "anchors": [
            "Leaders lead with context, not control.",
            "Managers set context and let teams make the decisions rather than controlling them.",
        ],
        "deck_quote": "Context, not control: provide the insight and understanding to enable sound decisions.",
        "generic": False,
        "objectivity": None,
    },
    "no_vacation_policy": {
        "label": "No vacation policy / unlimited time off",
        # First anchor is the deck's own s68/s69 phrasing (origin was landing
        # at 2017 with paraphrase-only anchors).
        "anchors": [
            "There is no vacation policy or tracking — just as we don't have a 9-to-5 workday policy, we don't need a vacation policy.",
            "We have no vacation policy; take time off as you see fit.",
            "There is no formal vacation tracking — take the time you need.",
        ],
        "deck_quote": "We should focus on what people get done, not on how many days worked. Just as we don't have a 9am–5pm workday policy, we don't need a vacation policy.",
        "generic": False,
        "objectivity": None,
    },
    # ---- generic tier: industry convergence (Amazon's register, not Netflix's).
    # Tracked for the record; excluded from the lineage vizzes and quote cards.
    "raise_the_bar": {
        "label": "Raise the bar",
        "anchors": [
            "We hold relentlessly high standards and keep raising the bar.",
            "Every new hire must raise the average and lift the whole team's bar.",
        ],
        "deck_quote": None,
        "generic": True,
        "objectivity": {"claims": True, "metric": False,
                        "eval": "Hiring-manager discretion about “above the bar”"},
    },
    "judged_by_outcomes": {
        "label": "Judged by outcomes/results",
        "anchors": [
            "You are judged by your results and outcomes, not your effort or hours.",
            "We measure people by impact and results, not activity.",
        ],
        "deck_quote": None,
        "generic": True,
        "objectivity": {"claims": True, "metric": False,
                        "eval": "Unspecified “outcomes” / “impact”"},
    },
    "only_the_best": {
        "label": "Only the best / A-players",
        "anchors": [
            "We hire only the best and the brightest — A-players, top talent.",
            "We recruit only elite, top-tier people and accept nothing less.",
        ],
        "deck_quote": None,
        "generic": True,
        "objectivity": {"claims": True, "metric": False,
                        "eval": "Undefined “best” / “top talent”"},
    },
}

GENERIC = {cid for cid, c in CONCEPTS.items() if c["generic"]}

# Quote cards: one per distinctive concept, registry order, deck's own lines —
# by construction the same set and labels as the lineage viz rows.
DECK_QUOTES = [
    {"label": c["label"], "text": c["deck_quote"]}
    for c in CONCEPTS.values()
    if not c["generic"] and c["deck_quote"]
]

# Scoreboard matrix: concepts whose copy claims objectivity, registry order.
OBJECTIVITY_MATRIX = [
    {"concept": c["label"], **c["objectivity"]}
    for c in CONCEPTS.values()
    if c["objectivity"]
]
