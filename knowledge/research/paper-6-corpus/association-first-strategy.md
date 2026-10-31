### Updated Method Strategy — Association Discovery Before Relational Mining

**Decision:** Introduce association rule mining as an exploratory first stage. Retain Python/Jupyter, PyClause and AnyBURL for the subsequent relational stage. Prolog remains a candidate for richer explicit reasoning; no implementation winner or speedup has been measured. This decision supersedes the earlier recommendation to begin directly with relational mining.

| Stage | Proposed tool / artifact | Question answered | Handoff |
|---|---|---|---|
| 1. Freeze and normalize | Pinned corpus, provenance and typed extraction | What is actually present and observable? | Source-linked graph facts and eligible transactions |
| 2. Association discovery | mlxtend FP-Growth followed by association_rules | Which declared features co-occur, and which associations exceed their background prevalence? | Ranked exploratory associations with support, confidence, lift, exceptions and family coverage |
| 3. Inspect and design the relational encoding | Mapping ledger and source witnesses | Which associations suggest meaningful predicates, context or search restrictions? | Documented encoding choices; retained full eligible facts and a baseline encoding |
| 4. Relational rule learning | PyClause with AnyBURL; AMIE as a possible comparison | Which explicit variable-linked relationships can be learned in the chosen representation? | Candidate relational rules, exact evidence accounting and declared engine scores |
| 5. Independent checks and interpretation | Separate-family evaluation and boundary checks | Do rules transfer, and what do they actually establish? | Supported, challenged or inconclusive claims; no automatic composite promotion |

**Why the preliminary stage helps:** It can identify promising component combinations, typed edge features and resource dependencies to investigate. It cannot decide the correct ontology, recover ordering discarded by a basket representation, establish causal necessity, or prove a useful composite boundary. Speed and usefulness on this corpus remain hypotheses.

#### Transaction design comes first

| Exploratory view | Transaction / possible items | What must remain explicit |
|---|---|---|
| Whole graph presence | One eligible deduplicated graph; native component types and observable resource kinds | Presence ignores multiplicity, role and wiring; never interpret co-presence as a connection |
| Typed connection features | One graph; items encoding observed source type/port → target type/port relations | Direction and port identity must be encoded in the item itself; association does not add those semantics |
| Local neighborhood | One scoped occurrence neighborhood under a fixed definition | Many neighborhoods in one graph are dependent; use separate denominators and family-aware summaries |

Run these as separate analyses rather than mixing transactions with incompatible meanings. Do not include source IDs or unique occurrence IDs as predictive basket items. Keep them as provenance. Exclude configuration values, credentials and copied code from the item vocabulary. Distinguish observed absence from unknown extraction; record coverage and avoid silently replacing unknowns with False.

#### Critical controls

- Establish source families and the development/evaluation split **before** exploratory association mining. Choosing features using every graph would leak evaluation information.
- Count exact duplicates once while preserving every origin. Report both graph-level frequency and source-family breadth so mirrors cannot masquerade as independent support.
- Define the transaction population, minimum support/count, itemset-size cap, rule filters and parameter search bounds before runs. Candidate rule counts can grow combinatorially; runtime is not guaranteed by using FP-Growth.
- Report support and confidence together with lift and raw counts. High confidence can result from a ubiquitous consequent; high lift can rest on very few cases. Thresholds and uncertainty treatment remain to be specified.
- Associations suggest an encoding; they must not become the only facts supplied to the relational learner. Preserve the full eligible fact store and compare an association-guided encoding/search bias with a baseline that does not use that guidance.
- PyClause's AnyBURL and AMIE interfaces have their own rule languages and confidence definitions. Do not equate itemset confidence with their scores, or transfer a measured association into a hard constraint.
- Graph-local occurrence identities must prevent cross-template joins. Packaging, required-input preservation and behavioral validity remain separate checks.

**Immediate milestone:** An association evidence table linked to real source graphs, followed by a reasoned mapping from selected associations into a candidate relational representation. This is the new first experiment; no mining has run yet.

Primary implementation references: [mlxtend FP-Growth](https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/), [mlxtend association rules and metrics](https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/), [PyClause learning interfaces and scoring caveats](https://pyclause.readthedocs.io/en/latest/feature/learning.html), [AnyBURL official project](https://web.informatik.uni-mannheim.de/AnyBURL/).
