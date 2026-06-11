#!/usr/bin/env python
"""Track B: SPA-era recovery and alternate-domain probing.

Subcommands:
  deep-sample   B1: dense CDX query for careers.google.com content pages
                2018-2022, fetch up to N/year, keep by extraction coverage
  sample-json   B2: fetch ~10 archived JSON API responses, write samples for review
  probe-domains B3: CDX-probe alternate mission-bearing domains
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter

import httpx

from lowork.chunking import chunk_html, coverage_stats
from lowork.company import CompanyProfile
from lowork.config import company_dir
from lowork.io import read_json, write_json
from lowork.wayback import Capture, cdx_query, dedup_by_digest, fetch_capture, select_per_year

MIN_DOM_WORDS = 80  # coverage threshold for rendered captures


def manifest_sets(manifest: dict) -> tuple[set[tuple[str, str]], set[str]]:
    keys: set[tuple[str, str]] = set()
    digests: set[str] = set()
    for c in manifest.get("captures", []):
        keys.add((c["original"], c["timestamp"]))
        if "digest" in c:
            digests.add(c["digest"])
    return keys, digests


def cmd_deep_sample(company: str, per_year: int, from_year: int, to_year: int) -> None:
    profile = CompanyProfile.load(company)
    content_paths = profile.spa_content_paths
    if not content_paths:
        print(f"No spa_content_paths in profile for {company}; skipping deep-sample")
        return

    cdir = company_dir(company)
    manifest = read_json(cdir / "snapshots.json")
    raw_dir = cdir / "raw_html"
    urls, digests = manifest_sets(manifest)

    added = 0
    kept = []
    with httpx.Client(follow_redirects=True) as client:
        for path in content_paths:
            print(f"CDX (no collapse): {path}")
            caps = cdx_query(
                client, path, match_type="exact", collapse=None,
                from_ts=str(from_year), to_ts=str(to_year + 1),
            )
            by_year: dict[int, list[Capture]] = {}
            for cap in caps:
                by_year.setdefault(cap.year, []).append(cap)
            for year, year_caps in sorted(by_year.items()):
                pool = sorted(year_caps, key=lambda c: c.timestamp)
                if len(pool) > per_year:
                    step = max(1, len(pool) // per_year)
                    pool = pool[::step][:per_year]
                for cap in pool:
                    if (cap.original, cap.timestamp) in urls or cap.digest in digests:
                        continue
                    try:
                        path_obj, nbytes = fetch_capture(client, cap, raw_dir)
                        html = path_obj.read_bytes()
                        chunks = chunk_html(html, source_url=cap.original, timestamp=cap.timestamp)
                        stats = coverage_stats(chunks, html)
                    except RuntimeError as err:
                        print(f"  skip {cap.timestamp}: {err}")
                        continue
                    if stats["dom_words"] < MIN_DOM_WORDS:
                        print(f"  thin {cap.timestamp} {cap.original}: {stats['dom_words']} words")
                        path_obj.unlink(missing_ok=True)
                        continue
                    rec = {
                        **cap.to_dict(),
                        "html_file": path_obj.name,
                        "source": "spa_deep_sample",
                        "coverage": stats,
                    }
                    manifest["captures"].append(rec)
                    urls.add((cap.original, cap.timestamp))
                    digests.add(cap.digest)
                    added += 1
                    kept.append(rec)
                    print(f"  KEPT {cap.timestamp} {stats['dom_words']} words")

    write_json(cdir / "snapshots.json", manifest)
    write_json(cdir / "spa_deep_sample_results.json", {"added": added, "kept": kept})
    print(f"\nB1: added {added} rendered SPA-era captures")


def cmd_sample_json(company: str, n: int, seed: int) -> None:
    cdir = company_dir(company)
    manifest = read_json(cdir / "snapshots.json")
    candidates = manifest.get("json_candidates", [])
    if not candidates:
        print("No json_candidates in manifest")
        return

    rng = random.Random(seed)
    # spread across endpoint types
    by_type: dict[str, list] = {}
    for c in candidates:
        key = c["original"].split("/api/")[-1].split("/")[0] if "/api/" in c["original"] else "other"
        by_type.setdefault(key, []).append(c)
    sample = []
    per = max(1, n // len(by_type))
    for group in by_type.values():
        sample.extend(rng.sample(group, min(per, len(group))))
    sample = sample[:n]

    raw_dir = cdir / "raw_html"
    raw_dir.mkdir(exist_ok=True)
    out_dir = cdir / "json_samples"
    out_dir.mkdir(exist_ok=True)
    findings = []

    with httpx.Client(follow_redirects=True) as client:
        for rec in sample:
            cap = Capture(**rec)
            try:
                path_obj, nbytes = fetch_capture(client, cap, raw_dir)
                # JSON stored with .html extension from fetch_capture — read as text
                text = path_obj.read_text(errors="replace")[:8000]
                out_file = out_dir / f"{cap.timestamp}_{cap.digest[:8]}.json"
                out_file.write_text(text)
                # quick structure probe
                has_mission = any(
                    kw in text.lower()
                    for kw in ("mission", "culture", "benefits", "team", "description", "summary")
                )
                is_listing = "job" in text.lower() and ("title" in text.lower() or "location" in text.lower())
                findings.append({
                    "url": cap.original,
                    "timestamp": cap.timestamp,
                    "bytes": nbytes or path_obj.stat().st_size,
                    "has_mission_keywords": has_mission,
                    "looks_like_job_listing": is_listing,
                    "sample_file": out_file.name,
                    "preview": text[:300],
                })
                print(f"  {cap.timestamp} mission={has_mission} listing={is_listing}")
            except RuntimeError as err:
                findings.append({"url": cap.original, "error": str(err)})

    write_json(cdir / "json_sample_findings.json", findings)
    lines = [
        "# B2: Archived JSON sample findings",
        "",
        f"Sampled {len(findings)} payloads. Review `data/{company}/json_samples/`.",
        "",
        "## Recommendation",
        "",
    ]
    mission_hits = sum(1 for f in findings if f.get("has_mission_keywords") and not f.get("looks_like_job_listing"))
    if mission_hits:
        lines.append(f"- {mission_hits} payloads may carry brand/mission copy — consider a parser.")
    else:
        lines.append("- Payloads appear to be job-search API responses only — skip JSON parser.")
    lines += ["", "## Samples", ""]
    for f in findings:
        lines.append(f"- `{f.get('timestamp', '?')}` {f.get('url', f.get('error', ''))}")
    (cdir / "json_sample_report.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote json_sample_findings.json and json_sample_report.md")


def cmd_probe_domains(company: str) -> None:
    profile = CompanyProfile.load(company)
    alt_domains = profile.alt_domains
    if not alt_domains:
        print(f"No alt_domains in profile for {company}; skipping probe-domains")
        return

    cdir = company_dir(company)
    patterns_path = profile.profile_path
    cfg = read_json(patterns_path)
    lines = [f"# B3: Alternate domain probe ({company})", ""]
    new_patterns = []

    with httpx.Client(follow_redirects=True) as client:
        for probe in alt_domains:
            print(f"CDX: {probe['url']}")
            caps = cdx_query(client, probe["url"], match_type=probe["match_type"])
            years = sorted({c.year for c in caps})
            lines.append(f"## {probe['url']}")
            lines.append(f"- Captures: {len(caps)}")
            lines.append(f"- Years: {years or 'none'}")
            if caps:
                new_patterns.append(probe)
            lines.append("")

    existing_urls = {p["url"] for p in cfg["patterns"]}
    to_add = [p for p in new_patterns if p["url"] not in existing_urls]
    for p in to_add:
        cfg["patterns"].append(p)
    write_json(patterns_path, cfg)

    manifest = read_json(cdir / "snapshots.json")
    raw_dir = cdir / "raw_html"
    m_urls, digests = manifest_sets(manifest)
    fetched = 0
    with httpx.Client(follow_redirects=True) as client:
        for probe in to_add:
            caps = cdx_query(client, probe["url"], match_type=probe["match_type"])
            unique, _ = dedup_by_digest(caps)
            selected = select_per_year(unique, per_year=4)
            for year_caps in selected.values():
                for cap in year_caps:
                    if (cap.original, cap.timestamp) in m_urls or cap.digest in digests:
                        continue
                    try:
                        path_obj, nbytes = fetch_capture(client, cap, raw_dir)
                        manifest["captures"].append({
                            **cap.to_dict(),
                            "html_file": path_obj.name,
                            "source": "alt_domain",
                        })
                        m_urls.add((cap.original, cap.timestamp))
                        digests.add(cap.digest)
                        fetched += 1
                        print(f"  fetched {cap.timestamp} {cap.original}")
                    except RuntimeError as err:
                        print(f"  FAILED {cap.original}: {err}")
    if fetched:
        write_json(cdir / "snapshots.json", manifest)

    (cdir / "alt_domain_probe.md").write_text("\n".join(lines) + "\n")
    print(f"B3: probed {len(alt_domains)} domains, added {len(to_add)} patterns, fetched {fetched} captures")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["deep-sample", "sample-json", "probe-domains"])
    parser.add_argument("--company", default="google")
    parser.add_argument("--per-year", type=int, default=20)
    parser.add_argument("--from-year", type=int, default=2018)
    parser.add_argument("--to-year", type=int, default=2022)
    parser.add_argument("-n", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.command == "deep-sample":
        cmd_deep_sample(args.company, args.per_year, args.from_year, args.to_year)
    elif args.command == "sample-json":
        cmd_sample_json(args.company, args.n, args.seed)
    else:
        cmd_probe_domains(args.company)
    sys.exit(0)
