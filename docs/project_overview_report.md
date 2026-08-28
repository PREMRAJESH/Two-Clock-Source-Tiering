# Project Overview & Implementation Report

**Paper:** *"The Two-Clock Model: Structural Presence and AI Perception of Technology Entities"* (Mohan Das, 2026, Zenodo DOI [10.5281/zenodo.21532575](https://doi.org/10.5281/zenodo.21532575))
**Research Contribution:** Citation Source-Tiering / Weighting Analysis
**Repository:** `two-clock-source-tiering/`
**Report last regenerated:** 2026-08-22 -- every claim below was verified against the working tree, `git ls-files`, and `git log` on this date; anything not verifiable from a real file is marked *(unverified)* rather than asserted.

---

## 1. Academic Context & Core Research Objective

The paper introduces the **Two-Clock Model**, treating structural web presence S(t) and AI perception P(t) as two representations of an entity's establish-ness moving at different speeds. The perception gap G(t) = S(t) - P(t) is predicted to close as third-party news citations C(t) accumulate.

- **Baseline Paper Finding (Unweighted Raw Counts):** Citation ramps precede perception onsets in **28 of 33 testable entities (85%)**, with a median lead of **83 days** (two-sided exact sign test p = 6.6 x 10^-5).
- **Assigned Research Contribution:** Test whether weighting news citations by source authority (C_weighted(t) vs. raw unweighted mention counts C(t)) strengthens or weakens the precedence result.
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
│   │                                 URL generation + JSON ingest (TRACKED, committed cd47959)
│   ├── ct_artlist_harvester.py     <- Viveka's article harvester (SUPERSEDED, other_week retired)
│   ├── ct_source_harvester.py      <- Our peak-week GDELT ArtList harvester (28 remaining entities;
│   │                                 ALREADY_COVERED populated, not yet run against live GDELT)
│   ├── verify_week_match.py        <- Phase 0 spot-check script (STALE/SUPERSEDED, see section 5)
│   ├── merge_source_data.py        <- Task 1: merged source/domain data
│   ├── build_tier_map.py           <- Task 2: Jenks natural-breaks tier assignment
│   ├── apply_weights.py            <- Task 3: tier map -> weighted C(t)
│   ├── precedence_test_weighted.py <- Task 4: exact sign test, raw vs weighted
│   ├── sensitivity_analysis.py     <- Task 5: Table 2 grid + weight sweep + perturbations
│   ├── test_pipeline_smoketest.py  <- Task 6: isolated end-to-end smoke test
│   ├── README.md                   <- Computational methods index
│   └── __pycache__/                <- gitignored, untracked
├── data_derived/                <- Generated outputs (regenerable; see section 4.2 tracking policy)
│   ├── ct_artlist_contrast.csv     <- TRACKED milestone: 22-entity contrast-week audit batch
│   │                                 (263 rows, 78y/185n; triage complete 2026-08-25)
│   ├── amber_rows_review.csv       <- TRACKED: 27 AMBER rows, labeled 16y/5n/6 unverifiable
│   ├── precedence_comparison.csv   <- TRACKED milestone: raw-fallback run, 2026-08-17
│   ├── sensitivity_results.csv     <- TRACKED milestone: Table 2 mirror grid, raw-fallback
│   ├── README.md                   <- Derived-outputs record
│   └── .placeholder.md             <- TRACKED dir placeholder from first commit
├── reference/                   <- Non-run artifacts
│   ├── contrast_collection_2026-08-18/ <- Archived raw GDELT ArtList JSONs (22 files)
│   │   ├── README.md
│   │   ├── 01_Cursor.json ... 22_Manus.json
│   ├── gdelt_artlist_sample_response.json <- Sample GDELT ArtList JSON
│   └── README.md                   <- Reference evidence index
├── docs/                        <- Decision log + methodology
│   ├── session_log.md              <- Chronological decisions/state (source of truth for decisions)
│   ├── project_overview_report.md  <- This file
│   ├── tier_methodology.md         <- Tier-definition rationale (still DRAFT/template)
│   └── README.md                   <- Research documentation index
├── .venv/                       <- Project-local virtualenv (gitignored) -- see section 4.3
├── .gitignore
├── LICENSE-CODE.md
├── LICENSE-DATA.md
└── README.md                      <- Research repository overview
```

Tracked files (`git ls-files`, 2026-08-22): everything under `inputs_frozen/`, all `scripts/*.py`, all `data_derived/` milestone files (ct_artlist_contrast.csv, amber_rows_review.csv, precedence_comparison.csv, sensitivity_results.csv, .placeholder.md, README.md), everything under `reference/` (22 archive JSONs + sample JSON + READMEs), all `docs/` files, `.gitignore`, both LICENSE files, `README.md`, and `scripts/README.md`.

Not tracked by design: `.venv/`, `scripts/__pycache__/`, `inputs_frozen/__pycache__/` (all `.gitignore`-covered).

---

## 3. Task-by-Task Implementation Summary

### Baseline Reproduction -- CONFIRMED (the paper result is real and reproducible)

**File:** `scripts/reproduce_baseline.py`

- **Exact exclusion rule, verified against paper Sections 4.5 (Table 1) and 5.4:**
  - **TESTABLE 33 = all 50 entities MINUS 17:**
    - **10 precision-audit FAIL** (Section 4.5): DBRX, Kimi, Ideogram, Lovable, Gemini (Google model), Dream Machine, Liquid AI, Mamba, Operator, vLLM
    - **7 no-onset entities** (Section 5.4): OpenAI o1, OpenAI o3, DeepSeek, DeepSeek-R1, Manus, World Labs, Bolt.new
- **Result, re-verified live 2026-08-18 (running the actual script, venv Python):**
  - Floor=3: **28/33**, median lead **83 days**, p = **6.62x10^-5** -> PASS
  - Floor=5: **28/33**, median lead **83 days**, p = **6.62x10^-5** -> PASS
- **Verified in the real pipeline:** `scripts/precedence_test_weighted.py` carries the same exclusion sets plus the PT<->CT name bridge, and `scripts/sensitivity_analysis.py` imports that exclusion logic. The raw-fallback run confirms it on disk.
- **Caveat from the raw-fallback run:** the weighted/tier1/tier12 columns are all empty -- they were produced *before* any weighted source data existed.

### The self_ref_openai bug -- found and fixed (commit e3a12e7)

- **The bug:** `precedence_test_weighted.py` originally excluded entities using the `self_ref_openai` flag. That flag is **NOT** part of the paper's baseline.
- **What it would have broken:** GPT-4, GPT-4o, and Sora would have been silently excluded, producing a non-paper subset.
- **Second half of the same fix:** 14 of 50 entities use parenthetical disambiguators in the perception CSV. A raw join silently dropped all 14, leaving only 26 testable entities instead of 33. Fixed with a canonical name bridge.

### The :port domain-normalization bug -- found and fixed (commit 880c107)

- **The bug:** `normalize_domain()` in `scripts/merge_source_data.py` did not strip the trailing `:port` from URLs. The contrast-audit QA surfaced `asiaone.com:443` and `asiaone.com` counting as separate domains.
- **What it would have broken:** Domain-level breadth/volume metrics would be distorted; tier assignment potentially affected.
- **Fix:** `normalize_domain()` now strips trailing `:port`. Both `read_viveka()` and `read_harvester()` call it. Smoke test passes.
- **Also committed in 880c107:** documented syndication examples added to `docs/tier_methodology.md` (Threads 6x NBC affiliates, Operator 4x Nine papers, Qwen 5x independent outlets).
- **Session-log gap:** previously documented only in the commit message. Now recorded in `docs/session_log.md` (2026-08-22 catch-up entry).

### The other_week mismatch investigation -- RESOLVED/CLOSED (see section 5)

Viveka's original second-week rule was found to be **unrecoverable**. Resolution: a new deterministic `contrast_week` (v2) method in `scripts/ct_artlist_audit.py`. The old rule is retired, not corrected.

### Task 0: Phase 0 Spot-Check -- SUPERSEDED, not blocking

**File:** `scripts/verify_week_match.py` (stale)

References `../data_derived/ct_artlist_results.csv` which does not exist. The old `other_week` rule is retired. **Do not run.**

### Tasks 1-6: Weighting pipeline scaffolding -- complete, smoke-tested, waiting on source data

All six pipeline scripts exist and are structurally complete. Smoke test passed cleanly. **None has been run on real source data.** The committed milestone CSVs are raw-fallback baseline outputs only.

### Source-data collection lanes

> **Methodology decision (2026-08-18, audited):** the ANALYTICAL source
> sample is `peak_week`-only in BOTH lanes. The second-week sample
> (`contrast_week`, v2) is a query-precision AUDIT for the 22 overridden
> entities only -- it is validation data, not tier-map evidence.

- **Viveka's lane (22 overridden entities):** **Status: 22/22 collected, 263 article rows, raw JSONs archived `reference/contrast_collection_2026-08-18/`, committed cd47959. A `needs_translation` column (boolean, 31 of 263 flagged) was added 2026-08-22.**
- **Our lane (28 remaining entities):** `ALREADY_COVERED` is populated with the exact 22 entity names from the xlsx (verified 2026-08-22). **Not yet run against live GDELT.**

---

## 4. Methodology & Infrastructure Decisions

### 4.1 Source-tier methodology

Documented in `docs/tier_methodology.md`. Still explicitly a **DRAFT/template** -- tier boundaries are not pre-assigned from assumption.

### 4.2 data_derived/ tracking policy (decided 2026-08-18)

- **Ignore by default** (`.gitignore`); reproducibility rests on frozen inputs + pinned scripts + decision log.
- **Deliberate milestone snapshots** committed with `git add -f`.
- **Currently tracked:** ct_artlist_contrast.csv (cd47959), amber_rows_review.csv (3b50d5b), precedence_comparison.csv and sensitivity_results.csv (9e24bc3), data_derived/README.md (08b7dbd), .placeholder.md.

### 4.3 Project-local virtualenv policy (decided 2026-08-18)

- **Never install into the global C:\Python interpreter again.**
- **Use the repo-root .venv** for all project runs. Currently contains `requests`, `matplotlib`, and `openpyxl`.

### 4.4 Model-retirement facts (Viveka-verified 2026-08-18)

- **gpt-4.1 is NOT retiring.** Only the separate "nano" variant is being retired.
- **gpt-4-0613 and gpt-4o-2024-05-13 retire Oct 23, 2026.** Two remaining P(t) reruns must happen before then.

---

## 5. The other_week Mismatch Investigation (full record)

**Status: RESOLVED / CLOSED (2026-08-18).**

Full detail in `docs/session_log.md` (2026-08-18 entries). The deterministic v2 `contrast_week()` (min 4-week gap from peak, seeded per entity, `random.seed(20260708)`) is the go-forward method.

---

## 6. Current Status -- Genuinely Blocking vs. Resolved

### Blocking (active, real)

| Item | Status | Detail |
|---|---|---|
| **27 AMBER precision-audit rows** | **COMPLETE (manual)** | Extracted to `data_derived/amber_rows_review.csv` (27 rows, entity breakdown: Apple Intelligence 13, Kimi 10, Qwen 2, Dream Machine 1, Lovable 1). Final distribution: **16 `y`, 5 `n`, 6 `unverifiable`** (dead links / redirect mismatches; see session log 2026-08-22). |
| **263-row contrast-week precision batch** | **COMPLETE** | `data_derived/ct_artlist_contrast.csv` (22/22 entities, 263 rows). **263/263 labeled, 78y/185n.** Committed 886019f. `needs_translation` column (31 flagged) added 2026-08-22. |

### Resolved (closed, on disk)

| Item | Status |
|---|---|
| Baseline reproduction 28/33 / 83d / 6.62e-05 | **CONFIRMED** (both floors; live run 2026-08-18) |
| self_ref_openai exclusion bug + PT<->CT name bridge | **FIXED** (commit e3a12e7) |
| :port domain-normalization bug | **FIXED** (commit 880c107) |
| other_week mismatch investigation | **CLOSED** -- replaced by deterministic v2 contrast_week |
| File placement cleanup | **DONE** (committed d478763) |
| gpt-4.1 retirement question | **RESOLVED** -- not retiring |
| Oct 23, 2026 P(t) deadline | **TRACKED** -- early-to-mid October |
| data_derived/ tracking policy | **DECIDED** (ignore default, git add -f milestones) |
| Project-local .venv policy | **DECIDED** |
| Pipeline scaffolding Tasks 1-6 | **COMPLETE + smoke-tested** |
| Raw-fallback analysis run | **EXECUTED** (2026-08-17; milestone CSVs tracked) |
| 22-entity contrast-week audit collection | **COMPLETE** (22/22, 263 rows; committed cd47959); labeling pending |
| AMBER rows extraction | **COMPLETE** (27 rows to amber_rows_review.csv; labeled 16y/5n/6 unverifiable, committed `3b50d5b`) |
| ALREADY_COVERED populated | **COMPLETE** (22 entities; 28 remaining for Lane B) |
| needs_translation flagging | **COMPLETE** (31 of 263 flagged) |
| Documentation rewrite (7 READMEs) | **COMPLETE** (committed 08b7dbd) |
| 263-row contrast-week triage | **COMPLETE** (263/263 labeled, 78y/185n; committed 886019f) |
| Report regeneration | **COMPLETE** (this file, 2026-08-22) |

### Pending but not blocking

- Weighting pipeline execution on real source data (Tasks 1-6) -- awaits the source-collection lanes.
- Remaining 28-entity source pull (`ct_source_harvester.py`) -- ALREADY_COVERED populated, not yet run.
- `docs/tier_methodology.md` content -- intentionally unfilled until real domain data exists.

---

## 7. What's Still Needed from Viveka vs. Fully in Our Hands

### Fully in our hands now (no dependency on her)

- Baseline reproduction and the whole precedence/sensitivity pipeline.
- The v2 contrast_week audit lane (ct_artlist_audit.py): URL generation, JSON ingest, CSV output.
- The 28-entity Lane B harvest (ct_source_harvester.py): ALREADY_COVERED populated, ready to run when rate-limit budget allows.
- The project-local .venv, tracking policies, and repo hygiene.

### Still needed from Viveka (or joint)

1. **Sign-off on the AMBER-batch reconciliation** (CSV-vs-master export bug, 5 Kimi y->n overrides) -- labeling itself is complete (16y/5n/6 unverifiable), but her review/confirmation of these specific decisions is still open.
2. **Two P(t) reruns before Oct 23, 2026** -- hers, targeting early-to-mid October.

---

## 8. Commit History (for traceability)

```
886019f post-triage adjustments: xAI 8 rows n->y (product coverage), Apple Vision Pro L30 n->y (discontinuation cycle); 78y/185n total
3b50d5b AMBER extraction, ALREADY_COVERED, needs_translation flag, session-log catch-up
08b7dbd rewrite repository documentation as professional research documentation
880c107 fix: strip trailing :port in domain normalization (asiaone.com:443 bug found via contrast-audit QA)
e88174d update status: contrast collection complete, both manual-labeling tasks tracked separately
cd47959 complete 22-entity contrast-week audit collection
cb65297 enforce peak-week analytical sampling guardrail
9a5ba50 regenerate project report; add v2 contrast-week audit lane
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
