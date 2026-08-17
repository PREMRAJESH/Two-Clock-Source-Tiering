#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sensitivity_analysis.py  --  Robustness checks for the weighted precedence test
===============================================================================
Mirrors the paper's Table 2 shape so the weighted result is directly
comparable line-by-line, not just narratively similar.

WHAT THIS DOES
--------------
1. THRESHOLD GRID (Table 2 mirror):
   Ramp thresholds {5%, 10%, 20%} × Onset thresholds {P≥2, P≥3, P≥4}
   = 9 cells, each run for: raw, weighted, Tier1-only, Tier1+2.
   This is the primary output — it shows whether the precedence result
   is robust to threshold choices for BOTH the original and weighted series.

2. TIER-BOUNDARY PERTURBATION:
   Perturb the Jenks break points by ±10% of the gap between breaks,
   reassign tiers, recompute weighted counts, and rerun the baseline
   (10%, P≥3) test. If the sign-test result flips, the finding is
   fragile at the boundary.

3. WEIGHT SENSITIVITY (continuous mode only):
   Sweep Tier 2 weight in {0.25, 0.50, 0.75, 1.0} and Tier 3 weight
   in {0.0, 0.10, 0.25, 0.50} with Tier 1 fixed at 1.0 (16 combos).
   Report the full surface.

4. PASS-ONLY SUBSET:
   Rerun the baseline on only PASS entities from the precision audit
   (n=12 where citation counts are most trustworthy).

5. CAPPED-WEEK EXCLUSION:
   Drop entities whose peak week hit the 250-article cap and rerun.

INPUTS
------
    data_derived/ct_results_weighted.csv
    data_derived/ct_source_all.csv
    data_derived/domain_tier_map.csv
    data_derived/domain_frequency_analysis.csv
    inputs_frozen/pt_pilot_results.csv
    inputs_frozen/entities.py
    inputs_frozen/ct_artlist_precision.csv

OUTPUT
------
    data_derived/sensitivity_results.csv
        One row per (ramp_threshold, onset_threshold, count_type, variant)
        combination: n_precedes, n_testable, median_lead, p_value.

    Printed to stdout: formatted tables mirroring Table 2.
"""

import csv
import os
import sys
from collections import defaultdict

# Import from sibling scripts (same directory)
sys.path.insert(0, os.path.dirname(__file__))
from precedence_test_weighted import (
    load_paper_excluded_entities, load_perception, load_citation_series,
    find_ramp_date, find_onset_date, compute_lead, compute_sign,
    sign_test_two_sided,
)
from apply_weights import (
    load_tier_map, load_source_articles, load_frozen_counts,
    compute_weighted_counts, build_output, OUT_FIELDS as WEIGHTED_FIELDS,
    DEFAULT_WEIGHTS,
)

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data_derived")
FROZEN_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs_frozen")

OUT_SENSITIVITY = os.path.join(DATA_DIR, "sensitivity_results.csv")
FREQ_ANALYSIS = os.path.join(DATA_DIR, "domain_frequency_analysis.csv")
PRECISION_CSV = os.path.join(FROZEN_DIR, "ct_artlist_precision.csv")
WEIGHTED_CSV = os.path.join(DATA_DIR, "ct_results_weighted.csv")

# Table 2 grid
RAMP_THRESHOLDS = [0.05, 0.10, 0.20]
ONSET_THRESHOLDS = [2, 3, 4]
RAMP_FLOOR = 3

# Weight sweep grid
TIER2_WEIGHTS = [0.25, 0.50, 0.75, 1.0]
TIER3_WEIGHTS = [0.0, 0.10, 0.25, 0.50]

# Perturbation magnitude for tier boundaries
BOUNDARY_PERTURBATION = 0.10  # ±10% of the gap between breaks

SENSITIVITY_FIELDS = [
    "variant", "ramp_threshold", "onset_threshold", "count_type",
    "weight_t1", "weight_t2", "weight_t3",
    "n_precedes", "n_testable", "n_ties", "median_lead_days", "p_value",
]


# ---------------------------------------------------------------------------
# Core: run one precedence test with given parameters
# ---------------------------------------------------------------------------

def run_one_test(citation_series, perception, flagged,
                 ramp_threshold, onset_score, count_index,
                 ramp_floor=RAMP_FLOOR, entity_filter=None):
    """
    Run the sign test for a single threshold combination and count type.

    citation_series: entity -> [(week, mc, wc, t1, t12), ...]
    perception: entity -> [(cutoff, score), ...]
    count_index: 1=raw, 2=weighted, 3=tier1, 4=tier12

    Returns dict with n_precedes, n_testable, n_ties, median_lead, p_value.
    """
    leads = []
    for entity in perception:
        if entity in flagged:
            continue
        if entity_filter is not None and entity not in entity_filter:
            continue

        onset_cutoff, _ = find_onset_date(perception[entity],
                                           min_score=onset_score)
        if onset_cutoff is None:
            continue

        ct = citation_series.get(entity, [])
        if not ct:
            continue

        ramp_wk, _ = find_ramp_date(ct, count_index,
                                     threshold=ramp_threshold,
                                     floor=ramp_floor)
        if ramp_wk is None:
            continue

        lead = compute_lead(ramp_wk, onset_cutoff)
        if lead is not None:
            leads.append(lead)

    if not leads:
        return {
            "n_precedes": 0, "n_testable": 0, "n_ties": 0,
            "median_lead_days": 0, "p_value": 1.0,
        }

    signs = [compute_sign(l) for l in leads]
    n_pos = sum(1 for s in signs if s > 0)
    n_neg = sum(1 for s in signs if s < 0)
    n_zero = sum(1 for s in signs if s == 0)
    n_test = n_pos + n_neg
    median_lead = sorted(leads)[len(leads) // 2]
    p = sign_test_two_sided(min(n_pos, n_neg), n_test)

    return {
        "n_precedes": n_pos,
        "n_testable": n_pos + n_neg + n_zero,
        "n_ties": n_zero,
        "median_lead_days": median_lead,
        "p_value": p,
    }


# ---------------------------------------------------------------------------
# 1. Threshold grid (Table 2 mirror)
# ---------------------------------------------------------------------------

def threshold_grid(citation_series, perception, flagged,
                   entity_filter=None, variant_label="baseline"):
    """Run the full 3×3 threshold grid for all count types."""
    results = []
    count_types = [
        (1, "raw"),
        (2, "weighted"),
        (3, "tier1_only"),
        (4, "tier1_plus_2"),
    ]

    for rt in RAMP_THRESHOLDS:
        for ot in ONSET_THRESHOLDS:
            for ci, ct_label in count_types:
                res = run_one_test(
                    citation_series, perception, flagged,
                    ramp_threshold=rt, onset_score=ot, count_index=ci,
                    entity_filter=entity_filter,
                )
                results.append({
                    "variant": variant_label,
                    "ramp_threshold": rt,
                    "onset_threshold": ot,
                    "count_type": ct_label,
                    "weight_t1": DEFAULT_WEIGHTS.get(1, ""),
                    "weight_t2": DEFAULT_WEIGHTS.get(2, ""),
                    "weight_t3": DEFAULT_WEIGHTS.get(3, ""),
                    **res,
                })
    return results


# ---------------------------------------------------------------------------
# 3. Weight sensitivity sweep
# ---------------------------------------------------------------------------

def weight_sweep(source_articles, tier_map_dict, frozen_counts,
                 perception, flagged,
                 ramp_threshold=0.10, onset_score=3):
    """Sweep Tier 2/3 weights and rerun the baseline test."""
    results = []

    for w2 in TIER2_WEIGHTS:
        for w3 in TIER3_WEIGHTS:
            weights = {1: 1.0, 2: w2, 3: w3}

            # Recompute weighted counts with these weights
            agg = compute_weighted_counts(source_articles, tier_map_dict,
                                           weights=weights)
            output_rows = build_output(agg, frozen_counts)

            # Build a citation series from the recomputed rows
            series = defaultdict(list)
            for r in output_rows:
                try:
                    mc = float(r["mention_count"])
                except (ValueError, TypeError):
                    mc = 0.0
                try:
                    wc = float(r["weighted_count"])
                except (ValueError, TypeError):
                    wc = 0.0
                series[r["entity"]].append((
                    r["week_start"], mc, wc,
                    int(r.get("tier1_count", 0)),
                    int(r.get("tier12_count", 0)),
                ))
            for e in series:
                series[e].sort()

            # Run the test on the weighted count (index 2)
            res = run_one_test(
                series, perception, flagged,
                ramp_threshold=ramp_threshold,
                onset_score=onset_score,
                count_index=2,
            )
            results.append({
                "variant": "weight_sweep",
                "ramp_threshold": ramp_threshold,
                "onset_threshold": onset_score,
                "count_type": "weighted",
                "weight_t1": 1.0,
                "weight_t2": w2,
                "weight_t3": w3,
                **res,
            })

    return results


# ---------------------------------------------------------------------------
# 4/5. Subset analyses
# ---------------------------------------------------------------------------

def load_pass_entities():
    """Return set of entity names with PASS in precision audit."""
    entities = set()
    if os.path.exists(PRECISION_CSV):
        for r in csv.DictReader(open(PRECISION_CSV, encoding="utf-8")):
            if r["verdict"] == "PASS":
                entities.add(r["entity"])
    return entities


def load_capped_entities():
    """Return set of entities with any capped week in the weighted CSV."""
    entities = set()
    if os.path.exists(WEIGHTED_CSV):
        for r in csv.DictReader(open(WEIGHTED_CSV, encoding="utf-8")):
            if str(r.get("capped", "")).lower() in ("true", "1", "yes"):
                entities.add(r["entity"])
    return entities


# ---------------------------------------------------------------------------
# Pretty-print Table 2-style output
# ---------------------------------------------------------------------------

def print_table2(results, variant_label):
    """Print a formatted Table 2-style grid."""
    print(f"\n{'=' * 80}")
    print(f"  {variant_label}")
    print(f"{'=' * 80}")

    for ct_label in ["raw", "weighted", "tier1_only", "tier1_plus_2"]:
        print(f"\n  Count type: {ct_label}")
        print(f"  {'':>12s}", end="")
        for ot in ONSET_THRESHOLDS:
            print(f"  {'P>=' + str(ot):>16s}", end="")
        print()

        for rt in RAMP_THRESHOLDS:
            print(f"  {str(int(rt*100))+'% ramp':>12s}", end="")
            for ot in ONSET_THRESHOLDS:
                match = [r for r in results
                         if r["variant"] == variant_label
                         and abs(r["ramp_threshold"] - rt) < 0.001
                         and r["onset_threshold"] == ot
                         and r["count_type"] == ct_label]
                if match:
                    m = match[0]
                    cell = (f"{m['n_precedes']}/{m['n_testable']} "
                            f"p={m['p_value']:.1e}")
                    print(f"  {cell:>16s}", end="")
                else:
                    print(f"  {'-':>16s}", end="")
            print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("SENSITIVITY ANALYSIS — Source Tiering Weighted Precedence Test")
    print("=" * 80)

    # Load shared data
    flagged = load_paper_excluded_entities()
    perception = load_perception()
    citation_series = load_citation_series()

    all_results = []

    # 1. Baseline threshold grid
    print("\n1. THRESHOLD GRID (baseline weights)")
    baseline = threshold_grid(citation_series, perception, flagged,
                               variant_label="baseline")
    all_results.extend(baseline)
    print_table2(baseline, "baseline")

    # 4. PASS-only subset
    print("\n\n4. PASS-ONLY SUBSET (precision audit PASS entities)")
    pass_entities = load_pass_entities()
    if pass_entities:
        print(f"   PASS entities (n={len(pass_entities)}): "
              f"{sorted(pass_entities)}")
        pass_results = threshold_grid(
            citation_series, perception, flagged,
            entity_filter=pass_entities,
            variant_label="pass_only",
        )
        all_results.extend(pass_results)
        print_table2(pass_results, "pass_only")
    else:
        print("   [SKIP] No precision audit data available.")

    # 5. Exclude capped-week entities
    print("\n\n5. EXCLUDE CAPPED-WEEK ENTITIES")
    capped_entities = load_capped_entities()
    if capped_entities:
        print(f"   Capped entities excluded (n={len(capped_entities)}): "
              f"{sorted(capped_entities)}")
        non_capped = {e for e in citation_series if e not in capped_entities}
        nocap_results = threshold_grid(
            citation_series, perception, flagged,
            entity_filter=non_capped,
            variant_label="no_capped",
        )
        all_results.extend(nocap_results)
        print_table2(nocap_results, "no_capped")
    else:
        print("   No capped entities found — skipping.")

    # 3. Weight sensitivity sweep (requires re-computing weighted counts)
    print("\n\n3. WEIGHT SENSITIVITY SWEEP")
    try:
        tier_map_dict = load_tier_map()
        source_articles = load_source_articles()
        frozen = load_frozen_counts()
        weight_results = weight_sweep(
            source_articles, tier_map_dict, frozen,
            perception, flagged,
        )
        all_results.extend(weight_results)

        # Print weight sweep as a matrix
        print(f"\n  Tier 1 = 1.0 (fixed)")
        print(f"  {'T3 \\ T2':>10s}", end="")
        for w2 in TIER2_WEIGHTS:
            print(f"  {'T2=' + str(w2):>14s}", end="")
        print()
        for w3 in TIER3_WEIGHTS:
            print(f"  {'T3=' + str(w3):>10s}", end="")
            for w2 in TIER2_WEIGHTS:
                match = [r for r in weight_results
                         if abs(r["weight_t2"] - w2) < 0.001
                         and abs(r["weight_t3"] - w3) < 0.001]
                if match:
                    m = match[0]
                    cell = (f"{m['n_precedes']}/{m['n_testable']} "
                            f"p={m['p_value']:.1e}")
                    print(f"  {cell:>14s}", end="")
                else:
                    print(f"  {'—':>14s}", end="")
            print()
    except (SystemExit, FileNotFoundError) as e:
        print(f"   [SKIP] Weight sweep requires source data: {e}")

def tier_boundary_perturbation(source_articles, domain_tier_map_dict,
                                freq_analysis_rows, frozen_counts,
                                perception, flagged,
                                ramp_threshold=0.10, onset_score=3):
    """
    Shift borderline domains (within 10% of Jenks break points) up/down a tier
    and rerun the baseline precedence test to verify boundary stability.
    """
    results = []

    # Calculate log_score break points from domain_frequency_analysis
    tier1_scores = [float(r["log_score"]) for r in freq_analysis_rows if int(r["tier"]) == 1]
    tier2_scores = [float(r["log_score"]) for r in freq_analysis_rows if int(r["tier"]) == 2]
    tier3_scores = [float(r["log_score"]) for r in freq_analysis_rows if int(r["tier"]) == 3]

    if not (tier1_scores and tier2_scores and tier3_scores):
        return []

    min_t1 = min(tier1_scores)
    max_t2 = max(tier2_scores)
    min_t2 = min(tier2_scores)
    max_t3 = max(tier3_scores)

    b1_gap = abs(min_t1 - max_t2) or 0.1
    b2_gap = abs(min_t2 - max_t3) or 0.1

    # Calculate total article volume across all source articles
    total_volume = len(source_articles) or 1
    domain_article_counts = Counter(r.get("domain", "").strip() for r in source_articles if r.get("domain"))

    # Shift Up: upgrade Tier 2 domains close to Tier 1 boundary -> Tier 1,
    #           upgrade Tier 3 domains close to Tier 2 boundary -> Tier 2
    map_up = dict(domain_tier_map_dict)
    shifted_up = []
    for r in freq_analysis_rows:
        d = r["domain"]
        ls = float(r["log_score"])
        t = int(r["tier"])
        if t == 2 and abs(ls - min_t1) <= b1_gap * 1.5:
            map_up[d] = 1
            shifted_up.append(d)
        elif t == 3 and abs(ls - min_t2) <= b2_gap * 1.5:
            map_up[d] = 2
            shifted_up.append(d)

    vol_up = sum(domain_article_counts[d] for d in shifted_up)
    pct_vol_up = (vol_up / total_volume) * 100

    # Shift Down: downgrade Tier 1 domains close to boundary -> Tier 2,
    #             downgrade Tier 2 domains close to boundary -> Tier 3
    map_down = dict(domain_tier_map_dict)
    shifted_down = []
    for r in freq_analysis_rows:
        d = r["domain"]
        ls = float(r["log_score"])
        t = int(r["tier"])
        if t == 1 and abs(ls - min_t1) <= b1_gap * 1.5:
            map_down[d] = 2
            shifted_down.append(d)
        elif t == 2 and abs(ls - min_t2) <= b2_gap * 1.5:
            map_down[d] = 3
            shifted_down.append(d)

    vol_down = sum(domain_article_counts[d] for d in shifted_down)
    pct_vol_down = (vol_down / total_volume) * 100

    for label, tmap, shifted_list, vol, pct in [
        ("boundary_shift_up", map_up, shifted_up, vol_up, pct_vol_up),
        ("boundary_shift_down", map_down, shifted_down, vol_down, pct_vol_down),
    ]:
        agg = compute_weighted_counts(source_articles, tmap)
        output_rows = build_output(agg, frozen_counts)
        series = defaultdict(list)
        for r in output_rows:
            try:
                mc = float(r["mention_count"])
            except (ValueError, TypeError):
                mc = 0.0
            try:
                wc = float(r["weighted_count"])
            except (ValueError, TypeError):
                wc = 0.0
            series[r["entity"]].append((
                r["week_start"], mc, wc,
                int(r.get("tier1_count", 0)),
                int(r.get("tier12_count", 0)),
            ))
        for e in series:
            series[e].sort()

        res = run_one_test(
            series, perception, flagged,
            ramp_threshold=ramp_threshold,
            onset_score=onset_score,
            count_index=2,
        )
        results.append({
            "variant": label,
            "ramp_threshold": ramp_threshold,
            "onset_threshold": onset_score,
            "count_type": "weighted",
            "weight_t1": DEFAULT_WEIGHTS.get(1, 1.0),
            "weight_t2": DEFAULT_WEIGHTS.get(2, 0.5),
            "weight_t3": DEFAULT_WEIGHTS.get(3, 0.25),
            "n_reassigned_domains": len(shifted_list),
            "reassigned_vol_pct": round(pct, 2),
            **res,
        })

    return results


def main():
    print("SENSITIVITY ANALYSIS — Source Tiering Weighted Precedence Test")
    print("=" * 80)

    # Load shared data
    flagged = load_paper_excluded_entities()
    perception = load_perception()
    citation_series = load_citation_series()

    all_results = []

    # 1. Baseline threshold grid
    print("\n1. THRESHOLD GRID (baseline weights)")
    baseline = threshold_grid(citation_series, perception, flagged,
                               variant_label="baseline")
    all_results.extend(baseline)
    print_table2(baseline, "baseline")

    # 4. PASS-only subset
    print("\n\n4. PASS-ONLY SUBSET (precision audit PASS entities)")
    pass_entities = load_pass_entities()
    if pass_entities:
        print(f"   PASS entities (n={len(pass_entities)}): "
              f"{sorted(pass_entities)}")
        pass_results = threshold_grid(
            citation_series, perception, flagged,
            entity_filter=pass_entities,
            variant_label="pass_only",
        )
        all_results.extend(pass_results)
        print_table2(pass_results, "pass_only")
    else:
        print("   [SKIP] No precision audit data available.")

    # 5. Exclude capped-week entities
    print("\n\n5. EXCLUDE CAPPED-WEEK ENTITIES")
    capped_entities = load_capped_entities()
    if capped_entities:
        print(f"   Capped entities excluded (n={len(capped_entities)}): "
              f"{sorted(capped_entities)}")
        non_capped = {e for e in citation_series if e not in capped_entities}
        nocap_results = threshold_grid(
            citation_series, perception, flagged,
            entity_filter=non_capped,
            variant_label="no_capped",
        )
        all_results.extend(nocap_results)
        print_table2(nocap_results, "no_capped")
    else:
        print("   No capped entities found — skipping.")

    # 3. Weight sensitivity sweep (requires re-computing weighted counts)
    print("\n\n3. WEIGHT SENSITIVITY SWEEP")
    try:
        tier_map_dict = load_tier_map()
        source_articles = load_source_articles()
        frozen = load_frozen_counts()
        weight_results = weight_sweep(
            source_articles, tier_map_dict, frozen,
            perception, flagged,
        )
        all_results.extend(weight_results)

        # Print weight sweep as a matrix
        print(f"\n  Tier 1 = 1.0 (fixed)")
        print(f"  {'T3 \\ T2':>10s}", end="")
        for w2 in TIER2_WEIGHTS:
            print(f"  {'T2=' + str(w2):>14s}", end="")
        print()
        for w3 in TIER3_WEIGHTS:
            print(f"  {'T3=' + str(w3):>10s}", end="")
            for w2 in TIER2_WEIGHTS:
                match = [r for r in weight_results
                         if abs(r["weight_t2"] - w2) < 0.001
                         and abs(r["weight_t3"] - w3) < 0.001]
                if match:
                    m = match[0]
                    cell = (f"{m['n_precedes']}/{m['n_testable']} "
                            f"p={m['p_value']:.1e}")
                    print(f"  {cell:>14s}", end="")
                else:
                    print(f"  {'—':>14s}", end="")
            print()
    except (SystemExit, FileNotFoundError) as e:
        print(f"   [SKIP] Weight sweep requires source data: {e}")

    # 2. Tier-boundary perturbation test
    print("\n\n2. TIER-BOUNDARY PERTURBATION TEST")
    try:
        if os.path.exists(FREQ_ANALYSIS):
            with open(FREQ_ANALYSIS, newline="", encoding="utf-8") as f:
                freq_rows = list(csv.DictReader(f))
            perturb_results = tier_boundary_perturbation(
                source_articles, tier_map_dict, freq_rows, frozen, perception, flagged
            )
            all_results.extend(perturb_results)
            print(f"  {'Variant':<25s} {'Reassigned':>12s} {'Vol %':>8s} {'Precedes':>10s} {'Median lead':>12s} {'p-value':>12s}")
            print("  " + "-" * 84)
            for pr in perturb_results:
                re_str = f"{pr.get('n_reassigned_domains', 0)} doms"
                vol_str = f"{pr.get('reassigned_vol_pct', 0.0):.1f}%"
                n_str = f"{pr['n_precedes']}/{pr['n_testable']}"
                lead_str = f"{pr['median_lead_days']:.0f} d"
                p_str = f"{pr['p_value']:.2e}"
                print(f"  {pr['variant']:<25s} {re_str:>12s} {vol_str:>8s} {n_str:>10s} {lead_str:>12s} {p_str:>12s}")
        else:
            print("   [SKIP] Requires domain_frequency_analysis.csv from build_tier_map.py.")
    except Exception as e:
        print(f"   [SKIP] Boundary perturbation requires generated data: {e}")

    # Save all results
    with open(OUT_SENSITIVITY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SENSITIVITY_FIELDS)
        w.writeheader()
        for r in all_results:
            w.writerow({k: r.get(k, "") for k in SENSITIVITY_FIELDS})
    print(f"\nAll results saved to {OUT_SENSITIVITY} "
          f"({len(all_results)} rows)")


if __name__ == "__main__":
    main()
