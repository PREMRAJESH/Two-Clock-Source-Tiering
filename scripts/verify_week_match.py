#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_week_match.py  --  The Kimi/Mamba spot-check Viveka asked for
==========================================================================
*** SUPERSEDED (2026-08-18) — STALE SCAFFOLDING, DO NOT RUN AS-IS ***
--------------------------------------------------------------------------
This script is retained for provenance only. It was early scaffolding written
against a guessed column layout and Viveka's since-abandoned `other_week`
median-count rule. That whole approach was replaced on 2026-08-18 by the
deterministic v2 `contrast_week()` method (see scripts/*contrast* and
docs/session_log.md). The `other_week` median rule proved unrecoverable, so
the premise of this check no longer holds and its assumptions below (guessed
CSV/label column names, per-entity single-week model) are known to be wrong.

Do NOT run this as part of the pipeline or treat its output as authoritative.
Kept, not deleted, so the reasoning trail from the original spot-check request
survives. If you need the week-alignment check, use the v2 contrast_week logic
instead.
--------------------------------------------------------------------------
BEFORE ANYTHING ELSE ON SOURCE-WEIGHTING PROCEEDS, this needs to pass.

Compares the `other_week` her ct_artlist_harvester.py picked (median-count
week, by her own description) against the week already recorded for the
same entity in ct_artlist_LABELING.xlsx. If they match for Kimi and Mamba,
her method is confirmed compatible with the existing labeled data. If they
don't, tell her before anyone builds weighting logic on either dataset.

ASSUMPTIONS -- CHECK THESE AGAINST THE REAL FILES BEFORE TRUSTING OUTPUT
--------------------------------------------------------------------------
This was written without seeing her actual ct_artlist_harvester.py or its
real output CSV -- only her description in chat ("outputs
ct_artlist_results.csv" with an "other_week" column). Column names below
are best guesses. Open ct_artlist_results.csv and ct_artlist_LABELING.xlsx
yourself first and fix CSV_WEEK_COL / LABEL_WEEK_COL / LABEL_ENTITY_COL
below to match what's actually there -- don't run this blind.

USAGE
-----
    pip install openpyxl pandas
    python verify_week_match.py

OUTPUT
------
Prints a match/mismatch table for every entity present in both files,
with Kimi and Mamba called out first since those are the ones she asked
about by name.
"""

import pandas as pd

CT_ARTLIST_RESULTS = "../data_derived/ct_artlist_results.csv"   # her script's output -- copy it here once you have it
LABELING_XLSX = "../inputs_frozen/ct_artlist_LABELING.xlsx"      # copy the .xlsx here too (not in inputs_frozen yet -- add it)

# TODO: confirm these against the real files
CSV_ENTITY_COL = "entity"
CSV_WEEK_COL = "other_week"
LABEL_ENTITY_COL = "entity"
LABEL_WEEK_COL = "window"   # her screenshot showed a `date` column per row, not
                             # one week per entity -- if the labeling file has
                             # per-article dates rather than one week per entity,
                             # this needs to derive "the week" from those dates
                             # (e.g. the most common week among labeled rows)
                             # before comparing. Fix this once you see the real
                             # column layout.

PRIORITY_ENTITIES = ["Kimi", "Mamba"]


def main():
    try:
        results = pd.read_csv(CT_ARTLIST_RESULTS)
    except FileNotFoundError:
        print(f"Missing {CT_ARTLIST_RESULTS} -- run ct_artlist_harvester.py "
              f"and copy its output here first.")
        return
    try:
        labeled = pd.read_excel(LABELING_XLSX)
    except FileNotFoundError:
        print(f"Missing {LABELING_XLSX} -- copy the .xlsx into inputs_frozen/ first.")
        return

    # one row per entity from her results (assumes one other_week per entity;
    # if her CSV has multiple rows per entity, this takes the first -- check
    # that's actually right once you see the real shape)
    results_by_entity = results.groupby(CSV_ENTITY_COL)[CSV_WEEK_COL].first()

    # for the labeling file: if it's one row per article (not per entity),
    # derive the dominant week per entity here. Placeholder: assumes
    # LABEL_WEEK_COL already IS one value per entity -- fix if not.
    labeled_by_entity = labeled.groupby(LABEL_ENTITY_COL)[LABEL_WEEK_COL].first()

    common = sorted(set(results_by_entity.index) & set(labeled_by_entity.index))
    ordered = [e for e in PRIORITY_ENTITIES if e in common] + \
              [e for e in common if e not in PRIORITY_ENTITIES]

    print(f"{'entity':28s} {'her other_week':18s} {'labeled week':18s} match?")
    n_match, n_mismatch = 0, 0
    for e in ordered:
        a = str(results_by_entity.get(e, "—"))
        b = str(labeled_by_entity.get(e, "—"))
        ok = (a == b)
        n_match += ok
        n_mismatch += not ok
        flag = "PRIORITY " if e in PRIORITY_ENTITIES else "          "
        print(f"{flag}{e:18s} {a:18s} {b:18s} {'OK' if ok else 'MISMATCH'}")

    print(f"\n{n_match} match, {n_mismatch} mismatch, out of {len(ordered)} compared.")
    if n_mismatch:
        print("Do not proceed with weighting until this is resolved with Viveka.")


if __name__ == "__main__":
    main()
