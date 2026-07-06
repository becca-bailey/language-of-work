#!/usr/bin/env python
"""Build the blind hand-coding sheet for locus/specificity validation (Phase 1.3).

Reads data/<co>/wellbeing_benefits.jsonl for the given companies and emits:
  data/wellbeing_locus_review.csv         — blind sheet (no model labels; avoids anchoring)
  data/wellbeing_locus_review.xlsx        — same, with dropdown constraints on the hand cols
  data/wellbeing_locus_review_model.csv   — model labels, held separately for the alpha join

`exclude` is an allowed hand value for items that are NOT well-being benefits (compensation,
equity, insurance, retirement) — distinct from `ambiguous` (is a benefit, locus unclear).
Excluded rows drop from Krippendorff's alpha and from the individualization index.
"""

from __future__ import annotations

import argparse
import csv
import json

from lowork.config import DATA_DIR, company_dir

LOCUS_VALUES = ["individual", "structural", "ambiguous", "exclude"]
SPEC_VALUES = ["enumerated_number", "named_no_number", "generic", "exclude"]
HEADER = ["id", "company", "year", "category", "verbatim",
          "hand_locus", "hand_specificity", "notes"]


def load_items(companies: list[str]) -> list[dict]:
    rows = []
    for co in companies:
        path = company_dir(co) / "wellbeing_benefits.jsonl"
        if not path.exists():
            print(f"  (skip {co}: no wellbeing_benefits.jsonl)")
            continue
        rows.extend(json.loads(line) for line in path.read_text().splitlines() if line.strip())
    return rows


def write_csv(rows: list[dict]) -> None:
    with open(DATA_DIR / "wellbeing_locus_review.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for i, r in enumerate(rows):
            w.writerow([i, r["company"], r["year"], r["category"], r["verbatim"], "", "", ""])
    with open(DATA_DIR / "wellbeing_locus_review_model.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "model_locus", "model_specificity"])
        for i, r in enumerate(rows):
            w.writerow([i, r["locus"], r["specificity"]])


def write_xlsx(rows: list[dict]) -> None:
    from openpyxl import Workbook
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "locus_review"
    ws.append(HEADER)
    for i, r in enumerate(rows):
        ws.append([i, r["company"], r["year"], r["category"], r["verbatim"], "", "", ""])

    n = len(rows) + 1  # last data row (header is row 1)
    dv_locus = DataValidation(
        type="list", formula1='"' + ",".join(LOCUS_VALUES) + '"', allow_blank=True,
        showErrorMessage=True, errorTitle="Invalid locus",
        error="Choose: " + ", ".join(LOCUS_VALUES))
    dv_spec = DataValidation(
        type="list", formula1='"' + ",".join(SPEC_VALUES) + '"', allow_blank=True,
        showErrorMessage=True, errorTitle="Invalid specificity",
        error="Choose: " + ", ".join(SPEC_VALUES))
    ws.add_data_validation(dv_locus)
    ws.add_data_validation(dv_spec)
    dv_locus.add(f"F2:F{n}")   # hand_locus column
    dv_spec.add(f"G2:G{n}")    # hand_specificity column

    # readable column widths; wrap the verbatim column
    widths = {"A": 5, "B": 11, "C": 6, "D": 24, "E": 70, "F": 15, "G": 18, "H": 30}
    for col, wdt in widths.items():
        ws.column_dimensions[col].width = wdt
    ws.freeze_panes = "A2"
    wb.save(DATA_DIR / "wellbeing_locus_review.xlsx")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("companies", nargs="+", help="companies with wellbeing_benefits.jsonl")
    args = ap.parse_args()

    rows = load_items(args.companies)
    write_csv(rows)
    write_xlsx(rows)
    print(f"wrote {len(rows)} items:")
    print("  blind sheet:  data/wellbeing_locus_review.csv + .xlsx (dropdowns on F/G)")
    print("  model labels: data/wellbeing_locus_review_model.csv (held for the alpha join)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
