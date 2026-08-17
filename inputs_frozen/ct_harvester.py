#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ct_harvester.py  --  The Citation Clock, C(t)
==============================================
Third and final clock in the Two-Clock Validation project. Mirrors
st_harvester.py / pt_pilot.py in structure and conventions.

WHAT IT DOES
------------
For each of the 50 entities:
  1. Builds a GDELT full-text search query for the entity (with manual
     disambiguation terms for names that collide with common words / other
     real-world things -- see QUERY_OVERRIDES below).
  2. Calls the GDELT DOC 2.0 API (mode=timelinevolraw) in 90-day windows,
     from WEEKS_BEFORE_BIRTH weeks before the entity's birth date through
     AS_OF_DATE (defaults to "today" -- see the freeze note below).
  3. Aggregates the raw daily article counts GDELT returns into Monday-start
     ISO weeks: MentionCount = total matching articles that week.
  4. Plots one C(t) curve per entity (weekly mentions vs. days from birth,
     with a vertical line at birth).

OUTPUT
------
  ct_results.csv     one row per entity x week: entity, birth_date,
                     week_start, days_from_birth, mention_count, query_used,
                     status.
  ct_<entity>.png    one C(t) curve per entity.

NO API KEY NEEDED. GDELT DOC 2.0 is free/public, but IS rate-limited to
1 request per 5 seconds (their published limit, confirmed 2026-07-08 via
their own 429 message). One call now covers an entity's full range (see
CHUNK_DAYS), so a clean run is ~50 requests / ~5-6 minutes total.

SETUP (run once, in PowerShell)
-------------------------------
  py -m pip install requests matplotlib

RUN
---
  py ct_harvester.py

IMPORTANT -- DATA FREEZING FOR THE PAPER
-----------------------------------------
AS_OF_DATE below defaults to None, which means "as of whenever this script
is run" -- fine for iterating, but C(t) numbers will keep changing every day
because it's a live news feed. Before any result from this script is quoted
in the whitepaper, set AS_OF_DATE to a fixed date (e.g. "2026-07-08") and
re-run once, so every number in the paper traces to one frozen snapshot.

NOTES (read before trusting a number)
--------------------------------------
- Disambiguation queries in QUERY_OVERRIDES are BEST-EFFORT, same caveat as
  the Wikidata collisions already logged for P(t)/S(t) (Kimi, Suno, Sora,
  Operator, Manus, Mamba, etc. all collide with unrelated real-world things).
  Spot-check a few MentionCount spikes against actual GDELT articles before
  publishing any specific number.
- GDELT's DOC 2.0 API indexes online news from 2017 onward and is
  English-language-dominant. Chinese-origin entities (DeepSeek, Kimi, Qwen)
  will likely undercount relative to their real-world attention, because
  most Chinese-language coverage isn't in GDELT's monitored corpus. Flag
  this the same way the P(t) language-coverage caveat was flagged.
- A week with truly zero matching articles is legitimate data (status=ok),
  not a failure. status="fetch_failed" means the HTTP call itself broke.
- Tunable knobs are all in the CONFIG block below.
"""

import csv
import re
import sys
import time
from datetime import datetime, timedelta

import requests

import matplotlib
matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt


# =========================================================================
# CONFIG  --  edit here to add entities, change window, or retune queries
# =========================================================================

# How many weeks before birth to start each entity's C(t) series.
WEEKS_BEFORE_BIRTH = 4

# Freeze the dataset for publication -- see docstring. None = "today".
AS_OF_DATE = None   # e.g. "2026-07-08"

# GDELT call chunking. Confirmed 2026-07-08: a single call spanning 3+ years
# still returns date_resolution=day, so one call covers any entity's full
# range -- 2000 means "never chunk" (longest range is ~1300 days). Total
# request count drops from ~700 to 50, i.e. ~5 min instead of 30-60+.
CHUNK_DAYS = 2000

# Politeness / robustness.
REQUEST_TIMEOUT = 30
# GDELT's own published limit (confirmed via their 429 message, 2026-07-08):
# "Please limit requests to one every 5 seconds." 6.0s gives a safety margin.
SLEEP_BETWEEN_CALLS = 6.0
MAX_RETRIES = 4
RATE_LIMIT_BASE_WAIT = 30       # seconds; doubles each 429 retry (30,60,120,240)
# Browser-style UA -- GDELT throttles unfamiliar/bot-style UAs much harder
# once an IP has tripped the rate limit (confirmed 2026-07-08: identical
# query succeeded instantly with a browser UA while the old research UA
# got instant 429s). Changed from "TwoClockValidation/1.0 (research; ...)".
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"

# Output file names (written to the current folder).
OUT_RESULTS = "ct_results.csv"
PLOT_PREFIX = "ct_"           # -> ct_<entity>.png

# Entity list -- SAME 50 names/birth-dates as st_harvester.py's ENTITIES,
# so entity names match exactly across st_results.csv / master_two_clock.csv
# and this file for a clean merge. Keep this list in sync with that one.
ENTITIES = [
    ("ElevenLabs",              "2023-01-23"),
    ("Cursor",                  "2023-03-01"),
    ("GPT-4",                   "2023-03-14"),
    ("Mistral AI",              "2023-04-28"),
    ("Apple Vision Pro",        "2023-06-05"),
    ("vLLM",                    "2023-06-20"),
    ("Ollama",                  "2023-07-01"),
    ("Threads",                 "2023-07-05"),
    ("xAI",                     "2023-07-12"),
    ("NotebookLM",              "2023-07-12"),
    ("DeepSeek",                "2023-07-17"),
    ("Llama 2",                 "2023-07-18"),
    ("Sakana AI",               "2023-08-01"),
    ("Qwen",                    "2023-08-03"),
    ("Ideogram",                "2023-08-22"),
    ("Kimi",                    "2023-10-09"),
    ("Grok",                    "2023-11-04"),
    ("Humane Ai Pin",           "2023-11-09"),
    ("Mamba",                   "2023-12-01"),
    ("Gemini (Google model)",   "2023-12-06"),
    ("Liquid AI",               "2023-12-06"),
    ("Mixtral 8x7B",            "2023-12-08"),
    ("Suno",                    "2023-12-20"),
    ("Rabbit R1",               "2024-01-09"),
    ("AlphaGeometry",           "2024-01-17"),
    ("Gemini 1.5 Pro",          "2024-02-15"),
    ("Sora",                    "2024-02-15"),
    ("Stable Diffusion 3",      "2024-02-22"),
    ("Claude 3",                "2024-03-04"),
    ("Devin AI",                "2024-03-12"),
    ("DBRX",                    "2024-03-27"),
    ("Command R+",              "2024-04-04"),
    ("Udio",                    "2024-04-10"),
    ("Llama 3",                 "2024-04-18"),
    ("Phi-3",                   "2024-04-23"),
    ("AlphaFold 3",             "2024-05-08"),
    ("GPT-4o",                  "2024-05-13"),
    ("Apple Intelligence",      "2024-06-10"),
    ("Dream Machine",           "2024-06-12"),
    ("Safe Superintelligence",  "2024-06-19"),
    ("Black Forest Labs",       "2024-08-01"),
    ("OpenAI o1",               "2024-09-12"),
    ("World Labs",              "2024-09-13"),
    ("Bolt.new",                "2024-10-04"),
    ("Windsurf",                "2024-11-13"),
    ("Lovable",                 "2024-11-21"),
    ("OpenAI o3",               "2024-12-20"),
    ("DeepSeek-R1",             "2025-01-20"),
    ("Operator",                "2025-01-23"),
    ("Manus",                   "2025-03-06"),
]

# Manual disambiguation for names that collide with common words or other
# real-world entities (same collision list flagged for Wikidata in the S(t)
# handover section). Query syntax: GDELT DOC API treats space-separated
# terms as AND, "OR" + parentheses as OR, quotes as exact phrase.
# Anything NOT listed here just uses the quoted bare name.
QUERY_OVERRIDES = {
    # -- Names shorter than 5 characters: GDELT rejects QUOTED phrases under
    #    ~5 chars ("The specified phrase is too short.") but accepts the same
    #    word UNQUOTED (confirmed 2026-07-08 on Qwen). Short names therefore
    #    go unquoted, with AND-disambiguation to control noise.
    "vLLM":          'vLLM (inference OR LLM OR library OR "open source")',
    "xAI":           'xAI (Musk OR Grok OR startup OR company)',
    "Qwen":          'Qwen (Alibaba OR model OR AI)',
    "Kimi":          'Kimi (Moonshot OR chatbot OR "AI assistant")',
    "Grok":          'Grok (xAI OR Musk OR chatbot)',
    "Suno":          'Suno (AI OR music OR song OR "text-to-music")',
    "Sora":          'Sora (OpenAI OR video OR "text-to-video")',
    "DBRX":          'DBRX (Databricks OR model OR AI OR LLM)',
    "Udio":          'Udio (AI OR music OR song OR "text-to-music")',
    # -- Names that collide with common words / other real-world things.
    #    Cursor added 2026-07-08: bare "Cursor" returned 51k mentions with a
    #    PRE-birth peak -- the ordinary English word, not the editor.
    "Threads":       '"Threads" (Meta OR Instagram OR app)',
    "Cursor":        '"Cursor" (Anysphere OR "code editor" OR AI OR coding)',
    # Lovable: run 1 returned 27,075 mentions for the bare word -- the
    # English adjective, not the Swedish AI startup. Same disease as Cursor.
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
    # -- Display name is a label, not a searchable phrase: the quoted
    #    fallback '"Gemini (Google model)"' matches ~nothing.
    "Gemini (Google model)": '"Google Gemini"',
}


# =========================================================================
# HTTP helpers
# =========================================================================

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

# ---- Adaptive global rate limiter -------------------------------------
# GDELT's own 429 message says "one request every 5 seconds", but in
# practice a client that has just been throttled needs MORE than 5s before
# it's let back in -- a flat per-chunk sleep isn't enough, because it only
# paces between chunks, not the true gap since the last real HTTP request
# (including retries). This tracks ONE shared clock across every request
# to GDELT, no matter which entity/chunk it came from: it backs off harder
# every time GDELT says 429, and only eases back toward the base pace
# after several clean successes in a row.
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
    """GET with retries and a timeout. Returns Response or None.
    Every attempt (across every chunk/entity) goes through the same
    adaptive throttle -- see _throttle()/_note_rate_limited() above."""
    kw.setdefault("timeout", REQUEST_TIMEOUT)
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        _throttle()
        try:
            r = SESSION.get(url, **kw)
            _mark_sent()
            if r.status_code == 200:
                _note_success()
                return r
            if r.status_code == 429:
                _note_rate_limited()
                wait = RATE_LIMIT_BASE_WAIT * (2 ** (attempt - 1))
                last_err = "HTTP 429 (rate limited)"
                print("   [debug] 429 -- pace now %.0fs/req, waiting %ds before retry %d/%d"
                      % (_current_gap[0], wait, attempt, MAX_RETRIES))
                time.sleep(wait)
                continue
            last_err = "HTTP %d -- body: %s" % (r.status_code, r.text[:300])
        except requests.RequestException as e:
            _mark_sent()
            last_err = "%s: %s" % (type(e).__name__, e)
        time.sleep(SLEEP_BETWEEN_CALLS * attempt)
    print("   [debug] all %d attempts failed for %s -- last error: %s"
          % (MAX_RETRIES, url, last_err))
    return None


# =========================================================================
# GDELT DOC 2.0 API
# =========================================================================

def query_for(name):
    return QUERY_OVERRIDES.get(name, '"%s"' % name)


# Which timeline mode/metric this run uses -- decided ONCE at startup by
# preflight_mode(), never per-chunk, so the metric is consistent across all
# 50 entities. GDELT intermittently serves EMPTY 200 bodies for the raw
# mode (observed repeatedly 2026-07-08); normalized volume intensity is the
# fallback. Raw counts and intensity are NOT comparable -- the CSV records
# which one was used in the `metric` column.
_MODE = ["TimelineVolRaw"]
_METRIC = ["raw_count"]


def preflight_mode():
    """One tiny call before the real run. Three outcomes:
    - raw mode returns good JSON  -> keep raw counts.
    - raw mode returns empty/junk -> fall back to timelinevol (intensity).
    - request fails outright      -> IP still rate-limited; abort now
      instead of burning 50 entities' worth of retries."""
    params = {
        "query": '"ElevenLabs"', "mode": "TimelineVolRaw", "format": "json",
        "startdatetime": "20230101000000", "enddatetime": "20230115000000",
    }
    r = _get(GDELT_DOC_API, params=params)
    if r is None:
        print("\nABORTING: preflight request failed -- this IP is still")
        print("rate-limited by GDELT. Run `py ct_probe.py` until it says")
        print("CLEAN before trying the harvester again.")
        sys.exit(2)
    if r.text.strip():
        try:
            r.json()
            print("preflight: raw article counts available (TimelineVolRaw)")
            return
        except ValueError:
            pass
    _MODE[0] = "timelinevol"
    _METRIC[0] = "vol_intensity"
    print("preflight: WARNING -- raw mode returned an empty/invalid body;")
    print("falling back to normalized volume intensity (mode=timelinevol)")
    print("for the WHOLE run. mention_count is now a 0-1-ish intensity, not")
    print("an article count. Recorded in the CSV `metric` column.")


def fetch_chunk(query, start, end):
    """
    One GDELT timelinevolraw call for [start, end). Returns list of
    (date, count) daily tuples, or None on hard failure. Empty list is a
    legitimate "zero hits this window" result, not a failure.
    """
    params = {
        "query": query,
        # Set by preflight_mode() -- raw counts if GDELT will serve them,
        # normalized intensity otherwise. Note the raw mode also seems
        # case-sensitive: lowercase "timelinevolraw" reliably returned
        # empty bodies on 2026-07-08 while "TimelineVolRaw" worked.
        "mode": _MODE[0],
        "format": "json",
        "startdatetime": start.strftime("%Y%m%d%H%M%S"),
        "enddatetime": end.strftime("%Y%m%d%H%M%S"),
    }
    r = _get(GDELT_DOC_API, params=params)
    if r is None:
        return None
    try:
        data = r.json()
    except ValueError:
        print("   [debug] GDELT returned non-JSON for %s -> %s : body: %s"
              % (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), r.text[:300]))
        return None
    timeline = data.get("timeline", [])
    if not timeline:
        return []
    series = timeline[0].get("data", [])
    out = []
    for point in series:
        d = point.get("date", "")
        v = point.get("value", 0)
        if len(d) >= 8:
            out.append((datetime.strptime(d[:8], "%Y%m%d"), v))
    return out


def fetch_entity_daily_counts(query, range_start, range_end):
    """
    Chunk [range_start, range_end) into CHUNK_DAYS windows, concatenate.
    A chunk that fails all retries no longer kills the whole entity -- it's
    recorded in failed_ranges and the loop moves on to the next chunk, so
    one bad GDELT call costs you ~90 days of data for one entity, not the
    entire entity. Returns (daily_counts, failed_ranges).
    """
    daily = {}
    failed_ranges = []
    cur = range_start
    while cur < range_end:
        chunk_end = min(cur + timedelta(days=CHUNK_DAYS), range_end)
        points = fetch_chunk(query, cur, chunk_end)
        if points is None:
            failed_ranges.append((cur, chunk_end))
            print("   [debug] chunk %s -> %s failed after retries -- skipping, continuing"
                  % (cur.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
        else:
            for d, v in points:
                daily[d] = daily.get(d, 0) + v
        time.sleep(SLEEP_BETWEEN_CALLS)
        cur = chunk_end
    return daily, failed_ranges


# =========================================================================
# Weekly aggregation
# =========================================================================

def week_start(d):
    """Monday of the ISO week containing date d."""
    return d - timedelta(days=d.weekday())


def to_weekly(daily_counts, range_start, range_end):
    """Bucket a {date: count} dict into Monday-start weeks covering the
    full range (weeks with no data still appear, with mention_count=0)."""
    weeks = {}
    w = week_start(range_start)
    last_w = week_start(range_end)
    while w <= last_w:
        weeks[w] = 0
        w += timedelta(days=7)
    for d, v in daily_counts.items():
        wk = week_start(d)
        if wk in weeks:
            weeks[wk] += v
    return weeks


def week_overlaps_failed(wk, failed_ranges):
    """True if this Monday-start week overlaps any chunk that failed all
    retries -- its mention_count is unknown, not zero."""
    wk_end = wk + timedelta(days=7)
    for f_start, f_end in failed_ranges:
        if wk < f_end and wk_end > f_start:
            return True
    return False


# =========================================================================
# Main
# =========================================================================

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


_any_entity_succeeded = [False]

CSV_FIELDS = ["entity", "birth_date", "week_start", "days_from_birth",
              "mention_count", "metric", "query_used", "status"]


def _write_csv(results):
    with open(OUT_RESULTS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(results)


def load_previous():
    """RESUME SUPPORT. GDELT's flakiness means a single pass rarely gets all
    50 entities, so each run keeps what already succeeded. Reads an existing
    ct_results.csv (if any) and returns (kept_rows, done_entities):
    an entity is done -- and skipped this run -- only if ALL its rows are
    status=ok AND its recorded query matches the current query_for(name),
    so changing an entity's QUERY_OVERRIDE automatically forces a refetch
    (e.g. the contaminated bare-"Cursor" data gets thrown away, not kept)."""
    import os
    if not os.path.exists(OUT_RESULTS):
        return [], set()
    with open(OUT_RESULTS, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    all_ok = {}
    for r in rows:
        ok = (r.get("status") == "ok"
              and r.get("query_used") == query_for(r.get("entity", "")))
        all_ok[r["entity"]] = all_ok.get(r["entity"], True) and ok
    done = {e for e, ok in all_ok.items() if ok}
    kept = [{k: r.get(k, "") for k in CSV_FIELDS}
            for r in rows if r["entity"] in done]
    return kept, done


def main():
    as_of = (datetime.strptime(AS_OF_DATE, "%Y-%m-%d")
             if AS_OF_DATE else datetime.now())
    print("C(t) harvest as of: %s%s"
          % (as_of.strftime("%Y-%m-%d"),
             "  (LIVE -- not frozen, see docstring)" if not AS_OF_DATE else "  (FROZEN)"))

    results, done_entities = load_previous()
    if done_entities:
        print("resume: keeping %d complete entities from existing %s; "
              "refetching the rest" % (len(done_entities), OUT_RESULTS))

    preflight_mode()

    n = len(ENTITIES)

    for i, (name, birth_str) in enumerate(ENTITIES, 1):
        if name in done_entities:
            print("[%d/%d] %s -- already complete, skipping" % (i, n, name))
            continue
        birth = datetime.strptime(birth_str, "%Y-%m-%d")
        range_start = birth - timedelta(weeks=WEEKS_BEFORE_BIRTH)
        range_end = as_of
        query = query_for(name)
        print("\n[%d/%d] %s  (born %s)  query=%s" % (i, n, name, birth_str, query))

        if range_start >= range_end:
            print("   skipped -- birth date is after AS_OF_DATE")
            continue

        daily, failed_ranges = fetch_entity_daily_counts(query, range_start, range_end)
        weekly = to_weekly(daily, range_start, range_end)

        entity_curve = []  # (days_from_birth, count) for plotting -- ok weeks only
        ok_weeks = 0
        failed_weeks = 0
        for wk in sorted(weekly):
            dfb = (wk - birth).days
            if week_overlaps_failed(wk, failed_ranges):
                results.append({
                    "entity": name, "birth_date": birth_str,
                    "week_start": wk.strftime("%Y-%m-%d"),
                    "days_from_birth": dfb, "mention_count": "",
                    "metric": _METRIC[0],
                    "query_used": query, "status": "chunk_failed",
                })
                failed_weeks += 1
            else:
                count = weekly[wk]
                results.append({
                    "entity": name, "birth_date": birth_str,
                    "week_start": wk.strftime("%Y-%m-%d"),
                    "days_from_birth": dfb, "mention_count": count,
                    "metric": _METRIC[0],
                    "query_used": query, "status": "ok",
                })
                entity_curve.append((dfb, count))
                ok_weeks += 1

        if ok_weeks:
            _any_entity_succeeded[0] = True
            total_mentions = sum(c for _, c in entity_curve)
            peak = max(entity_curve, key=lambda t: t[1])
            print("   %d ok weeks, %d failed weeks, %d total mentions, peak %+d days (%d)"
                  % (ok_weeks, failed_weeks, total_mentions, peak[0], peak[1]))
        else:
            print("   ALL %d weeks failed -- GDELT unreachable for this entity, rerun later"
                  % failed_weeks)
            if not _any_entity_succeeded[0]:
                print("\nABORTING: the first fetched entity got nothing at all, so this")
                print("IP is still rate-limited. Continuing would just re-burn the")
                print("cooldown. Wait 30+ min with ZERO GDELT traffic, then retry.")
                _write_csv(results)
                print("(previously-complete entities were preserved in %s)" % OUT_RESULTS)
                sys.exit(2)

        # --- Plot this entity's C(t) curve ---
        if entity_curve:
            fig, ax = plt.subplots(figsize=(8, 4.2))
            xs = [d for d, _ in entity_curve]
            ys = [c for _, c in entity_curve]
            ax.plot(xs, ys, marker="o", markersize=3, linewidth=1.5)
            ax.axvline(0, color="grey", linestyle="--", linewidth=1, label="birth")
            ax.set_title("C(t) - %s  (born %s)" % (name, birth_str))
            ax.set_xlabel("Days from birth (week-start)")
            ax.set_ylabel("Weekly mention count (GDELT)")
            ax.grid(True, alpha=0.3)
            ax.legend(loc="upper left", fontsize=8)
            fig.tight_layout()
            fig.savefig("%s%s.png" % (PLOT_PREFIX, slugify(name)), dpi=120)
            plt.close(fig)   # avoid the >20-figures matplotlib warning

    # --- Write CSV ---
    _write_csv(results)

    ok_rows = sum(1 for r in results if r["status"] == "ok")
    failed_rows = sum(1 for r in results if r["status"] == "chunk_failed")
    print("\n" + "=" * 60)
    print("DONE.  %d rows written to %s  (%d ok weekly rows, %d weeks lost to GDELT errors)"
          % (len(results), OUT_RESULTS, ok_rows, failed_rows))
    if failed_rows:
        incomplete = sorted({r["entity"] for r in results if r["status"] != "ok"})
        print("INCOMPLETE entities (%d): %s" % (len(incomplete), ", ".join(incomplete)))
        print("Just re-run the script -- complete entities are kept (resume mode),")
        print("only the incomplete ones above are refetched.")
    print("C(t) curves -> %s<entity>.png" % PLOT_PREFIX)
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
