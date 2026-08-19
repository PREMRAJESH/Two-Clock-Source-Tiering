# Frozen Research Inputs

This directory is the **fixed research input state** for the source-tiering /
weighting analysis. It contains the v1 deposit of the *Two-Clock Model*
dataset and code (frozen 2026-07-08), plus two files received from the
lead author after the deposit.

These files are the **starting point of the analysis**. Everything derived
elsewhere in this repository is computed from these inputs; nothing here is
regenerated, overwritten, or edited by the analysis.

---

## Purpose

This directory preserves the exact evidence on which the analysis is built.
It exists so that a reviewer can ask "what was the raw material, and was it
stable?" and find a single, versioned, immutable answer. Without this fixed
input state, the reproducibility of every downstream number is compromised.

## Freeze Principle

These files represent a **frozen research input state**.

**DO NOT MODIFY THESE FILES IN PLACE.**

If a new version of the deposit is ever needed, it must be added as a **new,
explicitly versioned deposit** (e.g. a separate frozen directory or a v2
snapshot) — never by silently editing files here. The freeze is recorded in
the analysis's decision log (`../docs/session_log.md`, tracking-policy entry
2026-08-18).

## Provenance

What is known about the origin and status of these files:

- The **8-file v1 deposit** (data + harvesters + roster + README) was
  authored by Viveka Mohan Das (AISearch Global, Sydney) and frozen
  **2026-07-08**. It is the version the paper's analyses are based on.
- `ct_artlist_precision.csv` and `ct_artlist_LABELING.xlsx` were received
  from the lead author **after** the deposit; they are treated as immutable
  reference inputs the same way.
- The v1 deposit is versioned externally: Zenodo DOI
  **10.5281/zenodo.21532575** (see "Cite as" below).

No other origin details are asserted beyond what the files themselves
record (`as_of = 2026-07-08` in the citation series; author and declarations
in the deposit README, preserved below).

## Inventory

| File | Evidence / role | Analytical relevance | Status |
|---|---|---|---|
| `ct_results_v1_frozen.csv` | **Citation series C(t)** — weekly GDELT news-mention counts per entity (6,570 rows), indexed to days from birth; carries the per-entity `ct_precision` verdict. `as_of = 2026-07-08`. | The raw C(t) that weighting modifies; also the source of per-entity peak weeks. | Frozen (v1) |
| `pt_pilot_results.csv` | **Perception results P(t)** — 250 probe records (50 entities × 5 dated model snapshots), each scored 0–4 against ground truth. | The perception onset series used in the precedence test. | Frozen (v1) |
| `st_results.csv` | **Structural presence results S(t)** — archived-homepage snapshots scored on machine-readability components (250 rows). | Not used by the weighting analysis; part of the deposit's three-clock evidence. | Frozen (v1) |
| `ct_artlist_precision.csv` | **Citation precision audit** — per-entity name-relevance audit for the 22 collision-prone entities (22 rows; verdicts: 12 PASS, 10 FAIL). | Defines which citation series are high-confidence (PASS) vs. interpreted with caution (FAIL); the 10 FAIL entities are excluded from the testable 33. | Received (post-deposit) |
| `ct_artlist_LABELING.xlsx` | **Lead-author's labeled article file** — per-article rows for the 22 entities (`Label` sheet: `#, entity, window, date, title, domain, url, suggested_label, relevant`; 566 rows, 517 `peak_week` + 49 `other_week`). | The `peak_week` article rows are the analytical source evidence for Lane A (22 entities). | Received (post-deposit) |
| `entities.py` | **Entity roster** — 50 entities with `name`, `birth_date`, `date_precision`, `category`, optional `flag` (incl. `self_ref_openai`), and `ground_truth` used to score P(t). | Seeds entity names, birth dates, and the exclusion-rule variant analysis. | Frozen (v1) |
| `ct_harvester.py` | **Original citation harvester** — defines the entity queries used to build C(t) from GDELT (`TimelineVolRaw` mode). | Source of truth for entity queries reused by the collection/audit procedures. | Frozen (v1) |
| `pt_pilot.py` | **Perception-clock collector** — probes the dated model ladder and scores answers 0–4. | Defines how P(t) was measured. | Frozen (v1) |
| `st_harvester.py` | **Structural presence harvester** — computes S(t) from archived homepages. | Defines how S(t) was measured. | Frozen (v1) |
| `README.md` | This file — provenance and consumption record. | Maintained. | — |

## Relationship to Analysis

These inputs enter the analysis as follows (full procedural detail in
`../scripts/README.md`):

- **Baseline reproduction** reads the citation and perception series only —
  no derived data is needed.
- **Source collection (Lane A)** reads `ct_harvester.py` (queries) and the
  citation series (peak weeks), and uses the labeled file's `peak_week`
  rows as its analytical source evidence.
- **Source collection (Lane B)** computes each entity's peak week from the
  citation series.
- **Tier construction / weighting / precedence / sensitivity** read the
  citation series, the precision audit, the entity roster, and the
  perception series.
- The **precision audit** defines the testable set: the paper's 33 testable
  entities are all 50 minus the 10 precision-FAIL and 7 no-onset entities
  (verified against paper Sections 4.5 and 5.4; see `../docs/session_log.md`,
  2026-08-17).

No analytical procedure writes into this directory.

## Immutability and Reproducibility

Changing a frozen input would silently change every derived number that
depends on it:

- Editing the citation series would shift peak weeks, tier inputs, and the
  weighted series.
- Editing the perception series would change onsets and the precedence
  verdicts.
- Editing the precision audit would change which entities are testable.

The baseline lock (`scripts/reproduce_baseline.py`) asserts the paper's
exact numbers (28/33, 83 days, 6.6 × 10⁻⁵) against these inputs and fails on
any deviation. Keeping the inputs frozen is therefore not a courtesy — it is
what makes the analysis's reproducibility claim meaningful.

## Cite as

> Mohan Das, V. (2026). *The Two-Clock Model: Structural Presence and AI
> Perception of Technology Entities* [Dataset]. Zenodo.
> https://doi.org/10.5281/zenodo.21532575

**Author:** Viveka Mohan Das — AISearch Global, Sydney, Australia
**Version:** v1 (frozen 2026-07-08) · **Released:** July 2026

## Method in brief (from the deposit)

- **P(t) — model-cutoff natural experiment.** A ladder of dated model
  snapshots (browsing OFF) is asked to describe each entity; each answer is
  scored 0–4 against the roster's `ground_truth` by an LLM judge.
- **S(t) — archived structure.** Homepage snapshots from the Wayback
  Machine at offsets from birth are scored on machine-readability
  components.
- **C(t) — citation series.** Weekly GDELT news-mention counts per entity,
  indexed to days from birth, filtered by the queries in `ct_harvester.py`.

## Limitations (from the deposit)

1. **P(t) is a single-run pilot.** AI-search answers vary run-to-run; read
   the perception series as a pilot measurement, not a stabilised estimate.
2. **Citation precision is bimodal.** Entity-mention counts are only reliable
   where the name is distinctive. Treat **PASS** entities (12 of 22 audited)
   as high-confidence citation series; interpret FAIL entities with caution.
3. **Frozen snapshot.** All data are frozen against dataset v1 (2026-07-08).
   Re-running harvesters later will not reproduce these exact numbers
   (GDELT, archives, and model snapshots all move).

## Licensing

Data files are licensed **CC-BY-4.0**; code is licensed **MIT** — see
`../LICENSE-DATA.md` and `../LICENSE-CODE.md`.

## Declarations (from the deposit)

**Author contributions (CRediT).** Viveka Mohan Das — conceptualization (the
two-clock model and the perception-gap framing G(t) = S(t) − P(t));
methodology; investigation (all literature and background searches,
conducted and synthesised manually by the author); formal analysis; data
curation; software (direction and review); and writing — original draft and
review & editing. Single author; sole responsibility for all content.

**Competing interests.** The author is the founder of AISearch Global, a
consultancy that provides answer engine optimization (AEO / GEO) services.
This paper concerns AEO/GEO. The interest is disclosed here; it did not
affect the frozen data or the reported results.

**Funding.** This research received no specific grant from any funding
agency in the public, commercial, or not-for-profit sectors.

**Declaration of generative-AI use.** The two-clock concept and all
literature searches are the author's own manual work. Generative AI was used
in two distinct capacities, both reviewed by the author, who takes full
responsibility for the outputs:

- *As the object and instrument of measurement (intrinsic to the method).*
  P(t) is reconstructed from five dated OpenAI model snapshots —
  `gpt-4-0613`, `gpt-4o-2024-05-13`, `gpt-4o-2024-11-20`,
  `gpt-4.1-2025-04-14`, and `gpt-5.2` (probed with browsing off). Each
  answer was scored 0–4 against author-written ground truth by an LLM judge
  (`gpt-4o-2024-11-20`). The collection code also supports an Anthropic
  probe ladder, which was not used in the frozen v1 series.
- *As a coding and drafting assistant.* AI assistants helped implement and
  refactor the data-collection and analysis scripts (`ct_harvester.py`,
  `pt_pilot.py`, `st_harvester.py`) and helped draft and copy-edit
  documentation. No finding, number, or citation was accepted without author
  verification against the frozen source data.

## Contact

Viveka Mohan Das · AISearch Global, Sydney · viveka@aisearch.global