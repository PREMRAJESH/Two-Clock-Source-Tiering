# Project Overview & Implementation Report

**Paper:** *"The Two-Clock Model: Structural Presence and AI Perception of Technology Entities"* (Mohan Das, 2026, Zenodo DOI [10.5281/zenodo.21532575](https://doi.org/10.5281/zenodo.21532575))
**Research Contribution:** Citation Source-Tiering / Weighting Analysis
**Repository:** `two-clock-source-tiering/`
**Report last regenerated:** 2026-08-18 — every claim below was verified against the working tree, `git ls-files`, and live script runs on this date; anything not verifiable from a real file is marked *(unverified)* rather than asserted.

---

## 1. Academic Context & Core Research Objective

The paper introduces the **Two-Clock Model**, treating structural web presence $S(t)$ and AI perception $P(t)$ as two representations of an entity's establish-ness moving at different speeds. The perception gap $G(t) = S(t) - P(t)$ is predicted to close as third-party news citations $C(t)$ accumulate.

- **Baseline Paper Finding (Unweighted Raw Counts):** Citation ramps precede perception onsets in **28 of 33 testable entities (85%)**, with a median lead of **83 days** (two-sided exact sign test $p = 6.6 \times 10^{-5}$).
- **Assigned Research Contribution:** Test whether weighting news citations by source authority ($C_{\text{weighted}}(t)$ vs. raw unweighted mention counts $C(t)$) strengthens or weakens the precedence result.
- **Scientific Standard:** A null result (weighting does not improve precedence) is an acceptable, reportable finding. Methodological choices must be honest, reproducible, and traceably justified rather than selected to force a predetermined outcome.

---

## 2. Repository Layout (as it exists right now)

```
two-clock-source-tiering/
├── inputs_frozen/               <- READ-ONLY frozen v1 deposit + received labeled data
│   ├── ct_results_v1_frozen.csv   <- Raw weekly citation series C(t) (no per-source field)
│   ├── pt_pilot_results.csv       <- Perception ladder P(t) across model cutoffs
│   ├── ct_artlist_precision.csv   <- Disambiguation precision audit (PASS/FAIL/NOT_AUDITED)
│   ├── ct_artlist_LABELING.xlsx   <- Viveka's labeled article file (RECEIVED; Label sheet:
│   │                                  #, entity, window, date, title, domain, url,
│   │                                  suggested_label, relevant)
│   ├── ct_harvester.py            <- Her original C(t) harvester (TimelineVolRaw mode)
│   ├── st_harvester.py            <- Structural presence (S(t)) harvester
│   ├── st_results.csv             <- S(t) results
│   ├── pt_pilot.py                <- Perception pilot runner
│   ├── entities.py                <- 50-entity roster with birth dates and flags
│   └── README.md                  <- Frozen-deposit documentation
├── scripts/                     <- All working code
│   ├── reproduce_baseline.py       <- Exact paper-baseline reproduction (28/33)
│   ├── ct_artlist_audit.py         <- Browser-lane query-precision audit; v2 contrast-week
│   │                                 URL generation + JSON ingest (NEW, untracked)
│   ├── ct_artlist_harvester.py     <- Viveka's article harvester (renamed from the
│   │                                 space-containing "ct artlist harvester.py")
│   ├── ct_source_harvester.py      <- Our peak-week GDELT ArtList harvester (~30 entities)
│   ├── verify_week_match.py        <- Phase 0 spot-check script (STALE/SUPERSEDED, see §5)
│   ├── merge_source_data.py        <- Task 1: merged source/domain data
│   ├── build_tier_map.py           <- Task 2: Jenks natural-breaks tier assignment
│   ├── apply_weights.py            <- Task 3: tier map -> weighted C(t)
│   ├── precedence_test_weighted.py <- Task 4: exact sign test, raw vs weighted
│   ├── sensitivity_analysis.py     <- Task 5: Table 2 grid + weight sweep + perturbations
│   ├── test_pipeline_smoketest.py  <- Task 6: isolated end-to-end smoke test
│   └── __pycache__/                <- gitignored, untracked
├── data_derived/                <- Generated outputs (regenerable; see §4.2 tracking policy)
│   ├── precedence_comparison.csv   <- TRACKED milestone: raw-fallback run, 2026-08-17
│   ├── sensitivity_results.csv     <- TRACKED milestone: Table 2 mirror grid, raw-fallback
│   └── .placeholder.md             <- TRACKED dir placeholder from first commit
├── reference/                   <- Non-run artifacts
│   └── gdelt_artlist_sample_response.json <- TRACKED sample GDELT ArtList JSON
├── docs/                        <- Decision log + methodology
│   ├── session_log.md              <- Chronological decisions/state (source of truth for decisions)
│   ├── project_overview_report.md  <- This file
│   └── tier_methodology.md         <- Tier-definition rationale (still DRAFT/template —
│                                      intentionally not filled in until real domain data exists)
├── .venv/                       <- Project-local virtualenv (gitignored) — see §4.3
├── .gitignore
├── LICENSE-CODE.md
├── LICENSE-DATA.md
└── README.md
```

Tracked files (`git ls-files`, 2026-08-18): everything under `inputs_frozen/`, all `scripts/*.py`, both `data_derived` milestone CSVs + `.placeholder.md`, `reference/gdelt_artlist_sample_response.json`, `docs/*`, `.gitignore`, both LICENSE files, `README.md`.

Not tracked by design: `.venv/`, `scripts/__pycache__/` (both `.gitignore`-covered), and any new `data_derived/*` file (see §4.2). The only untracked source file is `scripts/ct_artlist_audit.py` (deliberately held pending the manual-collection milestone).

---

## 3. Task-by-Task Implementation Summary

### Baseline Reproduction — CONFIRMED (the paper result is real and reproducible)

**File:** `scripts/reproduce_baseline.py`

- **Exact exclusion rule, verified against paper Sections 4.5 (Table 1) and 5.4:**
  - **TESTABLE 33 = all 50 entities MINUS 17:**
    - **10 precision-audit FAIL** (Section 4.5): `DBRX`, `Kimi`, `Ideogram`, `Lovable`, `Gemini (Google model)`, `Dream Machine`, `Liquid AI`, `Mamba`, `Operator`, `vLLM`
    - **7 no-onset entities** (Section 5.4): `OpenAI o1`, `OpenAI o3`, `DeepSeek`, `DeepSeek-R1`, `Manus`, `World Labs`, `Bolt.new`
- **Result, re-verified live 2026-08-18 (running the actual script, venv Python):**
  - Floor=3: **28/33**, median lead **83 days**, p = **6.62×10⁻⁵** → `PASS`
  - Floor=5: **28/33**, median lead **83 days**, p = **6.62×10⁻⁵** → `PASS`
- **Verified in the real pipeline, not just the standalone checker:** `scripts/precedence_test_weighted.py` carries the same `PRECISION_FAIL` / `NO_ONSET` / `PAPER_EXCLUDED` sets plus the PT↔CT name bridge, and `scripts/sensitivity_analysis.py` imports that exclusion logic (`load_paper_excluded_entities`). The raw-fallback run committed to `data_derived/` confirms it on disk:
  - `sensitivity_results.csv` → row `baseline,0.1,3,raw,...,28,33,0,83,6.618769839406013e-05`
  - `precedence_comparison.csv` → per-entity ramp/onset/lead for the 33 testable entities.
- **Caveat from the raw-fallback run:** the weighted/tier1/tier12 columns are all empty in those milestone CSVs — they were produced *before* any weighted source data existed. They validate the raw baseline and the pipeline mechanics only.

### The `self_ref_openai` bug — found and fixed (commit `e3a12e7`)

- **The bug:** `precedence_test_weighted.py` originally excluded entities using the `self_ref_openai` flag from `inputs_frozen/entities.py`. That flag is **NOT** part of the paper's baseline — it exists for a separate self-recognition confound analysis (OpenAI entities probed on an OpenAI ladder).
- **What it would have broken:** GPT-4, GPT-4o, and Sora (all flagged `self_ref_openai`) would have been silently excluded from the baseline, so the "28/33" reproduction would instead have been a non-paper subset — the headline result would not be traceable to the paper's rule at all.
- **Second half of the same fix:** the perception CSV (`pt_pilot_results.csv`) uses parenthetical disambiguators (e.g. `Cursor (the AI code editor)`) while the citation CSV uses short names (e.g. `Cursor`). **14 of 50 entities** are affected. A join on raw entity name silently dropped all 14, leaving only **26 testable entities** instead of 33. Fixed with a canonical name bridge (`build_name_bridge` / `_base_name`) that strips parentheticals. Live output of the bridge (verified 2026-08-18): 14 mappings, e.g. `Gemini (the Google AI model) -> Gemini (Google model)`, `Sora (the OpenAI model) -> Sora`.

### The `other_week` mismatch investigation — RESOLVED/CLOSED (see §5 for the full record)

Short version: Viveka's original second-week rule was found to be **unrecoverable** (the original pull parameters no longer exist), an independent computation against `ct_results_v1_frozen.csv` **mismatched** the one known xlsx value, and the resolution is a new **deterministic `contrast_week` (v2)** method shipped in `scripts/ct_artlist_audit.py`. The old rule is retired, not corrected. Full detail in §5.

### Task 0: Phase 0 Spot-Check — SUPERSEDED, not blocking

**File:** `scripts/verify_week_match.py` (stale — see below)

Originally the gatekeeper for the whole weighting pipeline: compare the `other_week` from Viveka's harvester against the week recorded in `ct_artlist_LABELING.xlsx` for Kimi and Mamba, and block weighting until it passed.

Current reality, verified on disk:
- Viveka's harvester **was received** (now `scripts/ct_artlist_harvester.py`) and the LABELING xlsx **was received** (`inputs_frozen/ct_artlist_LABELING.xlsx`).
- Her harvester's output CSV `ct_artlist_results.csv` is **still not present anywhere** on this machine (`data_derived/` has only the two milestone CSVs; `verify_week_match.py` points at `../data_derived/ct_artlist_results.csv`, which does not exist).
- The spot-check's premise (that the old `other_week` is the correct second sample) is **moot**: the old rule is unrecoverable and replaced by v2 `contrast_week` (§5). `verify_week_match.py` therefore **should not be run as-is**; it is stale scaffolding that references files and a method that no longer govern the pipeline.

### Tasks 1–6: Weighting pipeline scaffolding — 100% complete, smoke-tested, waiting on source data

All six pipeline scripts exist and are structurally complete. `scripts/test_pipeline_smoketest.py` creates an isolated sandbox, generates synthetic data (10 entities / 18 domains), runs Tasks 1–5 end-to-end, validates stdout/GVF/sensitivity outputs, and cleans up. It **passed cleanly** (per `docs/session_log.md`, 2026-08-16; the smoke test script is on disk).

**None of Tasks 1–6 has been run on real source data** — they are awaiting the article/domain evidence from the source-collection lane (§6 blockers). The committed milestone CSVs are the raw-fallback baseline outputs only.

### Source-data collection lanes

- **Viveka's lane (22 overridden entities):** `scripts/ct_artlist_audit.py` is the current browser-lane tool. `--contrast-urls` generates the 22 GDELT ArtList URLs (one per overridden entity, ~9 min at 25s apart). The JSON files those URLs produce are then ingested with `--contrast` into `ct_artlist_contrast.csv`. **Status: 0/22 JSON files collected (§6, active blocker).**
- **Our lane (~30 remaining entities):** `scripts/ct_source_harvester.py` (peak-week, GDELT ArtList, rate-limit-safe). Pending the `ALREADY_COVERED` entity list and the method decision. **Not yet run against live GDELT.**
- `reference/gdelt_artlist_sample_response.json` is a small sample response for reference/testing only.

---

## 4. Methodology & Infrastructure Decisions

### 4.1 Source-tier methodology

Documented in `docs/tier_methodology.md`. It is still explicitly a **DRAFT/template** — tier boundaries are not pre-assigned from assumption; they are to be filled in only after real domain data exists, using Approach B (empirical Jenks natural breaks on $\log(\text{breadth} \times \text{volume})$, GVF ≥ 0.70) with a documented syndication/aggregator caveat and a precision-audit cross-check. NewsGuard / Moz DA are paywalled and intentionally not used.

### 4.2 `data_derived/` tracking policy (decided 2026-08-18)

- **Ignore `data_derived/*` by default** (`.gitignore`), because it is regenerable scratch output; reproducibility rests on frozen inputs + pinned scripts + the decision log.
- **Deliberate milestone snapshots** are committed with `git add -f`.
- **Currently tracked:** `data_derived/precedence_comparison.csv` and `data_derived/sensitivity_results.csv` (the 2026-08-17 raw-fallback run, committed `9e24bc3`), plus the `data_derived/.placeholder.md` from the first commit. Future regenerated CSVs (e.g. `ct_artlist_contrast.csv`, `ct_results_weighted.csv`) will be ignored until deliberately force-added.
- Reasoned rationale recorded in `docs/session_log.md` (2026-08-18 entry).

### 4.3 Project-local virtualenv policy (decided 2026-08-18)

- **Never install into the global `C:\Python` interpreter again.** Earlier that day the global env's broken numpy/matplotlib/Pillow/kiwisolver/contourpy C-extensions were repaired via pip (cp314 wheels) to unblock the audit script — a one-off, with the acknowledged risk of breaking other Python work on this machine that pins older versions.
- **Use the repo-root `.venv`** (already `.gitignore`-covered) for all project runs: `.venv\Scripts\python.exe`. It currently contains only `requests` + `matplotlib` (pandas is not required by `ct_harvester` or the audit script).
- Verified 2026-08-18: `.venv\Scripts\python.exe scripts/ct_artlist_audit.py --contrast-urls` and `scripts/reproduce_baseline.py` both run clean under the venv.

### 4.4 Model-retirement facts (Viveka-verified 2026-08-18)

- **gpt-4.1 is NOT retiring.** Viveka checked OpenAI's official model page directly; only the separate "nano" variant is being retired. Treat gpt-4.1 as stable.
- **`gpt-4-0613` and `gpt-4o-2024-05-13` retire Oct 23, 2026** — confirmed. This anchors the earliest point on the perception curve; the two remaining P(t) reruns must happen before the cutoff. Viveka targets early-to-mid October. No Anthropic/Claude fallback logic is needed — the two reruns use the original OpenAI-only ladder.

---

## 5. The `other_week` Mismatch Investigation (full record)

**Status: RESOLVED / CLOSED (2026-08-18).**

1. **What was tested.** `scripts/ct_artlist_harvester.py` (Viveka's) selects two weeks per entity: `peak_week` (max `mention_count`) and `other_week`. The `other_week` selection is an assumption about how her original 22-entity file chose its second week.
2. **Independent verification.** Ran her exact algorithm against `inputs_frozen/ct_results_v1_frozen.csv` for Mamba (140 `status=ok` weeks, ranked descending):
   - `peak_week = weeks[0]` = **2025-03-31** (count 28)
   - `other_week = weeks[140 // 2] = weeks[70]` = **2025-09-29** (count 1; no fallback triggered)
3. **Result: peak side MATCHES, other_week side MISMATCHES.**
   - The xlsx's 25 Mamba `peak_week` article rows are dated 2025-04-03/04, inside the computed peak week — consistent.
   - The xlsx's single known Mamba `other_week` value is **2024-01-26** (a Friday article date; its Monday-week 2024-01-22 is ranked only #46 today) — **not** the computed 2025-09-29.
4. **Why it diverges (cannot be pinned down further):** the original 22-entity pull likely ran against an earlier snapshot of the frozen series (fewer weeks → different median index); the median-by-count strategy was itself a script assertion; and `TimelineVolRaw` aggregate counts can rank a week differently than ArtList's actual article count. The original pull parameters are gone.
5. **Resolution — Viveka's `scripts/ct_artlist_audit.py` confirms the old rule is unrecoverable and replaces it.** Quoting its own docstring:
   > "Documented 2026-08-18 replacement for the original (unrecoverable) second-week rule ... Picks a week that genuinely contrasts peak_week (>= min_gap_weeks away), deterministically: seeded on entity name + a fixed version tag only, never on a run date or row order, so re-running this later reproduces the same pick even if unrelated rows are added to results_path."
   The legacy v1 lane in that script (`peak_and_random_week()`) confirms the old audit's second-week pick was **random** (`random.Random("ctaudit-<entity>-20260708")`), so it was never reproducible. The deterministic v2 `contrast_week()` (min 4-week gap from peak, seeded per entity, `random.seed(20260708)`) is the go-forward method.
6. **Consequence:** the Mamba divergence is **moot** — the old rule is retired, not fixed. `verify_week_match.py` is superseded. Kimi is no longer blocked by the xlsx lacking an `other_week` row: `--contrast-urls` generates Kimi's `contrast_week` (2026-03-16) directly.
7. Full trace in `docs/session_log.md` (2026-08-18 entries, including the resolution).

---

## 6. Current Status — Genuinely Blocking vs. Resolved

Be honest version. **Blocking** = nothing can proceed on that path until it clears. **Resolved** = closed on disk with a committed decision.

### Blocking (active, real)

| Item | Status | Detail |
|---|---|---|
| **Manual GDELT JSON collection** | **BLOCKED — 0/22 collected** | The 22 ArtList URLs for the overridden entities exist and are generated by `--contrast-urls`, but **as of 2026-08-18 zero of the 22 JSON files exist anywhere on this machine** (verified: `scripts/`, repo root, Downloads, Desktop, Documents all empty of them). An earlier message claiming the files were collected was incorrect — nothing was found on disk. Until the JSONs are actually saved into `scripts/`, `--contrast` cannot run and no `ct_artlist_contrast.csv` can be produced. |
| **27 AMBER precision-audit rows** | **BLOCKED (manual)** | Manual relevance judgment rows; kept deliberately separate from the automated pipeline. Needs a human (jointly with Viveka) to finish. |

### Resolved (closed, on disk)

| Item | Status |
|---|---|
| Baseline reproduction 28/33 / 83d / 6.62e-05 | **CONFIRMED** (both floors; live run 2026-08-18; pipeline + standalone) |
| `self_ref_openai` exclusion bug + PT↔CT name bridge | **FIXED** (commit `e3a12e7`; would have silently dropped GPT-4/GPT-4o/Sora and 14 disambiguated names → 26/33) |
| `other_week` mismatch investigation | **CLOSED** — old rule unrecoverable, replaced by deterministic v2 `contrast_week` |
| File placement cleanup (JSON sample, LABELING xlsx, harvester rename) | **DONE** (committed `d478763`) |
| gpt-4.1 retirement question | **RESOLVED** — not retiring; no action |
| Oct 23, 2026 P(t) deadline | **TRACKED** — internal TODO flagged for early-to-mid-October follow-up |
| `data_derived/` tracking policy | **DECIDED** (ignore default, `git add -f` milestones) |
| Project-local `.venv` policy | **DECIDED** (never touch global interpreter again) |
| Pipeline scaffolding Tasks 1–6 | **COMPLETE + smoke-tested** — but not yet run on real source data |
| Raw-fallback analysis run | **EXECUTED** (2026-08-17; milestone CSVs tracked) |

### Pending but not blocking

- Weighting pipeline execution on real source data (Tasks 1–6) — awaits the source-collection lanes.
- `ct_artlist_results.csv` from Viveka — no longer required for the v2 lane; only relevant if the old median rule ever needs reconciliation.
- Remaining ~30-entity source pull (`ct_source_harvester.py`) — pending `ALREADY_COVERED` list and method decision; not yet run.
- `docs/tier_methodology.md` content — intentionally unfilled until real domain data exists.

---

## 7. What's Still Needed from Viveka vs. Fully in Our Hands

### Fully in our hands now (no dependency on her)

- Baseline reproduction and the whole `precedence_test_weighted.py` / `sensitivity_analysis.py` pipeline.
- The v2 `contrast_week` audit lane (`ct_artlist_audit.py`): URL generation, JSON ingest, CSV output.
- The manual GDELT collection itself (open each URL, Ctrl+S the JSON, drop into `scripts/`) — this is our action, not hers.
- The project-local `.venv`, tracking policies, and repo hygiene.

### Still needed from Viveka (or joint)

1. **27 AMBER precision-audit judgments** — the manual labeling pass she originally asked us to verify; joint human task.
2. **Two P(t) reruns before Oct 23, 2026** — hers, targeting early-to-mid October (tracked in the status table as an internal reminder).
3. *(Optional / low priority)* `ct_artlist_results.csv` (her harvester's output) — only if the old median rule ever needs reconciling; not required by the v2 lane.
4. *(When we reach it)* `ALREADY_COVERED` entity-list confirmation for `ct_source_harvester.py`'s ~30-entity pull.

---

## 8. Commit History (for traceability)

```
905d4f2 ignore regenerable data_derived outputs by default; log tracking policy
9e24bc3 add raw-fallback precedence/sensitivity outputs (2026-08-17 run, pre-weighting)
0b28d62 log Mamba other_week mismatch findings
d478763 add Viveka's harvester, LABELING xlsx, and GDELT sample response; log Mamba other_week mismatch
d61ed36 log Viveka model-retirement verification; flag Oct 23 P(t) deadline in status table
e3a12e7 Align exclusion rule and entity joins with paper baseline
520f709 baseline reproduction: 28/33 exact match confirmed (Section 4.5+5.4 exclusion rule, not self_ref_openai)
8107fa0 add updated Project Overview and Implementation Report
ff7e57f first commit
```