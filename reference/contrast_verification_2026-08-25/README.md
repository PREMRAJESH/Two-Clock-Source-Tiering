# Contrast-Week Article Sample & Independent Verification

> **Collection Scope:** 22 Ambiguous Query Entities  
> **Methodological Role:** Query Disambiguation & Full-Text Precision Validation  
> **Sampling Protocol:** Deterministic Off-Peak ($4+$ weeks offset from $\text{peak\_week}$)

---

## 1. Objective & Context

This dataset comprises an independent full-text verification pass of the second-week (`contrast_week`) sample across the 22 entities requiring query disambiguation. It functions as an empirical audit layer additive to the baseline peak-week audit (`ct_artlist_audit.csv`), which remains untouched in `inputs_frozen/`.

The `contrast_week` is derived deterministically via `scripts/ct_artlist_audit.py` using entity-name string hashing and a fixed random seed (`20260708`) with a minimum 4-week separation from each entity's peak mention week.

---

## 2. Dataset Inventory

* **`ct_artlist_contrast_viveka_verified.csv`**: Complete record of 263 articles across the 22 audited entities.
  - **Schema:** `entity, query, sample_window, seendate, title, domain, url, relevant, note`
  - **Classification Verdicts:** 67 Verified Affirmative (`y`), 196 Verified Negative (`n`)

---

## 3. Two-Tier Verification Methodology

Every article record underwent a structured evaluation:

1. **Tier 1 (Primary Title-Based Pass — All 263 Rows):**  
   Evaluated conservatively based on title semantics. A record was labeled affirmative (`y`) if the exact entity name or unambiguous synonym was present, or if the headline was inextricably linked to the entity's core launch, product event, or corporate action.
2. **Tier 2 (Full-Text Deep Audit — 28 Ambiguous Rows):**  
   For rows where headline semantics were insufficient, full web article contents were reviewed directly. For archived or inaccessible URLs, corroborating secondary coverage and Wayback captures were checked, with specific rationale recorded in the `note` field.

---

## 4. Key Empirical Findings

* **OpenAI Operator Precision Degradation:**  
  Within the contrast-week query sample for Operator (`"Operator" (OpenAI OR ChatGPT OR agent)`), full-text verification established that only **3 of ~25 articles** pertained to OpenAI's Operator product. The remaining ~22 items represented generic terminology ("phone operator", "tour operator") or Opera browser coverage.
* **Resolutions for Mamba & vLLM:**  
  Ambiguous hits for Mamba and vLLM were verified as authentic domain hits (e.g., IBM Granite 4.0 architecture discussions for Mamba; Red Hat infrastructure press releases for vLLM).

---

## 5. Scope & Caveats

> [!NOTE]
> **Audit Confidence Level:**  
> While the 28 ambiguous rows received full-text manual verification, the remaining 235 rows rely on conservative headline matching. This dataset provides a robust validation audit for disambiguation queries, but remains categorized as an off-peak precision audit rather than primary analytical evidence.
