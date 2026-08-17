#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_tier_map.py  --  Evidence-based domain -> tier assignment
===============================================================================
PRIMARY METHOD: Approach B — empirical frequency clustering.
(External authority lists like NewsGuard / Moz DA are paywalled and not
accessible. If a genuinely free list surfaces — e.g. AP/Reuters partner
rosters — it can be added as a cross-check, not a replacement.)

This script does NOT assign tiers by "this outlet feels important." Every
boundary is derived from the observed domain-frequency distribution in
ct_source_all.csv. The tier assignment is then subjected to a boundary-
perturbation sensitivity check (Phase 4) to confirm the precedence test
result is stable.

APPROACH
--------
1. Count how many distinct entities each domain covers (breadth) and total
   article count across all entities (volume).
2. Cluster domains into tiers using natural breaks (Jenks optimization)
   on log(breadth × volume). Three tiers: high-authority (appears across
   many entities, high volume), mid-authority, low-authority.
3. Cross-check tier assignments against ct_artlist_precision.csv — do
   PASS entities draw more heavily from Tier 1 sources? (This is a sanity
   check, not the basis for tier assignment, because precision measures
   name-relevance, not source authority.)
4. Output the tier map with per-domain evidence columns so every assignment
   is traceable.

INPUTS
------
    data_derived/ct_source_all.csv  (output of merge_source_data.py)
    inputs_frozen/ct_artlist_precision.csv  (for cross-check only)

OUTPUTS
-------
    data_derived/domain_frequency_analysis.csv
        Per-domain: domain, entity_count, article_count, log_score,
        tier (once assigned)

    data_derived/domain_tier_map.csv
        Final tier map: domain, tier, entity_count, article_count,
        evidence_note

    data_derived/tier_cross_check.txt
        PASS vs. FAIL entity domain-mix comparison

    docs/tier_methodology.md is NOT auto-updated — fill it in manually
    from these outputs so the reasoning is in your own words.
"""

import csv
import math
import os
import sys
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data_derived")
FROZEN_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs_frozen")

SOURCE_ALL_CSV = os.path.join(DATA_DIR, "ct_source_all.csv")
PRECISION_CSV = os.path.join(FROZEN_DIR, "ct_artlist_precision.csv")

OUT_FREQ_ANALYSIS = os.path.join(DATA_DIR, "domain_frequency_analysis.csv")
OUT_TIER_MAP = os.path.join(DATA_DIR, "domain_tier_map.csv")
OUT_CROSS_CHECK = os.path.join(DATA_DIR, "tier_cross_check.txt")

# Number of tiers.  Three is the paper's template (Tier 1/2/3); only
# change this if the data's distribution clearly doesn't support three
# clusters (e.g. if Jenks variance-explained is low).
N_TIERS = 3


# ---------------------------------------------------------------------------
# Jenks natural breaks (Fisher-Caspall algorithm)
# ---------------------------------------------------------------------------
# Implemented from scratch to avoid a numpy/scipy dependency for a simple
# 1-D clustering.  This is the standard "goodness of variance fit" method
# used in cartographic classification.

def _jenks_matrices(data, n_classes):
    """Compute Jenks lower-class-limit and variance matrices."""
    n = len(data)
    lower = [[0] * (n_classes + 1) for _ in range(n + 1)]
    variance = [[float("inf")] * (n_classes + 1) for _ in range(n + 1)]
    variance[0][0] = 0.0

    for cl in range(1, n_classes + 1):
        lower[1][cl] = 1
        variance[1][cl] = 0.0

    for i in range(2, n + 1):
        s2 = 0.0
        s1 = 0.0
        for m in range(1, i + 1):
            val = data[i - m]  # 0-indexed
            s2 += val * val
            s1 += val
            w = m
            iv = s2 - (s1 * s1) / w
            if i != 1:
                for j in range(2, n_classes + 1):
                    test = iv + variance[i - m][j - 1]
                    if test < variance[i][j]:
                        lower[i][j] = i - m + 1
                        variance[i][j] = test
            variance[i][1] = iv
            lower[i][1] = 1

    return lower, variance


def jenks_breaks(data, n_classes):
    """
    Return n_classes-1 break values for sorted data using Jenks
    natural-breaks optimization.
    """
    if len(data) <= n_classes:
        return sorted(set(data))

    sorted_data = sorted(data)
    lower, _ = _jenks_matrices(sorted_data, n_classes)

    breaks = [sorted_data[0]]
    k = len(sorted_data)
    for j in range(n_classes, 1, -1):
        breaks.insert(1, sorted_data[lower[k][j] - 1])
        k = lower[k][j] - 1
    breaks.append(sorted_data[-1])

    # Return the inner break points (n_classes - 1 values)
    return breaks[1:-1]


def gvf(data, breaks):
    """Goodness of variance fit (0–1, higher = better separation)."""
    sorted_data = sorted(data)
    n = len(sorted_data)
    overall_mean = sum(sorted_data) / n
    sdam = sum((x - overall_mean) ** 2 for x in sorted_data)
    if sdam == 0:
        return 1.0

    # Assign classes
    thresholds = sorted(breaks)
    sdcm = 0.0
    idx = 0
    for b in thresholds + [float("inf")]:
        group = []
        while idx < n and sorted_data[idx] < b:
            group.append(sorted_data[idx])
            idx += 1
        # Include values equal to break in this group (except last)
        while idx < n and sorted_data[idx] == b and b != float("inf"):
            group.append(sorted_data[idx])
            idx += 1
        if group:
            gm = sum(group) / len(group)
            sdcm += sum((x - gm) ** 2 for x in group)

    return 1.0 - sdcm / sdam


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def load_source_data():
    """Load ct_source_all.csv, return list of dicts."""
    if not os.path.exists(SOURCE_ALL_CSV):
        print(f"Missing {SOURCE_ALL_CSV} — run merge_source_data.py first.")
        sys.exit(1)
    with open(SOURCE_ALL_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_precision():
    """Load precision audit verdicts: entity -> verdict."""
    verdicts = {}
    if os.path.exists(PRECISION_CSV):
        with open(PRECISION_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                verdicts[row["entity"]] = row["verdict"]
    return verdicts


def compute_domain_stats(rows):
    """
    For each domain, compute:
      - entity_count: number of distinct entities it appears with
      - article_count: total article rows
    Returns dict of domain -> {entity_count, article_count, log_score}
    """
    domain_entities = defaultdict(set)
    domain_articles = Counter()

    for r in rows:
        d = r.get("domain", "").strip()
        if not d:
            continue
        domain_entities[d].add(r["entity"])
        domain_articles[d] += 1

    stats = {}
    for d in domain_entities:
        ec = len(domain_entities[d])
        ac = domain_articles[d]
        # log_score: log(breadth * volume + 1) — the +1 avoids log(0)
        # for domains with entity_count=1, article_count=1
        ls = math.log(ec * ac + 1)
        stats[d] = {
            "domain": d,
            "entity_count": ec,
            "article_count": ac,
            "log_score": round(ls, 4),
        }
    return stats


# Standard convention for acceptable Jenks natural breaks fit is GVF >= 0.70.
GVF_THRESHOLD = 0.70

def assign_tiers(domain_stats, n_tiers=N_TIERS):
    """
    Assign tiers using Jenks natural breaks on log_score.
    Tier 1 = highest authority (highest log_score cluster).
    """
    scores = [s["log_score"] for s in domain_stats.values()]
    if len(set(scores)) <= n_tiers:
        # Not enough distinct values to cluster — fall back to equal-count bins
        print(f"[WARN] Only {len(set(scores))} distinct log_scores — "
              f"using equal-count quantile bins instead of Jenks.")
        sorted_scores = sorted(scores)
        breaks = [
            sorted_scores[int(len(sorted_scores) * i / n_tiers)]
            for i in range(1, n_tiers)
        ]
    else:
        breaks = jenks_breaks(scores, n_tiers)
        fit = gvf(scores, breaks)
        if fit >= GVF_THRESHOLD:
            print(f"[PASS] Jenks natural breaks GVF = {fit:.4f} >= {GVF_THRESHOLD:.2f} threshold  (breaks at {breaks})")
        else:
            print(f"[WARN] Jenks natural breaks GVF = {fit:.4f} < {GVF_THRESHOLD:.2f} threshold  (breaks at {breaks}). "
                  "Tier boundaries explain limited variance; check boundary stability in sensitivity_analysis.py.")

    # Assign: Tier 1 = above highest break, Tier 3 = below lowest break
    sorted_breaks = sorted(breaks, reverse=True)
    for d, s in domain_stats.items():
        tier = n_tiers  # default to lowest tier
        for i, b in enumerate(sorted_breaks):
            if s["log_score"] >= b:
                tier = i + 1
                break
        s["tier"] = tier

    return domain_stats


# ---------------------------------------------------------------------------
# Cross-check against precision audit
# ---------------------------------------------------------------------------

def cross_check(rows, domain_stats, precision_verdicts, outpath):
    """
    Compare the domain mix for PASS vs. FAIL entities.
    This is a SANITY CHECK — precision measures name-relevance, not
    source authority. We're looking for: do PASS entities draw from
    recognizably different sources than FAIL entities? If not, that's fine
    — it just means precision and authority are orthogonal, as expected.
    """
    pass_domains = Counter()
    fail_domains = Counter()

    for r in rows:
        d = r.get("domain", "").strip()
        if not d:
            continue
        v = precision_verdicts.get(r["entity"], "NOT_AUDITED")
        if v == "PASS":
            pass_domains[d] += 1
        elif v == "FAIL":
            fail_domains[d] += 1

    with open(outpath, "w", encoding="utf-8") as f:
        f.write("TIER CROSS-CHECK: PASS vs. FAIL Entity Domain Mix\n")
        f.write("=" * 60 + "\n")
        f.write("NOTE: Precision audit measures NAME-RELEVANCE, not source\n")
        f.write("authority. This cross-check looks for whether the two\n")
        f.write("constructs happen to correlate in this data, but tier\n")
        f.write("assignments must NOT be based on this.\n\n")

        # Tier distribution for PASS vs. FAIL
        for label, domain_counts in [("PASS", pass_domains),
                                      ("FAIL", fail_domains)]:
            tier_counts = Counter()
            total = sum(domain_counts.values())
            for d, c in domain_counts.items():
                t = domain_stats.get(d, {}).get("tier", "?")
                tier_counts[t] += c

            f.write(f"\n{label} entities ({total} total article rows):\n")
            for t in sorted(tier_counts):
                pct = 100 * tier_counts[t] / total if total else 0
                f.write(f"  Tier {t}: {tier_counts[t]:>5d} rows "
                        f"({pct:5.1f}%)\n")

    print(f"Cross-check written to {outpath}")


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_frequency_analysis(domain_stats, outpath):
    """Write per-domain frequency analysis CSV."""
    fields = ["domain", "entity_count", "article_count", "log_score", "tier"]
    sorted_domains = sorted(
        domain_stats.values(),
        key=lambda s: s["log_score"],
        reverse=True,
    )
    with open(outpath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for s in sorted_domains:
            w.writerow({k: s.get(k, "") for k in fields})
    print(f"Frequency analysis: {outpath}  ({len(sorted_domains)} domains)")


def write_tier_map(domain_stats, outpath):
    """
    Write the final tier map: domain, tier, evidence columns.
    This is what apply_weights.py consumes.
    """
    fields = ["domain", "tier", "entity_count", "article_count",
              "log_score", "evidence_note"]

    sorted_domains = sorted(
        domain_stats.values(),
        key=lambda s: (s.get("tier", 99), -s["log_score"]),
    )

    with open(outpath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for s in sorted_domains:
            row = {k: s.get(k, "") for k in fields}
            row["evidence_note"] = (
                f"breadth={s['entity_count']} entities, "
                f"volume={s['article_count']} articles, "
                f"log_score={s['log_score']}"
            )
            w.writerow(row)
    print(f"Tier map: {outpath}  ({len(sorted_domains)} domains)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    rows = load_source_data()
    precision = load_precision()
    print(f"Loaded {len(rows)} article rows from {SOURCE_ALL_CSV}")

    domain_stats = compute_domain_stats(rows)
    print(f"Found {len(domain_stats)} unique normalized domains")

    domain_stats = assign_tiers(domain_stats)

    # Summary
    tier_counts = Counter(s["tier"] for s in domain_stats.values())
    for t in sorted(tier_counts):
        examples = sorted(
            [d for d, s in domain_stats.items() if s["tier"] == t],
            key=lambda d: domain_stats[d]["log_score"],
            reverse=True,
        )[:5]
        print(f"  Tier {t}: {tier_counts[t]:>4d} domains  "
              f"(top: {', '.join(examples)})")

    write_frequency_analysis(domain_stats, OUT_FREQ_ANALYSIS)
    write_tier_map(domain_stats, OUT_TIER_MAP)
    cross_check(rows, domain_stats, precision, OUT_CROSS_CHECK)

    print("\nNext steps:")
    print("  1. Review tier assignments - spot-check 5-10 domains by visiting")
    print("     the actual sites. Document in docs/tier_methodology.md.")
    print("  2. Run apply_weights.py to compute weighted C(t).")
    print("  3. Run sensitivity_analysis.py to check boundary stability.")


if __name__ == "__main__":
    main()
