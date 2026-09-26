# Research Documentation & Decision Registry

> **Directory Scope:** `docs/`  
> **Classification:** Methodological Specifications, Decision Logs & Consolidated State Reports  
> **Governance:** Traceability Chain for Two-Clock Source-Tiering Research

---

## 1. Documentation Architecture

This directory maintains the formal scientific and operational records that connect frozen input datasets (`inputs_frozen/`) to derived statistical findings (`data_derived/`).

| Document Name | Document Layer | Primary Governance Function |
| :--- | :--- | :--- |
| [`session_log.md`](session_log.md) | **Decision & Provenance Record** | Chronological ledger documenting every methodological choice, technical remediation, bug fix, and associated Git commit hash. **Authoritative source of truth**. |
| [`project_overview_report.md`](project_overview_report.md) | **Consolidated State Report** | Comprehensive snapshot of repository architecture, lane status, implementation benchmarks, and blocking dependencies. |
| [`tier_methodology.md`](tier_methodology.md) | **Methodological Specification** | Formal specification of domain clustering algorithms (Jenks natural breaks), authority tier definitions, continuous/binary weighting schemes, and sensitivity protocols. |
| [`declarations_and_credit.md`](declarations_and_credit.md) | **Publication Declarations** | Formal CRediT contributor taxonomy and Generative AI instrument/editorial disclosures (Tasks 22 & 23). |
| [`ssrn_publishing_and_licensing_policy.md`](ssrn_publishing_and_licensing_policy.md) | **Preprint & Rights Policy** | Legal, copyright retention, Creative Commons license selection (CC-BY-NC-ND vs. CC-BY), and journal prior-publication compliance guide for SSRN and Zenodo (Task 19). |

---

## 2. Document Navigation & Usage Guide

* **To Review Methodological Decisions & Chronology:**  
  Consult [`session_log.md`](session_log.md). Entries are ordered chronologically; recent decisions appear toward the bottom.
* **To Inspect Operational Project Status & Milestone Progress:**  
  Consult [`project_overview_report.md`](project_overview_report.md) for task-by-task execution states and pipeline verification status.
* **To Inspect Tiering Formulas, Mathematical Formulations, & Limitations:**  
  Consult [`tier_methodology.md`](tier_methodology.md) for statistical formulations and syndication handling rules.

---

## 3. Methodological Governance Standards

1. **Traceability Principle:** Every empirical claim must trace directly to a reproducible computational script in `scripts/` and a verified input in `inputs_frozen/`.
2. **Decision Precedence:** In cases of discrepancies between summary prose and chronological entries, [`session_log.md`](session_log.md) holds ultimate precedence.
3. **Hypothesis Neutrality:** Methodological pipelines and exclusion criteria must remain invariant regardless of whether results yield a positive correlation or a reportable null finding.

---

## 4. Licensing

Documentation in this directory is released under the **MIT License** ([`LICENSE-CODE.md`](../LICENSE-CODE.md)).