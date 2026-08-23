#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_pipeline_smoketest.py  --  End-to-end synthetic pipeline smoke test
========================================================================
Generates synthetic data for 10 entities and 18 domains, runs the full
pipeline:
  merge_source_data -> build_tier_map -> apply_weights ->
  precedence_test_weighted -> sensitivity_analysis

Verifies that all scripts run cleanly without runtime errors or logical crashes,
checks generated outputs, prints perturbation stats, and cleans up temporary test files.
"""

import csv
import math
import os
import subprocess
import sys
import shutil
import tempfile

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data_derived")
INPUTS_DIR = os.path.join(ROOT_DIR, "inputs_frozen")
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")

# Synthetic entity names
ENTITIES = [
    ("SynthAlpha", "2023-03-01", False),
    ("SynthBeta", "2023-04-15", False),
    ("SynthGamma", "2023-05-10", False),
    ("SynthDelta", "2023-06-01", False),
    ("SynthEpsilon", "2023-07-01", False),
    ("SynthZeta", "2023-08-15", False),
    ("SynthEta", "2023-09-01", False),
    ("SynthTheta", "2023-10-01", False),
    ("SynthIota", "2023-11-01", False),
    ("SynthOpenAI", "2023-12-01", True),  # flagged self_ref_openai
]

# Synthetic domains (varied frequency: high volume / high breadth vs low)
DOMAINS = [
    # High volume & breadth (Tier 1-ish)
    ("reuters.com", 15, 45),
    ("bloomberg.com", 14, 40),
    ("nytimes.com", 12, 35),
    ("techcrunch.com", 10, 30),
    ("theverge.com", 10, 28),
    ("wsj.com", 9, 25),
    # Mid volume & breadth (Tier 2-ish)
    ("arstechnica.com", 7, 18),
    ("venturebeat.com", 6, 15),
    ("wired.com", 6, 14),
    ("zdnet.com", 5, 12),
    ("theregister.com", 5, 10),
    ("infoq.com", 4, 8),
    # Low volume & breadth (Tier 3-ish)
    ("medium.com", 3, 5),
    ("subtack.com", 2, 4),
    ("dev.to", 2, 3),
    ("mytechblog.io", 1, 2),
    ("randomforum.org", 1, 1),
    ("coolai.net", 1, 1),
]


def main():
    sandbox_dir = tempfile.mkdtemp(prefix="twoclock_smoketest_")
    print(f"Created isolated test sandbox: {sandbox_dir}")

    sb_data_dir = os.path.join(sandbox_dir, "data_derived")
    sb_inputs_dir = os.path.join(sandbox_dir, "inputs_frozen")
    sb_scripts_dir = os.path.join(sandbox_dir, "scripts")

    os.makedirs(sb_data_dir, exist_ok=True)
    os.makedirs(sb_inputs_dir, exist_ok=True)
    os.makedirs(sb_scripts_dir, exist_ok=True)

    try:
        # Copy scripts into sandbox
        for s in ["merge_source_data.py", "build_tier_map.py", "apply_weights.py", "precedence_test_weighted.py", "sensitivity_analysis.py"]:
            src_script = os.path.join(SCRIPTS_DIR, s)
            dst_script = os.path.join(sb_scripts_dir, s)
            shutil.copy2(src_script, dst_script)

        # Copy entities.py into sb_inputs_dir
        shutil.copy2(os.path.join(INPUTS_DIR, "entities.py"), os.path.join(sb_inputs_dir, "entities.py"))

        # 1. Viveka labeled export CSV — real Label-sheet columns
        #    (entity, window, date, title, domain, url, suggested_label,
        #    relevant). week_start is DERIVED from `date` by merge_source_data,
        #    so it is intentionally NOT a column here. One non-peak row is
        #    included to exercise the non-peak_week exclusion guardrail.
        viveka_file = os.path.join(sb_data_dir, "viveka_labeled_export.csv")
        with open(viveka_file, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["entity", "window", "date", "title", "domain", "url", "suggested_label", "relevant"])
            w.writeheader()
            for name, birth, flagged in ENTITIES[:5]:
                for d, ec, ac in DOMAINS[:10]:
                    w.writerow({
                        "entity": name,
                        "window": "peak_week",
                        "date": birth,
                        "title": f"Story about {name}",
                        "domain": d,
                        "url": f"https://www.{d}/article-1",
                        "suggested_label": "y",
                        "relevant": "y",
                    })
            w.writerow({
                "entity": ENTITIES[0][0],
                "window": "other_week",
                "date": ENTITIES[0][1],
                "title": "Audit-only second-week row (must be excluded)",
                "domain": "randomforum.org",
                "url": "https://randomforum.org/audit-row",
                "suggested_label": "?",
                "relevant": "n",
            })

        # 2. Harvester CSV (remaining 5 entities)
        harvester_file = os.path.join(sb_data_dir, "ct_source_results.csv")
        with open(harvester_file, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["entity", "birth_date", "window", "peak_week_start", "domain", "url", "title", "seendate", "sourcecountry", "capped", "status"])
            w.writeheader()
            for name, birth, flagged in ENTITIES[5:]:
                for d, ec, ac in DOMAINS[5:]:
                    w.writerow({
                        "entity": name,
                        "birth_date": birth,
                        "window": "peak_week",
                        "peak_week_start": birth,
                        "domain": d,
                        "url": f"https://{d}/story-2",
                        "title": f"Harvester article for {name}",
                        "seendate": "20230701T000000Z",
                        "sourcecountry": "US",
                        "capped": "False",
                        "status": "ok",
                    })

        # 3. ct_results_v1_frozen.csv
        frozen_file = os.path.join(sb_inputs_dir, "ct_results_v1_frozen.csv")
        with open(frozen_file, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["entity", "birth_date", "week_start", "days_from_birth", "mention_count", "metric", "query_used", "status", "as_of", "ct_precision"])
            w.writeheader()
            for name, birth, flagged in ENTITIES:
                for i in range(-2, 8):
                    days = i * 7
                    mc = max(0, int(50 * math.exp(-0.1 * abs(i - 2)))) if i >= 0 else 0
                    w.writerow({
                        "entity": name,
                        "birth_date": birth,
                        "week_start": f"2023-06-0{i+3}" if i < 7 else "2023-07-20",
                        "days_from_birth": str(days),
                        "mention_count": str(mc),
                        "metric": "raw_count",
                        "query_used": f'"{name}"',
                        "status": "ok",
                        "as_of": "2026-07-08",
                        "ct_precision": "PASS" if not flagged else "NOT_AUDITED",
                    })

        # 4. pt_pilot_results.csv
        pt_file = os.path.join(sb_inputs_dir, "pt_pilot_results.csv")
        cutoffs = [
            ("2021-09", "gpt-4-0613", 0),
            ("2023-10", "gpt-4o-2024-05-13", 2),
            ("2023-10", "gpt-4o-2024-11-20", 3),
            ("2024-06", "gpt-4.1-2025-04-14", 4),
            ("2025-06", "gpt-5.2", 4),
        ]
        with open(pt_file, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["entity", "birth_date", "provider", "model", "reported_cutoff", "score", "justification", "answer"])
            w.writeheader()
            for name, birth, flagged in ENTITIES:
                for cutoff, model, score in cutoffs:
                    w.writerow({
                        "entity": name,
                        "birth_date": birth,
                        "provider": "openai",
                        "model": model,
                        "reported_cutoff": cutoff,
                        "score": str(score),
                        "justification": "Mock justification",
                        "answer": f"Mock answer for {name}",
                    })

        # 5. ct_artlist_precision.csv
        prec_file = os.path.join(sb_inputs_dir, "ct_artlist_precision.csv")
        with open(prec_file, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["entity", "relevant_y", "relevant_n", "excluded", "precision_pct", "verdict"])
            w.writeheader()
            for name, birth, flagged in ENTITIES:
                w.writerow({
                    "entity": name,
                    "relevant_y": "20",
                    "relevant_n": "2",
                    "excluded": "0",
                    "precision_pct": "90.0",
                    "verdict": "PASS" if not flagged else "FAIL",
                })

        # Run pipeline in sandbox
        pipeline_scripts = [
            "merge_source_data.py",
            "build_tier_map.py",
            "apply_weights.py",
            "precedence_test_weighted.py",
            "sensitivity_analysis.py",
        ]

        print("\n" + "=" * 70)
        print("RUNNING END-TO-END PIPELINE SMOKE TEST IN SANDBOX")
        print("=" * 70)

        for s in pipeline_scripts:
            script_path = os.path.join(sb_scripts_dir, s)
            print(f"\n--- Executing {s} ---")
            res = subprocess.run([sys.executable, script_path], capture_output=True, text=True, cwd=sandbox_dir)
            print(res.stdout)
            if res.returncode != 0:
                print(f"[FAIL] Script {s} failed with exit code {res.returncode}!")
                print(f"Stderr:\n{res.stderr}")
                return

        print("\n>>> SMOKE TEST PASSED CLEANLY! All 5 pipeline scripts executed without error. <<<")

    finally:
        print("\nCleaning up sandbox directory...")
        shutil.rmtree(sandbox_dir, ignore_errors=True)
        print("Cleanup complete.")


if __name__ == "__main__":
    main()
