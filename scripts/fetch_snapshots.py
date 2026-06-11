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
import sys
from collections import Counter

import httpx

from lowork.config import company_dir
from lowork.io import read_json, write_json
from lowork.wayback import Capture, cdx_query, dedup_by_digest, fetch_capture, select_per_year


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
    header = "| Pattern | " + " | ".join(str(y)[2:] for y in all_years) + " |"
    sep = "|---" * (len(all_years) + 1) + "|"
    lines += [header, sep]
    for url, caps in results.items():
        counts = Counter(c.year for c in caps)
        lines.append(f"| {url} | " + " | ".join(str(counts.get(y, "")) for y in all_years) + " |")

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

    with httpx.Client(follow_redirects=True) as client:
        results = query_all_patterns(client, cfg["patterns"])
        all_caps = [c for caps in results.values() for c in caps]
        unique, digest_timeline = dedup_by_digest(all_caps)
        print(f"\n{len(all_caps)} captures, {len(unique)} unique by digest")

        selected = select_per_year(unique, per_year=per_year)
        n_selected = sum(len(v) for v in selected.values())
        print(f"Selected {n_selected} pattern captures across {len(selected)} years\n")

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
