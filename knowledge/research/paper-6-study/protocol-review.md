# Paper 6 — Protocol Review Before the First Bounded Rule-Mining Experiment

Status: internal AI methodological review of the proposed protocol, not academic peer review or an independent experiment. Reviewed 30 October 2026. Read-only assessment; no mining or execution performed by this reviewer.

## Verdict

Proceed with a bounded **observational connection-rule study**, provided the denominator, output activation, family split and evaluation target are fixed before scoring test data. The design can establish whether source-conditioned relation frequencies transfer to separated source families. It cannot yet establish normative connection rules, composite formation, behavioral success, full AMIE/gSpan/NEAT, or general instance generation.

The protocol has a sound narrow objective, explicit unknowns and a useful family-dependence safeguard. The principal risk is silently changing the prediction problem between extraction, rule scoring and baseline evaluation.

## Findings and required dispositions

| Severity | Finding | Why it matters | Required disposition |
|---|---|---|---|
| High | An output declared in a component template is not necessarily the active output in a saved occurrence. | Langflow can select one output mode; dynamic or stale declarations create false unconnected opportunities. | Specify effective-output extraction. Use explicit output-selection evidence when present; distinguish always-emitted, selectable, connected-only evidence and unresolved cases. Unknown activation must not become an absent edge. |
| High | A rule `A.output p → B.input q` merges target existence and wiring choice. | If no B exists in a graph, a failed consequent can mean target selection rather than a missed connection. | Either label the task jointly as target-and-connection association, or condition the wiring-only task on an eligible B/q occurrence. State exactly which question is evaluated. Do not alternate conventions by case. |
| High | Source-occurrence support, graph support and source-family support are different. | Many repeated A occurrences in one graph or copied family can dominate apparent confidence. | Define a canonical opportunity ID `(graph occurrence, source component occurrence, effective output)` and deduplicate repeated equivalent edges. Report grounding/occurrence confidence plus distinct-graph and family witness counts. |
| High | A frozen split can still leak through discarded duplicate-origin metadata. | Deduplicating bytes first and retaining one repository can sever links between otherwise dependent families. | Build union-find lineage over **all retained provenance origins**, including excluded duplicate copies, before choosing representatives. Then assign representatives to split groups. Assert zero group crossing. |
| High | A normalized topology fingerprint is an equivalence heuristic, not source ancestry. | Common tiny graphs can merge unrelated projects; coarse histograms can collide. | Publish the normalization recipe. Prefer exact labeled graph canonicalization/isomorphism verification for overlap grouping, or label conservative hash grouping as heuristic and disclose over-merging risk. Include ports/direction and distinguish missing from empty. |
| High | The baseline must solve the identical opportunity-level target task. | Comparing conditional rule confidence to global edge frequency uses different denominators and rewards popular targets unfairly. | Construct a source-agnostic baseline on development opportunities, with the same target tuple vocabulary, unknown policy, candidate set, none outcome and test denominator. Define tie breaking before test. |
| Medium | Fanout makes the target multi-label, not ordinary one-class prediction. | One source output may connect to several B/q tuples or several occurrences of the same tuple. | Represent each opportunity's observed target tuples as a set. For top-one evaluation, explicitly score whether the chosen tuple is present, alongside coverage/abstention and observed set size. Do not call this exhaustive reconstruction. |
| Medium | Multiple destination occurrences can share `(B,q)`. | Type-and-port association loses occurrence selection information. | Collapse only for the type-relation prediction task; retain underlying destination witness IDs. Do not infer which B instance to connect or count all compatible pairs as independent evidence. |
| Medium | Graph occurrence and artifact are not one-to-one. | Nested export bundles can contain multiple graphs, while exact deduplication only removes identical files. | Include graph JSON pointer in identity; optionally deduplicate normalized graph copies with a documented policy. Report file, graph and opportunity counts separately. |
| Medium | Port strings may be serialized handle objects, versioned aliases or incomplete. | Naive string parsing creates false relation types or merges incompatible ports. | Preserve raw handles and normalization evidence; reject or mark unknown on unresolved source/target handles. Pin native component signatures rather than quietly aliasing by display name. |
| Medium | A complete `edges` array establishes static observation, not behavior or completeness of an intended workflow. | Many examples are partial sketches and may intentionally leave outputs unused. | Name zero-edge cases "no serialized outgoing connection observed". Never label them invalid, required to connect, or negative behavioral outcomes. |
| Medium | One holdout pass is only credible if model selection is restricted to development. | Thresholds, smoothing, rule sizes, source grouping or reporting choices can be tuned after seeing outcomes. | Save protocol/config/split hashes and selected candidates before test. Record first test outcome unchanged; subsequent revisions require a separately labeled development or fresh evaluation round. |
| Medium | Giant lineage groups may leave too little varied evaluation data. | Repo overlap and topology unions can connect most corpus into one family. | Report component-size distribution, largest-group share and train/test family counts. If a valid separated test is unavailable, report the limitation rather than splitting the giant group opportunistically. |
| Medium | Mining eligibility is not extraction validity. | Static index checks cannot guarantee all edges resolve to declared ports/types. | Emit per-stage attrition and reasons; eligibility must not be presented as all graphs having trustworthy opportunities. |
| Medium | Type-only/target-frequency predictors cannot discover packaging boundaries. | A high-quality edge relation does not identify purpose, external interface or reusable unit. | State that first results are relationship rules only. Composite boundary proposals require a later contract and separate evaluation. |

## Minimal frozen protocol

| Item | Definition to freeze |
|---|---|
| Corpus | Index hash, source manifest hashes, eligible/artifact exclusions, file hashes and nested graph pointers. |
| Unit | Source occurrence/effective-output opportunity with raw source and normalized signature evidence. |
| Antecedent | Native source component type plus resolved effective output signature; optionally version/type attributes under explicitly fixed grouping. |
| Consequent | Existence of at least one observed outgoing edge to normalized `(target native type, target input signature)`. This is a joint target-and-connection association unless target existence is in the antecedent. |
| Observation statuses | Assessable nonempty target set; assessable empty set; unresolved/unknown. Inactive outputs excluded from opportunity population. |
| Count convention | At most one witness per target tuple per source-output opportunity; retain all underlying edge witnesses separately. |
| Rule confidence | Development opportunities satisfying body and head divided by development assessable opportunities satisfying body. Name this observational occurrence confidence; do not call it PCA confidence. |
| Candidate selection | Development-only minimum body count, minimum distinct graph/family count, confidence threshold or top-one selection, ties and abstention rules. |
| Baseline | Development-only source-agnostic target association with exactly the same opportunity universe and target semantics. |
| Split | Provenance-plus-normalized-overlap union groups formed from all origin records; deterministic group assignment, fixed seed if random, no shared group. |
| Evaluation | First-pass test top-one membership accuracy among attempted predictions, opportunity coverage, unknown attrition, empty-output handling and family-level summaries. Report raw numerators/denominators. |
| Generality | Report rules supported by one family separately; no generalization claim from single-source-family support. |
| Limits | Static, supplied-corpus, type-relation association only. No behavior, normative dependency, composite quality or general emergence conclusions. |

An acceptable simpler evaluation is a fixed binary rule-transfer task: for each preselected rule, compute test body/head witnesses, absence observations and unknowns. That avoids pretending a ranked multi-target predictor reconstructs a whole graph. Choose one primary endpoint in advance; others are descriptive.

## Specific checks to document in the implementation record

- All edge endpoints refer to non-note component occurrences; every retained handle maps unambiguously to a declared port or an explicitly supported saved-export handle representation.
- Selected-output or dynamic-port uncertainty is counted and surfaced, not silently resolved from connected edges alone.
- A connected output can be observed even when its declaration is missing, but then it belongs to a separately labeled observed-edge-only analysis; it must not expand the unconnected-opportunity denominator.
- Repeated raw edges do not increase support; fanout to the same type/input produces one type-level witness while preserving all edge IDs.
- Unknowns are reported against the original candidate population, so excluding difficult graphs cannot inflate apparent reliability invisibly.
- No source URL, repository name or graph ID enters the mined antecedent or predictor unless provenance memorization is explicitly the object of study.
- Candidate corpus counts and evaluable opportunity counts are separately reported. Exact byte uniqueness and normalized graph equivalence are also distinct.
- Confidence must not be equated with a calibrated probability or causal implication; source-family macro summaries and a paired baseline difference improve interpretation, but small or dependent samples remain limited.

## Critical interpretation guide

| Possible result | Defensible statement | Unsupported leap |
|---|---|---|
| Conditional predictor beats global frequency | Source type/output context improves this observed target-association task on the specified separated set. | We learned how to build composites. |
| High development confidence falls in evaluation | Rules may reflect source-family conventions, sparse evidence or representation mismatch. | Rule mining cannot work in general. |
| Both methods perform well | Common target patterns may explain much of the task; incremental value may be small. | Sophisticated search is unnecessary for every future task. |
| Many cases unknown | Saved exports do not support the planned denominator without better extraction evidence. | Missing ports are false connections. |
| Giant family prevents a useful split | Corpus dependence prevents the planned independent-family evaluation. | Randomly split individual graphs and call them independent. |

## Source grounding

Port modes and version concerns are grounded in [Langflow's official component documentation](https://docs.langflow.org/components/). The distinction between conditional-rule support and assumptions about missing evidence follows [AMIE 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC7250613/). Group-separation mechanics are documented in [scikit-learn grouped cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data); our source-family definition remains a study-specific judgment. Selection-bias concerns follow [Cawley and Talbot](https://www.jmlr.org/papers/v11/cawley10a.html). Full curated source limits and adaptation cautions are in `knowledge/research/paper-6-corpus/literature-review.md`.

## Review conclusion

The bounded study is viable if framed as mining and evaluating **descriptive source-conditioned relation rules**. Freeze the opportunity policy and baseline before evaluating. The highest-priority repairs are active-output treatment, identical baseline denominators and preserving duplicate provenance in family grouping. A test can legitimately return insufficient evaluable data; that is a useful result, not a reason to weaken the protocol after looking.

## Language decision checkpoint: Prolog

Implementation is paused while language choice is reconsidered. This review remains conceptual; no miner or experiment was run.

Prolog can represent the scoped component/port relations and evaluate supplied rules through unification and search. That is **inference over rules we provide**. Discovering rule bodies, selecting variables/constraints, measuring support and choosing generalizations is a separate **inductive logic programming or rule-mining** task. Choosing Prolog does not automatically implement discovery, confidence accounting, family isolation or experiment tracking.

| Concern | Prolog-specific design requirement | Language-independent requirement |
|---|---|---|
| Inference versus induction | Separate predicates that query a fixed rule from code that enumerates/refines candidate rules. | Record which knowledge is supplied and which is learned. |
| Negation as failure | A failed goal is not automatically an explicit negative; only use failure for a predicate whose relevant scoped world is declared complete. | Preserve unknown/assessable-absence distinction. |
| Finite search | Bound rule size, predicate vocabulary, variable introduction and recursion; guard against duplicate substitutions and nontermination. | Record budgets and search-limit outcomes. |
| Counting | Deduplicate canonical opportunities before `findall`-style collection or aggregation. | Fix support unit and denominator. |
| Provenance | Carry graph/source identifiers as context and witness references, not accidental predictive variables. | Keep duplicate origins and family membership. |
| Interchange | Use an explicit JSON↔fact mapping with typed values and stable graph-local identities. | Preserve original exports and extraction version. |

A meaningful language comparison would hold facts, candidate grammar, hard constraints, counting semantics and budget constant, then compare clarity, traceability and performance of the same narrow operation. It should not compare a supplied Prolog rule against a Python induction engine and conclude that one language discovers better rules. No language winner is recommended by this checkpoint.
