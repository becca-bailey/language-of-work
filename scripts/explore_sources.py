#!/usr/bin/env python
"""Phase 1a: fan out over every registered source and write a per-case census.

Wide, shallow, capped — answers "does enough text exist, in each register,
across the relevant years?" not "fetch it all." Writes data/<case>/source_map.md.

Usage: uv run scripts/explore_sources.py --case menlo [--limit 20]
"""

from __future__ import annotations

import argparse

import httpx

from lowork.config import company_dir
from lowork.io import read_json, write_json
from lowork.sources import base


def load_cfg(case: str) -> dict:
    cfg = read_json(company_dir(case) / "sources.json")
    cfg.setdefault("case", case)
    return cfg


def explore_case(case: str, limit: int) -> dict:
    cfg = load_cfg(case)
    reg = base.registry()
    out: dict[str, list] = {}
    with httpx.Client(follow_redirects=True, headers={"User-Agent": "language-of-work/research"}) as client:
        for name, mod in reg.items():
            print(f"[{case}] exploring {name} ({mod.REGISTER}) ...")
            try:
                results = mod.explore(cfg, client, limit=limit)
            except Exception as e:  # one flaky source must not sink the census
                print(f"  ! {name} failed: {e}")
                out[name] = [
                    base.ExploreResult(source=name, register=mod.REGISTER, query="", total=None, note=f"ERROR: {e}")
                ]
                continue
            for r in results:
                print(f"  {name} q={r.query!r}: total={r.total} dates={r.date_min}..{r.date_max} samples={len(r.samples)}")
            out[name] = results
    return cfg, out


def write_map(case: str, cfg: dict, out: dict) -> None:
    cdir = company_dir(case)
    lines = [
        f"# Source map: {cfg.get('display_name', case)}",
        "",
        "Phase 1a wide-exploration census (capped). Counts/date-ranges per source by register.",
        "",
        "> Caveat: HN Algolia `nbHits` overcounts (loose token / OR matching), and Open Library",
        "> date ranges include off-topic hits. Trust the ranked **samples**, not raw totals, as the",
        "> viability signal. Empty press/legal rows are tooling gaps (news.py/courts.py unbuilt),",
        "> not data gaps.",
        "",
        "| Source | Register | Query | Total hits | Date range | Samples |",
        "|---|---|---|---|---|---|",
    ]
    by_register: dict[str, list] = {}
    for name, results in out.items():
        for r in results:
            by_register.setdefault(r.register, []).append(r)
            rng = f"{r.date_min}..{r.date_max}" if r.date_min else "—"
            total = r.total if r.total is not None else "?"
            note = f" — {r.note}" if r.note else ""
            lines.append(f"| {name} | {r.register} | `{r.query}` | {total} | {rng} | {len(r.samples)}{note} |")

    lines += ["", "## Register coverage (viability gate)", ""]
    for register in base.REGISTERS:
        rs = by_register.get(register, [])
        tot = sum((r.total or 0) for r in rs)
        lines.append(f"- **{register}**: {len(rs)} source-queries, ~{tot} total hits")

    lines += ["", "## Samples", ""]
    for name, results in out.items():
        for r in results:
            if not r.samples:
                continue
            lines.append(f"### {name} — `{r.query}` ({r.register})")
            for s in r.samples[:8]:
                title = s.get("title") or "(untitled)"
                lines.append(f"- **{s.get('date','')}** [{title}]({s.get('url','')})")
                if s.get("snippet"):
                    lines.append(f"  > {s['snippet']}")
            lines.append("")

    (cdir / "source_map.md").write_text("\n".join(lines) + "\n")
    # Also persist the raw census for downstream selection.
    write_json(cdir / "source_census.json", {name: [vars(r) for r in rs] for name, rs in out.items()})
    print(f"\nWrote {cdir / 'source_map.md'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()
    cfg, out = explore_case(args.case, args.limit)
    write_map(args.case, cfg, out)


if __name__ == "__main__":
    main()
