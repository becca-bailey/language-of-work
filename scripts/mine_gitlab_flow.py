#!/usr/bin/env python
"""Mine the GitLab handbook git history for a well-being benefit's event timeline.

The GitLab flow instrument (plan §GitLab flow data). A benefit page's history is NOT
followable with `git log --follow`: it crosses slug changes, section moves, directory
reorgs, and the 2023 repo migration (verified Phase 0.2 / Phase 2). So we stitch: collect
commits matching ANY of the page's historical path patterns from the pre-migration
www-gitlab-com clone, merge with the post-migration handbook repo's commits (via API),
dedup by commit sha, sort by date, and classify a coarse change_type from the subject.

Pilot target: Family & Friends Day. Its lineage (discovered Phase 2):
  source/handbook/ceo/family-friends-day/            (2020-04 creation, pre 2020-06 reorg)
  sites/handbook/source/handbook/ceo/family-friends-day/
  sites/marketing/source/company/family-and-friends-day/
  sites/uncategorized/source/company/family-and-friends-day/   (2021-05 →)
  [handbook repo] content/handbook/company/family-and-friends-day.md   (2023-08 →)

Writes data/gitlab/wellbeing_flow.jsonl (one row per commit).
Usage: python scripts/mine_gitlab_flow.py --repo /path/to/www-gitlab-com/clone
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess

import httpx

from lowork.config import company_dir

# Any historical path fragment of the page in www-gitlab-com. Globbed as pathspecs.
WGC_PATHSPECS = [
    "*/ceo/family-friends-day/*",
    "*/company/family-and-friends-day/*",
    "*pandemic-support-day*",
]
# Post-migration: handbook repo (project id resolved Phase 0.2) + file path.
HANDBOOK_PROJECT = "42817607"
HANDBOOK_PATH = "content/handbook/company/family-and-friends-day.md"

# Coarse change_type from the commit subject (ordered — first match wins).
CHANGE_RULES = [
    ("remove", r"\bremov|delet|deprecat|retir|sunset|discontinu"),
    ("add", r"\badd|introduc|creat|launch|propos|new\b"),
    ("expand", r"\bexpand|extend|increas|permanent|additional|more\b"),
    ("restrict", r"\brestrict|reduc|limit|paus|cancel|fewer|scale back"),
    ("reframe", r"\brename|renam|move|reorganiz|reword|clarif|format|typo|link"),
]


def classify(subject: str) -> str:
    s = subject.lower()
    for label, pat in CHANGE_RULES:
        if re.search(pat, s):
            return label
    return "update"


def mine_wgc(repo: str) -> list[dict]:
    fmt = "%H%x1f%ad%x1f%s"
    cmd = ["git", "-C", repo, "log", "--all", "--date=short", f"--format={fmt}",
           "--", *WGC_PATHSPECS]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=180).stdout
    rows = []
    for line in out.splitlines():
        if not line.strip():
            continue
        sha, date, subj = line.split("\x1f", 2)
        rows.append({"sha": sha, "date": date, "subject": subj, "repo": "www-gitlab-com"})
    return rows


def mine_handbook_api() -> list[dict]:
    url = f"https://gitlab.com/api/v4/projects/{HANDBOOK_PROJECT}/repository/commits"
    rows, page = [], 1
    while True:
        r = httpx.get(url, params={"path": HANDBOOK_PATH, "per_page": 100, "page": page},
                      timeout=30)
        if r.status_code != 200 or not r.json():
            break
        for c in r.json():
            rows.append({"sha": c["id"], "date": c["created_at"][:10],
                         "subject": c["title"], "repo": "handbook"})
        if len(r.json()) < 100:
            break
        page += 1
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, help="path to a www-gitlab-com clone")
    ap.add_argument("--no-api", action="store_true", help="skip the handbook-repo API pull")
    args = ap.parse_args()

    rows = mine_wgc(args.repo)
    print(f"www-gitlab-com: {len(rows)} commits across {len(WGC_PATHSPECS)} path patterns")
    if not args.no_api:
        hb = mine_handbook_api()
        print(f"handbook repo (API): {len(hb)} commits")
        rows += hb

    # dedup by sha, sort by date
    seen, uniq = set(), []
    for r in sorted(rows, key=lambda x: x["date"]):
        if r["sha"] in seen:
            continue
        seen.add(r["sha"])
        r["change_type"] = classify(r["subject"])
        uniq.append(r)

    out = company_dir("gitlab") / "wellbeing_flow.jsonl"
    with out.open("w") as f:
        for r in uniq:
            f.write(json.dumps(r) + "\n")
    print(f"{len(uniq)} unique commits -> {out}")
    if uniq:
        print(f"span: {uniq[0]['date']} .. {uniq[-1]['date']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
