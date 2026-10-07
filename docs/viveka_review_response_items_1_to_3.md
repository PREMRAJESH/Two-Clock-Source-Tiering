# Methodological Audit: Response to Review Items 1–3

**To:** Viveka Mohan Das (AISearch Global)  
**From:** Prem Sargara  
**Date:** October 5, 2026  
**Subject:** Technical Audit and Verification of Items 1–3 (Peak-Week Truncation & Weighted Ramp Dynamics)  
**Accompanying File:** `data_derived/ct_results_weighted.csv`  

---

### Executive Summary

Viveka's observation in **"CHECK THIS FIRST"** is completely correct and uncovers a fundamental flaw in the construction of `ct_results_weighted.csv`. 

Because article-level domain data was harvested **only for each entity's peak citation week** (originally adopted in `merge_source_data.py` to manage GDELT API rate limits), the longitudinal weighting script (`scripts/apply_weights.py`) filled all other 130 weeks of each entity's 131-week timeline with `0.0`. 

Consequently:
1. Every entity's weighted citation time series is a **single-week impulse function** supported solely at the peak week.
2. The operational ramp condition ($C(t) \ge \max(0.10 \cdot \text{Peak}, 3)$) is trivially satisfied at that single non-zero week, so the detected "weighted ramp date" is identically the **peak citation week** ($t_{\text{ramp, weighted}} \equiv t_{\text{peak}}$).
3. The reported lead time $\Delta t_{\text{weighted}} = t_{\text{onset}} - t_{\text{ramp, weighted}}$ is actually measuring **$t_{\text{onset}} - t_{\text{peak}}$**, which is negative for mature models whose perception onset predates late-stage peak media buzz.
4. The collapse from 28/33 (+83 days) to 13/33 (−51 days) is **not** an effect of source-tier weighting. It occurs identically under unweighted equal weights $W = (1, 1, 1)$, under Tier 1 only, and across all 16 cells of the weight sensitivity grid.

Below are the detailed, audited answers to questions 1, 2, and 3, accompanied by mathematical derivations and code assertions.

---

### Item 1: Nonzero Counts in Other Weeks & Handling of Unharvested Weeks

> **Reviewer Question 1:**  
> *Does `ct_results_weighted.csv` have nonzero weighted counts in weeks other than the peak week? How are weeks with no harvested articles weighted?*

#### 1. Nonzero Count Audit
**No.** `ct_results_weighted.csv` has **zero** weighted counts in every week other than the peak week.

Across all 50 entities $\times$ 131 weeks = 6,570 entity-week records in `ct_results_weighted.csv`:
- **Total entity-weeks in dataset:** 6,570
- **Entity-weeks with nonzero raw mentions (`mention_count > 0`):** 5,102 (distributed across the full timeline)
- **Entity-weeks with nonzero weighted counts (`weighted_count > 0`):** **Exactly 50** (exactly 1 week per entity)
- **Entity-weeks with nonzero tier counts (`tier1_count > 0` or `all_tier_count > 0`):** **Exactly 50** (exactly 1 week per entity)

Distribution of nonzero weeks per entity in `ct_results_weighted.csv`:
$$\text{Distribution: } \{1 \text{ nonzero week}: 50 \text{ entities}, \text{any other count}: 0\}$$

#### 2. How Weeks with No Harvested Articles are Handled
In `scripts/apply_weights.py` (lines 197–227):
```python
def build_output(weighted_agg, frozen_counts):
    rows = []
    for entity in sorted(frozen_counts):
        for week in sorted(frozen_counts[entity]):
            fc = frozen_counts[entity][week]
            key = (entity, week)
            wa = weighted_agg.get(key, {})

            rows.append({
                "entity": entity,
                "birth_date": fc["birth_date"],
                "week_start": week,
                "days_from_birth": fc["days_from_birth"],
                "mention_count": fc["mention_count"],
                "weighted_count": round(wa.get("weighted_count", 0.0), 4),
                "tier1_count": wa.get("tier1_count", 0),
                "tier12_count": wa.get("tier12_count", 0),
                "all_tier_count": wa.get("all_tier_count", 0),
                ...
            })
    return rows
```
Because `ct_source_all.csv` contains articles harvested *only* for the single peak citation week per entity, `weighted_agg[(entity, week)]` does not exist for the other ~130 weeks. The code defaults missing weeks to `0.0`. 

Weeks without harvested articles are **not weighted or imputed**; they are strictly zeroed out.

---

### Item 2: Weights of (1, 1, 1) and Reproduction of Raw Series

> **Reviewer Question 2:**  
> *Do weights of (1, 1, 1) reproduce the raw series exactly? Please add this check to `reproduce_baseline.py`.*

#### 1. Direct Answer
**No.** Weights of $(1, 1, 1)$ do **not** reproduce the raw series. In fact, they produce the exact same collapsed result as the weighted pipeline (13/33, −51 days, $p = 0.296$).

#### 2. Code Implementation in `scripts/reproduce_baseline.py`
We added `check_weights_111_equivalence()` directly into `scripts/reproduce_baseline.py`. When executing `python scripts/reproduce_baseline.py`, the following output is now produced:

```text
------------------------------------------------------------------------
  WEIGHTS (1, 1, 1) REPRODUCTION CHECK (Review Item 2)
------------------------------------------------------------------------
  Total entity-weeks in dataset:        6570
  Weeks with nonzero raw mentions:       5102 (full longitudinal timeline)
  Weeks with nonzero harvested articles: 50 (exactly 1 peak week per entity)
  Entity-week count mismatches:         5077/6570 (77.3%)

  Testable entities evaluated:          33
  Entities where (1,1,1) ramp = raw ramp: 11/33 (33.3%)
  Entities where (1,1,1) ramp != raw:     22/33 (66.7%)

  Raw baseline precedence:              28/33 (84.8%), median lead: +83d
  (1, 1, 1) weighted precedence:        13/33 (39.4%), median lead: -51d, p = 0.296

  VERDICT: FAIL
  Weights of (1, 1, 1) do NOT reproduce the raw series.
  ROOT CAUSE:
    Domain data was harvested ONLY for each entity's single peak citation week.
    All other 130 weeks are filled with 0.0. Therefore, any weighting scheme
    (including (1,1,1)) reduces each entity's citation timeline to a single-week
    impulse at the peak week. The 'weighted ramp' is identically the peak week,
    converting the analysis into 'peak week vs. perception onset'.
========================================================================
```

#### 3. Why 11 Entities Matched
The 11 entities where $(1, 1, 1)$ ramp matched the raw ramp (e.g., AlphaFold 3, Apple Vision Pro, Devin AI, GPT-4, GPT-4o, Threads) are entities whose public announcement generated an immediate viral surge where the **peak week coincided with the initial launch week**. For the remaining 22 entities (e.g., Cursor, ElevenLabs, Claude 3, Ollama, xAI), the raw ramp was triggered early, but the peak week occurred hundreds of days later. Truncating the series to the peak week forced their ramps to move forward in time by hundreds of days.

---

### Item 3: Invariance Across All 16 Weight Sweep Cells

> **Reviewer Question 3:**  
> *Why do Tier 2 and Tier 3 weights from 0 to 1 change nothing, in all 16 cells? That does not fit the claim that the early signal sits in lower tiers.*

#### 1. Mathematical Explanation
Let entity $e$ have citation timeline $C_e(t)$ over weeks $t \in \{t_1, \dots, t_T\}$. In `ct_results_weighted.csv`, let $t_{\text{peak}}$ denote the single harvested peak week.

For any weight vector $\mathbf{w} = (w_1, w_2, w_3) \in [0, 1]^3$:
$$C_{\text{weighted}, e}(t) = \begin{cases} 
\sum_{k=1}^3 w_k \cdot N_{k, e}(t_{\text{peak}}), & \text{if } t = t_{\text{peak}} \\
0, & \text{if } t \ne t_{\text{peak}}
\end{cases}$$

Let $W_{\text{peak}} = \sum_{k=1}^3 w_k \cdot N_{k, e}(t_{\text{peak}})$. The maximum volume of the series is:
$$\text{Peak}(C_{\text{weighted}, e}) = W_{\text{peak}}$$

The ramp detection function `find_ramp_date()` seeks the earliest week $t$ satisfying:
$$C_{\text{weighted}, e}(t) \ge \max(\theta_{\text{ramp}} \cdot \text{Peak}, \text{Floor}) = \max(0.10 \cdot W_{\text{peak}}, 3)$$

- For any week $t \ne t_{\text{peak}}$: $C_{\text{weighted}, e}(t) = 0 < 3$, so no unharvested week can ever qualify.
- For $t = t_{\text{peak}}$: since $\theta_{\text{ramp}} = 0.10 \le 1.0$, the inequality $W_{\text{peak}} \ge 0.10 \cdot W_{\text{peak}}$ is a mathematical tautology.
- Therefore, as long as $W_{\text{peak}} \ge 3$ (which holds across all evaluated testable entities because peak weeks have tens to hundreds of articles), the condition is **always and only satisfied at $t_{\text{peak}}$**.

#### 2. Substantive Consequence
Varying $w_2 \in \{0.25, 0.50, 0.75, 1.00\}$ and $w_3 \in \{0.00, 0.10, 0.25, 0.50\}$ scales the scalar value $W_{\text{peak}}$, but **cannot shift the ramp week**, because there is literally no other candidate week in the array. 

The identical results across all 16 cells in Table C.2 (and the binary regimes Tier 1 Only and Tier 1+2) are an **artifact of single-point time series support**, not evidence of parameter robustness or source timing dynamics.

The claim that "early citation signal sits in lower tiers" was an erroneous narrative constructed to explain an attenuation that was entirely generated by peak-week truncation.

---

### Summary of What This Means for the Paper

1. **The current paper cannot be published with its core claim:**  
   The paper currently claims that source-tier weighting attenuates the citation-precedence relationship (from 85% to 38%) and proposes the *Diffuse Ingestion Hypothesis* as an explanation. That conclusion is empirically invalid because the 38% concordance is simply **peak week vs. perception onset**, which occurs even at unweighted $(1, 1, 1)$.

2. **Immediate Step:**  
   We are not editing the manuscript text until we discuss and align on the path forward. All files and reproductions are frozen and inspectable in the repository.

3. **Possible Paths Forward:**
   - **Path A (True Longitudinal Source Weighting):** Harvest article-level domain metadata across all 131 weeks for the testable entities (or a representative sample) to construct a genuinely time-varying $C_{\text{weighted}}(t)$.
   - **Path B (Reframe as "Peak Dynamics vs. Ramp Dynamics"):** Formally reframe the study around the divergence between early ramp dates and peak citation concentration in relation to AI perception onsets.
   - **Path C (Methodological Diagnostic Paper):** Document this exact phenomenon as a methodological case study on temporal aggregation artifacts in bibliometric time series.
