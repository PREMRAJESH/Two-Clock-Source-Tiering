# Source tier methodology — DRAFT / TEMPLATE

Status: not yet filled in. Fill this in only after real domain data
exists in `data_derived/ct_source_results.csv` — do not pre-assign tiers
from assumption.

## 1. What this is testing

Does weighting citation mentions by source authority produce a stronger
(or tighter) relationship with AI-perception onset than raw, unweighted
citation counts do? (Paper's Section 4.6 precedence test, rerun on a
weighted C(t).)

## 2. Tier definitions

| Tier | Definition | Example domains (fill in once observed) | Weight |
|---|---|---|---|
| 1 | major national/international news, Wikipedia, government | TBD | TBD |
| 2 | trade press, industry publications | TBD | TBD |
| 3 | blogs, forums, low-authority sites | TBD | TBD |

*Note on Upstream Tiering Confound:* Primary tier assignment uses Approach B (empirical frequency clustering on $\log(\text{breadth} \times \text{volume})$). High-volume syndication aggregators (e.g. `yahoo.com`, `msn.com`) carrying republished wire stories (AP/Reuters) accumulate high volume and entity breadth, which can cluster them into Tier 1 or Tier 2 based on republication volume rather than original reporting authority.

## 3. Evidence for the boundaries

Do NOT justify boundaries by "this outlet feels important." Justify by:

- **Empirical Frequency Clustering (Approach B):** Natural breaks (Jenks optimization) on $\log(\text{breadth} \times \text{volume})$ across all observed domains in `ct_source_all.csv`, evaluated with Goodness of Variance Fit (GVF $\ge 0.70$).
- **Syndication Upstream Impact:** Acknowledge that Jenks cluster breaks reflect raw domain frequency in GDELT, meaning syndication aggregators inherit higher placement due to high republication volume.
- **Precision Audit Cross-Check:** Compare domain prevalence between high-precision (PASS) and low-precision (FAIL) entities in `inputs_frozen/ct_artlist_precision.csv` (used as a sanity cross-check, since precision audits name-relevance rather than authority).

## 4. Evidence for the weights

[Not gut-call numbers — derive from something checkable: e.g. an
independent authority ranking, or an empirical sensitivity check showing
which weight ratios change the precedence result and which don't.]

## 5. Baseline exclusion rule (verified against paper)

The paper's 33-entity testable set is derived as follows (Viveka,
confirmed against Sections 4.5 and 5.4 of the paper text):

    TESTABLE 33 = all 50 entities MINUS:
      10 precision-audit FAIL (Section 4.5, Table 1):
          DBRX, Kimi, Ideogram, Lovable, Gemini (Google model),
          Dream Machine, Liquid AI, Mamba, Operator, vLLM
      7 no-onset entities (Section 5.4):
          OpenAI o1, OpenAI o3, DeepSeek, DeepSeek-R1,
          Manus, World Labs, Bolt.new

**The `self_ref_openai` flag in `entities.py` is NOT part of this
baseline.** GPT-4, GPT-4o, and Sora are included in the 33. The flag
exists for a separate robustness analysis (self-recognition confound on
OpenAI entities probed on an OpenAI ladder) but is a distinct, clearly-
labeled variant — not the baseline.

Reproduced exactly by `scripts/reproduce_baseline.py` (2026-08-17):

| | Ramp precedes onset | Median lead (days) | p-value |
|---|---|---|---|
| Raw baseline (floor=3) | 28/33 (85%) | 83 | 6.62 × 10⁻⁵ |
| Raw baseline (floor=5) | 28/33 (85%) | 83 | 6.62 × 10⁻⁵ |
| Weighted | TBD | TBD | TBD |
| Weighted (excl. self_ref_openai) | TBD | TBD | TBD |

## 6. Caveats & Limitations

- **Syndication and Domain Dilution:** Domain-level tiering counts every article URL as an independent citation of its hosting domain (e.g. `yahoo.com`, `msn.com`). It does not deduplicate syndicated wire stories (e.g. a Reuters or AP article republished verbatim across multiple aggregators). Consequently, domain-level frequency metrics may under-count original wire-service originators and over-count high-volume syndication aggregators. This is a recognized limitation of domain-level GDELT ArtList sampling.
- **Capped windows:** Carry forward any `capped` windows from the harvester — weighted scores for those weeks rest on a partial source sample (250-article limit).
- **Tier ambiguity:** Note any domains near cluster boundaries that didn't cleanly separate; sensitivity checks perturb these boundary domains to verify result stability.
- **Entity name mismatch between CSVs:** The perception CSV uses parenthetical disambiguators (e.g. `Cursor (the AI code editor)`) while the citation CSV uses short names (e.g. `Cursor`). 14 of 50 entities are affected. Any script joining these datasets must use a name bridge (strip parentheticals) or it will silently drop entities.
