# SSRN Publishing-Rights & Preprint Licensing Policy

> **Task Reference:** TASK-19 (SSRN Publishing-Rights & Preprint Licensing Policy)  
> **Associated Tasks:** TASK-22 (CRediT Authorship), TASK-25 (Target Venue Selection & Zenodo DOI)  
> **Status:** Resolved & Publication-Ready Guidance  
> **Date:** September 2026

---

## 1. Executive Summary & Core Decisions

This policy document resolves the legal, copyright, and distribution considerations for depositing the Two-Clock Model manuscript on **SSRN (Social Science Research Network)** alongside the existing **Zenodo repository** ([10.5281/zenodo.21532575](https://doi.org/10.5281/zenodo.21532575)).

| Question | Resolution | Practical Action |
| :--- | :--- | :--- |
| **Does SSRN require transfer of copyright?** | **No.** Authors retain full, exclusive copyright. SSRN receives only a non-exclusive distribution license. | Maintain standard author copyright notice on paper header. |
| **Which license should be selected on SSRN?** | **CC-BY-NC-ND 4.0** *(Recommended for paper draft)* or **CC-BY 4.0** *(Maximum Open Access)*. | Select during the SSRN e-Submission metadata step. |
| **Does posting on SSRN count as "prior publication"?** | **No.** Virtually all major academic publishers (Elsevier, Springer-Nature, ACM, IEEE, INFORMS) explicitly permit preprints. | Declare preprint existence and SSRN URL in journal submission cover letter. |
| **How does SSRN link to the Zenodo deposit?** | Direct bidirectional cross-reference. | Cite Zenodo dataset DOI in SSRN abstract; add SSRN URL to Zenodo v2 metadata. |

---

## 2. SSRN Copyright & Rights Framework

### 2.1 Author Copyright Retention
Under SSRN's Terms of Service and Author Agreement:
1. **Non-Exclusive Right to Distribute:** SSRN is granted a perpetual, non-exclusive, worldwide license to host, archive, index, and distribute the full-text working paper.
2. **Authors Retain Ownership:** The authors (**Viveka Mohan Das & Prem Sargara**) retain 100% of underlying intellectual property, copyright, and the right to submit the identical or revised manuscript to any peer-reviewed journal or conference.
3. **No Commercial Exclusivity:** SSRN does not claim commercial rights, nor does it prevent the authors from monetizing, revising, or republishing the work elsewhere.

---

## 3. Preprint Licensing Selection Matrix

SSRN allows authors to select specific Creative Commons licenses upon submission. Because the analytical code is released under **MIT** and the dataset is released under **CC-BY 4.0** on Zenodo, the manuscript preprint license can be chosen based on the target journal strategy:

| License Option | Description | Journal Compatibility | Recommended For |
| :--- | :--- | :--- | :--- |
| **CC-BY-NC-ND 4.0**<br>*(Attribution-NonCommercial-NoDerivatives)* | Anyone may read and share the PDF with attribution, but cannot sell it or create unauthorized derivative papers. | **Highest Compatibility.** Accepted by 100% of commercial and society publishers (Elsevier, Springer, IEEE, ACM, Taylor & Francis). | **Recommended Option.** Protects manuscript text while allowing free global preprint distribution. |
| **CC-BY 4.0**<br>*(Attribution)* | Anyone may read, share, adapt, and build upon the work, even commercially, provided attribution is given. | Accepted by all Gold Open Access journals (e.g., *PLOS ONE*, *Nature Communications*, *Frontiers*); accepted by most hybrid journals, but a few traditional publishers prefer NC. | Best if targeting fully open-access journals or if institutional funder mandates strict CC-BY. |
| **SSRN Default / All Rights Reserved** | Standard preprint distribution without explicit CC re-use terms. | Universally accepted by traditional journals. | Fallback if publisher has unusual restrictions. |

> [!TIP]
> **Recommendation:** Select **CC-BY-NC-ND 4.0** on SSRN for the paper manuscript.  
> This ensures that third parties cannot commercialize or modify the manuscript without permission, while preserving complete flexibility to submit to any high-impact journal later. The underlying code and dataset remain openly usable under MIT and CC-BY 4.0.

---

## 4. Journal "Prior Publication" Compliance

A frequent concern is whether an SSRN working paper disqualifies a paper from subsequent journal publication (the "Ingelfinger Rule"). 

Under modern publishing standards (COPE and SHERPA/RoMEO conventions):
1. **Preprints are Standard Practice:** Major technology, information systems, and computer science venues treat preprints as early working drafts designed to solicit feedback, not formal prior publication.
2. **Key Publisher Policies:**
   * **Elsevier:** Explicitly permits preprints on preprint servers (including SSRN, which is owned by Elsevier) at any time.
   * **Springer Nature:** Encourages posting preprints before or during formal submission.
   * **ACM & IEEE:** Permit preprints on non-commercial repositories (including SSRN and arXiv); authors update the preprint with the final DOI upon publication.
   * **INFORMS & AIS (MIS Quarterly, ISR, Management Science):** Fully support preprints; authors must disclose prior distribution in submission comments.

### Required Journal Disclosure Statement:
Upon submitting to a journal, include this standard statement in the cover letter:
> *"An earlier working paper version of this research, reporting initial empirical findings, was posted as a preprint on SSRN (SSRN ID: [INSERT]) and data deposited on Zenodo (DOI: 10.5281/zenodo.21532575). In accordance with your journal's preprint policy, this distribution is non-commercial and does not constitute prior formal publication."*

---

## 5. Integration Architecture: SSRN + Zenodo + GitHub

To maintain scientific rigor and clear provenance across platforms, the repository connects as follows:

```
[ GitHub Repository ] 
        │ (Public Release Tag / v2.0)
        ▼
[ Zenodo v2 Deposit ] ──(DOI: 10.5281/zenodo.21532575)
        ▲
        │ Cross-links dataset DOI & scripts
        ▼
[ SSRN Working Paper ] ──(Paper Abstract & PDF)
```

1. **In the SSRN Manuscript / Abstract:**
   * Include the standard Data & Code Availability statement:  
     *"All reproducible data pipelines, classification scripts, and frozen empirical datasets are permanently archived on Zenodo (DOI: [10.5281/zenodo.21532575](https://doi.org/10.5281/zenodo.21532575)) and GitHub."*
2. **In the Zenodo Deposit:**
   * When publishing the v2 version of the Zenodo deposit (following Task 10/11 production run), include the SSRN paper URL under "Related identifiers" as `IsSupplementTo`.

---

## 6. Actionable Submission Checklist for Viveka

When uploading the manuscript to SSRN:
- [ ] **Paper Title:** *"The Two-Clock Model: Structural Presence, Citation Ramps, and AI Perception of Technology Entities"*
- [ ] **Author Line:** Viveka Mohan Das & Prem Sargara
- [ ] **Affiliations & Disclosures:** Include declarations from [`docs/declarations_and_credit.md`](declarations_and_credit.md)
- [ ] **License Selected:** Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (**CC-BY-NC-ND 4.0**)
- [ ] **SSRN e-Library Networks:** 
  * Information Systems & eBusiness Network (ISN)
  * Economics Research Network (ERN) / Innovation & Technology Management
  * Artificial Intelligence & Machine Learning Subject Matter e-Journal
- [ ] **Cross-link:** Paste Zenodo DOI `10.5281/zenodo.21532575` in the abstract.
