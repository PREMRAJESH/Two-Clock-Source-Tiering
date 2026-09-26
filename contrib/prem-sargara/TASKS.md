# Contributor Workspace & Task Tracking — Prem Sargara

> **Workstream:** Citation Source-Tiering & Weighting Analysis  
> **Repository Scope:** `contrib/prem-sargara/`  
> **Status:** Active (Phase 2 Execution) | **Last Updated:** 2026-09-22

---

## 1. Contributor Metadata & Overview

| Attribute | Specification |
| :--- | :--- |
| **Contributor** | Prem Sargara (`prem-sargara`) |
| **Primary Domain** | Analytical Pipeline, Source-Tier Weighting Engine, GDELT Harvesting & Data Normalization |
| **Core Deliverables** | Analytical Merging Engine, Tier Weighting Methodology (`tier_methodology.md`), Precedence Test Suite |
| **Current Phase** | Lane A Dry-Run Completed → Preparing Lane B Harvest & Full Analytical Pipeline |

### Executive Summary
Prem Sargara leads the quantitative and computational track for citation source-tiering and weighting analysis. This workstream encompasses pipeline engineering, bug remediation on baseline datasets, deterministic domain normalization, peak-week sampling guardrails, and running the weighted precedence and sensitivity test suites prior to paper publication.

---

## 2. Workspace Architecture & Subfolders

- **Subfolder**: `[UNSET]`
  <!-- TODO: Add subfolder location here once prem-sargara confirms his preferred folder name. Do not guess or auto-assign a folder name. -->

---

## 3. Completed Infrastructure & Milestones

> [!NOTE]
> All items below have been fully implemented, independently reproduced, and verified in the live production pipeline.

- [x] **Repo Scaffolding & Separation**: Repository structured with clean boundaries (`inputs_frozen/`, `scripts/`, `data_derived/`, `docs/`) and proper licensing.
- [x] **Baseline Paper Reproduction**: Baseline paper result ($28/33$, median lead 83 days, $p=6.62\times 10^{-5}$) independently reproduced and verified in the analytical pipeline.
- [x] **`self_ref_openai` Bug Patch**: Resolved silent exclusion bug that would have skewed baseline calculations.
- [x] **Entity Name Bridge (PT ↔ CT)**: Mapped 14 entity name discrepancies between Perception Track and Citation Track.
- [x] **Deterministic Contrast-Week v2**: Investigated `other_week` discrepancy and replaced unrecoverable rule with deterministic `contrast_week` v2 method.
- [x] **Domain Normalization Port Patch**: Fixed port-stripping QA bug (`asiaone.com:443` vs `asiaone.com`).
- [x] **Analytical Sampling Policy**: Implemented peak-week-only sampling policy with automated guardrail tests.
- [x] **Environment Isolation**: Adopted project-local `.venv` environment policy.
- [x] **Data Derived Tracking Standard**: Established deliberate milestone commit policy for `data_derived/`.
- [x] **Contrast-Week Audit Collection**: Collected and archived 22-entity contrast-week dataset (22/22 entities, 263 rows).
- [x] **Model Retirement Verification**: Verified model retirement schedules against primary API documentation (gpt-4.1 safe; gpt-4-0613 / gpt-4o-2024-05-13 retiring Oct 23, 2026).
- [x] **Precision Audit Review**: Reviewed 27 AMBER precision-audit rows (16 affirmative `y`, 5 negative `n`, 6 pending Wayback verification).
- [x] **Non-English Contrast Flagging**: Flagged 31/263 non-English contrast rows for downstream reconciliation.

---

## 4. Operational Task Backlog & Execution Roadmap

### Phase A — Technical Pipeline & Data Processing (PRS Ownership)

| Task ID | Task Description & Deliverable | Status | Target / Dependency |
| :---: | :--- | :---: | :--- |
| **TASK-01** | Fix `VIVEKA_COL_MAP` in `merge_source_data.py` to align with live Label-sheet column schema | `[x] Complete` | Lane A Schema Align |
| **TASK-02** | Reconcile non-English contrast-row count (31 flagged: breakdown genuine vs. false-positive vs. uncertain) | `[x] Complete` | Audit Reconciliation |
| **TASK-03** | Triage 263-row contrast batch: resolve unambiguous rows autonomously, isolate ambiguous rows for Viveka | `[x] Complete` | Triage Batch |
| **TASK-04** | Deprecate `verify_week_match.py` and mark script header as superseded | `[x] Complete` | Maintenance |
| **TASK-05** | Execute browser-based Wayback Machine verification on 6 unverifiable AMBER audit rows | `[x] Complete` | Archive Inspection |
| **TASK-06** | Execute `test_pipeline_smoketest.py` suite to ensure total pipeline green state | `[x] Complete` | QA Validation |
| **TASK-07** | Self-generate `viveka_labeled_export.csv` from live Label master sheet (notify Viveka) | `[x] Complete` | Pipeline Ingestion |
| **TASK-08** | Perform dry-run of complete analytical pipeline on Lane A dataset alone | `[x] Complete` | Validation Run |
| **TASK-09** | Execute Lane B harvest (~28–30 remaining entities) upon GDELT API rate limit reset | `[ ] Pending` | GDELT Availability |
| **TASK-10** | Run full production analytical pipeline (Merge → Tier Map → Weights → Precedence Test → Sensitivity Analysis) | `[ ] Pending` | Post-Lane B Harvest |
| **TASK-11** | Authorship of `tier_methodology.md` (Tier definitions, empirical evidence, weight rationale, raw vs. weighted delta) | `[ ] Pending` | Final Analytical Run |

---

### Phase D — Search Result Distortion Audit

| Task ID | Task Description & Deliverable | Status | Target / Dependency |
| :---: | :--- | :---: | :--- |
| **TASK-20** | Execute Round 3 validation pass (location-based search-result distortion check) | `[x] Complete` | Output: `data_derived/location_distortion_check.csv` (2026-09-17) |

---

### Phase E — Publication Readiness & Joint Synthesis

| Task ID | Task Description & Deliverable | Status | Target / Dependency |
| :---: | :--- | :---: | :--- |
| **TASK-21** | Integrate weighted-vs-raw analytical findings, tier methodology, and syndication caveats into paper draft | `[ ] Pending` | Post-Task 11 |
| **TASK-22** | Update manuscript Declarations and CRediT authorship taxonomy matrix | `[x] Draft Complete` | Drafted in `docs/declarations_and_credit.md` |
| **TASK-23** | Compose Generative AI and AI-Agent usage disclosure section for manuscript | `[x] Draft Complete` | Drafted in `docs/declarations_and_credit.md` |
| **TASK-24** | Conduct full multi-pass stress-test read-through of complete paper manuscript | `[ ] Pending` | Manuscript Freeze |
| **TASK-25** | Finalize target submission venue and update Zenodo DOI repository deposit versioning | `[ ] Pending` | Final Release |
| **TASK-26** | Perform final proofreading, style compliance, and typographic formatting pass | `[ ] Pending` | Final Release |

---

## 5. Cross-Contributor Handoff Matrix

> [!IMPORTANT]
> **Handoff Dependencies:**
> - **Input from Viveka**: Confirmation of `ALREADY_COVERED` entity list (Task 15) before triggering Task 09 (Lane B Harvest).
> - **Output to Viveka**: Self-generated `viveka_labeled_export.csv` schema validation for her final sign-off.
> - **Joint Target**: Completion of Phase E manuscript integration prior to target venue deadline.
