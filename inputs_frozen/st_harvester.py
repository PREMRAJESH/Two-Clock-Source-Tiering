#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
st_harvester.py  --  The Structural Clock, S(t)
================================================
Second clock in the Two-Clock Validation project. Mirrors pt_pilot.py.

WHAT IT DOES
------------
For each of the 50 entities:
  1. Looks up the entity's own homepage on the Wayback Machine at
     T0 / T30 / T60 / T90 / T180 days after its birth date.
  2. Downloads the archived HTML (raw, no Wayback toolbar) for each snapshot.
  3. Scores the page's MACHINE-READABILITY 0-8 (the S(t) score) from 8
     structural components: <title>, <h1>, meta description, JSON-LD,
     schema.org Organization/type, Open Graph tags, social links, content depth.
  4. Pulls Wikidata for canonical inception date, QID, official website and
     aliases (also useful for disambiguating the P(t) probes later).

OUTPUT
------
  st_results.csv        one row per entity x offset (50 x 5 = 250 rows)
  st_wikidata.csv       one row per entity (canonical metadata)
  st_<entity>.png       one S(t) curve per entity (S vs days after birth)

NO API KEY NEEDED. Wayback + Wikidata are free/public.

SETUP (run once, in PowerShell)
-------------------------------
  py -m pip install requests beautifulsoup4 lxml matplotlib

RUN
---
  py st_harvester.py

NOTES
-----
- Snapshots that don't exist in the archive are recorded as status="no_snapshot"
  with S(t) left blank -- honest missing data, not a zero.
- Deep product pages (e.g. openai.com/sora) are archived less densely than root
  domains; the script degrades gracefully. Edit the URL in the ENTITIES block
  if you want a different page for any entity.
- Tunable knobs are all in the CONFIG block below.
"""

import csv
import json
import re
import sys
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

import matplotlib
matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt


# =========================================================================
# CONFIG  --  edit here to add entities, change offsets, or retune scoring
# =========================================================================

# Days after birth at which we sample the structural clock.
SNAPSHOT_OFFSETS = [0, 30, 60, 90, 180]

# Content-depth component: visible words needed to count as "has real content".
CONTENT_DEPTH_MIN_WORDS = 150

# Politeness / robustness.
REQUEST_TIMEOUT = 30          # seconds per HTTP call
SLEEP_BETWEEN_CALLS = 1.0     # seconds, be kind to the archive
MAX_RETRIES = 3
USER_AGENT = "TwoClockValidation/1.0 (research; contact: vivi.mdas@gmail.com)"

# Output file names (written to the current folder).
OUT_RESULTS = "st_results.csv"
OUT_WIKIDATA = "st_wikidata.csv"
PLOT_PREFIX = "st_"           # -> st_<entity>.png

# Entity list: (name, birth_date YYYY-MM-DD, homepage_or_product_url)
# Birth dates carried over from the audited P(t) dataset (Handover v2 sec.4).
# URLs are the entity's OWN controllable web presence -- root domain where the
# entity *is* the company, product/announcement page where it's a sub-brand.
ENTITIES = [
    ("ElevenLabs",              "2023-01-23", "https://elevenlabs.io"),
    ("Cursor",                  "2023-03-01", "https://www.cursor.com"),
    ("GPT-4",                   "2023-03-14", "https://openai.com/gpt-4"),
    ("Mistral AI",              "2023-04-28", "https://mistral.ai"),
    ("Apple Vision Pro",        "2023-06-05", "https://www.apple.com/apple-vision-pro/"),
    ("vLLM",                    "2023-06-20", "https://github.com/vllm-project/vllm"),
    ("Ollama",                  "2023-07-01", "https://ollama.com"),
    ("Threads",                 "2023-07-05", "https://www.threads.net"),
    ("xAI",                     "2023-07-12", "https://x.ai"),
    ("NotebookLM",              "2023-07-12", "https://notebooklm.google"),
    ("DeepSeek",                "2023-07-17", "https://www.deepseek.com"),
    ("Llama 2",                 "2023-07-18", "https://ai.meta.com/llama/"),
    ("Sakana AI",               "2023-08-01", "https://sakana.ai"),
    ("Qwen",                    "2023-08-03", "https://qwenlm.github.io"),
    ("Ideogram",                "2023-08-22", "https://ideogram.ai"),
    ("Kimi",                    "2023-10-09", "https://kimi.moonshot.cn"),
    ("Grok",                    "2023-11-04", "https://x.ai/grok"),
    ("Humane Ai Pin",           "2023-11-09", "https://hu.ma.ne"),
    ("Mamba",                   "2023-12-01", "https://github.com/state-spaces/mamba"),
    ("Gemini (Google model)",   "2023-12-06", "https://deepmind.google/technologies/gemini/"),
    ("Liquid AI",               "2023-12-06", "https://www.liquid.ai"),
    ("Mixtral 8x7B",            "2023-12-08", "https://mistral.ai/news/mixtral-of-experts/"),
    ("Suno",                    "2023-12-20", "https://suno.com"),
    ("Rabbit R1",               "2024-01-09", "https://www.rabbit.tech"),
    ("AlphaGeometry",           "2024-01-17", "https://github.com/google-deepmind/alphageometry"),
    ("Gemini 1.5 Pro",          "2024-02-15", "https://deepmind.google/technologies/gemini/pro/"),
    ("Sora",                    "2024-02-15", "https://openai.com/sora"),
    ("Stable Diffusion 3",      "2024-02-22", "https://stability.ai/news/stable-diffusion-3"),
    ("Claude 3",                "2024-03-04", "https://www.anthropic.com/news/claude-3-family"),
    ("Devin AI",                "2024-03-12", "https://www.cognition-labs.com"),
    ("DBRX",                    "2024-03-27", "https://www.databricks.com/blog/introducing-dbrx-new-state-art-open-llm"),
    ("Command R+",              "2024-04-04", "https://cohere.com/blog/command-r-plus"),
    ("Udio",                    "2024-04-10", "https://www.udio.com"),
    ("Llama 3",                 "2024-04-18", "https://ai.meta.com/blog/meta-llama-3/"),
    ("Phi-3",                   "2024-04-23", "https://azure.microsoft.com/en-us/blog/introducing-phi-3-redefining-whats-possible-with-slms/"),
    ("AlphaFold 3",             "2024-05-08", "https://deepmind.google/technologies/alphafold/"),
    ("GPT-4o",                  "2024-05-13", "https://openai.com/index/hello-gpt-4o/"),
    ("Apple Intelligence",      "2024-06-10", "https://www.apple.com/apple-intelligence/"),
    ("Dream Machine",           "2024-06-12", "https://lumalabs.ai/dream-machine"),
    ("Safe Superintelligence",  "2024-06-19", "https://ssi.inc"),
    ("Black Forest Labs",       "2024-08-01", "https://blackforestlabs.ai"),
    ("OpenAI o1",               "2024-09-12", "https://openai.com/o1/"),
    ("World Labs",              "2024-09-13", "https://www.worldlabs.ai"),
    ("Bolt.new",                "2024-10-04", "https://bolt.new"),
    ("Windsurf",                "2024-11-13", "https://codeium.com/windsurf"),
    ("Lovable",                 "2024-11-21", "https://lovable.dev"),
    ("OpenAI o3",               "2024-12-20", "https://openai.com/o3/"),
    ("DeepSeek-R1",             "2025-01-20", "https://api-docs.deepseek.com/news/news250120"),
    ("Operator",                "2025-01-23", "https://openai.com/index/introducing-operator/"),
    ("Manus",                   "2025-03-06", "https://manus.im"),
]

# Component columns (order = display order in CSV and total).
COMPONENTS = [
    "title", "h1", "meta_description", "json_ld",
    "schema_org_type", "open_graph", "social_links", "content_depth",
]
S_MAX = len(COMPONENTS)  # 8


# =========================================================================
# HTTP helpers
# =========================================================================

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def _get(url, **kw):
    """GET with retries and a timeout. Returns Response or None."""
    kw.setdefault("timeout", REQUEST_TIMEOUT)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = SESSION.get(url, **kw)
            if r.status_code == 200:
                return r
            # 404/short pages from the archive are legitimate "no data".
            if r.status_code in (404, 400):
                return r
        except requests.RequestException:
            pass
        time.sleep(SLEEP_BETWEEN_CALLS * attempt)
    return None


# =========================================================================
# Wayback Machine
# =========================================================================

def find_snapshot(url, target_date):
    """
    Ask the Wayback availability API for the snapshot closest to target_date.
    Returns (timestamp 'YYYYMMDDhhmmss', archived_raw_url) or (None, None).
    """
    ts = target_date.strftime("%Y%m%d")
    api = "https://archive.org/wayback/available"
    r = _get(api, params={"url": url, "timestamp": ts})
    if r is None:
        return None, None
    try:
        data = r.json()
    except ValueError:
        return None, None
    snap = data.get("archived_snapshots", {}).get("closest")
    if not snap or not snap.get("available"):
        return None, None
    stamp = snap.get("timestamp")
    # Rebuild as a RAW capture URL (id_) so the Wayback toolbar/scripts are not
    # injected into the HTML -- keeps the structural score honest.
    raw = "https://web.archive.org/web/%sid_/%s" % (stamp, url)
    return stamp, raw


def fetch_html(archived_raw_url):
    r = _get(archived_raw_url)
    if r is None:
        return None
    # Let requests handle decoding; fall back to utf-8.
    if not r.encoding:
        r.encoding = "utf-8"
    return r.text


# =========================================================================
# Machine-readability scoring  (validated offline against sample HTML)
# =========================================================================

_SOCIAL_RE = re.compile(
    r"(twitter\.com|x\.com|linkedin\.com|facebook\.com|youtube\.com|"
    r"github\.com|instagram\.com|discord\.(gg|com)|t\.me|tiktok\.com)", re.I)

_SCHEMA_TYPE_RE = re.compile(
    r'"@type"\s*:\s*"(Organization|Corporation|LocalBusiness|'
    r'SoftwareApplication|Product|WebSite|TechArticle|Article)"', re.I)


def score_html(html):
    """Return (total 0-8, {component: 0/1}, word_count)."""
    soup = BeautifulSoup(html, "html.parser")
    c = {k: 0 for k in COMPONENTS}

    t = soup.find("title")
    c["title"] = 1 if (t and t.get_text(strip=True)) else 0

    c["h1"] = 1 if soup.find("h1") else 0

    md = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    c["meta_description"] = 1 if (md and md.get("content", "").strip()) else 0

    jsonld = soup.find_all("script", attrs={"type": re.compile(r"application/ld\+json", re.I)})
    c["json_ld"] = 1 if jsonld else 0

    org = 0
    for s in jsonld:
        txt = s.string or s.get_text() or ""
        if _SCHEMA_TYPE_RE.search(txt):
            org = 1
            break
    if not org and soup.find(attrs={"itemtype": re.compile(r"schema\.org", re.I)}):
        org = 1
    c["schema_org_type"] = org

    c["open_graph"] = 1 if soup.find("meta", attrs={"property": re.compile(r"^og:", re.I)}) else 0

    c["social_links"] = 1 if soup.find("a", href=_SOCIAL_RE) else 0

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    words = len(re.findall(r"\w+", soup.get_text(" ", strip=True)))
    c["content_depth"] = 1 if words >= CONTENT_DEPTH_MIN_WORDS else 0

    return sum(c.values()), c, words


# =========================================================================
# Wikidata  (canonical inception date, QID, official website, aliases)
# =========================================================================

def wikidata_lookup(name):
    """Best-effort. Returns dict of canonical metadata (blank fields if miss)."""
    out = {"wikidata_qid": "", "wd_label": "", "wd_inception": "",
           "wd_official_website": "", "wd_aliases": ""}
    r = _get("https://www.wikidata.org/w/api.php", params={
        "action": "wbsearchentities", "search": name, "language": "en",
        "format": "json", "limit": 1, "type": "item"})
    if r is None:
        return out
    try:
        hits = r.json().get("search", [])
    except ValueError:
        return out
    if not hits:
        return out
    qid = hits[0]["id"]
    out["wikidata_qid"] = qid
    out["wd_label"] = hits[0].get("label", "")

    r2 = _get("https://www.wikidata.org/w/api.php", params={
        "action": "wbgetentities", "ids": qid, "format": "json",
        "props": "claims|aliases"})
    if r2 is None:
        return out
    try:
        ent = r2.json()["entities"][qid]
    except (ValueError, KeyError):
        return out

    claims = ent.get("claims", {})
    # P571 inception
    try:
        t = claims["P571"][0]["mainsnak"]["datavalue"]["value"]["time"]
        out["wd_inception"] = t.lstrip("+")[:10]
    except (KeyError, IndexError, TypeError):
        pass
    # P856 official website
    try:
        out["wd_official_website"] = claims["P856"][0]["mainsnak"]["datavalue"]["value"]
    except (KeyError, IndexError, TypeError):
        pass
    # aliases
    try:
        al = [a["value"] for a in ent.get("aliases", {}).get("en", [])]
        out["wd_aliases"] = "; ".join(al)
    except (KeyError, TypeError):
        pass
    return out


# =========================================================================
# Main
# =========================================================================

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main():
    results = []       # rows for st_results.csv
    wiki_rows = []     # rows for st_wikidata.csv

    n = len(ENTITIES)
    for i, (name, birth_str, url) in enumerate(ENTITIES, 1):
        birth = datetime.strptime(birth_str, "%Y-%m-%d")
        print("\n[%d/%d] %s  (born %s)  %s" % (i, n, name, birth_str, url))

        # --- Wikidata (once per entity) ---
        wd = wikidata_lookup(name)
        wiki_rows.append({"entity": name, "birth_date": birth_str,
                          "url": url, **wd})
        if wd["wikidata_qid"]:
            print("   wikidata: %s  inception=%s  site=%s"
                  % (wd["wikidata_qid"], wd["wd_inception"] or "-",
                     wd["wd_official_website"] or "-"))
        time.sleep(SLEEP_BETWEEN_CALLS)

        # --- Structural snapshots ---
        entity_curve = []  # (offset, S) for plotting
        for off in SNAPSHOT_OFFSETS:
            target = birth + timedelta(days=off)
            stamp, raw = find_snapshot(url, target)
            row = {"entity": name, "birth_date": birth_str, "url": url,
                   "offset_days": off, "target_date": target.strftime("%Y-%m-%d"),
                   "snapshot_timestamp": stamp or "", "snapshot_url": raw or "",
                   "S_t": "", "word_count": "", "status": ""}
            for k in COMPONENTS:
                row[k] = ""

            if not stamp:
                row["status"] = "no_snapshot"
                print("   T+%-3d %s -> no snapshot" % (off, target.strftime("%Y-%m-%d")))
            else:
                html = fetch_html(raw)
                if not html:
                    row["status"] = "fetch_failed"
                    print("   T+%-3d %s -> snapshot %s but fetch failed"
                          % (off, target.strftime("%Y-%m-%d"), stamp))
                else:
                    total, comp, words = score_html(html)
                    row["S_t"] = total
                    row["word_count"] = words
                    row["status"] = "ok"
                    for k in COMPONENTS:
                        row[k] = comp[k]
                    entity_curve.append((off, total))
                    print("   T+%-3d %s -> S=%d/%d  (%s)"
                          % (off, target.strftime("%Y-%m-%d"), total, S_MAX,
                             "".join(str(comp[k]) for k in COMPONENTS)))
            results.append(row)
            time.sleep(SLEEP_BETWEEN_CALLS)

        # --- Plot this entity's S(t) curve ---
        if entity_curve:
            fig, ax = plt.subplots(figsize=(7, 4))
            xs = [o for o, _ in entity_curve]
            ys = [s for _, s in entity_curve]
            ax.plot(xs, ys, marker="o", linewidth=2)
            ax.set_title("S(t) - %s  (born %s)" % (name, birth_str))
            ax.set_xlabel("Days after birth")
            ax.set_ylabel("Structural score (0-%d)" % S_MAX)
            ax.set_ylim(-0.3, S_MAX + 0.3)
            ax.set_xticks(SNAPSHOT_OFFSETS)
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            fig.savefig("%s%s.png" % (PLOT_PREFIX, slugify(name)), dpi=120)
            plt.close(fig)   # avoid the >20-figures matplotlib warning

    # --- Write CSVs ---
    res_fields = (["entity", "birth_date", "url", "offset_days", "target_date",
                   "snapshot_timestamp", "S_t"] + COMPONENTS +
                  ["word_count", "status", "snapshot_url"])
    with open(OUT_RESULTS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=res_fields)
        w.writeheader()
        w.writerows(results)

    wiki_fields = ["entity", "birth_date", "url", "wikidata_qid", "wd_label",
                   "wd_inception", "wd_official_website", "wd_aliases"]
    with open(OUT_WIKIDATA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=wiki_fields)
        w.writeheader()
        w.writerows(wiki_rows)

    ok = sum(1 for r in results if r["status"] == "ok")
    print("\n" + "=" * 60)
    print("DONE.  %d rows written to %s  (%d scored, %d missing/failed)"
          % (len(results), OUT_RESULTS, ok, len(results) - ok))
    print("Wikidata metadata -> %s" % OUT_WIKIDATA)
    print("S(t) curves -> %s<entity>.png" % PLOT_PREFIX)
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
