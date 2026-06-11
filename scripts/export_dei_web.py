#!/usr/bin/env python
"""Export DEI scores for the Next.js frontend."""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.company import CompanyProfile
from lowork.config import DATA_DIR, ROOT, TOP_K, company_dir
from lowork.dei import DEI_REGISTERS
from lowork.io import read_json, write_json

REGISTER_KEYS = [f"register_{r}" for r in DEI_REGISTERS]

# Companies with DEI data on disk but excluded from the public DEI view
DEI_VIEW_EXCLUDED: set[str] = set()


def update_manifest(company: str) -> None:
    manifest_path = ROOT / "web" / "public" / "data" / "companies.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
    else:
        manifest = {"companies": []}

    profile = CompanyProfile.load(company)
    existing = next((c for c in manifest["companies"] if c["id"] == company), None)
    companies = [c for c in manifest["companies"] if c["id"] != company]
    axes = set(existing["axes"]) if existing else set()
    if company not in DEI_VIEW_EXCLUDED:
        axes.add("dei")
    else:
        axes.discard("dei")
    axes.discard("control")
    companies.append({
        "id": company,
        "displayName": profile.display_name,
        "axes": sorted(axes),
    })
    companies.sort(key=lambda c: c["displayName"])
    write_json(manifest_path, {"companies": companies})
    print(f"Updated {manifest_path}")


def main(company: str) -> None:
    profile = CompanyProfile.load(company)
    cdir = company_dir(company)
    yearly = pd.read_parquet(cdir / "dei_scores.parquet")
    evidence = read_json(cdir / "dei_evidence.json")
    phrases_path = cdir / "dei_phrases.json"
    phrases = read_json(phrases_path) if phrases_path.exists() else {"terms": [], "high_scoring_sentences": []}

    years = []
    for r in yearly.itertuples():
        registers = {reg: int(getattr(r, f"register_{reg}")) for reg in DEI_REGISTERS}
        years.append({
            "year": int(r.year),
            "inclusionTopkMean": round(float(r.inclusion_topk_mean), 4),
            "inclusionMean": round(float(r.inclusion_mean), 4),
            "inclusionMax": round(float(r.inclusion_max), 4),
            "inclusionFractionPresent": round(float(r.inclusion_fraction_present), 4),
            "meritocracyTopkMean": round(float(r.meritocracy_topk_mean), 4),
            "meritocracyMean": round(float(r.meritocracy_mean), 4),
            "nChunks": int(r.n_chunks),
            "kUsed": int(r.inclusion_k_used),
            "thin": int(r.n_chunks) < TOP_K,
            "registers": registers,
            "controlTopkMean": (
                round(float(r.control_raw_topk_mean), 4)
                if r.control_raw_topk_mean is not None and pd.notna(r.control_raw_topk_mean)
                else None
            ),
            "inclusionQuotes": evidence.get("inclusion", {}).get(str(int(r.year)), []),
            "meritocracyQuotes": evidence.get("meritocracy", {}).get(str(int(r.year)), []),
        })

    out_dir = ROOT / "web" / "public" / "data" / company
    write_json(
        out_dir / "dei.json",
        {
            "company": company,
            "displayName": profile.display_name,
            "axis": "dei",
            "years": years,
            "phrases": phrases,
        },
    )
    print(f"Wrote {out_dir / 'dei.json'} ({len(years)} years)")
    update_manifest(company)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
