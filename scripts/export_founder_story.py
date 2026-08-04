#!/usr/bin/env python
"""Export the founder-speech (dhh_blog) story data for the Astro site.

Reads the case-corpus artifacts (group_references.json, dei_stances.json,
gender_score.json, contrast_summary.json) plus the published gender story's
company columns for the comparison strip, and writes
astro/src/data/stories/founder-speech.json.

The story page is a DRAFT (published: false) until the hand-label validation
gate passes; the export carries validation_pending so the page can badge
every number as provisional.

Usage:
  uv run scripts/export_founder_story.py
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

from lowork.config import WEB_DATA_DIR, company_dir
from lowork.io import load_all_chunks, read_json, write_json

CASE = "dhh_blog"
FRAMES = ["sympathetic_defense", "neutral_mention", "policy_critique", "hostile_derogatory", "threat_crime_framing"]
# Hostility ordering for collapsing a post's several passages to one frame
# per group: the most-hostile frame present wins ("worst frame").
FRAME_SEVERITY = {
    "threat_crime_framing": 4,
    "hostile_derogatory": 3,
    "policy_critique": 2,
    "neutral_mention": 1,
    "sympathetic_defense": 0,
}
PRO_REGISTERS = ["explicit_demographic", "structural_process", "aspirational_vague", "belonging_culture"]


def per_group_worst(refs_list: list[dict]) -> dict[str, str]:
    """{group: worst frame present} for one post — the post-level unit."""
    worst: dict[str, str] = {}
    for r in refs_list:
        g, f = r.get("group"), r.get("frame")
        if f not in FRAME_SEVERITY or not g:
            continue
        if g not in worst or FRAME_SEVERITY[f] > FRAME_SEVERITY[worst[g]]:
            worst[g] = f
    return worst
# Editorial quote picks: the arc, not just the extremes. slug -> pick reasons
QUOTE_PICKS = [
    # (slug, group, frame, quote_substring) — resolved against extracted refs
    # below; the substring picks the exact reference when a post has several.
    ("america-is-never-getting-to-denmark-e471ae91", "migrants_refugees", "sympathetic_defense", "most welcoming"),
    ("the-reality-of-the-danish-fairytale-78069fbf", "migrants_refugees", "threat_crime_framing", ""),
    ("as-i-remember-london-e7d38e64", "migrants_refugees", "threat_crime_framing", "demographic replacement"),
    ("the-rape-of-britain-610412f8", "muslims", "threat_crime_framing", ""),
    ("three-sacred-cows-that-must-die-so-europe-can-live-1afb203d", "migrants_refugees", "threat_crime_framing", "must go"),
    ("wolves-sheep-and-gypsies-ba44af6a", "roma", "threat_crime_framing", ""),
]


def register_series(case: str, display: str, min_year: int | None = None) -> dict:
    """StoryRegisterChart-compatible series for one corpus: per-year
    `registers` merges pro-inclusion register counts and counter stance
    counts (register and stance are separate instruments by design), plus
    the component's label-aware tooltip quotes (counter prefers a
    civilizational chunk over an apolitical one). nChunks = chunks the
    register classifier covered that year; stance counts are taken over the
    same covered set."""
    cdir = company_dir(case)
    regs_path = cdir / "dei_registers.json"
    registers = read_json(regs_path) if regs_path.exists() else {}
    stances_path = cdir / "dei_stances.json"
    stances = read_json(stances_path) if stances_path.exists() else {}
    chunks = {c["chunk_id"]: c for c in load_all_chunks(cdir / "chunks")}

    covered: dict[str, list[dict]] = defaultdict(list)
    for cid, label in registers.items():
        c = chunks.get(cid)
        if c and c.get("year"):
            covered[str(c["year"])].append(c)

    def _quote(c: dict, *, register: str | None = None, stance: str | None = None) -> dict:
        return {
            "text": c["text"][:400],
            "heading": c.get("heading") or "",
            "register": register,
            "stance": stance,
        }

    out_years = []
    for y in sorted(covered):
        if min_year is not None and int(y) < min_year:
            continue
        reg_counts = Counter(registers[c["chunk_id"]] for c in covered[y])
        stance_counts = Counter(s for c in covered[y] if (s := stances.get(c["chunk_id"])))
        inclusion = civ = apol = None
        for c in covered[y]:
            cid = c["chunk_id"]
            if inclusion is None and registers.get(cid) in PRO_REGISTERS:
                inclusion = _quote(c, register=registers[cid])
            s = stances.get(cid)
            if civ is None and s == "civilizational_mission":
                civ = _quote(c, stance=s)
            if apol is None and s == "mission_focus_apolitical":
                apol = _quote(c, stance=s)
        out_years.append(
            {
                "year": int(y),
                "nChunks": len(covered[y]),
                "thin": False,
                "registers": {
                    **{r: reg_counts.get(r, 0) for r in PRO_REGISTERS},
                    "absent": reg_counts.get("absent", 0),
                    "mission_focus_apolitical": stance_counts.get("mission_focus_apolitical", 0),
                    "civilizational_mission": stance_counts.get("civilizational_mission", 0),
                },
                "inclusionQuote": inclusion,
                "counterQuote": civ or apol,
            }
        )
    return {"id": case, "displayName": display, "years": out_years}


def main() -> None:
    cdir = company_dir(CASE)
    refs = read_json(cdir / "group_references.json")
    stances = read_json(cdir / "dei_stances.json")
    gender = read_json(cdir / "gender_score.json")
    contrast = read_json(cdir / "contrast_summary.json")

    posts_by_year = contrast["census"]["posts_by_year"]

    # POST-LEVEL aggregation (unit = the post, not the passage): the model's
    # passage segmentation is arbitrary, so each post collapses to one worst
    # frame per group, and `frames` counts POSTS bucketed by their overall
    # worst frame (each post once). `groups` counts POSTS referencing each
    # group. This matches how the hand-labels are coded and how every claim
    # is stated ("N posts", not "N references").
    frames_by_year: dict[str, Counter] = defaultdict(Counter)   # posts by worst frame
    groups_by_year: dict[str, Counter] = defaultdict(Counter)   # posts referencing each group
    posts_with_refs: Counter = Counter()
    for p in refs["posts"]:
        year = (p["date"] or "")[:4]
        if not year:
            continue
        worst = per_group_worst(p["refs"])  # {group: worst frame}
        if not worst:
            continue
        posts_with_refs[year] += 1
        post_frame = max(worst.values(), key=lambda f: FRAME_SEVERITY[f])
        frames_by_year[year][post_frame] += 1
        for g in worst:
            groups_by_year[year][g] += 1

    years = sorted(posts_by_year)
    ref_rows = [
        {
            "year": int(y),
            "posts": posts_by_year[y],
            "postsWithRefs": posts_with_refs.get(y, 0),
            "frames": {f: frames_by_year[y].get(f, 0) for f in FRAMES},
            "groups": dict(groups_by_year[y]),
        }
        for y in years
    ]

    # Mirrored stance chart, same shape as the DEI story: pro-inclusion
    # REGISTER classes stack up, counterforce STANCE classes stack down —
    # two instruments by design (register = pro-DEI content type; stance =
    # the bipolar counterforce axis). Registers may be absent if
    # classify_dei_register.py hasn't run yet; export zeros so the page
    # still renders.
    chunks = {c["chunk_id"]: c for c in load_all_chunks(cdir / "chunks")}
    registers_path = cdir / "dei_registers.json"
    registers = read_json(registers_path) if registers_path.exists() else {}
    reg_by_year: dict[str, Counter] = defaultdict(Counter)
    for cid, r in registers.items():
        c = chunks.get(cid)
        if c and r in PRO_REGISTERS:
            reg_by_year[str(c["year"])][r] += 1
    stance_by_year: dict[str, Counter] = defaultdict(Counter)
    for cid, s in stances.items():
        c = chunks.get(cid)
        if c:
            stance_by_year[str(c["year"])][s] += 1
    stance_rows = [
        {
            "year": int(y),
            "chunks": sum(stance_by_year[y].values()),
            "pro": {r: reg_by_year[y].get(r, 0) for r in PRO_REGISTERS},
            "affirming": stance_by_year[y].get("affirming_dei", 0),
            "apolitical": stance_by_year[y].get("mission_focus_apolitical", 0),
            "civilizational": stance_by_year[y].get("civilizational_mission", 0),
        }
        for y in years
    ]

    # StoryRegisterChart-compatible series (the DEI story's own component):
    # the blog next to Basecamp's careers corpus over the same era, so the
    # company-clean / founder-loud contrast reads in one figure.
    dei_companies = [register_series(CASE, "DHH's blog")]

    # Gender comparison strip: blog pooled vs anchor companies from the story
    story = read_json(WEB_DATA_DIR / "stories" / "gender-language.json")
    by_co = {c["company"]: c for c in story["columns"]}
    anchors = ["anduril", "basecamp", "netflix", "coinbase", "snap"]
    gender_rows = [
        {
            "key": "dhh_blog",
            "name": "DHH's blog",
            "meanZ": gender["pooled"]["meanZ"],
            "mascShare": gender["pooled"]["mascShare"],
            "femShare": gender["pooled"]["femShare"],
            "isBlog": True,
        }
    ] + [
        {
            "key": co,
            "name": by_co[co].get("name", co),
            "meanZ": by_co[co].get("meanZ"),
            "mascShare": by_co[co].get("mascShare"),
            "femShare": by_co[co].get("femShare"),
            "isBlog": False,
        }
        for co in anchors
        if co in by_co
    ]

    # Quote cards, resolved from the machine-checked extractions
    by_slug = {p["slug"]: p for p in refs["posts"]}
    quotes = []
    for slug, group, frame, needle in QUOTE_PICKS:
        p = by_slug.get(slug)
        if not p:
            continue
        match = next(
            (r for r in p["refs"]
             if r["group"] == group and r["frame"] == frame
             and (not needle or needle in r["quote"])),
            None,
        )
        if match:
            quotes.append(
                {
                    "date": p["date"],
                    "title": p["title"],
                    "url": p["url"],
                    "group": group,
                    "frame": frame,
                    "quote": match["quote"],
                }
            )

    out = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "case": CASE,
        "validationPending": True,
        "model": refs["model"],
        "promptVersion": refs["promptVersion"] if "promptVersion" in refs else refs.get("prompt_version"),
        "nPosts": refs["n_posts"],
        "nPostsWithRefs": sum(posts_with_refs.values()),
        "nThreatPosts": sum(
            fb.get("threat_crime_framing", 0) for fb in frames_by_year.values()
        ),
        "nMentions": refs["n_refs"],  # raw passage count; secondary, not a headline
        "quoteCheckFailures": refs["quote_check_failures"],
        "refusals": len(refs["refusals"]),
        "frames": FRAMES,
        "refsByYear": ref_rows,
        "stanceByYear": stance_rows,
        "deiCompanies": dei_companies,
        "genderCompare": gender_rows,
        "genderByYear": [
            {"year": int(y), **v} for y, v in sorted(gender["by_year"].items())
        ],
        "quotes": quotes,
        "policyDate": "2021-04-26",
    }
    path = WEB_DATA_DIR / "stories" / "founder-speech.json"
    write_json(path, out)
    print(f"Wrote {path}")
    print(f"  {len(ref_rows)} ref years, {len(stance_rows)} stance years, "
          f"{len(gender_rows)} gender rows, {len(quotes)} quotes")


if __name__ == "__main__":
    main()
