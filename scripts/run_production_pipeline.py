#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_production_pipeline.py  --  Master Pipeline Runner
===============================================================================
Orchestrates the entire analytical source-tiering pipeline end-to-end:
  1. merge_source_data.py        (Merge Lane A + Lane B into ct_source_all.csv)
  2. build_tier_map.py           (Natural breaks Jenks clustering into 3 tiers)
  3. apply_weights.py            (Apply tier weights to weekly citation counts)
  4. precedence_test_weighted.py (Precedence sign test with --merged consensus)
  5. sensitivity_analysis.py     (90-cell sensitivity grid sweep)

Usage:
  python scripts/run_production_pipeline.py
"""

import os
import subprocess
import sys
import time

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPTS_DIR, ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data_derived")


def check_prerequisites():
    """Verify input files exist before starting pipeline."""
    v_csv = os.path.join(DATA_DIR, "viveka_labeled_export.csv")
    h_csv = os.path.join(DATA_DIR, "ct_source_results.csv")
    missing = []
    if not os.path.isfile(v_csv):
        missing.append("data_derived/viveka_labeled_export.csv (Lane A)")
    if not os.path.isfile(h_csv):
        missing.append("data_derived/ct_source_results.csv (Lane B)")
    if missing:
        print("[ERROR] Missing required input files:")
        for m in missing:
            print("  -", m)
        return False
    return True


def run_stage(script_name, args=None):
    """Run a pipeline script and handle errors."""
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, script_name)]
    if args:
        cmd.extend(args)
    display_cmd = "python scripts/%s %s" % (script_name, " ".join(args or []))
    print("\n" + "=" * 70)
    print("STAGE: %s" % display_cmd.strip())
    print("=" * 70)
    start_time = time.time()
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    elapsed = time.time() - start_time
    if result.returncode != 0:
        print("\n[FAIL] %s failed with exit code %d (elapsed: %.1fs)" % (script_name, result.returncode, elapsed))
        sys.exit(result.returncode)
    print("[PASS] %s completed in %.1fs" % (script_name, elapsed))


def main():
    print("Two-Clock Source-Tiering -- Master Production Pipeline Runner")
    print("Workspace: %s" % REPO_ROOT)

    if not check_prerequisites():
        sys.exit(1)

    # 1. Merge source datasets
    run_stage("merge_source_data.py")

    # 2. Build tier map via natural breaks clustering
    run_stage("build_tier_map.py")

    # 3. Apply weights to citation counts
    run_stage("apply_weights.py")

    # 4. Precedence Sign Test (using consensus multi-run perception)
    run_stage("precedence_test_weighted.py", args=["--merged"])

    # 5. Full sensitivity analysis sweeps
    run_stage("sensitivity_analysis.py")

    print("\n" + "=" * 70)
    print("ALL PRODUCTION PIPELINE STAGES COMPLETED SUCCESSFULLY!")
    print("Derived outputs saved to data_derived/:")
    print("  - ct_source_all.csv")
    print("  - domain_tier_map.csv")
    print("  - ct_results_weighted.csv")
    print("  - precedence_comparison.csv")
    print("  - sensitivity_results.csv")
    print("=" * 70)


if __name__ == "__main__":
    main()
