#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ct_source_harvester.py  --  Per-source citation data, PEAK-WEEK ONLY
==========================================================================
v2 -- switched from full-timeline to peak-week sampling on 2026-08-16 to
match Viveka's existing 20-entity manual pull, after she confirmed
peak-week is the intended method (see docs/session_log.md).

STATUS UPDATE (2026-08-16, later same day): Viveka has now built her own
harvester (`ct_artlist_harvester.py`, not in this repo) whose week-choice
logic she describes as "median-count week" -- NOT the max/true-peak logic
this script uses. These are two different weeks for most entities. DO NOT
run this script for real or trust its output until the Kimi/Mamba
spot-check against ct_artlist_LABELING.xlsx (see session_log.md) confirms
which method matches her existing labeled data. This script may end up
superseded by hers, or the two may need reconciling -- unresolved as of
this note.

WHY PEAK WEEK, NOT FULL TIMELINE
----------------------------------
Mixing a peak-week sample for some entities with a full-timeline sample
for others would confound any tier-weighting result with WHEN each
entity was sampled, not just WHICH entity. Peak week tends to be
launch-hype-heavy; full timeline includes quieter follow-up coverage.
Matching her method across all 50 removes that confound.

"Peak week" = the week_start with the single highest mention_count for
that entity in inputs_frozen/ct_results_v1_frozen.csv. Verified against
her actual output for Apple Vision Pro (2023-06-05) and Apple
Intelligence (2024-09-09) -- both match this definition exactly.

WHO THIS RUNS FOR
------------------
Only entities NOT already covered by Viveka's "ct artlist LABELING.xlsx"
(20 of 50). Fill in ALREADY_COVERED below once that entity list is
confirmed -- do not run this against all 50, it would duplicate/waste
her existing work and burn GDELT rate-limit for nothing.

OUTPUT
------
    ct_source_results.csv   one row per article: entity, birth_date,
                             window, peak_week_start, domain, url, title,
                             seendate, sourcecountry, capped, status
    `window` is fixed to "peak_week" so this can be concatenated directly
    with her file once it's exported to the same shape.

NOT YET RUN against live GDELT (no network path from where this was
written). Test on 1-2 entities before the full remaining-entity run.
"""

import csv
import time
from datetime import datetime, timedelta

import requests

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

FROZEN_CSV = "../inputs_frozen/ct_results_v1_frozen.csv"   # relative to scripts/
MAXRECORDS = 250
REQUEST_TIMEOUT = 30
SLEEP_BETWEEN_CALLS = 6.0
MAX_RETRIES = 4
RATE_LIMIT_BASE_WAIT = 30
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
OUT_RESULTS = "../data_derived/ct_source_results.csv"

# Populated from the unique `entity` column values in
# inputs_frozen/ct_artlist_LABELING.xlsx (Label sheet).
# Names match exactly (case, punctuation) against ENTITIES below.
# Verified 2026-08-22: 22 unique entities, leaving 28 remaining.
ALREADY_COVERED = [
    "Apple Intelligence",
    "Apple Vision Pro",
    "Cursor",
    "DBRX",
    "Dream Machine",
    "Gemini (Google model)",
    "Grok",
    "Ideogram",
    "Kimi",
    "Liquid AI",
    "Lovable",
    "Mamba",
    "Manus",
    "Operator",
    "Qwen",
    "Sora",
    "Suno",
    "Threads",
    "Udio",
    "Windsurf",
    "vLLM",
    "xAI",
]

# Same 50 entities/dates as ct_harvester.py -- verified byte-identical
# against inputs_frozen/ct_harvester.py on 2026-08-15.
ENTITIES = [
    ("ElevenLabs", "2023-01-23"), ("Cursor", "2023-03-01"), ("GPT-4", "2023-03-14"),
    ("Mistral AI", "2023-04-28"), ("Apple Vision Pro", "2023-06-05"), ("vLLM", "2023-06-20"),
    ("Ollama", "2023-07-01"), ("Threads", "2023-07-05"), ("xAI", "2023-07-12"),
    ("NotebookLM", "2023-07-12"), ("DeepSeek", "2023-07-17"), ("Llama 2", "2023-07-18"),
    ("Sakana AI", "2023-08-01"), ("Qwen", "2023-08-03"), ("Ideogram", "2023-08-22"),
    ("Kimi", "2023-10-09"), ("Grok", "2023-11-04"), ("Humane Ai Pin", "2023-11-09"),
    ("Mamba", "2023-12-01"), ("Gemini (Google model)", "2023-12-06"), ("Liquid AI", "2023-12-06"),
    ("Mixtral 8x7B", "2023-12-08"), ("Suno", "2023-12-20"), ("Rabbit R1", "2024-01-09"),
    ("AlphaGeometry", "2024-01-17"), ("Gemini 1.5 Pro", "2024-02-15"), ("Sora", "2024-02-15"),
    ("Stable Diffusion 3", "2024-02-22"), ("Claude 3", "2024-03-04"), ("Devin AI", "2024-03-12"),
    ("DBRX", "2024-03-27"), ("Command R+", "2024-04-04"), ("Udio", "2024-04-10"),
    ("Llama 3", "2024-04-18"), ("Phi-3", "2024-04-23"), ("AlphaFold 3", "2024-05-08"),
    ("GPT-4o", "2024-05-13"), ("Apple Intelligence", "2024-06-10"), ("Dream Machine", "2024-06-12"),
    ("Safe Superintelligence", "2024-06-19"), ("Black Forest Labs", "2024-08-01"),
    ("OpenAI o1", "2024-09-12"), ("World Labs", "2024-09-13"), ("Bolt.new", "2024-10-04"),
    ("Windsurf", "2024-11-13"), ("Lovable", "2024-11-21"), ("OpenAI o3", "2024-12-20"),
    ("DeepSeek-R1", "2025-01-20"), ("Operator", "2025-01-23"), ("Manus", "2025-03-06"),
]

QUERY_OVERRIDES = {
    "vLLM":          'vLLM (inference OR LLM OR library OR "open source")',
    "xAI":           'xAI (Musk OR Grok OR startup OR company)',
    "Qwen":          'Qwen (Alibaba OR model OR AI)',
    "Kimi":          'Kimi (Moonshot OR chatbot OR "AI assistant")',
    "Grok":          'Grok (xAI OR Musk OR chatbot)',
    "Suno":          'Suno (AI OR music OR song OR "text-to-music")',
    "Sora":          'Sora (OpenAI OR video OR "text-to-video")',
    "DBRX":          'DBRX (Databricks OR model OR AI OR LLM)',
    "Udio":          'Udio (AI OR music OR song OR "text-to-music")',
    "Threads":       '"Threads" (Meta OR Instagram OR app)',
    "Cursor":        '"Cursor" (Anysphere OR "code editor" OR AI OR coding)',
    "Lovable":       '"Lovable" (AI OR startup OR "app builder" OR coding OR vibe)',
    "Mamba":         '"Mamba" (AI OR "state space" OR architecture OR transformer)',
    "Ideogram":      '"Ideogram" (AI OR "text-to-image" OR image)',
    "Dream Machine": '"Dream Machine" (Luma OR video OR AI)',
    "Operator":      '"Operator" (OpenAI OR ChatGPT OR agent)',
    "Manus":         '"Manus" (AI OR agent OR Monica)',
    "Windsurf":      '"Windsurf" (Codeium OR "code editor" OR AI)',
    "Liquid AI":     '"Liquid AI"',
    "Apple Intelligence": '"Apple Intelligence" (Apple OR iOS OR iPhone)',
    "Apple Vision Pro":   '"Apple Vision Pro"',
    "Gemini (Google model)": '"Google Gemini"',
}


def query_for(name):
    return QUERY_OVERRIDES.get(name, '"%s"' % name)


# ---------------------------------------------------------------------------
# Peak-week lookup -- computed from the frozen counts file, not hardcoded,
# so it stays correct if the frozen file is ever replaced.
# ---------------------------------------------------------------------------

def load_peak_weeks():
    """entity -> week_start (as datetime) of max mention_count."""
    peak = {}
    with open(FROZEN_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                mc = float(row["mention_count"])
            except (ValueError, TypeError):
                continue
            e = row["entity"]
            if e not in peak or mc > peak[e][1]:
                peak[e] = (row["week_start"], mc)
    return {e: datetime.strptime(wk, "%Y-%m-%d") for e, (wk, _) in peak.items()}


# ---------------------------------------------------------------------------
# HTTP helpers -- unchanged from v1
# ---------------------------------------------------------------------------

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})
_last_request_at = [0.0]
_current_gap = [SLEEP_BETWEEN_CALLS]
_consecutive_ok = [0]
_GAP_CAP = 90.0


def _throttle():
    wait = _current_gap[0] - (time.time() - _last_request_at[0])
    if wait > 0:
        time.sleep(wait)


def _mark_sent():
    _last_request_at[0] = time.time()


def _note_success():
    _consecutive_ok[0] += 1
    if _consecutive_ok[0] >= 5 and _current_gap[0] > SLEEP_BETWEEN_CALLS:
        _current_gap[0] = max(SLEEP_BETWEEN_CALLS, _current_gap[0] * 0.75)
        _consecutive_ok[0] = 0


def _note_rate_limited():
    _consecutive_ok[0] = 0
    _current_gap[0] = min(_current_gap[0] * 2, _GAP_CAP)


def _get(url, **kw):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        _throttle()
        try:
            r = SESSION.get(url, timeout=REQUEST_TIMEOUT, **kw)
            _mark_sent()
            if r.status_code == 200:
                _note_success()
                return r
            if r.status_code == 429:
                _note_rate_limited()
                wait = RATE_LIMIT_BASE_WAIT * (2 ** (attempt - 1))
                print("   [429] rate-limited, backing off %ds (attempt %d/%d)"
                      % (wait, attempt, MAX_RETRIES))
                time.sleep(wait)
                continue
            last_err = "HTTP %d -- body: %s" % (r.status_code, r.text[:300])
        except requests.RequestException as e:
            _mark_sent()
            last_err = "%s: %s" % (type(e).__name__, e)
        time.sleep(SLEEP_BETWEEN_CALLS * attempt)
    print("   [debug] all %d attempts failed -- last error: %s" % (MAX_RETRIES, last_err))
    return None


def fetch_artlist_week(query, week_start_dt):
    """One ArtList call for the 7 days starting week_start_dt (Mon-Sun)."""
    week_end = week_start_dt + timedelta(days=7)
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": str(MAXRECORDS),
        "sort": "DateAsc",
        "format": "json",
        "startdatetime": week_start_dt.strftime("%Y%m%d000000"),
        "enddatetime": week_end.strftime("%Y%m%d000000"),
    }
    r = _get(GDELT_DOC_API, params=params)
    if r is None:
        return [], False, "fetch_failed"
    try:
        data = r.json()
    except ValueError:
        return [], False, "bad_json"
    articles = data.get("articles", [])
    capped = len(articles) >= MAXRECORDS
    return articles, capped, "ok"


CSV_FIELDS = ["entity", "birth_date", "window", "peak_week_start",
              "domain", "url", "title", "seendate", "sourcecountry",
              "capped", "status"]


def run():
    peak_weeks = load_peak_weeks()
    rows = []

    targets = [(n, b) for n, b in ENTITIES if n not in ALREADY_COVERED]
    print("Running peak-week harvest for %d entities (%d already covered by Viveka's file, skipped)"
          % (len(targets), len(ENTITIES) - len(targets)))
    if not ALREADY_COVERED:
        print("WARNING: ALREADY_COVERED is empty -- this will run ALL 50 entities. "
              "Fill in the list from ct artlist LABELING.xlsx before running for real.")

    for name, birth_str in targets:
        if name not in peak_weeks:
            print("[skip] %s: no peak week found in frozen CSV" % name)
            continue
        wk = peak_weeks[name]
        query = query_for(name)
        print("\n=== %s -- peak week %s ===" % (name, wk.date()))
        articles, capped, status = fetch_artlist_week(query, wk)
        if capped:
            print("   [warn] hit the %d-article cap -- source mix for this week "
                  "is a truncated sample" % MAXRECORDS)
        for a in articles:
            rows.append({
                "entity": name,
                "birth_date": birth_str,
                "window": "peak_week",
                "peak_week_start": wk.strftime("%Y-%m-%d"),
                "domain": a.get("domain", ""),
                "url": a.get("url", ""),
                "title": a.get("title", ""),
                "seendate": a.get("seendate", ""),
                "sourcecountry": a.get("sourcecountry", ""),
                "capped": capped,
                "status": status,
            })
        print("   -> %d article rows" % len(articles))

        with open(OUT_RESULTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            w.writeheader()
            w.writerows(rows)

    print("\nSaved %s (%d article rows total)" % (OUT_RESULTS, len(rows)))
    n_capped = sum(1 for r in rows if r["capped"])
    if n_capped:
        print("NOTE: %d rows came from a capped week -- domain mix for those "
              "entities is a partial sample, not exhaustive." % n_capped)


if __name__ == "__main__":
    run()
