#!/usr/bin/env python
"""Corpus pipeline orchestrator.

After manually fetching new data (`fetch_snapshots.py`), run:

    uv run scripts/pipeline.py run        # detect changes, run stale stages
    uv run scripts/pipeline.py diff       # what would run, and why (no writes)
    uv run scripts/pipeline.py status     # coverage table + prose figures
    uv run scripts/pipeline.py validate   # coverage assertions (warn by default)
    uv run scripts/pipeline.py baseline   # mark current corpus clean (run once)

Stages and story membership are defined in src/lowork/pipeline.py + pipeline.yaml.
"""

from __future__ import annotations

import argparse
import sys

from lowork import pipeline as P


def cmd_run(args) -> int:
    cfg = P.load_config()
    state = P.load_state()
    changed = P.changed_companies(cfg, state)
    print(f"Enabled stories: {sorted(cfg.enabled)}")
    print(f"Detected new/changed data in: {changed or 'none'}")
    only = set(args.company) if args.company else None
    plan = P.run(cfg, only_companies=only, force=args.force)
    if not plan:
        print("Nothing to do — everything up to date.")
    else:
        print(f"\nRan {len(plan)} stage(s).")
        figs = P.prose_figures()
        if figs:
            print("\nProse-sensitive figures (check against the MDX stories):")
            for k, v in figs.items():
                print(f"  {k}: {v}")
    return 0


def cmd_diff(args) -> int:
    cfg = P.load_config()
    state = P.load_state()
    changed = P.changed_companies(cfg, state)
    print(f"Detected new/changed data in: {changed or 'none'}")
    only = set(args.company) if args.company else None
    plan = P.evaluate(cfg, state, only_companies=only)
    if not plan:
        print("Nothing stale — `run` would do nothing.")
        return 0
    print(f"\n{len(plan)} stage(s) would run:")
    for step in plan:
        scope = "global" if step.stage.scope is P.Scope.GLOBAL else f"{len(step.companies)} co"
        who = "" if step.stage.scope is P.Scope.GLOBAL else f" [{', '.join(step.companies)}]"
        print(f"  {step.stage.name:28} ({scope}) — {step.reason}{who}")
    return 0


def cmd_status(args) -> int:
    cfg = P.load_config()
    print(f"{'company':10} {'chunks':>7} {'classfd':>7} {'analysis':>8} "
          f"{'reg_miss':>8} {'stn_miss':>8} {'emb_miss':>8}")
    for co in cfg.companies:
        c = P.coverage(co)
        print(f"{co:10} {c['chunks']:>7} {c['classified']:>7} {c['analysis']:>8} "
              f"{c['register_missing']:>8} {c['stance_missing']:>8} {c['embed_missing']:>8}")
    figs = P.prose_figures()
    if figs:
        print("\nProse-sensitive figures (check against the MDX stories):")
        for k, v in figs.items():
            print(f"  {k}: {v}")
    return 0


def cmd_validate(args) -> int:
    cfg = P.load_config()
    warnings = P.validate(cfg)
    if not warnings:
        print("OK — no coverage gaps.")
        return 0
    for w in warnings:
        print(f"WARN: {w}")
    if args.strict:
        print(f"\n{len(warnings)} issue(s); exiting non-zero (--strict).")
        return 1
    print(f"\n{len(warnings)} issue(s) (warn-only; pass --strict to fail).")
    return 0


def cmd_baseline(args) -> int:
    cfg = P.load_config()
    n = P.record_baseline(cfg)
    print(f"Recorded baseline for {n} stage entries — `run` is now incremental.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="run stale stages for enabled stories")
    p_run.add_argument("--company", action="append", help="restrict to this company (repeatable)")
    p_run.add_argument("--force", action="store_true", help="ignore fingerprints; run everything")
    p_run.set_defaults(func=cmd_run)

    p_diff = sub.add_parser("diff", help="show what would run, and why")
    p_diff.add_argument("--company", action="append")
    p_diff.set_defaults(func=cmd_diff)

    p_status = sub.add_parser("status", help="coverage table + prose figures")
    p_status.set_defaults(func=cmd_status)

    p_val = sub.add_parser("validate", help="coverage assertions")
    p_val.add_argument("--strict", action="store_true", help="exit non-zero on any issue")
    p_val.set_defaults(func=cmd_validate)

    p_base = sub.add_parser("baseline", help="mark current corpus clean (run once on adoption)")
    p_base.set_defaults(func=cmd_baseline)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
