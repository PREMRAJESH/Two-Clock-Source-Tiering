# Reference Evidence

This directory holds **reference and archived evidence** retained for
provenance, methodological inspection, auditability, and — where possible —
reconstruction of collection procedures.

These materials are **not frozen analytical inputs** and **not derived
outputs**. They are the raw, unprocessed record of how evidence was
collected:

| Entry | What it is | Why it is retained |
|---|---|---|
| `gdelt_artlist_sample_response.json` | A sample GDELT ArtList (browser-export) API response, captured early in the audit work. | Documents the exact response envelope the collection procedures consume; useful if GDELT's export shape changes or for inspecting the raw schema. |
| `contrast_collection_2026-08-18/` | Archive of the **22 raw GDELT ArtList JSON responses** collected on 2026-08-18 for the v2 contrast-week precision audit — one file per audit entity. | Raw-source preservation: lets the audit ingest be re-run or re-verified from the exact bytes GDELT returned. See its own [README](contrast_collection_2026-08-18/README.md). |
| `contrast_verification_2026-08-25/` | Viveka's independent full-text-verified contrast-week labeling pass: her `ct_artlist_contrast_viveka_verified.csv` (263 rows, 67y/196n) and README. | Reconciliation source for the5-label disagreements resolved in the triage; preserved as the verification evidence trail. |

## What this directory is NOT

- **Not frozen analytical inputs** — those live in `../inputs_frozen/` and
  are the immutable starting point of the analysis.
- **Not derived outputs** — those live in `../data_derived/` and are
  produced by the procedures in `../scripts/`.

## Conventions

- **Reference material, not pipeline input.** The audit ingest expects the
  raw JSONs in the working directory of `ct_artlist_audit.py` (normally
  `scripts/`), not in `reference/`. Copy from here if a re-ingest is ever
  needed; do not point the procedure at this directory.
- **Read-only.** These files are archived provenance and should not be
  edited. The raw JSONs especially — renaming or re-saving them would change
  the re-ingest result (entity matching is filename-based; see the archive's
  README).
- The archived JSON `seendate` fields are raw GDELT UTC timestamps
  (e.g. `20250317T114500Z`), not normalized.

## Licensing

Reference/archived evidence is part of the derived-and-archived data and
inherits the CC-BY-4.0 attribution requirement of the deposit
(`../LICENSE-DATA.md`).