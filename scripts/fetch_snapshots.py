#!/usr/bin/env python
"""Step 1: query the Wayback CDX API and download raw careers-page HTML.

Subcommands:
  discover  CDX capture counts per pattern/year -> data/<company>/discovery_report.md
            (input to manual step M1; no downloads)
  fetch     Select 3-4 captures/year, download raw HTML via id_ URLs, write
            snapshots.json manifest and spotcheck_links.md (manual step M2)
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter

import httpx

from lowork.chunking import chunk_html
from lowork.config import company_dir
from lowork.io import read_json, write_json
from lowork.wayback import (
    Capture,
    cdx_query,
    dedup_by_digest,
    fetch_capture,
    fetch_raw_text,
    select_per_year,
)

# Below this many DOM-extracted words, a sample is a nav/boilerplate shell.
# We measure with structure-aware chunk_html, NOT trafilatura: trafilatura
# recovers the ~156-word EEO boilerplate even on empty SPA shells, which would
# mask them as content. chunk_html skips that div-based boilerplate, so a real
# server-rendered page scores well above this floor and a shell scores ~0.
SHELL_WORD_THRESHOLD = 50


def _sample_captures(caps: list[Capture], k: int = 3) -> list[Capture]:
    """Earliest / median / latest captures — content presence varies by era
    within one pattern (a path can be a live page in some years, a redirect
    shell in others), so a single sample misclassifies. Dedup when < k exist."""
    ordered = sorted(caps, key=lambda c: c.timestamp)
    if len(ordered) <= k:
        return ordered
    idxs = sorted({0, len(ordered) // 2, len(ordered) - 1})
    return [ordered[i] for i in idxs]


def probe_content_signal(
    client: httpx.Client, caps: list[Capture]
) -> dict | None:
    """Sample a few captures across a pattern's eras and measure real prose.

    Returns {words, samples, shell} where `words` is the best DOM-extracted
    word count seen — a pattern is a shell only if *every* sampled era is one.
    None if nothing was fetchable.
    """
    samples: list[dict] = []
    for cap in _sample_captures(caps):
        html = fetch_raw_text(client, cap)
        if html is None:
            continue
        dom_words = sum(c["word_count"] for c in chunk_html(
            html, source_url=cap.original, timestamp=cap.timestamp))
        samples.append({"timestamp": cap.timestamp, "words": dom_words})
    if not samples:
        return None
    best = max(s["words"] for s in samples)
    return {"words": best, "samples": samples, "shell": best < SHELL_WORD_THRESHOLD}


def load_patterns(company: str) -> dict:
    return read_json(company_dir(company) / "url_patterns.json")


def query_all_patterns(client: httpx.Client, patterns: list[dict]) -> dict[str, list[Capture]]:
    results: dict[str, list[Capture]] = {}
    for pat in patterns:
        print(f"CDX query: {pat['url']} ({pat['match_type']})")
        caps = cdx_query(client, pat["url"], match_type=pat["match_type"])
        print(f"  {len(caps)} captures")
        results[pat["url"]] = caps
    return results


def cmd_discover(company: str) -> None:
    cfg = load_patterns(company)
    out_path = company_dir(company) / "discovery_report.md"
    lines = [
        f"# CDX discovery report: {company}",
        "",
        "Captures per pattern per year (status 200, ~monthly collapse).",
        "Use this during manual step M1 to confirm/extend `url_patterns.json`.",
        "",
    ]
    with httpx.Client(follow_redirects=True) as client:
        results = query_all_patterns(client, cfg["patterns"])

        all_years = sorted({c.year for caps in results.values() for c in caps})
        if not all_years:
            print("No captures found for any pattern.")
            return

        # Content probe: one representative sample per pattern, to tell
        # content-bearing paths from SPA/nav shells before we bulk-fetch.
        print("\nProbing content signal (earliest/median/latest per pattern)...")
        signals: dict[str, dict] = {}
        for url, caps in results.items():
            if not caps:
                continue
            sig = probe_content_signal(client, caps)
            if sig is None:
                continue
            signals[url] = sig
            tag = "SHELL" if sig["shell"] else "content"
            eras = ",".join(f"{s['timestamp'][:6]}:{s['words']}w" for s in sig["samples"])
            print(f"  {url}: best {sig['words']}w [{tag}]  ({eras})")
        write_json(company_dir(company) / "discovery_signals.json", signals)

    header = "| Pattern | signal | " + " | ".join(str(y)[2:] for y in all_years) + " |"
    sep = "|---" * (len(all_years) + 2) + "|"
    lines += [header, sep]
    for url, caps in results.items():
        counts = Counter(c.year for c in caps)
        sig = signals.get(url)
        if sig is None:
            cell = "—"
        else:
            cell = f"{sig['words']}w" + (" ⚠shell" if sig["shell"] else "")
        lines.append(
            f"| {url} | {cell} | "
            + " | ".join(str(counts.get(y, "")) for y in all_years) + " |"
        )

    shells = [u for u, s in signals.items() if s["shell"]]
    if shells:
        lines += ["", "## Shell patterns (skipped by fetch)", "",
                  "Sample extracted < %d words — SPA/nav shell, no archived prose:"
                  % SHELL_WORD_THRESHOLD, ""]
        lines += [f"- {u}" for u in shells]

    lines += ["", "## Gaps to investigate", ""]
    year_totals = Counter()
    for caps in results.values():
        year_totals.update({c.year for c in caps})
    expected = range(2005, max(all_years) + 1)
    gaps = [y for y in expected if year_totals.get(y, 0) == 0]
    lines.append(
        f"Years with no coverage from any pattern: {gaps or 'none'}"
    )

    out_path.write_text("\n".join(lines) + "\n")
    print(f"\nWrote {out_path}")


def _existing_keys(manifest: dict) -> tuple[set[tuple[str, str]], set[str]]:
    """Return (url, timestamp) pairs and digests already in the manifest."""
    capture_keys: set[tuple[str, str]] = set()
    digests: set[str] = set()
    for cap in manifest.get("captures", []):
        capture_keys.add((cap["original"], cap["timestamp"]))
        if "digest" in cap:
            digests.add(cap["digest"])
    return capture_keys, digests


def cmd_fetch(company: str, per_year: int) -> None:
    cfg = load_patterns(company)
    cdir = company_dir(company)
    raw_dir = cdir / "raw_html"
    raw_dir.mkdir(exist_ok=True)

    manifest_path = cdir / "snapshots.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        print(f"Merging into existing manifest ({len(manifest.get('captures', []))} captures)")
    else:
        manifest = {"company": company, "captures": []}

    existing_keys, existing_digests = _existing_keys(manifest)
    added = 0

    # Content signals from `discover`; skip patterns probed as pure shells.
    sig_path = cdir / "discovery_signals.json"
    signals = read_json(sig_path) if sig_path.exists() else {}
    if not signals:
        print("No discovery_signals.json — run `discover` first to skip shell "
              "patterns; fetching all patterns this run.")

    with httpx.Client(follow_redirects=True) as client:
        results = query_all_patterns(client, cfg["patterns"])
        all_caps = [c for caps in results.values() for c in caps]
        _, digest_timeline = dedup_by_digest(all_caps)

        # Select per-pattern-per-year so content-bearing subpaths each get their
        # own quota instead of being crowded out by the high-volume root page.
        # Dedup by digest across patterns so identical content isn't re-fetched.
        # Optional per-pattern min_year/max_year bound the selection window —
        # for domains whose early captures predate the company (e.g. uber.com
        # before Uber acquired it), era_hint alone is documentation. Optional
        # exclude_url regex drops captures by URL — for locale subpaths under a
        # shared host (e.g. apple.com/careers/de/), which CDX prefix matching
        # cannot express as an include-list.
        bounds = {
            p["url"]: (p.get("min_year"), p.get("max_year"))
            for p in cfg["patterns"]
        }
        excludes = {
            p["url"]: re.compile(p["exclude_url"])
            for p in cfg["patterns"] if p.get("exclude_url")
        }
        seen_digests: set[str] = set()
        selected: dict[int, list[Capture]] = {}
        for url, caps in results.items():
            if signals.get(url, {}).get("shell"):
                print(f"  skip shell pattern {url}")
                continue
            lo, hi = bounds.get(url, (None, None))
            if lo or hi:
                before = len(caps)
                caps = [c for c in caps
                        if (lo is None or c.year >= lo) and (hi is None or c.year <= hi)]
                if len(caps) != before:
                    print(f"  {url}: year bounds dropped {before - len(caps)} captures")
            if url in excludes:
                before = len(caps)
                caps = [c for c in caps if not excludes[url].search(c.original)]
                if len(caps) != before:
                    print(f"  {url}: exclude_url dropped {before - len(caps)} captures")
            unique, _ = dedup_by_digest(caps)
            unique = [c for c in unique if c.digest not in seen_digests]
            for year, chosen in select_per_year(unique, per_year=per_year).items():
                for cap in chosen:
                    if cap.digest in seen_digests:
                        continue
                    seen_digests.add(cap.digest)
                    selected.setdefault(year, []).append(cap)
        for year in selected:
            selected[year].sort(key=lambda c: c.timestamp)
        n_selected = sum(len(v) for v in selected.values())
        print(f"\nSelected {n_selected} captures across {len(selected)} years "
              f"(per-pattern, {len(seen_digests)} unique digests)\n")

        spotcheck = [f"# M2 spot-check links: {company}", "",
                     "Open a sample across eras; confirm real careers content.", ""]
        for year, caps in sorted(selected.items()):
            spotcheck.append(f"## {year}")
            for cap in caps:
                key = (cap.original, cap.timestamp)
                if key in existing_keys:
                    print(f"  skip dup {cap.timestamp} {cap.original}")
                    continue
                if cap.digest in existing_digests:
                    print(f"  skip digest {cap.timestamp} {cap.original}")
                    continue
                try:
                    path, nbytes = fetch_capture(client, cap, raw_dir)
                    status = "cached" if nbytes == 0 else f"{nbytes} bytes"
                except RuntimeError as e:
                    print(f"  FAILED {cap.timestamp} {cap.original}: {e}")
                    manifest["captures"].append({**cap.to_dict(), "fetch_error": str(e)})
                    continue
                print(f"  {cap.timestamp} {cap.original} ({status})")
                rec = {**cap.to_dict(), "html_file": path.name, "source": "pattern_fetch"}
                manifest["captures"].append(rec)
                existing_keys.add(key)
                existing_digests.add(cap.digest)
                added += 1
                spotcheck.append(f"- [{cap.timestamp} — {cap.original}]({cap.replay_url})")
            spotcheck.append("")

        # SPA-era JSON probes: surface candidates for manual review, don't download
        json_candidates = []
        for probe in cfg.get("spa_json_probes", []):
            caps = cdx_query(
                client, probe["url"], match_type=probe["match_type"],
                filters=["statuscode:200", "mimetype:application/json"],
            )
            json_candidates.extend(c.to_dict() for c in caps)
        manifest["json_candidates"] = json_candidates
        manifest["digest_timeline"] = digest_timeline
        print(f"\nSPA JSON candidates found: {len(json_candidates)}")
        print(f"Added {added} new pattern captures (total {len(manifest['captures'])})")

    write_json(manifest_path, manifest)
    (cdir / "spotcheck_links.md").write_text("\n".join(spotcheck) + "\n")
    print(f"Wrote {cdir / 'snapshots.json'} and {cdir / 'spotcheck_links.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["discover", "fetch"])
    parser.add_argument("--company", default="google")
    parser.add_argument("--per-year", type=int, default=4)
    args = parser.parse_args()
    if args.command == "discover":
        cmd_discover(args.company)
    else:
        cmd_fetch(args.company, args.per_year)
    sys.exit(0)
