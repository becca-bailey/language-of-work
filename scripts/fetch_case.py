#!/usr/bin/env python
"""Phase 1b: run the chosen source fetchers for real and converge into chunks.

Each fetcher yields SourceRecords; we take their to_chunk() output, group by
year, dedup, and write data/<case>/chunks/{year}.jsonl — the *same* files
extract_chunks.py produces from Wayback HTML — so classify/embed/score run
unchanged regardless of where the text came from (plan §0, "diverge at fetch,
converge at chunk"). Also writes corpus_manifest.json: per-source counts,
register/subtype breakdown, and date coverage (the Phase-1b manifest §1b wants).

Merge-by-source: each run freshly pulls the sources you name and *replaces* their
prior chunks, while preserving chunks from sources not in this run. So fetchers can
be run incrementally — `--sources hn,books` then later `--sources wayback` — and
re-running a source after a fix cleans out its old chunks (empty year files are
deleted, not orphaned).

Usage:
  uv run scripts/fetch_case.py --case automattic --sources hn,books,reddit
  uv run scripts/fetch_case.py --case automattic --sources hn,books
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone

import httpx

from lowork.chunking import dedup_chunks
from lowork.config import company_dir
from lowork.io import read_json, read_jsonl, write_json, write_jsonl
from lowork.sources import base
from lowork.sources.reddit import RedditAuthError


def load_cfg(case: str) -> dict:
    cfg = read_json(company_dir(case) / "sources.json")
    cfg.setdefault("case", case)
    return cfg


def fetch_case(case: str, sources: list[str], client: httpx.Client) -> dict:
    cfg = load_cfg(case)
    reg = base.registry()
    requested = [s.strip() for s in sources if s.strip()]
    unknown = [s for s in requested if s not in reg]
    if unknown:
        raise SystemExit(f"unknown source(s): {unknown}; registered: {sorted(reg)}")

    by_year: dict[int, list[dict]] = defaultdict(list)
    per_source: dict[str, dict] = {}
    undated_total = 0

    for name in requested:
        mod = reg[name]
        print(f"[{case}] fetching {name} ({mod.REGISTER}) ...")
        n_kept = n_undated = 0
        subtypes: Counter = Counter()
        years: list[int] = []
        try:
            for rec in mod.fetch(cfg, client):
                if rec.year is None:  # no resolvable date can't sit on the timeline
                    n_undated += 1
                    continue
                by_year[rec.year].append(rec.to_chunk())
                n_kept += 1
                subtypes[rec.subtype or "—"] += 1
                years.append(rec.year)
        except RedditAuthError as e:  # missing creds: skip cleanly, don't sink the run
            print(f"  ! {name} skipped (no creds): {e}")
            per_source[name] = {"register": mod.REGISTER, "status": "skipped", "reason": str(e), "records": 0}
            continue
        except Exception as e:  # one flaky source must not sink the corpus
            print(f"  ! {name} failed: {e}")
            per_source[name] = {"register": mod.REGISTER, "status": "error", "reason": str(e), "records": n_kept}
            continue

        undated_total += n_undated
        span = f"{min(years)}..{max(years)}" if years else "—"
        print(f"  {n_kept} records kept ({n_undated} undated dropped), {span}")
        per_source[name] = {
            "register": mod.REGISTER,
            "status": "ok",
            "records": n_kept,
            "undated_dropped": n_undated,
            "subtypes": dict(subtypes),
            "year_min": min(years) if years else None,
            "year_max": max(years) if years else None,
        }

    # Merge-by-source: a run replaces only the sources it pulled and preserves
    # chunks from sources not in this run, so fetchers can be run incrementally
    # (e.g. canon via wayback after hn/books). Year files that end up empty —
    # e.g. a fix removed a junk hit's only chunk — are deleted, not orphaned.
    # Only *completed* sources destructively replace their prior chunks. A source
    # that errored or was skipped mid-stream (e.g. archive.org throttling) keeps
    # its existing on-disk chunks — a partial fetch must never delete good prior
    # data — while any partial chunks it did yield are added and deduped, so a
    # retry is additive, not destructive.
    cdir = company_dir(case)
    chunks_dir = cdir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    replace_set = {name for name, info in per_source.items() if info.get("status") == "ok"}
    incomplete = [name for name in requested if name not in replace_set]
    if incomplete:
        print(f"  note: {incomplete} did not complete — preserving their prior chunks (additive merge)")
    existing_years = {int(p.stem) for p in chunks_dir.glob("*.jsonl") if p.stem.isdigit()}

    total = 0
    reg_counts: Counter = Counter()
    sub_counts: Counter = Counter()
    for year in sorted(existing_years | set(by_year)):
        path = chunks_dir / f"{year}.jsonl"
        preserved = [
            c for c in (read_jsonl(path) if path.exists() else [])
            if c.get("extraction_source") not in replace_set
        ]
        merged = preserved + by_year.get(year, [])
        if not merged:
            path.unlink(missing_ok=True)  # stale year, no chunks survive
            print(f"{year}: removed (no chunks)")
            continue
        unique = dedup_chunks(merged)
        total += write_jsonl(path, unique)
        for c in unique:
            reg_counts[c["register"]] += 1
            sub_counts[c.get("subtype") or "—"] += 1
        dropped = len(merged) - len(unique)
        note = f" ({dropped} near-dups dropped)" if dropped else ""
        print(f"{year}: {len(unique)} unique chunks{note}")

    manifest = {
        "case": case,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources_requested": requested,
        "per_source": per_source,
        "register_counts": dict(reg_counts),
        "subtype_counts": dict(sub_counts),
        "total_chunks": total,
        "year_span": (
            [min(final_years), max(final_years)]
            if (final_years := {int(p.stem) for p in chunks_dir.glob("*.jsonl") if p.stem.isdigit()})
            else None
        ),
        "undated_dropped": undated_total,
        "caveats": [
            "Worker-register text (hn/reddit) is community discussion-about (subtype=community), "
            "not verified first-person testimony — weight downstream, never a point estimate.",
            "Firm register spans book metadata (codification dates), longitudinal canon snapshots "
            "(wayback), and the live present-day canon (live); tag the canon subset before drift analysis.",
            "Counts/spans reflect the full on-disk corpus (merge-by-source), not just this run.",
            "Undated records (no resolvable year) are dropped from the timeline; see undated_dropped.",
        ],
    }
    write_json(cdir / "corpus_manifest.json", manifest)
    print(f"\nTotal: {total} chunks across {len(by_year)} years.")
    print(f"Registers: {dict(reg_counts)}")
    print(f"Manifest: {cdir / 'corpus_manifest.json'}")
    return manifest


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", required=True)
    p.add_argument("--sources", default="hn,books", help="comma-separated registered source names")
    args = p.parse_args()
    with httpx.Client(
        follow_redirects=True, headers={"User-Agent": "language-of-work/research"}
    ) as client:
        fetch_case(args.case, args.sources.split(","), client)


if __name__ == "__main__":
    main()
