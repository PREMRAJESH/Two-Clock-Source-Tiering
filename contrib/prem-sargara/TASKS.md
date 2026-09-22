# Prem Sargara - Contributor Workspace & Tasks

This directory is designated for contributions, workspace files, and task tracking for **prem-sargara**.

## Subfolders & Modules

- **Subfolder**: `[UNSET]`
  <!-- TODO: Add subfolder location here once prem-sargara confirms her preferred folder name. Do not guess or auto-assign a folder name. -->

## Tasks & Progress

**Contribution:** Citation Source-Tiering / Weighting Analysis  
**As of:** 2026-08-22

---

### Tasks Completed So Far

- [x] Repo scaffolded, licensed, cleanly separated (frozen inputs / scripts / derived outputs / docs)
- [x] Baseline paper result (28/33, median lead 83 days, p=6.62×10⁻⁵) independently reproduced and verified in the real pipeline, not just a standalone checker
- [x] `self_ref_openai` exclusion bug found and fixed (would have silently broken the baseline)
- [x] PT↔CT entity name mismatch (14 entities) found and fixed with a name bridge
- [x] `other_week` mismatch investigated, root-caused (original rule unrecoverable), resolved with a new deterministic `contrast_week` v2 method
- [x] Domain-normalization `:port` bug found via QA and fixed (`asiaone.com:443` vs `asiaone.com`)
- [x] Peak-week-only analytical sampling policy decided and enforced in code (guardrail tested)
- [x] Project-local `.venv` policy adopted (stopped touching the global Python install)
- [x] `data_derived/` tracking policy decided (ignore by default, deliberate milestone commits)
- [x] 22-entity contrast-week audit fully collected (22/22, 263 rows) and archived
- [x] Model-retirement facts verified against primary sources (gpt-4.1 safe, gpt-4-0613 / gpt-4o-2024-05-13 retiring Oct 23)
- [x] 27 AMBER precision-audit rows reviewed (16 y, 5 n, 6 unverifiable pending Wayback check)
- [x] Non-English contrast rows flagged (31/263), pending final reconciliation of the count

---

### Task List — Remaining Work

#### Part A — Fully in your hands

- [x] **Task 1:** Fix `VIVEKA_COL_MAP` in `merge_source_data.py` to match her real Label-sheet columns
- [x] **Task 2:** Reconcile the non-English contrast-row count (31 flagged — confirm genuine vs. false-positive vs. still-uncertain breakdown)
- [x] **Task 3:** Triage the 263-row contrast batch — clear unambiguous rows yourself, leave only genuinely uncertain ones for Viveka
- [x] **Task 4:** Mark `verify_week_match.py` as superseded
- [x] **Task 5:** Run Wayback Machine check (your own browser) on the 6 unverifiable AMBER rows
- [x] **Task 6:** Run `test_pipeline_smoketest.py` to confirm pipeline is still green
- [x] **Task 7:** Self-generate `viveka_labeled_export.csv` from her Label sheet (flag this choice to her — see Task 13)
- [x] **Task 8:** Dry-run the full pipeline on Lane A data alone (preliminary, validates real column layout)
- [ ] **Task 9:** Run Lane B harvest (~28-30 remaining entities) once GDELT rate limit clears
- [ ] **Task 10:** Run the full analytical pipeline for real once both lanes have data (merge → tier map → weights → precedence test → sensitivity analysis)
- [ ] **Task 11:** Fill in `tier_methodology.md` for real — tier definitions, evidence, weight rationale, actual weighted-vs-raw result

#### Part B — Needs Viveka (source-tiering track)

- [x] **Task 12:** Her review/sign-off on the CSV-vs-master discrepancy and the 5 Kimi y→n overrides
- [x] **Task 13:** Her sign-off on self-generating her export file rather than waiting for her hand-export
- [x] **Task 14:** Her final calls on the genuinely ambiguous non-English contrast rows
- [x] **Task 15:** Her confirmation of the final `ALREADY_COVERED` entity list before Lane B counts as final

#### Part C — Entirely hers (P(t) / perception track)

- [x] **Task 16:** Two independent P(t) reruns before Oct 23, 2026 (hard deadline)
- [x] **Task 17:** Her round-2 scoring pass on the 50 entities
- [x] **Task 18:** Decide on the 3×-repeat-per-cutoff stability check (optional, her call)
- [ ] **Task 19:** Resolve the SSRN publishing-rights question

#### Part D — PRS other pending commitment

- [ ] **Task 20:** Round 3 validation pass (location-based search-result distortion check), after her round 2 lands

#### Part E — Joint, late-stage (before publication)

- [ ] **Task 21:** Write results into the paper draft (weighted-vs-raw comparison, tier methodology section, syndication caveat)
- [ ] **Task 22:** Update Declarations / CRediT section for your contribution and authorship
- [ ] **Task 23:** Update Generative AI use disclosure to cover your side's AI-agent usage
- [ ] **Task 24:** Full stress-test read-through of the whole paper
- [ ] **Task 25:** Decide submission venue / update Zenodo deposit versioning
- [ ] **Task 26:** Final proofread and formatting pass

