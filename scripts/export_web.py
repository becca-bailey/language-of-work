#!/usr/bin/env python
"""Export altruism-story pipeline output + cross-company fingerprints for the Astro frontend.

Writes astro/src/data/<company>/<axis>.json — one year series per axis,
sentence-level only (the default analysis granularity).
"""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.company import CompanyProfile
from lowork.config import WEB_DATA_DIR, TOP_K, company_dir
from lowork.io import read_json, write_json

LEVEL = "sentence"

# Human labels for the per-company "values fingerprint" (one bar per axis). Only
# axes present in a company's scores are shown; order here is the display order.
AXIS_LABELS = {
    "altruism": "Mission / idealism",
    "performance": "Performance intensity",
    "meritocracy": "Meritocracy",
    "wellbeing": "Wellbeing & balance",
    "inclusion": "Inclusion & belonging",
    "techno_optimism": "Techno-optimism",
    "craft": "Craft vs iteration",
}


def _company_axis_level(company: str, axis: str) -> tuple[float | None, float | None, int, int]:
    """This company's representative raw level on an axis: (allYearsMean,
    recentMean, recentYear, nYears) over non-thin years (raw cosine, comparable
    across companies). recentMean is the latest 3 years. None if no signal."""
    path = WEB_DATA_DIR / company / f"{axis}.json"
    if not path.exists():
        return None, None, 0, 0
    years = read_json(path).get("years", [])
    usable = [y for y in years if not y.get("thin")] or years
    if not usable:
        return None, None, 0, 0
    usable.sort(key=lambda y: y["year"])
    vals = [y["rawTopkMean"] for y in usable]
    recent = vals[-3:]
    return (
        sum(vals) / len(vals),
        sum(recent) / len(recent),
        usable[-1]["year"],
        len(usable),
    )


def export_fingerprints(companies: list[str]) -> None:
    """Per-company 'values fingerprint': each axis standardized ACROSS companies,
    so a bar reads 'this company leans on X more/less than its peers'. Must run
    over the whole cohort at once — a single company has no peer baseline."""
    levels: dict[str, dict[str, tuple[float | None, float | None, int, int]]] = {}
    for company in companies:
        levels[company] = {a: _company_axis_level(company, a) for a in AXIS_LABELS}

    # Per-axis cross-company mean/std of the all-years level → z-scores.
    import statistics

    stats: dict[str, tuple[float, float]] = {}
    # Rank among peers (1 = highest level). With ~13 companies the z-scores are
    # fragile (one outlier moves everyone), so ranks are exported alongside as
    # the honest "relative position in a small cohort" reading.
    ranks: dict[str, dict[str, int]] = {}
    for axis in AXIS_LABELS:
        present = [(c, levels[c][axis][0]) for c in companies if levels[c][axis][0] is not None]
        if len(present) >= 2:
            vals = [v for _, v in present]
            mean = statistics.fmean(vals)
            std = statistics.pstdev(vals) or 1.0
            stats[axis] = (mean, std)
            ordered = sorted(present, key=lambda cv: cv[1], reverse=True)
            ranks[axis] = {c: i + 1 for i, (c, _) in enumerate(ordered)}

    for company in companies:
        rows = []
        for axis, label in AXIS_LABELS.items():
            level, recent, recent_year, n_years = levels[company][axis]
            if level is None or axis not in stats:
                continue
            mean, std = stats[axis]
            rows.append({
                "axis": axis,
                "label": label,
                "zscore": round((level - mean) / std, 4),
                "recentZscore": round(((recent if recent is not None else level) - mean) / std, 4),
                "recentYear": recent_year,
                "nYears": n_years,
                "rank": ranks[axis][company],
                "nCompanies": len(ranks[axis]),
            })
        profile = CompanyProfile.load(company)
        # Outside the per-company export dir (which is hashed as synthesis input)
        # so writing it doesn't perpetually re-trigger synthesize_company.
        write_json(
            WEB_DATA_DIR / "fingerprints" / f"{company}.json",
            {"company": company, "displayName": profile.display_name, "axes": rows},
        )
    print(f"Wrote fingerprints/ for {len(companies)} companies (cross-company z)")


def update_companies_manifest(company: str, axes: list[str]) -> None:
    """Merge this company's export into astro/src/data/companies.json."""
    manifest_path = WEB_DATA_DIR / "companies.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
    else:
        manifest = {"companies": []}

    profile = CompanyProfile.load(company)
    # Merge (don't replace): preserve axes added by other exporters (e.g. dei),
    # so re-running altruism doesn't drop a company's dei axis from the manifest.
    existing = next((c for c in manifest["companies"] if c["id"] == company), None)
    axes_set = set(existing["axes"]) if existing else set()
    axes_set.update(a for a in axes if a != "control")
    axes_set.discard("control")
    entry = {
        "id": company,
        "displayName": profile.display_name,
        "axes": sorted(axes_set),
    }
    companies = [c for c in manifest["companies"] if c["id"] != company]
    companies.append(entry)
    companies.sort(key=lambda c: c["displayName"])
    write_json(manifest_path, {"companies": companies})
    print(f"Updated {manifest_path}")


def main(company: str) -> None:
    profile = CompanyProfile.load(company)
    cdir = company_dir(company)
    scores = pd.read_parquet(cdir / "axis_scores.parquet")
    quotes = read_json(cdir / "evidence_quotes.json")
    out_dir = WEB_DATA_DIR / company

    # Altruism is cleaned: techno-optimism (product hype) is split out so the
    # per-company line tracks genuine "change the world" mission, not "we build
    # amazing technology". n==0 years (no world-changing language) are dropped as
    # absences rather than imputed, so the detail chart matches the story line.
    split_path = cdir / "altruism_split.parquet"
    split_df = pd.read_parquet(split_path) if split_path.exists() else None
    split_quotes = (
        read_json(cdir / "altruism_split_quotes.json")
        if (cdir / "altruism_split_quotes.json").exists()
        else {}
    )

    exported_axes: list[str] = []
    for axis in scores["axis"].unique():
        sub = scores[(scores["axis"] == axis) & (scores["level"] == LEVEL)].sort_values("year")
        axis_quotes = quotes.get(axis, {}).get(LEVEL, {})

        if axis == "altruism" and split_df is not None:
            wq = split_quotes.get("worldChanging", {})
            years = [
                {
                    "year": int(r.year),
                    "zscore": round(float(r.world_zscore), 4),
                    "rawTopkMean": round(float(r.world_topk), 4),
                    "nChunks": int(r.world_n),
                    "kUsed": min(int(r.world_n), TOP_K),
                    "thin": int(r.world_n) < TOP_K,
                    "carriedForwardFrac": None,
                    "technoShare": round(float(r.techno_share), 4),
                    "quotes": wq.get(str(int(r.year)), []),
                }
                for r in split_df.sort_values("year").itertuples()
                if int(r.world_n) > 0 and pd.notna(r.world_zscore)
            ]
        else:
            years = [
                {
                    "year": int(r.year),
                    "zscore": round(float(r.zscore), 4),
                    "rawTopkMean": round(float(r.raw_topk_mean), 4),
                    "nChunks": int(r.n_chunks),
                    "kUsed": int(r.k_used),
                    "thin": int(r.n_chunks) < TOP_K,
                    "carriedForwardFrac": None,
                    "quotes": axis_quotes.get(str(int(r.year)), []),
                }
                for r in sub.itertuples()
            ]
        write_json(
            out_dir / f"{axis}.json",
            {"company": company, "displayName": profile.display_name, "axis": axis, "years": years},
        )
        exported_axes.append(axis)
        print(f"Wrote {out_dir / f'{axis}.json'} ({len(years)} years, {LEVEL})")

    update_companies_manifest(company, exported_axes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
