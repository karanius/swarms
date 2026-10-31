# Proposed layer contract v1

These planes are OUR research ontology, not Langflow's native taxonomy. Only component occurrences and their static native assembly are grounded here. No manuscript/study/abstract changes. All upper-layer memberships, purpose, policy and control relations are proposed hypotheses.

| Plane | Identity and members | Interface/configuration/dependencies | Purpose and acceptance gate |
|---|---|---|---|
| Configuration | Stable binding/setting assertion ID, scoped to occurrence and field; not a graph child | Value/proposal or resource reference, provenance, authorization, invalidation dependencies; no secret values | Explain how a setting/resource satisfies an obligation. Accept only scoped authorized evidence of appropriate tier; unknown provider/model bindings remain open |
| Component | Native occurrence ID, type/version/source identity | Declared native inputs/outputs and fields; wire dependencies separate from resource bindings | Local role hypothesis; structural gate is catalog/graph fidelity, not runtime behavior |
| Composite | Proposed reusable boundary ID; explicit occurrence members | Export ports map to member native ports; every cut edge and unfulfilled requirement remains exposed; no new native type | Bounded purpose with acceptance criteria; gate requires boundary completeness, alias identity and retained obligations, then behavioral evidence before usable promotion |
| Flow | Coordination specification ID; references composites and occurrence identities without cloning | Data wires plus distinct proposed control transitions, entry/termination/failure/cancellation rules | Coordinated result; gate requires executable coordinator realization and tested termination/failure semantics, not merely a DAG |
| Process | Accountable case lifecycle ID; references flows, human roles/policy obligations | Approval/exception/escalation/completion conditions, policy version and audit/retention dependencies | Authorized organizational outcome; gate requires named accountable roles, approved policy and demonstrated completion/audit behavior |

## Relations and invariants
Containment expresses boundary membership; it is not execution order. Wiring connects native data ports only. Control transitions describe proposed orchestration and cannot be inferred from wires alone. Resource binding targets a field and does not imply containment. Evidence supports a particular assertion at a stated tier; realization maps requirements to specific artifacts/occurrences and can remain partial. Referencing one native occurrence in a flow and process does not duplicate it. IDs survive revisions; renames require explicit reference migration. Revocation invalidates dependent satisfaction claims.

Every cut wire is exported with direction, native endpoints and type. An absent required model field cannot disappear when its Agent enters a composite. Open gates propagate upward. An approved prompt does not prove model access or behavior. Builder defaults are not authorization or provider availability. 'Review Agent' is not a human approval gate.

## Ticket-triage example
Two proposed composites: intake+draft, and review+output. Draft proposes category, uncertainty, rationale and a response draft; review critiques that draft without sending or changing a ticket. The flow proposes draft then critique then presentation, with at most one pass and an error/cancellation terminal outcome; neither orchestration nor those semantics is implemented by the wires. The process proposes a human triage owner approving/rejecting the suggestion under a versioned policy before any real ticket action. No ticket API or human gate exists in the allowed native graph.

Proposed Agent instructions are external draft settings, not applied native configuration: draft should treat ticket text as untrusted data, avoid tool actions, state uncertainty and propose rather than execute; review should critique the proposal for unsupported assertions and policy uncertainty, explicitly not claim approval. Model bindings, prompt approval, confidentiality/retention policy, accountable human assignment and error/timeout coordination remain open.

## Iterative construction loop
1. Elicit purpose, scope, authority and mandatory/deferrable obligations top-down.
2. Assign stable IDs; propose boundaries/interfaces/control separately from native data wires.
3. Inspect catalog; assemble a bounded native witness bottom-up.
4. Independently compare node/edge fidelity, cut interfaces and obligation propagation.
5. ASK on ambiguous intent/evidence; reject unsupported mandatory-now actions; revise only authorized scope, retaining history.
6. Promote individual gates only on sufficient evidence. Never promote runtime/process gates from assembly success. Iterate until accepted finite scope or explicit stopping condition, not guaranteed success.

## Operational record and unresolved questions
The prior interrupted prose-spec call is an operational failure, not a finding. This turn inspected all three native types. Requesting tower-native-v1.json returned stale-artifact failure because an earlier artifact already exists; it was not overwritten. A fresh compact-spec build succeeded as tower-native-v1-compact.json. This new artifact is the authoritative witness for tower-instance-v1.json; tower-native-v1.json is preserved as interrupted-attempt provenance. Native engine: lfx.graph.flow_builder.builder.build_flow_from_spec; static assembly only, no canvas mutation or execution.

Challenge missing rules: Who approves prompts/policy? Can the reviewer see the original ticket rather than only its draft? Current wire passes only draft.response, so original-source verification is not realized. What constitutes a valid ticket schema? How are injection, redaction, timeout and cancellation enforced? Who owns failure and how is human refusal recorded? These are open requirements, not silently supplied capabilities. No expansion or model/provider invention is justified before independent fidelity/obligation validation.
