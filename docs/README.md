# Research Documentation

This directory holds the **research documentation** of the analysis: the
record of methodological decisions, the current research state, and the
methodological specification. Together they provide the traceability chain
that ties frozen evidence to derived results.

Three documents, each a distinct layer of research traceability:

| Document | Layer | Role |
|---|---|---|
| `session_log.md` | **Decision & provenance record** | Chronological, dated entries recording every methodological decision, why it was made, and (where relevant) the commit that implemented it. The **authoritative** record: it supersedes any prose summary elsewhere. |
| `project_overview_report.md` | **Consolidated state report** | A point-in-time snapshot of the whole analysis: repository layout, collection lanes, task-by-task implementation status, blockers, and commit history for traceability. |
| `tier_methodology.md` | **Methodological specification** | The definition and rationale for source-tier construction and weighting, written as a template to be filled from observed data. |

## When to consult each document

- **To learn what was decided and why** → `session_log.md`. It is
  chronological; read the most recent entries first.
- **To get the current consolidated state of the analysis** →
  `project_overview_report.md`. Note it is a snapshot regenerated on a
  stated date and can lag the session log (see notes below).
- **To understand or extend the tier-construction method** →
  `tier_methodology.md`.

## Notes on current status

- **`tier_methodology.md` is a DRAFT / TEMPLATE.** It is intentionally not
  filled in: tier boundaries and weights are to be derived from observed
  domain data, not pre-assigned from assumption. Do not read its unfilled
  sections as results. It records the methodology *specification and
  rationale* (Approach B empirical frequency clustering, syndication
  caveat, precision cross-check, baseline exclusion rule) and its observed
  syndication examples.
- **`project_overview_report.md` is a point-in-time snapshot.** It was last
  regenerated **2026-08-18**, before the 22-entity contrast collection
  completed later that day. A few lines are therefore stale against the
  current working tree — most notably the §2 layout note calling
  `scripts/ct_artlist_audit.py` "NEW, untracked" and the §3 line
  "Status: 0/22 JSON files collected (§6, active blocker)". The collection
  is now **complete** (22/22 entities, 263 rows, archived + committed
  `cd47959`), and `ct_artlist_audit.py` is tracked. The §6 status table was
  updated in commit `e88174d`. Until the report is next regenerated, treat
  the status table, `session_log.md`, and git history as authoritative over
  the §2/§3 prose.

## Conventions

- **Decisions live in the session log**, not in prose documents, so they
  are never lost or contradicted.
- **Nothing is claimed as a result unless it is supported by a procedure
  and its derived output** (see `../data_derived/README.md`).

## Licensing

Documentation text in this directory is covered by the repository's code
license (MIT; `../LICENSE-CODE.md`).