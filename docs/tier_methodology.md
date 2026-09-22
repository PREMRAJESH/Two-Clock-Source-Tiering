# Source-Tiering Methodology & Weighting Specification

> **Status:** Draft / Methodological Specification Template  
> **Target Milestone:** Source Data Ingestion & Production Tiering Run  
> **Reference Paper:** *The Two-Clock Model: Structural Presence and AI Perception of Technology Entities* (Mohan Das, 2026)  
> **Repository:** `two-clock-source-tiering`

---

## 1. Research Question & Empirical Objective

This document establishes the methodological framework and computational specification for testing the source-authority hypothesis within the Two-Clock Model framework:

> **Core Research Question:**  
> Does weighting third-party news citations $C(t)$ by **source authority** ($C_{\text{weighted}}(t)$) strengthen, attenuate, or leave unchanged the observed empirical precedence of citation ramps over AI-perception onsets $P(t)$?

In the baseline paper, citation ramps precede perception onsets in **28 of 33 testable entities (84.8%)** with a median lead of **83 days** ($p = 6.62 \times 10^{-5}$, two-sided exact sign test). This analytical contribution tests whether incorporating domain-level authority signals provides additional predictive power beyond raw volumetric accumulation.

---

## 2. Source Authority Tier Architecture

> [!IMPORTANT]
> **Empirical Derivation Standard:**  
> Tier boundaries and continuous weighting parameters must be derived empirically from observed data (`data_derived/ct_source_all.csv`) via statistical clustering rather than subjective qualitative assignment.

| Tier | Conceptual Scope | Target Domain Archetypes | Weight Scheme (Binary) | Weight Scheme (Continuous) |
| :---: | :--- | :--- | :---: | :---: |
| **Tier 1** | Primary National / Global Outlets & Institutional Authorities | Top-tier national/international newspapers, wire services (Reuters, AP), Wikipedia, official governmental portals | $1.00$ | Normalized mean frequency within cluster |
| **Tier 2** | Specialized Trade Press & Regional Publications | Accredited technology journals, industry-specific trade publications, established regional outlets | $0.50$ | Normalized mean frequency within cluster |
| **Tier 3** | Syndication Aggregators, Blogs & Niche Web Media | Syndication mirrors, niche tech blogs, community forums, low-authority content aggregators | $0.25$ | Normalized mean frequency within cluster |

---

## 3. Methodological Principles & Boundary Formulation

Boundary selection rests on reproducible, data-driven statistical methods:

1. **Empirical Frequency Clustering (Approach B):**  
   Domain tier assignments are generated using 1D $k$-means / Jenks natural breaks optimization applied to the compound metric:
   $$\text{Metric} = \log(\text{Breadth} \times \text{Volume})$$
   where $\text{Breadth}$ is the count of distinct entities citing the domain, and $\text{Volume}$ is the total article mention count across all sampled entities. Clustering quality is validated by ensuring a Goodness of Variance Fit ($\text{GVF} \ge 0.70$).

2. **Precision Audit Cross-Validation:**  
   Domain prevalence distributions are cross-referenced between high-precision ($\text{PASS}$) and low-precision ($\text{FAIL}$) entity subsets (`inputs_frozen/ct_artlist_precision.csv`) as an empirical sanity check to ensure clustering stability across distinct query noise profiles.

3. **Weight Sensitivity Grid:**  
   To safeguard against arbitrary weight selection, results are subjected to a multi-dimensional parameter sweep across alternative continuous and discrete weighting vectors:
   $$\mathbf{W} \in \{ (1.0, 0.5, 0.25), (1.0, 0.75, 0.5), (1.0, 0.33, 0.1), (1.0, 1.0, 0.0) \}$$

---

## 4. Baseline Exclusion Protocol (Paper Alignment)

The analytical sample strictly mirrors the 33-entity testable set established in Sections 4.5 and 5.4 of the baseline paper:

$$\text{Testable Set (33)} = \text{Total Entities (50)} \setminus \left( \text{Precision FAIL (10)} \cup \text{No-Onset Entities (7)} \right)$$

### Exclusion Roster

* **Precision-Audit Failures (10 Entities; Section 4.5, Table 1):**  
  `DBRX`, `Kimi`, `Ideogram`, `Lovable`, `Gemini (Google model)`, `Dream Machine`, `Liquid AI`, `Mamba`, `Operator`, `vLLM`
* **No-Onset Entities (7 Entities; Section 5.4):**  
  `OpenAI o1`, `OpenAI o3`, `DeepSeek`, `DeepSeek-R1`, `Manus`, `World Labs`, `Bolt.new`

> [!NOTE]
> **OpenAI Self-Reference Handling:**  
> The `self_ref_openai` flag in `inputs_frozen/entities.py` applies to entities evaluated on an OpenAI-based model ladder (`GPT-4`, `GPT-4o`, `Sora`). These entities remain in the primary 33-entity baseline to ensure direct comparability with published results, and are isolated only within dedicated sensitivity sub-analyses.

### Verified Reproduction vs. Projected Results

| Analysis Variant | Sample Size ($N$) | Ramp Precedes Onset | Concordance Rate | Median Lead | $p$-value (Sign Test) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Raw Baseline ($\text{Floor}=3$)** | 33 | 28 / 33 | 84.8% | 83 days | $6.62 \times 10^{-5}$ |
| **Raw Baseline ($\text{Floor}=5$)** | 33 | 28 / 33 | 84.8% | 83 days | $6.62 \times 10^{-5}$ |
| **Weighted Analytical Model** | 33 | *[Pending Data]* | *[Pending Data]* | *[Pending Data]* | *[Pending Data]* |
| **Weighted (Excl. `self_ref_openai`)** | 30 | *[Pending Data]* | *[Pending Data]* | *[Pending Data]* | *[Pending Data]* |

---

## 5. Methodological Caveats & Structural Limitations

1. **Syndication and Wire Story Duplication:**  
   GDELT ArtList mode records individual article URLs per hosting domain. High-volume syndication aggregators (e.g. `yahoo.com`, `msn.com`) republish wire stories from primary agencies (Reuters, AP) verbatim, artificially inflating aggregator frequency metrics while under-representing original wire sources.
   
   *Empirical instances documented during 2026-08-18 audit spot-checks:*
   - **Threads:** A single syndicated story (*"Conspiracy theories about the Trump rally shooting flourish online"*) was captured $6\times$ across distinct regional NBC affiliate domains (`nbcsandiego.com`, `nbcnewyork.com`, `nbcdfw.com`, etc.).
   - **Operator:** *"Perplexity AI wants to dethrone Google…"* appeared across $4$ independent Nine-owned Australian mastheads (`smh.com.au`, `theage.com.au`, etc.).
   - **Qwen:** Alibaba integration coverage appeared across $5$ separate international syndication outlets.

2. **Contrast-Week Base Rates vs. Peak-Week Sampling:**  
   Off-peak sampling (`contrast_week`) surfaces higher ambient linguistic noise than peak-week sampling. Consequently, peak-week precision cannot be assumed for contrast weeks, necessitating granular, row-by-row triage on ambiguous entities (`Apple Vision Pro`, `Apple Intelligence`, `Threads`).

3. **Domain Normalization Integrity:**  
   Standardized domain parsing strips port artifacts (e.g. `asiaone.com:443` $\to$ `asiaone.com`) to prevent artificial domain fragmentation across cluster boundaries.

4. **Entity Disambiguation Bridge:**  
   Discrepancies between parenthetical perception names (e.g., `Cursor (the AI code editor)`) and short citation strings (`Cursor`) must be reconciled via the canonical name bridge in `scripts/precedence_test_weighted.py` to prevent silent entity loss.
