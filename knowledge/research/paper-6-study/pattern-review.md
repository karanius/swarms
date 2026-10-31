# Paper 6 — Connected-Pattern and Association Explorer Review

Status: internal AI methodological review. Exploratory whole-corpus analysis; no held-out evaluation, generalization claim, behavior claim or composite-formation claim. The prior corpus topology explorer must remain separate and usable. This reviewer owns this critique only and does not run mining experiments.

## Protocol assessment

The proposed design studies **co-occurrence of resolved incident relation types around an actual component occurrence**. That is a defensible, narrow connected-neighborhood mining task. A transaction is not an entire workflow, not a component type, and not an independent research sample. A pair of items shares its center occurrence but may also share the same outer occurrence; therefore two item types do not imply three distinct nodes.

| Topic | Required interpretation / check | Consequence if ignored |
|---|---|---|
| Transaction identity | `(original graph identity, scoped center occurrence)` once, restricted to nonfixture origins and at least one incident recorded edge | Repeated exports or type aggregation inflate support or manufacture neighborhoods |
| Item identity | `(centerType, direction relative to center, neighborType, sourcePort, targetPort)` with source/target roles unambiguous | Incoming edges can be mislabeled as outgoing; port identities can swap |
| Set semantics | Repeated identical incident tuples count once within a transaction; retain all edge witnesses separately | Parallel edges inflate confidence/support |
| Full resolution | All incident records relevant to a center must resolve endpoints, component types and handles; unknown centers are excluded and counted | Partial parsing can make missing consequences look like real absence |
| Unknown attrition | Report reasons and the prefilter population; a single unresolved incident edge may remove many otherwise parseable relations | Clean-subset findings are mistaken for full-corpus findings |
| Motif topology | Two tuples guarantee common center only; outer endpoints may alias, and reciprocal/parallel/self-loop edges require explicit depiction | A three-node chain is invented from a two-node reciprocal relation |
| Witness visualization | Use actual edge endpoint IDs and an original source graph, not a generic guessed arrangement | The diagram does not demonstrate the claimed mined pattern |
| FP-growth bounds | `max_len=2`, minimum transaction count 5, binary baskets; generate one-item antecedent → one-item consequent only | Results are misrepresented as unbounded rule mining or relational Horn induction |
| Confidence | `count(A and B)/count(A)` over the same assessable transaction population | Different denominators produce invalid scores |
| Lift | `confidence(A→B)/P(B)` on that population; label observational | Popular consequents can yield high confidence without conditional specificity |
| Support units | Transaction counts primary; graph and source-family witness counts separate | Many occurrences from one large graph appear as broad evidence |
| Family counts | Retain all duplicate origins when unioning repositories/exact overlaps; label conservative grouping, not independence | Dedup representative loses known lineage; numeric family count overclaims independent replication |
| Absence examples | Body item observed and head item absent in a fully parsed neighborhood; no claim of error, incompleteness or missing required behavior | Descriptive co-occurrence becomes a normative connection law |
| Corpus exposure | All corpus already inspectable in viewer; mining is exploratory | Claimed held-out or independent validation is false |
| Nonfixture selection | Define whether a duplicate with at least one nonfixture source is retained; display fixture origins separately | Ambiguous filtering changes denominators or loses provenance |

## Intended output and language

Call the output a **connected incident-pair pattern** and its directional association an **observational one-to-one rule**. The direction of implication is statistical conditioning; it is different from the directions of the two underlying workflow edges. A high score says these two incident relation types co-occur in this analyzed dataset under the stated representation. It does not say either relation causes, requires, should create or validates the other.

The minimum-five threshold is a transaction-count floor, not five independent graphs or families. Publish both counts before implying breadth. With no behavioral labels, there is no validated fitness function for useful composite formation. This experiment is neither AnyBURL nor an AMIE/gSpan/NEAT implementation.

## Review checklist for the implementation

- Candidate pair counts equal recomputation from transaction witness IDs.
- Singleton and pair support use the identical total number of assessable nonempty transactions.
- No rule has identical antecedent and consequent; each item belongs to the same center type in a pair.
- Anti-parallel, fanout, repeated-edge and shared-neighbor cases remain distinguishable in examples.
- When center IDs are graph-local, every witness also carries a graph key; nested graphs cannot cross-join.
- Unknown endpoint edges are retained in raw analysis and invalidate the intended neighborhoods where incident membership can be determined. If an unresolved endpoint prevents determining one center, report that limitation rather than treating all other centers as safely unaffected by inference.
- Source component/port type is read from archived evidence, not fetched current definitions or display labels.
- Family numerator counts each group once per pair or singleton; union labels use all origin repositories rather than just the representative URL.
- No configuration secrets, source code or literal credential values appear in generated explorer datasets.
- Existing corpus-map endpoints, routes and notebook embed remain intact; the new explorer has a distinct route and clear title.

## Suggested reporting table

| Metric | Required number |
|---|---|
| Eligible original graph objects | [Before incident-resolution filtering] |
| Non-note center occurrences with incident edges | [Prefilter opportunity count] |
| Assessable transactions retained | [Miner denominator] |
| Excluded neighborhoods by reason | [Missing type, endpoint, handle, other; overlaps disclosed] |
| Unique relation items | [After tuple normalization] |
| Frequent singleton/pair itemsets | [Minimum count and max length stated] |
| One-to-one rules | [Any additional confidence/lift filter stated] |
| Rule witness graph and family breadth | [Distinct counts separate from occurrences] |
| Same-outer-node versus distinct-outer-node witnesses | [Topology mix, not inferred from item names] |

## First verdict

Conceptually viable as an exploratory relationship catalog. Proceed only with literal counting labels, actual witness diagrams and explicit unknown attrition. Implementation review is pending; the protocol assessment alone does not establish code correctness or visible UI behavior.

## Implementation review — `mine_patterns.py`

Reviewed the source statically after it was written. This reviewer did not run the miner or tests. The implementation does the intended bounded FP-growth pass, not a relational variable-rule learner. Its output is exploratory and it explicitly avoids held-out, behavioral and composite claims.

### What the source implements consistently

- `neighborhoods` scopes a center to its original graph and discards neighborhoods with an unresolved recorded endpoint/port/type, a self-loop or more than 24 distinct incident feature types. Zero-incident centers are separately counted.
- Items are JSON-encoded tuples of center type, direction, neighbor type and source/target port names. Each center's items are a set; duplicate parallel relation tuples do not multiply transaction support. Edge IDs remain in `edgeWitnesses`.
- `score_rule` recomputes body, joint and body-without-head transaction sets. Confidence agrees with the external library output through an assertion. All retained rule sides share a center type.
- `lift` uses the head prevalence among transactions with that common center type; `globalLift` retains the library's all-center value. These measures have different reference populations and must stay visibly named.
- Source-group union uses every origin repository attached to every deduplicated graph, including fixture origins, before the nonfixture mining restriction. This preserves known exact-copy bridges. It does not perform topology-based near-copy clustering; its limits correctly say modified copies can remain undetected.
- Full rule outputs and all witness/absence lists are written separately; the UI index keeps only the first 200 rules ranked by recorded group/graph breadth and counts. Display truncation is not mining truncation.

### Remaining qualifications and concrete fixes

| Priority | Observation in source | Recommendation |
|---|---|---|
| Required wording | `resolved` and nonempty parsed port names establish saved-edge handle resolution. The miner itself does not verify that each port exists in the archived component declaration or that endpoint data types match. | Say **resolved saved-handle neighborhoods**, not type-compatible or declared-port-valid neighborhoods. Include this limit beside results. Any stronger compatibility claim requires a separate check. |
| Reproducibility | Freeze hashes `topology/index.json`, corpus index and miner source, but not each derived `topology/graphs/<id>.json` read for transactions. Index rows contain original-file hashes, not complete derived-graph hashes. | Record a deterministic digest over graph ID plus derived-graph bytes or a per-file digest manifest. That pins the exact analyzed data rather than merely its index. |
| Count guard | FP-growth threshold uses a small epsilon to retain exact count-five itemsets; counts are then independently recomputed. | Assert `jointCount >= minimumJointNeighborhoods` and finite, valid confidence/lift on the final rules. This makes the published count contract explicit. |
| Repeat-run hygiene | `rules/` is created but prior rule files are not removed when a subsequent run yields fewer/different IDs. | Generate into a fresh versioned run directory or remove stale owned outputs safely. Endpoints should expose only current catalog IDs. Otherwise an old rule URL may look current. |
| Alias topology | Rule features intentionally lose outer occurrence identity; returned witness contains actual edge IDs, not a precomputed distinct-node count. | UI must derive its diagram from that actual witness graph and display the number of distinct endpoint occurrences. Do not draw a canonical three-node motif just from two features. |
| Selection bias | Dropped-neighborhood reason counters are grouped; unknown endpoint, type, port and self-loop share one reason. | Current combined category is honest if labeled exactly; separate reason counts are preferable when interpreting extraction limitations. Do not report it as only malformed data. |
| Search bounds | `maximumDistinctIncidentFeatures=24` excludes high-degree or heterogeneous centers, not only computationally large workflows. | Publish excluded count and note that hubs may be disproportionately removed; results concern the bounded subpopulation. |
| Statistical interpretation | No confidence intervals, significance correction or independently sampled evaluation are computed. | Appropriate for this exploratory catalog. Do not attach significance or calibrated predictive probability language to the percentages. |

### Reviewed implementation verdict

The source supports an **exploratory, source-traceable association catalog of observed incident relation pairs**, with center-conditioned confidence/lift and actual witnesses. Its methodological claims are acceptable under the wording and reproducibility qualifications above. No automatic composite or general-rule learning claim follows. Runtime correctness and browser interaction require the parent agent's separate evidence; this static review does not substitute for them.

## Final disposition pass

Static re-review covered the current `mine_patterns.py`, `verify_patterns.py`, `frontend/server/pattern-analysis.mjs`, and the notebook's current Sections 1–14. The reviewer read the persisted verification report; the reviewer did not rerun experiments or tests.

| Earlier concern | Verified disposition in current sources | Status |
|---|---|---|
| Exact analyzed data not frozen | Miner hashes each loaded derived graph file and combines IDs/hashes into `derivedGraphFilesSha256`; verifier recomputes that digest and checks topology index/miner hashes. | Addressed for the frozen derived inputs. |
| Minimum-five count implicit | Final rule loop asserts recomputed `jointCount >= minimumJointNeighborhoods`; verifier also checks at least five. | Addressed. |
| Stale rule files reachable | API accepts only validated hexadecimal IDs present in current `all-rules.json`, before reading any per-rule file. | Addressed at the serving boundary; old files can remain as unserved local residue. |
| Invented three-node previews | `previewEdgeIds` selects one actual body edge and, when present, one actual head edge. Verifier checks incidence, feature identity and one/two-edge preview size against original derived graph records. | Addressed in evidence generation; UI drawing remains separately browser-verified by parent. |
| Saved handles described as type-safe ports | Exported limits and notebook Sections 2, 5, 11 and 12 explicitly limit claims to saved named handles and distinguish declaration, activation and compatibility. | Addressed in the implemented-study claims. |
| Whole-corpus results relabeled held out | Current Sections 3, 4, 8 and 12 explicitly state whole-corpus exploration and no untouched/generalization evaluation. | Addressed in the implemented-study claims. |
| Score/count witness mismatch | Persisted `verification.json` reports 890 rules recounted, 62,265 witness previews and 981 source graphs checked, with frozen-data hashes matched. Source verifier independently recounts persisted transaction evidence rather than trusting only FP-Growth metrics. | Recorded verification supports implementation consistency, not independent behavioral evaluation. |
| UI output truncation | Display cap now 1,000; all 890 rules fit this run; complete rule summaries and examples remain exported. | Addressed for this run; future cap remains explicit. |

**No remaining blocking methodological issue was found for the narrow exploratory catalog as currently claimed.** The notebook properly separates recurrence from composite usefulness, source groups from independent samples, and observational absence from violations. Core Section 1–14 claims match the bounded method and reported verification scope.

### Nonblocking editorial cleanup

The retained pre-experiment strategy/background cells still contain older instructions such as establishing a development/evaluation split before exploration, and old prose saying no implementation/results exist. Section 14 labels the earlier dossier as historical background, which prevents treating its direct-relational-first recommendation as current. A conspicuous **historical plan / superseded by current exploratory study** label immediately above each retained block would further reduce confusion. In particular, the sentence saying the earlier plan is now implemented should specify **the association-discovery slice**, because its later relational/generalization stages are explicitly not implemented. These are narrative consistency improvements, not evidence that the current exploratory results were falsely held out.

A second limit remains inherent rather than repaired: the verifier checks counts and source-edge witnesses against the extracted/persisted representation. It does not establish the extractor's universal semantic correctness, archived-port activation, behavior, or transfer to new sources. The paper currently discloses those limits appropriately.
