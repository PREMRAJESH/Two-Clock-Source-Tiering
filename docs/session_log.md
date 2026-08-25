# Session log

Dated notes on decisions made and why — matches the convention already
used for date-verification in `inputs_frozen/entities.py`.

## 2026-08-15

- Read through the v1 deposit (README, entities.py, ct_harvester.py,
  ct_results_v1_frozen.csv, ct_artlist_precision.csv, st_harvester.py,
  st_results.csv).
- Found: `ct_results_v1_frozen.csv` has no per-source/domain field —
  only aggregate weekly `mention_count` from GDELT `TimelineVolRaw`
  mode. Source-tier weighting can't be computed against it as-is.
- Found: `ct_artlist_precision.csv` audits entity-name relevance
  (disambiguation), not source authority — different construct from
  what's needed for tiering. Flagged so it isn't mistaken for the
  evidence base for tier boundaries.
- Asked Viveka whether an older article-level GDELT pull with sources
  still exists.
- Built `scripts/ct_source_harvester.py` as a fallback/parallel path —
  pulls per-article domains via GDELT ArtList mode. Not yet run against
  live GDELT.

## 2026-08-16 (cont.)

- Viveka built her own harvester, `ct_artlist_harvester.py` (outputs
  `ct_artlist_results.csv`), separate from the one built in this repo.
  Run location: same folder as `ct_harvester.py` and
  `ct_results_v1_frozen.csv`.
- **Discrepancy flagged, not yet resolved:** her script's week-selection
  logic is "guessed... median-count week" per her own message — this is
  DIFFERENT from the "max mention_count week" (true peak) logic used in
  this repo's `scripts/ct_source_harvester.py`. These will pick
  different weeks for most entities. Do not treat them as interchangeable
  until the spot-check below resolves which one matches her existing
  labeled data.
- Action before anything else on source-weighting proceeds: run her
  script, then compare its `other_week` output for Kimi and Mamba
  (both already in `ct_artlist_LABELING.xlsx`) against the week already
  recorded there. Match -> standardize on her median-week method going
  forward and update this repo's harvester to match. Mismatch -> flag
  back to her per her own instruction, decide together which method is
  correct before building any weighting on top of either.
- Separate ask from her: verify/check y/n calls on 27 AMBER rows in the
  precision-audit labeling file.
- Deadline: two more P(t) runs need to happen before **Oct 23, 2026** —
  OpenAI is retiring `gpt-4-0613` and `gpt-4o-2024-05-13`, the two
  oldest rungs anchoring the earliest point on the perception curve.
  Once retired, that data point is permanently uncollectable, not just
  harder to get. This deadline applies to the P(t)/perception side
  (her primary area), but affects overall project timing.
- GDELT rate-limiting is worse than expected in practice — she reports
  needing retries roughly every 1 minute, tested from 2-3 different
  locations. Build in patience/longer backoff when actually running
  harvester scripts, not just the 6s gap coded so far.
- Viveka invited contributing a written section to the paper directly
  (not just data work) and showcasing any additional skills — framed as
  a portfolio-worthy addition, not just an ask.

## 2026-08-16 (session 2 — scaffolding build)

- Viveka reviewed and approved the implementation plan with two
  modifications:
  1. Ramp/onset definitions supplied directly from Section 4.6 — no need
     to re-read the PDF:
       - Ramp date = first week C(t) reaches 10% of its peak
         (floor of 3–5 mentions to avoid noise)
       - Onset = first model cutoff where P ≥ 3
       - Sensitivity grid: {5%, 10%, 20%} × {P≥2, P≥3, P≥4} — must
         mirror Table 2 shape for line-by-line comparability
  2. Default to Approach B (empirical frequency clustering) for tiering —
     NewsGuard and Moz DA are paywalled. Only use external lists if a
     genuinely free one surfaces (e.g. AP/Reuters partner rosters).
- Open questions all resolved:
  - Files (ct_artlist_results.csv, ct_artlist_LABELING.xlsx): need to
    check locally; obtaining them is the next action if not present.
  - 27 AMBER rows: kept separate from this pipeline.
  - Harvester protocol: confirmed — spot-check decides, no exceptions.
  - 20 covered entities: two-minute lookup from xlsx once in hand.
- Wrote scaffolding scripts (all structurally complete, not yet runnable
  without source data):
  - `scripts/merge_source_data.py` — merges her 20 + our ~30, domain
    normalization, overlap/gap diagnostics
  - `scripts/build_tier_map.py` — Jenks natural breaks on
    log(breadth × volume), GVF quality metric, precision cross-check
  - `scripts/apply_weights.py` — continuous weights + binary exclusion
    (Tier 1 only, Tier 1+2), unmatched-domain tracking
  - `scripts/precedence_test_weighted.py` — Section 4.6 sign test
    baked in, raw/weighted/Tier1/Tier12 all run simultaneously
  - `scripts/sensitivity_analysis.py` — Table 2 mirror grid, weight
    sweep (4×4), PASS-only subset, capped-week exclusion
- Entity analysis from the frozen data:
  - 50 total entities, 6 flagged self_ref_openai (GPT-4, GPT-4o,
    OpenAI o1, OpenAI o3, Sora, Operator)
  - 5 model ladder rungs: gpt-4-0613 (cutoff 2021-09),
    gpt-4o-2024-05-13 (2023-10), gpt-4o-2024-11-20 (2023-10),
    gpt-4.1-2025-04-14 (2024-06), gpt-5.2 (2025-06)
  - Two models share cutoff 2023-10 — handled by taking max score
    per cutoff per entity
  - 37 non-flagged entities reach onset (P≥3), 7 do not (Bolt.new,
    DeepSeek, DeepSeek-R1, Liquid AI, Lovable, Manus, World Labs)
  - Precision audit: 12 PASS, 10 FAIL, 28 NOT_AUDITED
- **Blocker status unchanged:** spot-check still cannot run. Next
  action is obtaining the two files from Viveka.

## 2026-08-17 — Baseline reproduction fix (28/33 exact match confirmed)

- **Corrected exclusion rule.** Viveka supplied the exact rule, verified
  against Sections 4.5 (Table 1) and 5.4 of the paper:

      TESTABLE 33 = all 50 entities MINUS:
        10 precision-audit FAIL (Section 4.5, Table 1):
            DBRX, Kimi, Ideogram, Lovable, Gemini (Google model),
            Dream Machine, Liquid AI, Mamba, Operator, vLLM
        7 no-onset entities (Section 5.4):
            OpenAI o1, OpenAI o3, DeepSeek, DeepSeek-R1,
            Manus, World Labs, Bolt.new

  The `self_ref_openai` flag in `entities.py` is **NOT** part of this
  baseline. GPT-4, GPT-4o, and Sora are included in the 33. The flag
  exists for a separate robustness analysis (self-recognition confound)
  but must not be conflated with the 33-entity baseline.

- **Name-mismatch discovery.** The perception CSV (`pt_pilot_results.csv`)
  uses parenthetical disambiguators (e.g. `Cursor (the AI code editor)`)
  while the citation CSV (`ct_results_v1_frozen.csv`) uses short names
  (e.g. `Cursor`). 14 of 50 entities are affected. Previous code that
  joined directly on entity name silently dropped these 14, producing
  only 26 testable entities instead of 33. Fixed by building a canonical
  name bridge that strips parentheticals.

- **Confirmed reproduction:** `scripts/reproduce_baseline.py` now
  reproduces the paper's result exactly:
    - Floor=3: 28/33, median lead 83 days, p = 6.62 × 10⁻⁵ ✓
    - Floor=5: 28/33, median lead 83 days, p = 6.62 × 10⁻⁵ ✓
  Both match the paper's reported values. The per-entity detail shows
  5 entities with negative lead (ramp after onset): Apple Intelligence,
  Cursor, Grok, Humane Ai Pin, Safe Superintelligence.

- **Impact on weighting pipeline.** The existing `precedence_test_weighted.py`
  uses the `self_ref_openai` flag as an exclusion, which is wrong for
  baseline reproduction. For the weighting analysis, the baseline check
  should use the paper's exact rule (10 FAIL + 7 no-onset). The
  `self_ref_openai` exclusion is a valid additional robustness variant
  but must be clearly labeled as such, not as the baseline.

- **Name bridge also needed in `precedence_test_weighted.py` and
  `sensitivity_analysis.py`** — these scripts join PT and CT entity names
  and will silently drop the 14 mismatched entities without the bridge.
  Must be fixed before any real weighting run.

## 2026-08-18 — Viveka verification update

- **gpt-4.1 is NOT retiring.** Viveka checked OpenAI's official model
  page directly (not the Azure page). Only the "nano" variant is being
  retired, which is a separate model we don't use. No action needed on
  gpt-4.1; treat it as stable going forward.
- **gpt-4-0613 and gpt-4o-2024-05-13 retirement on Oct 23, 2026 is
  confirmed** — this matches what's already in the status table; no change
  to that deadline.
- **No Claude Opus swap needed.** The two remaining P(t) reruns use the
  original OpenAI-only ladder, so Opus-4-1's retirement is irrelevant
  here — do not add any Anthropic-model fallback logic for these runs.
- **Viveka is targeting early-to-mid October** for her side of the two
  remaining P(t) runs, ahead of the Oct 23 cutoff.

## 2026-08-18 (cont.) — Independent other_week computation for Mamba: MISMATCH

- Ran Viveka's exact week-selection algorithm independently against
  `ct_results_v1_frozen.csv` for Mamba (all 140 `status=ok` weeks,
  ranked by `mention_count` descending):
  - `peak_week` = `weeks[0]` = **2025-03-31** (count 28)
  - `other_week` = `weeks[140 // 2]` = `weeks[70]` = **2025-09-29**
    (count 1; not equal to peak's 28, so no fallback to `weeks[1]`)
- **Peak side lines up:** the xlsx's 25 Mamba `peak_week` article rows
  are dated 2025-04-03 / 2025-04-04, which fall inside the 2025-03-31
  week — consistent with the frozen series' max-count week.
- **`other_week` side diverges:** computed = 2025-09-29 vs. the xlsx's
  single known `other_week` value = 2024-01-26 (article date; that
  Monday-week is 2024-01-22, ranked only #46 today with count 1 — not
  the median week).
- **Where it likely diverges (cannot be distinguished without her pull
  parameters / an earlier snapshot of the frozen CSV):**
  1. The original 22-entity pull likely ran against an EARLIER snapshot
     of `ct_results_v1_frozen.csv` — with far fewer ok weeks the median
     index would land on a different week.
  2. The median-by-count strategy is itself an assumption (the script's
     own docstring says so) — the original `other_week` may have been
     chosen by a different method entirely.
  3. `TimelineVolRaw` aggregate counts (frozen CSV) can rank a week
     differently than ArtList's actual article count.
- **Consequence:** the median algorithm is NOT independently confirmed.
  Per Viveka's own instruction this goes back to her — decide together
  which week-selection method is correct before building weighting on
  either. Note this validates/refutes the ALGORITHM only; it says
  nothing about Kimi's missing `other_week` — the xlsx still has no
  `other_week` row for Kimi, so that check still depends on her
  sending `ct_artlist_results.csv` or on running her harvester locally.
- File placement cleanup this session: moved `Mamba 29092025.json` ->
  `reference/gdelt_artlist_sample_response.json`, `ct artlist
  LABELING.xlsx` -> `inputs_frozen/ct_artlist_LABELING.xlsx`, renamed
  `scripts/ct artlist harvester.py` -> `scripts/ct_artlist_harvester.py`.
  `scripts/__pycache__/` is gitignored and untracked; no tracking
  removal needed. LABELING xlsx `Label` sheet columns verified to match
  the harvester's `CSV_FIELDS` exactly (`#`, `entity`, `window`, `date`,
  `title`, `domain`, `url`, `suggested_label`, `relevant`).

### RESOLVED — CLOSED (2026-08-18, via `scripts/ct_artlist_audit.py`)

- The original second-week rule is **confirmed unrecoverable** — Viveka
  acknowledges the original `other_week` selection cannot be
  reconstructed, so the Mamba mismatch above is moot (it is not a fixable
  divergence; the old rule is being retired, not corrected). The audit
  script's own docstring states this:
  > "Documented 2026-08-18 replacement for the original (unrecoverable)
  > second-week rule -- see changes.md 2026-08-18 entry. Picks a week that
  > genuinely contrasts peak_week (>= min_gap_weeks away), deterministically:
  > seeded on entity name + a fixed version tag only, never on a run date or
  > row order, so re-running this later reproduces the same pick even if
  > unrelated rows are added to results_path."
- **Going forward, the deterministic v2 `contrast_week()` replaces the
  median-by-count assumption** (`CONTRAST_MIN_GAP_WEEKS = 4`, seeded
  `"contrast-week-v2-<entity>"`, `random.seed(20260708)`). Re-runs
  reproduce identical picks.
- `scripts/ct_artlist_audit.py --contrast-urls` now runs cleanly from this
  repo's layout: added a `sys.path` bootstrap to import `ct_harvester`
  from `inputs_frozen/`, and `contrast_week` now resolves
  `inputs_frozen/ct_results_v1_frozen.csv` via the script's own location
  instead of a CWD-relative name. Produces 22 real GDELT ArtList URLs (one
  per overridden entity, ~9 min at 25s apart). Note Mamba's v2
  `contrast_week` lands on 2025-09-29 — same date as the independent
  median computation, coincidentally, but v2 does NOT use the median rule.
- **Kimi note unchanged but de-blocked:** the xlsx still has no
  `other_week`/`contrast_week` row for Kimi, but with v2 that no longer
  blocks the audit — `--contrast-urls` already generated Kimi's
  `contrast_week` (2026-03-16) directly. The old spot-check's dependency
  on her `ct_artlist_results.csv` is superseded by the v2 audit lane.
- Environment fix required to run: the Python 3.14 env had broken
  C-extensions for numpy/matplotlib/Pillow/kiwisolver/contourpy.
  Repaired via pip (cp314 wheels): numpy 2.5.2, matplotlib 3.11.1,
  pillow 12.3.0, kiwisolver 1.5.0, contourpy 1.3.3, fonttools 4.63.0.
  `pandas` is not installed but is not needed by `ct_harvester`/audit.

## 2026-08-18 (cont.) — data_derived/ tracking policy

- Committed the two raw-fallback outputs as a deliberate milestone
  snapshot (`data_derived/precedence_comparison.csv`,
  `data_derived/sensitivity_results.csv`, commit `9e24bc3`) — they back
  the "Raw-Fallback Analysis Run: Executed 2026-08-17" row in the
  project overview status table.
- **Decision going forward: ignore `data_derived/*` by default; commit
  milestone snapshots deliberately with `git add -f`.**
  - Why: `data_derived/` is defined as regenerable scratch output
    (project overview, Section 2). Reproducibility rests on the frozen
    inputs + pinned scripts + this decision log; derived CSVs are
    intermediate artifacts, not source-of-truth data.
  - Tracking every regen by default adds diff noise, risks stale or
    contradictory outputs being mistaken for authoritative, and causes
    merge churn on regenerated files.
  - The escape hatch stays available: a specific output that backs a
    stated result (like the two above) is force-added as a frozen
    milestone tied to the commit that produced it.
  - Already-tracked files (`data_derived/.placeholder.md` and the two
    milestone CSVs) are unaffected; the ignore rule applies only to new
    files. `.gitignore` now documents the `git add -f` convention.

## 2026-08-18 (cont.) — Project-local `.venv` (no more global-env edits)

- **Context:** the numpy/matplotlib/Pillow/kiwisolver/contourpy upgrades
  above were applied to the global `C:\Python` interpreter to unblock the
  audit script. That risks breaking other Python work on this machine that
  pinned older versions of those packages — a one-off fix, not a policy.
- **Policy from now on:** use a project-local venv at the repo root
  (`.venv/`), already covered by `.gitignore` line 4. All future runs of
  the harvester/audit scripts should use
  `.venv\Scripts\python.exe` (or activate `.venv`), NOT the global
  interpreter.
- Venv created 2026-08-18 with `python -m venv .venv`; installed
  `requests` + `matplotlib` only (pandas not required by
  `ct_harvester`/audit). Verified: `.venv\Scripts\python.exe
  scripts/ct_artlist_audit.py --contrast-urls` runs clean and reproduces
  the same 22 GDELT URLs as the global interpreter.
- Add new dependencies to the venv with
  `.venv\Scripts\python.exe -m pip install <pkg>`; never install into the
  global environment for project work.

## 2026-08-18 (cont.) — Collection-lane methodology decision (Lane A vs Lane B audit)

**Prompt:** Reviewer (Claude) concern that Lane A (22 `QUERY_OVERRIDES`
entities, `scripts/ct_artlist_audit.py`) collects `peak_week` +
`contrast_week`, while Lane B (~30 entities, `scripts/ct_source_harvester.py`)
collects `peak_week` only — a possible sampling-depth inconsistency.

**Audit finding (evidence-based, no data changed):**

- The ANALYTICAL source sample is `peak_week`-only in BOTH lanes:
  - Lane A: peak-week article rows from Viveka's manual labels
    (`ct_artlist_LABELING.xlsx`, Label sheet: 517 of 566 rows are
    `peak_week`).
  - Lane B: `ct_source_harvester.py` fixes `window="peak_week"` and its
    docstring records peak-week as the intended method (confirmed with
    Viveka, 2026-08-16).
  - `apply_weights.py` docstring: "source data is peak-week only for now".
  - `build_tier_map.py` computes domain stats ignoring `window`.
- `contrast_week` is collected ONLY for the 22 collision-prone entities by
  `ct_artlist_audit.py` as a QUERY-PRECISION AUDIT sample (name-relevance
  validation). It writes `ct_artlist_contrast.csv` / `ct_artlist_audit.csv`,
  and no pipeline script (`merge_source_data`, `build_tier_map`,
  `apply_weights`, `precedence_test_weighted`) reads either file. It is
  NOT part of the tiering/weighting dataset.
- `contrast_week` is the deterministic v2 replacement for the retired,
  unrecoverable `other_week` (see 2026-08-18 Mamba mismatch entry).

**Verdict: reviewer's concern is PARTIALLY valid** — not valid as a
description of the current analytical design, but valid as a latent risk:
- NOT a current defect: both lanes feed `peak_week` only; the second-week
  sample is audit/validation only, so the asymmetry is intentional (only the
  collision-prone entities need precision checks on their names).
- REAL risk #1 (guardrail now enforced): `merge_source_data.py` previously
  hardcoded Viveka rows to `window="peak_week"` and had no `window` column
  mapping — her 49 `other_week` rows would have entered the analytical
  sample as `peak_week`. Now the script maps `window`, excludes non-peak
  rows from the analytical sample, and reports the exclusion in
  `merge_diagnostics.txt`.
- REAL risk #2 (documented prohibition): `ct_artlist_contrast.csv` /
  `ct_artlist_audit.csv` must NEVER be merged into `ct_source_all.csv`
  (tier map / weighted counts) without reconciling (a) the window asymmetry
  (2 weeks for 22 entities vs 1 for 30) and (b) the volume asymmetry
  (manual pull ~25–50 rows/entity/week vs harvester cap of 250). Merging
  them as-is would bias the tier map and shift weighted ramp dates for
  Lane A only.

**DECISION: OPTION B.** Keep Lane B `peak_week`-only; `contrast_week`
stays an audit/validation sample, never an analytical one. Chosen on
evidence, not symmetry: the two lanes already converge on the same
analytical sample, so extending Lane B to collect a second week would add
cost (rate-limited GDELT pulls) with no methodological gain, and the
audit lane's purpose (precision) is different from the analytical lane's
purpose (volume/breadth).

**Affected lane:** Lane A unchanged (audit script untouched);
Lane B unchanged (harvester still peak-week only). Change is confined to
the merge guardrail + documentation.

**Implications for later analysis:**
- `merge_source_data.py` `read_viveka()` now requires (or defaults) a
  `window` column and drops non-peak rows; a merged file is therefore
  peak-week-only by construction.
- Remaining pre-existing TODO (not changed): `VIVEKA_COL_MAP` still maps
  `week_start`/`seendate`/`sourcecountry` best-guess; the real xlsx Label
  sheet has `date` not `week_start`. Re-verify the column map against the
  actual CSV export before the first real merge run.
- The ~30-entity Lane B collection can proceed as planned (peak-week only);
  it is NOT blocked by this audit.

**Verification:** `scripts/test_pipeline_smoketest.py` run via
`.venv\Scripts\python.exe` — PASSED cleanly; synthetic Viveka export now
includes a `window` column plus one `other_week` row, which the merge
excluded (diagnostic printed), and the full 5-script pipeline completed
without error.

## 2026-08-18 (cont.) — Contrast-week audit collection COMPLETE (22/22)

- **All 22 ArtList JSON files for the overridden entities were collected
  and ingested.** `--contrast` now covers **22/22 entities, 263 article
  rows** in `data_derived/ct_artlist_contrast.csv` (all in the v2
  `contrast_week` window; rows carry the empty `relevant` field awaiting
  the precision labeling pass).
- **Matching detail:** the GDELT ArtList JSONs are bare `{"articles":...}`
  envelopes — they carry **no `query_details` field**, so entity matching
  is filename-based via `FILENAME_ALIASES`. This was confirmed directly in
  `Apple.json` / `Liquid.json` before ingestion.
- **Fix applied (required to match all 22):**
  - `_filename_entity()` in `scripts/ct_artlist_audit.py` now strips
    leading digits (numbered-archive prefixes like `01_`) and converts `_`
    to spaces before alias lookup. Without this, `Apple_Intelligence.json`,
    `Dream_Machine.json`, and `Liquid_AI.json` were skipped, and the
    numbered archive scheme below would never re-ingest.
  - `Apple.json` (ambiguous base name) was renamed to
    `Apple_Vision_Pro.json` before ingestion — `apple` alone is ambiguous
    because both `Apple Intelligence` and `Apple Vision Pro` are overridden
    entities.
- **Archive:** the 22 raw JSONs now live in
  `reference/contrast_collection_2026-08-18/`, renamed with the original
  generation order (verified against the `QUERY_OVERRIDES` roster order
  used by `print_contrast_urls`): `01_Cursor.json` … `22_Manus.json`.
  Verified: the fixed `_filename_entity()` resolves all 22 archived names
  to the correct entities, so the archive is re-ingestable.
- `data_derived/ct_artlist_contrast.csv` tracked deliberately with
  `git add -f` (milestone convention), same as the other two milestone CSVs.
- **Remaining step for the audit lane:** hand-label the `relevant`
  column (y/n) on the 263 contrast-week rows — the precision-audit
  verdict for the collision-prone names. Not done here.
- **Still-pending manual-labeling tasks (both open, both equally
  not-done — listed separately so neither reads as more current):**
  1. The **original 27 AMBER precision-audit rows** (from
     `ct_artlist_LABELING.xlsx` / the original audit file) — needs a
     human (jointly with Viveka) to finish. Untouched by this session.
  2. The **263-row contrast-week batch** (`data_derived/
     ct_artlist_contrast.csv`) — same y/n `relevant` convention as the
     original audit file; collection is done, labeling is not.
  Neither has any `relevant` value prefilled by tooling.

## 2026-08-22 — Catch-up entry (log fell behind)

**Honest note:** this log fell behind after 2026-08-18. Work continued
across 2026-08-19 and 2026-08-22 but was not recorded in real time. This
entry consolidates everything that happened since the last dated entry — it
is not a granular day-by-day reconstruction.

### What happened (commits, in order)

1. **`e88174d` (2026-08-19) — status update:** Updated the project overview
   status table to track both manual-labeling tasks separately (27 AMBER
   rows + 263 contrast-week rows), rather than letting one read as more
   current than the other. Added the "Still-pending manual-labeling tasks"
   section to this log.

2. **`880c107` (2026-08-19) — `:port` domain-normalization fix:** During
   contrast-audit QA (ingesting the 22 archived JSONs), discovered that
   `asiaone.com:443` and `asiaone.com` were counting as separate domains
   in `merge_source_data.py` because `urlparse().netloc` preserves the port.
   Fixed by stripping trailing `:port` in `normalize_domain()`. Verified:
   both `read_viveka()` and `read_harvester()` call `normalize_domain()` at
   their domain-normalization points; smoke test passes. Also added
   documented syndication examples to `docs/tier_methodology.md` (Threads 6×
   NBC affiliates, Operator 4× Nine papers, Qwen 5× independent outlets)
   — observed, not theoretical.

3. **`08b7dbd` (2026-08-19) — documentation rewrite:** Rewrote all
   repository READMEs as professional research documentation: root overview,
   frozen-deposit provenance record (`inputs_frozen/`), computational
   methods index (`scripts/`), derived-outputs record (`data_derived/`),
   documentation index (`docs/`), reference evidence index (`reference/`),
   and archived contrast-collection record. The `data_derived/README.md`
   was force-added as a milestone per the tracking policy.

### What happened (uncommitted session work, 2026-08-22)

These were done during the current working session, committed together
with this log update:

4. **Report regeneration (`docs/project_overview_report.md`):** Regenerated
   the full report against current `git ls-files` / `git log`. Fixed the
   §3 / §6 contradiction (§3 still said "0/22 JSON files collected" while
   §6 said complete). Added the `:port` domain-normalization bug as its own
   writeup (same format as the `self_ref_openai` bug entry). Updated §8
   commit history to include all 15 commits through `08b7dbd`. Updated §2
   tree and tracked-files list to reflect current reality (22 archive JSONs,
   `ct_artlist_contrast.csv`, new READMEs, `ct_artlist_audit.py` tracked).

5. **AMBER rows extracted:** Isolated the 27 `?`-flagged rows from
   `inputs_frozen/ct_artlist_LABELING.xlsx` into
   `data_derived/amber_rows_review.csv` (columns: entity, window, date,
   title, domain, url, suggested_label, relevant). The `relevant` column is
   empty — awaiting manual y/n labeling. Entity breakdown: Apple Intelligence
   (13), Kimi (10), Qwen (2), Dream Machine (1), Lovable (1).

6. **`ALREADY_COVERED` populated in `ct_source_harvester.py`:** Filled the
   skip-list with the exact 22 entity names from the xlsx's entity column.
   Remaining for Lane B: 28 entities (not the ~30 previously estimated).
   Harvester is configured but **not run against live GDELT** — awaiting
   sanity-check before burning rate-limit budget.

7. **`needs_translation` column added to `ct_artlist_contrast.csv`:** Added
   a boolean column flagging rows with non-ASCII characters in the title
   (rough heuristic for non-English). 31 of 263 rows flagged. Caveat: ~5–6
   are false positives (em-dashes, £ symbols in otherwise-English titles).
   This is a first-pass conversation starter for Viveka, not a final
   translation judgment.

### Current state of labeling tasks

| Task | Rows | Status |
|---|---|---|
| 27 AMBER precision-audit rows | 27 | Extracted to `amber_rows_review.csv`, `relevant` empty — manual labeling pending |
| 263-row contrast-week batch | 263 | `relevant` empty in `ct_artlist_contrast.csv` — manual labeling pending |
| Total | 290 | Neither has any value prefilled by tooling |

### What this log update is

This is a catch-up, not a real-time record. The entries above cover work
that happened across 2026-08-19 and 2026-08-22, consolidated into one
dated entry because the log fell behind. Future entries should resume
real-time logging at the next decision point.

## 2026-08-22 (cont.) — needs_translation verification + Lane B test attempt

### needs_translation verified (real numbers)

Confirmed against `data_derived/ct_artlist_contrast.csv` (263 rows):

- **31 of 263 rows flagged `needs_translation=true`** (11.8%)
- **232 rows `needs_translation=false`**
- **0 rows empty** (column fully populated)

Entity breakdown of flagged rows:
| Entity | Flagged |
|---|---|
| Operator | 9 |
| Apple Vision Pro | 5 |
| Dream Machine | 4 |
| Cursor | 3 |
| Grok | 3 |
| xAI | 3 |
| Apple Intelligence | 1 |
| Gemini (Google model) | 1 |
| Sora | 1 |
| Threads | 1 |

**False-positive caveat (~5-6 rows):** em-dashes, £ symbols, and
accented characters in otherwise-English titles. Examples:
- Row 33 (Apple Vision Pro, radiotimes.com): "Apple Music offers three
  months for ?1.99" -- the ? is a £ sign, English article
- Row 98 (Gemini, techradar.com): "Siri is truly terrible, but I'm
  optimistic..." -- the ? is an em-dash, English article
- Row 102 (Grok, dailymaverick.co.za): "Grok -- Elon Musk's new sassy..."
  -- em-dash, English article

**Genuine non-English candidates:** the Chinese-language domains
(ddaily.co.kr, finance.sina.com.cn, tech.ifeng.com, kwongwah.com.my,
news.china.com, newtalk.tw, news.ifeng.com, ura.news, dailyinqilab.com)
and Spanish-language domains (malagahoy.es, elperiodico.com,
dobreprogramy.pl) are the real signal. The heuristic catches them but
also catches the false positives above.

### Lane B 2-entity test — BLOCKED (GDELT rate-limited)

Attempted to test `ct_source_harvester.py` against 2 entities
(ElevenLabs, Bolt.new) with 35s spacing and retry/backoff logic.

**Result: all attempts returned HTTP 429** ("Please limit requests to
one every 5 seconds"). Tried waiting 60s, 120s, and 300s between attempts.
The rate limit persisted across all waits. This is likely a daily quota
exhausted by the earlier 22-entity contrast-week collection burst
(~22 GDELT calls in a short window on 2026-08-18).

**GDELT is currently inaccessible from this IP.** The 2-entity test
cannot proceed until the rate limit clears (likely tomorrow).

### Full ~30-entity batch runtime estimate (theoretical, pending rate-limit clearance)

Based on `ct_source_harvester.py` code:
- **28 remaining entities** (50 total minus 22 ALREADY_COVERED)
- **1 GDELT ArtList call per entity** (peak week, 7-day window)
- **Base spacing:** `SLEEP_BETWEEN_CALLS = 6.0s` (harvester default)
- **Typical response time:** 2-5 seconds per call

**Best case (no 429s):** 28 calls * (6s sleep + 3s avg response) =
~252 seconds = **~4.2 minutes**

**Realistic case (some 429 backoff):** If ~30% of calls hit 429, backoff
is 30s/60s/120s per retry. Estimated: **~15-25 minutes**

**Conservative case (heavy 429s, user-requested 35s spacing):** If we
override `SLEEP_BETWEEN_CALLS` to 35s: 28 * 35s = 980s + responses =
**~18-20 minutes**

**Recommendation:** Wait until tomorrow for the daily quota to reset,
then run with the harvester's default 6s spacing (not 35s -- the
harvester's adaptive throttling handles backoff). If the quota resets
overnight, the full batch should complete in ~5-10 minutes. If 429s
recur, the backoff logic will slow down automatically but the batch
could take 20-30 minutes.

## 2026-08-22 (cont.) — Lane B retry ALSO 429; GDELT testing PAUSED for the day

- **Second Lane B test attempt today also blocked.** Re-attempted
  `ct_source_harvester.py` with 35s spacing plus 60/120/300s retry
  backoff. Every attempt still returned HTTP 429 — the block did not
  clear across any of the waits.
- **This reads as a longer block than the earlier one, not a transient
  throttle.** A 429 that survives a full 300s wait is qualitatively
  different from the per-5s "one request every 5 seconds" throttle.
  Continuing to retry risks *extending* the block (resetting its window)
  rather than clearing it — so more attempts today are counterproductive.
- **DECISION: STOP all GDELT calls for today.** No further Lane B test
  attempts on 2026-08-22. This supersedes the earlier entry's
  "wait until tomorrow, run with 6s spacing" recommendation — the block
  is more persistent than a simple daily-quota reset would explain.
- **Next attempt: a later cooldown window** — at least several hours out,
  ideally the next calendar day, to give the block time to fully clear.
- **At the next attempt, also change network.** Test from a different
  network (e.g. a mobile hotspot) to distinguish a shared-IP cause
  (another user on this IP exhausted the quota) from a genuine extended
  block tied to this project's own GDELT usage. This determines whether
  the fix is "wait it out" or "route around the IP."

## 2026-08-22 (cont.) — 27 AMBER rows finalized + CSV-vs-master discrepancy

**Reviewed and wrote the `relevant` column for all 27 AMBER rows** in
`data_derived/amber_rows_review.csv`. Final distribution: **16 `y`,
5 `n`, 6 `unverifiable`** (count verified = 27 before writing; each row
matched on entity + domain, not just row order). The master
`inputs_frozen/ct_artlist_LABELING.xlsx` Label sheet was **NOT** modified
— only the derived CSV was written.

**Discrepancy found (data integrity):** the master xlsx Label sheet
already carried `relevant` values for all 27 `?`-suggested rows, present
since the file's Aug 18 mtime — **21 `y`, 5 `404`, 1 "leads to different
article".** The 2026-08-22 extraction into `amber_rows_review.csv`
(catch-up entry, item 5) **blanked all 27** `relevant` cells ("awaiting
manual labeling"), discarding those pre-existing calls — so that CSV was
never a faithful export of the master's `relevant` column; it silently
dropped values that existed upstream. Flagged for reconciliation with
Viveka; deliberately NOT auto-back-filled from the master, because
several of the master's tentative `y`s were overridden on review (below).

**Kimi override (precedent-based, not a fresh guess):** the 5 live-link
Kimi "China top AI players" rows (homenewshere, digitaljournal, kdhnews,
wyomingnews, averyjournal) were set to **`n`**, overriding the master's
tentative `y`. Basis: Viveka's own definite (non-AMBER,
`suggested_label='n'`) Kimi calls elsewhere in the Label sheet — all 15
are multi-company / China-AI-roundup pieces ("Trump administration vows
crackdown on Chinese companies exploiting AI models made in US" ×14
syndicated copies + "Tencent unveils AI model in high-stakes test for
OpenAI hire") and she marked **every one `n`.** "China top AI players" is
the same listicle/roundup shape (Kimi named among several Chinese AI
firms, not the article's subject), so `n` matches her established
standard. Caveat: the "How to label" sheet gives **no** explicit
"primarily-about vs any-meaningful-mention" definition — it frames the
task as a "Query Precision Audit (pre-filled)" and relies on her
pre-filled calls plus a sanity hint (Mamba/Liquid AI/Operator/vLLM ~all
`n`; Cursor/Suno/Threads ~all `y`) — so precedent-matching against her
own firm calls is the only available standard, not a written rule.

**6 rows marked `unverifiable` (not forced y/n):**
- 5 Kimi rows with dead links (HTTP `404` in the master): the-messenger,
  lebanondemocrat, gjsentinel, themountainpress, suncommercial.
- 1 Apple Intelligence row: lifehacker.com.au, flagged "leads to
  different article" in the master (URL resolves to something other than
  the labeled headline).
- **Wayback Machine could not be consulted from this environment.**
  `archive.org` / `web.archive.org` are outside the network egress
  allowlist (only `agentrouter.org` is permitted); both WebFetch and the
  workspace fetch tool returned `cowork-egress-blocked`. Per the review
  instruction, these are marked `unverifiable` rather than forced to a
  y/n. **Next step for these 6:** re-check via Wayback from a network
  where the archive is reachable (or have Viveka pull the archived
  snapshots / re-fetch the dead links), then finalize.


## 2026-08-22 (cont.) — Step 1: VIVEKA_COL_MAP fixed to real Label-sheet columns

Reworked `scripts/merge_source_data.py` so `read_viveka()` reads the columns
Viveka's `ct_artlist_LABELING.xlsx` (Label sheet) actually has, instead of the
old best-guess set.

**What changed:**
- `VIVEKA_COL_MAP` now maps only the real, verified columns: `entity`,
  `window`, `date`, `domain`, `url`, `title`. Dropped the phantom `seendate`,
  `sourcecountry`, and `week_start` keys (her sheet has none of these). Removed
  the stale `# TODO: inspect her actual xlsx export and fix these.` comment.
- `week_start` is now DERIVED, not read: new helper `week_start_from_date()`
  returns the Monday of the ISO week containing the article `date` (GDELT weeks
  are Monday-based). All peak_week articles for an entity fall inside the same
  7-day window, so they collapse to one Monday that matches the harvester's
  `peak_week_start` and the frozen counts' `week_start` keys. This matters
  because `apply_weights` buckets weighted counts by `(entity, week_start)` and
  `precedence_test_weighted` keys its citation series on `week_start` — an empty
  or mismatched value would silently zero out weighted counts.
- `seendate` is now carried from her `date` column (cosmetic passthrough; not
  consumed by the tier/weight path). `sourcecountry` is written as `""`.
- Missing-column check now validates the ACTUAL column names (map values),
  with `window` optional (rows without it default to peak_week). Also guarded
  an empty `window` cell to default to peak_week rather than being silently
  dropped as non-peak.
- Updated the module docstring's "Expected columns" block to the verified real
  columns.

**Coupled fix (required by the contract change):**
`scripts/test_pipeline_smoketest.py` built its synthetic Viveka export with the
OLD columns (`seendate`, `sourcecountry`, `week_start`, no `date`). After this
change the reader requires `date`, so the smoke test's fixture would fail the
missing-columns check. Updated that fixture to the real column layout
(`entity, window, date, title, domain, url, suggested_label, relevant`); the
non-peak `other_week` guardrail row was preserved. (Smoke test is run in Step 4.)

**Verification:** `python3 -m py_compile` clean on both files;
`week_start_from_date` unit-checked on 7 cases (Mon→itself, Tue/Sun→same
Monday, next-Monday, mid-week→prior Monday, empty→"", unparseable→"") — all pass.


## 2026-08-22 (cont.) — Step 2: non-English contrast-row reconciliation (31/263)

Went through all 31 `needs_translation=true` rows in
`data_derived/ct_artlist_contrast.csv` (263 data rows total) and classified
each by Unicode-script analysis + reading the title. Three-way breakdown:

- **Genuinely non-English: 15.** By language: Korean 3 (ddaily.co.kr, all
  Apple Vision Pro), Chinese 7 (Cursor 3 — finance.sina.com.cn ×2 +
  tech.ifeng.com; Dream Machine 4 — kwongwah.com.my, news.china.com,
  newtalk.tw, news.ifeng.com), Russian 1 (ura.news, Operator), Bengali 1
  (dailyinqilab.com, Operator), Spanish 2 (malagahoy.es, elperiodico.com,
  Operator), Polish 1 (dobreprogramy.pl, Operator). 12 of these are
  non-Latin scripts (Hangul/CJK/Cyrillic/Bengali); the other 3 are
  Latin-script but unambiguously Spanish/Polish by content.
- **False-positive flags: 16.** Every one is an English title; the flag was
  tripped purely by a non-ASCII *punctuation/symbol* character, not by any
  foreign-language text: 13× EN DASH (U+2013), 1× POUND SIGN (U+00A3, the
  radiotimes "£1.99" Apple Music deal), 1× NO-BREAK SPACE (U+00A0, the
  mactech Bluey/Apple Arcade item), 1× NON-BREAKING HYPHEN (U+2011, the
  tomshardware "frontier-level" Grok 4 item).
- **Genuinely uncertain: 0.** No flagged title was ambiguous — each resolved
  cleanly to English or to a specific foreign language.

**Sum check: 15 + 16 + 0 = 31.** ✓

**Root cause / recommendation:** the `needs_translation` heuristic evidently
fires on the presence of ANY non-ASCII codepoint, so ubiquitous typographic
punctuation (en-dashes especially) produces a ~52% false-positive rate on this
batch. Recommend tightening it to detect non-Latin *letters* (or running real
language detection) rather than any-non-ASCII, before the 263-row contrast set
is hand-labeled. Only the 15 genuine rows actually need translation to judge
relevance; the 16 English rows can be labeled as-is.


## 2026-08-22 (cont.) — Step 3: verify_week_match.py flagged SUPERSEDED

Added a prominent `*** SUPERSEDED (2026-08-18) — STALE SCAFFOLDING, DO NOT RUN
AS-IS ***` banner at the top of `scripts/verify_week_match.py`'s docstring. The
note states it was early scaffolding built on guessed column names and Viveka's
abandoned `other_week` median-count rule, which was replaced on 2026-08-18 by
the deterministic v2 `contrast_week()` method; its premise no longer holds and
its assumptions are known-wrong. File was NOT deleted — retained for provenance
of the original Kimi/Mamba spot-check request, per instruction ("just flag it").
No other lines in the file were changed.


## 2026-08-22 (cont.) — Step 4: smoke test — found + fixed a real portability bug, now passes

Ran `scripts/test_pipeline_smoketest.py`. **First run FAILED** — but not on
logic: `sensitivity_analysis.py` raised a `SyntaxError` at line 391 (and again
at 589):

    print(f"  {'T3 \\ T2':>10s}", end="")
    SyntaxError: f-string expression part cannot include a backslash

This is a real portability defect: backslashes inside an f-string *expression*
were illegal before Python 3.12 (PEP 701 lifted the restriction). The file
therefore does not even parse on Python 3.10/3.11. The first 4 pipeline scripts
ran clean; only script 5 was blocked, and it was blocked at parse time (so it
would also have blocked Step 6).

**Fix (behavior-preserving):** hoisted the backslash literal out of the
f-string expression into a plain string assignment, in both places:

    axis_label = 'T3 \\ T2'
    print(f"  {axis_label:>10s}", end="")

Output is identical (right-justified "T3 \ T2" grid-axis header). This is now
valid on every Python version (3.10 through 3.13). `py_compile` clean on all 5
scripts afterward.

**Re-run result: `>>> SMOKE TEST PASSED CLEANLY! All 5 pipeline scripts
executed without error. <<<`** (ran under the sandbox's Python 3.10.12; all 5
scripts are pure-stdlib so this is environment-independent — no pandas/requests
needed for Lane A).

Notes:
- The smoke test's synthetic Viveka fixture was already updated to the real
  column layout in Step 1, so the merge step ingested it correctly (excluded 1
  non-peak_week guardrail row; merged 50 Viveka + 65 harvester = 115).
- Weighted / Tier-1 / Tier-1+2 precedence cells read "0/0 (no testable
  entities)" in the smoke test because the synthetic `week_start` (Monday of
  the synthetic birth date) intentionally does not line up with the synthetic
  frozen counts' weeks; the raw path gives the expected 10/10. This is
  pre-existing synthetic-data behavior (identical before the Step 1 change) and
  is not a regression — the test only asserts clean execution.
- ACTION FOR USER: confirm the target Python version. If the team runs 3.12+,
  the old code worked and this fix is a harmless portability improvement; if
  anyone runs <=3.11, this fix was load-bearing (the pipeline could not run).


## 2026-08-22 (cont.) — Step 5: generated viveka_labeled_export.csv (peak_week only)

Self-generated `data_derived/viveka_labeled_export.csv` from the Label sheet of
`inputs_frozen/ct_artlist_LABELING.xlsx` (read-only, master untouched).

- Source Label sheet: 566 data rows, header
  `#, entity, window, date, title, domain, url, suggested_label, relevant`.
  Window split: **peak_week 517 / other_week 49** (517+49=566).
- Export written with peak_week rows ONLY: **517 rows**, dropping the 49
  other_week (precision-audit) rows per the 2026-08-18 sampling policy. Dropped
  the leading `#` index column; kept the 8 substantive columns
  (`entity, window, date, title, domain, url, suggested_label, relevant`),
  which is exactly the contract `read_viveka()` now expects.
- Verified: re-read row count = 517, every row window == peak_week, 22 distinct
  entities (= Lane A's 22 QUERY_OVERRIDES entities). Dates were already ISO
  strings in the sheet (no Excel-serial conversion needed).
- End-to-end reader check: `read_viveka()` ingests all 517 (0 excluded as
  non-peak), derives a non-empty `week_start` for every row, and 100% of the
  derived week_start values fall on a Monday (GDELT convention) — confirms the
  Step 1 derivation works on the real data, not just the synthetic fixture.


## 2026-08-22 (cont.) — Step 6: full Lane-A pipeline dry-run — all 5 clean; found + fixed a 2nd real bug

Ran the full pipeline on Lane A data ALONE (the 517-row peak_week
viveka_labeled_export.csv from Step 5 + real inputs_frozen; NO harvester file,
since Lane B is not yet harvested). Executed in an isolated sandbox copy so the
real data_derived/ outputs (precedence_comparison.csv, sensitivity_results.csv)
were NOT touched — verified identical before/after.

**Chain result: all 5 scripts exit 0 (CLEAN).** No column-layout bugs surfaced
in merge -> build_tier_map -> apply_weights -> precedence_test_weighted ->
sensitivity_analysis against real data.

Real-data checkpoints (vs the synthetic smoke test):
- merge_source_data: 517 Viveka + 0 harvester = 517 rows (harvester correctly
  skipped).
- build_tier_map: 329 unique normalized domains; **Jenks GVF = 0.926 (PASS,
  >= 0.70)** — real natural-breaks tiering (T1=21, T2=61, T3=247), not the
  quantile fallback the synthetic data triggered.
- apply_weights: all 517 article domains matched the tier map; frozen counts
  for 50 entities; **22/50 entities have source data** — the 28 "missing" are
  exactly the un-harvested Lane B entities (expected, not a bug). Wrote
  ct_results_weighted.csv (6570 rows).
- precedence_test_weighted: ran clean. Comparison table:

      Method                              Precedes  Median lead   p-value
      Raw (original paper)                   28/33        83 d     6.6e-05
      Raw (original mention_count)           28/33        83 d     6.62e-05   <- reproduces baseline exactly
      Weighted (continuous tier weights)      3/11      -100 d     2.27e-01
      Tier 1 only (binary exclusion)          2/10      -100 d     1.09e-01
      Tier 1+2 (binary exclusion)             3/11      -100 d     2.27e-01

  IMPORTANT: the weighted rows are PRELIMINARY and NOT interpretable yet — only
  ~11/50 entities are testable because Lane B isn't harvested. The -100 d /
  non-significant weighted results are an artifact of the partial Lane-A-only
  sample, NOT a finding that weighting kills the effect. The raw baseline
  reproducing at 28/33, p=6.6e-05 is the meaningful signal that the plumbing is
  correct.

**2nd real bug found + fixed (sensitivity_analysis.py):** the "TIER-BOUNDARY
PERTURBATION TEST" (Section 2) was silently dead. `Counter` is used at line 441
but was never imported (top of file only imported `defaultdict`), so it raised
`NameError: name 'Counter' is not defined`, which the broad `except Exception`
at line ~633 swallowed and mislabeled as "[SKIP] ... requires generated data".
This meant the boundary-perturbation robustness check produced NOTHING on any
input, ever. Fixed by importing Counter (`from collections import defaultdict,
Counter`). After the fix the perturbation test runs and emits real variants:
boundary_shift_up (26 doms, 13.2% vol, 3/11, p=2.27e-01) and boundary_shift_down
(52 doms, 24.6% vol, 3/11, p=2.27e-01); sensitivity_results.csv grew 88 -> 90
rows. RECOMMENDATION: narrow that `except Exception` (and the similar one in the
weight-sweep block) — a catch-all that reports every error as "requires
generated data" is exactly what hid this bug; it should let NameError/AttributeError
propagate rather than masquerade as a data-availability skip.

Caveat on environment: run under the sandbox's Python 3.10.12 (all pipeline
scripts are pure-stdlib for Lane A, so no venv needed here). Numbers above are
preliminary pending the Lane B harvest.

## 2026-08-23 — Contrast-batch triage (Task 3) begins; Batch 1 (Operator) labeled

Started triaging the 263-row contrast batch (data_derived/ct_artlist_contrast.csv)
by entity, using Viveka's DEFINITE (non-'?') precedent calls from the master
Label sheet (inputs_frozen/ct_artlist_LABELING.xlsx) as the relevance standard
for each entity. New method caveat recorded in docs/tier_methodology.md §6:
contrast_week rows must NOT be block-judged on an entity's peak-week precedent
rate — the contrast week is deliberately off-peak and surfaces more ambient /
unrelated term-matches than the peak week. Apple Vision Pro is the clearest case
(25/0 'y' precedent, yet contrast rows are mostly Apple TV/Music/Arcade noise,
not the headset). Batches 16-18 (Apple Vision Pro, Apple Intelligence, Threads)
flagged for row-by-row reads, not block treatment.

Batch 1 — Operator (25 rows), precedent 0 'y' / 50 'n' (she has never marked an
Operator article relevant, including generic agentic-AI pieces). All 25 contrast
rows are off-topic (OpenAI-Seoul-office ×7, Perplexity-dethrones-Google ×4,
Opera-"Neon"-browser ×3, generic AI-agent ×3, assorted foreign-language/earnings
noise) — none name OpenAI's Operator agent. Viveka confirmed all 25 → relevant=n
(incl. the borderline generic-agent rows 10/18/19). Written to the CSV via a
byte-preserving targeted edit: only the 25 Operator lines changed, CRLF and every
other row preserved byte-for-byte (verified 25/25 differing lines == Operator
indices). 25 of 263 contrast rows now labeled.

Batch 2 — Gemini (Google model) (25 rows), precedent 2 'y' / 23 'n'. Her standard
is consistent: Gemini-model-specific how-to / feature / integration content = y;
broad-AI or other-product stories = n (her 23 'n' include a 19× syndicated "Teens
use AI chatbots" block, none Gemini-specific). Contrast rows split 10 y / 15 n.
The 15 n: an Apple–Baidu-partnership cluster (6 rows, one rolling syndicated
story) + broad-AI/off-topic (9, incl. a zerohedge/thenewamerican "AI leftist
bias" dup pair). The 10 y: 9 Gemini-specific pieces (Workspace / Maps / Messages /
Pixel-Nano / how-tos / Advanced-vs-Copilot) + row 22 (qz "How AI chatbots are
censored") — Viveka's override: it names and discusses Gemini's actual behavior
alongside other chatbots, closer to her Gemini-specific 'y' pattern than the
generic-chatbot 'n' pattern. Written via the byte-preserving verified method
(25/25 differing lines == Gemini indices; CRLF + all other rows preserved).
50 of 263 contrast rows now labeled.

Batch 3 — Dream Machine (5 rows), precedent 0 'y' / 32 'n' (pure-N wall; the term
is polluted and she has never counted a Dream Machine article — her 'n' set
includes a large syndicated "Alain Delon dies" block). All 5 contrast rows are
off-topic: 1 English Holocaust-memorial-award PR item + a 4-row foreign-language
cluster on the June 2025 Air India Boeing 787 crash. None reference Luma's Dream
Machine video model. All 5 → n (verified, 5/5 differing lines). 55 of 263 labeled.

Batch 4 — Lovable (5 rows), precedent 2 'y' / 22 'n'. Her 'y' examples are
Lovable-the-company-specific ("Lovable Launches Vibe Coding App…", "Lovable Is
Offering a 10% Raise…"); her 'n' set is adjacent-startup noise (a ~15x syndicated
"Roomba pioneer builds AI pet" block, "Voi founder's startup Pit", "Stockholm
hottest startup city") — none about Lovable. All 5 contrast rows are off-topic or
only topically adjacent: row 2 (LGBTQ+ hotels NYC, independent.co.uk) and row 3
(StumbleUpon time-killer, howtogeek) are pure noise; row 4 is about rival Base44's
own model (techcrunch); rows 1 (vibe-coding-in-Nepal, phnompenhpost) and 5
(founding-to-unicorn, fortune) are vibe-coding / startup-trend pieces whose titles
do not name Lovable. Rows 1 & 5 were checked against the local harvest artifact
reference/contrast_collection_2026-08-18/20_Lovable.json — it stores only GDELT
ArtList metadata (url/title/seendate/socialimage/domain/language/sourcecountry),
no body or snippet text, so a by-name Lovable mention is not confirmable locally
and neither title names it. Viveka confirmed all 5 → relevant=n. Written via the
byte-preserving verified method (5/5 differing lines == Lovable indices; CRLF and
all other rows preserved). 60 of 263 contrast rows now labeled.

Batch 5 — Liquid AI (2 rows), precedent 0 'y' / 33 'n' (pure-N wall; the term is
polluted by "liquid cooling" hardware/infra stories — her 33 'n' include NVIDIA/LG
"AI factory", Arista, Supermicro/Dell items, and she has never counted a Liquid AI
article). Both contrast rows → n: row 1 "Vertiv expands global liquid cooling
services" (technicalreviewmiddleeast.com) is a clean liquid-cooling term collision;
row 2 "Edge Computing For Tomorrow" (forbes.com) is topically adjacent (edge /
on-device inference is Liquid AI's space) but its title does not name the company
and no local snippet exists to confirm a by-name mention — Viveka kept it n,
consistent with her precedent of excluding broad-AI/infra think-pieces (none of her
33 N examples cleared that bar either). Written via the byte-preserving verified
method (2/2 differing lines == Liquid AI indices; CRLF and all other rows
preserved). 62 of 263 contrast rows now labeled.

Batch 6 — Kimi (2 rows), precedent 0 definite-'y' / 15 definite-'n' (+ ~10 amber).
Nuance: all 15 'n' are one generic China-AI-policy story (a 6x+ syndicated "Trump
administration vows crackdown on Chinese companies exploiting AI models" block),
so the 0-Y precedent reflects that no genuinely Kimi-specific article reached her
peak-week sample — not a rule that she excludes Kimi-specific content. Split 1 y /
1 n: row 1 "China Alibaba could launch Qwen for enterprise this week"
(siliconrepublic.com) is about a rival model (Qwen), not Kimi → n; row 2 "Cursor
admits its new coding model was built on top of Moonshot AI Kimi" (techcrunch.com)
names Kimi in the title and is substantively about it → y (Viveka's call; the
0-Y precedent, being noise-only, does not bind against a genuine name-in-title
Kimi piece). First 'y' in the recent run of all-N batches. Written via the
byte-preserving verified method (2/2 differing lines == Kimi indices; CRLF and all
other rows preserved). 64 of 263 contrast rows now labeled.

Batch 7 — vLLM (2 rows), precedent 0 'y' / 14 'n' (her 'n' are all generic
AI-infra/agent noise — ROCm/phoronix hardware, a syndicated "FlyHermes Agent"
block, Meiro "enterprise AI infrastructure"; no vLLM-specific piece has cleared
her bar). Both contrast rows sit in the inference-serving infra space but neither
names vLLM in its title and no local snippet exists: row 1 "About nCompass"
(ncompass.tech) is a corporate about-page for an inference startup, not coverage
of vLLM; row 2 "Red Hat Delivers Next Wave of Gen AI Innovation…" (webwire.com) is
a broad Gen-AI press release — Red Hat genuinely ships/serves on vLLM so a body
mention is plausible, but the title is generic PR of exactly the kind her 14 N's
exclude. Both → n (Viveka's call). Written via the byte-preserving verified method
(2/2 differing lines == vLLM indices; CRLF and all other rows preserved). 66 of
263 contrast rows now labeled.

2026-08-25 — Reconciliation with Viveka's contrast-week package
--------------------------------------------------------------
Received D:\Prem_Package_contrast_week\ from Viveka: a README, her own
ct_artlist_contrast.csv (present twice — a root copy ct_artlist_contrast_1.csv
and Prem_Package/ct_artlist_contrast.csv, byte-identical to each other), and 22
raw GDELT ArtList JSON fetches (one per entity, named by entity).

Verified provenance (read-only comparison; nothing merged blindly):
- Her CSV is a COMPLETE PARALLEL LABELING PASS over the SAME sample, not an
  earlier stage: 263 rows, all labeled (67 'y' / 196 'n'). Schema matches ours on
  the first 8 columns; her 9th column is `note` where ours is `needs_translation`.
- Row alignment is exact: 263/263 rows match by (entity,url) in identical order,
  no unmatched rows either side.
- Her README documents a two-tier method: title-based primary pass on all 263,
  then FULL-TEXT verification on the 28 title-ambiguous rows (annotated in `note`).
  Result 67y/196n. She flags an Operator query-precision finding (only 3 of ~25
  Operator rows genuinely discuss OpenAI's Operator on full-text read) and notes
  Mamba + vLLM's flagged rows resolved as genuine hits (IBM Granite 4.0; a Red Hat
  press release).
- The 22 raw_gdelt_fetches are the SAME underlying pulls as our archived
  reference/contrast_collection_2026-08-18/ (numbered 01-22): all 22/22 entities
  have identical URL sets (0 only-mine, 0 only-hers) and, on spot-checked files
  (Operator, Mamba, Apple Vision Pro), every shared record is field-for-field
  identical (title/seendate/domain/language/sourcecountry). Same collection,
  re-exported and renamed — consistent with the deterministic contrast_week rule
  (seeded on entity name + version tag, not run-date).

Five disagreements between her file and ours among the 66 rows both had labeled;
resolved as follows (writes below):
- L149 / L157 / L158 Operator (theregister / forbes / blog.skyvern): OURS n ->
  HERS y. Took HER calls -> y. Her full-text verification beats our Batch-1
  title/precedent sweep (we had zeroed all 25 Operator rows). These are exactly the
  3 genuine Operator articles her README precision finding calls out.
- L239 vLLM (webwire "Red Hat Delivers Next Wave of Gen AI Innovation"): OURS n ->
  HERS y. Took HER call -> y (full text confirms an explicit vLLM mention). This
  reverses the Batch-7 n on that row.
- L97 Gemini (qz "How AI chatbots are censored"): OURS y vs HERS n. KEPT our y —
  NO change. Her n was title-only tier (no verification note), so this is not her
  rigorous method beating ours; it's two unverified guesses. A web-search check of
  the actual article content (prem, 2026-08-25) confirms it is specifically about
  Gemini refusing ~half the test questions — more than any other chatbot in the
  piece — i.e. substantive Gemini-specific content, supporting our 'y'.

Batch 8 (Mamba) resolved: L137 IBM Granite 4.0 (ibm.com) -> y. Her file
independently marks it y with a full-text verification note on the same article,
matching what we found via search (Granite 4.0 is a genuine Mamba-2/Transformer
hybrid). Batch 8 closed as y.

Writes applied via a byte-preserving surgical edit keyed on (entity,url): exactly
5 physical CSV lines changed (137,149,157,158,239 -> 'y'); all other rows and CRLF
line endings preserved byte-for-byte; semantic re-read verified. Contrast CSV now
67 of 263 labeled (16 'y' / 51 'n'). Note: our repo CSV keeps its own
`needs_translation` 9th column; her `note` column was used only as evidence for the
reconciliation, not merged into our schema.

Batch 9 — Qwen (25 rows). Now cross-referenced against Viveka's package labels
(all 25 Qwen rows were TITLE-tier in her pass — no verification notes — so her
calls here are a second opinion at the same tier as ours, not full-text verdicts).
Outcome: 8 'y' / 17 'n'.
- 7 y: the Alibaba-integrates-Qwen-into-Taobao / agentic-shopping story, syndicated
  7x (L179,180,181,183,184 same headline + L186 scmp + L187 gdnonline variants).
  Unambiguously Qwen-specific; matches her y; this is the same cluster already cited
  as a syndication example in tier_methodology.md.
- 14 clear-noise n: L165,166,167,169,170,171,172,174,175,176,177,178,182,188
  (other models/companies or generic AI, none about Qwen).
- 3 uncertain -> n: L173 (foreignpolicy "How China Is Winning the AI Race" — Qwen at
  most a passing example), L189 (jola.dev "Running local models on an M4" — not a
  named comparison piece), L185 (clichemag "Discover the Best AI Model 2026").
- 1 uncertain -> y (OVERRIDE of both our lean and her n): L168 memeburn "7 Best AI
  Models of 2026: Ranked". prem verified via web search that the actual article
  names "Qwen 3.6 Plus" specifically with a substantive comparative claim ("makes
  more sense for high-volume workloads") — a named + substantive hit, not a passing
  mention. Same override pattern as Kimi/Cursor (Batch 6) and Mamba/IBM-Granite
  (Batch 8): where the body names the entity substantively, it beats a title-only
  n on either side.
- LOW-CONFIDENCE n flag: L185 (clichemag) is the SAME genre as L168 — a "best AI
  model" roundup from a similar period — and L168 turned out to genuinely name Qwen
  with substance. L185 could not be verified specifically, so it stays n by default
  rather than assumed-y from L168's pattern. Worth a second look if a full-text pass
  is done later.
Written via the byte-preserving verified method (exactly 25 physical lines 165-189
changed; CRLF + all other rows preserved; semantic re-read confirms 8y/17n). 92 of
263 contrast rows now labeled (24 'y' / 68 'n').

2026-08-25 — Archived Viveka's verification package into the repo
----------------------------------------------------------------
Created reference/contrast_verification_2026-08-25/ holding Viveka's independent,
full-text-verified contrast-week labeling pass:
- README.md (her package readme, copied as-is)
- ct_artlist_contrast_viveka_verified.csv (her 263-row labeled file, 67 'y' /
  196 'n'; renamed from her ct_artlist_contrast.csv to keep it distinct from our
  working data_derived/ct_artlist_contrast.csv).
This is the reconciliation source used for the 5 label disagreements + the Mamba
resolution documented in the "2026-08-25 — Reconciliation with Viveka's
contrast-week package" entry above. Not copied (confirmed byte-identical to files
already in the repo): her raw_gdelt_fetches/ (== reference/contrast_collection_
2026-08-18/, 22/22 identical URL sets) and her standalone root ct_artlist_contrast_1.csv
(== the package copy). Her `note` column is preserved here as the verification
evidence trail; it is NOT merged into our working file's schema.
