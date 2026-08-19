# Derived Analytical Outputs

This directory holds the **computationally generated outputs** of the
analysis — the intermediate and final numbers produced by applying the
documented procedures (`../scripts/`) to the frozen evidence
(`../inputs_frozen/`).

**These files are NOT primary evidence.** They are derived from the frozen
inputs and are regenerable: the procedure that produced each file is
committed, so a re-run reproduces it. The authoritative evidence base is
the frozen deposit; the derived files are its analytical transformation.

---

## Primary evidence vs. derived output

| | Frozen evidence (`../inputs_frozen/`) | Derived output (`data_derived/`) |
|---|---|---|
| Nature | Original evidence/data deposits | Analytical transformations of that evidence |
| Regenerable | No (immutable) | Yes (by committed procedures) |
| Source of truth | The deposit (externally versioned) | The producing procedure + its inputs |
| Edited | Never in place | Only by re-running the producing procedure |

## Inventory

| File | Derived quantity / analysis | Input basis | Research role | Status |
|---|---|---|---|---|
| `ct_artlist_contrast.csv` | **v2 contrast-week precision-audit batch** — 263 article rows, all 22 audit entities, columns `entity, query, sample_window, seendate, title, domain, url, relevant`. | Archived raw GDELT JSONs (`../reference/contrast_collection_2026-08-18/`), ingested by `ct_artlist_audit.py --contrast`. | **Audit/validation data** — the query-precision sample, **not** analytical evidence. `relevant` is empty awaiting manual labeling. | Tracked milestone (`cd47959`) |
| `precedence_comparison.csv` | **Precedence comparison per entity** — raw / weighted / Tier-1 / Tier-1+2 ramp dates, leads, and signs, plus `excluded_reason`. Columns: `entity, birth_date, ramp_raw_week, ramp_raw_count, ramp_weighted_week, ramp_weighted_count, ramp_tier1_week, ramp_tier12_week, onset_cutoff, onset_score, lead_raw_days, lead_weighted_days, lead_tier1_days, lead_tier12_days, sign_raw, sign_weighted, sign_tier1, sign_tier12, excluded_reason`. | `precedence_test_weighted.py` on frozen series (raw-fallback run). | **Statistical output** — currently a raw-only placeholder (see below). | Tracked milestone (`9e24bc3`) |
| `sensitivity_results.csv` | **Table-2-mirror sensitivity grid** — rows `variant, ramp_threshold, onset_threshold, count_type, weight_t1, weight_t2, weight_t3, n_precedes, n_testable, n_ties, median_lead_days, p_value`. | `sensitivity_analysis.py` on frozen series (raw-fallback run). | **Sensitivity output** — currently a raw-only placeholder (see below). | Tracked milestone (`9e24bc3`) |
| `.placeholder.md` | Directory placeholder (empty-directory marker). | — | — | Tracked (first commit) |

## Current status of the result files

**Important:** the two result CSVs were generated on the **raw-fallback
path** (2026-08-17), **before any weighted source evidence existed**:

- `precedence_comparison.csv` has `sign_raw` and the raw ramp/lead columns
  populated; the **weighted, tier1, and tier12 columns are empty**.
- `sensitivity_results.csv`'s weighted rows are present but have
  `n_testable = 0`.

They therefore validate the **raw baseline and the pipeline mechanics
only**. They are **not final weighted results.** The true weighted analysis
will re-run these procedures once the source-collection lanes
(`ct_source_harvester.py`, and the Lane A labeling) supply real
source/domain evidence.

The raw numbers they do contain match the paper baseline (28/33,
83 days, 6.6 × 10⁻⁵; p = 6.618769839406013e-05 in the sensitivity grid).

## Tracking policy

`data_derived/*` is **gitignored by default** (see `../.gitignore`),
because the outputs are regenerable and not source-of-truth data.
**Milestone snapshots** — specific outputs that back a stated result — are
committed deliberately with `git add -f`, tied to the commit that produced
them. The policy is recorded in `../docs/session_log.md` (2026-08-18).

- **Ignored (regenerable):** `ct_source_results.csv`, `ct_source_all.csv`,
  `merge_diagnostics.txt`, `domain_frequency_analysis.csv`,
  `domain_tier_map.csv`, `tier_cross_check.txt`, `ct_results_weighted.csv`,
  and any other run-time output.
- **Tracked milestones:** the three files in the inventory above.

A file should be committed here only when it is a deliberate milestone
backing a stated result — not on every re-run.

## Audit / provenance note

`ct_artlist_contrast.csv` is the derived form of the **archived raw
evidence** in `../reference/contrast_collection_2026-08-18/`. Its
`sample_window` is `contrast_week` for every row. Per the lane-sampling
decision, it is **audit data, never analytical data**: no pipeline
procedure reads it into the tier map or weighted counts. Its `relevant`
column awaits manual y/n labeling before query precision can be scored.

## Regenerating

Re-running the pipeline procedures recreates the outputs from the frozen
inputs (commands in `../scripts/README.md`). The contrast batch is
regenerated by the offline ingest (`ct_artlist_audit.py --contrast` run
from `scripts/`, with the archived JSONs in the working directory).

## Licensing

Derived data inherits the frozen deposit's attribution requirement
(CC-BY-4.0; `../LICENSE-DATA.md`).