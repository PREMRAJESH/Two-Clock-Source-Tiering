# Formal Methodological Withdrawal Notice

**Date:** October 5, 2026  
**Authors / Contributors:** Prem Sargara (Independent Researcher), Viveka Mohan Das (AISearch Global)  
**Repository:** `two-clock-source-tiering`  
**Status:** Permanent Methodological Audit Record  

---

## 1. Executive Summary & Directive

Following an internal pre-publication methodological audit initiated on 2026-10-05, all **weighted numerical results**, **attenuation statistics**, and the associated **Diffuse Ingestion Hypothesis** framing in this repository are formally **WITHDRAWN**.

This action follows the peer-review directive from Viveka Mohan Das (AISearch Global), issued on October 5, 2026:

> *"What it means:*  
> *- The weighted analysis measured peak citation week versus perception onset. It did not measure a weighted ramp. A (1, 1, 1) weighting should reproduce raw 28/33 and gave 13/33 instead.*  
> *- Please treat as withdrawn: 13/33, 12/32, the Tier 1 only rows, the 16-cell and 2-cell sweeps, the weighted rows of the 108-cell matrix, and the Diffuse Ingestion framing as support for anything.*  
> *- Your baseline reproduction, tier map as a description, and syndication and location audits stand, subject to my earlier fix list.*  
> *Please do not edit the manuscript or delete any repo history. Add a dated note in docs."*

In accordance with academic integrity standards and contributor agreements:
- **No manuscript text is deleted.** Historical drafts remain intact for full auditability.
- **No Git history is purged.** All commit lineages (`ff7e57f` through current) are permanently preserved.
- **Advisory banners** are placed at the top of relevant methodological and manuscript documents pointing directly to this notice.

---

## 2. Root Cause: Peak-Week Impulse Truncation

In the original pipeline implementation (`merge_source_data.py` and `scripts/apply_weights.py`):
1. Article-level domain metadata from GDELT ArtList were harvested **only for each entity's single peak citation week** (adopted to respect upstream API rate limits).
2. In `scripts/apply_weights.py` (lines 197–227), unharvested weeks across the 131-week timeline were zero-filled (`wa.get("weighted_count", 0.0)`).
3. As a result, each entity's weighted time series $C_{\text{weighted}}(t)$ contained non-zero values in **exactly 1 week out of 131** (50 non-zero weeks across all 6,570 entity-week records in `ct_results_weighted.csv`).
4. The operational ramp condition ($C(t) \ge \max(0.10 \cdot \text{Peak}, 3)$) was trivially satisfied at that single non-zero week, collapsing the detected "weighted ramp date" to the **peak citation week** ($t_{\text{ramp, weighted}} \equiv t_{\text{peak}}$).
5. The reported lead time $\Delta t_{\text{weighted}} = t_{\text{onset}} - t_{\text{ramp, weighted}}$ was actually measuring **$t_{\text{onset}} - t_{\text{peak}}$**, which is systematically negative for mature models whose perception onset predates late-stage media volume spikes.
6. **Empirical Proof:** When evaluated under equal unweighted parameters $W = (1, 1, 1)$ via `scripts/reproduce_baseline.py`, the pipeline fails to reproduce the raw baseline ($28/33, +83\text{d}, p = 6.62 \times 10^{-5}$); instead, $W=(1, 1, 1)$ identically yields the collapsed result ($13/33, -51\text{d}, p = 0.296$).

The apparent precedence attenuation and invariance across parameter sweeps were mathematical artifacts of single-point time series support, not genuine characteristics of source authority or news timing.

---

## 3. Inventory of Withdrawn Claims and Artefacts

The following claims, numerical values, and interpretations are formally **WITHDRAWN** and must not be cited as empirical findings:

| Withdrawn Claim / Value | Associated Specification | Source Location |
| :--- | :--- | :--- |
| **13 / 33 (39.4%), median lead −51 d, $p = 0.296$** | Continuous weighted precedence ($W = 1.0, 0.5, 0.25$) on Published Baseline ($N=33$) | `tier_methodology.md` Table §4 Row 2; `manuscript_section_source_tiering.md` Table §3.2 Row 2; `standalone_working_paper.md` Abstract & §5 |
| **12 / 32 (37.5%), median lead −51 d, $p = 0.215$** | Continuous weighted precedence ($W = 1.0, 0.5, 0.25$) on Consensus Baseline ($N=32$) | `tier_methodology.md` Table §4 Row 4; `manuscript_section_source_tiering.md` Table §3.2 Row 4; `standalone_working_paper.md` §5 |
| **Tier 1 Only: 12 / 32 (37.5%), −51 d, $p = 0.215$** | Binary exclusion (Tier 1 domains only) | `tier_methodology.md` Table §4 Row 5; `manuscript_section_source_tiering.md` Table §3.2 Row 5 |
| **Tier 1+2: 12 / 32 (37.5%), −51 d, $p = 0.215$** | Binary exclusion (Tier 1 + Tier 2 domains) | `tier_methodology.md` Table §4 Row 6; `manuscript_section_source_tiering.md` Table §3.2 Row 6 |
| **Lane A Benchmark (Continuous): 3 / 11 (27.3%)** | 11-entity preliminary test cohort | `tier_methodology.md` Table §4 Row 7 |
| **All 16 Weight-Sweep Cells** | $4 \times 4$ parameter grid ($w_2 \in [0.25, 1.0], w_3 \in [0.0, 0.5]$) yielding invariant $13/33$ | `manuscript_section_source_tiering.md` §4.1; `data_derived/sensitivity_results.csv` (`variant=weight_sweep`) |
| **Weighted Rows of 108-Cell Matrix** | Ramp thresholds $\times$ floor values $\times$ perception cutoffs | `manuscript_section_source_tiering.md` §4.5; `data_derived/sensitivity_results.csv` |
| **Boundary Perturbation Weighted Rows** | $\pm 10\%$ Jenks boundary perturbation cells | `manuscript_section_source_tiering.md` §4.2; `data_derived/sensitivity_results.csv` |
| **The Diffuse Ingestion Hypothesis** | Framing domain down-weighting as evidence of long-tail LLM pretraining absorption | `manuscript_section_source_tiering.md` §5; `standalone_working_paper.md` §6 |

---

## 4. Inventory of Surviving Results

The following empirical results and analytical assets remain valid, verified, and unaffected by the single-week impulse artifact:

| Surviving Result / Asset | Verified Benchmark | Notes |
| :--- | :--- | :--- |
| **Raw Baseline Reproduction** | **28 / 33 (84.8%), median lead +83 d, $p = 6.62 \times 10^{-5}$** | Fully reproducible via `scripts/reproduce_baseline.py` against frozen baseline inputs |
| **Consensus Raw Baseline** | **27 / 32 (84.4%), median lead +89 d, $p = 1.13 \times 10^{-4}$** | Section 5.5 multi-run consensus mean spec (`pt_pilot_results_merged.csv`) |
| **Descriptive Domain Tier Map** | 1,210 domains classified into Tier 1 (11), Tier 2 (142), Tier 3 (1,057); $\text{GVF} = 0.8606$ | Valid as a descriptive taxonomy of domain coverage breadth $\log(\text{Breadth} \times \text{Volume})$ |
| **Empirical Syndication Findings** | Verbatim story duplication across regional affiliate networks (Threads, Operator, Qwen) | Observational finding regarding GDELT ArtList syndication concentration |
| **Geographic Distortion Audit** | 0-day shift across high-concentration single-country entities | Validated in `data_derived/location_distortion_check.csv` (Task 20) |

> [!IMPORTANT]
> **Condition of Retention:** Per Viveka Mohan Das's directive, the surviving results stand **subject to the earlier fix list (Items 4–35)**. Full item-by-item triage and resolution are tracked in [`docs/viveka_review_response_items_4_to_35.md`](file:///d:/two-clock-source-tiering/docs/viveka_review_response_items_4_to_35.md).

---

## 5. References & Audit Trail

- Technical Audit Memo: [`docs/viveka_review_response_items_1_to_3.md`](file:///d:/two-clock-source-tiering/docs/viveka_review_response_items_1_to_3.md)
- Equivalence Assertion: [`scripts/reproduce_baseline.py`](file:///d:/two-clock-source-tiering/scripts/reproduce_baseline.py) (`check_weights_111_equivalence()`)
- Project Session Log: [`docs/session_log.md`](file:///d:/two-clock-source-tiering/docs/session_log.md)
- Code Guardrails: `scripts/apply_weights.py`, `scripts/precedence_test_weighted.py`, `scripts/sensitivity_analysis.py`, `scripts/run_production_pipeline.py`
