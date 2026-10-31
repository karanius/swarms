# Relational engine research for Paper 6

Status: primary-source research only, 30 October 2026. No package installed, downloaded workflow executed, or experiment run by this research agent. The implementation owner must record actual revisions, hashes, runtime and results. Recommendations below are design inferences, not facts established by the libraries.

## Recommendation

Use Python/Jupyter as the experiment controller, AnyBURL as the bounded rule learner, and PyClause for applying/recounting supported rule types **if its compiled extension works in the selected runtime**. The official installation instructions explicitly document Windows/Linux; they do not establish support for this Apple Silicon macOS host. A direct official AnyBURL JAR run is a useful fallback, but must be disclosed as such rather than called a successful PyClause integration. [Installation](https://pyclause.readthedocs.io/en/latest/start/installation.html), [AnyBURL](https://web.informatik.uni-mannheim.de/AnyBURL/).

Do not begin by claiming a full composite-rule learner. First ask whether learned rules transfer a source-scoped structural relationship to separated examples. Follow any proposed group with the existing boundary checks. Connectivity, exposed inputs and required-field accounting do not establish purpose or behavioral usefulness.

## Verified installation and runtime facts

| Item | Verified fact | Source / practical consequence |
|---|---|---|
| Python package | Official install is editable checkout or `pip install git+https://github.com/symbolic-kg/PyClause.git`; recommendation is Python 3.7+ | [Installation](https://pyclause.readthedocs.io/en/latest/start/installation.html). Pin a commit rather than moving master. |
| Native extension | `setup.py` builds `c_clause` with pybind11 and C++14, adds `-fopenmp` at compile/link time for Unix, and lists numpy/flatdict/pyyaml dependencies | [setup.py](https://raw.githubusercontent.com/symbolic-kg/PyClause/master/setup.py). A Python package import alone does not prove native functionality. |
| Build requirements | pyproject declares setuptools≥42 and pybind11≥2.10 | [pyproject.toml](https://raw.githubusercontent.com/symbolic-kg/PyClause/master/pyproject.toml). Record resolved build dependencies. |
| Learner binaries | PyClause learning docs say AMIE/AnyBURL JARs ship with the package and were compiled under Java 8 | [Learning](https://pyclause.readthedocs.io/en/latest/feature/learning.html). Java is still a runtime prerequisite. |
| Version mismatch to resolve | PyClause docs name AnyBURL-23-1; official homepage currently names 23-1x, a later bugfix | [Learning](https://pyclause.readthedocs.io/en/latest/feature/learning.html), [homepage](https://web.informatik.uni-mannheim.de/AnyBURL/). Record actual JAR hash/class/version; do not silently equate releases. |

The source build's unconditional Unix OpenMP flags are a concrete compatibility concern on macOS; this is an inference from build code, not proof that no compatible toolchain can build it. Avoid changing global compilers or the existing research environment merely to satisfy the package; isolate new dependencies.

## Exact learning interface

The official example uses `clause.Learner`, `clause.Options`, a training triple file and a rule-output path. The wrapper accepts original learner options under `raw`. This is an adapted bounded configuration, not a tested run:

```python
from clause import Learner, Options

opts = Options()
opts.set('learner.mode', 'anyburl')
opts.set('learner.anyburl.time', 30)
opts.set('learner.anyburl.raw.MAX_LENGTH_CYCLIC', 2)
opts.set('learner.anyburl.raw.WORKER_THREADS', 1)
opts.set('learner.anyburl.raw.THRESHOLD_CORRECT_PREDICTIONS', 5)
opts.set('learner.anyburl.java_options', ['-Xmx2g', '-Dfile.encoding=UTF-8'])
learner = Learner(options=opts.get('learner'))
learner.learn_rules(path_data='train.tsv', path_output='rules.txt')
```

The API shape and learner/time/raw keys come from [Learning Rules](https://pyclause.readthedocs.io/en/latest/feature/learning.html); heap-option syntax and additional raw defaults are documented in [config-default.yaml](https://raw.githubusercontent.com/symbolic-kg/PyClause/master/clause/config-default.yaml). The chosen bounds are our design choices. Use a subprocess with an external timeout as well; a learner time budget alone is not an application watchdog.

Direct JAR route, if selected: the current official entry point is `de.unima.ki.anyburl.Learn`, invoked with a properties file. Input is whitespace/tab-separated subject–relation–object triples. Token names should be alphabetic-leading and at least two characters, or use `SAFE_PREFIX_MODE=true`. `SINGLE_RELATIONS` restricts head predicates. [Official execution guidance](https://web.informatik.uni-mannheim.de/AnyBURL/).

No documented fixed random-seed option was established in the sources inspected. One worker reduces concurrency variability but does not prove deterministic learning. Preserve raw learned rule files and run identifiers; repeat equal-budget runs if making comparative claims.

## Rule language and scores

PyClause supports binary Horn clauses with one head atom. Its B-rules have a path-shaped body connecting head variables; U_c rules contain a head constant and a body constant; U_d rules contain a head constant and an existential body endpoint; zero rules express distributions. Arbitrary multi-branch conjunctions are not automatically in this language. Spacing and variable ordering are significant to the parser. Constants used for application must exist in the loaded graph. [Rule types and syntax](https://pyclause.readthedocs.io/en/latest/data/rule_types.html).

| Quantity | Meaning / treatment |
|---|---|
| Association confidence | Conditional frequency of one binary neighborhood feature given another; existing study's denominator is center neighborhoods |
| AnyBURL learner confidence | Engine rule statistic; save exactly as emitted and independently recount relevant accepted rules |
| PyClause raw rule statistics | `RulesHandler.get_statistics()` gives `[number_of_predictions, support]` per input rule; counts are based on the Loader's data graph |
| Application smoothing | Default config uses support divided by body-grounding count plus an unseen-example allowance; weights also vary by rule type |
| AMIE comparison | PyClause docs warn AMIE output uses PCA confidence and differs from AnyBURL statistics |

[Rule confidence](https://pyclause.readthedocs.io/en/latest/feature/rule_confidence.html), [default scoring configuration](https://raw.githubusercontent.com/symbolic-kg/PyClause/master/clause/config-default.yaml), [learning score caveat](https://pyclause.readthedocs.io/en/latest/feature/learning.html).

Do not label any engine confidence a probability of composite usefulness or equate it with the current association confidence/lift. Do not aggregate rule confidences without stating the method.

## Exact application/recount interface

Load the evidence graph as `data`; `filter` and `target` serve particular query/ranking functions rather than magically creating a held-out evaluation. A Loader can load data only once, so use separate loaders for separated evidence graphs. [Loading data](https://pyclause.readthedocs.io/en/latest/data/loading_data.html).

```python
from clause import Options
from c_clause import Loader, RulesHandler

opts = Options()
opts.set('rules_handler.collect_predictions', True)
opts.set('rules_handler.num_threads', 1)
loader = Loader(options=opts.get('loader'))
loader.load_data(data='application-evidence.tsv')
rh = RulesHandler(options=opts.get('rules_handler'))
rh.calculate_predictions(rules=['head(X,Y) <= body(X,Y)'], loader=loader)
predictions = rh.get_predictions(as_string=True)  # one list per input rule
statistics = rh.get_statistics()                # predictions, support
```

This is the documented interface with a schematic rule. `RulesHandler` receives rule strings directly; loading those rules into Loader first is unnecessary. Full materialization can be expensive; disable prediction collection for statistics-only passes and retain a bounded set for human evidence inspection. [Materialization](https://pyclause.readthedocs.io/en/latest/feature/rule_materialization.html), [statistics](https://pyclause.readthedocs.io/en/latest/feature/rule_confidence.html).

## Representation decision: two distinct experiments

The following is our proposed design, not a built-in Langflow adapter.

| Encoding | Actual question it can answer | Important limit |
|---|---|---|
| `(occurrence, typed_port_edge_relation, occurrence)` with graph-scoped occurrence IDs; relation token encodes source type, source port, target type, target port | Can an alternative observed path predict another endpoint connection? | Tree-like source graphs may have few recurring redundant paths. Zero useful rules is a valid result, not a reason to invent shortcut positives. |
| `(center_occurrence, has_feature, feature_constant)` where a feature includes center type, direction, neighbor type and both ports | Does an observed feature predict another feature at the same scoped center? | A U_c rule here is a relational serialization of the association problem. It is not evidence of learning larger topology or a complete composite boundary. |
| Shared entity nodes for native types, port names or features | Convenient schema/metadata representation | Variables can walk through those shared entities into another workflow. Namespacing occurrence IDs alone does not prevent such cross-graph joins. |

For a first reliable implementation, the feature encoding provides a feasible AnyBURL check against existing associations. Record its limited expressivity plainly. Preserve raw occurrence edges as the grounding authority; map each predicted feature back to exact local witnesses before proposing a group. A genuinely new component or edge proposal needs a separate candidate/constraint mechanism; observing a feature in another workflow is not execution or verified synthesis.

For the occurrence-edge experiment, keep learning predicates exclusively between occurrence entities, or validate that every grounding variable belongs to a single source graph. Do not put schema constants into traversal paths and then assume graph isolation. Scope checks belong in independent verification and in controlled adversarial tests.

## Bounded comparison proposal

1. Freeze corpus, extraction, family map, eligible neighborhoods and token dictionary with hashes. Use the existing all-origin family grouping before the split. Retain exclusions and dependent/mirrored-source caveats.
2. Make deterministic provenance-group partitions. Recompute association guidance **using training data only**. Existing all-corpus associations cannot serve as leakage-free guidance.
3. Label this a newly partitioned exploratory experiment. Prior whole-corpus exposure means it is not pristine held-out scientific confirmation, even if the learner never sees the assessment partition.
4. Freeze a common rule vocabulary, minimum support, time budget, length cap and acceptance thresholds before looking at separated results. Distinguish vocabulary known from the full schema from frequency-based feature selection.
5. Compare direct AnyBURL on the common training facts against the same learned rules/candidate language with train-only association guidance. If guidance is applied after learning, call it a **post-learning rule filter**, not accelerated learning. Equal time alone does not establish an efficient-search advantage.
6. Recount all accepted rules on training and assessment evidence independently. Report support, predictions, confidence, abstention/coverage, source groups and contradictions separately. Include a frequency-only/always-common-feature baseline.
7. Keep unknown extraction separate from absent saved features. Do not use arbitrary unobserved edges as known incorrect wiring. A masked-edge recovery task must hide every reverse/derived alias of the target fact from application evidence.
8. Build a candidate JSON only from matched local source occurrences, with every internal and crossing edge and required declaration accounted for. Run the established boundary tests. Call this retrieval/structural proposal evidence, not behavioral composite validation.
9. Save each rule's provenance: exact clause, encoding, learner run/JAR hash, training and assessment counts, supporting source links, absence examples, projected occurrence IDs, rejected or unknown conditions.
10. Write a failure-first conclusion. Possible outcomes include no transferable rules, gains explained by feature frequency, association guidance dropping useful rules, schema contamination or structurally valid candidates whose purpose remains unknown.

## Verification targets before claiming success

- An engineered two-workflow fixture where common type labels tempt a cross-graph join; no accepted grounding may mix scopes.
- Two distinct centers of the same type within one graph; their features must not merge.
- Edge direction and port-name changes must alter feature identity.
- Duplicate raw edges must not inflate binary feature support; all original witnesses remain inspectable.
- A target mask must remove derived feature aliases, not merely the raw edge.
- Hand-counted clauses must match both independent recounts and PyClause materialization for supported rules.
- Complete source-family isolation between learner training and separated application evidence; explicit warning that prior human exposure remains.
- Constant-only/zero/frequency rules and tautologies must be labeled or filtered by a documented rule-class policy, not presented as discovered composition logic.
- Every proposed group's internal/cut partition must match the original saved graph; required unwired fields remain unknown rather than falsely absent.

## Sources consulted and limitations

Primary sources are the official PyClause documentation, its maintainers' repository/build files and the official AnyBURL project page. Documentation and moving master can disagree; installation/version claims must be verified against the pinned checkout actually used. No performance claim, macOS compatibility result, measured accuracy, useful composite rule or experiment outcome is established by this memo. The report intentionally does not install packages, execute learners, alter notebook sections or modify the corpus.

## Focused update: querying a fixed center in a partial graph

The official query API takes `(source_entity, relation)` and `direction='tail'` for `(source_entity, relation, ?)`. Results are one ordered candidate/score list per query. Setting `qa_handler.collect_rules=True` enables the predicting-rule lists; `filter_w_data=True` suppresses already-observed answers. [Query Answering](https://pyclause.readthedocs.io/en/latest/feature/query_answering.html).

```python
from clause import Options
from c_clause import Loader, QAHandler

opts = Options()
opts.set('qa_handler.collect_rules', True)
opts.set('qa_handler.filter_w_data', True)
opts.set('qa_handler.aggregation_function', 'maxplus')
opts.set('qa_handler.num_threads', 1)
# Length of the frozen training feature vocabulary, not tuned on answers.
opts.set('qa_handler.topk', vocabulary_size)
opts.set('qa_handler.disc_at_least', -1)
opts.set('qa_handler.hard_stop_at', -1)
opts.set('qa_handler.num_top_rules', -1)

loader = Loader(options=opts.get('loader'))
# partial_facts must exclude each masked target and every alias of it.
loader.load_data(data=partial_facts)
loader.load_rules(rules=accepted_same_X_Uc_clauses,
                  stats=train_num_predictions_and_support)
qa = QAHandler(options=opts.get('qa_handler'))
qa.calculate_answers(queries=[(center_token, 'has_feature')],
                     loader=loader, direction='tail')
answers = qa.get_answers(as_string=True)[0]
reasons = qa.get_rules(as_string=True)[0]
```

The method signatures, output shape and filtering behavior are from [Query Answering](https://pyclause.readthedocs.io/en/latest/feature/query_answering.html); option keys and stopping defaults are from [default configuration](https://raw.githubusercontent.com/symbolic-kg/PyClause/master/clause/config-default.yaml). This is a proposed configuration, not a locally tested snippet. `stats` order is number of predictions then support. Maxplus scores and smoothing are ranking machinery, not confidence in task correctness. Disable or explicitly set `loader.c_num_unseen` if comparing against raw association confidence; record that policy, do not silently mix smoothed scores and raw ratios.

**Vocabulary caution:** head constants must be known to the Loader. The docs show `set_entity_index(index=[...])` / `set_relation_index(index=[...])` before `load_data`, but the rule-syntax page also says constants must exist in the loaded KG. Test the exact pinned package's behavior when a feature is absent from every partial fact. A robust alternative for this restricted one-body same-X language is to load training facts plus partial assessment facts, using globally distinct center occurrence tokens, and query only assessment centers. With only `has_feature(X,fB) <= has_feature(X,fA)` accepted, training centers cannot contribute the body fact for a different assessment center. Prove that isolation with a fixture; do not generalize that guarantee to arbitrary paths through shared constants.

**Masking and split:** mask complete feature facts, not only raw connections, before creating application triples. Independent scoring may compare the returned feature token with the saved source neighborhood afterward. Source-family partitions remain retrospective exploratory partitions because this corpus was already exposed. Do not call them pristine held-out validation. A successful feature-recovery experiment shows rule transfer in this encoding; it does not show autonomous topology generation.

# Internal implementation review — bounded feature-rule experiment

Review scope: static inspection of `RELATIONAL-PROTOCOL.md`, `relational_experiment.py`, `test_relational.py`, the subsequently added `verify_relational.py`, and relevant pinned PyClause application/wrapper source. This is internal AI review, not academic peer review. No experiment or native package was executed by the reviewer. The implementation owner was running the study concurrently; later changes can supersede the observations below.

## Findings requiring attention

### R1 — Native QA stopping can truncate supposedly complete candidate sets

**Observed original implementation:** `native_answers` set `qa_handler.topk=-1` but retained `disc_at_least=10`. In pinned `src/c_clause/core/QueryResults.cpp`, nonpositive top-k disables candidate insertion truncation. However, `src/c_clause/features/Application.cpp` still tests current size against top-k and can break after discrimination; a negative top-k does not by itself disable that condition. The original single-answer native fixture would not exercise this.

**Disposition observed during review:** the owner added `disc_at_least=-1`, `num_top_rules=-1`, `hard_stop_at=-1` explicitly, and a 16-answer native test. Static cause addressed; actual test outcome must come from the owner's execution. The full-run native/direct candidate-set and score assertions are useful additional protection.

### R2 — A failed rerun can reuse a stale output and look successful

`run_engine` originally accepted Python return code zero plus an existing nonempty `rules.txt`. Pinned `clause/learning/anyburl_wrapper.py` explicitly calls `sys.exit(0)` when Java returns a code other than its expected `1`. That exits before `engine_worker` can perform its post-call artifact check. If an older rule file is already present, the parent process can therefore accept a failed rerun and hash the old rules as a new attempt.

**Required protection:** use a fresh invocation directory, or reject pre-existing output/snapshot paths before launch; preserve prior artifacts rather than overwriting them. Record that the expected snapshot was created for this attempt and renamed successfully. This is a rerun robustness issue; no stale artifact was observed in the clean first-run directories during this review.

### R3 — Independent verification initially did not cover all stated proposal/metric checks

At inspection, `verify_relational.py` checked training-only descriptors, source origins, declared port existence and required-input exposures. It did **not** independently establish that the proposal's two edge signatures equal one triggering visible body plus the predicted head, nor recompute the stored type judgments/structural flags. A corruption to another declared port or type pairing could escape those checks.

The verifier also independently recounted the three rule arms but not the center-frequency baseline, and did not fully reconstruct all rate/macro-family denominators. Those are important if the write-up calls the complete comparison independently verified. The implementation itself appears to compute the baseline and macro metric sensibly; this finding concerns verification coverage, not an observed wrong result.

**Suggested completion:** reconstruct both edge-role signatures from the proposal's declared node types, edge direction and ports, compare with accepted triggering body/head, recompute declared label overlap and required fields, and independently recompute every baseline/rate/macro score from cases. Add deliberate-corruption fixtures to prove the verifier rejects each mismatch.

## Scope and leakage assessment

No direct training/evaluation leakage was found **within the restricted accepted language**. The parser requires a single shared subject, one body atom, known feature constants, distinct body/head and equal center type. Training and application occurrences are separately scoped. Loading training facts plus partial assessment facts does not let these one-body same-subject clauses read another center's feature. This would not be true for unrestricted paths through shared schema constants.

The family hash split, train-only recomputed guidance and complete target-feature removal match the protocol. The existing whole-corpus exposure is explicitly disclosed as retrospective rather than pristine held-out evaluation. The selected-case cap is deterministic. Unknown target vocabulary remains in the case denominator and can lead to abstention or non-recovery rather than being silently dropped.

The protocol correctly calls the guidance a post-learning shortlist. This comparison can establish a coverage/recovery tradeoff for that filter; it cannot establish faster AnyBURL learning. It also correctly identifies feature clauses as association serialization rather than deeper topology discovery.

## Score and proposal interpretation

The accepted rules are independently recounted with a center-conditioned lift threshold. PyClause application receives exact `[bodyCount,jointCount]`, zero U_c unseen smoothing and max aggregation; original AnyBURL statistics remain separately stored. This avoids directly equating native sampled learner confidence with the current neighborhood ratio. Final output ranking is the experiment's canonical tie-break over maximum raw confidence, not necessarily PyClause's full native maxplus tie order; the protocol states that distinction.

Proposal assembly chooses saved declarations from training only, introduces fresh symbolic neighbor occurrences, and retains unresolved purpose/configuration/aliasing. It does not recreate the exact masked source group or prove an appropriate boundary. A three-node proposal can differ from a two-node source witness because aliasing is explicitly unresolved. Any final claim should remain “schema-based synthetic proposal,” and should report unknown/conflicting type judgments rather than calling all returned proposals valid composites.

## Additional bounded robustness observations

- The current protocol promises source-graph freeze verification; `main` itself reads current descriptor graphs without checking their aggregate hash, but the new independent verifier checks the earlier frozen derived-graph digest. Do not finalize results if that verification fails.
- `metrics` uses `zip`; current main builds equally sized lists, but adding an explicit length assertion prevents a future short prediction stream from silently distorting denominators.
- The timeout sends SIGTERM then waits five seconds. If a child ignores termination, a SIGKILL fallback would make the watchdog robust. No ignored termination was observed.
- No scientific generalization, task usefulness, native-component certification or full composite-generation claim is warranted by this study, regardless of recovery rate.

# Final internal review disposition — executed Study C

Final check inspected `relational/summary.json`, `verification.json`, the current implementation/verifier/test files, the Study C manuscript generator, saved notebook outputs and the raw-wire failure log. This remained an internal read-only code/evidence review; only this report was edited. It is not external academic review or behavioral evaluation.

## Findings disposition

| Finding | Final evidence | Disposition |
|---|---|---|
| R1 native candidate truncation | All QA stopping options explicitly disabled; 16-answer regression present; full application compares native/direct candidate sets and scores; notebook output records20 tests OK | Addressed for this delivery |
| R2 stale output acceptance | Each invocation creates a fresh engine-batch directory; `run_engine` rejects an existing final rules path before launch; missing output is failure; timeout now has SIGKILL fallback | Addressed for this delivery |
| R3 verifier coverage | Independent verifier now reconstructs frequency baseline, all rates/macros, triggering body/head signatures, type judgments, resources and required exposures; deliberate corruption tests cover several mismatches | Addressed for current saved artifacts |

Additional read-only inspection confirmed all58 saved proposals have exactly two center-incident edges, two matching type-check records, and exact agreement between each edge and its stored check record. A future verifier hardening could assert these cardinality/center-incidence conditions explicitly instead of relying on the proposal writer's construction; no such mismatch was observed in the delivered artifacts.

## Final numerical and claim checks

- The learned union has205 qualified local feature implications; exhaustive same-language counting also has205. This is a restricted feature implication result, not arbitrary topology-rule discovery.
- AnyBURL/exact-counting recover34 of402 masked cases, answering58. The center-frequency baseline recovers43 of402 and answers249. The manuscript correctly reports no all-case or macro-family advantage for the learned rule arm. Answered-only recovery is selective and cannot be presented as overall superiority.
- The training-only association shortlist retains61 rules, answers50 and recovers31. This supports a catalog-size/coverage tradeoff, not faster learning or better generation.
- Only167 of402 masked signatures occur in the training vocabulary. All402 remain in the denominator. This is a coverage diagnostic rather than an excuse to discard difficult cases.
- All58 produced designs are explicitly symbolic three-role/two-edge proposals using training declarations.58 show declared type-label overlap;0 lack descriptors. Required configuration, active outputs, purpose and aliasing remain unresolved. These observations do not certify native Langflow contracts or useful composites.
- `verification.json` reports410 recounted rule records including the baseline set,8,258 reconstructed transactions,15,366 checked incident witnesses,1,107 source graphs,402 checked cases,58 proposal specifications,65 required-exposure records and zero source-family overlap. The qualification correctly states same-corpus/internal implementation recount rather than independent behavioral evaluation.
- The raw-wire probe log contains `java.lang.OutOfMemoryError: Java heap space` during precomputing relation/direction starting points after setting up1,599 relations. Its reported infrastructure failure is consistent with the log. Null rule counts correctly avoid treating failure as zero learned rules.
- The saved notebook has six executed Study C code cells with execution counts1–6, zero error outputs, and a test output stating20 contract/corruption tests passed.

## Remaining editorial precision

Two small wording corrections were sent to the implementation owner: per-rule native learner statistics live in `rules.json` rather than all being present in `summary.json`, so refer to “saved artifacts”; and the feature tuple does not explicitly include version, so any statement about fragmentation across versions should mean changed type/port labels across versions, not a version feature. Neither changes the recorded results.

**Final judgment:** no remaining blocker found for the bounded exploratory Study C claims, with the explicit retrospective-split, restricted-language, symbolic-proposal and infrastructure-failure qualifications preserved. The results establish an executed research baseline with useful negative findings; they do not establish autonomous useful-composite formation, general instance generation or behavioral correctness.
