#!/usr/bin/env python
"""Extract and code marginalized-group references across a founder-blog case corpus.

Reads the raw post cache (data/<case>/raw_posts/*.json — full post text, not
chunks), runs the group-reference instrument (prompts/group_references.yaml,
GROUP_REF_MODEL) one post per request, then applies machine-side guards:

- 100% verbatim-quote containment check against the raw post text (normalized
  whitespace/quote glyphs); failures are dropped AND counted, never silent.
- taxonomy validation (unknown group/frame values dropped and counted).
- refusal log: refusal-shaped responses are retried once with reinforced
  analyst framing; leftovers are listed for hand-coding. Refusals must never
  silently zero a post's count.

Writes data/<case>/group_references.json: per-post references plus
by_year_group / by_year_frame / posts_with_refs rollups, model + prompt
version pins, and all guard counts.

Usage:
  uv run scripts/classify_group_refs.py --case dhh_blog
  uv run scripts/classify_group_refs.py --case dhh_blog --limit 5   # smoke test
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone

from lowork.config import GROUP_REF_MODEL, company_dir
from lowork.group_refs import FRAMES, GROUPS, extract_references, load_prompt
from lowork.io import write_json

_WS = re.compile(r"\s+")
_GLYPHS = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-"})


def _norm(s: str) -> str:
    return _WS.sub(" ", s.translate(_GLYPHS)).strip().lower()


def load_posts(case: str) -> list[dict]:
    raw_dir = company_dir(case) / "raw_posts"
    posts = [json.loads(p.read_text()) for p in sorted(raw_dir.glob("*.json"))]
    if not posts:
        raise SystemExit(f"no raw posts under {raw_dir} — run fetch_case.py first")
    return sorted(posts, key=lambda p: p.get("date") or "9999")


def validate_refs(post: dict, refs: list[dict]) -> tuple[list[dict], int, int]:
    """(kept, quote_failures, taxonomy_failures) for one post's extractions."""
    body = _norm(post.get("text", ""))
    kept, bad_quote, bad_taxonomy = [], 0, 0
    for ref in refs:
        group, frame = ref.get("group"), ref.get("frame")
        quote = ref.get("quote", "")
        if group not in GROUPS or frame not in FRAMES:
            bad_taxonomy += 1
            continue
        if not quote or _norm(quote) not in body:
            bad_quote += 1
            continue
        item = {"group": group, "frame": frame, "quote": quote, "sentence": ref.get("sentence", "")}
        if ref.get("group_name"):
            item["group_name"] = ref["group_name"]
        kept.append(item)
    return kept, bad_quote, bad_taxonomy


def main(case: str, limit: int | None) -> None:
    posts = load_posts(case)
    if limit:
        posts = posts[:limit]
    print(f"{len(posts)} posts to code")

    results = extract_references(posts)

    refused = [slug for slug, r in results.items() if r["refused"]]
    if refused:
        print(f"retrying {len(refused)} refusal(s) with reinforced framing...")
        by_slug = {p["slug"]: p for p in posts}
        retry = extract_references(
            [by_slug[s] for s in refused], retry_slugs=set(refused)
        )
        results.update(retry)
    still_refused = sorted(slug for slug, r in results.items() if r["refused"])

    prompt = load_prompt()
    per_post, quote_failures, taxonomy_failures = [], 0, 0
    by_year_group: dict[str, Counter] = defaultdict(Counter)
    by_year_frame: dict[str, Counter] = defaultdict(Counter)
    posts_with_refs: Counter = Counter()
    for post in posts:
        res = results.get(post["slug"], {"refs": [], "refused": True})
        kept, bad_q, bad_t = validate_refs(post, res["refs"])
        quote_failures += bad_q
        taxonomy_failures += bad_t
        year = (post.get("date") or "")[:4] or "undated"
        if kept:
            posts_with_refs[year] += 1
            for ref in kept:
                by_year_group[year][ref["group"]] += 1
                by_year_frame[year][ref["frame"]] += 1
        per_post.append(
            {
                "slug": post["slug"],
                "url": post["url"],
                "title": post.get("title", ""),
                "date": post.get("date", ""),
                "fetched_at": post.get("fetched_at", ""),
                "refused": res["refused"],
                "refs": kept,
            }
        )

    out = {
        "case": case,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": GROUP_REF_MODEL,
        "prompt_version": prompt.get("version"),
        "n_posts": len(posts),
        "n_posts_with_refs": sum(posts_with_refs.values()),
        "n_refs": sum(sum(c.values()) for c in by_year_group.values()),
        "quote_check_failures": quote_failures,
        "taxonomy_failures": taxonomy_failures,
        "refusals": still_refused,
        "by_year_group": {y: dict(c) for y, c in sorted(by_year_group.items())},
        "by_year_frame": {y: dict(c) for y, c in sorted(by_year_frame.items())},
        "posts_with_refs_by_year": dict(sorted(posts_with_refs.items())),
        "posts": per_post,
    }
    path = company_dir(case) / "group_references.json"
    write_json(path, out)
    print(
        f"\n{out['n_refs']} references across {out['n_posts_with_refs']}/{len(posts)} posts"
        f" | quote-check failures: {quote_failures} | taxonomy failures: {taxonomy_failures}"
        f" | unresolved refusals: {len(still_refused)}"
    )
    if still_refused:
        print(f"  hand-code these: {still_refused}")
    print(f"Wrote {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    p.add_argument("--limit", type=int, default=None, help="smoke-test on first N posts")
    args = p.parse_args()
    main(args.case, args.limit)
