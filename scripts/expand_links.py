#!/usr/bin/env python
"""Track A: one-hop link expansion from archived careers pages.

Subcommands:
  discover  Harvest same-domain content links from stored HTML, resolve via
            CDX to captures near parent timestamps -> expansion_discovery.json
            + expansion_report.md (manual gate M8)
  fetch     Download approved expansion captures (all entries in discovery file
            unless --only-approved and an approval list exists)
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter

import httpx

from lowork.company import CompanyProfile
from lowork.config import company_dir
from lowork.io import read_json, write_json
from lowork.links import harvest_from_manifest
from lowork.wayback import Capture, cdx_query, fetch_capture, html_path


def nearest_capture(client: httpx.Client, url: str, target_ts: str) -> Capture | None:
    """CDX lookup for exact URL; pick capture closest to target_ts."""
    caps = cdx_query(
        client,
        url.replace("https://", "").replace("http://", ""),
        match_type="exact",
        collapse=None,
        filters=["statuscode:200", "mimetype:text/html"],
    )
    if not caps:
        # try with trailing slash variant
        alt = url if url.endswith("/") else url + "/"
        caps = cdx_query(
            client,
            alt.replace("https://", "").replace("http://", ""),
            match_type="exact",
            collapse=None,
            filters=["statuscode:200"],
        )
    if not caps:
        return None
    return min(caps, key=lambda c: abs(int(c.timestamp) - int(target_ts)))


def existing_urls(manifest: dict) -> set[str]:
    return {c["original"] for c in manifest.get("captures", [])}


def existing_digests(manifest: dict) -> set[str]:
    return {c["digest"] for c in manifest.get("captures", []) if "digest" in c}


def cmd_discover(company: str, cap_per_page: int) -> None:
    profile = CompanyProfile.load(company)
    cdir = company_dir(company)
    manifest = read_json(cdir / "snapshots.json")
    raw_dir = cdir / "raw_html"
    hosts = tuple(profile.hosts)
    harvested = harvest_from_manifest(
        raw_dir, manifest["captures"], hosts=hosts, cap_per_page=cap_per_page
    )
    print(f"Harvested {len(harvested)} unique content URLs from {len(manifest['captures'])} captures")

    already = existing_urls(manifest)
    entries = []
    with httpx.Client(follow_redirects=True) as client:
        for url, parents in sorted(harvested.items()):
            if url in already or any(p["parent_url"] in url for p in parents):
                # skip if already in manifest or self-referential
                if url in already:
                    entries.append({"url": url, "status": "already_fetched", "parents": parents})
                continue
            # use earliest parent timestamp as anchor
            parent = min(parents, key=lambda p: p["parent_timestamp"])
            cap = nearest_capture(client, url, parent["parent_timestamp"])
            if cap is None:
                entries.append({"url": url, "status": "no_cdx", "parents": parents})
                print(f"  no CDX: {url}")
                continue
            entries.append(
                {
                    "url": url,
                    "status": "candidate",
                    "parents": parents,
                    "capture": cap.to_dict(),
                }
            )
            print(f"  candidate: {url} -> {cap.timestamp}")

    candidates = [e for e in entries if e["status"] == "candidate"]
    write_json(cdir / "expansion_discovery.json", {"company": company, "entries": entries})

    lines = [
        f"# Link expansion discovery: {company}",
        "",
        f"Harvested **{len(harvested)}** unique URLs; **{len(candidates)}** new CDX candidates.",
        "Review before fetch (manual step M8). Run `expand_links.py fetch` to download.",
        "",
        "## Summary",
        "",
        f"- Already in manifest: {sum(1 for e in entries if e['status'] == 'already_fetched')}",
        f"- No CDX match: {sum(1 for e in entries if e['status'] == 'no_cdx')}",
        f"- New candidates: {len(candidates)}",
        "",
        "## Candidates by year",
        "",
    ]
    by_year = Counter(e["capture"]["timestamp"][:4] for e in candidates)
    for year, n in sorted(by_year.items()):
        lines.append(f"- {year}: {n}")
    lines += ["", "## Candidate URLs", ""]
    for e in candidates:
        cap = e["capture"]
        lines.append(f"- [{cap['timestamp']}] {e['url']}")
    (cdir / "expansion_report.md").write_text("\n".join(lines) + "\n")
    print(f"\nWrote {cdir / 'expansion_discovery.json'} and expansion_report.md")


def cmd_fetch(company: str) -> None:
    cdir = company_dir(company)
    manifest = read_json(cdir / "snapshots.json")
    discovery = read_json(cdir / "expansion_discovery.json")
    raw_dir = cdir / "raw_html"
    raw_dir.mkdir(exist_ok=True)
    digests = existing_digests(manifest)
    urls = existing_urls(manifest)

    candidates = [e for e in discovery["entries"] if e["status"] == "candidate"]
    print(f"Fetching {len(candidates)} expansion candidates")

    added = 0
    with httpx.Client(follow_redirects=True) as client:
        for e in candidates:
            cap = Capture(**e["capture"])
            if cap.original in urls or cap.digest in digests:
                print(f"  skip dup {cap.original}")
                continue
            try:
                path, nbytes = fetch_capture(client, cap, raw_dir)
            except RuntimeError as err:
                print(f"  FAILED {cap.original}: {err}")
                manifest["captures"].append({**cap.to_dict(), "fetch_error": str(err)})
                continue
            rec = {**cap.to_dict(), "html_file": path.name, "source": "link_expansion"}
            manifest["captures"].append(rec)
            urls.add(cap.original)
            digests.add(cap.digest)
            added += 1
            print(f"  {cap.timestamp} {cap.original} ({nbytes or 'cached'} bytes)")

    write_json(cdir / "snapshots.json", manifest)
    print(f"Added {added} expansion captures to manifest")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["discover", "fetch"])
    parser.add_argument("--company", default="google")
    parser.add_argument("--cap-per-page", type=int, default=10)
    args = parser.parse_args()
    if args.command == "discover":
        cmd_discover(args.company, args.cap_per_page)
    else:
        cmd_fetch(args.company)
    sys.exit(0)
