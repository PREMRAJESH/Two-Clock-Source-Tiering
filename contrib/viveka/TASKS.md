# Contributor Workspace & Task Tracking — Viveka

> **Workstream:** Source-Tiering Sign-offs & Perception Track $P(t)$  
> **Repository Scope:** `contrib/viveka/`  
> **Status:** Active (Phase 2 Review & Sign-off) | **Last Updated:** 2026-09-22

---

## 1. Contributor Metadata & Overview

| Attribute | Specification |
| :--- | :--- |
| **Contributor** | Viveka (`viveka`) |
| **Primary Domain** | Source Quality Classification, Expert Labeling, Perception Track $P(t)$ Analysis |
| **Core Deliverables** | Source Tiering Sign-Offs, Round 2 Entity Scoring, Dual $P(t)$ Replication Passes |
| **Current Phase** | Expert Sign-offs Completed → Pending $P(t)$ Reruns & SSRN Rights Resolution |

### Executive Summary
Viveka leads the qualitative source-tiering assessment and perception tracking ($P(t)$) stream. Her responsibilities include reviewing domain classifications, signing off on edge cases and ambiguous non-English contrast rows, conducting multi-pass scoring on the 50 target entities, and maintaining the perception-track timeline ahead of model retirement deadlines.

---

## 2. Workspace Architecture & Subfolders

- **Subfolder**: `[UNSET]`
  <!-- TODO: Add subfolder location here once viveka confirms her preferred folder name. Do not guess or auto-assign a folder name. -->

---

## 3. Operational Task Backlog & Execution Roadmap

### Phase B — Source-Tiering Review & Expert Sign-Offs

| Task ID | Task Description & Deliverable | Status | Target / Dependency |
| :---: | :--- | :---: | :--- |
| **TASK-12** | Review and sign off on CSV-vs-master discrepancy and the 5 Kimi `y → n` overrides | `[x] Complete` | Master Sheet Audit |
| **TASK-13** | Formal sign-off on automated pipeline export (`viveka_labeled_export.csv`) vs. manual hand-export | `[x] Complete` | Ingestion Sign-off |
| **TASK-14** | Deliver final expert rulings on genuinely ambiguous non-English contrast rows | `[x] Complete` | Contrast Triage |
| **TASK-15** | Confirm final `ALREADY_COVERED` entity list prior to triggering Lane B production harvest | `[x] Complete` | Pre-Lane B Freeze |

---

### Phase C — Perception Track $P(t)$ & Longitudinal Scoring

> [!IMPORTANT]
> **Hard Deadline:** October 23, 2026 for $P(t)$ reruns due to legacy model deprecation schedules (`gpt-4-0613`, `gpt-4o-2024-05-13`).

| Task ID | Task Description & Deliverable | Status | Target / Dependency |
| :---: | :--- | :---: | :--- |
| **TASK-16** | Complete two independent $P(t)$ rerun executions prior to hard deadline (Oct 23, 2026) | `[x] Complete` | Hard Deadline: Oct 23 |
| **TASK-17** | Complete Round-2 qualitative scoring pass on the 50 target entities | `[x] Complete` | Scoring Pass |
| **TASK-18** | Evaluate necessity and execute $3\times$-repeat-per-cutoff stability verification check | `[x] Complete` | Stability Audit |
| **TASK-19** | Investigate and resolve SSRN publishing-rights and pre-print licensing policy | `[ ] Pending` | Pre-Publication |

---

### Phase E — Publication Readiness & Joint Synthesis

| Task ID | Task Description & Deliverable | Status | Target / Dependency |
| :---: | :--- | :---: | :--- |
| **TASK-21** | Collaborate on paper manuscript draft (weighted-vs-raw comparison, source-tier section) | `[ ] Pending` | Post-Task 11 |
| **TASK-22** | Update Declarations section and verify CRediT contributor taxonomy | `[ ] Pending` | Pre-Submission |
| **TASK-23** | Review Generative AI / Agent disclosure section for accuracy | `[ ] Pending` | Pre-Submission |
| **TASK-24** | Participate in complete stress-test read-through of the manuscript | `[ ] Pending` | Manuscript Freeze |
| **TASK-25** | Finalize target submission venue selection and Zenodo DOI archiving | `[ ] Pending` | Final Release |
| **TASK-26** | Perform final proofreading and formatting verification | `[ ] Pending` | Final Release |

---

## 4. Cross-Contributor Handoff Matrix

> [!NOTE]
> **Handoff Dependencies:**
> - **Deliverable to Prem Sargara**: Round-2 scoring output to enable Prem's Round-3 location-based search distortion audit (Task 20).
> - **Input from Prem Sargara**: Analytical output delta from `tier_methodology.md` for joint manuscript integration.
