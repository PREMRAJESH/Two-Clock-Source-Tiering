#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reproduce_baseline.py  --  Exact reproduction of the paper's 28/33 result
==========================================================================
Exclusion rule from Viveka, verified against the paper text:

  TESTABLE 33 = all 50 entities MINUS:
    - 10 precision-audit FAIL entities (Section 4.5, Table 1):
          DBRX, Kimi, Ideogram, Lovable, Gemini (Google model),
          Dream Machine, Liquid AI, Mamba, Operator, vLLM
    - 7 no-onset entities (Section 5.4, exact list):
          OpenAI o1, OpenAI o3, DeepSeek, DeepSeek-R1,
          Manus, World Labs, Bolt.new

  The self_ref_openai flag in entities.py is NOT used for this baseline.
  GPT-4, GPT-4o, and Sora are included in the 33.

Expected result: 28/33, median lead 83 days, p = 6.62e-05
for BOTH floor=3 and floor=5.

NAME MISMATCH HANDLING
----------------------
The perception CSV (pt_pilot_results.csv) uses parenthetical disambiguators
like "Cursor (the AI code editor)" while the citation CSV (ct_results_v1_frozen.csv)
uses shorter names like "Cursor". This script builds a canonical name bridge
using the base name (stripping parentheticals) to join the two datasets.

INPUTS (frozen data only -- no weighted CSV needed)
------
    inputs_frozen/ct_results_v1_frozen.csv
    inputs_frozen/pt_pilot_results.csv
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

FROZEN_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs_frozen")
CT_CSV = os.path.join(FROZEN_DIR, "ct_results_v1_frozen.csv")
PT_CSV = os.path.join(FROZEN_DIR, "pt_pilot_results.csv")

# ---------------------------------------------------------------------------
# The EXACT exclusion lists from the paper (using CT/short names)
# ---------------------------------------------------------------------------

# Section 4.5 Table 1: 10 precision-audit FAIL entities
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

# Section 5.4: 7 no-onset entities
NO_ONSET = {
    "OpenAI o1",
    "OpenAI o3",
    "DeepSeek",
    "DeepSeek-R1",
    "Manus",
    "World Labs",
    "Bolt.new",
}

ALL_EXCLUDED = PRECISION_FAIL | NO_ONSET  # 17 names


# ---------------------------------------------------------------------------
# Name normalization: bridge PT names <-> CT names
# ---------------------------------------------------------------------------

def _base_name(entity_name):
    """Strip parenthetical disambiguators: 'Cursor (the AI code editor)' -> 'Cursor'."""
    idx = entity_name.find(" (")
    if idx > 0:
        return entity_name[:idx]
    return entity_name


def build_name_bridge(pt_entities, ct_entities):
    """
    Build a mapping from PT entity names to CT entity names.
    Handles the parenthetical disambiguator mismatch between the two CSVs.

    Returns: dict mapping pt_name -> ct_name
    """
    bridge = {}
    # Direct matches first
    for pt_name in pt_entities:
        if pt_name in ct_entities:
            bridge[pt_name] = pt_name
        else:
            # Try base name match
            base = _base_name(pt_name)
            if base in ct_entities:
                bridge[pt_name] = base
            else:
                # Try matching CT names that share the same base
                for ct_name in ct_entities:
                    if _base_name(ct_name) == base:
                        bridge[pt_name] = ct_name
                        break
    return bridge


def is_excluded(entity_name):
    """Check if entity matches any of the 17 excluded names (using CT short names)."""
    if entity_name in ALL_EXCLUDED:
        return True
    base = _base_name(entity_name)
    if base in ALL_EXCLUDED:
        return True
    return False


# ---------------------------------------------------------------------------
# Sign test (exact two-sided, no scipy)
# ---------------------------------------------------------------------------

def _comb(n, k):
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
    if n_total == 0:
        return 1.0
    k = min(n_positive, n_total - n_positive)
    p = 0.0
    for i in range(k + 1):
        p += _comb(n_total, i)
    p *= 2
    p /= 2 ** n_total
    return min(p, 1.0)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_perception():
    """entity -> list of (cutoff, max_score) sorted by cutoff."""
    raw = defaultdict(list)
    for r in csv.DictReader(open(PT_CSV, encoding="utf-8")):
        raw[r["entity"]].append((r["reported_cutoff"], int(r["score"])))
    perception = {}
    for entity, pairs in raw.items():
        by_cutoff = defaultdict(int)
        for cutoff, score in pairs:
            by_cutoff[cutoff] = max(by_cutoff[cutoff], score)
        perception[entity] = sorted(by_cutoff.items())
    return perception


def load_raw_citation_series():
    """entity -> list of (week_start, mention_count) sorted by week."""
    series = defaultdict(list)
    for r in csv.DictReader(open(CT_CSV, encoding="utf-8")):
        mc = int(r["mention_count"])
        series[r["entity"]].append((r["week_start"], mc))
    for e in series:
        series[e].sort()
    return series


# ---------------------------------------------------------------------------
# Ramp and onset
# ---------------------------------------------------------------------------

def find_ramp_date(weekly_data, threshold, floor):
    """First week where mention_count >= max(threshold * peak, floor)."""
    if not weekly_data:
        return None
    peak = max(mc for _, mc in weekly_data)
    if peak <= 0:
        return None
    ramp_level = max(threshold * peak, floor)
    for week, mc in weekly_data:
        if mc >= ramp_level:
            return week
    return None


def find_onset_date(perception_ladder, min_score=3):
    """First cutoff where score >= min_score."""
    for cutoff, score in perception_ladder:
        if score >= min_score:
            return cutoff
    return None


def compute_lead(ramp_week, onset_cutoff):
    """Lead in days = onset - ramp. Positive = ramp precedes onset."""
    r = datetime.strptime(ramp_week, "%Y-%m-%d")
    o = datetime.strptime(onset_cutoff + "-01", "%Y-%m-%d")
    return (o - r).days


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_baseline(ramp_threshold, ramp_floor, onset_score):
    """Run the baseline precedence test with the paper's exact exclusion rule."""
    perception = load_perception()
    citation = load_raw_citation_series()

    # Build name bridge between PT and CT entity names
    pt_entities = set(perception.keys())
    ct_entities = set(citation.keys())
    bridge = build_name_bridge(pt_entities, ct_entities)

    leads = []
    included = []
    excluded_detail = []

    for pt_name in sorted(perception.keys()):
        ct_name = bridge.get(pt_name)

        # Check exclusion using BOTH name forms
        if is_excluded(pt_name) or (ct_name and is_excluded(ct_name)):
            excluded_detail.append((pt_name, "paper_exclusion"))
            continue

        # Onset check
        onset = find_onset_date(perception[pt_name], min_score=onset_score)
        if onset is None:
            excluded_detail.append((pt_name, f"no_onset (max P < {onset_score})"))
            continue

        # Citation series (using CT name via bridge)
        if ct_name is None:
            excluded_detail.append((pt_name, "no_citation_data (name not bridgeable)"))
            continue

        ct = citation.get(ct_name, [])
        if not ct:
            excluded_detail.append((pt_name, "no_citation_data"))
            continue

        ramp = find_ramp_date(ct, ramp_threshold, ramp_floor)
        if ramp is None:
            excluded_detail.append((pt_name, "no_ramp"))
            continue

        lead = compute_lead(ramp, onset)
        leads.append(lead)
        sign = "+" if lead > 0 else ("0" if lead == 0 else "-")
        included.append((pt_name, ramp, onset, lead, sign))

    # Stats
    n_pos = sum(1 for l in leads if l > 0)
    n_neg = sum(1 for l in leads if l < 0)
    n_zero = sum(1 for l in leads if l == 0)
    n_test = n_pos + n_neg  # ties excluded from sign test
    n_total = len(leads)
    median_lead = sorted(leads)[len(leads) // 2] if leads else 0
    p = sign_test_two_sided(min(n_pos, n_neg), n_test)

    return {
        "included": included,
        "excluded": excluded_detail,
        "n_pos": n_pos,
        "n_neg": n_neg,
        "n_zero": n_zero,
        "n_total": n_total,
        "median_lead": median_lead,
        "p_value": p,
        "bridge": bridge,
    }


def main():
    print("=" * 72)
    print("BASELINE REPRODUCTION: Paper Section 4.6 / 5.4 exact rule")
    print("=" * 72)
    print()
    print("Exclusion rule (from Viveka, verified against paper):")
    print("  - 10 precision-audit FAIL (Section 4.5, Table 1)")
    print("  - 7 no-onset entities (Section 5.4)")
    print("  - self_ref_openai flag NOT applied for this baseline")
    print()

    # Show name bridge for transparency
    perception = load_perception()
    citation = load_raw_citation_series()
    bridge = build_name_bridge(set(perception.keys()), set(citation.keys()))
    mismatched = [(pt, ct) for pt, ct in sorted(bridge.items()) if pt != ct]
    if mismatched:
        print("Name bridge (PT name -> CT name):")
        for pt, ct in mismatched:
            print(f"  {pt:45s} -> {ct}")
        print()

    for floor in [3, 5]:
        print("-" * 72)
        print(f"  RAMP FLOOR = {floor}")
        print("-" * 72)
        res = run_baseline(ramp_threshold=0.10, ramp_floor=floor, onset_score=3)

        print(f"  Testable entities: {res['n_total']}")
        print(f"  Ramp precedes onset: {res['n_pos']}/{res['n_total']}")
        print(f"  Ties (lead=0): {res['n_zero']}")
        print(f"  Median lead: {res['median_lead']} days")
        print(f"  p-value (two-sided exact sign test): {res['p_value']:.2e}")
        print()

        # Check
        ok_n = (res['n_total'] == 33)
        ok_precedes = (res['n_pos'] == 28)
        ok_median = (res['median_lead'] == 83)
        ok_p = abs(res['p_value'] - 6.62e-5) < 1e-6

        status = "PASS" if (ok_n and ok_precedes and ok_median and ok_p) else "FAIL"
        print(f"  CHECK n_total=33:    {'OK' if ok_n else 'MISMATCH: ' + str(res['n_total'])}")
        print(f"  CHECK precedes=28:   {'OK' if ok_precedes else 'MISMATCH: ' + str(res['n_pos'])}")
        print(f"  CHECK median=83d:    {'OK' if ok_median else 'MISMATCH: ' + str(res['median_lead'])}")
        print(f"  CHECK p~6.62e-05:    {'OK' if ok_p else 'MISMATCH: ' + str(res['p_value'])}")
        print(f"  >>> FLOOR={floor}: {status}")
        print()

        if not (ok_n and ok_precedes):
            print("  --- Per-entity detail ---")
            for entity, ramp, onset, lead, sign in res["included"]:
                print(f"    {sign} {entity:45s} ramp={ramp}  onset={onset}  lead={lead:+d}d")
            print()
            print("  --- Excluded ---")
            for entity, reason in res["excluded"]:
                print(f"    X {entity:45s} {reason}")
            print()


if __name__ == "__main__":
    main()
