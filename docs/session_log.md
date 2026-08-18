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
