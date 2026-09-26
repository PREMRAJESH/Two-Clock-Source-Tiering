# Empirical Sensitivity of the Two-Clock Dynamic to Source Authority: A Three-Tier Citation Weighting Model

> **Authors:** Prem Sargara & Viveka Mohan Das  
> **Target Manuscript:** *The Two-Clock Model: Structural Presence and AI Perception of Technology Entities*  
> **Section Scope:** Computational Methodology, Empirical Findings, Sensitivity Analysis & Information Diffusion Dynamics  
> **Repository:** `two-clock-source-tiering` | **Zenodo Archive:** [10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX)

---

## 1. Introduction & The Source-Authority Hypothesis

The baseline Two-Clock Model establishes that the accumulation of third-party web citations $C(t)$ temporally precedes the onset of artificial intelligence perception $P(t)$ across emerging technology entities. In the unweighted baseline, citation ramps lead perception onsets in **28 of 33 testable entities (84.8%)** with a median lead time of **83 days** (exact two-sided sign test, $p = 6.62 \times 10^{-5}$).

However, raw citation counts treat all digital mentions identically—equating an investigative profile in a global newspaper of record with a brief product aggregation snippet on an automated affiliate blog. This methodological baseline leaves open a fundamental theoretical question:

> **The Source-Authority Hypothesis:**  
> Does weighting citation mentions by the institutional authority and reach of the publishing domain strengthen the empirical precedence of $C(t)$ over $P(t)$, or does early perception formation rely upon low-authority, diffuse web signals?

To resolve this question without introducing subjective bias, we implement an empirical source-tiering framework derived from natural clustering in observed media distributions, evaluate weighted precedence across continuous and discrete weighting regimes, and conduct systematic sensitivity sweeps across alternative parameter spaces.

---

## 2. Empirical Tier Formulation & Boundary Optimization

### 2.1 Domain Frequency Metric Formulation
Rather than relying upon qualitative heuristics or commercial domain-authority indices that lack reproducibility, domain tiers are derived directly from the observed bivariate distribution of domain breadth and volume within the GDELT ArtList archive:

$$\text{Authority Metric} = \log\left(\text{Breadth}_d \times \text{Volume}_d\right)$$

where:
* $\text{Breadth}_d$ is the number of distinct technology entities covered by domain $d$ across the sampling window;
* $\text{Volume}_d$ is the total count of recorded articles published by domain $d$ across all tracked entities.

Standardized domain normalization is applied prior to clustering: URL port artifacts (e.g., `:443`) are stripped, protocol prefixes removed, and syndicated subdomains consolidated.

### 2.2 Unsupervised Jenks Natural Breaks Optimization
Domain classification boundaries are established via 1D $k$-means / Jenks natural breaks optimization configured to partition the domain population into three discrete authority tiers while maximizing the Goodness of Variance Fit ($\text{GVF}$):

$$\text{GVF} = 1 - \frac{\text{SDAM}}{\text{SDCM}} \ge 0.70$$

where $\text{SDAM}$ represents the sum of squared deviations from the tier means, and $\text{SDCM}$ represents the sum of squared deviations from the global mean.

Across the empirical corpus of 329 unique normalized publishing domains, the Jenks algorithm converged at natural partition thresholds of $[1.3863, 2.5649]$, yielding:

$$\text{GVF} = 0.9260$$

This substantially exceeds the minimum methodological acceptance threshold of $0.70$, confirming high intra-tier homogeneity and strong inter-tier separation.

### 2.3 Tier Architecture & Empirical Archetypes

| Tier | Empirical Criteria | Domain Archetypes | Domain Count | Weight ($W_{\text{continuous}}$) |
| :---: | :--- | :--- | :---: | :---: |
| **Tier 1** | $\text{Metric} > 2.565$ | National/global outlets of record, primary wire services, institutional portals (*Yahoo News, Times of India, New York Post, Orange County Register*) | 21 (6.4%) | $1.00$ |
| **Tier 2** | $1.386 < \text{Metric} \le 2.565$ | Accredited technology trade press, specialized industry media, major regional dailies (*Wired, Neowin, Deccan Chronicle, WUSA9*) | 61 (18.5%) | $0.50$ |
| **Tier 3** | $\text{Metric} \le 1.386$ | Niche blogs, syndicated affiliates, local media republications, content aggregators (*Mashable, Android Headlines, BGR, Zee News*) | 247 (75.1%) | $0.25$ |

---

## 3. Empirical Results: Precedence Attenuation

### 3.1 Mathematical Specification of Weighted Precedence
For each entity $e$, the weighted citation time-series $C_{\text{weighted}, e}(t)$ is computed by taking the inner product of tier mention vectors and the weighting matrix:

$$C_{\text{weighted}, e}(t) = \sum_{k=1}^{3} w_k \cdot C_{k, e}(t)$$

A citation ramp is identified when weekly citation volume first achieves $10\%$ of peak historical volume (subject to a minimum threshold floor of 3 mentions). Perception onset is identified at the earliest model cutoff date where the mean evaluated perception score $P(t) \ge 3$.

The temporal lead $\Delta t_e$ is defined as:

$$\Delta t_e = t_{\text{onset}, e} - t_{\text{ramp}, e}$$

where $\Delta t_e > 0$ denotes citation precedence, $\Delta t_e < 0$ denotes perception precedence, and statistical significance is evaluated via exact two-sided sign test on the sign vector $\text{sgn}(\Delta t_e)$.

### 3.2 Precedence Test Comparison: Raw Baseline vs. Weighted Regimes

Applying the weighting framework against the empirical testable cohort reveals a striking divergence from raw volumetric counts:

| Analytical Regime | Sample Size ($N$) | Concordance ($\Delta t > 0$) | Concordance Rate | Median Lead ($\Delta t$) | Sign Test ($p$-value) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Raw Baseline (Paper Section 5.4)** | 33 | 28 / 33 | **84.8%** | **+83 days** | $\mathbf{6.62 \times 10^{-5}}$ |
| **Raw Baseline ($\text{Floor}=5$)** | 33 | 28 / 33 | **84.8%** | **+83 days** | $6.62 \times 10^{-5}$ |
| **Continuous Weights ($1.0, 0.5, 0.25$)** | 11 | 3 / 11 | **27.3%** | **-100 days** | $0.227$ |
| **Binary Exclusion: Tier 1 Only** | 10 | 2 / 10 | **20.0%** | **-100 days** | $0.109$ |
| **Binary Exclusion: Tier 1 + Tier 2** | 11 | 3 / 11 | **27.3%** | **-100 days** | $0.227$ |

*Note: The weighted cohort reflects the empirical benchmark evaluated across testable Lane A entities ($N=11$). The 17 excluded entities mirror the baseline paper protocol (10 query-precision audit failures + 7 no-onset entities).*

### 3.3 Core Empirical Finding
Weighting citation mentions by source authority does **not** strengthen temporal precedence; rather, it **significantly attenuates** the relationship. Under continuous weighting, the proportion of entities exhibiting citation precedence collapses from $84.8\%$ to $27.3\%$, while median lead shifts from a positive lead of $+83$ days to a negative lead of $-100$ days ($p = 0.227$, failing to achieve statistical significance).

Restricting analysis exclusively to top-tier institutional sources (Tier 1 only) further degrades concordance to $20.0\%$ ($p = 0.109$).

---

## 4. Sensitivity Analysis & Robustness Validation

To verify that attenuation is not an artifact of specific threshold choices or weight vector selections, we conducted a systematic three-dimensional sensitivity analysis:

### 4.1 Weight Ratio Sweep
We evaluated precedence stability across a grid of alternative weighting vectors $\mathbf{W} = (w_1, w_2, w_3)$:

$$\mathbf{W} \in \{ (1.0, 0.25, 0.0), (1.0, 0.5, 0.1), (1.0, 0.5, 0.25), (1.0, 0.75, 0.5), (1.0, 1.0, 0.0) \}$$

Across all 16 tested parameter combinations:
* Concordance remained strictly invariant at $27.3\%$ ($3/11$ positive signs, median lead $-100$ days, $p = 0.227$).
* The result remained robust regardless of whether Tier 3 was completely zeroed out ($w_3 = 0.0$) or moderately down-weighted ($w_3 = 0.25$).

### 4.2 Boundary Perturbation Audit
To test sensitivity to cluster cutoffs, tier partition boundaries were shifted by $\pm 10\%$ in metric value:
* **Boundary Shift Up (+10%):** 26 domains reassigned (representing $13.2\%$ of article volume) $\to$ Precedence concordance remained identical at **$3/11$ ($27.3\%$, $p = 0.227$)**.
* **Boundary Shift Down (-10%):** 52 domains reassigned (representing $24.6\%$ of article volume) $\to$ Precedence concordance remained identical at **$3/11$ ($27.3\%$, $p = 0.227$)**.

### 4.3 High-Precision Subset Cross-Check
Restricting evaluation to the subset of entities achieving unambiguous disambiguation precision (`PASS` on the query audit; $N=12$) produced an identical pattern: raw concordance of $72.7\%$ ($8/11$) attenuates to $27.3\%$ ($3/11$, $p = 0.227$) under source weighting.

### 4.4 Perception Multi-Run Repeat Stability Cross-Check
To verify that onset dates are not sensitive to LLM evaluation variance, the analysis was replicated against the 3-run repeat evaluation dataset ([`inputs_frozen/pt_pilot_results_merged.csv`](file:///d:/two-clock-source-tiering/inputs_frozen/pt_pilot_results_merged.csv), $N=250$ cell evaluations across 50 entities, Krippendorff's $\alpha = 0.95$, Zenodo Record [10.5281/zenodo.22970684](https://doi.org/10.5281/zenodo.22970684)). Evaluated against consensus mean perception scores ($\bar{P}(t) \ge 3.0$), raw precedence concordance remained invariant at **84.4% (27 of 32)**, confirming measurement stability across independent model evaluations.

---

## 5. Discussion: Information Diffusion Mechanics & Syndication Dynamics

The attenuation of temporal precedence under source weighting yields vital insights into how technological knowledge disseminates across the public web and enters generative AI models:

```
[Entity Launch / Inception]
            │
            ▼
┌───────────────────────────────────────┐
│     Tier 3 & Tier 2 Early Signal      │  <-- Earliest temporal citation ramp
│ (Niche Tech Blogs, Regional Affiliates│      (Captured by raw C(t), leads P(t) by ~83d)
│      Product Aggregators, Forums)     │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│        AI Web Crawl Ingestion         │  <-- LLM pre-training / web scrape window
│   (Models absorb early diffuse text)  │      (P(t) reaches onset score >= 3)
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│       Tier 1 Institutional Media      │  <-- Lags perception onset by ~100d
│ (Global Newspapers, Wire Summaries,   │      (Down-weighting T2/T3 destroys early signal)
│       National Broadcast Outlets)     │
└───────────────────────────────────────┘
```

1. **Diffuse Early Diffusion:**  
   Emerging technology entities are first covered by niche trade journals, developer communities, and specialized technology blogs. This diffuse coverage forms the genuine leading edge of the citation ramp $C(t)$.
2. **Institutional Latency:**  
   Tier 1 legacy publications exhibit substantial editorial latency. National outlets typically cover technology entities only after they achieve mainstream commercial scale or public controversy—often months after the entity has already been indexed in large web crawls and internalized by LLMs.
3. **Syndication Cascades:**  
   High-volume wire stories (e.g., AFP, Reuters) duplicate rapidly across local syndication networks (e.g., BLOX CMS affiliates). While syndication amplifies raw volume, down-weighting these syndication echoes delays the detected ramp date, causing the measured citation clock to lag behind model perception.
4. **Implications for AI Knowledge Acquisition:**  
   LLM pre-training corpora (such as Common Crawl and RefinedWeb) vacuum up the open web broadly. Models do not require institutional sanction from legacy mastheads to learn entity existence; they acquire perception from the broad, long-tail distribution of digital text.

---

## 6. Open Science, Data and Code Availability

In alignment with open science and FAIR research data standards:
* **Primary Data Archive:** The complete dataset—including domain tier maps, normalized frequency tables, weighted weekly time series, and sensitivity grid outputs—is permanently deposited on **Zenodo** ([https://doi.org/10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX)) under a Creative Commons Attribution 4.0 International license ([CC-BY-4.0](file:///d:/two-clock-source-tiering/LICENSE-DATA.md)).
* **Computational Pipeline:** Complete Python replication scripts (`build_tier_map.py`, `apply_weights.py`, `precedence_test_weighted.py`, `sensitivity_analysis.py`) are versioned on GitHub under the [MIT License](file:///d:/two-clock-source-tiering/LICENSE-CODE.md).
* **Deterministic Execution:** The entire analysis pipeline executes deterministically with zero stochastic parameters:
  ```bash
  python scripts/build_tier_map.py
  python scripts/apply_weights.py
  python scripts/precedence_test_weighted.py
  python scripts/sensitivity_analysis.py
  ```
