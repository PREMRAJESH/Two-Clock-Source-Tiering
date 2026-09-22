# Reference Evidence & Archived Research Records

> **Directory Scope:** `reference/`  
> **Classification:** Raw Primary Scrapes, API Payloads, and Provenance Archives  
> **Integrity:** Read-Only Historical Artifacts

---

## 1. Overview & Purpose

This directory maintains immutable copies of raw API responses, schema samples, and third-party validation datasets collected during the course of the research. These files serve as the audit trail for GDELT data collection and quality-control investigations.

> [!NOTE]
> **Distinction from Other Layers:**  
> - **Not Frozen Deposits (`inputs_frozen/`):** These are not baseline model weights or frozen baseline metrics.
> - **Not Derived Outputs (`data_derived/`):** These files are raw, un-transformed JSON/CSV payloads preserved for provenance.

---

## 2. Inventory of Reference Collections

| Resource Path | Description | Methodological Role | Integrity & Storage Rules |
| :--- | :--- | :--- | :--- |
| `contrast_collection_2026-08-18/` | Archive of **22 raw GDELT ArtList JSON files** (`01_Cursor.json` to `22_Manus.json`) collected 2026-08-18. | Raw byte-level responses backing the v2 contrast-week precision audit. | **Read-only**: File names match entity alias parsers; do not rename or alter. |
| `contrast_verification_2026-08-25/` | Independent full-text verification pass (`ct_artlist_contrast_viveka_verified.csv`) containing 263 rows (67y / 196n). | Ground-truth adjudication for resolving label disagreements in the contrast triage pass. | **Read-only**: Audit verification record. |
| `gdelt_artlist_sample_response.json` | Captured GDELT API payload envelope. | Architectural schema reference for parser development and API stability verification. | **Read-only**: Schema reference. |

---

## 3. Operational Protocols

1. **Working Directory Conventions:**  
   Procedures such as `scripts/ct_artlist_audit.py` ingest raw JSON responses directly from their active working context. Do not link analytical pipeline scripts directly to `reference/` paths.
2. **Timestamp Integrity:**  
   The `seendate` fields inside raw GDELT JSON envelopes are preserved in their native UTC string format (`YYYYMMDDTHHMMSSZ`) without synthetic normalization.

---

## 4. Licensing & Attribution

All archived data in this directory is released under the Creative Commons Attribution 4.0 International license (**CC-BY-4.0**), maintaining full attribution to the underlying Two-Clock Model project (Zenodo DOI [10.5281/zenodo.21532575](https://doi.org/10.5281/zenodo.21532575)).