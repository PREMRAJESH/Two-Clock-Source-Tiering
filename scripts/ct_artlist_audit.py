#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ct_artlist_audit.py  --  Query-precision audit for C(t)  (BROWSER LANE)
"""

import csv
import glob
import json
import os
import random
import sys
import urllib.parse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "inputs_frozen"))

from ct_harvester import (ENTITIES, QUERY_OVERRIDES, query_for,
                          GDELT_DOC_API)

OUT = "ct_artlist_audit.csv"
PER_WINDOW = 25
random.seed(20260708)
FIELDS = ["entity", "query", "sample_window", "seendate",
          "title", "domain", "url", "relevant"]


def peak_and_random_week(entity):
    if not os.path.exists("ct_results.csv"):
        return None, None
    rows = [r for r in csv.DictReader(open("ct_results.csv", encoding="utf-8"))
            if r["entity"] == entity and r["status"] == "ok"
            and r["mention_count"] not in ("", "0")]
    if not rows:
        return None, None
    peak = max(rows, key=lambda r: float(r["mention_count"]))
    rnd = random.Random("ctaudit-%s-20260708" % entity).choice(rows)
    f = lambda r: datetime.strptime(r["week_start"], "%Y-%m-%d")
    return f(peak), f(rnd)


def windows_for(entity, birth):
    peak_wk, rnd_wk = peak_and_random_week(entity)
    if peak_wk:
        w = [("peak_week", peak_wk, peak_wk + timedelta(days=7))]
        if rnd_wk and rnd_wk != peak_wk:
            w.append(("random_week", rnd_wk, rnd_wk + timedelta(days=7)))
        return w
    return [("full_range", birth, datetime(2026, 7, 8))]


CONTRAST_MIN_GAP_WEEKS = 4

FROZEN_RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "..", "inputs_frozen", "ct_results_v1_frozen.csv")


def contrast_week(entity, results_path=FROZEN_RESULTS,
                   min_gap_weeks=CONTRAST_MIN_GAP_WEEKS):
    """Documented 2026-08-18 replacement for the original (unrecoverable)
    second-week rule -- see changes.md 2026-08-18 entry. Picks a week that
    genuinely contrasts peak_week (>= min_gap_weeks away), deterministically:
    seeded on entity name + a fixed version tag only, never on a run date or
    row order, so re-running this later reproduces the same pick even if
    unrelated rows are added to results_path.
    """
    if not os.path.exists(results_path):
        return None, None
    rows = [r for r in csv.DictReader(open(results_path, encoding="utf-8"))
            if r["entity"] == entity and r["status"] == "ok"
            and r["mention_count"] not in ("", "0")]
    if not rows:
        return None, None
    rows.sort(key=lambda r: r["week_start"])
    f = lambda r: datetime.strptime(r["week_start"], "%Y-%m-%d")
    peak = max(rows, key=lambda r: float(r["mention_count"]))
    peak_wk = f(peak)
    candidates = [r for r in rows if abs((f(r) - peak_wk).days) >= min_gap_weeks * 7]
    if not candidates:
        candidates = [r for r in rows if r is not peak]
    if not candidates:
        return peak_wk, None
    picked = random.Random("contrast-week-v2-%s" % entity).choice(candidates)
    return peak_wk, f(picked)


def windows_for_v2(entity, birth):
    peak_wk, contrast_wk = contrast_week(entity)
    if peak_wk:
        w = [("peak_week", peak_wk, peak_wk + timedelta(days=7))]
        if contrast_wk:
            w.append(("contrast_week", contrast_wk, contrast_wk + timedelta(days=7)))
        return w
    return [("full_range", birth, datetime(2026, 7, 8))]


def artlist_url(query, start, end, n=PER_WINDOW):
    return ("%s?query=%s&mode=ArtList&format=json&maxrecords=%d&sort=hybridrel"
            "&startdatetime=%s&enddatetime=%s"
            % (GDELT_DOC_API, urllib.parse.quote(query, safe="()"), n,
               start.strftime("%Y%m%d%H%M%S"),
               end.strftime("%Y%m%d%H%M%S")))


def print_urls(peak_only=False):
    audited = [(n, b) for n, b in ENTITIES if n in QUERY_OVERRIDES]
    total = 0
    kind = "PEAK-WEEK" if peak_only else "all"
    print("ArtList precision audit -- %s windows, %d overridden entities."
          % (kind, len(audited)))
    print("Open each URL, wait for JSON, Ctrl+S (Downloads is fine), ~25s apart.")
    print("Then move *.json into this folder and: py ct_artlist_audit.py\n")
    for name, birth_str in audited:
        birth = datetime.strptime(birth_str, "%Y-%m-%d")
        q = query_for(name)
        for label, s, e in windows_for(name, birth):
            if peak_only and label != "peak_week":
                continue
            total += 1
            print("# %s  (%s %s)" % (name, label, s.date()))
            print(artlist_url(q, s, e))
    print("\nTotal URLs to fetch: %d  (~%d min at 25s apart)"
          % (total, round(total * 25 / 60)))


def print_contrast_urls():
    audited = [(n, b) for n, b in ENTITIES if n in QUERY_OVERRIDES]
    total = 0
    print("ArtList contrast-week audit -- v2 rule, %d overridden entities."
          % len(audited))
    print("Open each URL, wait for JSON, Ctrl+S (Downloads is fine), ~25s apart.")
    print("Then move *.json into this folder and: py ct_artlist_audit.py\n")
    for name, birth_str in audited:
        birth = datetime.strptime(birth_str, "%Y-%m-%d")
        q = query_for(name)
        for label, s, e in windows_for_v2(name, birth):
            if label != "contrast_week":
                continue
            total += 1
            print("# %s  (%s %s)" % (name, label, s.date()))
            print(artlist_url(q, s, e))
    print("\nTotal URLs to fetch: %d  (~%d min at 25s apart)"
          % (total, round(total * 25 / 60)))


def _seedate(a):
    d = str(a.get("seendate", "")).replace("T", "").replace("Z", "")
    if len(d) >= 8:
        try:
            return datetime.strptime(d[:8], "%Y%m%d")
        except ValueError:
            return None
    return None


def assign_window(articles, windows):
    best, best_hits = windows[0][0], -1
    for label, s, e in windows:
        hits = sum(1 for a in articles
                   if (d := _seedate(a)) and s <= d < e)
        if hits > best_hits:
            best, best_hits = label, hits
    return best


FILENAME_ALIASES = {
    "apple intelligence": "Apple Intelligence",
    "apple vision": "Apple Vision Pro",
    "apple vision pro": "Apple Vision Pro",
    "cursor": "Cursor",
    "data bricks": "DBRX",
    "dbrx": "DBRX",
    "dream machine": "Dream Machine",
    "google gemini": "Gemini (Google model)",
    "gemini (google model)": "Gemini (Google model)",
    "gemini": "Gemini (Google model)",
    "grok ai": "Grok",
    "grok": "Grok",
    "hermes": "vLLM",
    "ideogram": "Ideogram",
    "kimi ai": "Kimi",
    "kimi": "Kimi",
    "liquid ai": "Liquid AI",
    "loveable": "Lovable",
    "lovable": "Lovable",
    "mamba": "Mamba",
    "manus": "Manus",
    "openai": "Operator",
    "operator": "Operator",
    "qwen": "Qwen",
    "sora": "Sora",
    "suno": "Suno",
    "threads": "Threads",
    "udio": "Udio",
    "vllm": "vLLM",
    "windsurf": "Windsurf",
    "xai": "xAI",
}


def _filename_entity(path):
    base = os.path.splitext(os.path.basename(path))[0].lower()
    for junk in (" artlist", " peak", " random", "_peak", "_random"):
        base = base.replace(junk, "")
    base = base.strip()
    return FILENAME_ALIASES.get(base)


def _windows_cache():
    cache = {}
    for name, birth_str in ENTITIES:
        if name not in QUERY_OVERRIDES:
            continue
        birth = datetime.strptime(birth_str, "%Y-%m-%d")
        cache[name] = windows_for(name, birth)
    return cache


def _refuse_if_labeled(path, force=False):
    if force or not os.path.exists(path):
        return
    labeled = [r for r in csv.DictReader(open(path, encoding="utf-8"))
               if r.get("relevant", "") in ("y", "n")]
    if labeled:
        sys.exit("%s already has %d hand-labelled rows -- refusing to "
                  "overwrite. Pass --force if this is really intended."
                  % (path, len(labeled)))


def ingest(force=False):
    query_map = {query_for(n): (n, b) for n, b in ENTITIES}
    name_map = {n: b for n, b in ENTITIES}
    windows_cache = _windows_cache()
    files = sorted(glob.glob("*.json"))
    rows, used, skipped = [], [], []
    seen = set()

    for path in files:
        try:
            with open(path, encoding="utf-8-sig") as f:
                data = json.load(f)
        except (ValueError, OSError) as e:
            skipped.append((path, "unreadable/not JSON: %s" % e))
            continue

        if not isinstance(data, dict):
            skipped.append((path, "not an ArtList-shaped JSON object -- skipped"))
            continue
        articles = data.get("articles")
        if articles is None:
            skipped.append((path, "no 'articles' key (timeline file?) -- skipped"))
            continue

        title = (data.get("query_details", {}) or {}).get("title", "").strip()
        if title in query_map:
            name, birth_str = query_map[title]
        else:
            name = _filename_entity(path)
            if name is None or name not in name_map:
                skipped.append((path, "no query_details and filename doesn't "
                                       "match a known alias -- skipped"))
                continue
            birth_str = name_map[name]
            title = query_for(name)
        if name not in QUERY_OVERRIDES:
            skipped.append((path, "%s is not an overridden entity -- skipped" % name))
            continue

        window = assign_window(articles, windows_cache[name])
        n_added = 0
        for a in articles:
            key = (name, window, a.get("url", ""))
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "entity": name, "query": title, "sample_window": window,
                "seendate": a.get("seendate", ""), "title": a.get("title", ""),
                "domain": a.get("domain", ""), "url": a.get("url", ""),
                "relevant": "",
            })
            n_added += 1
        print("[ok] %-18s <- %-40s %s: %d articles"
              % (name, path[:40], window, n_added))
        used.append((name, window))

    if not rows:
        print("No ArtList JSON found here.")
        for path, reason in skipped:
            print("  skipped %s: %s" % (path, reason))
        return

    _refuse_if_labeled(OUT, force=force)
    rows.sort(key=lambda r: (r["entity"], r["sample_window"], r["seendate"]))
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    audited = {n for n, _ in ENTITIES if n in QUERY_OVERRIDES}
    covered = {n for n, _ in used}
    print("\n" + "=" * 60)
    print("Wrote %d article rows -> %s" % (len(rows), OUT))
    print("Entities covered: %d/%d" % (len(covered), len(audited)))
    missing = sorted(audited - covered)
    if missing:
        print("Still need ArtList JSON for %d: %s" % (len(missing), ", ".join(missing)))
    for path, reason in skipped:
        print("  skipped %s: %s" % (path, reason))
    print("=" * 60)


CONTRAST_OUT = "ct_artlist_contrast.csv"


def ingest_contrast(force=False):
    """Same matching as ingest(), but only keeps rows whose real dates land
    inside the v2 contrast_week window, and writes to CONTRAST_OUT --
    never OUT. This lets leftover peak/random JSON files from the original
    audit sit in the same folder without risk: they won't match
    contrast_week and get silently skipped, and ct_artlist_audit.csv
    (566 hand-labelled rows) is never opened for writing here.
    """
    query_map = {query_for(n): (n, b) for n, b in ENTITIES}
    name_map = {n: b for n, b in ENTITIES}
    windows_cache = {n: windows_for_v2(n, datetime.strptime(b, "%Y-%m-%d"))
                      for n, b in ENTITIES if n in QUERY_OVERRIDES}
    files = sorted(glob.glob("*.json"))
    rows, used, skipped = [], [], []
    seen = set()

    for path in files:
        try:
            with open(path, encoding="utf-8-sig") as f:
                data = json.load(f)
        except (ValueError, OSError) as e:
            skipped.append((path, "unreadable/not JSON: %s" % e))
            continue

        if not isinstance(data, dict):
            skipped.append((path, "not an ArtList-shaped JSON object -- skipped"))
            continue
        articles = data.get("articles")
        if articles is None:
            skipped.append((path, "no 'articles' key (timeline file?) -- skipped"))
            continue

        title = (data.get("query_details", {}) or {}).get("title", "").strip()
        if title in query_map:
            name, birth_str = query_map[title]
        else:
            name = _filename_entity(path)
            if name is None or name not in name_map:
                skipped.append((path, "no query_details and filename doesn't "
                                       "match a known alias -- skipped"))
                continue
            birth_str = name_map[name]
            title = query_for(name)
        if name not in QUERY_OVERRIDES:
            skipped.append((path, "%s is not an overridden entity -- skipped" % name))
            continue

        window = assign_window(articles, windows_cache[name])
        if window != "contrast_week":
            skipped.append((path, "best-matching window is %r, not "
                                   "contrast_week -- skipped" % window))
            continue
        n_added = 0
        for a in articles:
            key = (name, window, a.get("url", ""))
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "entity": name, "query": title, "sample_window": window,
                "seendate": a.get("seendate", ""), "title": a.get("title", ""),
                "domain": a.get("domain", ""), "url": a.get("url", ""),
                "relevant": "",
            })
            n_added += 1
        print("[ok] %-18s <- %-40s %s: %d articles"
              % (name, path[:40], window, n_added))
        used.append((name, window))

    if not rows:
        print("No contrast-week ArtList JSON found here.")
        for path, reason in skipped:
            print("  skipped %s: %s" % (path, reason))
        return

    _refuse_if_labeled(CONTRAST_OUT, force=force)
    rows.sort(key=lambda r: (r["entity"], r["seendate"]))
    with open(CONTRAST_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    audited = {n for n, _ in ENTITIES if n in QUERY_OVERRIDES}
    covered = {n for n, _ in used}
    print("\n" + "=" * 60)
    print("Wrote %d article rows -> %s" % (len(rows), CONTRAST_OUT))
    print("Entities covered: %d/%d" % (len(covered), len(audited)))
    missing = sorted(audited - covered)
    if missing:
        print("Still need ArtList JSON for %d: %s" % (len(missing), ", ".join(missing)))
    for path, reason in skipped:
        print("  skipped %s: %s" % (path, reason))
    print("=" * 60)


if __name__ == "__main__":
    if "--contrast-urls" in sys.argv:
        print_contrast_urls()
    elif "--contrast" in sys.argv:
        ingest_contrast(force="--force" in sys.argv)
    elif "--urls" in sys.argv:
        print_urls(peak_only="--peak" in sys.argv)
    else:
        ingest(force="--force" in sys.argv)
