# The Two-Clock Model: Structural Presence and AI Perception of Technology Entities

**Dataset and analysis code**

## Cite as

> Mohan Das, V. (2026). *The Two-Clock Model: Structural Presence and AI Perception
> of Technology Entities* [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.21532575


**Author:** Viveka Mohan Das — AISearch Global, Sydney, Australia
**Version:** v1 (frozen 2026-07-08) · **Released:** July 2026 · **License:** see below

---

## Abstract

A structural answer engine optimization (AEO) score measures whether a website is
machine-readable. It does not measure whether AI platforms have updated what they
know and cite about the entity behind that website. The **two-clock model** treats
structural presence **S(t)** and AI perception **P(t)** as the same underlying
construct — how established an entity is — measured from two viewpoints that move at
different speeds. The perception gap **G(t) = S(t) − P(t)** is predicted to be largest
at birth and to close as third-party citation accumulates.

This deposit contains the frozen data and code behind the empirical panel: fifty
technology entities launched between January 2023 and March 2025. AI perception is
reconstructed with a model-cutoff natural experiment over dated OpenAI snapshots;
archived homepage snapshots measure structural presence; weekly GDELT news mentions
provide a citation series **C(t)**.

Headline findings in the paper: the birth gap is universal in this panel (structure
≈64.2% of maximum at birth vs. perception ≈0.5%; mean gap 63.6 pp, zero
counter-examples); citation precision is bimodal (distinctive names exceed 70%
precision, common-word names collapse); and citation ramps precede perception onsets
in 28 of 33 entities (85%; median lead 83 days; two-sided exact sign test
p = 6.6 × 10⁻⁵).

---

## Files in this deposit

### Frozen data

| File | Rows | What it is |
|---|---|---|
| `ct_results_v1_frozen.csv` | 6,570 | **Citation clock C(t).** Weekly GDELT news-mention counts per entity, indexed to days from birth. Columns: `entity, birth_date, week_start, days_from_birth, mention_count, metric, query_used, status, as_of, ct_precision`. `as_of = 2026-07-08`. `ct_precision` carries the per-entity audit verdict (PASS / FAIL / NOT_AUDITED). |
| `pt_pilot_results.csv` | 250 | **Perception clock P(t) — pilot.** One row per entity × dated OpenAI snapshot (50 entities × 5 snapshots). Each answer (browsing OFF) is judged 0–4 against ground truth by an LLM judge. Columns: `entity, birth_date, provider, model, reported_cutoff, score, justification, answer`. |
| `st_results.csv` | 250 | **Structure clock S(t).** Archived-homepage snapshots at several offsets from birth, scored on machine-readability components. Columns: `entity, birth_date, url, offset_days, target_date, snapshot_timestamp, S_t, title, h1, meta_description, json_ld, schema_org_type, open_graph, social_links, content_depth, word_count, status, snapshot_url`. |
| `ct_artlist_precision.csv` | 22 | **Citation precision audit.** Per-entity PASS/FAIL verdict from hand-labelling GDELT article lists (566 articles labelled in total). Columns: `entity, relevant_y, relevant_n, excluded, precision_pct, verdict`. 12 entities PASS (high-confidence citation series); the rest FAIL (common-word name collapse). |
| `entities.py` | 50 entities | **Entity roster.** Name, `birth_date`, `date_precision`, `category` (startup / model / product / oss), optional `flag` (e.g. `self_ref_openai`), and a `ground_truth` description used to score P(t). |

### Code

| File | What it does |
|---|---|
| `ct_harvester.py` | Citation harvester — **source of truth for the entity queries** used to build C(t) from GDELT. |
| `pt_pilot.py` | Perception-clock collection: probes the dated model ladder and scores answers 0–4. |
| `st_harvester.py` | Structure-score harvester: pulls archived homepages and computes S(t). |

---

## Method in brief

- **P(t) — model-cutoff natural experiment.** For each entity, a ladder of dated model
  snapshots (browsing OFF) is asked to describe the entity; each answer is scored 0–4
  against the roster's `ground_truth` by an LLM judge. Plotting score against each
  model's knowledge-cutoff date reconstructs perception at frozen moments.
- **S(t) — archived structure.** Homepage snapshots from the Wayback Machine at offsets
  from birth are scored on machine-readability components (title, H1, meta description,
  JSON-LD, schema.org type, Open Graph, social links, content depth).
- **C(t) — citation series.** Weekly GDELT news-mention counts per entity, indexed to
  days from birth, filtered by the queries in `ct_harvester.py`.

## Limitations

1. **P(t) is a single-run pilot.** AI-search answers are known to vary run-to-run, so
   the perception series should be read as a pilot measurement, not a stabilised
   estimate. (See the paper's Limitation 2.)
2. **Citation precision is bimodal.** Entity-mention counts are only reliable where the
   name is distinctive. Use `ct_precision` / `ct_artlist_precision.csv`: treat **PASS**
   entities as high-confidence citation series and interpret FAIL entities with caution.
3. **Frozen snapshot.** All data and analysis are frozen against **dataset v1 as of
   2026-07-08**. Re-running the harvesters later will not reproduce these exact numbers
   (GDELT, archives, and model snapshots all move).

## License

Suggested: **CC-BY-4.0** for the data files and **MIT** for the code. Set the license
on the Zenodo record before publishing; change these defaults if your venue or
institution requires otherwise.

## Declarations

**Author contributions (CRediT).** Viveka Mohan Das — conceptualization (the two-clock
model and the perception-gap framing G(t) = S(t) − P(t)); methodology; investigation
(all literature and background searches, conducted and synthesised manually by the
author); formal analysis; data curation; software (direction and review); and writing —
original draft and review & editing. Single author; sole responsibility for all content.

**Competing interests.** The author is the founder of AISearch Global, a consultancy
that provides answer engine optimization (AEO / GEO) services. This paper concerns
AEO/GEO. The interest is disclosed here; it did not affect the frozen data or the
reported results.

**Funding.** This research received no specific grant from any funding agency in the
public, commercial, or not-for-profit sectors.

**Declaration of generative-AI use.** The two-clock concept and all literature searches
are the author's own manual work. Generative AI was used in two distinct capacities,
both reviewed by the author, who takes full responsibility for the outputs:

- *As the object and instrument of measurement (intrinsic to the method).* P(t) is
  reconstructed from five dated OpenAI model snapshots — `gpt-4-0613`,
  `gpt-4o-2024-05-13`, `gpt-4o-2024-11-20`, `gpt-4.1-2025-04-14`, and `gpt-5.2`
  (probed with browsing off). Each answer was scored 0–4 against author-written ground
  truth by an LLM judge (`gpt-4o-2024-11-20`). The collection code also supports an
  Anthropic probe ladder, which was not used in the frozen v1 series.
- *As a coding and drafting assistant.* AI assistants helped implement and refactor the
  data-collection and analysis scripts (`ct_harvester.py`, `pt_pilot.py`,
  `st_harvester.py`) and helped draft and copy-edit documentation. No finding, number,
  or citation was accepted without author verification against the frozen source data.

## Contact

Viveka Mohan Das · AISearch Global, Sydney · viveka@aisearch.global
