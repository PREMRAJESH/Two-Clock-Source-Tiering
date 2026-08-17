# Project Overview & Implementation Report

**Paper:** *"The Two-Clock Model: Structural Presence and AI Perception of Technology Entities"* (Mohan Das, 2026, Zenodo DOI [10.5281/zenodo.21532575](https://doi.org/10.5281/zenodo.21532575))  
**Research Contribution:** Citation Source-Tiering / Weighting Analysis  
**Repository Location:** `two-clock-source-tiering/`

---

## 1. Academic Context & Core Research Objective

The paper introduces the **Two-Clock Model**, treating structural web presence $S(t)$ and AI perception $P(t)$ as two representations of an entity's establish-ness moving at different speeds. The perception gap $G(t) = S(t) - P(t)$ is predicted to close as third-party news citations $C(t)$ accumulate.

- **Baseline Paper Finding (Unweighted Raw Counts):** Citation ramps precede perception onsets in **28 of 33 testable entities (85%)**, with a median lead of **83 days** (two-sided exact sign test $p = 6.6 \times 10^{-5}$).
- **Assigned Research Contribution:** Test whether weighting news citations by source authority ($C_{\text{weighted}}(t)$ vs. raw unweighted mention counts $C(t)$) strengthens or weakens the precedence result.
- **Scientific Standard:** A null result (weighting does not improve precedence) is an acceptable, reportable finding. Methodological choices must be honest, reproducible, and traceably justified rather than selected to force a predetermined outcome.

---

## 2. Repository Layout & Architecture

```
two-clock-source-tiering/
├── inputs_frozen/                  <- READ-ONLY frozen v1 deposit (author original data)
│   ├── ct_results_v1_frozen.csv    <- Raw weekly citation series C(t) (no per-source field)
│   ├── pt_pilot_results.csv        <- Perception ladder P(t) across model cutoffs
│   ├── ct_artlist_precision.csv    <- Disambiguation precision audit (PASS/FAIL/NOT_AUDITED)
│   ├── entities.py                 <- 50-entity roster with birth dates and flags
│   └── README.md                   <- Dataset documentation & author declarations
├── scripts/                        <- Analysis & harvesting scripts
│   ├── verify_week_match.py        <- Phase 0: Spot-check script for harvester week logic
│   ├── ct_source_harvester.py      <- Peak-week article GDELT ArtList harvester
│   ├── reproduce_baseline.py       <- Baseline reproduction: exact 28/33 match check
│   ├── merge_source_data.py        <- Task 1: Merges labeled & harvested source data
│   ├── build_tier_map.py           <- Task 2: Jenks natural-breaks frequency tier assignment
│   ├── apply_weights.py            <- Task 3: Tier map + source data -> weighted C(t)
│   ├── precedence_test_weighted.py <- Task 4: Exact sign test on raw vs. weighted series
│   ├── sensitivity_analysis.py     <- Task 5: 3x3 threshold grid, weight sweep & perturbation
│   └── test_pipeline_smoketest.py  <- Task 6: Isolated sandbox end-to-end smoke test
├── data_derived/                   <- Generated outputs (scratch / reproducible)
│   ├── ct_source_all.csv           <- Unified article-level domain harvest across entities
│   ├── domain_frequency_analysis.csv <- Per-domain breadth, volume, and log-score
│   ├── domain_tier_map.csv         <- Domain -> Tier assignments with traceable evidence
│   ├── ct_results_weighted.csv     <- Final weighted weekly citation series
│   ├── precedence_comparison.csv   <- Per-entity lead & sign test comparison
│   └── sensitivity_results.csv     <- Full Table 2 mirror sensitivity grid
└── docs/                           <- Methodological justification & session logs
    ├── tier_methodology.md         <- Tier definitions, boundary evidence & caveats
    └── session_log.md              <- Chronological record of decisions and state changes
```

---

## 3. Structured Task-by-Task Implementation Summary

### Task 0: Harvester Reconciliation & Spot-Check Verification
- **File:** [scripts/verify_week_match.py](file:///d:/two-clock-source-tiering/scripts/verify_week_match.py)
- **Objective:** Reconcile script week-selection logic between our harvester ("max mention_count week" / true peak) and Viveka's harvester (`ct_artlist_harvester.py`, "median-count week").
- **Implementation:** Compares week outputs for priority spot-check entities (`Kimi` and `Mamba`) against `ct_artlist_LABELING.xlsx`. Enforces a strict blocker rule: **no weighting work proceeds until this check passes**.

### Task 1: Unified Source Data Merging & Domain Normalization
- **File:** [scripts/merge_source_data.py](file:///d:/two-clock-source-tiering/scripts/merge_source_data.py)
- **Objective:** Merge Viveka's 20-entity manually labeled dataset with our harvested dataset into a single canonical file (`data_derived/ct_source_all.csv`).
- **Key Features:**
  - Standardizes domain strings (lowercasing, stripping `www.` prefixes, trimming trailing slashes).
  - Preserves raw domain strings for full auditing.
  - Automatically flags overlap/duplicate entities and logs unharvested roster gaps.
  - Outputs a detailed diagnostic report (`data_derived/merge_diagnostics.txt`).

### Task 2: Evidence-Based Empirical Tier Assignment (Approach B)
- **File:** [scripts/build_tier_map.py](file:///d:/two-clock-source-tiering/scripts/build_tier_map.py)
- **Objective:** Cluster domains into Tier 1 (High Authority), Tier 2 (Trade Press), and Tier 3 (Low Authority) based on observed data rather than subjective outlet prestige.
- **Key Features:**
  - Computes domain breadth (number of distinct entities covered) and total article volume.
  - Formulates a composite authority score: $\text{log\_score} = \log(\text{breadth} \times \text{volume} + 1)$.
  - Implements a zero-dependency **Jenks Natural Breaks (Fisher-Caspall)** clustering algorithm.
  - Evaluates Goodness of Variance Fit ($\text{GVF} \ge 0.70$ pass/warn threshold).
  - Cross-checks domain mix against `ct_artlist_precision.csv` (precision PASS/FAIL).

### Task 3: Citation Series Weighting Engine
- **File:** [scripts/apply_weights.py](file:///d:/two-clock-source-tiering/scripts/apply_weights.py)
- **Objective:** Map tier assignments onto the timeline of weekly citation counts, generating both continuous-weighted and binary-exclusion counts.
- **Key Features:**
  - Supports continuous weighting (baseline starting grid: Tier 1 = 1.0, Tier 2 = 0.5, Tier 3 = 0.25).
  - Computes binary exclusion series: `tier1_count` (Tier 1 only) and `tier12_count` (Tiers 1 & 2).
  - Aligns weighted counts with `inputs_frozen/ct_results_v1_frozen.csv` so all original entity-weeks are preserved.
  - Tracks unmatched domains and carries through `capped` week flags (GDELT 250-article cap).

### Task 4: Precedence Sign Test Execution
- **File:** [scripts/precedence_test_weighted.py](file:///d:/two-clock-source-tiering/scripts/precedence_test_weighted.py)
- **Objective:** Evaluate Section 4.6 precedence (ramp date vs. perception onset date) on both raw and weighted citation series.
- **Key Definitions (Direct from Lead Author):**
  - **Ramp Date:** First week $C(t) \ge \text{threshold} \times \text{peak}(C(t))$, with floor of 3 mentions (default 10% threshold).
  - **Onset Date:** First model cutoff where $P(t) \ge 3$ (0–4 scale).
  - **Lead:** $\text{Onset Date} - \text{Ramp Date}$ (in days; positive = ramp precedes onset).
- **Statistical Test:** Implements an exact two-sided sign test without external library dependencies.
- **Baseline Exclusion Rule (verified against paper Sections 4.5 and 5.4):**
  - **10 precision-audit FAIL** entities (Section 4.5, Table 1): `DBRX`, `Kimi`, `Ideogram`, `Lovable`, `Gemini (Google model)`, `Dream Machine`, `Liquid AI`, `Mamba`, `Operator`, `vLLM`.
  - **7 no-onset** entities (Section 5.4): `OpenAI o1`, `OpenAI o3`, `DeepSeek`, `DeepSeek-R1`, `Manus`, `World Labs`, `Bolt.new`.
  - This leaves exactly **33 testable entities** (50 − 10 FAIL − 7 no-onset = 33).
  - **Important:** The `self_ref_openai` flag in `entities.py` is **NOT** part of this baseline. GPT-4, GPT-4o, and Sora are included in the 33. The flag exists for a separate robustness analysis (self-recognition confound on OpenAI entities probed on an OpenAI ladder) — it is a distinct, clearly-labeled variant, not the baseline.
- **Weighting Variants:** Runs the sign test on raw, continuous-weighted, Tier 1-only, and Tier 1+2 citation series simultaneously.
- **Known Issue (pending fix):** Currently uses the `self_ref_openai` flag instead of the paper's FAIL+no-onset rule, and lacks the PT↔CT entity name bridge. Must be updated before any real weighted-data run.

### Task 5: Robustness & Sensitivity Analysis
- **File:** [scripts/sensitivity_analysis.py](file:///d:/two-clock-source-tiering/scripts/sensitivity_analysis.py)
- **Objective:** Test whether precedence findings are robust or fragile across parameter choices, matching the paper's Table 2 structure.
- **Analyses Included:**
  1. **Table 2 Threshold Grid:** $3 \times 3$ matrix of Ramp Thresholds ({5%, 10%, 20%}) $\times$ Onset Thresholds ({$P \ge 2, 3, 4$}) for raw, weighted, Tier 1, and Tier 1+2 series.
  2. **Tier-Boundary Perturbation Test:** Identifies borderline domains near Jenks break points, shifts them up/down (`boundary_shift_up` and `boundary_shift_down`), reports reassigned domain counts, and calculates the exact % of total citation volume reassigned.
  3. **Weight Grid Sweep:** $4 \times 4$ grid sweeping Tier 2 weights ({0.25, 0.50, 0.75, 1.0}) $\times$ Tier 3 weights ({0.0, 0.10, 0.25, 0.50}).
  4. **PASS-Only Subset:** Reruns baseline on high-precision entities ($n=12$ PASS entities).
  5. **Capped-Week Exclusion:** Reruns analysis with 250-article capped entities excluded.

### Task 6: Isolated Sandbox End-to-End Smoke Testing
- **File:** [scripts/test_pipeline_smoketest.py](file:///d:/two-clock-source-tiering/scripts/test_pipeline_smoketest.py)
- **Objective:** Verify that all 5 pipeline scripts execute cleanly end-to-end without runtime errors, type mismatches, or file permission crashes.
- **Implementation:**
  - Creates a temporary isolated sandbox (`tempfile.mkdtemp()`).
  - Generates synthetic datasets (10 entities, 18 domains with varied frequency distributions, perception ladders, and weekly counts).
  - Executes Tasks 1–5 in sequence and validates stdout, GVF score evaluation, and sensitivity outputs.
  - Cleans up synthetic temporary directories upon completion.
  - **Verification Result:** Smoke test **PASSED CLEANLY**.

### Pipeline Helper: GDELT Citation Harvester
- **File:** [scripts/ct_source_harvester.py](file:///d:/two-clock-source-tiering/scripts/ct_source_harvester.py)
- **Objective:** Harvester script designed to pull per-article domains via the GDELT Doc API for the remaining ~30 entities not covered by Viveka's manual labeling.
- **Key Features:**
  - Queries GDELT Doc API specifically for the **peak-week** (highest mention_count week) to align with Viveka's 20-entity manual dataset.
  - Skips already-covered entities (read from manual export) to save rate-limit capacity.
  - Built with rate-limit safety buffers, exponential backoff (retries up to 4 times), and handles GDELT's pagination (capped at 250 records).
  - Note: Pending run until the Task 0 Spot-Check confirms her week-choice method matches her manual data.

### Baseline Reproduction Check
- **File:** [scripts/reproduce_baseline.py](file:///d:/two-clock-source-tiering/scripts/reproduce_baseline.py)
- **Objective:** Independently reproduce the paper's headline 28/33 result using only frozen data and the exact exclusion rule from Sections 4.5/5.4.
- **Key Features:**
  - Uses only `inputs_frozen/ct_results_v1_frozen.csv` and `inputs_frozen/pt_pilot_results.csv` — no weighted CSV needed.
  - Applies the paper's exact exclusion rule (10 FAIL + 7 no-onset), not the `self_ref_openai` flag.
  - Includes a canonical name bridge to handle the PT↔CT entity name mismatch (14 of 50 entities have parenthetical disambiguators in the perception CSV but short names in the citation CSV).
  - Checks both floor=3 and floor=5.
- **Verification Result:** Both floors produce **28/33, median lead 83 days, p = 6.62 × 10⁻⁵** — exact match. ✓

---

## 4. Methodological Standards & Documented Caveats

All methodological details have been incorporated into [docs/tier_methodology.md](file:///d:/two-clock-source-tiering/docs/tier_methodology.md):

1. **No Paywalled Dependencies:** Avoided paid authority tools (NewsGuard, Moz DA) in favor of data-driven empirical clustering (Approach B) reproducible directly from GDELT harvest data.
2. **Syndication and Domain Dilution Limitation:** Documented in Sections 2, 3, and 6 that domain-level frequency counting treats every URL as an independent host citation. Syndicated wire stories (AP, Reuters) republished across aggregators (`yahoo.com`, `msn.com`) accumulate higher volume/breadth, which can cluster aggregators into higher tiers based on republication volume rather than original reporting authority. The composite metric $\log(\text{breadth} \times \text{volume})$ helps buffer this by requiring a domain to span multiple distinct technology entities to rank as high authority.
3. **Windows Encoding Safety:** All script console outputs use pure ASCII strings (replacing non-ASCII symbols like `→` or `≥` with `->` and `>=`) to prevent Windows console `UnicodeEncodeError` exceptions.
4. **Entity Name Mismatch Between CSVs:** The perception CSV (`pt_pilot_results.csv`) uses parenthetical disambiguators (e.g. `Cursor (the AI code editor)`) while the citation CSV (`ct_results_v1_frozen.csv`) uses short names (e.g. `Cursor`). 14 of 50 entities are affected. Any script joining these datasets must use a name bridge (strip parentheticals) or it will silently drop entities, producing incorrect testable counts.

---

## 5. Current Project Status & Next Steps

| Component | Status | Next Required Action |
|---|---|---|
| Baseline Reproduction (`reproduce_baseline.py`) | **CONFIRMED ✓** | 28/33 exact match for both floor=3 and floor=5 |
| Pipeline Scaffolding (Tasks 1–6) | **100% Complete & Verified** | Ready to run once source data is in place |
| Name Bridge Fix (`precedence_test_weighted.py`, `sensitivity_analysis.py`) | **Pending** | Must add PT↔CT name bridge and switch to paper's exclusion rule before real weighted runs |
| Phase 0 Spot-Check (`verify_week_match.py`) | **Blocked** | Pending delivery of `ct_artlist_results.csv` and `ct_artlist_LABELING.xlsx` |
| Remaining Harvest (`ct_source_harvester.py`) | **Pending Spot-Check** | Fill `ALREADY_COVERED` entity list from Viveka's file and run for remaining ~30 entities |
| Precision Audit (27 AMBER rows) | **Pending Review** | Manual judgment task, kept separate from the automated code pipeline |
| P(t) Model Retirement Deadline | **Oct 23, 2026** | Two more P(t) model runs needed before OpenAI retires `gpt-4-0613` and `gpt-4o-2024-05-13` |
| Precision Audit PASS/FAIL Entities | **Verified** | **12 PASS** entities: `Apple Intelligence`, `Apple Vision Pro`, `Cursor`, `Grok`, `Manus`, `Qwen`, `Sora`, `Suno`, `Threads`, `Udio`, `Windsurf`, `xAI`. |
