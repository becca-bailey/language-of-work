#!/usr/bin/env python
"""Export multi-company story JSON for the Next.js story pages."""

from __future__ import annotations

import argparse
import hashlib
import re

import pandas as pd

from lowork.company import CompanyProfile
from lowork.config import DATA_DIR, ROOT, company_dir
from lowork.io import read_json, write_json

STORY_COMPANIES = ["google", "amazon", "meta", "palantir", "coinbase", "netflix"]
DEI_VIEW_EXCLUDED = {"palantir"}
INVESTOR_COVERAGE_START = 2020

DEI_REGISTERS = [
    "explicit_demographic",
    "structural_process",
    "aspirational_vague",
    "belonging_culture",
    "meritocracy",
    "absent",
]
# Registers that signal active DEI language (pro-inclusion stance)
ACTIVE_DEI_REGISTERS = [
    "explicit_demographic",
    "structural_process",
    "aspirational_vague",
    "belonging_culture",
]


def _year_rows(df: pd.DataFrame, fraction_col: str, mean_col: str) -> list[dict]:
    from lowork.config import TOP_K

    rows = []
    for r in df.sort_values("year").itertuples():
        thin = bool(getattr(r, "thin", int(r.n_chunks) < TOP_K))
        rows.append({
            "year": int(r.year),
            "fractionPresent": round(float(getattr(r, fraction_col)), 4),
            "topkMean": round(float(getattr(r, mean_col)), 4),
            "nChunks": int(r.n_chunks),
            "thin": thin,
        })
    return rows


PERFORMANCE_STANCES: list[dict] = [
    {
        "id": "work_hard_play_hard",
        "label": "Work hard, play hard",
        "note": "The classic startup-era bargain — intensity framed as fun.",
        "pattern": re.compile(
            r"work hard.*(?:play hard|have fun|make history)|play here.*dream here",
            re.I | re.S,
        ),
    },
    {
        "id": "raise_the_bar",
        "label": "Raise the bar",
        "note": "Leadership-principles language — standards others may find unreasonable.",
        "pattern": re.compile(
            r"raise the bar|relentlessly high standards|unreasonably high",
            re.I,
        ),
    },
    {
        "id": "flexible_autonomy",
        "label": "Trust over hours",
        "note": "Anti-crunch framing — output matters, not face time.",
        "pattern": re.compile(r"no set hours|whatever schedule suits you", re.I),
    },
    {
        "id": "move_fast",
        "label": "Move fast",
        "note": "Speed and scale as hiring pitch.",
        "pattern": re.compile(r"move fast|milliseconds and terabytes|immediate impact", re.I),
    },
    {
        "id": "mission_intensity",
        "label": "Mission intensity",
        "note": "Post-2020 civilizational framing — consequence, the West, impact over consensus.",
        "pattern": re.compile(
            r"future of the West|mission-critical|optimize for impact|hardest problems.*smartest",
            re.I,
        ),
    },
    {
        "id": "not_a_family",
        "label": "Not a family",
        "note": "Netflix culture memo — high performance over kinship.",
        "pattern": re.compile(
            r"not a family|dream team|stunning colleagues|keeper test|adequate performance",
            re.I,
        ),
    },
    {
        "id": "high_performer",
        "label": "High-performer ultimatum",
        "note": "Coinbase championship-team framing — outsized rewards, severance for the unremarkable.",
        "pattern": re.compile(
            r"outsized reward|generous severance|championship team|faint of heart|"
            r"pushed beyond what you think",
            re.I,
        ),
    },
    {
        "id": "mission_focused",
        "label": "Mission-focused",
        "note": "Coinbase post-2020 apolitical, mission-first framing.",
        "pattern": re.compile(
            r"mission.?focused|apolitical|political activism|refuge from division|"
            r"stay focused on making progress toward the mission",
            re.I,
        ),
    },
    {
        "id": "investor_tone",
        "label": "Investor-facing",
        "note": "How performance language reads in 10-K Human Capital sections.",
        "pattern": re.compile(
            r"perform at a high level|competition for qualified personnel|work hard to create|"
            r"talented personnel|high.?performing",
            re.I,
        ),
    },
]


def _highlight_id(company: str, year: int, text: str) -> str:
    return hashlib.sha256(f"{company}:{year}:{text[:80]}".encode()).hexdigest()[:12]


def _curate_performance_highlights(companies: list[str]) -> list[dict]:
    """Pick stance-defining quotes from performance evidence."""
    profiles = {c: CompanyProfile.load(c).display_name for c in companies}
    candidates: list[dict] = []

    for company in companies:
        path = company_dir(company) / "performance_evidence.json"
        if not path.exists():
            continue
        evidence = read_json(path)
        for source, by_year in evidence.items():
            for year_str, quotes in by_year.items():
                year = int(year_str)
                for q in quotes:
                    text = q.get("text", "")
                    for stance in PERFORMANCE_STANCES:
                        if source == "careers" and stance["id"] == "investor_tone":
                            continue
                        if source == "investor" and stance["id"] in (
                            "work_hard_play_hard",
                            "flexible_autonomy",
                            "move_fast",
                            "mission_intensity",
                            "not_a_family",
                            "high_performer",
                            "mission_focused",
                        ):
                            continue
                        if not stance["pattern"].search(text):
                            continue
                        score = float(q.get("score", 0))
                        # Prefer distinctive phrasing over generic mission copy
                        if stance["id"] == "mission_intensity":
                            if re.search(r"future of the West|optimize for impact", text, re.I):
                                score += 0.08
                            elif re.search(r"hardest problems.*smartest", text, re.I):
                                score += 0.05
                        candidates.append({
                            "id": _highlight_id(company, year, text),
                            "stance": stance["id"],
                            "stanceLabel": stance["label"],
                            "stanceNote": stance["note"],
                            "company": company,
                            "displayName": profiles[company],
                            "year": year,
                            "source": source,
                            "text": text,
                            "heading": q.get("heading", ""),
                            "score": round(score, 4),
                        })

    # Dedupe near-identical text; top quotes per stance (max 3, min 1 company each)
    seen_text: set[str] = set()
    unique: list[dict] = []
    for c in sorted(candidates, key=lambda x: (-x["score"], -x["year"])):
        key = c["text"][:100]
        if key in seen_text:
            continue
        seen_text.add(key)
        unique.append(c)

    highlights: list[dict] = []
    stance_order = [s["id"] for s in PERFORMANCE_STANCES]
    for stance_id in stance_order:
        items = [c for c in unique if c["stance"] == stance_id]
        picked: list[dict] = []
        used_companies: set[str] = set()
        # First pass: best quote per company
        for company in companies:
            company_items = [c for c in items if c["company"] == company]
            if company_items:
                best = max(company_items, key=lambda x: x["score"])
                picked.append(best)
                used_companies.add(company)
        # Second pass: fill to 3 with highest remaining scores
        picked_ids = {p["id"] for p in picked}
        for c in items:
            if len(picked) >= 3:
                break
            if c["id"] not in picked_ids:
                picked.append(c)
                picked_ids.add(c["id"])
        highlights.extend(sorted(picked, key=lambda x: (-x["score"], x["year"]))[:3])

    return highlights


def _aggregate_lexicons(companies: list[str], filename: str) -> dict:
    merged: dict[str, list] = {}
    for company in companies:
        path = company_dir(company) / filename
        if not path.exists():
            continue
        data = read_json(path)
        for era, terms in data.get("lexicons", {}).items():
            for t in terms:
                merged.setdefault(era, []).append({**t, "company": company})
    return merged


def export_performance(companies: list[str]) -> None:
    sources: dict[str, dict] = {}
    for source in ("careers", "investor"):
        company_series = []
        for company in companies:
            path = company_dir(company) / "performance_scores.parquet"
            if not path.exists():
                continue
            df = pd.read_parquet(path)
            sub = df[df["source"] == source]
            if sub.empty:
                continue
            profile = CompanyProfile.load(company)
            company_series.append({
                "id": company,
                "displayName": profile.display_name,
                "years": _year_rows(
                    sub,
                    "performance_fraction_present",
                    "performance_topk_mean",
                ),
            })
        if company_series:
            sources[source] = {
                "coverageStart": (
                    INVESTOR_COVERAGE_START if source == "investor"
                    else min(
                        y["year"]
                        for c in company_series
                        for y in c["years"]
                    )
                ),
                "companies": company_series,
            }

    lexicons = _aggregate_lexicons(companies, "performance_phrases.json")
    highlights = _curate_performance_highlights(companies)
    out = {
        "story": "performance",
        "title": "Performance Language",
        "metric": "fractionPresent",
        "metricLabel": "Share of chunks with performance language",
        "sources": sources,
        "lexicons": lexicons,
        "highlights": highlights,
    }
    out_dir = ROOT / "web" / "public" / "data" / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "performance.json", out)
    print(f"Wrote {out_dir / 'performance.json'}")


DEI_STANCES: list[dict] = [
    {
        "id": "explicit_inclusion",
        "label": "Explicit inclusion",
        "note": "Demographic or structural DEI commitments on careers pages.",
        "pattern": re.compile(
            r"\b(diversity|inclusion|belonging|equity|underrepresented|"
            r"representation|accessibility)\b",
            re.I,
        ),
    },
    {
        "id": "apolitical",
        "label": "Apolitical workplace",
        "note": "Coinbase-style refusal of workplace activism unrelated to mission.",
        "pattern": re.compile(
            r"political activism|refuge from division|apolitical|"
            r"unrelated to our mission while at work",
            re.I,
        ),
    },
    {
        "id": "not_a_family",
        "label": "Not a family",
        "note": "Netflix culture memo — sports team over kinship.",
        "pattern": re.compile(
            r"not a family|professional sports team|stunning colleagues",
            re.I,
        ),
    },
    {
        "id": "meritocracy",
        "label": "Meritocracy rhetoric",
        "note": "Best-idea-wins and merit framing (including anti-DEI counter-programming).",
        "pattern": re.compile(
            r"meritocracy|best idea wins|best person|A players|top talent",
            re.I,
        ),
    },
]


def _curate_dei_highlights(companies: list[str]) -> list[dict]:
    profiles = {c: CompanyProfile.load(c).display_name for c in companies}
    candidates: list[dict] = []

    for company in companies:
        for source, fname in (("careers", "dei_evidence.json"), ("investor", "dei_investor_evidence.json")):
            path = company_dir(company) / fname
            if not path.exists():
                continue
            evidence = read_json(path)
            quote_sets = (
                [("inclusion", evidence.get("inclusion", evidence))]
                if source == "investor"
                else [("inclusion", evidence.get("inclusion", {})), ("meritocracy", evidence.get("meritocracy", {}))]
            )
            for _axis, by_year in quote_sets:
                if not isinstance(by_year, dict):
                    continue
                for year_str, quotes in by_year.items():
                    year = int(year_str)
                    for q in quotes:
                        text = q.get("text", "")
                        for stance in DEI_STANCES:
                            if source == "investor" and stance["id"] in (
                                "not_a_family",
                                "apolitical",
                            ):
                                continue
                            if not stance["pattern"].search(text):
                                continue
                            score = float(q.get("score", 0))
                            candidates.append({
                                "id": _highlight_id(company, year, text),
                                "stance": stance["id"],
                                "stanceLabel": stance["label"],
                                "stanceNote": stance["note"],
                                "company": company,
                                "displayName": profiles[company],
                                "year": year,
                                "source": source,
                                "text": text,
                                "heading": q.get("heading", ""),
                                "score": round(score, 4),
                            })

    seen_text: set[str] = set()
    unique: list[dict] = []
    for c in sorted(candidates, key=lambda x: (-x["score"], -x["year"])):
        key = c["text"][:100]
        if key in seen_text:
            continue
        seen_text.add(key)
        unique.append(c)

    highlights: list[dict] = []
    stance_order = [s["id"] for s in DEI_STANCES]
    for stance_id in stance_order:
        items = [c for c in unique if c["stance"] == stance_id]
        picked: list[dict] = []
        for company in companies:
            company_items = [c for c in items if c["company"] == company]
            if company_items:
                picked.append(max(company_items, key=lambda x: x["score"]))
        picked_ids = {p["id"] for p in picked}
        for c in items:
            if len(picked) >= 3:
                break
            if c["id"] not in picked_ids:
                picked.append(c)
                picked_ids.add(c["id"])
        highlights.extend(sorted(picked, key=lambda x: (-x["score"], x["year"]))[:3])

    return highlights


def _dei_careers_year_rows(df: pd.DataFrame) -> list[dict]:
    """Register-derived shares + signed net score per year.

    activeShare: fraction of chunks in active DEI registers (pro-inclusion stance)
    meritocracyShare: fraction in the meritocracy/counter-programming register
    netScore: inclusion minus meritocracy projection (signed; >0 = inclusion-leaning)
    """
    from lowork.config import TOP_K

    rows = []
    for r in df.sort_values("year").itertuples():
        n = int(r.n_chunks)
        registers = {reg: int(getattr(r, f"register_{reg}", 0)) for reg in DEI_REGISTERS}
        active = sum(registers[reg] for reg in ACTIVE_DEI_REGISTERS)
        rows.append({
            "year": int(r.year),
            "activeShare": round(active / n, 4) if n else 0.0,
            "meritocracyShare": round(registers["meritocracy"] / n, 4) if n else 0.0,
            "netScore": round(
                float(r.inclusion_topk_mean) - float(r.meritocracy_topk_mean), 4
            ),
            "topkMean": round(float(r.inclusion_topk_mean), 4),
            "registers": registers,
            "nChunks": n,
            "thin": n < TOP_K,
        })
    return rows


def _dei_investor_year_rows(df: pd.DataFrame) -> list[dict]:
    """Investor filings have no register classification — net score only."""
    from lowork.config import TOP_K

    rows = []
    for r in df.sort_values("year").itertuples():
        n = int(r.n_chunks)
        mer = getattr(r, "meritocracy_topk_mean", None)
        net = (
            round(float(r.inclusion_topk_mean) - float(mer), 4)
            if mer is not None and pd.notna(mer)
            else None
        )
        rows.append({
            "year": int(r.year),
            "netScore": net,
            "topkMean": round(float(r.inclusion_topk_mean), 4),
            "nChunks": n,
            "thin": bool(getattr(r, "thin", n < TOP_K)),
        })
    return rows


def _curate_dei_timelines(companies: list[str]) -> list[dict]:
    """Per-company chronological quotes showing how DEI language changed.

    Picks the first and last quote of each register the company ever used,
    so the timeline reads as a then-vs-now narrative.
    """
    timelines: list[dict] = []
    for company in companies:
        path = company_dir(company) / "dei_evidence.json"
        if not path.exists():
            continue
        evidence = read_json(path)
        profile = CompanyProfile.load(company)

        # year -> best quote per register (from both axis evidence sets)
        candidates: list[dict] = []
        for axis in ("inclusion", "meritocracy"):
            for year_str, quotes in evidence.get(axis, {}).items():
                year = int(year_str)
                for q in quotes:
                    reg = q.get("register")
                    if reg is None or reg == "absent" or (isinstance(reg, float) and pd.isna(reg)):
                        continue
                    # meritocracy quotes only from the meritocracy axis ranking
                    if reg == "meritocracy" and axis != "meritocracy":
                        continue
                    if reg != "meritocracy" and axis != "inclusion":
                        continue
                    candidates.append({
                        "year": year,
                        "register": reg,
                        "text": q["text"],
                        "heading": q.get("heading", ""),
                        "score": round(float(q.get("score", 0)), 4),
                    })

        if not candidates:
            continue

        # Best candidate per (year, register)
        best: dict[tuple[int, str], dict] = {}
        for c in candidates:
            key = (c["year"], c["register"])
            if key not in best or c["score"] > best[key]["score"]:
                best[key] = c

        # First and last appearance per register, dedup by text
        by_register: dict[str, list[dict]] = {}
        for c in best.values():
            by_register.setdefault(c["register"], []).append(c)

        picked: list[dict] = []
        seen_text: set[str] = set()
        for reg, items in by_register.items():
            items.sort(key=lambda x: x["year"])
            for item in [items[0], items[-1]]:
                key = item["text"][:80]
                if key in seen_text:
                    continue
                seen_text.add(key)
                picked.append(item)

        picked.sort(key=lambda x: (x["year"], x["register"]))
        timelines.append({
            "company": company,
            "displayName": profile.display_name,
            "quotes": picked[:8],
        })

    return timelines


def export_dei(companies: list[str]) -> None:
    dei_companies = [c for c in companies if c not in DEI_VIEW_EXCLUDED]
    sources: dict[str, dict] = {}

    # Careers: register-derived shares from dei_scores.parquet
    careers_series = []
    for company in dei_companies:
        path = company_dir(company) / "dei_scores.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        profile = CompanyProfile.load(company)
        careers_series.append({
            "id": company,
            "displayName": profile.display_name,
            "years": _dei_careers_year_rows(df),
        })
    if careers_series:
        sources["careers"] = {
            "coverageStart": min(
                y["year"] for c in careers_series for y in c["years"]
            ),
            "companies": careers_series,
        }

    # Investor: net score from dei_investor_scores.parquet (no registers)
    investor_series = []
    for company in dei_companies:
        path = company_dir(company) / "dei_investor_scores.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        profile = CompanyProfile.load(company)
        investor_series.append({
            "id": company,
            "displayName": profile.display_name,
            "years": _dei_investor_year_rows(df),
        })
    if investor_series:
        sources["investor"] = {
            "coverageStart": INVESTOR_COVERAGE_START,
            "companies": investor_series,
        }

    # Merge phrase lexicons from all dei companies
    lexicons: dict[str, list] = {"inclusion": [], "civilizational": []}
    for company in dei_companies:
        path = company_dir(company) / "dei_phrases.json"
        if not path.exists():
            continue
        data = read_json(path)
        for era in ("inclusion", "civilizational"):
            for t in data.get("lexicons", {}).get(era, data.get("terms", [])):
                lexicons[era].append({**t, "company": company})

    highlights = _curate_dei_highlights(dei_companies)
    timelines = _curate_dei_timelines(dei_companies)
    out = {
        "story": "dei",
        "title": "DEI Language",
        "metric": "activeShare",
        "metricLabel": "Share of careers-page chunks in an active DEI register",
        "sources": sources,
        "lexicons": lexicons,
        "highlights": highlights,
        "timelines": timelines,
    }
    out_dir = ROOT / "web" / "public" / "data" / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "dei.json", out)
    print(f"Wrote {out_dir / 'dei.json'}")


def main(story: str, companies: list[str]) -> None:
    if story in ("performance", "all"):
        export_performance(companies)
    if story in ("dei", "all"):
        export_dei(companies)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--story", choices=["performance", "dei", "all"], default="all")
    parser.add_argument("--companies", default=",".join(STORY_COMPANIES))
    args = parser.parse_args()
    main(args.story, [c.strip() for c in args.companies.split(",")])
