#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_weights.py  --  Tier map + source data -> weighted C(t)
===============================================================================
Joins the domain tier map onto the article-level source data, then
aggregates into a weighted weekly citation series comparable to the
original ct_results_v1_frozen.csv.

Two modes of weighting are computed simultaneously (both are needed
for the precedence test and the sensitivity analysis):

  1. CONTINUOUS WEIGHTS — each article's contribution is scaled by its
     tier weight. Default: Tier 1 = 1.0, Tier 2 = 0.5, Tier 3 = 0.25.
     These defaults are NOT justified by evidence — they exist only as
     a starting grid point. The sensitivity analysis
     (sensitivity_analysis.py) sweeps across weight ratios to show
     whether the result depends on the exact values chosen.

  2. BINARY EXCLUSION — for each tier subset (Tier 1 only; Tier 1+2;
     all), count articles from those tiers only. Simpler to interpret,
     harder to accidentally p-hack.

Both modes produce output columns so the precedence test can be run on
any of them.

INPUTS
------
    data_derived/ct_source_all.csv      (merge_source_data.py output)
    data_derived/domain_tier_map.csv    (build_tier_map.py output)
    inputs_frozen/ct_results_v1_frozen.csv  (for the original weekly counts)

OUTPUT
------
    data_derived/ct_results_weighted.csv
        One row per entity × week_start.  Columns include the original
        mention_count (from the frozen file) alongside:
          - weighted_count           (continuous-weight sum)
          - tier1_count              (articles from Tier 1 only)
          - tier12_count             (articles from Tier 1 + 2)
          - all_tier_count           (all articles, unweighted — should
                                      approximate mention_count but won't
                                      match exactly because source ≠ raw)
          - capped                   (True if the 250-article cap was hit)
          - n_unmatched_domains      (articles whose domain wasn't in the
                                      tier map — should be 0)
"""

import csv
import os
import sys
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data_derived")
FROZEN_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs_frozen")

SOURCE_ALL = os.path.join(DATA_DIR, "ct_source_all.csv")
TIER_MAP = os.path.join(DATA_DIR, "domain_tier_map.csv")
FROZEN_CSV = os.path.join(FROZEN_DIR, "ct_results_v1_frozen.csv")
OUT_CSV = os.path.join(DATA_DIR, "ct_results_weighted.csv")

# Default tier weights for the continuous-weight mode.
# These are starting values for the sensitivity grid — NOT evidence-based.
# The sensitivity analysis sweeps over alternatives to show robustness.
DEFAULT_WEIGHTS = {
    1: 1.0,
    2: 0.5,
    3: 0.25,
}

# Weight for articles whose domain is NOT in the tier map.
# Set to 0.0 so unmatched domains don't silently inflate the weighted count.
# The n_unmatched_domains column tracks how many articles this affects.
UNMATCHED_WEIGHT = 0.0


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_tier_map():
    """domain -> tier (int)."""
    if not os.path.exists(TIER_MAP):
        print(f"Missing {TIER_MAP} — run build_tier_map.py first.")
        sys.exit(1)
    tiers = {}
    with open(TIER_MAP, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tiers[row["domain"]] = int(row["tier"])
    return tiers


def load_source_articles():
    """Return list of article dicts from the merged source file."""
    if not os.path.exists(SOURCE_ALL):
        print(f"Missing {SOURCE_ALL} — run merge_source_data.py first.")
        sys.exit(1)
    with open(SOURCE_ALL, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_frozen_counts():
    """entity -> week_start -> mention_count from the frozen CSV."""
    counts = defaultdict(dict)
    with open(FROZEN_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                mc = float(row["mention_count"])
            except (ValueError, TypeError):
                mc = 0.0
            counts[row["entity"]][row["week_start"]] = {
                "mention_count": mc,
                "birth_date": row["birth_date"],
                "days_from_birth": row["days_from_birth"],
                "ct_precision": row.get("ct_precision", ""),
            }
    return counts


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def compute_weighted_counts(articles, tier_map, weights=None):
    """
    Aggregate article-level data into per-entity, per-week weighted counts.

    Returns: dict of (entity, week_start) -> {
        weighted_count, tier1_count, tier12_count, all_tier_count,
        capped, n_unmatched_domains
    }
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    agg = defaultdict(lambda: {
        "weighted_count": 0.0,
        "tier1_count": 0,
        "tier12_count": 0,
        "all_tier_count": 0,
        "capped": False,
        "n_unmatched_domains": 0,
    })

    for art in articles:
        entity = art["entity"]
        week = art.get("week_start", "")
        domain = art.get("domain", "").strip()

        key = (entity, week)
        a = agg[key]

        tier = tier_map.get(domain)
        if tier is None:
            a["n_unmatched_domains"] += 1
            w = UNMATCHED_WEIGHT
            tier_num = None
        else:
            w = weights.get(tier, UNMATCHED_WEIGHT)
            tier_num = tier

        a["weighted_count"] += w
        a["all_tier_count"] += 1
        if tier_num == 1:
            a["tier1_count"] += 1
            a["tier12_count"] += 1
        elif tier_num == 2:
            a["tier12_count"] += 1

        if str(art.get("capped", "")).lower() in ("true", "1", "yes"):
            a["capped"] = True

    return agg


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

OUT_FIELDS = [
    "entity", "birth_date", "week_start", "days_from_birth",
    "mention_count",           # original from frozen CSV
    "weighted_count",          # continuous-weight sum
    "tier1_count",             # binary: Tier 1 only
    "tier12_count",            # binary: Tier 1 + 2
    "all_tier_count",          # all articles (unweighted)
    "capped",
    "n_unmatched_domains",
    "ct_precision",
]


def build_output(weighted_agg, frozen_counts):
    """
    Merge weighted aggregates with the frozen weekly timeline so every
    entity × week in the original frozen CSV has a row, even if the
    source data doesn't cover that week (source data is peak-week only
    for now, but the frozen CSV has the full timeline).
    """
    rows = []

    for entity in sorted(frozen_counts):
        for week in sorted(frozen_counts[entity]):
            fc = frozen_counts[entity][week]
            key = (entity, week)
            wa = weighted_agg.get(key, {})

            rows.append({
                "entity": entity,
                "birth_date": fc["birth_date"],
                "week_start": week,
                "days_from_birth": fc["days_from_birth"],
                "mention_count": fc["mention_count"],
                "weighted_count": round(wa.get("weighted_count", 0.0), 4),
                "tier1_count": wa.get("tier1_count", 0),
                "tier12_count": wa.get("tier12_count", 0),
                "all_tier_count": wa.get("all_tier_count", 0),
                "capped": wa.get("capped", False),
                "n_unmatched_domains": wa.get("n_unmatched_domains", 0),
                "ct_precision": fc.get("ct_precision", ""),
            })

    return rows


def main():
    tier_map = load_tier_map()
    print(f"Loaded tier map: {len(tier_map)} domains")

    articles = load_source_articles()
    print(f"Loaded {len(articles)} source articles")

    frozen = load_frozen_counts()
    print(f"Loaded frozen counts for {len(frozen)} entities")

    weighted_agg = compute_weighted_counts(articles, tier_map)

    # Diagnostics
    total_unmatched = sum(v["n_unmatched_domains"] for v in weighted_agg.values())
    if total_unmatched:
        print(f"\nWARNING: {total_unmatched} article rows had domains not in "
              f"the tier map — their weight is {UNMATCHED_WEIGHT}. "
              f"Check domain normalization consistency between "
              f"merge_source_data.py and build_tier_map.py.")
    else:
        print("All article domains matched the tier map.")

    # Which entities have weighted data (i.e., source-level data exists)?
    entities_with_source = set(e for e, _ in weighted_agg)
    entities_total = set(frozen.keys())
    print(f"\nEntities with source-level data: {len(entities_with_source)} "
          f"/ {len(entities_total)}")
    if entities_total - entities_with_source:
        print(f"  Missing source data for: "
              f"{sorted(entities_total - entities_with_source)}")
        print("  (These will have weighted_count=0 in all weeks — the "
              "precedence test will use the original mention_count for them, "
              "or they'll need to be excluded from the weighted comparison.)")

    rows = build_output(weighted_agg, frozen)

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved {OUT_CSV} ({len(rows)} rows)")

    # Print tier weight summary
    print(f"\nWeights used: {DEFAULT_WEIGHTS}")
    print("NOTE: These are starting-grid defaults, not evidence-based.")
    print("Run sensitivity_analysis.py to sweep across weight alternatives.")


if __name__ == "__main__":
    main()
