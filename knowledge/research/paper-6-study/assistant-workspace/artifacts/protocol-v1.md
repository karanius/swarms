# Protocol v1 — synthetic specification grounding and obligation transitions

Status: proposed for coordinator debate and freeze; no cases executed, no outcomes inspected. No manuscript edits. Changes after freeze must be logged as amendments, not silently applied.

## 1. Question, scope and strongest weakness
Can an explicit deterministic obligation ledger transform an incomplete synthetic instance specification into a more grounded specification, a precise clarification, or a justified rejection without inventing support?

The objects are authored specification states, not saved corpus examples and not deployed flows. Alphabet: ChatInput, Agent, ChatOutput only. Capability claims are closed-world with respect to this pinned alphabet and supplied evidence, not claims about all Langflow components. No runtime, provider, credential, endpoint, tool or port activation validation occurs.

Strongest weakness: the same researchers design the cases, obligations and evaluator, so an apparently successful checklist can merely implement its own answer key. Comparing it only with ports-only would amplify this problem. The defensible outcome is a bounded software-conformance/diagnostic demonstration, not learned generation or empirical task utility. Reduce circularity with an independently authored acceptance manifest, a requirement-aware baseline, metamorphic checks, and publication of every case and failure. Independence here means separate implementation/authoring where available, not external validation.

The earlier paired proposal audit is withdrawn: retrofitting intents to corpus examples is unjustified, and a ledger-versus-no-ledger comparison could reward a requirement the original artifact never claimed to meet. Existing mining outcomes remain unchanged: 205 rules, 34/402 recovery versus 43/402 frequency baseline; 58 symbolic proposals; retrospective split; unresolved configuration/aliasing/purpose; 512 MB typed-wire infrastructure failure.

## 2. Evidence and epistemic boundary
Grounding source: `context/native_catalog.json`, SHA256/revision aa54672f51053b7403d5b6a9d1ba063f1ce9ed54d55eda31539757c8da44b6ed, Langflow commit aeb10d96bb2ea797696613af931e91ddf51f3320, with three class-source hashes. Catalog contains metadata and return annotations, not configuration values or verified activation. Agent.model and ChatOutput.input_value are declared required. Agent.api_key is not declared required; do not infer a universal API-key obligation. Conditional provider requirements cannot be inferred from absent provider rules.

`context/assistant_runtime.md` revision 30fd33b536fb04aed62e84ade9c354b1928faa6187f4cf1da04395e6afadb9d3 is source/dependency inspection, not its own execution proof. Coordinator reports the current assistant is a native AgentComponent profile and has made a tool call; keep this operational provenance separate from the catalog experiment and from deployment claims.

Message return annotations may justify annotation-compatible candidate edges when output declaredTypes is empty; record the provenance tier explicitly. They never establish active ports. For declaredTypes and return annotation disagreement, preserve both; matching one is not a runtime verdict. Agent.structured_response declares Data and annotates JSON; do not normalize those into a single verified type.

## 3. State and ledger schema
A case has immutable case_id, explicit synthetic intent requirements, node IDs/types/catalog pins, proposed edges, configuration assertions, external binding attestations, revision events and an evidence manifest. Intent requirements use a small explicit DSL (e.g. route chat through Agent; keep Agent identity; no external tool capability claim), not unconstrained natural-language inference. Natural-language paraphrases are display text only.

Each obligation has stable ID, subject node/edge/requirement, origin (catalog-required / authored-intent / conditional / runtime), predicate, dependencies, evidence IDs, and exactly one status:
- SATISFIED_SPEC: a nonconflicting witness satisfies the static predicate at its declared evidence tier. An authored external binding attestation is accepted only as a synthetic assumption, never as resource availability.
- MISSING: obligation applies and the needed assertion/witness is absent. Omission is not a negative behavioral outcome.
- CONFLICT: simultaneous assertions cannot jointly satisfy the same scoped predicate; preserve both witnesses and do not select one silently.
- UNSUPPORTED: the explicit request cannot be represented by the allowed alphabet/evidence under the declared scope. This is not impossibility in Langflow generally.
- UNKNOWN: truth requires unavailable evidence, including runtime activation, provider-specific conditions or ambiguous aliasing.
- NOT_APPLICABLE: the obligation's guard is explicitly false; include guard evidence. Unresolved guards yield UNKNOWN, not NOT_APPLICABLE.

An edge-compatible predicate and an activation predicate are separate. Runtime obligations remain UNKNOWN in every case; they do not prevent reporting static progress, but preclude ready-to-run claims. A wired field does not satisfy unrelated configuration. No guessing defaults, model selection, secret values or provider rules.

## 4. Transition and decision semantics
Each transition returns a complete ledger, unchanged intent IDs, an explicit patch (possibly empty), outstanding blockers, and one primary action:
- REJECT_SCOPE if a mandatory requirement is UNSUPPORTED; give exact capability and scope reason. Offer revising the requirement, never silently remove it.
- ASK if an applicable static obligation is MISSING, CONFLICT or UNKNOWN and resolution needs user/evidence input. Questions name affected node/requirement, uncertainty, and admissible evidence; never solicit secret values. If unsupported and missing coexist, reject is primary but retain every blocker.
- REVISE if all blockers can be resolved by a unique, explicitly authorized static patch without inventing configuration or identities. Validate patch and emit updated ledger; use ASK when alternatives are not uniquely authorized.
- SPEC_GROUNDED only if every applicable mandatory static obligation is SATISFIED_SPEC (or legitimately NOT_APPLICABLE); explicitly report runtime UNKNOWN. Means grounded under authored assumptions, not runnable or useful.

Priority: REJECT_SCOPE > ASK > REVISE > SPEC_GROUNDED. No-op/already-grounded states have empty patch. Any type-changing or identity-changing patch requires explicit authorization and invalidation/rechecking of dependent evidence. Revoking a binding must revoke its satisfaction witness. Lower-priority blockers are never dropped.

## 5. Frozen family inventory: 24 base cases
Exactly eight families, three predetermined cases each; full input fixtures and independent expected assertions must be frozen and hashed before engine execution. These descriptions are the case blueprint, not a frozen executable dataset yet.

F1 Required configuration: (a) Agent.model omitted; (b) synthetic scoped LanguageModel binding attested; (c) binding revoked in a revision. Chat path otherwise annotation-compatible. Check precise missing model, assumption-tier satisfaction, then reopening.
F2 Structural obligations: (a) ChatOutput.input_value omitted; (b) compatible ChatInput.message -> ChatOutput.input_value edge; (c) ChatInput.message -> Agent.model type conflict. No invented converters.
F3 Unsupported capabilities: mandatory (a) vector retrieval, (b) database write, (c) email transmission, with no supporting tool/resource evidence in the alphabet. Reject within scope; do not claim Agent can satisfy these merely because tools input exists.
F4 Conflicting facts: (a) same node has mutually exclusive type assertions; (b) same Agent.model binding asserted both present and revoked in one revision; (c) explicit intent both requires and forbids same route. Preserve conflicting witnesses, ask, no silent precedence.
F5 Identity/revision: (a) configuration attached to nonexistent node; (b) explicitly authorized rename with evidence references updated; (c) two candidate Agents with unresolved intended identity. Do not duplicate or transfer configuration silently.
F6 Evidence boundary: (a) annotation-only Message output edge; (b) request to certify active ports from metadata; (c) selected provider asserted with no provider-condition metadata. Separate compatibility, unsupported certification request, and unknown conditional obligations. No inference that optional api_key must be provided.
F7 Intent preservation: (a) compatible direct ChatInput -> ChatOutput path despite explicit through-Agent intent; (b) same intent with authorized insertion of an existing uniquely identified Agent plus attested model binding; (c) follow-up revision requests removing Agent while retaining mandatory through-Agent intent. Respect explicit constraints; ask about contradictions.
F8 Mixed and transition controls: (a) fully statically grounded three-node specification under synthetic model-binding assumption; (b) unsupported capability plus missing model; (c) same grounded state with binding evidence changed to wrong node. Verify grounded control, blocker retention, invalidation.

No case claims a real model binding exists. Inputs contain symbolic references, not real credentials or configuration secrets. No case uses mined rules to fill capabilities; this diagnostic bridge does not test their contribution.

## 6. Comparators
B0 ports-only, plainly labeled: verifies node/port declaration existence and static type compatibility at declared/annotation evidence tiers. Reports only PORTS_PASS / PORTS_FAIL / PORTS_UNKNOWN; no readiness claim. Score only its declared predicates on its own coverage. For a common downstream decision table, report what would happen if PORTS_PASS were used as promotion eligibility, clearly labeled a hypothetical policy, not a claim B0 made.

B1 required-fields baseline (recommended primary comparator): B0 plus unconditional catalog-required-field presence and witness references, with local contradiction detection; no intent/dependency tracking. Uses identical inputs and evidence tiers. This controls for the trivial advantage of checking Agent.model and ChatOutput.input_value. Report incremental coverage on conditional evidence, revisions and intent—not a headline superiority percentage across designer-selected cases.

L ledger: full explicit obligations and transitions above. All three are deterministic, transparent programs; no LLM-inference or learning claim. Separate ledger implementation from evaluator code. Same evaluation predicates apply wherever a method makes a claim; abstention is not automatic success.

## 7. Independent checks and freeze procedure
Coordinator (or separate checker author) prepares expected mandatory blocker sets, admissible actions, permissible patches, and evidence-witness assertions from the blueprint and catalog before seeing engine outputs. Allow sets of equivalent precise questions rather than exact text matching. If the same author must do both, declare weakened independence and require coordinator review before execution.

Freeze catalog revision, fixture JSON, intent DSL, checker manifest, implementations, budgets and hash manifest before first evaluation. No train/test terminology: cases are authored conformance fixtures. Do not tune to failures; corrections require a new version and retain first-run outputs.

Independent checker recomputes catalog-required fields and edge checks directly from catalog, verifies every positive witness and node identity, detects dropped intent requirements, validates patch scope, and compares action/blocker sets to frozen expectations. It must not call the ledger's predicate functions.

Metamorphic variants: for each of 24 cases, generate one bijective node-ID rename and one assertion/edge-order permutation (72 total states including originals). Results must be equivariant after ID mapping. Duplicate identical witnesses must not resolve missing/conflicting obligations; apply one duplicate-witness variant to each base case (96 total states). Report base-case and transformed-state results separately, never inflate independent sample size.

Budget: at most 24 base cases and 72 derived checks, one engine pass per frozen method, one independent checking pass; local sandbox notebook <=120 seconds, no network, no native component execution. Preserve outputs/errors. If incomplete, report partial execution and failures; do not expand case families after outcomes.

## 8. Measures and failure criteria
Report per-case: exact statuses, expected versus observed blockers/actions, invalid patches, unsupported positive claims, missing catalog-required obligations, retained intent/identity references, number and specificity of questions, unresolved runtime obligations, and baseline coverage. Aggregate descriptive counts only, with family breakdown. No p-values, population estimates or learned-generation success rate.

Hard correctness failures: any invented component/resource/binding; SATISFIED_SPEC without a valid scoped witness; dropped mandatory intent; silent conflict resolution; invalid patch; stale satisfaction after revocation; runtime-ready claim; unsupported capability asserted as supported; metamorphic inconsistency. Any such event falsifies full conformance for this suite and must be retained.

Diagnostic limitation/failure: all questions are generic; B1 achieves identical useful next actions; independent expected labels cannot be agreed; catalog lacks enough evidence to classify a planned static predicate; or no case can reach SPEC_GROUNDED even under explicit synthetic assumptions. These do not warrant relabeling unknown as failure or modifying thresholds. They may show that a simpler validator suffices or the test is underspecified.

## 9. Permissible conclusions
Success establishes only that an authored finite-state specification/obligation mechanism conforms to this small synthetic suite and makes certain missing information explicit. It may give an executable diagnostic bridge from an incomplete instance to a grounded static specification, precise question or scoped rejection. It does not show mined patterns are useful, composites emerge, native ports activate, credentials work, tasks succeed, the complete Langflow catalog is covered, or real users prefer the decisions. Existing negative mining results remain central and unchanged.

## 10. Answers for next round and remaining freeze decisions
1. Completion target accepted: honest subsystem paper plus one tested diagnostic bridge; no native task execution required. Current assistant tool use is not evidence that generated artifacts run.
2. Use prospective authored intents and states, not retrofitted corpus purposes. The protocol treats checklist advantage as designed functionality; B1 and independent checks constrain overclaiming.
3. Prioritize hidden configuration obligations, then intent/identity preservation under revision. Never equate optional credential metadata with required credentials. Future useful-composite claims need task evidence.

Coordinator decisions needed before freeze: approve B1 as primary comparator; assign independent fixture/checker author or explicitly accept same-author limitation; approve synthetic external model-binding attestations as assumption-tier static witnesses (otherwise there may be no grounded Agent control). Freeze only after concrete fixture and oracle artifacts exist and have been reviewed.
