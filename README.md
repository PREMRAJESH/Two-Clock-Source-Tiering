# Source Tiering/Weighting — working folder

My contribution to Viveka Mohan Das's *Two-Clock Model* paper (Zenodo DOI
10.5281/zenodo.21532575): testing whether weighting citations by source
authority strengthens the citation → perception precedence result.

## Layout

```
two-clock-source-tiering/
├── inputs_frozen/     <- exact copies of her v1 deposit. NEVER EDIT THESE.
├── scripts/           <- my code
├── data_derived/       <- everything my scripts produce
└── docs/               <- reasoning + running notes
```

### `inputs_frozen/` — read-only

Copies of the 8 files from her v1 deposit (frozen 2026-07-08). These are
here so I can run/reference them without touching her originals or
risking editing the frozen dataset by accident. If she ships an updated
frozen version later, this folder gets replaced wholesale, not patched.

### `scripts/` — my code

- `ct_source_harvester.py` — pulls per-article source domains from GDELT
  (ArtList mode), since `inputs_frozen/ct_results_v1_frozen.csv` only has
  aggregate weekly counts with no source attribution. **Not yet run
  against live GDELT — test on a small entity first.**
- next: `build_tier_map.py` — turns raw domains into Tier 1/2/3
  assignments, with the evidence for each boundary documented in
  `docs/tier_methodology.md`.
- next: `apply_weights.py` — joins the tier map onto the citation data,
  produces a weighted C(t) series.
- next: `precedence_test_weighted.py` — reruns the Section 4.6 sign test
  (ramp-precedes-onset) on the weighted series and compares against the
  original 28/33, p = 6.6×10⁻⁵ result.

Run them in that order — each one's output is the next one's input.

### `data_derived/` — outputs, nothing frozen yet

- `ct_source_results.csv` — raw output of `ct_source_harvester.py`
  (one row per article: entity, domain, week, capped-flag).
- `domain_tier_map.csv` — domain → tier, once decided.
- `ct_results_weighted.csv` — final weighted citation dataset.
- `precedence_comparison.csv` — raw-count result vs. weighted result,
  side by side.

Nothing in here is authoritative until it's been discussed with Viveka —
treat this folder as scratch, not a second frozen dataset.

### `docs/` — reasoning and notes

- `tier_methodology.md` — the tier boundaries and weights, with the
  justification for each (this is the actual deliverable — she
  specifically wants this grounded in evidence, not "gut call").
- `session_log.md` — running dated notes on decisions made and why,
  matching the convention she already uses (`entities.py`'s docstring
  points to a "changes.md / session log" for her own date-verification
  decisions).

## Status (2026-08-16)

Data gap confirmed: the frozen citation dataset has no per-source field.
Viveka has 20/50 entities covered manually (peak-week sample) and has
now built her own harvester (`ct_artlist_harvester.py`, not yet in this
repo) for the rest. **Current blocker:** her script's week-selection
logic ("median-count week") differs from this repo's
`ct_source_harvester.py` ("max/true-peak week") — unresolved until the
Kimi/Mamba spot-check (`scripts/verify_week_match.py`) confirms which
matches her existing labeled data. Do not run either harvester for a
full pass until that's settled. See `docs/session_log.md` for the full
decision trail.

Also pending: review of 27 AMBER rows in the precision-audit labeling
file, and two more P(t) runs before **Oct 23, 2026**, when OpenAI
retires the two oldest model snapshots anchoring the earliest point on
the perception curve.
