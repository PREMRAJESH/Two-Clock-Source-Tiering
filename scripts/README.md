# Computational Procedures

This directory contains the **computational procedures** that operationalize
the documented research methods. Each procedure is the executable form of a
methodological decision recorded in `../docs/session_log.md`; the decision
log is the authority for *why* a procedure does what it does, and each
procedure's docstring declares its exact inputs and outputs.

These are research procedures, not software features. They are organized
below by their **methodological role** in the analysis.

---

## Roles overview

| Procedure | Research purpose | Principal input | Principal output | Analytical role |
|---|---|---|---|---|
| `reproduce_baseline.py` | Verify the paper's raw-count precedence baseline against the frozen deposit | `../inputs_frozen/ct_results_v1_frozen.csv`, `../inputs_frozen/pt_pilot_results.csv` | stdout report (no files) | **Baseline verification** — locks the reference point the weighting comparison must beat |
| `ct_artlist_audit.py` | Audit query precision for the 22 collision-prone entities (v2 `contrast_week`); ingest archived GDELT JSONs | `../inputs_frozen/ct_harvester.py`, `../inputs_frozen/ct_results_v1_frozen.csv` | CWD-relative `ct_artlist_contrast.csv` (v2) or `ct_artlist_audit.csv` (v1) | **Audit / validation** — produces *audit* data, never analytical data |
| `ct_source_harvester.py` | Collect article-level GDELT evidence (peak week) for the 28 entities not covered by Lane A | `../inputs_frozen/ct_results_v1_frozen.csv`, `../inputs_frozen/ct_harvester.py` | `../data_derived/ct_source_results.csv` | **Evidence collection (analytical lane)** — network; not yet run |
| `ct_artlist_harvester.py` | Lead author's article-level harvester (peak + a guessed second week) | `ct_harvester.py` (same folder) | CSV files | **Superseded** — its second-week rule is retired (see below) |
| `verify_week_match.py` | Old week-consistency spot-check | `../data_derived/ct_artlist_results.csv` (does not exist), `../inputs_frozen/ct_artlist_LABELING.xlsx` | stdout report | **Superseded / stale** — do not run |
| `merge_source_data.py` | Combine collected source evidence into the analytical source file | `../inputs_frozen/entities.py`, optional `../data_derived/viveka_labeled_export.csv`, `../data_derived/ct_source_results.csv` | `../data_derived/ct_source_all.csv`, `../data_derived/merge_diagnostics.txt` | **Data preparation** — enforces the peak-week analytical sampling |
| `build_tier_map.py` | Construct the evidence-based domain → tier mapping | `../data_derived/ct_source_all.csv`, `../inputs_frozen/ct_artlist_precision.csv` | `../data_derived/domain_frequency_analysis.csv`, `../data_derived/domain_tier_map.csv`, `../data_derived/tier_cross_check.txt` | **Source-tier construction** |
| `apply_weights.py` | Apply tier weights to weekly citation counts | `../data_derived/ct_source_all.csv`, `../data_derived/domain_tier_map.csv`, `../inputs_frozen/ct_results_v1_frozen.csv` | `../data_derived/ct_results_weighted.csv` | **Citation weighting** |
| `precedence_test_weighted.py` | Rerun the Section 4.6 precedence test on weighted and tier-subset series | `../data_derived/ct_results_weighted.csv`, `../inputs_frozen/pt_pilot_results.csv`, `../inputs_frozen/entities.py` | `../data_derived/precedence_comparison.csv` | **Statistical / precedence analysis** |
| `sensitivity_analysis.py` | Table-2-mirror sensitivity grid over thresholds, count types, and weights | `../data_derived/ct_results_weighted.csv`, `../data_derived/ct_source_all.csv`, `../data_derived/domain_tier_map.csv`, `../data_derived/domain_frequency_analysis.csv`, `../inputs_frozen/pt_pilot_results.csv`, `../inputs_frozen/entities.py`, `../inputs_frozen/ct_artlist_precision.csv` | `../data_derived/sensitivity_results.csv` | **Sensitivity analysis** |
| `test_pipeline_smoketest.py` | End-to-end execution check of the pipeline on synthetic data in an isolated sandbox | none (self-contained) | none (cleaned up) | **Validation** — pipeline mechanics only, not statistical correctness |

---

## Baseline reproduction

### `reproduce_baseline.py`

Reproduces the paper's Section 4.5 + 5.4 precedence result directly from
frozen inputs and **asserts** the exact baseline: 28/33 ramp-precedes-onset,
median lead 83 days, two-sided exact sign test p = 6.6 × 10⁻⁵, verified
under both ramp floors (3 and 5). Uses the paper's exact exclusion rule
(10 precision-FAIL + 7 no-onset entities) and the entity-name bridge; the
`self_ref_openai` flag is deliberately **not** part of the baseline. Fails
the process if any asserted number deviates. Offline; no outputs written.

## Evidence collection and audit

### `ct_artlist_audit.py` — query-precision audit lane (v2)

Human-assisted audit of GDELT query precision for the **22 collision-prone
entities** whose names are ambiguous (e.g. `Threads`, `Grok`, `Gemini`).
Modes:

- `--contrast-urls`: prints the 22 GDELT ArtList URLs (one per overridden
  entity) to fetch manually.
- `--contrast`: ingests the saved JSON responses from the **current working
  directory** and writes `ct_artlist_contrast.csv` (CWD-relative). Offline;
  no network call at ingest.
- `--urls` / `--peak` (v1): legacy single-week generation (peak week);
  superseded by the v2 flow for the audit.
- `--force`: overrides the existing-output safety check.

The v2 `contrast_week` is a **deterministic** replacement for the retired,
unrecoverable second-week rule: seeded on entity name + a fixed version tag
(`random.seed(20260708)`, minimum 4-week gap from peak), so re-runs
reproduce identical picks. The legacy v1 rule used a random second week and
was never reproducible.

> **Analytical role: audit/validation only.** `contrast_week` is not part
> of the weighted analytical dataset. It is never merged into the tier map
> or weighted counts (enforced by `merge_source_data.py`; decision recorded
> in `../docs/session_log.md`, 2026-08-18).

The archived raw responses it ingests live in
`../reference/contrast_collection_2026-08-18/` (see its README).

### `ct_source_harvester.py` — analytical lane (peak week)

Collects article-level GDELT evidence (ArtList mode) for the 28 entities
not covered by Lane A, for each entity's **peak week** (the single highest
`mention_count` week in the frozen citation series). Peak-week-only by
design, matching the lead author's confirmed method and the lane-sampling
decision. Network; rate-limited; capped at 250 articles per entity.

**Status: not yet run against live GDELT.** Before running, the
`ALREADY_COVERED` set must be filled with the entities already covered by
the 22-entity audit, or it will re-pull them.

### `ct_artlist_harvester.py` — superseded

The lead author's article-level harvester (peak week + a second
`other_week` chosen by a median-count rule). Its second-week rule is
**retired** as unrecoverable (the original pull parameters no longer exist)
and replaced by the deterministic v2 `contrast_week` in
`ct_artlist_audit.py`. Kept for reference; not part of the analytical
pipeline. Network.

### `verify_week_match.py` — superseded / stale

An old spot-check comparing article-list weeks against the labeled Excel.
It references `../data_derived/ct_artlist_results.csv`, which does not
exist, and needs `pandas` + `openpyxl` (not in the project environment).
Its premise — that the old `other_week` was the correct second sample — is
moot because that rule is retired. **Do not run.**

## Data preparation

### `merge_source_data.py`

Combines the collected source evidence (Lane A labeled rows + Lane B
harvester output) into the analytical source file `ct_source_all.csv`,
using `entities.py` for birth dates.

**Guardrail:** rows whose `window` ≠ `peak_week` are excluded from the
analytical sample, with each exclusion logged to `merge_diagnostics.txt`.
This operationalizes the peak-week-only analytical sampling decision: the
`contrast_week`/`other_week` audit rows can never enter the tier map or
weighted counts through this path. Domain normalization strips trailing
`:port` (e.g. `asiaone.com:443` → `asiaone.com`).

## Source-tier construction

### `build_tier_map.py`

Builds the evidence-based domain → tier mapping (Approach B: empirical
frequency clustering via Jenks natural breaks on log(breadth × volume),
Goodness of Variance Fit ≥ 0.70), cross-checked against the precision
audit. Outputs the frequency analysis, the tier map, and a cross-check
report. Tier boundaries are **derived from observed data**, never
pre-assigned from assumption (see `../docs/tier_methodology.md`).

## Citation weighting

### `apply_weights.py`

Applies tier weights to the weekly citation counts, producing
`ct_results_weighted.csv`. Two weighting schemes:

- **continuous** — a domain's mean weekly mentions within its tier;
- **binary** — tier-level weights (Tier 1 = 1.0, Tier 2 = 0.5, Tier 3 =
  0.25).

Weighted series are emitted alongside raw counts for the precedence test.
Inputs are peak-week source data only, per the lane-sampling decision.

## Statistical / precedence analysis

### `precedence_test_weighted.py`

Reruns the Section 4.6 precedence sign test on the weighted series,
mirroring `reproduce_baseline.py` (ramp = first week C(t) reaches 10% of its
peak with a 3–5 floor; onset = first model cutoff with P ≥ 3; same
PAPER_EXCLUDED set). Emits `precedence_comparison.csv` with raw / weighted /
Tier-1 / Tier-1+2 columns per entity, plus `excluded_reason`. Uses the same
entity-name bridge as the baseline so the 14 parenthetically-disambiguated
entities are not silently dropped.

## Sensitivity analysis

### `sensitivity_analysis.py`

Table-2-mirror sensitivity grid over ramp threshold, onset threshold, count
type (raw/weighted), and tier weights; plus tier-boundary perturbation and
a weight sweep. Runs on the PASS-only precision subset and with
capped-week exclusion variants. Emits `sensitivity_results.csv`.

## Validation

### `test_pipeline_smoketest.py`

Offline, self-contained execution check: builds an isolated sandbox, writes
synthetic data (10 entities, 18 domains), runs the Tasks 1–5 procedures
end-to-end, verifies outputs are produced, and cleans up. It validates that
the pipeline executes without runtime errors — **statistical correctness is
the job of `reproduce_baseline.py`**, not this check.

---

## Procedure conventions

- **Read-only inputs.** Procedures read only from `inputs_frozen/` and
  `data_derived/`; none writes into `inputs_frozen/`.
- **Deterministic.** Pipeline and v2-audit procedures are deterministic on
  fixed inputs; re-running reproduces identical outputs.
- **Path handling.** Pipeline procedures locate inputs/outputs via
  `__file__`-relative paths and can be invoked from any working directory.
  `ct_artlist_audit.py` is an exception: it globs JSONs and writes its CSV
  in the **current working directory** (run it from `scripts/`).
- **Offline by default.** Only `ct_source_harvester.py` and
  `ct_artlist_harvester.py` require network access.
- **Environment.** The project-local interpreter is
  `.venv\Scripts\python.exe` (Windows), which contains only `requests` and
  `matplotlib`; the analytical pipeline is standard-library-only and needs
  neither.

## Licensing

Code in this directory is MIT-licensed (`../LICENSE-CODE.md`).