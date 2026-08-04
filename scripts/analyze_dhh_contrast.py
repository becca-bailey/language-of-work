#!/usr/bin/env python
"""Descriptive layer + policy-vs-founder-speech contrast for a blog case corpus.

Three parts, all over the raw post cache (full text):

1. Descriptive census: posts/year, words/year.
2. Transparent regex lexicon: group terms + the civilizational patterns from
   track_dei_phrases — the fully inspectable sanity anchor the LLM extractor
   (classify_group_refs.py) must roughly agree with (within ~2x per year;
   investigate divergence).
3. Contrast summary: the blog's reference counts (LLM + regex, side by side)
   against the company record already computed elsewhere — the April 2021
   "Changes at Basecamp" policy (canon), all-neutral careers DEI stances,
   near-bottom inclusion/altruism ranks. Company artifacts are READ, never
   recomputed, and nothing here writes outside data/<case>/.

Small-N discipline: raw counts by year, no percentages on denominators < 20,
no significance tests.

Usage:
  uv run scripts/analyze_dhh_contrast.py --case dhh_blog
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone

from track_dei_phrases import CIVILIZATIONAL_PATTERNS

from lowork.config import DATA_DIR, WEB_DATA_DIR, company_dir
from lowork.io import read_json, write_json
from lowork.sentences import split_sentences

POLICY_DATE = "2021-04-26"  # "Changes at Basecamp" (Fried), world.hey.com/jason
POLICY_CANON = "data/basecamp/canon/changes_at_basecamp_2021.md"

GROUP_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("migrants/immigration", re.compile(r"\bmigrants?\b|\bimmigr\w+|\basylum\b|\brefugees?\b", re.I)),
    ("roma/gypsies", re.compile(r"\broma\b|\bgyps(?:y|ies)\b", re.I)),
    ("muslims/islam", re.compile(r"\bmuslims?\b|\bislam\w*\b", re.I)),
    ("jews/jewish", re.compile(r"\bjews?\b|\bjewish\b|\bantisemit\w*", re.I)),
    ("black people", re.compile(r"\bblack (?:people|men|women|americans?|communit\w+)\b", re.I)),
    ("trans/gender ideology", re.compile(r"\btrans(?:gender)?\b|\bgender ideolog\w*", re.I)),
    ("foreigners/vagrants", re.compile(r"\bforeigners?\b|\bvagrants?\b", re.I)),
    ("deportation", re.compile(r"\bdeport\w*\b", re.I)),
]


def load_posts(case: str) -> list[dict]:
    raw_dir = company_dir(case) / "raw_posts"
    posts = [json.loads(p.read_text()) for p in sorted(raw_dir.glob("*.json"))]
    if not posts:
        raise SystemExit(f"no raw posts under {raw_dir} — run fetch_case.py first")
    return posts


def lexicon_scan(posts: list[dict]) -> dict:
    patterns = GROUP_PATTERNS + CIVILIZATIONAL_PATTERNS
    terms: dict[str, dict] = {}
    for post in posts:
        year = (post.get("date") or "")[:4] or "undated"
        for sent in split_sentences(post.get("text", "")):
            for label, pat in patterns:
                if not pat.search(sent):
                    continue
                rec = terms.setdefault(
                    label,
                    {
                        "mentions_by_year": Counter(),
                        "posts_by_year": defaultdict(set),
                        "first_date": post.get("date", ""),
                        "examples": [],
                    },
                )
                rec["mentions_by_year"][year] += 1
                rec["posts_by_year"][year].add(post["slug"])
                if post.get("date") and (not rec["first_date"] or post["date"] < rec["first_date"]):
                    rec["first_date"] = post["date"]
                if len(rec["examples"]) < 5:
                    rec["examples"].append(
                        {"date": post.get("date", ""), "slug": post["slug"], "sentence": sent.strip()[:220]}
                    )
    return {
        label: {
            "first_date": rec["first_date"],
            "total_mentions": sum(rec["mentions_by_year"].values()),
            "mentions_by_year": dict(sorted(rec["mentions_by_year"].items())),
            "posts_by_year": {y: len(s) for y, s in sorted(rec["posts_by_year"].items())},
            "examples": rec["examples"],
        }
        for label, rec in sorted(terms.items(), key=lambda kv: -sum(kv[1]["mentions_by_year"].values()))
    }


def company_record() -> dict:
    """Already-computed Basecamp facts, read-only, with provenance paths."""
    record: dict = {"policy_date": POLICY_DATE, "policy_canon": POLICY_CANON}
    stances_path = DATA_DIR / "basecamp" / "dei_stances.json"
    if stances_path.exists():
        record["careers_dei_stances"] = dict(Counter(read_json(stances_path).values()))
        record["careers_dei_stances_source"] = str(stances_path)
    fp_path = WEB_DATA_DIR / "fingerprints" / "basecamp.json"
    if fp_path.exists():
        fp = read_json(fp_path)
        record["careers_axis_ranks"] = {
            a.get("axis", a.get("key", "?")): a.get("rank")
            for a in fp.get("axes", [])
            if isinstance(a, dict)
        }
        record["careers_axis_ranks_source"] = str(fp_path)
    return record


def main(case: str) -> None:
    cdir = company_dir(case)
    posts = load_posts(case)

    posts_by_year: Counter = Counter()
    words_by_year: Counter = Counter()
    for post in posts:
        year = (post.get("date") or "")[:4] or "undated"
        posts_by_year[year] += 1
        words_by_year[year] += len(post.get("text", "").split())

    lexicon = lexicon_scan(posts)

    llm = {}
    refs_path = cdir / "group_references.json"
    if refs_path.exists():
        r = read_json(refs_path)
        llm = {
            "model": r["model"],
            "prompt_version": r["prompt_version"],
            "n_posts_with_refs": r["n_posts_with_refs"],
            "n_refs": r["n_refs"],
            "posts_with_refs_by_year": r["posts_with_refs_by_year"],
            "by_year_group": r["by_year_group"],
            "by_year_frame": r["by_year_frame"],
            "refusals": r["refusals"],
            "quote_check_failures": r["quote_check_failures"],
        }

    out = {
        "case": case,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "census": {
            "n_posts": len(posts),
            "via_wayback": sum(1 for p in posts if p.get("via_wayback")),
            "undated": sum(1 for p in posts if not p.get("date")),
            "posts_by_year": dict(sorted(posts_by_year.items())),
            "words_by_year": dict(sorted(words_by_year.items())),
        },
        "lexicon": lexicon,
        "llm_references": llm,
        "company_record": company_record(),
        "notes": [
            "Raw counts by year; no rates on denominators < 20; no significance tests.",
            "lexicon = transparent regex anchor; llm_references = coded instrument; "
            "compare per year (within ~2x), investigate divergence rather than averaging.",
            "company_record values are read from existing basecamp artifacts, never recomputed here.",
        ],
    }
    path = cdir / "contrast_summary.json"
    write_json(path, out)

    print(f"{len(posts)} posts; by year: {dict(sorted(posts_by_year.items()))}")
    print("\nLexicon (total mentions | posts by year):")
    for label, rec in lexicon.items():
        print(f"  {label:26s} {rec['total_mentions']:4d} | {rec['posts_by_year']}")
    if llm:
        print(f"\nLLM instrument: {llm['n_refs']} refs across {llm['n_posts_with_refs']} posts; "
              f"posts/year {llm['posts_with_refs_by_year']}")
    print(f"\nWrote {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    args = p.parse_args()
    main(args.case)
