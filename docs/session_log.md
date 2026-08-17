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
