#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ct_artlist_harvester.py  --  Article-level source data for C(t), all 50 entities
==================================================================================
Companion to ct_harvester.py. THAT script calls GDELT's TimelineVolRaw mode,
which by design returns only a per-day/per-week AGGREGATE COUNT -- no article
titles, domains, or URLs are available in that mode, for anyone, ever. This
script calls a DIFFERENT GDELT mode -- ArtList -- which returns the individual
articles themselves (title, domain, url, seendate) for a query + date window.

This is what produced ct_artlist_LABELING.xlsx / ct_artlist_precision.csv, but
that pull only covered 22 of the 50 entities (the ones that failed or needed
manual review in the precision audit). This script runs the same kind of pull
across ALL 50, so source/domain-level weighting isn't limited to a subset.

WHAT IT DOES
------------
For each of the 50 entities (list + queries imported directly from
ct_harvester.py so the two scripts can never drift out of sync):
  1. Reads ct_results_v1_frozen.csv to find that entity's PEAK week
     (highest mention_count, status=ok) -- this is "peak_week".
  2. Picks a second, non-adjacent week as "other_week" -- see
     OTHER_WEEK_STRATEGY below. This is an ASSUMPTION about how the original
     22-entity file chose its other_week; confirm against that file before
     treating this script's other_week choice as equivalent.
  3. Calls GDELT DOC 2.0 API (mode=ArtList) for each of those two weeks.
  4. Writes one row per returned article: entity, window, date, title,
     domain, url -- same column shape as ct_artlist_LABELING.xlsx's "Label"
     sheet (minus the manual suggested_label/relevant columns, added blank
     so this can be pasted straight into that workflow).

OUTPUT
------
  ct_artlist_results.csv   one row per entity x window x article.

IMPORTANT CAVEATS -- READ BEFORE TRUSTING A NUMBER
----------------------------------------------------
* GDELT's ArtList mode caps at 250 articles PER CALL (MAXRECORDS below). A
  week with more matching articles than that will be silently truncated to
  the top N by the `SORT` order -- this script uses "HybridRel" (relevance),
  matching the likely method behind the existing 22-entity file (its per-
  window counts of 25-50 look like a smaller, possibly hand-set maxrecords
  or a relevance cutoff, not a raw firehose). If exact parity with that file
  matters, check its actual pull parameters before relying on this default.
* other_week selection here is a guess (see OTHER_WEEK_STRATEGY) -- it is
  NOT confirmed to match however the original 22-entity file picked its
  other_week rows. Spot-check a shared entity (e.g. Kimi, Mamba) between
  this output and ct_artlist_LABELING.xlsx before assuming the methodology
  lines up.
* Same disambiguation caveat as ct_harvester.py: short/collision-prone names
  (Kimi, Sora, Suno, Operator, Manus, Mamba, etc.) use the same
  QUERY_OVERRIDES, but article-level review is exactly how you catch a
  collision that a bare count couldn't show you -- expect some of these
  entities to need the same manual relevant=y/n pass as the first 22.
* GDELT's English-language dominance caveat applies here too (Kimi, Qwen,
  DeepSeek will undercount non-English coverage).
* Entities with NO ok weeks in ct_results_v1_frozen.csv (all chunk_failed)
  are skipped -- there's no peak week to anchor on. Re-run ct_harvester.py
  for those first.

SETUP / RUN
-----------
    py -m pip install requests
    py ct_artlist_harvester.py

Must be run from the same folder as ct_harvester.py (imports from it) and
ct_results_v1_frozen.csv (or edit FROZEN_RESULTS_PATH below).
"""

import csv
import os
import sys
from datetime import datetime, timedelta

# Reuse the entity list, GDELT query strings, and the already-tuned adaptive
# rate limiter from ct_harvester.py -- one shared throttle, one shared query
# builder, so this script can never disagree with the main harvester about
# what query an entity uses.
from ct_harvester import (
    ENTITIES, query_for, _get, GDELT_DOC_API, slugify,
)

# =========================================================================
# CONFIG
# =========================================================================

FROZEN_RESULTS_PATH = "ct_results_v1_frozen.csv"
OUT_RESULTS = "ct_artlist_results.csv"

MAXRECORDS = 250          # GDELT ArtList hard cap per call
SORT_ORDER = "HybridRel"  # relevance-ranked; alternatives: DateDesc, DateAsc

# How to pick the second ("other_week") sample per entity, given all its
# ok weeks from ct_results_v1_frozen.csv ranked by mention_count descending.
# "median"    -> the middle-ranked ok week (default; avoids picking another
#                near-peak week, avoids picking a near-zero week too)
# "second"    -> the second-highest week (may sit right next to peak_week --
#                less useful as a contrast sample)
OTHER_WEEK_STRATEGY = "median"

CSV_FIELDS = ["#", "entity", "window", "date", "title", "domain", "url",
              "suggested_label", "relevant"]


# =========================================================================
# Load peak/other weeks from the frozen C(t) results
# =========================================================================

def load_entity_weeks(path):
    """Returns {entity: [(week_start:str, mention_count:int), ...]} sorted
    descending by mention_count, ok rows only."""
    by_entity = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("status") != "ok":
                continue
            try:
                count = int(float(row["mention_count"]))
            except (ValueError, TypeError):
                continue
            by_entity.setdefault(row["entity"], []).append(
                (row["week_start"], count))
    for ent in by_entity:
        by_entity[ent].sort(key=lambda t: t[1], reverse=True)
    return by_entity


def pick_windows(weeks):
    """weeks: list of (week_start, count) sorted desc by count.
    Returns {"peak_week": week_start, "other_week": week_start or None}."""
    if not weeks:
        return None
    peak = weeks[0][0]
    other = None
    if len(weeks) > 1:
        if OTHER_WEEK_STRATEGY == "second":
            other = weeks[1][0]
        else:  # "median"
            other = weeks[len(weeks) // 2][0]
        if other == peak and len(weeks) > 1:
            other = weeks[1][0]
    return {"peak_week": peak, "other_week": other}


# =========================================================================
# GDELT ArtList call
# =========================================================================

def fetch_articles(query, week_start_str):
    """One ArtList call covering the 7 days starting week_start_str
    (YYYY-MM-DD, Monday). Returns list of dicts: date, title, domain, url."""
    start = datetime.strptime(week_start_str, "%Y-%m-%d")
    end = start + timedelta(days=7)
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": MAXRECORDS,
        "sort": SORT_ORDER,
        "startdatetime": start.strftime("%Y%m%d%H%M%S"),
        "enddatetime": end.strftime("%Y%m%d%H%M%S"),
    }
    r = _get(GDELT_DOC_API, params=params)
    if r is None:
        return None
    try:
        data = r.json()
    except ValueError:
        print("   [debug] non-JSON ArtList response for %s @ %s: %s"
              % (query, week_start_str, r.text[:300]))
        return None
    out = []
    for art in data.get("articles", []):
        seendate = art.get("seendate", "")
        date_str = seendate[:8]
        try:
            date_fmt = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            date_fmt = seendate
        out.append({
            "date": date_fmt,
            "title": art.get("title", ""),
            "domain": art.get("domain", ""),
            "url": art.get("url", ""),
        })
    return out


# =========================================================================
# Main
# =========================================================================

def main():
    if not os.path.exists(FROZEN_RESULTS_PATH):
        print("ABORTING: %s not found. Run from the same folder, or edit "
              "FROZEN_RESULTS_PATH." % FROZEN_RESULTS_PATH)
        sys.exit(2)

    entity_weeks = load_entity_weeks(FROZEN_RESULTS_PATH)

    rows = []
    row_num = 0
    n = len(ENTITIES)
    skipped_no_data = []

    for i, (name, birth_str) in enumerate(ENTITIES, 1):
        weeks = entity_weeks.get(name)
        windows = pick_windows(weeks) if weeks else None
        if not windows:
            print("[%d/%d] %s -- no ok weeks in %s, skipping"
                  % (i, n, name, FROZEN_RESULTS_PATH))
            skipped_no_data.append(name)
            continue

        query = query_for(name)
        print("[%d/%d] %s  peak_week=%s  other_week=%s"
              % (i, n, name, windows["peak_week"], windows["other_week"]))

        for window_label in ("peak_week", "other_week"):
            wk = windows[window_label]
            if wk is None:
                continue
            articles = fetch_articles(query, wk)
            if articles is None:
                print("   [debug] %s / %s: fetch failed, skipping window"
                      % (name, window_label))
                continue
            print("   %s: %d articles" % (window_label, len(articles)))
            for art in articles:
                row_num += 1
                rows.append({
                    "#": row_num,
                    "entity": name,
                    "window": window_label,
                    "date": art["date"],
                    "title": art["title"],
                    "domain": art["domain"],
                    "url": art["url"],
                    "suggested_label": "",
                    "relevant": "",
                })

    with open(OUT_RESULTS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)

    print("\n" + "=" * 60)
    print("DONE. %d article rows written to %s across %d entities"
          % (len(rows), OUT_RESULTS, n - len(skipped_no_data)))
    if skipped_no_data:
        print("SKIPPED (no ok weeks, re-run ct_harvester.py for these first): %s"
              % ", ".join(skipped_no_data))
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
