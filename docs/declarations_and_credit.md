# Manuscript Declarations: CRediT Authorship & Generative AI Disclosure

> **Document Status:** Complete Draft for Joint Review & Manuscript Integration  
> **Associated Tasks:** TASK-22 (CRediT Authorship Taxonomy) & TASK-23 (Generative AI Disclosure)  
> **Reference Repository:** `two-clock-source-tiering`

---

## 1. Contributor Roles Taxonomy (CRediT)

In alignment with international journal publishing standards (CASRAI CRediT taxonomy), author responsibilities and contributions are declared as follows:

| Contributor | CRediT Roles & Specific Contributions |
| :--- | :--- |
| **Viveka Mohan Das** | **Conceptualization** (formulation of the Two-Clock Model and the perception-gap dynamic $G(t) = S(t) - P(t)$); **Methodology** (design of the longitudinal Perception Track $P(t)$ ladder and scoring rubrics); **Investigation** (qualitative baseline domain and entity research); **Data Curation** (primary expert labeling of citation samples, round-1 and round-2 precision audit datasets, full-text contrast verification package); **Writing – Original Draft** (core Two-Clock Model manuscript); **Writing – Review & Editing**; **Project Administration**. |
| **Prem Sargara** | **Methodology** (mathematical formulation of empirical source-tiering $\log(\text{Breadth} \times \text{Volume})$, GVF clustering criteria, discrete and continuous weighting functions); **Software** (design, engineering, and maintenance of the complete reproducible Python data pipeline, domain normalization routines, port-stripping fixes, automated test harness); **Formal Analysis** (independent baseline replication, precedence sign tests, sensitivity grid sweeps, location-based search distortion analysis); **Data Curation** (contrast-week GDELT ingestion, AMBER row archival reconciliation); **Writing – Review & Editing** (source-tiering methodology section, sensitivity analysis, syndication caveats). |

---

## 2. Competing Interests

* **Viveka Mohan Das:** The author is the founder of AISearch Global, a consultancy providing answer engine optimization (AEO / GEO) services. The research addresses structural dynamics of answer engine indexing; the author declares this professional affiliation. The interest did not alter or influence the collected data, statistical analysis, or reported findings.
* **Prem Sargara:** The author declares no financial or non-financial competing interests.

---

## 3. Funding

This research received no specific grant or financial support from public, commercial, or not-for-profit funding agencies. Computational resources and API credits were provided directly by the authors.

---

## 4. Declaration of Generative AI and AI-Assisted Technologies

The conceptual foundation of the Two-Clock Model, experimental design, and interpretive synthesis represent the original intellectual work of the human authors. Generative AI technologies were deployed strictly in two designated operational capacities, with the human authors assuming sole responsibility for all outputs, integrity, and conclusions:

### 1. Generative AI as the Object and Instrument of Measurement (Intrinsic to Method)
Longitudinal entity perception $P(t)$ is evaluated directly against five discrete OpenAI model checkpoints:
* `gpt-4-0613` (knowledge cutoff: 2021-09)
* `gpt-4o-2024-05-13` (knowledge cutoff: 2023-10)
* `gpt-4o-2024-11-20` (knowledge cutoff: 2023-10)
* `gpt-4.1-2025-04-14` (knowledge cutoff: 2024-06)
* `gpt-5.2` (knowledge cutoff: 2025-06)

All model probes were queried with web browsing disabled. Model responses were systematically scored ($0$–$4$) against human-authored ground-truth entity profiles by an LLM-assisted evaluator following a validated deterministic rubric, with edge cases reviewed and ratified by human audit.

### 2. Generative AI as Code Scaffolding and Editorial Assistance
AI-assisted coding environments and agentic coding tools (including Google Antigravity and Claude) were employed during computational pipeline development to assist in:
* Authoring reproducible data-processing scripts and unit tests;
* Identifying code bugs (such as f-string backslash portability across Python versions and `:port` URL parsing artifacts);
* Generating initial drafts for technical documentation and table formatting.

All source code, analytical pipelines, data outputs, and text modifications underwent exhaustive human review, execution testing, and independent statistical validation prior to inclusion in the repository.
