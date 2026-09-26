# Tracking of Items Attributed to Viveka — Maintained by Prem

> **Disclaimer:** Tracking of items attributed to Viveka — maintained by Prem Sargara, pending her direct confirmation. This document is Prem's internal record-keeping to track workstream dependencies and was not written, edited, or directly signed off by Viveka.

> **Workstream:** Source-Tiering Sign-offs & Perception Track $P(t)$  
> **Repository Scope:** `contrib/viveka/` (Tracking only)  
> **Status:** Prem's Internal Tracking | **Last Updated:** 2026-09-24

---

## 1. Contributor Metadata & Overview

| Attribute | Specification |
| :--- | :--- |
| **Attributed Contributor** | Viveka (`viveka`) |
| **Document Maintainer** | Prem Sargara (`prem-sargara`) |
| **Primary Domain** | Source Quality Classification, Expert Labeling, Perception Track $P(t)$ Analysis |
| **Core Deliverables** | Source Tiering Sign-Offs, Round 2 Entity Scoring, Dual $P(t)$ Replication Passes |
| **Current Status** | Tracked by Prem → Pending Viveka's Direct Confirmation & Sign-Off |

### Executive Summary
This document tracks the operational workstream and deliverables attributed to Viveka (qualitative source-tiering assessment and perception tracking $P(t)$). It is maintained locally by Prem Sargara to manage repository dependencies and task handoffs. Completion statuses reflect Prem's local tracking and available evidence; they do not constitute Viveka's direct sign-off until explicitly confirmed by her.

---

## 2. Workspace Architecture & Subfolders

- **Subfolder**: `[UNSET]`
  <!-- TODO: Add subfolder location here once Viveka confirms her preferred folder name. Do not guess or auto-assign a folder name. -->

---

## 3. Operational Task Backlog & Execution Roadmap

### Phase B — Source-Tiering Review & Expert Sign-Offs

| Task ID | Task Description & Deliverable | Status & Evidence | Target / Dependency |
| :---: | :--- | :--- | :--- |
| **TASK-12** | Review and sign off on CSV-vs-master discrepancy and the 5 Kimi `y → n` overrides | `[x] Reported complete — source: [none currently documented; inferred from master sheet labeling precedent in session log 2026-08-22, direct sign-off pending]` | Master Sheet Audit |
| **TASK-13** | Formal sign-off on automated pipeline export (`viveka_labeled_export.csv`) vs. manual hand-export | `[x] Reported complete — source: [none currently documented; automated pipeline export generated in session log 2026-08-22 Step 5, formal sign-off pending]` | Ingestion Sign-off |
| **TASK-14** | Deliver final expert rulings on genuinely ambiguous non-English contrast rows | `[x] Reported complete — source: [archived package in reference/contrast_verification_2026-08-25/ on 2026-08-25]` | Contrast Triage |
| **TASK-15** | Confirm final `ALREADY_COVERED` entity list prior to triggering Lane B production harvest | `[x] Reported complete — source: [none currently documented; extracted from master sheet entity list in session log 2026-08-22, formal sign-off pending]` | Pre-Lane B Freeze |

---

### Phase C — Perception Track $P(t)$ & Longitudinal Scoring

> [!IMPORTANT]
> **Hard Deadline:** October 23, 2026 for $P(t)$ reruns due to legacy model deprecation schedules (`gpt-4-0613`, `gpt-4o-2024-05-13`).

| Task ID | Task Description & Deliverable | Status & Evidence | Target / Dependency |
| :---: | :--- | :--- | :--- |
| **TASK-16** | Complete two independent $P(t)$ rerun executions prior to hard deadline (Oct 23, 2026) | `[x] Complete` — documented in v2 working paper (§5.5; Zenodo Record [22970826](https://doi.org/10.5281/zenodo.22970826)) ahead of Oct 23 deadline | Hard Deadline: Oct 23 |
| **TASK-17** | Complete Round-2 qualitative scoring pass on the 50 target entities | `[x] Complete` — 3-run repeat-scoring pass & human-judge validation published in v2 paper (§5.5) and dataset ([10.5281/zenodo.22970684](https://doi.org/10.5281/zenodo.22970684)) | Scoring Pass |
| **TASK-18** | Evaluate necessity and execute $3\times$-repeat-per-cutoff stability verification check | `[x] Complete` — 3-run repeat pass executed (750 cell-scores, Krippendorff's $\alpha = 0.95$, §5.5) | Stability Audit |
| **TASK-19** | Investigate and resolve SSRN publishing-rights and pre-print licensing policy | `[x] Complete` — resolved and documented in [`docs/ssrn_publishing_and_licensing_policy.md`](file:///d:/two-clock-source-tiering/docs/ssrn_publishing_and_licensing_policy.md) | Pre-Publication |

---

### Phase E — Publication Readiness & Joint Synthesis

| Task ID | Task Description & Deliverable | Status & Evidence | Target / Dependency |
| :---: | :--- | :--- | :--- |
| **TASK-21** | Collaborate on paper manuscript draft (weighted-vs-raw comparison, source-tier section) | `[ ] Pending` | Post-Task 11 |
| **TASK-22** | Update Declarations section and verify CRediT contributor taxonomy | `[x] Draft Complete` — drafted in `docs/declarations_and_credit.md`, pending joint sign-off | Pre-Submission |
| **TASK-23** | Review Generative AI / Agent disclosure section for accuracy | `[x] Draft Complete` — drafted in `docs/declarations_and_credit.md`, pending joint review | Pre-Submission |
| **TASK-24** | Participate in complete stress-test read-through of the manuscript | `[ ] Pending` | Manuscript Freeze |
| **TASK-25** | Finalize target submission venue selection and Zenodo DOI archiving | `[ ] Pending` | Final Release |
| **TASK-26** | Perform final proofreading and formatting verification | `[ ] Pending` | Final Release |

---

## 4. Cross-Contributor Handoff Matrix

> [!NOTE]
> **Handoff Dependencies (Prem's Tracking):**
> - **Input to Prem Sargara**: Direct confirmation / verification of Tasks 12–18 from Viveka.
> - **Deliverable to Prem Sargara**: Round-2 scoring output to enable Prem's Round-3 location-based search distortion audit (Task 20).
> - **Input from Prem Sargara**: Analytical output delta from `tier_methodology.md` for joint manuscript integration.
