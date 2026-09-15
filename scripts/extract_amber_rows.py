#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_amber_rows.py  --  Extract AMBER (suggested_label='?') rows from the master xlsx
=========================================================================================
Reads inputs_frozen/ct_artlist_LABELING.xlsx (Label sheet), filters to rows
where suggested_label == '?', and writes them to data_derived/amber_rows_review.csv.

CRITICAL: preserves the existing `relevant` column from the master xlsx. Previous
extraction attempts blanked this column, discarding pre-existing calls. This script
reads and carries forward whatever values the master already has.

Usage:
    .venv\\Scripts\\python.exe scripts/extract_amber_rows.py

Output:
    data_derived/amber_rows_review.csv
"""

import csv
import os
import sys

try:
    import openpyxl
except ImportError:
    print("[ERROR] openpyxl not installed. Run: .venv\\Scripts\\python.exe -m pip install openpyxl")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
MASTER_XLSX = os.path.join(REPO_ROOT, "inputs_frozen", "ct_artlist_LABELING.xlsx")
OUT_CSV = os.path.join(REPO_ROOT, "data_derived", "amber_rows_review.csv")

# Columns to extract (must match the master's Label sheet header exactly)
EXTRACT_COLS = ["entity", "window", "date", "title", "domain", "url",
                "suggested_label", "relevant"]


def main():
    if not os.path.exists(MASTER_XLSX):
        print(f"[ERROR] Master xlsx not found: {MASTER_XLSX}")
        sys.exit(1)

    wb = openpyxl.load_workbook(MASTER_XLSX, read_only=True, data_only=True)
    ws = wb["Label"]

    # Read header row
    header = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    col_indices = {}
    for col in EXTRACT_COLS:
        if col not in header:
            print(f"[ERROR] Column '{col}' not found in Label sheet header: {header}")
            sys.exit(1)
        col_indices[col] = header.index(col)

    sug_idx = col_indices["suggested_label"]

    # Extract AMBER rows (suggested_label == '?')
    amber_rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[sug_idx] == "?":
            row_data = {col: str(row[col_indices[col]] or "") for col in EXTRACT_COLS}
            amber_rows.append(row_data)

    wb.close()

    if not amber_rows:
        print("[WARN] No AMBER rows found (suggested_label='?'). Nothing written.")
        return

    # Write CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EXTRACT_COLS)
        w.writeheader()
        w.writerows(amber_rows)

    # Report
    from collections import Counter
    relevant_counts = Counter(r["relevant"] for r in amber_rows)
    print(f"Extracted {len(amber_rows)} AMBER rows -> {OUT_CSV}")
    print(f"relevant distribution: {dict(relevant_counts)}")

    # Sanity: show any rows where relevant is empty (potential data loss)
    empty_relevant = [r for r in amber_rows if not str(r["relevant"]).strip()]
    if empty_relevant:
        print(f"\nWARNING: {len(empty_relevant)} rows have empty 'relevant' — "
              f"check master xlsx:")
        for r in empty_relevant:
            print(f"  {r['entity']} | {r['domain']}")


if __name__ == "__main__":
    main()
