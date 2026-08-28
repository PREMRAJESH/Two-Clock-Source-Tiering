# Source Tiering / Weighting Analysis — Research Repository

Research repository for a co-authored analytical contribution to:

> **The Two-Clock Model: Structural Presence and AI Perception of
> Technology Entities** (Mohan Das, 2026).

This repository holds the evidence, methodological decisions, computational
procedures, and derived outputs for one specific contribution: testing
whether weighting third-party news citations by **source authority**
changes the paper's observed citation-to-perception precedence result. It is
organised as a **research evidence archive** — frozen inputs, archived raw
evidence, a decision log, and reproducible analysis procedures — rather than
as a software project.

---

## Research Context

The paper introduces the *Two-Clock Model*, in which an entity's
establish-ness is represented by two clocks that move at different speeds:

- **S(t)** — structural web presence (archived homepage structure);
- **P(t)** — AI perception (what dated model snapshots know/say about the
  entity);
- **C(t)** — third-party news citations (weekly GDELT news-mention counts).

The *perception gap* G(t) = S(t) − P(t) is predicted to close as citations
C(t) accumulate. The paper's baseline finding is that **citation ramps
precede perception onsets in 28 of 33 testable entities (85%)**, with a
median lead of **83 days** (two-sided exact sign test, p = 6.6 × 10⁻⁵).
This repository reproduces that result exactly from the frozen deposit and
then extends the analysis.

## Research Question

The specific question addressed here is:

> Does replacing raw citation counts C(t) with **source-authority-weighted**
> counts C_weighted(t) strengthen, weaken, or leave unchanged the observed
> precedence of citation ramp over perception onset?

This is a **distinct contribution** from the baseline paper. The paper
reports the raw-count precedence result; this repository tests whether
source authority carries additional signal beyond citation volume. A null
result (weighting does not change the precedence relationship) is an
acceptable, reportable finding.

## Analytical Object

What is being analysed:

- **Citation evidence** — weekly news-mention series per entity
  (`inputs_frozen/ct_results_v1_frozen.csv`), the raw C(t).
- **Source/domain information** — article-level domains from GDELT
  ArtList-mode pulls (two collection lanes, below).
- **Source authority / tiering** — an evidence-based mapping of observed
  news domains into authority tiers.
- **Weighted citation measures** — C(t) recomputed with tier-based weights.
- **Precedence** — the Section 4.6 sign test: does the weighted citation
  ramp still precede perception onset?
- **Sensitivity** — a Table-2-mirror grid probing how the precedence result
  responds to ramp/onset thresholds, count type, and weight choices.

## Research Design

The analytical design is a single chain from raw evidence to result:

```
raw citation counts C(t)   (frozen deposit)
        ↓
source evidence            (article-level domains, peak_week, both lanes)
        ↓
source-tier construction   (empirical frequency clustering of domains)
        ↓
weighted citation counts   C_weighted(t)
        ↓
precedence analysis        (Section 4.6 sign test, raw vs weighted vs tier subsets)
        ↓
sensitivity analysis       (Table-2-mirror grid)
```

Each transformation is implemented by a committed computational procedure
(`scripts/`), each intermediate result lands in `data_derived/`, and each
methodological choice is recorded in `docs/session_log.md`. The chain is
designed so that every derived number can be traced back to a documented
decision and a frozen input.

## Evidence Architecture

The repository distinguishes five kinds of material by their **research
role**, not by their file type:

| Layer | Location | Research role |
|---|---|---|
| **Frozen inputs** | `inputs_frozen/` | Original evidence/data deposits that must remain unchanged. |
| **Reference evidence** | `reference/` | Archived material retained for provenance and audit (raw GDELT responses). |
| **Derived data** | `data_derived/` | Computationally generated analytical outputs. |
| **Research documentation** | `docs/` | Methodological decisions and research-state records. |
| **Computational procedures** | `scripts/` | The procedures that reproduce transformations and analyses. |

Each layer has its own README ([`inputs_frozen/`](inputs_frozen/README.md),
[`reference/`](reference/README.md), [`data_derived/`](data_derived/README.md),
[`docs/`](docs/README.md), [`scripts/`](scripts/README.md)). The
distinction between *frozen evidence*, *reference evidence*, and *derived
output* is deliberately strict: it is what lets a reviewer trust that the
derived numbers were not produced by silently edited inputs.

## Sampling and Collection

The repository operates **two collection lanes with different purposes**,
and the distinction is central to the methodology:

**Analytical lane — `peak_week` (the analytical sample).**
The source-tiering evidence is the single highest-mention week per entity
(`peak_week`), consistent between both lanes and matching the lead author's
confirmed method. This is the only data that enters the tier map and the
weighted analysis.

**Audit lane — `contrast_week` (precision/query audit, 22 entities only).**
For the 22 collision-prone entities, a second, deterministically chosen week
(`contrast_week`, v2) is collected purely to audit **query precision** —
whether the entity's GDELT query returns on-topic articles. Its output
(`data_derived/ct_artlist_contrast.csv`) is **audit/validation data**, not
analytical data.

> **`contrast_week` is NOT an analytical sample.** It is never merged into
> the tier map or the weighted counts. This is enforced by a guardrail in
> `scripts/merge_source_data.py` (non-`peak_week` rows are excluded from
> the analytical sample) and documented as the collection-lane methodology
> decision in [`docs/session_log.md`](docs/session_log.md) (2026-08-18).

Two collection procedures are involved:

- **Viveka's lane (22 overridden entities):** `scripts/ct_artlist_audit.py`
  generates the 22 GDELT ArtList URLs and ingests the saved JSON responses.
  The raw JSONs are archived in
  [`reference/contrast_collection_2026-08-18/`](reference/contrast_collection_2026-08-18/README.md).
- **Our lane (28 remaining entities):** `scripts/ct_source_harvester.py`
  (peak-week, GDELT ArtList mode). **Not yet run against live GDELT.**

## Reproducibility and Provenance

The repository's reproducibility rests on **scientific traceability**, not
software-engineering conveniences:

- **Frozen inputs.** `inputs_frozen/` is immutable; the deposit's version
  and provenance are recorded in its README. Nothing is regenerated into it.
- **Preserved raw evidence.** GDELT responses collected for the audit lane
  are archived byte-for-byte in `reference/`.
- **Documented methodological decisions.** Every decision — including the
  exclusion rule, the `contrast_week` method, and the lane-sampling
  decision — is dated and justified in [`docs/session_log.md`](docs/session_log.md).
- **Deterministic procedures where applicable.** The v2 `contrast_week`
  selection is seeded on entity name + a fixed version tag, so re-runs
  reproduce the same pick. Pipeline procedures are deterministic on fixed
  inputs.
- **Version-controlled changes.** Commits are made at methodological
  milestones with descriptive messages; the history is part of the
  provenance record.
- **Baseline lock.** `scripts/reproduce_baseline.py` asserts the paper's
  exact baseline numbers and fails if any deviate, so the reference point
  for the weighting comparison is itself verified.

## Research Status

Statuses below are supported by the repository on disk and in the session
log; nothing is claimed that the repository does not show.

| Status | Item |
|---|---|
| **CONFIRMED** | Paper baseline reproduction: 28/33 ramp-precedes-onset, median lead 83 days, p = 6.6 × 10⁻⁵, verified under both ramp floors (3 and 5) by `scripts/reproduce_baseline.py`. |
| **IMPLEMENTED** | Weighting pipeline (Tasks 1–6: merge → tier map → weights → precedence → sensitivity → smoke test). Structurally complete and smoke-tested; **not yet run on real source data**. |
| **COMPLETE** | 22-entity `contrast_week` audit collection: 22/22 entities, 263 article rows, raw JSONs archived and committed (`cd47959`). **Triage complete: 263/263 labeled, 78y/185n** (committed `886019f`). |
| **AUDIT / VALIDATION** | Domain-normalization fix (`:port` stripping, e.g. `asiaone.com:443` → `asiaone.com`) verified against both call sites in `merge_source_data.py`. |
| **PENDING** | Weighting pipeline execution on real source data; 28-entity peak-week harvest (`ct_source_harvester.py`); tier-methodology fill-in. |
| **COMPLETE (manual)** | 27 AMBER precision-audit rows: extracted to `amber_rows_review.csv`, labeled 16y/5n/6 unverifiable (committed `3b50d5b`). |

See [`docs/project_overview_report.md`](docs/project_overview_report.md)
for the consolidated status with detail, and [`docs/session_log.md`](docs/session_log.md)
for the decision trail.

## Repository Map

| Location | Research role |
|---|---|
| [`inputs_frozen/`](inputs_frozen/README.md) | **Frozen source evidence** — the v1 deposit (citation, perception, structure series; entity roster; original harvesters) plus received labeled inputs. Immutable. |
| [`reference/`](reference/README.md) | **Archived / reference evidence** — sample GDELT response and the archived 22-file contrast-week collection. |
| [`data_derived/`](data_derived/README.md) | **Derived analytical outputs** — regenerable CSVs; milestone snapshots tracked deliberately. |
| [`docs/`](docs/README.md) | **Research decisions and methodology** — decision log, state report, tier-methodology spec. |
| [`scripts/`](scripts/README.md) | **Computational procedures** — the operationalized research methods. |
| `LICENSE-CODE.md`, `LICENSE-DATA.md` | Licensing for code and data respectively. |

## Reproduction

Minimum instructions for another researcher to reproduce the work. The
project-local interpreter is `.venv\Scripts\python.exe` (Windows); the
analytical pipeline is standard-library-only and runs offline.

1. **Baseline reproduction** (frozen inputs only, no derived data needed):

   ```
   .venv\Scripts\python.exe scripts/reproduce_baseline.py
   ```

2. **Weighting pipeline** (requires source evidence to exist; currently
   awaiting the collection lanes):

   ```
   .venv\Scripts\python.exe scripts/merge_source_data.py
   .venv\Scripts\python.exe scripts/build_tier_map.py
   .venv\Scripts\python.exe scripts/apply_weights.py
   .venv\Scripts\python.exe scripts/precedence_test_weighted.py
   .venv\Scripts\python.exe scripts/sensitivity_analysis.py
   ```

3. **Audit-lane ingest** (offline; run from `scripts/` with the archived
   JSONs in the working directory):

   ```
   .venv\Scripts\python.exe scripts/ct_artlist_audit.py --contrast
   ```

4. **Pipeline smoke test** (offline, isolated synthetic run):

   ```
   .venv\Scripts\python.exe scripts/test_pipeline_smoketest.py
   ```

Full procedural detail, including inputs/outputs of each procedure, is in
[`scripts/README.md`](scripts/README.md). Procedures that require network
access (`ct_source_harvester.py`, `ct_artlist_harvester.py`) are marked as
such there.

## Research Limitations

Actual limitations and unresolved methodological questions recorded in the
repository:

- **The weighted result does not yet exist.** `data_derived/precedence_comparison.csv`
  and `data_derived/sensitivity_results.csv` are **raw-fallback** outputs
  from 2026-08-17, produced before any weighted source evidence existed;
  their weighted/tier columns are empty. They are not final weighted
  results.
- **Two manual labeling tasks completed:** the 27 AMBER precision rows
  (16y/5n/6 unverifiable) and the 263-row contrast-week batch (78y/185n).
  Sign-off on the AMBER-batch reconciliation (CSV-vs-master export bug,
  5 Kimi y->n overrides) is still pending with Viveka.
- **`other_week` rule retired as unrecoverable.** The original second-week
  rule could not be reconstructed; the deterministic v2 `contrast_week`
  replaced it (documented 2026-08-18). The stale `scripts/verify_week_match.py`
  should not be run.
- **Syndication / domain dilution.** Domain-level tiering counts
  republished wire stories per hosting domain; observed instances are
  documented in [`docs/tier_methodology.md`](docs/tier_methodology.md)
  (e.g. one Threads story captured 6× across NBC affiliates).
- **Tier methodology is a draft/template.** [`docs/tier_methodology.md`](docs/tier_methodology.md)
  is intentionally unfilled until real domain data exists; tier boundaries
  are not pre-assigned from assumption.
- **P(t) is a single-run pilot** (per the deposit's own README); two
  perception reruns are time-constrained by the **Oct 23, 2026** retirement
  of `gpt-4-0613` and `gpt-4o-2024-05-13`.

## Citation / Related Research

> Mohan Das, V. (2026). *The Two-Clock Model: Structural Presence and AI
> Perception of Technology Entities* [Dataset]. Zenodo.
> https://doi.org/10.5281/zenodo.21532575

The frozen deposit's full provenance and author declarations are recorded
in [`inputs_frozen/README.md`](inputs_frozen/README.md).

## Data and Code Licensing

- **Code:** MIT — [`LICENSE-CODE.md`](LICENSE-CODE.md).
- **Data:** CC-BY-4.0 — [`LICENSE-DATA.md`](LICENSE-DATA.md); derived data
  inherits attribution to the frozen deposit (DOI 10.5281/zenodo.21532575).