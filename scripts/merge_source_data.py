#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_source_data.py  --  Combine Viveka's 20-entity labels with our harvested data
========================================================================================
Creates a single unified source-domain dataset across all 50 entities so that
tier-mapping and weighting operate on one file, not two.

INPUTS (both must exist before running)
-------
1. Viveka's labeled data, exported from ct_artlist_LABELING.xlsx to CSV:
       data_derived/viveka_labeled_export.csv
   Expected columns (VERIFY against the real file — these are best guesses):
       entity, domain, url, title, seendate, sourcecountry, week_start
   If her file has different column names, update VIVEKA_COL_MAP below.

2. Our harvested data for the remaining ~30 entities:
       data_derived/ct_source_results.csv
   Produced by scripts/ct_source_harvester.py.

OUTPUT
------
    data_derived/ct_source_all.csv
    One row per article across all 50 entities.
    Columns: entity, birth_date, window, week_start, domain, url, title,
             seendate, sourcecountry, capped, data_source

    data_derived/merge_diagnostics.txt
    Domain normalization log and overlap/gap diagnostics.

DOMAIN NORMALIZATION
--------------------
Domains are normalized before merging:
  - lowercased
  - www. prefix stripped
  - trailing dots/slashes stripped
This prevents "www.reuters.com" and "reuters.com" from counting as different
sources. The raw domain is preserved in a separate column for traceability.
"""

import csv
import os
import sys
from collections import defaultdict
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# CONFIG — update paths / column maps once real files are inspected
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data_derived")
FROZEN_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs_frozen")

VIVEKA_CSV = os.path.join(DATA_DIR, "viveka_labeled_export.csv")
HARVESTER_CSV = os.path.join(DATA_DIR, "ct_source_results.csv")
OUT_MERGED = os.path.join(DATA_DIR, "ct_source_all.csv")
OUT_DIAGNOSTICS = os.path.join(DATA_DIR, "merge_diagnostics.txt")

# Map Viveka's column names -> canonical names.
# TODO: inspect her actual xlsx export and fix these.
VIVEKA_COL_MAP = {
    "entity": "entity",
    "domain": "domain",       # or maybe "source_domain"?
    "url": "url",
    "title": "title",
    "seendate": "seendate",   # or "date"?
    "sourcecountry": "sourcecountry",
    "week_start": "week_start",   # or "window"? or "other_week"?
    "window": "window",   # verified real column in ct_artlist_LABELING.xlsx (Label sheet)
}

# Guardrail (2026-08-18 methodology decision): only peak_week rows enter the
# analytical source sample. Non-peak rows (other_week / contrast_week) are
# query-precision AUDIT rows, not tier-map evidence, and must not contaminate
# the tier map or weighted counts. See docs/session_log.md.
NON_PEAK_ROW_COUNT = [0]
NON_PEAK_ENTITIES = defaultdict(int)

# Our harvester's column names (known — from ct_source_harvester.py CSV_FIELDS)
HARVESTER_COL_MAP = {
    "entity": "entity",
    "birth_date": "birth_date",
    "window": "window",
    "peak_week_start": "week_start",   # rename to canonical
    "domain": "domain",
    "url": "url",
    "title": "title",
    "seendate": "seendate",
    "sourcecountry": "sourcecountry",
    "capped": "capped",
}

# Entities file — needed for birth_date lookup when Viveka's export
# doesn't include it
ENTITIES_PY = os.path.join(FROZEN_DIR, "entities.py")

CANONICAL_FIELDS = [
    "entity", "birth_date", "window", "week_start", "domain",
    "domain_raw", "url", "title", "seendate", "sourcecountry",
    "capped", "data_source",
]


# ---------------------------------------------------------------------------
# Domain normalization
# ---------------------------------------------------------------------------

def normalize_domain(raw: str) -> str:
    """Lowercase, strip www., strip trailing dots/slashes."""
    d = raw.strip().lower()
    if d.startswith("www."):
        d = d[4:]
    d = d.rstrip("/.")
    return d


def extract_domain_from_url(url: str) -> str:
    """Fallback: if domain column is empty, try parsing from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or ""
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Birth-date lookup from entities.py
# ---------------------------------------------------------------------------

def load_birth_dates() -> dict:
    """Load name -> birth_date from the frozen entities.py roster."""
    with open(ENTITIES_PY, encoding="utf-8") as f:
        src = f.read()
    idx = src.index("ENTITIES = [")
    ns = {}
    exec(src[idx:], ns)
    # entities.py uses "name" not "entity" in its dicts
    return {e["name"]: e["birth_date"] for e in ns["ENTITIES"]}


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------

def read_viveka(birth_dates: dict) -> list[dict]:
    """Read Viveka's labeled export, remap columns, normalize domains."""
    if not os.path.exists(VIVEKA_CSV):
        print(f"[SKIP] {VIVEKA_CSV} not found — Viveka's labeled data not yet exported.")
        return []

    rows = []
    with open(VIVEKA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Check that expected columns exist. "window" is optional: an export may
        # omit it, in which case rows default to peak_week.
        missing = [k for k in VIVEKA_COL_MAP if k not in reader.fieldnames
                   and k != "window"]
        if missing:
            print(f"[ERROR] Viveka CSV is missing columns: {missing}")
            print(f"        Available columns: {reader.fieldnames}")
            print("        Update VIVEKA_COL_MAP in this script to match.")
            sys.exit(1)

        for raw_row in reader:
            entity_name = raw_row[VIVEKA_COL_MAP["entity"]]
            window_val = raw_row.get(VIVEKA_COL_MAP["window"], "peak_week")
            if window_val.strip().lower() != "peak_week":
                NON_PEAK_ROW_COUNT[0] += 1
                NON_PEAK_ENTITIES[entity_name] += 1
                continue
            domain_raw = raw_row.get(VIVEKA_COL_MAP["domain"], "")
            if not domain_raw:
                domain_raw = extract_domain_from_url(
                    raw_row.get(VIVEKA_COL_MAP["url"], "")
                )
            rows.append({
                "entity": entity_name,
                "birth_date": birth_dates.get(entity_name, ""),
                "window": "peak_week",
                "week_start": raw_row.get(VIVEKA_COL_MAP["week_start"], ""),
                "domain": normalize_domain(domain_raw),
                "domain_raw": domain_raw,
                "url": raw_row.get(VIVEKA_COL_MAP["url"], ""),
                "title": raw_row.get(VIVEKA_COL_MAP["title"], ""),
                "seendate": raw_row.get(VIVEKA_COL_MAP["seendate"], ""),
                "sourcecountry": raw_row.get(VIVEKA_COL_MAP["sourcecountry"], ""),
                "capped": "",  # her manual pull isn't subject to the 250 cap
                "data_source": "viveka_manual",
            })
    if NON_PEAK_ROW_COUNT[0]:
        print(f"[INFO] Excluded {NON_PEAK_ROW_COUNT[0]} non-peak_week row(s) "
              f"from the analytical sample (precision-audit rows, not tier-map "
              f"evidence).")
    return rows


def read_harvester() -> list[dict]:
    """Read our harvester output, remap columns, normalize domains."""
    if not os.path.exists(HARVESTER_CSV):
        print(f"[SKIP] {HARVESTER_CSV} not found — harvester not yet run.")
        return []

    rows = []
    with open(HARVESTER_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            domain_raw = raw_row.get("domain", "")
            if not domain_raw:
                domain_raw = extract_domain_from_url(raw_row.get("url", ""))
            rows.append({
                "entity": raw_row["entity"],
                "birth_date": raw_row.get("birth_date", ""),
                "window": raw_row.get("window", "peak_week"),
                "week_start": raw_row.get(
                    "peak_week_start", raw_row.get("week_start", "")
                ),
                "domain": normalize_domain(domain_raw),
                "domain_raw": domain_raw,
                "url": raw_row.get("url", ""),
                "title": raw_row.get("title", ""),
                "seendate": raw_row.get("seendate", ""),
                "sourcecountry": raw_row.get("sourcecountry", ""),
                "capped": raw_row.get("capped", ""),
                "data_source": "harvester",
            })
    return rows


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def write_diagnostics(viveka_rows, harvester_rows, merged_rows, outpath):
    """Write a human-readable diagnostic report for the merge."""
    v_entities = set(r["entity"] for r in viveka_rows)
    h_entities = set(r["entity"] for r in harvester_rows)
    overlap = v_entities & h_entities

    # Domain normalization changes
    norm_changes = []
    for r in merged_rows:
        if r["domain"] != r["domain_raw"].strip().lower():
            norm_changes.append((r["domain_raw"], r["domain"]))

    with open(outpath, "w", encoding="utf-8") as f:
        f.write("MERGE DIAGNOSTICS\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Viveka labeled rows:    {len(viveka_rows):>6d}  "
                f"({len(v_entities)} entities)\n")
        f.write(f"Harvester rows:         {len(harvester_rows):>6d}  "
                f"({len(h_entities)} entities)\n")
        f.write(f"Merged total:           {len(merged_rows):>6d}\n")
        if NON_PEAK_ROW_COUNT[0]:
            f.write(f"Non-peak_week rows excluded from analytical sample: "
                    f"{NON_PEAK_ROW_COUNT[0]} "
                    f"({', '.join(sorted(NON_PEAK_ENTITIES))})\n")
        f.write("\n")

        if overlap:
            f.write(f"WARNING: {len(overlap)} entities appear in BOTH sources "
                    f"(possible duplicate harvest):\n")
            for e in sorted(overlap):
                f.write(f"  - {e}\n")
            f.write("\n")
        else:
            f.write("OK: No entity overlap between sources.\n\n")

        # Check for missing entities (in the 50-entity roster but in neither source)
        try:
            birth_dates = load_birth_dates()
            all_expected = set(birth_dates.keys())
            covered = v_entities | h_entities
            missing = all_expected - covered
            if missing:
                f.write(f"GAPS: {len(missing)} entities in the roster are in "
                        f"neither source:\n")
                for e in sorted(missing):
                    f.write(f"  - {e}\n")
                f.write("\n")
            else:
                f.write("OK: All 50 roster entities are covered.\n\n")
        except Exception as exc:
            f.write(f"Could not load entity roster for gap check: {exc}\n\n")

        # Domain normalization summary
        unique_changes = set(norm_changes)
        if unique_changes:
            f.write(f"Domain normalization: {len(unique_changes)} unique "
                    f"raw->normalized mappings that changed:\n")
            for raw, norm in sorted(unique_changes)[:50]:
                f.write(f"  '{raw}' -> '{norm}'\n")
            if len(unique_changes) > 50:
                f.write(f"  ... and {len(unique_changes) - 50} more\n")
        else:
            f.write("Domain normalization: no changes needed.\n")

        # Capped-week summary
        capped_entities = set(
            r["entity"] for r in merged_rows
            if str(r.get("capped", "")).lower() in ("true", "1", "yes")
        )
        if capped_entities:
            f.write(f"\nCapped weeks (250-article limit hit): "
                    f"{len(capped_entities)} entities\n")
            for e in sorted(capped_entities):
                f.write(f"  - {e}\n")

    print(f"Diagnostics written to {outpath}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    birth_dates = load_birth_dates()

    viveka_rows = read_viveka(birth_dates)
    harvester_rows = read_harvester()

    if not viveka_rows and not harvester_rows:
        print("Nothing to merge — neither input file exists yet.")
        print("Run ct_source_harvester.py and/or export Viveka's xlsx first.")
        return

    merged = viveka_rows + harvester_rows
    print(f"Merged: {len(viveka_rows)} (Viveka) + {len(harvester_rows)} "
          f"(harvester) = {len(merged)} rows")

    # Write merged CSV
    with open(OUT_MERGED, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS)
        w.writeheader()
        w.writerows(merged)
    print(f"Saved {OUT_MERGED}")

    # Write diagnostics
    write_diagnostics(viveka_rows, harvester_rows, merged, OUT_DIAGNOSTICS)


if __name__ == "__main__":
    main()
