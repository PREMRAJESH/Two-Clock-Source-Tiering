"""
P(t) PILOT — The Perception Clock, reconstructed via the model-cutoff natural experiment
=========================================================================================

Two-Clock Validation Project. Proof-of-method pilot.

WHAT THIS DOES
--------------
For each candidate entity, it asks a ladder of dated LLM snapshots (each with a known
knowledge cutoff) "what is this entity?", scores each answer 0-4 against a ground-truth
reference, and plots score vs. the model's cutoff date. That curve IS a reconstructed P(t).

The x-axis is the model's knowledge cutoff. The vertical dashed line is the entity's real
birth date. The gap between the birth line and where the curve rises = the perception lag.

WHY NOW
-------
The old snapshots that anchor the EARLY end of the curve are being retired through 2026.
The oldest still-queryable OpenAI pair expires ~23 Oct 2026. Run this while they exist.

SETUP
-----
    pip install openai anthropic matplotlib
    export OPENAI_API_KEY="sk-..."          # Windows: set OPENAI_API_KEY=sk-...
    export ANTHROPIC_API_KEY="sk-ant-..."   # either or both; missing provider is skipped
    python pt_pilot.py

OUTPUT
------
    pt_pilot_results.csv   — one row per (entity, model): raw answer + score + notes
    pt_pilot_<entity>.png  — the reconstructed P(t) curve

IMPORTANT
---------
* Browsing/tools are OFF (plain API calls). This is deliberate — with retrieval, P(t)
  collapses into S(t). We want what the *base model* knows.
* Model IDs below are a STARTER LADDER. Verify each against the live API and edit freely.
  Any ID that is unavailable/retired is caught and skipped, not fatal.
* "reported_cutoff" is the vendor-stated cutoff. Treat it as approximate (effective cutoff
  can differ). For a pilot it's fine; for the full study, estimate effective cutoffs.
"""

import os
import csv
import json
import re
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ----------------------------------------------------------------------------------
# CONFIG — edit these three blocks
# ----------------------------------------------------------------------------------

# 1) Entities to probe. The master roster (50 entities, verified birth dates,
#    stratification metadata) lives in entities.py — edit THAT file to add more.
from entities import ENTITIES

# 2) OpenAI model ladder. reported_cutoff = "YYYY-MM". Verify IDs against the live API.
OPENAI_MODELS = [
    {"model": "gpt-4-0613",         "reported_cutoff": "2021-09"},  # expires ~23 Oct 2026
    {"model": "gpt-4o-2024-05-13",  "reported_cutoff": "2023-10"},  # expires ~23 Oct 2026
    {"model": "gpt-4o-2024-11-20",  "reported_cutoff": "2023-10"},
    {"model": "gpt-4.1-2025-04-14", "reported_cutoff": "2024-06"},  # may already be retired
    {"model": "gpt-5.2",            "reported_cutoff": "2025-06"},  # current flagship — adjust
]

# 3) Anthropic model ladder. Verify IDs against the live API.
ANTHROPIC_MODELS = [
    {"model": "claude-opus-4-1-20250805", "reported_cutoff": "2025-01"},  # retires ~5 Aug 2026
    {"model": "claude-sonnet-4-5",        "reported_cutoff": "2025-03"},  # adjust to pinned ID
    {"model": "claude-opus-4-8",          "reported_cutoff": "2025-09"},  # current — adjust
]

# Judge model: scores answers 0-4 against ground_truth. Needs no current knowledge —
# it only compares two strings. Uses OpenAI if available, else Anthropic.
# Judge uses a stable, long-lived model so a wrong "current model" ID can't break scoring.
JUDGE_OPENAI = "gpt-4o-2024-11-20"   # callable ~until Oct 2026; capable enough to score 0-4
JUDGE_ANTHROPIC = "claude-opus-4-8"  # used only if you run Anthropic-only (no OpenAI key)

PROBE_TEMPLATE = (
    "What is {name}? Describe what it is, when it originated, who created it, and what it "
    "does. Be specific. If you are not aware of {name}, say so explicitly rather than "
    "guessing."
)

RUBRIC = """You are scoring how well an AI model's answer recognises an entity.
Compare the ANSWER to the GROUND TRUTH. Score 0-4:

0 = Denies knowing it, says no such thing exists, or describes something unrelated/hallucinated.
1 = Vague name-recognition only; no correct specifics (or mostly wrong).
2 = Partial: correct general category but thin or with notable errors.
3 = Mostly correct with several accurate specifics; minor gaps/errors.
4 = Accurate and specific: matches the ground truth on what it is, origin, creators, and purpose.

Reply with ONLY a JSON object: {"score": <0-4 integer>, "justification": "<one sentence>"}"""

# ----------------------------------------------------------------------------------
# CLIENTS
# ----------------------------------------------------------------------------------

openai_client = None
anthropic_client = None

if os.getenv("OPENAI_API_KEY"):
    try:
        from openai import OpenAI
        openai_client = OpenAI()
    except Exception as e:
        print(f"[warn] OpenAI SDK not ready: {e}")

if os.getenv("ANTHROPIC_API_KEY"):
    try:
        import anthropic
        anthropic_client = anthropic.Anthropic()
    except Exception as e:
        print(f"[warn] Anthropic SDK not ready: {e}")

if not openai_client and not anthropic_client:
    raise SystemExit("No API keys found. Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY.")


# ----------------------------------------------------------------------------------
# QUERY HELPERS  (browsing/tools OFF, temperature 0 where allowed)
# ----------------------------------------------------------------------------------

def ask_openai(model, prompt):
    """Return model's text answer, or raise on unavailable model."""
    kwargs = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    try:
        resp = openai_client.chat.completions.create(temperature=0, **kwargs)
    except Exception as e:
        # Some newer/reasoning models reject temperature — retry without it.
        if "temperature" in str(e).lower():
            resp = openai_client.chat.completions.create(**kwargs)
        else:
            raise
    return resp.choices[0].message.content.strip()


def ask_anthropic(model, prompt):
    resp = anthropic_client.messages.create(
        model=model,
        max_tokens=600,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


def judge(answer, ground_truth):
    """Score an answer 0-4 against ground truth. Returns (score, justification)."""
    content = f"{RUBRIC}\n\nGROUND TRUTH:\n{ground_truth}\n\nANSWER:\n{answer}"
    try:
        if openai_client:
            raw = ask_openai(JUDGE_OPENAI, content)
        else:
            raw = ask_anthropic(JUDGE_ANTHROPIC, content)
    except Exception as e:
        return None, f"judge failed: {e}"
    # Parse JSON; fall back to first digit found.
    try:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        obj = json.loads(m.group(0)) if m else json.loads(raw)
        return int(obj["score"]), obj.get("justification", "")
    except Exception:
        d = re.search(r"[0-4]", raw)
        return (int(d.group(0)) if d else None), f"unparsed judge output: {raw[:120]}"


def cutoff_to_date(yyyy_mm):
    return datetime.strptime(yyyy_mm, "%Y-%m")


# ----------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------

def run():
    ladder = []
    if openai_client:
        ladder += [{**m, "provider": "openai", "ask": ask_openai} for m in OPENAI_MODELS]
    if anthropic_client:
        ladder += [{**m, "provider": "anthropic", "ask": ask_anthropic} for m in ANTHROPIC_MODELS]

    rows = []
    for ent in ENTITIES:
        print(f"\n=== {ent['name']} (born {ent['birth_date']}) ===")
        prompt = PROBE_TEMPLATE.format(name=ent["name"])
        for m in ladder:
            label = f"{m['provider']}:{m['model']}"
            try:
                answer = m["ask"](m["model"], prompt)
            except Exception as e:
                print(f"  [skip] {label}: {e}")
                rows.append({
                    "entity": ent["name"], "birth_date": ent["birth_date"],
                    "provider": m["provider"], "model": m["model"],
                    "reported_cutoff": m["reported_cutoff"], "score": "",
                    "justification": f"model unavailable: {e}", "answer": "",
                })
                continue
            score, why = judge(answer, ent["ground_truth"])
            print(f"  {label:38s} cutoff {m['reported_cutoff']}  ->  score {score}")
            rows.append({
                "entity": ent["name"], "birth_date": ent["birth_date"],
                "provider": m["provider"], "model": m["model"],
                "reported_cutoff": m["reported_cutoff"], "score": score,
                "justification": why, "answer": answer,
            })

    # --- write CSV ---
    csv_path = "pt_pilot_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "entity", "birth_date", "provider", "model",
            "reported_cutoff", "score", "justification", "answer"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved {csv_path}")

    # --- plot one P(t) curve per entity ---
    TIFFANY = "#0ABAB5"
    GRAPHITE = "#3A3A3A"
    for ent in ENTITIES:
        pts = [r for r in rows if r["entity"] == ent["name"] and isinstance(r["score"], int)]
        pts.sort(key=lambda r: cutoff_to_date(r["reported_cutoff"]))
        if not pts:
            print(f"[warn] no scored points for {ent['name']}, skipping plot")
            continue
        xs = [cutoff_to_date(r["reported_cutoff"]) for r in pts]
        ys = [r["score"] for r in pts]

        fig, ax = plt.subplots(figsize=(9, 5.2))
        ax.plot(xs, ys, "-o", color=TIFFANY, linewidth=2.4, markersize=8,
                markerfacecolor=TIFFANY, markeredgecolor="white", zorder=3)
        birth = datetime.strptime(ent["birth_date"], "%Y-%m-%d")
        ax.axvline(birth, color=GRAPHITE, linestyle="--", linewidth=1.4, alpha=0.7)
        ax.text(birth, 4.15, "  entity born", color=GRAPHITE, fontsize=9, va="bottom")

        ax.set_ylim(-0.3, 4.5)
        ax.set_yticks(range(5))
        ax.set_ylabel("Perception score  P(t)   (0 = unknown, 4 = accurate)", fontsize=10)
        ax.set_xlabel("Model knowledge cutoff", fontsize=10)
        ax.set_title(f"Reconstructed Perception Clock — {ent['name']}",
                     fontsize=13, color=GRAPHITE, weight="bold")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.grid(True, alpha=0.25)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        fig.autofmt_xdate()
        fig.tight_layout()
        out = f"pt_pilot_{ent['name'].replace(' ', '_')}.png"
        fig.savefig(out, dpi=150)
        print(f"Saved {out}")


if __name__ == "__main__":
    run()
