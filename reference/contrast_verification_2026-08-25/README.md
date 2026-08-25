# Contrast-Week Article Sample — Two-Clock Validation

## What this is

A second, contrast-week article sample for the 22 overridden entities (the entities whose GDELT query needed disambiguation beyond an exact-name match). This is additive to the original frozen peak-week audit (`ct_artlist_audit.csv`) — that file is untouched.

**contrast_week** is defined as a week at least 4 weeks away from each entity's `peak_week`, chosen deterministically (seeded on the entity name plus a fixed version tag — not on the date it happens to be run, and not on row order). Full rule is documented in `ct_artlist_audit.py`'s `contrast_week()` / `windows_for_v2()`.

## Contents

- **`ct_artlist_contrast.csv`** — 263 articles across the 22 entities. Columns: `entity, query, sample_window, seendate, title, domain, url, relevant, note`.
- **`raw_gdelt_fetches/`** — the 22 raw GDELT ArtList JSON responses this CSV was built from, one file per entity (named by entity).

## Labelling method

Every row has a `relevant` column (y/n):

1. **Primary pass (all 263 rows):** title-based review — marked `y` if the entity's name or an unambiguous synonym appears in the title, or the headline's topic is inseparable from the entity (e.g. a story specifically about that product's launch/lawsuit/feature). Conservative by design.
2. **Verification pass (28 rows where the title alone couldn't establish relevance):** the full article text was checked directly for each. Where a page couldn't be accessed, the verdict is based on topic/title plus a corroborating source search — these cases are noted individually in the `note` column.

**Result: 67/263 marked `y`, 196/263 marked `n`.**

## Notable finding — Operator query precision

Of the ~25 contrast-week articles returned by the Operator query (`"Operator" (OpenAI OR ChatGPT OR agent)`), only **3** actually discuss OpenAI's Operator product once checked against full article text — the rest are homonym/unrelated noise (Opera browser stories, "operator" used generically, OpenAI-the-company news that isn't about the Operator product specifically). This held up under full-text verification, not just title matching, so it looks like a real precision issue with that query rather than a labelling artifact. Worth a look if the query gets revisited.

Mamba and vLLM's flagged rows both resolved with genuine hits on verification (IBM Granite 4.0 for Mamba; a Red Hat press release for vLLM).

## Caveat

The 235 rows outside the 28 verified above are still a title-only review — solid and conservative, but not a full-text read-through. Treat this file as a first-pass draft at the same tier as it currently stands, not the same rigor as the original 566-row hand-labelled peak-week audit, unless/until a full-text pass is done on the rest too.
