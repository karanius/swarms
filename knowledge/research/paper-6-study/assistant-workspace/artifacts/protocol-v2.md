# Protocol v2: prospective authored static conformance

Status: implementation prepared, not executed; pending coordinator inspection and freeze. Supersedes v1 implementation details; preserves its negative results and interpretive limits.

## Inputs and separation
Read-only inputs/cases-v1.json schemaVersion 1 contains 24 coordinator-authored cases and catalogSha256. These cases were written before ledger implementation; withheld expectations remain outside this workspace. This is internal author/implementation separation following a jointly designed blueprint, not independent academic evaluation. No case changes are authorized.

Catalog: context/native_catalog.json revision aa54672f51053b7403d5b6a9d1ba063f1ce9ed54d55eda31539757c8da44b6ed. Three native types only: ChatInput, Agent, ChatOutput. No component execution. Metadata/annotations are not active-port evidence. Synthetic LanguageModel attestations are assumption-tier static witnesses only. Optional api_key is not promoted to universally required.

## Concrete schema
Each case has opaque case_id/family/description (ignored by evaluator), nodes [{id,type}], edges [{id,source,output,target,input}], bindings [{id,node,field,kind,state,tier}], node_type_assertions [{node,type}], intent and optional revision. Intent.id is immutable. Intent includes route (any/direct/through_agent), required_agent, route_assertions, capabilities, certify_active_ports, and optional selected_provider {node,name}. Revisions have op, authorized and scoped node or old/new references.

Binding states attested/revoked are simultaneous assertions unless an authorized revoke_model transition changes the current state. Identical duplicates are not conflicts. Only attested synthetic-assumption bindings with compatible kind and correct node/field can witness a required field. A compatible edge can also witness a required input. Contradictory attested/revoked evidence cannot ground the field. Orphan binding evidence never transfers to another node.

## Evaluator contract
obligation_ledger.evaluate(case,catalog,method='ledger') returns action, blockers, questions, patches, post_state, runtime_unknowns, evidence_tiers, coverage. No branches on case_id/family/description. Methods: ledger, B0, B1. Standard library only. Each blocker has kind/node/field/details/evidence/status. Status vocabulary remains MISSING, CONFLICT, UNSUPPORTED, UNKNOWN; positive static witnesses are recorded in evidence_tiers. The return does not claim a complete positive obligation inventory. Unknown predicates are blockers, not passes.

Stable required blocker vocabulary: required_model, required_input, edge_type_conflict, unsupported_capability, node_type_conflict, model_conflict, intent_conflict, orphan_binding, ambiguous_identity, runtime_certification, provider_requirements_unknown, intent_route, revision_intent_conflict. Defensive extensions: catalog_unknown, port_unknown, binding_conflict, revision_unknown, intent_predicate_unknown, for evidence/predicates not established by implementation.

Static type compatibility uses declared output types when present, otherwise return annotation; inputs use declared types. Keep both source fields in evidence records; never interpret annotation compatibility as activation. Unknown type/port evidence remains UNKNOWN. Input/annotation disagreement is not silently resolved into runtime knowledge.

Ledger priority: REJECT_SCOPE for mandatory unsupported external capability; otherwise ASK if any static blocker; otherwise REVISE if authorized patch applied; otherwise SPEC_GROUNDED. All missing blockers survive a rejection. Runtime certification requests yield UNKNOWN/ASK rather than pretending static evidence can certify them. Selected-provider conditions yield UNKNOWN/ASK without invented provider or credential facts. Every output retains runtime unknowns even when statically grounded.

## Revisions
Ledger alone interprets revisions; B0/B1 assess the supplied pre-revision state and explicitly exclude revision coverage. Authorized rename_node updates node IDs and all schema-scoped references, including binding.node, edge endpoints, intent.required_agent, selected_provider.node and revision references, preserving intent.id and stable evidence IDs. Authorized revoke_model changes scoped binding states to revoked and rechecks required fields. Authorized route_through_agent requires the existing specified Agent and one unique direct chat edge; rewires that edge through this Agent without new nodes/bindings. Generated edge IDs avoid collisions. remove_node against retained through-Agent intent yields revision_intent_conflict and no patch. Other unsupported or ambiguous revisions remain revision_unknown/ASK rather than guessed edits. Applied revisions are cleared from post_state; patches preserve the original authorized operation.

Through-Agent route requires compatible ChatInput -> chosen Agent -> ChatOutput input_value edges. If required_agent is absent, exactly one Agent may be inferred as the only identity; alternatives require clarification. Route requirement contradictions are preserved. A direct route does not satisfy a through-Agent intent. General natural-language purpose inference is out of scope.

## Baselines and scoring
B0 reports PORTS_PASS/FAIL/UNKNOWN over declared ports/type predicates and node-type contradictions only. B1, primary comparator, adds unconditional required-field presence, local binding-state conflicts and orphan references; reports FIELDS_PASS/FAIL/UNKNOWN. Neither claims readiness or full specification grounding. FAIL takes precedence over UNKNOWN within baseline coverage. Ledger is a deliberately stronger designed validator, not learned generation or a treatment-effect intervention. Score baseline claims on declared coverage, not as though they made ledger claims.

## Frozen family design and variants
Unchanged 24 cases: F1 configuration/revocation; F2 structural obligations; F3 unsupported capabilities; F4 contradictory information; F5 identity/revisions; F6 metadata evidence boundaries; F7 retained intent; F8 controls/mixed blockers. Input fixtures are authoritative, not rewritten from descriptions.

Notebook produces base plus bijective renaming, list-order permutation, and duplicate-identical-binding variants per case: 96 states, each evaluated by all three methods (288 decision records). Rename mapping covers even orphan/scoped revision identities; node/evidence IDs are distinct namespaces. Order variants reverse nodes, edges, bindings, assertions and route/capability lists. Duplicate variant duplicates each binding; empty lists remain empty. Derived states are not independent observations. Complete inputs/outputs and transformations are saved for separate checker; notebook does not import or implement withheld expectations.

## Execution and freeze
Do not execute before coordinator authorization. freeze-manifest.json records SHA256 revisions of input/catalog/protocol/implementation and notebook. Tool-provided content revisions are used as byte hashes; notebook independently recomputes file SHA256 and fails on mismatch before evaluating. Fresh output artifacts/obligation-results.json uses exclusive creation; never overwrites. No network, native execution, model calls or credentials. Bounded notebook <=120 seconds. Complete failure is a retained outcome, not permission to tune.

Independent checker is separately authored against withheld expected actions/blocker sets and transition invariants. It must inspect false positives, stale evidence, dropped intent, invalid patches and metamorphic violations. No success assertion is made by the experiment notebook itself. Report original and transformed results separately; no significance testing or population estimates.

Hard failures: invented support; unsupported affirmative capability; missing mandatory blocker; silent contradiction resolution; stale satisfaction after revocation; unauthorized identity/intent change; invalid patch; readiness claims; metamorphic inconsistency. Generic/nonactionable questions, no incremental value over B1, and disagreement about oracle predicates are limitations requiring reporting. Corrections after execution require versioned amendment and preserved first-run outputs.

## Claim limits and preserved findings
Success means authored software conformance on a tiny synthetic native alphabet and a diagnostic specification transition, not useful composites, learned generation, runtime validity or real task efficacy. Existing mining evidence remains 205 narrow rules, 34/402 recovery versus center-frequency 43/402, 58 symbolic proposals, retrospective source separation, unresolved purpose/configuration/aliasing, and a typed-wire probe failing at 512 MB. This new test does not establish incremental benefit from those mined rules. Original abstract remains unchanged.
