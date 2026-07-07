#!/usr/bin/env python
"""Export multi-company story JSON for the Next.js story pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict

import numpy as np
import pandas as pd

from lowork.company import CompanyProfile
from lowork.config import WEB_DATA_DIR, DATA_DIR, ROOT, TOP_K, company_dir, load_companies
from lowork.dei import DEI_REGISTERS
from lowork.dei_stance import COUNTER_DEI_STANCES
from lowork.io import read_json, write_json

STORY_COMPANIES = load_companies()
INVESTOR_COVERAGE_START = 2020

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
    out_dir = WEB_DATA_DIR / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "performance.json", out)
    print(f"Wrote {out_dir / 'performance.json'}")


# Highlight categories are defined by the LLM-assigned register/stance labels
# (dei_chunk_labels.json, written by score_dei) — no phrase regexes. A chunk
# qualifies for a category when its label matches; ranking within a category is
# by salience (max inclusion/meritocracy cosine).
DEI_HIGHLIGHT_CATEGORIES: list[dict] = [
    {
        "id": "explicit_inclusion",
        "label": "Explicit inclusion",
        "note": "Named-group or bias-process commitments on careers pages (explicit_demographic / structural_process registers).",
        "match": lambda reg, stance: reg in ("explicit_demographic", "structural_process"),
    },
    {
        "id": "belonging",
        "label": "Belonging language",
        "note": "Worker-experience framing of inclusion — no named groups, no commitments (belonging_culture register).",
        "match": lambda reg, stance: reg == "belonging_culture",
    },
    {
        "id": "apolitical",
        "label": "Apolitical workplace",
        "note": "Refusal of workplace activism unrelated to mission (mission_focus_apolitical stance) — Coinbase's memo, Basecamp's calm-company policy.",
        "match": lambda reg, stance: stance == "mission_focus_apolitical",
    },
    {
        "id": "performance_elite",
        "label": "Performance over kinship",
        "note": "Outcomes-bar framing — sports team over family, stunning colleagues (performance_elite stance).",
        "match": lambda reg, stance: stance == "performance_elite",
    },
    {
        "id": "civilizational_mission",
        "label": "Civilizational mission",
        "note": "West/institutions framing as employer identity — counter-branding to DEI-era copy (civilizational_mission stance).",
        "match": lambda reg, stance: stance == "civilizational_mission",
    },
]

MAX_HIGHLIGHTS_PER_CATEGORY = 4


def _curate_dei_highlights(companies: list[str]) -> list[dict]:
    profiles = {c: CompanyProfile.load(c).display_name for c in companies}
    by_category: dict[str, list[dict]] = {cat["id"]: [] for cat in DEI_HIGHLIGHT_CATEGORIES}

    for company in companies:
        path = company_dir(company) / "dei_chunk_labels.json"
        if not path.exists():
            continue
        for cid, c in read_json(path).items():
            reg, stance = c.get("register"), c.get("stance")
            for cat in DEI_HIGHLIGHT_CATEGORIES:
                if not cat["match"](reg, stance):
                    continue
                by_category[cat["id"]].append({
                    "id": _highlight_id(company, c["year"], c["text"]),
                    "stance": cat["id"],
                    "stanceLabel": cat["label"],
                    "stanceNote": cat["note"],
                    "company": company,
                    "displayName": profiles[company],
                    "year": int(c["year"]),
                    "source": "careers",
                    "text": c["text"],
                    "heading": c.get("heading", ""),
                    "score": float(c.get("salience", 0)),
                })

    highlights: list[dict] = []
    for cat in DEI_HIGHLIGHT_CATEGORIES:
        items = sorted(by_category[cat["id"]], key=lambda x: (-x["score"], -x["year"]))
        # Dedup near-identical copy (same text recurs across snapshot years).
        seen_text: set[str] = set()
        unique = []
        for c in items:
            key = c["text"][:100]
            if key not in seen_text:
                seen_text.add(key)
                unique.append(c)
        # Breadth first: best quote per company, then best remaining.
        picked: list[dict] = []
        seen_companies: set[str] = set()
        for c in unique:
            if c["company"] not in seen_companies:
                picked.append(c)
                seen_companies.add(c["company"])
        for c in unique:
            if len(picked) >= MAX_HIGHLIGHTS_PER_CATEGORY:
                break
            if c not in picked:
                picked.append(c)
        highlights.extend(
            sorted(picked[:MAX_HIGHLIGHTS_PER_CATEGORY], key=lambda x: (-x["score"], x["year"]))
        )

    return highlights


def _optional_metric(val) -> float | None:
    if val is None or pd.isna(val):
        return None
    return round(float(val), 4)


def _clean_quote(q: dict | None) -> dict | None:
    if not q:
        return None
    return {
        "text": q.get("text", ""),
        "heading": q.get("heading", ""),
        "register": q.get("register"),
        "stance": q.get("stance"),
        "stanceDiff": q.get("stanceDiff"),
        "inclusion": q.get("inclusion"),
        "meritocracy": q.get("meritocracy"),
        "salience": q.get("salience"),
        "stanceProjection": q.get("stanceProjection"),
    }


def _dei_careers_year_rows(
    df: pd.DataFrame,
    stance_df: pd.DataFrame | None = None,
    evidence: dict | None = None,
) -> list[dict]:
    """Register-derived shares + stance envelope + salience per year."""
    from lowork.config import TOP_K

    stance_by_year: dict[int, object] = {}
    if stance_df is not None and not stance_df.empty:
        stance_by_year = {int(r.year): r for r in stance_df.itertuples()}

    rows = []
    for r in df.sort_values("year").itertuples():
        year = int(r.year)
        n = int(r.n_chunks)
        registers = {reg: int(getattr(r, f"register_{reg}", 0)) for reg in DEI_REGISTERS}
        active = sum(registers[reg] for reg in ACTIVE_DEI_REGISTERS)
        # Counter-programming counts come from the STANCE axis (registers are the
        # pro-inclusion scale only). Exported under the legacy keys the charts
        # already render: meritocracy ≙ mission_focus_apolitical.
        counter = {s: int(getattr(r, f"stance_{s}", 0)) for s in COUNTER_DEI_STANCES}

        env = (evidence or {}).get("envelope", {}).get(str(year), {})
        sr = stance_by_year.get(year)

        row = {
            "year": year,
            "activeShare": round(active / n, 4) if n else 0.0,
            "meritocracyShare": round(counter["mission_focus_apolitical"] / n, 4) if n else 0.0,
            "civilizationalShare": round(counter["civilizational_mission"] / n, 4) if n else 0.0,
            "counterShare": round(sum(counter.values()) / n, 4) if n else 0.0,
            "netScore": round(
                float(r.inclusion_topk_mean) - float(r.meritocracy_topk_mean), 4
            ),
            "topkMean": round(float(r.inclusion_topk_mean), 4),
            "stanceMean": round(float(getattr(r, "stance_mean", env.get("stanceMean", 0))), 4),
            "salienceTopkMean": round(
                float(getattr(r, "salience_topk_mean", env.get("salienceTopkMean", 0))), 4
            ),
            "textChurn": round(float(getattr(r, "text_churn", env.get("textChurn", 0))), 4),
            # Charts index the counter bars by the legacy register keys; the counts
            # are stance-sourced (meritocracy key carries mission_focus_apolitical).
            "registers": {
                **registers,
                "meritocracy": counter["mission_focus_apolitical"],
                "civilizational_mission": counter["civilizational_mission"],
            },
            "nChunks": n,
            "thin": n < TOP_K,
        }
        stance_max = _optional_metric(getattr(r, "stance_max", env.get("stanceMax")))
        stance_min = _optional_metric(getattr(r, "stance_min", env.get("stanceMin")))
        if stance_max is not None:
            row["stanceMax"] = stance_max
            if env.get("stanceMaxQuote"):
                row["stanceMaxQuote"] = _clean_quote(env.get("stanceMaxQuote"))
        if stance_min is not None:
            row["stanceMin"] = stance_min
            if env.get("stanceMinQuote"):
                row["stanceMinQuote"] = _clean_quote(env.get("stanceMinQuote"))
        if env.get("stanceCounterQuote"):
            row["stanceCounterQuote"] = _clean_quote(env.get("stanceCounterQuote"))
        if env.get("inclusionQuote"):
            row["inclusionQuote"] = _clean_quote(env.get("inclusionQuote"))
        if sr is not None:
            row["bipolarTopkMean"] = round(float(sr.stance_projection_topk_mean), 4)
            bipolar_max = _optional_metric(sr.stance_projection_max)
            bipolar_min = _optional_metric(sr.stance_projection_min)
            if bipolar_max is not None:
                row["bipolarMax"] = bipolar_max
            if bipolar_min is not None:
                row["bipolarMin"] = bipolar_min
        rows.append(row)
    return rows


def _build_envelopes(companies: list[str]) -> list[dict]:
    """Per-company envelope series for fast client access."""
    envelopes: list[dict] = []
    for company in companies:
        path = company_dir(company) / "dei_scores.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        evidence_path = company_dir(company) / "dei_evidence.json"
        evidence = read_json(evidence_path) if evidence_path.exists() else {}
        stance_path = company_dir(company) / "dei_stance_scores.parquet"
        stance_df = pd.read_parquet(stance_path) if stance_path.exists() else None
        profile = CompanyProfile.load(company)
        years = _dei_careers_year_rows(df, stance_df, evidence)
        envelopes.append({
            "company": company,
            "displayName": profile.display_name,
            "years": years,
        })
    return envelopes


def _build_stance_presence(companies: list[str]) -> list[dict]:
    """Per-company stance classifier shares per year."""
    from lowork.dei_stance import DEI_STANCES

    presence: list[dict] = []
    for company in companies:
        stances_path = company_dir(company) / "dei_stances.json"
        if not stances_path.exists():
            continue
        stances = read_json(stances_path)
        from lowork.io import load_all_chunks

        cdir = company_dir(company)
        chunk_list = load_all_chunks(cdir / "chunks")
        classifications_path = cdir / "classifications.json"
        if classifications_path.exists():
            classifications = read_json(classifications_path)
            chunk_list = [
                c for c in chunk_list
                if classifications.get(c["chunk_id"]) in {"mission_brand", "benefits_perks"}
            ]
        else:
            chunk_list = [
                c for c in chunk_list if c.get("label") in {"mission_brand", "benefits_perks"}
            ]
        by_year: dict[int, dict[str, int]] = {}
        for c in chunk_list:
            y = int(c["year"])
            s = stances.get(c["chunk_id"], "neutral")
            by_year.setdefault(y, {})
            by_year[y][s] = by_year[y].get(s, 0) + 1

        profile = CompanyProfile.load(company)
        year_rows = []
        for year in sorted(by_year):
            counts = by_year[year]
            total = sum(counts.values())
            shares = {
                s: round(counts.get(s, 0) / total, 4) if total else 0.0
                for s in DEI_STANCES
            }
            year_rows.append({"year": year, "counts": counts, "shares": shares, "nChunks": total})

        if year_rows:
            presence.append({
                "company": company,
                "displayName": profile.display_name,
                "years": year_rows,
            })
    return presence


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


def _altruism_year_rows(
    alt_df: pd.DataFrame,
    control_df: pd.DataFrame | None,
) -> list[dict]:
    from lowork.config import TOP_K

    control_by_year: dict[int, float] = {}
    if control_df is not None and not control_df.empty:
        for r in control_df.itertuples():
            control_by_year[int(r.year)] = round(float(r.zscore), 4)

    rows = []
    for r in alt_df.sort_values("year").itertuples():
        year = int(r.year)
        n = int(r.n_chunks)
        rows.append({
            "year": year,
            "zscore": round(float(r.zscore), 4),
            "topkMean": round(float(r.raw_topk_mean), 4),
            "controlZscore": control_by_year.get(year),
            "nChunks": n,
            "thin": n < TOP_K,
        })
    return rows


def _best_quote(quotes: list[dict] | None) -> dict | None:
    if not quotes:
        return None
    best = max(quotes, key=lambda q: float(q.get("score", 0)))
    return {
        "text": best.get("text", ""),
        "heading": best.get("heading", ""),
        "score": round(float(best.get("score", 0)), 4),
    }


def _build_altruism_peak_present(
    companies: list[str],
    series_by_company: dict[str, list[dict]],
    quotes_by_company: dict[str, dict],
) -> list[dict]:
    out: list[dict] = []
    for company in companies:
        years = series_by_company.get(company, [])
        if not years:
            continue
        peak = max(years, key=lambda y: y["zscore"])
        latest = years[-1]
        by_year = quotes_by_company.get(company, {})
        profile = CompanyProfile.load(company)
        out.append({
            "company": company,
            "displayName": profile.display_name,
            "peakYear": peak["year"],
            "peakZscore": peak["zscore"],
            "peakQuote": _best_quote(by_year.get(str(peak["year"]))),
            "latestYear": latest["year"],
            "latestZscore": latest["zscore"],
            "latestQuote": _best_quote(by_year.get(str(latest["year"]))),
        })
    return out


def _build_altruism_year_quotes(
    companies: list[str],
    series_by_company: dict[str, list[dict]],
    quotes_by_company: dict[str, dict],
) -> list[dict]:
    """Top idealism quote per company per year — for side-by-side comparison."""
    out: list[dict] = []
    profiles = {c: CompanyProfile.load(c).display_name for c in companies}
    zscore_by_company_year: dict[tuple[str, int], float] = {}
    for company, years in series_by_company.items():
        for y in years:
            zscore_by_company_year[(company, y["year"])] = y["zscore"]

    for company in companies:
        by_year = quotes_by_company.get(company, {})
        for year_str, quotes in by_year.items():
            if not quotes:
                continue
            year = int(year_str)
            best = max(quotes, key=lambda q: float(q.get("score", 0)))
            z = zscore_by_company_year.get((company, year))
            if z is None:
                continue
            out.append({
                "company": company,
                "displayName": profiles[company],
                "year": year,
                "text": best.get("text", ""),
                "heading": best.get("heading", ""),
                "score": round(float(best.get("score", 0)), 4),
                "zscore": z,
            })
    out.sort(key=lambda x: (x["year"], x["displayName"]))
    return out


def _altruism_split(company: str) -> tuple[list[dict], list[dict]] | None:
    """world-changing vs techno-optimism series from altruism_split.parquet."""
    path = company_dir(company) / "altruism_split.parquet"
    if not path.exists():
        return None
    df = pd.read_parquet(path).sort_values("year")
    world, techno = [], []
    for r in df.itertuples():
        y = int(r.year)
        world.append({
            "year": y,
            "zscore": None if pd.isna(r.world_zscore) else round(float(r.world_zscore), 4),
            "topkMean": None if pd.isna(r.world_topk) else round(float(r.world_topk), 4),
            "nChunks": int(r.world_n),
            "thin": int(r.world_n) < TOP_K,
        })
        techno.append({
            "year": y,
            "zscore": round(float(r.techno_zscore), 4) if pd.notna(r.techno_zscore) else None,
            "topkMean": None if pd.isna(r.techno_topk) else round(float(r.techno_topk), 4),
            "nChunks": int(r.techno_n),
            "technoShare": round(float(r.techno_share), 4),
            "thin": int(r.techno_n) < TOP_K,
        })
    return world, techno


def export_altruism(companies: list[str]) -> None:
    company_series = []
    series_by_company: dict[str, list[dict]] = {}
    quotes_by_company: dict[str, dict] = {}

    for company in companies:
        scores_path = company_dir(company) / "axis_scores.parquet"
        quotes_path = company_dir(company) / "evidence_quotes.json"
        if not scores_path.exists():
            continue
        scores = pd.read_parquet(scores_path)
        alt = scores[
            (scores["axis"] == "altruism") & (scores["level"] == "sentence")
        ].sort_values("year")
        if alt.empty:
            continue
        control = scores[
            (scores["axis"] == "control") & (scores["level"] == "sentence")
        ]
        years = _altruism_year_rows(alt, control)
        series_by_company[company] = years

        evidence = read_json(quotes_path) if quotes_path.exists() else {}
        quotes_by_company[company] = evidence.get("altruism", {}).get("sentence", {})

        profile = CompanyProfile.load(company)
        entry = {
            "id": company,
            "displayName": profile.display_name,
            "years": years,
        }
        split = _altruism_split(company)
        if split:
            world, _techno = split
            # Denormalize onto each worldChanging point exactly what the chart
            # renders: the control-line value and the single most-idealistic
            # quote for that year. The full split-quote lists and the techno
            # series are not rendered by anything, so they stay out of the JSON.
            control_by_year = {y["year"]: y.get("controlZscore") for y in years}
            split_q_path = company_dir(company) / "altruism_split_quotes.json"
            wc_quotes = (
                read_json(split_q_path).get("worldChanging", {})
                if split_q_path.exists() else {}
            )
            for pt in world:
                pt["control"] = control_by_year.get(pt["year"])
                items = wc_quotes.get(str(pt["year"]), [])
                if items:
                    pt["quote"] = max(items, key=lambda q: q.get("score", 0)).get("text")
            entry["worldChanging"] = world
        company_series.append(entry)

    if not company_series:
        print("No altruism data to export")
        return

    peak_present = _build_altruism_peak_present(
        companies, series_by_company, quotes_by_company
    )
    year_quotes = _build_altruism_year_quotes(
        companies, series_by_company, quotes_by_company
    )

    # Data only — editorial prose (title, axis label, the techno-optimism split
    # note) lives in the MDX story / component props, not in the dataset.
    out = {
        "story": "altruism",
        "metric": "zscore",
        "sources": {
            "careers": {
                "coverageStart": min(
                    y["year"] for c in company_series for y in c["years"]
                ),
                "companies": company_series,
            },
        },
        "lexicons": {},
        "peakPresent": peak_present,
        "yearQuotes": year_quotes,
    }
    out_dir = WEB_DATA_DIR / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "altruism.json", out)
    print(f"Wrote {out_dir / 'altruism.json'}")


# ── Well-being story datasets (H1 concession + locus divergence + GitLab flow) ──

_WB_BEN_LABELS = {"benefits_perks", "job_listing"}
_WB_MH = re.compile(r"mental health|well[- ]?being|wellness|therapy|counsel|meditation|"
                    r"headspace|\bEAP\b|burnout", re.I)
_WB_FAM = re.compile(r"parental leave|maternity|paternity|childcare|child care|adoption|"
                     r"family leave|caregiv|nursing (?:room|mother)|baby bonding|fertilit", re.I)


def _wb_pooled_axis(companies, axis, lo=2013, hi=2026):
    """Balanced pooled annual mean of a raw axis score across companies."""
    per_year = defaultdict(list)
    for co in companies:
        p = company_dir(co) / "axis_scores.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        d = df[(df["axis"] == axis) & (df["level"] == "chunk")]
        for _, r in d.iterrows():
            if lo <= r["year"] <= hi:
                per_year[int(r["year"])].append(float(r["raw_topk_mean"]))
    return {y: float(np.mean(v)) for y, v in per_year.items() if len(v) >= 4}


def _zscore_series(series: dict) -> dict:
    vals = np.array(list(series.values()))
    m, s = vals.mean(), vals.std() or 1.0
    return {y: (v - m) / s for y, v in series.items()}


def _wb_concession(companies) -> list[dict]:
    """care & DEI rhetoric (z-scored pooled) + JOLTS quits, per year — for the overlay."""
    care = _zscore_series(_wb_pooled_axis(companies, "wellbeing"))
    dei = _zscore_series(_wb_pooled_axis(companies, "inclusion"))
    quits = {q["year"]: q["quitsRate"]
             for q in read_json(DATA_DIR / "power_proxies.json")["quits"]}
    years = sorted(set(care) & set(dei))
    return [{"year": y, "careZ": round(care[y], 3), "deiZ": round(dei[y], 3),
             "quits": quits.get(y)} for y in years if 2015 <= y <= 2026]


def _wb_axes2020(companies) -> list[dict]:
    """Each axis's 2020 value as a within-axis z-score — which axes spiked."""
    axes = [("wellbeing", "Care"), ("inclusion", "DEI / inclusion"),
            ("altruism", "Altruism"), ("performance", "Performance"),
            ("meritocracy", "Meritocracy"), ("control", "Control"),
            ("techno_optimism", "Techno-optimism")]
    out = []
    for axis, label in axes:
        z = _zscore_series(_wb_pooled_axis(companies, axis))
        if 2020 in z:
            out.append({"axis": axis, "label": label, "z2020": round(z[2020], 2),
                        "concession": axis in ("wellbeing", "inclusion")})
    return sorted(out, key=lambda r: -r["z2020"])


def _wb_locus_divergence(companies) -> list[dict]:
    """Keyword prevalence of mental-health (individual-locus) vs family/caregiving
    (structural-locus) benefits per year — share of benefit chunks. The centerpiece."""
    mh_num, fam_num, den = defaultdict(int), defaultdict(int), defaultdict(int)
    for co in companies:
        cp = company_dir(co) / "classifications.json"
        chunks_dir = company_dir(co) / "chunks"
        if not cp.exists() or not chunks_dir.exists():
            continue
        labs = read_json(cp)
        for path in sorted(chunks_dir.glob("*.jsonl")):
            for line in path.read_text().splitlines():
                if not line.strip():
                    continue
                c = json.loads(line)
                if labs.get(c["chunk_id"]) not in _WB_BEN_LABELS:
                    continue
                y = c.get("year")
                if y is None:
                    continue
                den[y] += 1
                if _WB_MH.search(c["text"]):
                    mh_num[y] += 1
                if _WB_FAM.search(c["text"]):
                    fam_num[y] += 1
    return [{"year": y,
             "mentalHealth": round(mh_num[y] / den[y], 3),
             "caregiving": round(fam_num[y] / den[y], 3),
             "nChunks": den[y]}
            for y in sorted(den) if den[y] >= 3 and 2013 <= y <= 2026]


def _wb_flow() -> dict:
    """GitLab Family & Friends Day timeline: commits/year + the annotated events."""
    p = DATA_DIR / "gitlab" / "wellbeing_flow.jsonl"
    if not p.exists():
        return {}
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    by_year = defaultdict(int)
    for r in rows:
        by_year[int(r["date"][:4])] += 1
    events = [
        {"date": "2020-04", "label": "Created as pandemic relief", "kind": "add"},
        {"date": "2020-10", "label": "Formalized to monthly cadence", "kind": "expand"},
        {"date": "2021-04", "label": "Renamed “Pandemic Support Day” for six days, then reverted",
         "kind": "reframe"},
        {"date": "2022-07", "label": "Coverage requirements added — some must stay back",
         "kind": "restrict"},
        {"date": "2023-08", "label": "Migrated to the handbook repo", "kind": "reframe"},
    ]
    return {"byYear": [{"year": y, "commits": by_year[y]} for y in sorted(by_year)],
            "events": events}


def export_wellbeing(companies: list[str]) -> None:
    """Cross-company wellbeing (balance <-> intensity/sacrifice) year series.

    Story dataset only — no MDX story page consumes this yet; it is exported so
    the wellbeing counterforce is a first-class story axis alongside altruism/
    performance/dei when the story is written.
    """
    company_series = []
    for company in companies:
        scores_path = company_dir(company) / "axis_scores.parquet"
        if not scores_path.exists():
            continue
        scores = pd.read_parquet(scores_path)
        wb = scores[
            (scores["axis"] == "wellbeing") & (scores["level"] == "sentence")
        ].sort_values("year")
        if wb.empty:
            continue
        control = scores[
            (scores["axis"] == "control") & (scores["level"] == "sentence")
        ]
        years = _altruism_year_rows(wb, control)

        quotes_path = company_dir(company) / "evidence_quotes.json"
        evidence = read_json(quotes_path) if quotes_path.exists() else {}
        wb_quotes = evidence.get("wellbeing", {}).get("sentence", {})
        for row in years:
            best = _best_quote(wb_quotes.get(str(row["year"])))
            if best:
                row["quote"] = best["text"]

        profile = CompanyProfile.load(company)
        company_series.append({
            "id": company,
            "displayName": profile.display_name,
            "years": years,
        })

    if not company_series:
        print("No wellbeing data to export")
        return

    out = {
        "story": "wellbeing",
        "metric": "zscore",
        "sources": {
            "careers": {
                "coverageStart": min(
                    y["year"] for c in company_series for y in c["years"]
                ),
                "companies": company_series,
            },
        },
        # Story-page datasets (H1 concession bundle + locus divergence + GitLab flow).
        "concession": _wb_concession(companies),
        "axes2020": _wb_axes2020(companies),
        "locusDivergence": _wb_locus_divergence(companies),
        "flow": _wb_flow(),
    }
    out_dir = WEB_DATA_DIR / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "wellbeing.json", out)
    print(f"Wrote {out_dir / 'wellbeing.json'}")


def export_dei(companies: list[str]) -> None:
    dei_companies = companies
    sources: dict[str, dict] = {}

    # Careers: register-derived shares + envelope from dei_scores.parquet
    careers_series = []
    for company in dei_companies:
        path = company_dir(company) / "dei_scores.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        evidence_path = company_dir(company) / "dei_evidence.json"
        evidence = read_json(evidence_path) if evidence_path.exists() else {}
        stance_path = company_dir(company) / "dei_stance_scores.parquet"
        stance_df = pd.read_parquet(stance_path) if stance_path.exists() else None
        profile = CompanyProfile.load(company)
        careers_series.append({
            "id": company,
            "displayName": profile.display_name,
            "years": _dei_careers_year_rows(df, stance_df, evidence),
        })
    if careers_series:
        # Data only: the register chart needs registers + nChunks + thin (to
        # tell no-capture from DEI-absent); the hover needs the two stance
        # quotes. The retired salience/envelope/stance fields stay out.
        keep = {"year", "registers", "nChunks", "thin", "stanceMaxQuote", "stanceMinQuote"}
        for c in careers_series:
            c["years"] = [{k: v for k, v in y.items() if k in keep} for y in c["years"]]
        sources["careers"] = {
            "coverageStart": min(y["year"] for c in careers_series for y in c["years"]),
            "companies": careers_series,
        }

    # Editorial framing (title, axis label) lives in the MDX. The investor
    # source, phrase lexicons, and the retired salience/envelope/timeline
    # blocks are rendered by nothing, so they stay out of the JSON.
    out = {
        "story": "dei",
        "sources": sources,
        "highlights": _curate_dei_highlights(dei_companies),
    }
    out_dir = WEB_DATA_DIR / "stories"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "dei.json", out)
    print(f"Wrote {out_dir / 'dei.json'}")


def main(story: str, companies: list[str]) -> None:
    if story in ("performance", "all"):
        export_performance(companies)
    if story in ("dei", "all"):
        export_dei(companies)
    if story in ("altruism", "all"):
        export_altruism(companies)
    if story in ("wellbeing", "all"):
        export_wellbeing(companies)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--story",
        choices=["performance", "dei", "altruism", "wellbeing", "all"],
        default="all",
    )
    parser.add_argument("--companies", default=",".join(STORY_COMPANIES))
    args = parser.parse_args()
    main(args.story, [c.strip() for c in args.companies.split(",")])
