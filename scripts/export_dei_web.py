#!/usr/bin/env python
"""Export DEI scores for the Astro frontend."""

from __future__ import annotations

import argparse

import pandas as pd

from lowork.company import CompanyProfile
from lowork.config import WEB_DATA_DIR, TOP_K, company_dir
from lowork.dei import DEI_REGISTERS
from lowork.io import read_json, write_json

try:  # works whether `scripts` is a package (CLI) or on sys.path (pipeline _call)
    from scripts.export_web import update_companies_manifest
except ModuleNotFoundError:
    from export_web import update_companies_manifest

REGISTER_KEYS = [f"register_{r}" for r in DEI_REGISTERS]


def update_manifest(company: str) -> None:
    update_companies_manifest(company, ["dei"])
    print(f"Updated {WEB_DATA_DIR / 'companies.json'}")


def main(company: str) -> None:
    profile = CompanyProfile.load(company)
    cdir = company_dir(company)
    yearly = pd.read_parquet(cdir / "dei_scores.parquet")
    evidence = read_json(cdir / "dei_evidence.json")
    phrases_path = cdir / "dei_phrases.json"
    phrases = read_json(phrases_path) if phrases_path.exists() else {"terms": [], "high_scoring_sentences": []}

    years = []
    for r in yearly.itertuples():
        # Registers are the pro-inclusion scale; the two counter keys the charts
        # render are stance-sourced (see lowork.dei_stance.COUNTER_DEI_STANCES).
        registers = {reg: int(getattr(r, f"register_{reg}")) for reg in DEI_REGISTERS}
        registers["mission_focus_apolitical"] = int(getattr(r, "stance_mission_focus_apolitical", 0))
        registers["civilizational_mission"] = int(getattr(r, "stance_civilizational_mission", 0))
        years.append({
            "year": int(r.year),
            "inclusionTopkMean": round(float(r.inclusion_topk_mean), 4),
            "inclusionMean": round(float(r.inclusion_mean), 4),
            "inclusionMax": round(float(r.inclusion_max), 4),
            "inclusionFractionPresent": round(float(r.inclusion_fraction_present), 4),
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
        })

    out_dir = WEB_DATA_DIR / company
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
