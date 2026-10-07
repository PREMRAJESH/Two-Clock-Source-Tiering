> [!WARNING]
> **WITHDRAWAL ADVISORY (2026-10-05):** The weighted numerical results in this document (e.g., Abstract, Table 2 weighted rows, §5 results, and §6 Diffuse Ingestion framing) are formally **WITHDRAWN** due to single-week impulse truncation. The descriptive tier map, baseline reproduction, and structural methodology specifications stand. See [`docs/withdrawal_notice_2026-10-05.md`](file:///d:/two-clock-source-tiering/docs/withdrawal_notice_2026-10-05.md).

# Does Domain Coverage Breadth Matter? Source-Tier Weighting and the Temporal Precedence of News Mentions over AI Perception

**Prem Sargara**  
*Independent Researcher*  

*Working Paper — October 2026*  
**Repository:** https://github.com/PREMRAJESH/two-clock-source-tiering  

---

## Abstract

Recent empirical work on the temporal dynamics of artificial intelligence knowledge acquisition has established that third-party news citations systematically precede the onset of AI perception for emerging technology entities. In the Two-Clock Model (Mohan Das, 2026), citation ramps temporally precede perception onsets in 28 of 33 testable entities (concordance 84.8%, median lead +83 days, exact two-sided sign test $p = 6.62 \times 10^{-5}$). However, that baseline specification treats all news citations equally, aggregating mentions from high-volume national broadsheets, regional syndicates, and specialized technology blogs into an unweighted volume metric $C(t)$. 

This study investigates whether weighting news citations using an empirical, domain coverage-based source tiering scheme—derived via unsupervised Jenks natural breaks optimization on observed domain coverage breadth and volume—strengthens, attenuates, or leaves unchanged the observed citation-to-perception temporal precedence. Evaluated across 50 technology entities and 1,210 unique publishing domains observed in GDELT ArtList data (3,413 article records in the analytical benchmark; 1,239 domains in the full 50-entity harvest), source-tier weighting substantially attenuates the precedence signal: concordance drops from 84.8% (28/33) to 39.4% (13/33), the median lead time shifts from +83 days to −51 days, and statistical significance is lost ($p = 0.296$). Under the alternative multi-run consensus perception specification ($N = 32$), raw concordance is 84.4% (27/32, median lead +89 days, $p = 1.13 \times 10^{-4}$), collapsing under weighting to 37.5% (12/32, median lead −51 days, $p = 0.215$). 

This attenuation is robust across a systematic 126-condition sensitivity evaluation encompassing alternative threshold matrices (108 cells), weight-vector ratio sweeps (16 cells), and tier-boundary perturbations (2 cells). The findings are consistent with the early citation signal being concentrated in domains assigned to the lower-weighted tiers under the study's empirical tiering scheme, whereas domains assigned to Tier 1 systematically publish later in the entities' lifecycles. An explanatory conjecture—the *Diffuse Ingestion Hypothesis*, positing that web-scale LLM pretraining crawls absorb diffuse media before high-breadth institutional reporting emerges—is proposed for future investigation, though the present analysis does not directly test this pretraining mechanism. Major limitations include peak-week citation sampling and coarse temporal resolution of model checkpoints.

**Keywords:** Two-Clock Model, domain coverage tiering, citation weighting, AI perception, GDELT, Jenks natural breaks, temporal precedence, non-parametric sign test, sensitivity analysis, reproducible research.

---

## 1. Introduction

### 1.1 Research Context

Understanding how large language models (LLMs) acquire factual representations of real-world entities is a central question in AI evaluation, information retrieval, and computational social science. As foundation models increasingly serve as primary interfaces for knowledge discovery, the timeline and mechanisms governing their acquisition of real-world knowledge carry substantial practical and societal implications.

The Two-Clock Model (Mohan Das, 2026) established an empirical framework for analyzing this phenomenon by tracking technology entities across three temporal signals:
1. **$S(t)$ — Structural Web Presence:** The chronological inception of an entity's formal web presence, measured via public announcement dates and archived homepage captures.
2. **$P(t)$ — AI Perception:** The emergence of factual entity knowledge within AI models, measured by probing a longitudinal ladder of dated OpenAI model checkpoints (with web browsing disabled) and scoring outputs on a validated $0$–$4$ scale against ground-truth descriptions.
3. **$C(t)$ — Third-Party News Citations:** The accumulation of third-party public attention, measured through weekly news-mention volumes harvested from the Global Database of Events, Language, and Tone (GDELT).

The core empirical finding of the Two-Clock Model is that third-party citation ramps systematically precede the onset of AI perception across a statistically significant majority of testable entities (28 of 33, 84.8%, median lead +83 days, exact two-sided sign test $p = 6.62 \times 10^{-5}$). This established an empirical temporal precedence relationship between public citation accumulation and AI perception onset.

### 1.2 Research Question

The baseline Two-Clock Model specification operates on raw, unweighted citation counts: an article published by a major national daily of record, a regional newspaper syndicate, a specialized trade blog, or an automated RSS aggregator contributes identically to $C(t)$. In media studies, information retrieval, and bibliometrics, citations are rarely treated as homogeneous; coverage breadth, reporting volume, and institutional prominence are widely recognized as structuring the public diffusion of news.

This study poses a specific, empirical question:

> **Primary Research Question:** Does weighting third-party news citations by an empirical, coverage-based domain tiering scheme strengthen, attenuate, or leave unchanged the observed temporal precedence of citation ramps over AI perception onsets?

### 1.3 Motivation

This inquiry is motivated by two competing theoretical perspectives:

- **The Institutional Prominence Hypothesis ($H_1$):** If AI perception is primarily driven by prominent, high-volume institutional journalism that major web crawlers prioritize or that benchmark evaluations reflect, weighting citations by domain coverage prominence should *strengthen* the precedence relationship. Filtering out low-coverage noise would sharpen the citation ramp date, producing tighter concordance and stronger statistical significance.
- **The Diffuse Coverage Hypothesis ($H_2$):** If AI perception is instead driven by undifferentiated, high-volume web crawls (such as Common Crawl) that ingest broad distributions of digital content long before high-breadth institutional newsrooms allocate reporting resources, weighting by domain prominence should *attenuate* or invert the precedence relationship. Down-weighting diffuse, lower-tier media would delay the detected citation ramp until after perception onset.
- **The Orthogonal Null Hypothesis ($H_0$):** Domain coverage prominence may be temporally uncorrelated with citation volume, leaving concordance and lead times statistically indistinguishable from the raw baseline.

### 1.4 Contributions

This study provides the following specific analytical contributions:

1. **Independent Reproduction of Baseline Results:** Re-execution and verification of the Two-Clock Model baseline across both the published single-run specification ($N = 33$, 28/33, +83 days, $p = 6.62 \times 10^{-5}$) and the multi-run consensus mean specification ($N = 32$, 27/32, +89 days, $p = 1.13 \times 10^{-4}$).
2. **Empirical Source-Tier Taxonomy:** Construction of an unsupervised, reproducible three-tier domain classification for 1,210 publishing domains (1,239 in the full 50-entity harvest) observed across technology entities in GDELT ArtList data, utilizing an empirical coverage metric ($\log(\text{Breadth} \times \text{Volume} + 1)$) partitioned via Jenks natural breaks optimization ($\text{GVF} = 0.8606$; $\text{GVF} = 0.8729$ in the full harvest).
3. **Weighted Precedence Analysis:** Demonstration that source-tier weighting substantially *attenuates* the precedence relationship, dropping concordance to 39.4% (13/33, $p = 0.296$) on the published specification and 37.5% (12/32, $p = 0.215$) on the consensus specification, while shifting the median lead time from positive (+83/+89 days) to negative (−51 days).
4. **Comprehensive Sensitivity Evaluation:** Systematic execution of 126 evaluation conditions supporting the robustness of the observed attenuation across the evaluated parameterizations, including weight vector sweeps (16 cells), threshold combinations (108 cells), and tier boundary perturbations (2 cells).
5. **Methodological Characterization:** Identification that the findings are consistent with the early citation signal being concentrated in domains assigned to the lower-weighted tiers under the empirical tiering scheme, and formal specification of the *Diffuse Ingestion Hypothesis* as an explanatory framework for future research.

---

## 2. Background and Related Work

### 2.1 The Two-Clock Model

The Two-Clock Model (Mohan Das, 2026) models the emergence of technology entities across two distinct "clocks": Clock 1 ($S(t)$, structural web existence) and Clock 2 ($P(t)$, AI perception). The divergence between these signals defines the perception gap:

$$G(t) = S(t) - P(t)$$

The model posits that $G(t)$ closes as third-party citations $C(t)$ accumulate. To test whether citation accumulation temporally precedes perception onset, the study operationalizes:
- **Citation Ramp Date ($t_{\text{ramp}}$):** The earliest week in which $C(t)$ reaches at least 10% of its historical peak, subject to an absolute minimum floor of 3 mentions.
- **Perception Onset Date ($t_{\text{onset}}$):** The knowledge cutoff date of the earliest model checkpoint where $P(t) \ge 3$ (on a $0$–$4$ scale).
- **Temporal Lead ($\Delta t$):** $\Delta t = t_{\text{onset}} - t_{\text{ramp}}$ (measured in days). A positive lead ($\Delta t > 0$) denotes citation precedence.

Across 50 technology entities, after excluding 10 query-precision audit failures (Section 4.5) and 7 entities that had not achieved perception onset by the final model checkpoint (Section 5.4), the published testable cohort consists of $N = 33$ entities. The baseline result is:

$$\text{Concordance} = \frac{28}{33} \quad (84.8\%), \quad \text{Median Lead} = +83 \text{ days}, \quad p = 6.62 \times 10^{-5}$$

The underlying dataset is permanently archived on Zenodo (DOI: 10.5281/zenodo.21532575). In subsequent work, a multi-run consensus dataset across three repeat probe evaluations was released (Zenodo DOI: 10.5281/zenodo.22970684; Krippendorff's $\alpha = 0.95$), under which Windsurf's mean score reaches $2.67 < 3.0$, yielding $N = 32$ testable entities (27/32, 84.4%, median lead +89 days, $p = 1.13 \times 10^{-4}$).

### 2.2 Domain Stratification and Coverage Metrics

In bibliometrics and webometrics, domain stratification is frequently performed using commercial indices (e.g., Moz Domain Authority, NewsGuard trust ratings, or Alexa traffic ranks). However, such metrics introduce severe limitations: they are proprietary, paywalled, opaque in their algorithmic formulation, and impossible to audit or reproduce over time. Furthermore, commercial "authority" scores often conflate search-engine optimization with journalistic rigor.

To preserve scientific reproducibility and avoid subjective value judgments, this study deliberately eschews commercial authority claims in favor of an **endogenous, data-driven measure of domain coverage prominence** derived directly from the observed empirical corpus. The metric reflects publishing breadth and volume across technology entities, operationally classifying domains into tiers of coverage scale rather than measuring intrinsic journalistic credibility.

The Global Database of Events, Language, and Tone (GDELT) project (Leetaru & Schrodt, 2013) monitors news media worldwide in over 100 languages. GDELT's `TimelineVolRaw` service provides weekly aggregate mention frequencies, while its `ArtList` mode returns article-level metadata, including source URLs, publishing domains, publication timestamps, and headlines.

### 2.3 Research Gap

While the Two-Clock Model established a significant temporal relationship between aggregate citation volume and AI perception, it left the internal composition of $C(t)$ unexamined. It did not test whether domain coverage breadth moderates this relationship, nor whether the observed lead time is driven by high-breadth newsrooms or diffuse, long-tail digital publishing.

### 2.4 Position of This Study Relative to the Original Work

This paper is an **analytical extension** of the Two-Clock Model. Its boundaries are explicitly delimited:
- **Reproduction:** The baseline precedence results of the Two-Clock Model are independently reproduced from frozen inputs to establish an exact, audited benchmark.
- **Extension:** The coverage-based tiering taxonomy, the weighting procedures, the weighted precedence calculations, and the 126-condition sensitivity analysis represent new, distinct empirical work.
- **Non-Claims:** This study does not modify the underlying theoretical formulation of the Two-Clock Model, nor does it challenge the validity of the original unweighted baseline. It investigates an orthogonal empirical dimension: source composition.

---

## 3. Research Questions and Hypotheses

### 3.1 Formal Hypotheses

Let $\Delta t_{\text{raw}, e}$ and $\Delta t_{\text{weighted}, e}$ denote the temporal lead of citation ramps over perception onset for entity $e$ under unweighted and weighted citation series, respectively. Let $\pi = P(\Delta t > 0)$ denote the population concordance proportion.

We test the following competing hypotheses against the null:

- **Null Hypothesis ($H_0$):** Source-tier weighting does not alter the temporal precedence structure.
  $$\pi_{\text{weighted}} = \pi_{\text{raw}} \approx 0.85, \quad \text{Median}(\Delta t_{\text{weighted}}) \approx \text{Median}(\Delta t_{\text{raw}}) > 0$$
- **Institutional Prominence Hypothesis ($H_1$):** High-breadth institutional journalism drives AI perception. Weighting citations by domain coverage prominence sharpens the temporal signal, increasing concordance and statistical significance.
  $$\pi_{\text{weighted}} \ge \pi_{\text{raw}}, \quad p_{\text{weighted}} \le p_{\text{raw}}$$
- **Diffuse Coverage Hypothesis ($H_2$):** Early AI perception is driven by broad, diffuse digital coverage that precedes high-breadth institutional reporting. Weighting down diffuse media attenuates the precedence signal.
  $$\pi_{\text{weighted}} < 0.50, \quad \text{Median}(\Delta t_{\text{weighted}}) \le 0, \quad p_{\text{weighted}} > 0.05$$

### 3.2 Secondary Research Questions

1. Is the weighted precedence outcome sensitive to the specific weight ratios assigned to tiers?
2. Does the result depend on the precise mathematical boundaries of the unsupervised clustering partitions?
3. Does the result hold across varying ramp thresholds (5%, 10%, 20%) and perception onset thresholds ($P \ge 2, 3, 4$)?
4. Does binary tier filtering (Tier 1 only, or Tier 1 + Tier 2) yield results consistent with continuous weighting?

---

## 4. Data and Methodology

### 4.1 Dataset and Entity Selection

The target universe comprises the 50 technology entities established in the Two-Clock Model roster (`inputs_frozen/entities.py`, frozen as of 2026-07-08; Zenodo DOI: 10.5281/zenodo.21532575). Entities encompass foundation models, autonomous agents, developer infrastructure, consumer hardware, and generative applications announced between early 2023 and mid-2024.

The sample filtering protocol exactly follows the original Two-Clock Model specification:

| Sample Filter Stage | Entity Count | Entities Excluded / Included | Methodological Justification |
| :--- | :---: | :--- | :--- |
| **Total Entity Roster** | **50** | All entities in `inputs_frozen/entities.py` | Initial universe |
| **Precision-Audit Failures** | **−10** | DBRX, Kimi, Ideogram, Lovable, Gemini (Google model), Dream Machine, Liquid AI, Mamba, Operator, vLLM | Section 4.5, Table 1: High term collision rate on GDELT keyword searches |
| **No-Onset Entities (v1)** | **−7** | OpenAI o1, OpenAI o3, DeepSeek, DeepSeek-R1, Manus, World Labs, Bolt.new | Section 5.4: Entity did not achieve $P(t) \ge 3$ on the 5-checkpoint model ladder |
| **Published Testable Sample (v1)** | **33** | 33 testable technology entities | Primary benchmark specification |
| **Additional Exclusion (v2 Consensus)** | **−1** | Windsurf (Mean score reaches $2.67 < 3.0$) | Section 5.5: Multi-run consensus mean threshold exclusion |
| **Consensus Testable Sample (v2)** | **32** | 32 testable technology entities | 3-run consensus mean specification |

### 4.2 Citation and Perception Data

#### 4.2.1 Weekly Citation Counts $C(t)$
Weekly citation timelines are drawn from `inputs_frozen/ct_results_v1_frozen.csv`, comprising 6,570 entity-week records. For each entity, weekly news mention counts are tracked over a 131-week window spanning from 52 weeks prior to birth to 78 weeks post-birth.

#### 4.2.2 Longitudinal Perception Scores $P(t)$
Perception scores are evaluated across five discrete OpenAI model checkpoints queried with web browsing disabled:
1. `gpt-4-0613` (Knowledge cutoff: September 2021)
2. `gpt-4o-2024-05-13` (Knowledge cutoff: October 2023)
3. `gpt-4o-2024-11-20` (Knowledge cutoff: October 2023)
4. `gpt-4.1-2025-04-14` (Knowledge cutoff: June 2024)
5. `gpt-5.2` (Knowledge cutoff: June 2025)

Models were probed using standardized prompts, and responses were scored $0$–$4$ against expert ground truth. Two versions are examined:
- **v1 (Single-Run):** `inputs_frozen/pt_pilot_results.csv` (250 records).
- **v2 (3-Run Consensus Mean):** `inputs_frozen/pt_pilot_results_merged.csv` (250 records; Krippendorff's $\alpha = 0.95$).

### 4.3 Source-Level Evidence Collection

To assess domain coverage distributions, article-level metadata was collected via GDELT ArtList mode for each entity's peak citation week. Data collection proceeded across two lanes:
- **Lane A (22 entities):** Collision-prone entities evaluated and curated by the lead author of the original Two-Clock study, yielding 517 article records (`inputs_frozen/ct_artlist_LABELING.xlsx`).
- **Lane B (28 entities):** Remaining entities harvested via `scripts/ct_source_harvester.py`, yielding 3,146 article records (`data_derived/ct_source_results.csv`).

Merging Lane A and Lane B (`scripts/merge_source_data.py`) yields a complete corpus of **3,663 article records across all 50 entities** (`data_derived/ct_source_all.csv`). Domain normalization routines stripped protocol schemes (`http://`, `https://`), removed `www.` subdomains, eliminated trailing slashes, lowercased all strings, and stripped URL port artifacts (e.g., `asiaone.com:443` $\to$ `asiaone.com`).

Across the analytical benchmark corpus of 3,413 records (49 entities), **1,210 unique normalized publishing domains** are identified. Incorporating DeepSeek-R1 yields 3,663 records across 1,239 domains.

### 4.4 Source-Tier Construction

To eliminate subjectivity and proprietary lock-in, domain tiers are determined through unsupervised empirical clustering of observed publishing behavior.

#### Step 1: Compound Domain Coverage Metric Formulation
For each domain $d \in D$, we define a coverage prominence metric based on two orthogonal dimensions:
1. **Breadth ($B_d$):** The number of distinct technology entities covered by domain $d$ ($1 \le B_d \le 50$). High breadth indicates cross-industry journalistic purview.
2. **Volume ($V_d$):** The total number of articles published by domain $d$ across the entire corpus. High volume indicates substantial reporting output.

The compound metric is formulated as:

$$\text{Metric}_d = \log(B_d \times V_d + 1)$$

The $+1$ term represents a standard smoothing adjustment preventing undefined values for zero-frequency edge conditions.

#### Step 2: Unsupervised Jenks Natural Breaks Optimization
Domain classification boundaries are established via 1D Jenks natural breaks optimization (Fisher-Caspall algorithm), implemented in `scripts/build_tier_map.py`. The algorithm seeks partition boundaries $k_1, k_2$ that minimize squared deviations from tier means while maximizing squared deviations between tiers.

Model fit is evaluated via the Goodness of Variance Fit (GVF):

$$\text{GVF} = 1 - \frac{\text{SDAM}}{\text{SDCM}}$$

where $\text{SDAM}$ is the Sum of Squared Deviations from Class Means and $\text{SDCM}$ is the Sum of Squared Deviations from the Grand Mean. A fit of $\text{GVF} \ge 0.70$ is the pre-specified threshold for acceptable classification.

**Empirical Clustering Results:**  
Across the production corpus of **1,210 unique normalized publishing domains**, the Jenks algorithm converged at natural partition thresholds of **$[1.6094, 3.0445]$**, achieving:

$$\text{GVF} = 0.8606$$

This exceeds the minimum acceptance threshold of 0.70, confirming adequate intra-tier homogeneity. (In the expanded 50-entity harvest of 1,239 domains incorporating DeepSeek-R1, breaks partition at $[1.3863, 3.0445]$ with $\text{GVF} = 0.8729$; testable precedence results are identical across both runs because DeepSeek-R1 is in the no-onset exclusion set).

#### Step 3: Tier Architecture
The resulting three-tier taxonomy is structured as follows:

| Coverage Tier | Empirical Criteria | Domain Count | Percentage | Default Weight ($w_k$) | Representative Domain Archetypes |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **Tier 1 (High Breadth / Volume)** | $\text{Metric}_d \ge 3.0445$ | 178 | 14.7% | 1.00 | *TechCrunch, Economic Times, Yahoo Finance, Indian Express, BizToc, VentureBeat* |
| **Tier 2 (Specialized / Regional)** | $1.6094 \le \text{Metric}_d < 3.0445$ | 403 | 33.3% | 0.50 | *Proactive Investors UK, NBC Regional Affiliates, How-To Geek, Investing.com* |
| **Tier 3 (Diffuse / Long-Tail)** | $\text{Metric}_d < 1.6094$ | 629 | 52.0% | 0.25 | *Jamaica Gleaner, SwissInfo, IT Brief NZ, ComicBookMovie, niche digital blogs* |

### 4.5 Weighting Procedure

Weighted citation counts are computed for each entity $e$ and week $t$ by `scripts/apply_weights.py`. Let $C_{k, e}(t)$ denote the article count from domains assigned to tier $k \in \{1, 2, 3\}$. The weighted citation volume is:

$$C_{\text{weighted}, e}(t) = \sum_{k=1}^{3} w_k \cdot C_{k, e}(t)$$

where the baseline continuous weight vector is $\mathbf{W}_{\text{default}} = (1.00, 0.50, 0.25)$.

In addition to continuous weighting, two binary exclusion regimes are evaluated:
1. **Tier 1 Only:** $C_{\text{T1}, e}(t) = C_{1, e}(t)$ (retaining only top-tier institutional media).
2. **Tier 1 + Tier 2:** $C_{\text{T12}, e}(t) = C_{1, e}(t) + C_{2, e}(t)$ (excluding long-tail diffuse media).

### 4.6 Citation Precedence Measurement

Temporal precedence metrics are computed by `scripts/precedence_test_weighted.py`, strictly applying the Two-Clock Model definitions:
- **Peak Volume:** $\text{Peak}(C) = \max_t C(t)$.
- **Ramp Week ($t_{\text{ramp}}$):** The first week $t$ where:
  $$C(t) \ge \theta_{\text{ramp}} \cdot \text{Peak}(C) \quad \text{and} \quad C(t) \ge \text{Floor}$$
  Default parameters: threshold $\theta_{\text{ramp}} = 0.10$ (10% of peak); $\text{Floor} = 3$ mentions.
- **Onset Date ($t_{\text{onset}}$):** The earliest model cutoff date where perception score $P(t) \ge \theta_{\text{onset}}$ (default $\theta_{\text{onset}} = 3$).
- **Lead Time ($\Delta t$):** $\Delta t = t_{\text{onset}} - t_{\text{ramp}}$ (in days). A negative lead time ($\Delta t < 0$) indicates that the citation ramp occurred after perception onset; it does not imply an absence of earlier citations, but rather that citation volume did not cross the operational ramp threshold prior to $t_{\text{onset}}$.
- **Concordance Indicator:** $\text{sgn}(\Delta t) = +1$ if $\Delta t > 0$; $-1$ if $\Delta t < 0$; $0$ if $\Delta t = 0$.

### 4.7 Statistical Testing

Statistical significance is evaluated using the non-parametric **exact two-sided sign test** on the sign vector across all testable entities. Under $H_0$, the number of positive leads $K = \sum \mathbb{I}(\Delta t_e > 0)$ follows a binomial distribution:

$$K \sim \text{Binomial}(N, 0.5)$$

The two-sided exact $p$-value represents the probability of observing a result at least as extreme as $K$ in either direction under $H_0$:

$$p = 2 \cdot \sum_{i=0}^{\min(K, N-K)} \binom{N}{i} 0.5^N$$

This test makes no parametric assumptions regarding lead-time distributions and is robust to extreme outliers.

### 4.8 Sensitivity Analysis Framework

To evaluate methodological stability, `scripts/sensitivity_analysis.py` executes **126 distinct evaluation conditions**:
1. **Threshold Matrix (108 cells):** 3 entity cohorts ($\text{baseline}$, $\text{pass\_only}$, $\text{no\_capped}$) $\times$ 3 ramp thresholds (5%, 10%, 20%) $\times$ 3 onset thresholds ($P \ge 2, 3, 4$) $\times$ 4 count series ($\text{raw}$, $\text{weighted}$, $\text{tier1\_only}$, $\text{tier1\_plus\_2}$).
2. **Weight Ratio Sweep (16 cells):** $4 \times 4$ parameter grid fixing $w_1 = 1.00$, while varying $w_2 \in \{0.25, 0.50, 0.75, 1.00\}$ and $w_3 \in \{0.00, 0.10, 0.25, 0.50\}$.
3. **Boundary Perturbation (2 cells):** Shifting the empirical Jenks break points by $\pm 10\%$ of the inter-break distance and re-clustering domains.

### 4.9 Reproducibility and Computational Pipeline

The analytical pipeline is fully deterministic, containing zero stochastic parameters, and is implemented entirely in standard Python without external library dependencies:
- Master execution script: `scripts/run_production_pipeline.py`
- Pipeline validation test: `scripts/test_pipeline_smoketest.py`
- Baseline assertion lock: `scripts/reproduce_baseline.py`

All frozen inputs in `inputs_frozen/` are immutable and read-only.

---

## 5. Results

### 5.1 Baseline Reproduction

Execution of `scripts/reproduce_baseline.py` independently verifies the baseline results of the Two-Clock Model:

| Specification | $N$ | Precedes ($K$) | Concordance Rate | Median Lead | Exact Sign Test $p$-value | Verification Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Published Baseline (v1, Floor = 3)** | 33 | 28 / 33 | **84.8%** | **+83 days** | **$6.62 \times 10^{-5}$** | Exact Replication |
| **Published Baseline (v1, Floor = 5)** | 33 | 28 / 33 | **84.8%** | **+83 days** | **$6.62 \times 10^{-5}$** | Exact Replication |
| **Multi-Run Consensus (v2, $\bar{P} \ge 3.0$)** | 32 | 27 / 32 | **84.4%** | **+89 days** | **$1.13 \times 10^{-4}$** | Exact Replication |

Under the v2 multi-run consensus mean specification, Windsurf achieves a mean perception score of $2.67 < 3.0$, placing it in the no-onset exclusion set and reducing the testable sample from 33 to 32. Both baseline specifications reproduce the citation-precedence pattern with statistically significant exact sign-test results.

### 5.2 Weighted Precedence Analysis

Applying source-tier weighting yields a substantial attenuation of the temporal precedence signal across both specifications:

| Analytical Specification | Citation Metric | $N$ | Precedes ($K$) | Concordance Rate | Median Lead | Exact Sign Test $p$-value | Significance ($\alpha=0.05$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Published Baseline (v1)** | Raw $C(t)$ | 33 | 28 / 33 | **84.8%** | **+83 days** | **$6.62 \times 10^{-5}$** | Significant |
| **Published Baseline (v1)** | Weighted $C_{\text{weighted}}(t)$ | 33 | 13 / 33 | **39.4%** | **−51 days** | **0.296** | Not Significant |
| **Published Baseline (v1)** | Tier 1 Only | 33 | 13 / 33 | **39.4%** | **−51 days** | **0.296** | Not Significant |
| **Published Baseline (v1)** | Tier 1 + Tier 2 | 33 | 13 / 33 | **39.4%** | **−51 days** | **0.296** | Not Significant |
| **Consensus Baseline (v2)** | Raw $C(t)$ | 32 | 27 / 32 | **84.4%** | **+89 days** | **$1.13 \times 10^{-4}$** | Significant |
| **Consensus Baseline (v2)** | Weighted $C_{\text{weighted}}(t)$ | 32 | 12 / 32 | **37.5%** | **−51 days** | **0.215** | Not Significant |
| **Consensus Baseline (v2)** | Tier 1 Only | 32 | 12 / 32 | **37.5%** | **−51 days** | **0.215** | Not Significant |
| **Consensus Baseline (v2)** | Tier 1 + Tier 2 | 32 | 12 / 32 | **37.5%** | **−51 days** | **0.215** | Not Significant |

**Core Findings:**
1. **Concordance Collapse:** Weighting by domain coverage tier drops concordance by approximately 45 percentage points, crossing from strong precedence (~85%) to below the 50% chance threshold (~38%).
2. **Lead Time Inversion:** The median lead time flips from positive (+83 / +89 days) to negative (−51 days). After weighting by domain tier, AI perception *precedes* the citation ramp by nearly two months.
3. **Loss of Statistical Significance:** The exact sign test $p$-value transitions from highly significant ($p < 10^{-4}$) to completely non-significant ($p \approx 0.22$–$0.30$).
4. **Binary-Continuous Equivalence:** The identical results across the tested continuous and binary regimes indicate that the observed attenuation is not sensitive to these particular weighting formulations.
5. **Interpretation of Negative Lead Times:** A negative lead time (such as those observed for Mistral AI, Ollama, Sakana AI, and xAI; see Appendix B) does not imply that the entity lacked earlier citations altogether; rather, it indicates that the weighted citation series did not reach the specified 10%-of-peak ramp threshold until after the discrete perception-onset cutoff date.

### 5.3 Comparison Across Specifications and Subsets

To confirm that attenuation is not an artifact of specific entity classes or evaluation protocols, we examine entity sub-specifications:

#### 5.3.1 Self-Referential OpenAI Entities Excluded
In `inputs_frozen/entities.py`, OpenAI-developed entities (`GPT-4`, `GPT-4o`, `Sora`) probed on an OpenAI model ladder carry a potential self-recognition confound. Excluding these 3 entities yields:
- **v1 Specification ($N = 30$):**
  - Raw: $25 / 30$ (83.3%), median lead +82 days, $p = 3.25 \times 10^{-4}$
  - Weighted: $11 / 30$ (36.7%), median lead −76 days, $p = 0.200$
- **v2 Specification ($N = 29$):**
  - Raw: $24 / 29$ (82.8%), median lead +83 days, $p = 5.46 \times 10^{-4}$
  - Weighted: $10 / 29$ (34.5%), median lead −100 days, $p = 0.136$

The attenuation pattern is fully preserved when self-referential entities are removed.

#### 5.3.2 Query-Precision PASS Cohort
Restricting analysis to the 11 testable entities that passed rigorous manual precision audits (Section 4.5; e.g., Apple Vision Pro, Cursor, Grok, Suno, Threads, Udio, xAI):
- Raw ($10\%$ ramp, $P \ge 3$): $8 / 11$ (72.7%), $p = 0.227$
- Weighted ($10\%$ ramp, $P \ge 3$): $3 / 11$ (27.3%), $p = 0.227$

#### 5.3.3 Capped-Week Exclusions
Four testable entities reached GDELT's 250-article harvest ceiling during their peak week (`GPT-4`, `GPT-4o`, `OpenAI o1`, `DeepSeek`). Excluding capped entities ($N = 31$):
- Raw ($10\%$ ramp, $P \ge 3$): $26 / 31$ (83.9%), $p = 1.90 \times 10^{-4}$
- Weighted ($10\%$ ramp, $P \ge 3$): $11 / 31$ (35.5%), $p = 0.150$

### 5.4 Sensitivity Analysis

#### 5.4.1 Weight Ratio Sweep (16 Cells)
Fixing $w_1 = 1.00$ while sweeping $w_2 \in \{0.25, 0.50, 0.75, 1.00\}$ and $w_3 \in \{0.00, 0.10, 0.25, 0.50\}$ across all 16 parameter cells produced identical results across all 16 evaluated weight combinations:

$$\text{Concordance} = 13 / 33 \quad (39.4\%), \quad \text{Median Lead} = -51 \text{ days}, \quad p = 0.296$$

Even setting $w_3 = 0.00$ (completely discarding all Tier 3 diffuse media) yields identical concordance, suggesting that, within the evaluated weight grid, the attenuation is associated with the relative timing of Tier 1 coverage rather than fine-grained weight tuning.

#### 5.4.2 Boundary Perturbation Test (2 Cells)
Perturbing the Jenks clustering break points by $\pm 10\%$ of the inter-break gap reassigned domains across boundaries. In both perturbation states, results remained identical:

$$\text{Concordance} = 13 / 33 \quad (39.4\%), \quad \text{Median Lead} = -51 \text{ days}, \quad p = 0.296$$

#### 5.4.3 Threshold Matrix (108 Cells)
Across all 108 evaluated threshold combinations in `data_derived/sensitivity_results.csv`:
- **Raw Series:** Raw concordance ranges from 60.6% to 92.3% across the evaluated threshold conditions. Statistical significance is retained for the primary baseline specification and several lower-threshold variants, but not for every threshold condition (e.g., $p = 0.063$ at 20% ramp, $P \ge 3$ in selected raw variants; $p = 0.080$ at 20% ramp, $P \ge 2$).
- **Weighted Series:** Concordance ranges from 27.3% to 61.5%. **Zero cells achieve statistical significance ($p < 0.05$)**.

### 5.5 Robustness Checks Summary

Across all evaluated dimensions—single-run vs. multi-run perception, self-referential entity exclusion, precision audit filtering, capped-week exclusion, weight-vector sweeps, boundary perturbation, and ramp/onset threshold variations—the observed attenuation pattern remains consistent across the evaluated specifications and sensitivity conditions: **source-tier weighting systematically attenuates the citation precedence signal.**

---

## 6. Discussion

### 6.1 What the Results Show

**The findings are consistent with the early citation signal being concentrated in domains assigned to the lower-weighted tiers under the study's empirical tiering scheme.**

When citations are aggregated without weighting, the unweighted citation series often reaches the ramp threshold months before the AI model demonstrates perception onset. Under the source-tier weighting scheme, the resulting ramp occurs substantially later for the majority of entities, often after the observed perception onset. Because source-level metadata were collected from each entity's peak citation week rather than its ramp week, these results should be interpreted as evidence about the effect of applying the empirically derived tier map to the longitudinal citation series, rather than as a direct characterization of the source composition at the exact ramp week.

The identical results across the tested continuous and binary regimes indicate that the observed attenuation is not sensitive to these particular weighting formulations: under the study's empirical tiering scheme, coverage from domains classified as Tier 1 tends to appear relatively later in the entities' lifecycles compared to observed model perception onset.

### 6.2 What the Results Do NOT Show

To preserve scientific rigor, it is essential to delineate what these empirical results **do not** prove:

1. **No Direct Proof of Pretraining Web Crawl Mechanics:** The non-parametric sign test measures temporal displacement in observational time series. It does not inspect LLM pretraining data, token frequency counts, or Common Crawl ingestion timestamps.
2. **No Causal Mechanism:** The study does not establish whether AI models acquire entity knowledge *from* Tier 2/3 media, or whether both AI models and Tier 2/3 media are responding to an unobserved third factor (such as developer GitHub activity, social media discussions, or pre-print releases).
3. **No Generalization Beyond Technology Entities:** The 50-entity roster consists exclusively of technology products and organizations. Media dynamics for political, cultural, or macroeconomic entities may follow entirely different institutional diffusion paths.
4. **No Qualitative Judgment of Editorial Credibility:** Lower-tier classification in this study reflects empirical coverage breadth and volume within GDELT, not qualitative journalistic accuracy or lack thereof.

### 6.3 Possible Interpretations: The Diffuse Ingestion Hypothesis

Why does high-breadth institutional coverage lag behind AI perception while diffuse coverage leads it? We propose the following non-exclusive interpretations:

#### 1. The Diffuse Ingestion Hypothesis (Explanatory Conjecture)
Large language model pretraining pipelines ingest massive web scrapes (e.g., Common Crawl, web forums, social feeds) with broad, indiscriminate coverage. Emerging technology entities are discussed in developer forums, niche technology publications, and local news syndicates weeks or months before national broadsheets determine that the entity warrants editorial resources. If pretraining pipelines absorb this diffuse digital tail, models will achieve perception onset while high-breadth newsrooms are still in editorial gestation.

> [!IMPORTANT]
> **Hypothesis Status:** The Diffuse Ingestion Hypothesis is an *explanatory hypothesis*, not an empirically proven conclusion of this paper. Testing it requires direct auditing of pretraining corpus composition and crawl scheduling.

#### 2. Institutional Editorial Latency
High-breadth institutional publications (e.g., *The New York Times*, *The Wall Street Journal*, *Financial Times*) maintain rigorous editorial review, fact-checking, and significance thresholds. They rarely cover nascent software tools or developer prototypes upon launch, reporting on them only when commercial scale, regulatory scrutiny, or mainstream controversy emerges.

#### 3. Technology Domain Specialization
In technology domains, early reporting often originates in specialized trade ecosystems (Tier 2/3) that are fast to publish, whereas generalist national media (Tier 1) reports retrospectively.

### 6.4 Alternative Explanations

1. **Syndication Network Distortion:** Wire service stories (e.g., Reuters, Associated Press, AFP) are syndicated across hundreds of regional newspaper domains (e.g., BLOX CMS networks, NBC affiliates). A single syndicated wire piece can generate dozens of Tier 2/3 GDELT records simultaneously, artificially triggering early citation ramp thresholds.
2. **GDELT Indexing Dynamics:** GDELT's web scraper monitors an evolving roster of international domains. Changes in GDELT's crawl priority could induce observational artifacts in citation ramp timing.
3. **Peak-Week Analytical Sampling:** Source-level domain data was harvested for each entity's peak citation week. If domain composition during the peak week differs systematically from the ramp week, tier weighting may project peak-week coverage-tier structures onto early-week volume.

### 6.5 Relationship to the Original Two-Clock Model

These results **complement and enrich**, rather than contradict, the Two-Clock Model:
- The Two-Clock Model established that aggregate third-party attention $C(t)$ leads AI perception $P(t)$. That finding remains fully reproducible.
- This study uncovers the internal structure of that attention signal: the analysis indicates that a substantial component of the observed citation signal is associated with domains assigned to the lower-weighted tiers under the study's empirical tiering scheme.
- These results complement the Two-Clock framework by examining the source composition of the aggregate citation signal.

---

## 7. Limitations

1. **Peak-Week Sampling Strategy:** Detailed article-level source metadata was collected for each entity's peak citation week. Continuous longitudinal harvesting across all 131 weeks per entity was precluded by GDELT API rate-limiting and connection instability.
2. **Temporal Resolution of Model Checkpoints:** The longitudinal perception ladder relies on five historical OpenAI model checkpoints spanning September 2021 to June 2025. Temporal intervals between cutoffs range from 5 to 12 months, limiting the temporal granularity of $t_{\text{onset}}$.
3. **Imminent Checkpoint Retirement:** Legacy checkpoints `gpt-4-0613` and `gpt-4o-2024-05-13` retire on October 23, 2026, after which direct API reproduction of the v1 perception series will require cached responses or local surrogate models.
4. **Single Model Family:** Perception measurements are derived entirely from OpenAI models. Whether Anthropic, Google, or open-weight models exhibit identical temporal dynamics remains unverified.
5. **GDELT Query Ambiguity:** For entities with common-noun names (e.g., *Threads*, *Operator*, *Gemini*), search queries capture unrelated media coverage. While 10 precision-FAIL entities were formally excluded, residual noise may persist.
6. **Coverage Metric vs. Institutional Quality:** The compound metric $\log(B \times V + 1)$ measures coverage breadth and reporting volume within GDELT, not qualitative journalistic credibility, fact-checking rigor, or editorial quality.

---

## 8. Future Research

1. **Pretraining Corpus Audit:** Cross-referencing GDELT domain tier assignments with public pretraining corpus manifests (e.g., Dolma, FineWeb, RedPajama) to directly measure whether Tier 2/3 domains are overrepresented in early training splits.
2. **Full-Timeline Source Harvesting:** Deploying distributed scrapers to collect domain metadata across all 131 weeks for each entity, enabling dynamic, time-varying source-tier weighting.
3. **Multi-Model Perception Ladders:** Replicating the perception track across Claude, Gemini, and open-weight model families (e.g., Llama, Mistral) to evaluate cross-architecture universality.
4. **Syndication Deduplication via Content Fingerprinting:** Applying MinHash or text-embedding deduplication to cluster syndicated wire stories into single editorial events before computing citation ramps.

---

## 9. Conclusion

This study evaluated whether weighting news citations using an empirical domain coverage tiering scheme alters the temporal precedence of citation ramps over AI perception onsets in the Two-Clock Model.

**The primary empirical finding is that source-tier weighting substantially attenuates the observed precedence relationship.** Concordance collapses from ~85% to ~38%, median lead time inverts from positive (+83/+89 days) to negative (−51 days), and statistical significance is lost. This attenuation is robust across the 126 evaluated sensitivity conditions, alternative perception specifications, and entity subsets.

**The observed attenuation is consistent with the Diffuse Coverage Hypothesis (H₂), under which early citation activity may be concentrated in domains assigned to the lower-weighted tiers. However, the present analysis does not directly test the mechanism by which such coverage could influence LLM perception.** The findings are consistent with the early citation signal being concentrated in domains assigned to the lower-weighted tiers under the study's empirical tiering scheme. Under the study's empirical tiering scheme, higher-breadth domains contribute relatively later to the citation signal than the observed perception onset. This temporal pattern should not be interpreted as direct evidence about when or how AI models acquired their representations.

---

## References

1. Mohan Das, V. (2026). *The Two-Clock Model: Structural Presence and AI Perception of Technology Entities* [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.21532575
2. Mohan Das, V. (2026). *The Two-Clock Model: Structural Presence and AI Perception of Technology Entities — 3-Run Consensus Perception Dataset* [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.22970684
3. Jenks, G. F. (1967). The Data Model Concept in Statistical Mapping. *International Yearbook of Cartography*, 7, 186–190.
4. Leetaru, K., & Schrodt, P. A. (2013). GDELT: Global Database of Events, Language, and Tone, 1979–2012. *ISA Annual Convention*, San Francisco, CA.
5. Kleinberg, J. M. (1999). Authoritative sources in a hyperlinked environment. *Journal of the ACM*, 46(5), 604–632.
6. Page, L., Brin, S., Motwani, R., & Winograd, T. (1999). *The PageRank Citation Ranking: Bringing Order to the Web*. Stanford InfoLab Technical Report.
7. Krippendorff, K. (2004). Reliability in Content Analysis: Some Common Misconceptions and Recommendations. *Human Communication Research*, 30(3), 411–433.

---

## Appendix A — Reproducibility and Repository Architecture

### A.1 Directory Structure
```
two-clock-source-tiering/
├── inputs_frozen/                     ← Immutable frozen v1/v2 deposits
│   ├── ct_results_v1_frozen.csv       ← Weekly citation series C(t) (6,570 rows)
│   ├── pt_pilot_results.csv           ← v1 single-run perception series (250 rows)
│   ├── pt_pilot_results_merged.csv     ← v2 3-run consensus perception series (250 rows)
│   ├── ct_artlist_precision.csv       ← Manual precision audit labels (22 entities)
│   ├── ct_artlist_LABELING.xlsx       ← Lane A expert article labels (517 rows)
│   └── entities.py                    ← 50-entity master roster
├── scripts/                           ← Deterministic computational pipeline
│   ├── reproduce_baseline.py          ← Exact baseline reproduction assertion script
│   ├── merge_source_data.py           ← Lane A + Lane B article merger & normalizer
│   ├── build_tier_map.py              ← Unsupervised Jenks natural breaks clustering
│   ├── apply_weights.py               ← Weekly continuous & binary citation weighting
│   ├── precedence_test_weighted.py    ← Exact two-sided sign test evaluation
│   ├── sensitivity_analysis.py        ← 126-condition sensitivity evaluation engine
│   ├── run_production_pipeline.py     ← End-to-end master pipeline runner
│   └── test_pipeline_smoketest.py     ← Sandboxed unit & integration test harness
├── data_derived/                      ← Fully regenerable analytical outputs
│   ├── ct_source_all.csv              ← Unified article records (3,413 benchmark / 3,663 total)
│   ├── domain_tier_map.csv            ← 1,210 domain tier assignments (1,239 total)
│   ├── domain_frequency_analysis.csv  ← Domain breadth, volume, and tier metrics
│   ├── ct_results_weighted.csv        ← Weighted weekly citation series (6,570 rows)
│   ├── precedence_comparison.csv      ← Per-entity ramp dates, onsets, and leads
│   └── sensitivity_results.csv        ← 126-row sensitivity evaluation matrix
├── docs/                              ← Methodological documentation & logs
└── contrib/                           ← Contributor workstream demarcations
```

### A.2 Execution Commands
```bash
# 1. Independent baseline reproduction
python scripts/reproduce_baseline.py

# 2. Execute complete production pipeline (v2 consensus mode)
python scripts/run_production_pipeline.py

# 3. Or execute pipeline steps individually:
python scripts/merge_source_data.py
python scripts/build_tier_map.py
python scripts/apply_weights.py
python scripts/precedence_test_weighted.py --merged
python scripts/sensitivity_analysis.py
```

---

## Appendix B — Complete Statistical Tables

### B.1 Entity-Level Precedence Audit ($N = 33$ Testable Entities, v1 Specification)
*Data Source: `data_derived/precedence_comparison.csv`*

| Entity | Birth Date | Raw Ramp Week | Weighted Ramp Week | Onset Cutoff | Raw Lead (Days) | Weighted Lead (Days) | Raw Sign | Weighted Sign |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **AlphaFold 3** | 2024-05-08 | 2024-05-06 | 2024-05-06 | 2024-06 | +26 | +26 | +1 | +1 |
| **AlphaGeometry** | 2024-01-17 | 2024-01-15 | 2024-07-22 | 2024-06 | +138 | −51 | +1 | −1 |
| **Apple Intelligence** | 2024-06-10 | 2024-06-10 | 2024-09-09 | 2024-06 | −9 | −100 | −1 | −1 |
| **Apple Vision Pro** | 2023-06-05 | 2023-06-05 | 2023-06-05 | 2023-10 | +118 | +118 | +1 | +1 |
| **Black Forest Labs** | 2024-08-01 | 2024-08-12 | 2026-06-15 | 2025-06 | +293 | −379 | +1 | −1 |
| **Claude 3** | 2024-03-04 | 2024-03-04 | 2025-02-24 | 2024-06 | +89 | −268 | +1 | −1 |
| **Command R+** | 2024-04-04 | 2024-03-18 | 2026-02-09 | 2025-06 | +440 | −253 | +1 | −1 |
| **Cursor** | 2023-03-01 | 2025-04-14 | 2026-06-15 | 2025-06 | +48 | −379 | +1 | −1 |
| **Devin AI** | 2024-03-12 | 2024-03-11 | 2024-03-11 | 2024-06 | +82 | +82 | +1 | +1 |
| **ElevenLabs** | 2023-01-23 | 2023-01-30 | 2025-11-10 | 2023-10 | +244 | −771 | +1 | −1 |
| **GPT-4** | 2023-03-14 | 2023-03-13 | 2023-03-13 | 2023-10 | +202 | +202 | +1 | +1 |
| **GPT-4o** | 2024-05-13 | 2024-05-13 | 2024-05-13 | 2024-06 | +19 | +19 | +1 | +1 |
| **Gemini 1.5 Pro** | 2024-02-15 | 2024-02-12 | 2024-05-13 | 2024-06 | +110 | +19 | +1 | +1 |
| **Grok** | 2023-11-04 | 2025-02-17 | 2026-01-12 | 2024-06 | −261 | −590 | −1 | −1 |
| **Humane Ai Pin** | 2023-11-09 | 2023-11-06 | 2024-05-13 | 2023-10 | −36 | −225 | −1 | −1 |
| **Llama 2** | 2023-07-18 | 2023-07-17 | 2023-07-17 | 2023-10 | +76 | +76 | +1 | +1 |
| **Llama 3** | 2024-04-18 | 2024-04-08 | 2024-09-23 | 2024-06 | +54 | −114 | +1 | −1 |
| **Mistral AI** | 2023-04-28 | 2023-06-12 | 2026-01-12 | 2023-10 | +111 | −834 | +1 | −1 |
| **Mixtral 8x7B** | 2023-12-08 | 2023-12-11 | 2024-04-22 | 2024-06 | +173 | +40 | +1 | +1 |
| **NotebookLM** | 2023-07-12 | 2023-07-10 | 2025-05-19 | 2023-10 | +83 | −596 | +1 | −1 |
| **Ollama** | 2023-07-01 | 2024-04-22 | 2026-06-01 | 2024-06 | +40 | −730 | +1 | −1 |
| **Phi-3** | 2024-04-23 | 2024-04-22 | 2024-04-22 | 2024-06 | +40 | +40 | +1 | +1 |
| **Qwen** | 2023-08-03 | 2023-07-31 | 2025-01-27 | 2023-10 | +62 | −484 | +1 | −1 |
| **Rabbit R1** | 2024-01-09 | 2024-01-08 | 2024-01-08 | 2024-06 | +145 | +145 | +1 | +1 |
| **Safe Superintelligence**| 2024-06-19 | 2024-06-17 | 2024-06-17 | 2024-06 | −16 | −16 | −1 | −1 |
| **Sakana AI** | 2023-08-01 | 2024-03-18 | 2026-06-15 | 2024-06 | +75 | −744 | +1 | −1 |
| **Sora** | 2024-02-15 | 2024-02-12 | 2025-12-15 | 2024-06 | +110 | −562 | +1 | −1 |
| **Stable Diffusion 3** | 2024-02-22 | 2024-02-19 | 2024-04-15 | 2024-06 | +103 | +47 | +1 | +1 |
| **Suno** | 2023-12-20 | 2024-02-26 | 2024-06-24 | 2024-06 | +96 | −23 | +1 | −1 |
| **Threads** | 2023-07-05 | 2023-07-03 | 2023-07-03 | 2023-10 | +90 | +90 | +1 | +1 |
| **Udio** | 2024-04-10 | 2024-06-24 | 2024-06-24 | 2024-06 | −23 | −23 | −1 | −1 |
| **Windsurf** | 2024-11-13 | 2025-03-31 | 2025-04-14 | 2025-06 | +62 | +48 | +1 | +1 |
| **xAI** | 2023-07-12 | 2023-07-10 | 2026-01-12 | 2024-06 | +327 | −590 | +1 | −1 |

*(Under the v2 consensus specification, Windsurf is excluded due to mean $P(t) = 2.67 < 3.0$, yielding $N = 32$, Raw: 27/32, Weighted: 12/32).*

---

## Appendix C — Detailed Sensitivity Analysis Architecture

### C.1 The 126-Condition Evaluation Space
The sensitivity evaluation architecture (`data_derived/sensitivity_results.csv`, exactly 126 evaluation rows) resolves earlier historical labeling ambiguities:
- **Historical "90-cell" label:** Originated in early project logs (commit `e3a12e7`) when an early sensitivity run evaluated $3 \text{ cohorts} \times 9 \text{ threshold cells} \times \text{subset of modes} = 90 \text{ rows}$.
- **Production 126-condition evaluation space:**
  - **108 Threshold Matrix Cells:** 3 cohorts ($\text{baseline}$, $\text{pass\_only}$, $\text{no\_capped}$) $\times$ 9 parameter combinations ($\theta_{\text{ramp}} \in \{0.05, 0.10, 0.20\} \times \theta_{\text{onset}} \in \{2, 3, 4\}$) $\times$ 4 counting regimes ($\text{raw}$, $\text{weighted}$, $\text{tier1\_only}$, $\text{tier1\_plus\_2}$).
  - **16 Weight Ratio Sweep Cells:** $4 \times 4$ parameter grid ($w_2 \in \{0.25, 0.50, 0.75, 1.00\} \times w_3 \in \{0.00, 0.10, 0.25, 0.50\}$ with $w_1 = 1.00$ fixed).
  - **2 Boundary Perturbation Cells:** Jenks natural breaks shifted $\pm 10\%$.
  - **Total:** $108 + 16 + 2 = 126$ evaluation conditions.

### C.2 Complete Weight Ratio Sweep Matrix (16 Cells)
All 16 cells evaluated on the baseline specification ($N = 33$) yield strictly identical outcomes:

| Tier 2 Weight ($w_2$) \ Tier 3 Weight ($w_3$) | $w_3 = 0.00$ | $w_3 = 0.10$ | $w_3 = 0.25$ | $w_3 = 0.50$ |
| :---: | :---: | :---: | :---: | :---: |
| **$w_2 = 0.25$** | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) |
| **$w_2 = 0.50$** | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) |
| **$w_2 = 0.75$** | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) |
| **$w_2 = 1.00$** | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) | 13 / 33 ($p = 0.296$) |

---

## Appendix D — Methodological Decision Registry

Key research decisions logged in repository documentation (`docs/session_log.md`):
1. **Selection of Approach B (Empirical Clustering):** Adopted on 2026-08-17 to prevent reliance on proprietary, paywalled authority scores (Moz DA, NewsGuard) and guarantee full algorithmic reproducibility.
2. **Peak-Week Analytical Sampling Enforced (2026-08-18):** Enforced by an automated guardrail in `scripts/merge_source_data.py` to ensure uniform cross-entity temporal sampling.
3. **URL Port Normalization (2026-08-22):** Resolved crawler port artifacts (e.g., `asiaone.com:443`) that caused artificial domain fragmentation.
4. **Disambiguation Bridge Implementation (2026-08-26):** Implemented canonical name mapping bridging perception parentheticals (e.g., `Cursor (the AI code editor)`) to citation series names (`Cursor`).
5. **Formal Adoption of Hypothesis Framing (2026-10-01):** Following feedback from Viveka Mohan Das, the mechanism connecting early diffuse media to LLM pretraining absorption was formally designated as the *Diffuse Ingestion Hypothesis* to prevent conflating observational time-series attenuation with causal proof.

---

## Appendix E — Empirical Audits and Quality Assurance

### E.1 Location-Based Search Distortion Check
An empirical audit evaluated whether geographic concentration in GDELT article coverage distorted citation peak timing (`data_derived/location_distortion_check.csv`). For the 9 entities displaying $>60\%$ geographic concentration in a single country (e.g., Threads, Apple Vision Pro, Apple Intelligence, Cursor), recomputing peak dates while excluding the dominant country yielded a **0-day shift in peak timing**.

### E.2 News Syndication Duplication Audits
Audits of article URLs revealed extensive verbatim syndication:
- **Threads:** A single article was republished across 6 distinct NBC regional affiliate domains (`nbcsandiego.com`, `nbcnewyork.com`, `nbcdfw.com`, etc.).
- **Operator:** A single wire report appeared across 4 Nine-owned Australian mastheads (`smh.com.au`, `theage.com.au`, etc.).
- **Kimi:** An AFP multi-company roundup appeared across 5 local newspaper mastheads sharing the BLOX CMS platform.

---

## Declarations

### Author Statement
Prem Sargara is the sole author of this study. The author conceived and formulated the empirical source-tiering methodology ($\log(\text{Breadth} \times \text{Volume} + 1)$), engineered the Jenks natural breaks clustering pipeline and weighting algorithms, executed all statistical precedence tests and the 126-condition sensitivity analysis, engineered the reproducible software pipeline, and authored the complete manuscript.

### Acknowledgments
The author expresses sincere gratitude to Viveka Mohan Das (AISearch Global, Sydney) for conceptualizing the foundational Two-Clock Model framework, depositing the baseline empirical datasets on Zenodo, and providing critical methodological review, mentorship, and guidance throughout this research.

### Competing Interests
The author declares no competing financial or non-financial interests.

### Funding
This research received no external financial support from government, commercial, or non-profit funding bodies. Computational infrastructure and API resources were provided directly by the authors.

### Generative AI Disclosure
In compliance with academic transparency standards:
1. **Generative AI as Object of Study:** Dated OpenAI model checkpoints (`gpt-4-0613`, `gpt-4o-2024-05-13`, `gpt-4o-2024-11-20`, `gpt-4.1-2025-04-14`, `gpt-5.2`) served as the empirical measurement instrument for $P(t)$.
2. **Generative AI as Coding Assistant:** AI-assisted development tools (Claude and Google Antigravity) were employed for code scaffolding, bug identification, and drafting assistance. All algorithms, mathematical logic, statistical tests, data outputs, and textual drafts were reviewed, executed, and independently verified by the authors.

### Data and Code Availability
- **Frozen Research Datasets:** Permanently archived on Zenodo under CC-BY-4.0:
  - Two-Clock Model v1 Deposit: https://doi.org/10.5281/zenodo.21532575
  - Multi-Run Consensus Perception Dataset: https://doi.org/10.5281/zenodo.22970684
- **Software Pipeline:** Hosted on GitHub (`two-clock-source-tiering`), released under the MIT License: https://github.com/PREMRAJESH/two-clock-source-tiering
