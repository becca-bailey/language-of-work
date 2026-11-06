#!/usr/bin/env python
"""One-command corpus refresh.

Chains the capture and measurement steps that a manual refresh runs one by
one, with the one human gate (spot-checking new captures) kept explicit:

    uv run scripts/refresh.py                  # full refresh, pauses at the gate
    uv run scripts/refresh.py --capture-only   # discover+fetch+backup only (no API spend)
    uv run scripts/refresh.py --companies shopify stripe
    uv run scripts/refresh.py --dry-run        # show what fetch would select; write nothing
    uv run scripts/refresh.py --yes            # skip the spot-check pause (scheduled runs)

Steps: pull embedding cache -> discover+fetch per company -> [PAUSE: review
spotcheck_links.md] -> pipeline diff -> pipeline run -> validate --strict ->
push embedding cache + raw HTML to R2 -> summary.

API spend happens only inside `pipeline run` (classify/embed on new chunks);
capture is free. Companies without url_patterns.json are skipped; flock's
discover is skipped by profile rule (Wayback CDX 403s on the domain — manual
live capture is its route, see data/flock/url_patterns.json).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from lowork import pipeline as P
from lowork.config import company_dir

import fetch_snapshots

ROOT = Path(__file__).resolve().parent.parent
CACHE_SYNC = ROOT / "scripts" / "cache_sync.sh"

# Profile-rule skips for the Wayback path (manual capture only).
SKIP_DISCOVER = {"flock"}


def _capture_count(company: str) -> int:
    p = company_dir(company) / "snapshots.json"
    if not p.exists():
        return 0
    return len(json.loads(p.read_text()).get("captures", []))


def _sync(verb: str) -> None:
    try:
        subprocess.run([str(CACHE_SYNC), verb], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"WARN: cache_sync.sh {verb} failed ({e}) — continuing; run it by hand")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--companies", nargs="*", help="restrict to these companies")
    ap.add_argument("--per-year", type=int, default=4)
    ap.add_argument("--capture-only", action="store_true",
                    help="stop after capture + backup (no classify/embed spend)")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what fetch would select; write nothing")
    ap.add_argument("--yes", action="store_true",
                    help="skip the spot-check pause (for scheduled runs)")
    args = ap.parse_args()

    cfg = P.load_config()
    companies = args.companies or cfg.companies
    unknown = [c for c in companies if c not in cfg.companies]
    if unknown:
        ap.error(f"not in pipeline.yaml universe: {unknown}")

    if not args.dry_run:
        _sync("pull")

    # --- capture ------------------------------------------------------------
    before = {co: _capture_count(co) for co in companies}
    failures: list[str] = []
    for co in companies:
        if not (company_dir(co) / "url_patterns.json").exists():
            print(f"[skip] {co}: no url_patterns.json")
            continue
        if co in SKIP_DISCOVER:
            print(f"[skip] {co}: discover disabled by profile rule (manual capture only)")
            continue
        if not args.dry_run:  # discover writes discovery_report/signals
            print(f"\n=== {co}: discover ===")
            try:
                fetch_snapshots.cmd_discover(co)
            except Exception as e:  # CDX hiccups shouldn't kill the whole round
                print(f"FAILED discover {co}: {e}")
                failures.append(f"discover {co}")
                continue
        print(f"\n=== {co}: fetch ===")
        try:
            fetch_snapshots.cmd_fetch(co, args.per_year, dry_run=args.dry_run)
        except Exception as e:
            print(f"FAILED fetch {co}: {e}")
            failures.append(f"fetch {co}")

    added = {co: _capture_count(co) - before[co] for co in companies}
    touched = {co: n for co, n in added.items() if n > 0}
    print("\n=== capture summary ===")
    for co, n in sorted(touched.items()):
        print(f"  {co}: +{n} captures — review {company_dir(co) / 'spotcheck_links.md'}")
    if not touched:
        print("  no new captures")
    if failures:
        print(f"  FAILED: {', '.join(failures)} (re-run with --companies to retry)")

    if args.dry_run:
        return 0

    if not args.capture_only and touched and not args.yes:
        print("\nHuman gate: open the spotcheck files above, prune junk captures "
              "from snapshots.json, then continue.")
        input("Press Enter to continue to the pipeline run (Ctrl-C to stop here) ")

    if args.capture_only:
        _sync("push-raw")
        print("\nCapture-only round done. Next: review spotchecks, then "
              "`uv run scripts/pipeline.py run`.")
        return 0

    # --- measure ------------------------------------------------------------
    state = P.load_state()
    plan = P.evaluate(cfg, state)
    if plan:
        print(f"\n{len(plan)} stage(s) to run:")
        for step in plan:
            scope = "global" if step.stage.scope is P.Scope.GLOBAL else f"{len(step.companies)} co"
            print(f"  {step.stage.name:28} ({scope}) — {step.reason}")
    ran = P.run(cfg)
    print(f"\nRan {len(ran)} stage(s).")

    warnings = P.validate(cfg)
    for w in warnings:
        print(f"WARN: {w}")

    _sync("push")
    _sync("push-raw")

    figs = P.prose_figures()
    if figs:
        print("\nProse-sensitive figures (check against the published captions):")
        for k, v in figs.items():
            print(f"  {k}: {v}")
    print("\nDone. Review `git diff astro/src/data` and commit the exports.")
    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
