# GDELT Contrast-Week Audit Archive

Archive of the **22 raw GDELT ArtList JSON responses** collected for the v2
**contrast-week precision/query audit** of the 22 collision-prone entities.

---

## What was collected

- **22 GDELT ArtList JSON response files**, one per audited entity
  (`01_Cursor.json` … `22_Manus.json`), collected **2026-08-18**.
- Each file is a raw GDELT ArtList response envelope: `{"articles": [...]}`.
  The responses carry **no `query_details` field** — GDELT does not echo the
  query — so entity attribution is **filename-based** (see "File → entity
  mapping" below).
- Article counts per file are recorded in the inventory below (counted from
  the archived files). These are the raw responses as retrieved; no article
  content has been modified.

## Why it was collected

The 22 entities have **collision-prone names** (e.g. `Threads`, `Grok`,
`Gemini`, `Operator`) for which the GDELT query may return off-topic
articles. A **deterministic second week** — the v2 `contrast_week` — is
selected per entity (seeded on entity name + a fixed version tag, minimum
4-week gap from the peak week; see `../scripts/ct_artlist_audit.py` and the
decision record in `../docs/session_log.md`, 2026-08-18) and its articles
are collected so that **query precision can be audited** — i.e. whether the
entity's query returns on-topic articles.

The v2 `contrast_week` is the documented replacement for the original
`other_week` rule, which was retired as **unrecoverable** (the original pull
parameters no longer exist and the rule was not reproducible).

## What this collection is NOT

- **Not the primary analytical dataset.** These are archived `contrast_week`
  ArtList responses used for the **precision/query audit**.
- **Not the `peak_week` analytical sample.** The analytical source evidence
  is the single highest-mention week per entity (`peak_week`), per the
  lane-sampling methodology decision.
- **Not the weighted citation series.** These responses alone do not
  constitute C_weighted(t); they never enter the tier map or the weighted
  counts. The audit output derived from them (`../data_derived/ct_artlist_contrast.csv`)
  is audit/validation data only.

In short: **`contrast_week` is an audit sample, not an analytical sample.**

## Why the raw responses are preserved

- **Reproducibility of the audit.** Re-running the offline ingest
  (`ct_artlist_audit.py --contrast`) on these exact bytes reproduces the
  same `ct_artlist_contrast.csv` rows.
- **Auditability.** A reviewer can re-inspect what GDELT actually returned
  for each entity's contrast week, independently of any later processing.
- **Rawness.** These files are archived **as collected** and should be
  preserved unchanged. Renaming or re-saving a file would change the
  re-ingest result, because entity matching is filename-based.

## File → entity mapping

The files are numbered in the original generation order (matching the
`QUERY_OVERRIDES` roster order used to generate the URLs). The entity names
below are the canonical names as recorded in the derived audit batch
(`../data_derived/ct_artlist_contrast.csv`).

| # | Archived file | Entity | Articles in archive | Research role |
|---|---|---|---|---|
| 1 | `01_Cursor.json` | Cursor | 18 | contrast-week precision audit |
| 2 | `02_Apple_Vision_Pro.json` | Apple Vision Pro | 25 | contrast-week precision audit |
| 3 | `03_vLLM.json` | vLLM | 2 | contrast-week precision audit |
| 4 | `04_Threads.json` | Threads | 25 | contrast-week precision audit |
| 5 | `05_xAI.json` | xAI | 25 | contrast-week precision audit |
| 6 | `06_Qwen.json` | Qwen | 25 | contrast-week precision audit |
| 7 | `07_Ideogram.json` | Ideogram | 2 | contrast-week precision audit |
| 8 | `08_Kimi.json` | Kimi | 2 | contrast-week precision audit |
| 9 | `09_Grok.json` | Grok | 25 | contrast-week precision audit |
| 10 | `10_Mamba.json` | Mamba | 1 | contrast-week precision audit |
| 11 | `11_Gemini.json` | Gemini (Google model) | 25 | contrast-week precision audit |
| 12 | `12_Liquid_AI.json` | Liquid AI | 2 | contrast-week precision audit |
| 13 | `13_Suno.json` | Suno | 3 | contrast-week precision audit |
| 14 | `14_Sora.json` | Sora | 10 | contrast-week precision audit |
| 15 | `15_DBRX.json` | DBRX | 1 | contrast-week precision audit |
| 16 | `16_Udio.json` | Udio | 9 | contrast-week precision audit |
| 17 | `17_Apple_Intelligence.json` | Apple Intelligence | 25 | contrast-week precision audit |
| 18 | `18_Dream_Machine.json` | Dream Machine | 5 | contrast-week precision audit |
| 19 | `19_Windsurf.json` | Windsurf | 1 | contrast-week precision audit |
| 20 | `20_Lovable.json` | Lovable | 5 | contrast-week precision audit |
| 21 | `21_Operator.json` | Operator | 25 | contrast-week precision audit |
| 22 | `22_Manus.json` | Manus | 2 | contrast-week precision audit |

**Total:** 263 articles across the 22 files (counted from the archived
files, 2026-08-18). This matches the 263 rows ingested into
`../data_derived/ct_artlist_contrast.csv` (commit `cd47959`).

## How the ingest maps files to entities

`ct_artlist_audit.py` maps each filename to an entity through
`FILENAME_ALIASES` and the `_filename_entity` parser, which strips leading
digits (numbered-archive prefixes like `01_`) and converts underscores to
spaces before alias lookup (e.g. `01_Cursor.json` → `Cursor`,
`02_Apple_Vision_Pro.json` → `Apple Vision Pro`). This matching fix is what
allowed all 22 archived files to re-ingest correctly (documented in
`../docs/session_log.md`, 2026-08-18).

## Re-running the ingest

From `scripts/`, with the JSONs present in the working directory:

```
cd scripts
..\..\.venv\Scripts\python.exe ct_artlist_audit.py --contrast
```

The ingest is offline and deterministic: the same JSONs produce the same
rows.

## Provenance notes

- Collection date and method (2026-08-18; one GDELT ArtList URL per entity,
  ~9 minutes at 25 s spacing) are recorded in `../docs/session_log.md`.
- No API metadata beyond what GDELT returned is asserted here; the raw
  responses are the record.
- Preserve these files as collected. Do not edit, re-save, or rename them.