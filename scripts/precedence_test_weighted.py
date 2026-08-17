#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
precedence_test_weighted.py  --  Rerun Section 4.6 sign test on weighted C(t)
===============================================================================
Compares citation ramp date vs. perception onset for each entity, using both
the original (raw) citation counts and the tier-weighted counts. Reports the
exact sign test for each and the delta between them.

DEFINITIONS (from Section 4.6 of the paper — supplied directly by lead author)
-----------------------------------------------------------------------------
  RAMP DATE   = first week_start where C(t) >= threshold × peak(C(t)),
                subject to a floor of RAMP_FLOOR mentions (to avoid noise
                triggering on near-zero weeks).
                Default threshold: 10% of peak.  Sensitivity: 5%, 20%.

  ONSET DATE  = the reported_cutoff of the first model where P(t) >= onset_score.
                Default onset_score: 3 (on the 0–4 scale).
                Sensitivity: 2, 4.

  LEAD        = onset_date − ramp_date (in days).  Positive = ramp precedes onset.

  TEST        = two-sided exact sign test on the sign of lead across entities.

ENTITY SELECTION
----------------
  - EXCLUDE the paper's exact 17 entities:
      * 10 precision-audit FAIL entities from Section 4.5 / Table 1.
      * 7 no-onset entities from Section 5.4.
  - The self_ref_openai flag in entities.py is NOT part of the raw baseline.
  - The paper's baseline uses onset_score=3 and gets 33 testable entities
    (50 - 10 FAIL - 7 no-onset).
    This script will explicitly list its inclusions/exclusions so any discrepancy
    with the paper's 33 is visible and traceable.

INPUTS
------
    data_derived/ct_results_weighted.csv   (apply_weights.py output)
    inputs_frozen/pt_pilot_results.csv     (perception scores)
    inputs_frozen/entities.py              (not used for baseline exclusions)

OUTPUT
------
    data_derived/precedence_comparison.csv
        Per-entity: ramp dates (raw & weighted), onset date, leads, signs.

    Printed to stdout: the headline sign-test result for raw vs. weighted,
    and the comparison table.
"""

import csv
import math
import os
import sys
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data_derived")
FROZEN_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs_frozen")

WEIGHTED_CSV = os.path.join(DATA_DIR, "ct_results_weighted.csv")
CT_CSV = os.path.join(FROZEN_DIR, "ct_results_v1_frozen.csv")
PT_CSV = os.path.join(FROZEN_DIR, "pt_pilot_results.csv")
ENTITIES_PY = os.path.join(FROZEN_DIR, "entities.py")
OUT_CSV = os.path.join(DATA_DIR, "precedence_comparison.csv")

# Default thresholds (Section 4.6 baseline)
RAMP_THRESHOLD = 0.10     # 10% of peak
RAMP_FLOOR = 3            # minimum absolute mentions to count as ramp

# Section 4.5 Table 1: 10 precision-audit FAIL entities, exact paper names.
PRECISION_FAIL = {
    "DBRX",
    "Kimi",
    "Ideogram",
    "Lovable",
    "Gemini (Google model)",
    "Dream Machine",
    "Liquid AI",
    "Mamba",
    "Operator",
    "vLLM",
}

# Section 5.4: 7 no-onset entities, exact paper names.
NO_ONSET = {
    "OpenAI o1",
    "OpenAI o3",
    "DeepSeek",
    "DeepSeek-R1",
    "Manus",
    "World Labs",
    "Bolt.new",
}

PAPER_EXCLUDED = PRECISION_FAIL | NO_ONSET
ONSET_SCORE = 3           # P(t) >= 3 on the 0–4 scale


# ---------------------------------------------------------------------------
# Exact sign test (two-sided, no scipy dependency)
# ---------------------------------------------------------------------------

def _comb(n, k):
    """Binomial coefficient C(n, k)."""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def sign_test_two_sided(n_positive, n_total):
    """
    Two-sided exact sign test.
    H0: P(positive) = 0.5.
    Returns p-value as the probability of observing a result at least as
    extreme as n_positive (in either direction) under H0.
    """
    if n_total == 0:
        return 1.0
    # Sum probabilities for outcomes at least as extreme
    k = min(n_positive, n_total - n_positive)
    p = 0.0
    for i in range(k + 1):
        p += _comb(n_total, i)
    p *= 2  # two-sided
    p /= 2 ** n_total
    return min(p, 1.0)  # cap at 1.0


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _base_name(entity_name):
    """Strip parenthetical disambiguators: 'Cursor (the AI code editor)' -> 'Cursor'."""
    idx = entity_name.find(" (")
    if idx > 0:
        return entity_name[:idx]
    return entity_name


def load_paper_excluded_entities():
    """Return the paper's exact 10 FAIL + 7 no-onset exclusion set."""
    return set(PAPER_EXCLUDED)


def load_flagged_entities():
    """
    Backward-compatible alias for older callers.

    The baseline exclusion set is the paper's 10 FAIL + 7 no-onset names,
    not the self_ref_openai flag.
    """
    return load_paper_excluded_entities()


def is_paper_excluded(entity_name):
    """Check the paper exclusion set using exact and base-name forms."""
    return entity_name in PAPER_EXCLUDED or _base_name(entity_name) in PAPER_EXCLUDED


def build_name_bridge(pt_entities, ct_entities):
    """
    Build a PT-name -> CT-name mapping, stripping parenthetical disambiguators
    where needed.
    """
    bridge = {}
    for pt_name in pt_entities:
        if pt_name in ct_entities:
            bridge[pt_name] = pt_name
            continue

        pt_base = _base_name(pt_name)
        if pt_base in ct_entities:
            bridge[pt_name] = pt_base
            continue

        for ct_name in ct_entities:
            if _base_name(ct_name) == pt_base:
                bridge[pt_name] = ct_name
                break

    return bridge


def load_citation_entity_names():
    """Return the CT entity namespace from weighted output or frozen raw counts."""
    path = WEIGHTED_CSV if os.path.exists(WEIGHTED_CSV) else CT_CSV
    return {r["entity"] for r in csv.DictReader(open(path, encoding="utf-8"))}


def load_perception():
    """
    entity -> list of (cutoff_date, score) sorted by cutoff_date.
    For models sharing the same cutoff, take the MAX score (conservative:
    if any model at that cutoff recognizes the entity, onset has occurred).
    """
    raw = defaultdict(list)
    for r in csv.DictReader(open(PT_CSV, encoding="utf-8")):
        raw[r["entity"]].append((r["reported_cutoff"], int(r["score"])))

    bridge = build_name_bridge(set(raw.keys()), load_citation_entity_names())

    # Deduplicate by cutoff: take max score per cutoff
    perception = {}
    for pt_entity, pairs in raw.items():
        entity = bridge.get(pt_entity, pt_entity)
        by_cutoff = defaultdict(int)
        for cutoff, score in pairs:
            by_cutoff[cutoff] = max(by_cutoff[cutoff], score)
        existing = perception.setdefault(entity, [])
        existing.extend(by_cutoff.items())

    for entity, pairs in list(perception.items()):
        by_cutoff = defaultdict(int)
        for cutoff, score in pairs:
            by_cutoff[cutoff] = max(by_cutoff[cutoff], score)
        perception[entity] = sorted(by_cutoff.items())
    return perception


def load_citation_series():
    """
    entity -> list of (week_start_date, mention_count, weighted_count,
                       tier1_count, tier12_count) sorted by week_start.

    If weighted output has not been generated yet, fall back to the frozen raw
    CT counts so the raw-mode baseline remains checkable inside this script.
    """
    series = defaultdict(list)

    if os.path.exists(WEIGHTED_CSV):
        path = WEIGHTED_CSV
        weighted_available = True
    else:
        path = CT_CSV
        weighted_available = False

    for r in csv.DictReader(open(path, encoding="utf-8")):
        try:
            mc = float(r["mention_count"])
        except (ValueError, TypeError):
            mc = 0.0

        if weighted_available:
            try:
                wc = float(r["weighted_count"])
            except (ValueError, TypeError):
                wc = 0.0
            try:
                t1 = int(r["tier1_count"])
            except (ValueError, TypeError):
                t1 = 0
            try:
                t12 = int(r["tier12_count"])
            except (ValueError, TypeError):
                t12 = 0
        else:
            wc = 0.0
            t1 = 0
            t12 = 0

        series[r["entity"]].append((r["week_start"], mc, wc, t1, t12))

    for e in series:
        series[e].sort()
    return series


# ---------------------------------------------------------------------------
# Ramp and onset computation
# ---------------------------------------------------------------------------

def find_ramp_date(weekly_data, count_index, threshold=RAMP_THRESHOLD,
                   floor=RAMP_FLOOR):
    """
    Find the first week where the count reaches threshold × peak,
    subject to the floor.

    weekly_data: list of (week_start_str, mention_count, weighted_count,
                          tier1_count, tier12_count)
    count_index: which element of the tuple to use (1=raw, 2=weighted, etc.)

    Returns (week_start_str, count_at_ramp) or (None, None) if no ramp.
    """
    if not weekly_data:
        return None, None

    peak = max(row[count_index] for row in weekly_data)
    if peak <= 0:
        return None, None

    ramp_level = max(threshold * peak, floor)

    for row in weekly_data:
        if row[count_index] >= ramp_level:
            return row[0], row[count_index]

    return None, None


def find_onset_date(perception_ladder, min_score=ONSET_SCORE):
    """
    Find the first cutoff where score >= min_score.
    perception_ladder: sorted list of (cutoff_str, max_score).
    Cutoff format: "YYYY-MM" — convert to first of month for date arithmetic.
    Returns (onset_date_str, score) or (None, None).
    """
    for cutoff_str, score in perception_ladder:
        if score >= min_score:
            return cutoff_str, score
    return None, None


def cutoff_to_date(cutoff_str):
    """Convert 'YYYY-MM' to a datetime (first of month)."""
    return datetime.strptime(cutoff_str + "-01", "%Y-%m-%d")


def week_to_date(week_str):
    """Convert 'YYYY-MM-DD' to a datetime."""
    return datetime.strptime(week_str, "%Y-%m-%d")


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

OUT_FIELDS = [
    "entity", "birth_date",
    "ramp_raw_week", "ramp_raw_count",
    "ramp_weighted_week", "ramp_weighted_count",
    "ramp_tier1_week", "ramp_tier12_week",
    "onset_cutoff", "onset_score",
    "lead_raw_days", "lead_weighted_days",
    "lead_tier1_days", "lead_tier12_days",
    "sign_raw", "sign_weighted", "sign_tier1", "sign_tier12",
    "excluded_reason",
]


def compute_sign(lead_days):
    """Return +1, 0, or -1 for the sign of lead (positive = ramp precedes)."""
    if lead_days is None:
        return None
    if lead_days > 0:
        return 1
    elif lead_days < 0:
        return -1
    return 0


def compute_lead(ramp_week, onset_cutoff):
    """Compute lead in days (onset - ramp). Positive = ramp precedes onset."""
    if ramp_week is None or onset_cutoff is None:
        return None
    try:
        r = week_to_date(ramp_week)
        o = cutoff_to_date(onset_cutoff)
        return (o - r).days
    except (ValueError, TypeError):
        return None


def run_analysis(ramp_threshold=RAMP_THRESHOLD, onset_score=ONSET_SCORE,
                 ramp_floor=RAMP_FLOOR):
    """
    Run the full precedence analysis for a given set of thresholds.
    Returns (rows, summary_dict).
    """
    paper_excluded = load_paper_excluded_entities()
    perception = load_perception()
    citation = load_citation_series()

    # Get birth dates from citation data
    birth_dates = {}
    citation_path = WEIGHTED_CSV if os.path.exists(WEIGHTED_CSV) else CT_CSV
    for r in csv.DictReader(open(citation_path, encoding="utf-8")):
        birth_dates[r["entity"]] = r["birth_date"]

    rows = []
    for entity in sorted(perception.keys()):
        row = {"entity": entity, "birth_date": birth_dates.get(entity, "")}

        # Check exclusions
        if entity in paper_excluded or is_paper_excluded(entity):
            row["excluded_reason"] = "paper_exclusion (10 FAIL / 7 no-onset)"
            rows.append({k: row.get(k, "") for k in OUT_FIELDS})
            continue

        # Onset
        onset_cutoff, o_score = find_onset_date(
            perception[entity], min_score=onset_score
        )
        if onset_cutoff is None:
            row["excluded_reason"] = f"no_onset (max P < {onset_score})"
            rows.append({k: row.get(k, "") for k in OUT_FIELDS})
            continue

        row["onset_cutoff"] = onset_cutoff
        row["onset_score"] = o_score

        # Citation series for this entity
        ct = citation.get(entity, [])
        if not ct:
            row["excluded_reason"] = "no_citation_data"
            rows.append({k: row.get(k, "") for k in OUT_FIELDS})
            continue

        # Ramp dates for each count type
        # Index 1 = mention_count (raw), 2 = weighted_count,
        # 3 = tier1_count, 4 = tier12_count
        ramp_raw_wk, ramp_raw_ct = find_ramp_date(
            ct, 1, threshold=ramp_threshold, floor=ramp_floor)
        ramp_wt_wk, ramp_wt_ct = find_ramp_date(
            ct, 2, threshold=ramp_threshold, floor=ramp_floor)
        ramp_t1_wk, _ = find_ramp_date(
            ct, 3, threshold=ramp_threshold, floor=ramp_floor)
        ramp_t12_wk, _ = find_ramp_date(
            ct, 4, threshold=ramp_threshold, floor=ramp_floor)

        row["ramp_raw_week"] = ramp_raw_wk or ""
        row["ramp_raw_count"] = ramp_raw_ct or ""
        row["ramp_weighted_week"] = ramp_wt_wk or ""
        row["ramp_weighted_count"] = ramp_wt_ct or ""
        row["ramp_tier1_week"] = ramp_t1_wk or ""
        row["ramp_tier12_week"] = ramp_t12_wk or ""

        # Leads
        row["lead_raw_days"] = compute_lead(ramp_raw_wk, onset_cutoff)
        row["lead_weighted_days"] = compute_lead(ramp_wt_wk, onset_cutoff)
        row["lead_tier1_days"] = compute_lead(ramp_t1_wk, onset_cutoff)
        row["lead_tier12_days"] = compute_lead(ramp_t12_wk, onset_cutoff)

        # Signs
        row["sign_raw"] = compute_sign(row["lead_raw_days"])
        row["sign_weighted"] = compute_sign(row["lead_weighted_days"])
        row["sign_tier1"] = compute_sign(row["lead_tier1_days"])
        row["sign_tier12"] = compute_sign(row["lead_tier12_days"])

        if ramp_raw_wk is None:
            row["excluded_reason"] = "no_ramp (raw C(t) never reaches threshold)"
        else:
            row["excluded_reason"] = ""

        rows.append({k: row.get(k, "") for k in OUT_FIELDS})

    return rows


def summarize(rows, label, sign_col, lead_col):
    """Print sign-test summary for one count type."""
    testable = [r for r in rows if r.get("excluded_reason") == ""
                and r.get(sign_col) not in ("", None)]
    n_pos = sum(1 for r in testable if int(r[sign_col]) > 0)
    n_neg = sum(1 for r in testable if int(r[sign_col]) < 0)
    n_zero = sum(1 for r in testable if int(r[sign_col]) == 0)
    n_total = n_pos + n_neg  # ties excluded from sign test

    leads = [float(r[lead_col]) for r in testable
             if r.get(lead_col) not in ("", None)]
    median_lead = sorted(leads)[len(leads) // 2] if leads else 0

    p = sign_test_two_sided(min(n_pos, n_neg), n_total)

    print(f"\n  {label}:")
    print(f"    Ramp precedes onset: {n_pos}/{n_pos + n_neg + n_zero} "
          f"({100 * n_pos / (n_pos + n_neg + n_zero):.1f}%)"
          if (n_pos + n_neg + n_zero) else "    No testable entities")
    print(f"    Ties (lead=0): {n_zero}")
    print(f"    Median lead: {median_lead:.0f} days")
    print(f"    Sign test (two-sided): p = {p:.2e}  "
          f"(n_pos={n_pos}, n_neg={n_neg}, n_test={n_total})")

    return {
        "label": label,
        "n_precedes": n_pos,
        "n_total_testable": n_pos + n_neg + n_zero,
        "n_ties": n_zero,
        "median_lead": median_lead,
        "p_value": p,
    }


def main():
    print("=" * 70)
    print("PRECEDENCE TEST: Raw vs. Weighted Citation Ramp -> Perception Onset")
    print("=" * 70)
    print(f"\nRamp threshold: {RAMP_THRESHOLD * 100:.0f}% of peak "
          f"(floor={RAMP_FLOOR} mentions)")
    print(f"Onset threshold: P(t) >= {ONSET_SCORE}")

    rows = run_analysis()

    # Count exclusions
    excluded = [r for r in rows if r.get("excluded_reason")]
    by_reason = defaultdict(list)
    for r in excluded:
        by_reason[r["excluded_reason"]].append(r["entity"])
    print(f"\nEntity selection:")
    print(f"  Total in perception data: {len(rows)}")
    for reason, elist in sorted(by_reason.items()):
        print(f"  Excluded ({reason}): {len(elist)}  "
              f"[{', '.join(sorted(elist)[:5])}{'...' if len(elist) > 5 else ''}]")
    testable = [r for r in rows if not r.get("excluded_reason")]
    print(f"  Testable: {len(testable)}")

    # Run sign test for each count type
    print("\n" + "-" * 70)
    print("RESULTS")
    print("-" * 70)

    summaries = []
    summaries.append(summarize(rows, "Raw (original mention_count)",
                               "sign_raw", "lead_raw_days"))
    summaries.append(summarize(rows, "Weighted (continuous tier weights)",
                               "sign_weighted", "lead_weighted_days"))
    summaries.append(summarize(rows, "Tier 1 only (binary exclusion)",
                               "sign_tier1", "lead_tier1_days"))
    summaries.append(summarize(rows, "Tier 1+2 (binary exclusion)",
                               "sign_tier12", "lead_tier12_days"))

    # Comparison table
    print("\n" + "-" * 70)
    print("COMPARISON TABLE")
    print("-" * 70)
    print(f"{'Method':<35s} {'Precedes':>10s} {'Median lead':>12s} {'p-value':>12s}")
    print("-" * 70)
    baseline_label = "Raw (original paper)"
    print(f"{baseline_label:<35s} {'28/33':>10s} {'83 d':>12s} {'6.6e-05':>12s}")
    for s in summaries:
        n_str = f"{s['n_precedes']}/{s['n_total_testable']}"
        lead_str = f"{s['median_lead']:.0f} d"
        p_str = f"{s['p_value']:.2e}"
        print(f"{s['label']:<35s} {n_str:>10s} {lead_str:>12s} {p_str:>12s}")

    # Save per-entity CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nPer-entity results saved to {OUT_CSV}")

    # Interpretation guidance
    print("\n" + "=" * 70)
    print("INTERPRETATION NOTES")
    print("=" * 70)
    print("* If weighted p-value is LOWER than raw: weighting strengthens")
    print("  the relationship (source authority adds signal).")
    print("* If weighted p-value is HIGHER: weighting weakens it (authority")
    print("  filtering removes signal - low-authority sources carry the")
    print("  temporal information too).")
    print("* If p-values are similar: weighting doesn't help - source")
    print("  authority is orthogonal to the temporal precedence result.")
    print("* A null result (no difference) is a valid finding.")
    print("* Run sensitivity_analysis.py to check robustness across")
    print("  threshold combinations (mirrors Table 2 in the paper).")


if __name__ == "__main__":
    main()
