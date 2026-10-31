# Paper 6: native Langflow builder reuse for controlled layer formation

## Recommendation

Keep the current isolated research runtime and add a dedicated **native graph builder profile**. Reuse Langflow's real graph construction functions against a coordinator-pinned registry and a private graph document. Keep Configuration → Components → Composite → Flows → Processes as an explicit Swarms instance schema above that native graph. Langflow's term “flow” means its component graph; it does not establish our Composite, Flows, or Processes categories. This distinction follows directly from the builder's nodes/edges/config specification and output shape, not from a claim about an upstream multi-layer algorithm. [Native spec format](/Users/x/projects/langflow/src/lfx/src/lfx/graph/flow_builder/spec.py:1), [builder output](/Users/x/projects/langflow/src/lfx/src/lfx/graph/flow_builder/builder.py:64).

This is primary local-source research at Langflow commit `aeb10d96bb2ea797696613af931e91ddf51f3320`. Source inspection establishes feasibility; no model call, installation, service start, or native-tool execution was performed in this research pass. The research skill's delegated workflow is being fulfilled by this assigned research agent.

## What exists today

The current Paper 6 runtime uses native `AgentComponent`, an explicit connected `ChatOpenAI` through the local proxy, and custom research StructuredTools. Its existing tools read progressive context, write isolated draft sections/artifacts, fetch allowlisted references, and execute bounded notebooks. **It does not currently expose Langflow builder tools.** The running research collaborator therefore must not yet be described as the stock Langflow builder. [Tool surface](/Users/x/projects/swarms/services/paper6-assistant/runtime.py:52), [native agent construction](/Users/x/projects/swarms/services/paper6-assistant/runtime.py:130).

The stock factory `get_graph(provider=None, model_name=None, api_key_var=None, iterations_limit=None)` creates ChatInput → Agent → ChatOutput, installs `FLOW_BUILDER_PROMPT`, and calls `build_toolkit()`. That full toolkit includes graph mutation, RunFlow, GenerateComponent, templates, and filesystem tools. The prompt explicitly targets the user's canvas; copying this factory unchanged would grant inappropriate capabilities and retain an incorrect interaction contract. [Factory](/Users/x/projects/langflow/src/backend/base/langflow/agentic/flows/flow_builder_assistant.py:571), [full toolkit](/Users/x/projects/langflow/src/backend/base/langflow/agentic/flows/flow_builder_assistant.py:518).

## Minimum genuine native tools without the canvas backend

| Capability | Exact native entry point | Feasible headless behavior | Required boundary |
|---|---|---|---|
| Catalog | `load_local_registry()` | Loads bundled component-index JSON, cached locally; explicitly no running server/network required | Deep-copy and freeze the chosen subset; record index hash and source commit |
| Discovery | `lfx.mcp.registry.search_registry(registry, query=...)`; `describe_component(registry, component_type)` | Same registry discovery primitives used by native SearchComponentTypes/DescribeComponentType | Read only the pinned registry; do not load arbitrary user component overlays |
| Batch graph creation | `build_flow_from_spec(spec: str, registry: dict | None = None)` | Parses nodes/edges/config; checks type existence/references; adds/configures/connects/layouts and returns flow or structured errors plus node_id_map | Explicit pinned registry argument; save result only as private artifact; atomic commit on success |
| Incremental add | `component.add_component(flow, component_type, registry)` | Native node instantiation from registry | Operate on a deep-copy of the private graph |
| Configuration | `component.configure_component(flow, component_id, params)` | Pure local validation, including known fields, exact options, numeric ranges and conditional options; validates all parameters before applying | Reject secret literals; resource references remain unresolved rather than silently loading user credentials |
| Connect | `connect.add_connection(flow, source_id, source_output, target_id, target_input, registry=...)` | Real native port/handle construction and type-compatibility machinery | Independently assess required fields, DAG policy, boundary exports, and purpose; native connection acceptance is not behavioral proof |
| Native graph inspection | `flow.flow_info(flow)`, `flow.flow_to_spec_summary(flow)`; `component.get_component`, `list_components` | Private graph summaries with real identities | Redact configuration secrets before model exposure |

Sources: [local catalog and batch builder](/Users/x/projects/langflow/src/lfx/src/lfx/graph/flow_builder/builder.py:24), [search/describe tool use](/Users/x/projects/langflow/src/lfx/src/lfx/mcp/flow_builder_tools/read_tools.py:39), [native add](/Users/x/projects/langflow/src/lfx/src/lfx/graph/flow_builder/component.py:184), [configuration contract](/Users/x/projects/langflow/src/lfx/src/lfx/graph/flow_builder/component.py:361), [native connection](/Users/x/projects/langflow/src/lfx/src/lfx/graph/flow_builder/connect.py:287), [graph summaries](/Users/x/projects/langflow/src/lfx/src/lfx/graph/flow_builder/flow.py:22).

The minimal profile can initially expose search, describe, build-private-graph, read-private-graph, and validate-layer-document. Those are real native assembly primitives wrapped in our existing scoped tools. Add incremental edits only when the experiment needs them. Wrapping native primitives instead of reimplementing a fake builder preserves upstream construction semantics while removing unintended canvas/service authority.

## Alternative: exact native MCP component tools

The actual `SearchComponentTypes`, `DescribeComponentType`, `AddComponent`, `ConfigureComponent`, `ConnectComponents`, `BuildFlowFromSpec`, `GetFieldValue`, and `DescribeFlowIO` classes expose `await component.to_toolkit()`. Their operations use a working-flow ContextVar and an event deque rather than directly posting mutations to an HTTP canvas. Consequently these can be reused headlessly, **but require careful state binding**, registry policy initialization and user-context handling. [Exports](/Users/x/projects/langflow/src/lfx/src/lfx/mcp/flow_builder_tools/__init__.py:1), [native add/emit](/Users/x/projects/langflow/src/lfx/src/lfx/mcp/flow_builder_tools/mutate_tools.py:76), [batch state mutation](/Users/x/projects/langflow/src/lfx/src/lfx/mcp/flow_builder_tools/run_tools.py:184).

For that route, create a fresh asyncio task per private turn; call `isolate_flow_run_context()` first, then `init_working_flow(deepcopy(private_graph), flow_id=None)` before invoking the agent. Bind no active-canvas flow ID. Native batch construction intentionally mutates the working dictionary in place so sibling tool contexts share edits. At the end, obtain a deep-copy of `get_working_flow()`, save through the research artifact broker, drain native events into the research ledger, then reset in `finally`. Never forward its `set_flow`/connect/add events to the application canvas SSE consumer. `isolate_flow_run_context()` is crucial: reset alone clears the inherited deque by reference and can wipe a parent's events. [ContextVars and lifecycle](/Users/x/projects/langflow/src/lfx/src/lfx/mcp/flow_builder_tools/_state.py:65), [init/reset/isolate](/Users/x/projects/langflow/src/lfx/src/lfx/mcp/flow_builder_tools/_state.py:149).

This ContextVar boundary is **state separation, not an OS security boundary**. Prefer direct native primitives with explicit registry injection for the first delivery: `_load_registry_user_aware()` can walk user overlays and catalog/provider policy services, whereas the pure builder accepts the precise frozen registry as an argument. Do not monkeypatch that global loader in a shared process. [User-aware registry path](/Users/x/projects/langflow/src/lfx/src/lfx/mcp/flow_builder_tools/_state.py:43).

## Explicitly omit from the private profile

- `RunFlow`: imports `langflow.agentic.services.flow_run.run_working_flow`, binds user and model contexts, and can execute providers/tools. It is unnecessary for generating a specification and is not equivalent to the bounded notebook runner. [Execution dependency](/Users/x/projects/langflow/src/lfx/src/lfx/mcp/flow_builder_tools/run_tools.py:283).
- `GenerateComponent`: invokes the assistant service and validated component-generation pipeline; this exceeds the present requirement to select unchanged existing Langflow components. [Generation dependency](/Users/x/projects/langflow/src/lfx/src/lfx/mcp/flow_builder_tools/run_tools.py:398).
- Stock filesystem tools, user overlays, automatic template adoption, active flow identifiers, canvas approval events, and global variable/credential resolution. Retain the already-enforced research broker for writing and progressive context.

## Where native assembly ends and our theory begins

| Layer | Proposed representation | Grounding condition |
|---|---|---|
| Configuration | Typed values, resource references, unresolved bindings, provenance | Each required setting is supported by explicit field metadata or remains unknown; no invented credentials |
| Components | Native occurrence IDs + pinned definition identity + configuration references | Every occurrence maps to a real catalog type, with actual declared ports |
| Composite | Member occurrence references, internal connections, exposed inputs/outputs, obligations, purpose | Each boundary-crossing edge is exposed; mandatory inputs remain wired, bound or explicitly open; no copying that loses identity |
| Flows | Ordered/conditional relations between composite occurrences and their contracts | End-to-end handoffs preserve typed boundaries, control conditions and unresolved obligations |
| Processes | Flow occurrences with policy, roles, lifecycle, outcomes and exception contracts | Each process requirement has a supporting lower-layer path or a recorded gap |

These upper-layer schemas are **design proposals for Swarms**, not existing native Langflow guarantees. Keep one canonical private instance document; per-plane views and Langflow graph artifacts are projections with identity maps. Membership links are distinct from data/control edges. A reusable definition and an occurrence are separate entities. Graph grouping, community detection or a source file named “flow” does not alone determine its layer.

## Controlled downward/upward loop

1. Record intent, explicit assumptions, hard constraints and open questions with stable IDs.
2. Propose Processes → Flows → Composite obligations without claiming those units exist yet. Every decomposition records its parent requirement, reason and expected boundary.
3. Discover real catalog components and native configuration/ports; build the lowest concrete private graph through native functions. Preserve builder `node_id_map` as occurrence provenance.
4. Independently ground Configuration → Components → Composite → Flows → Processes. Promote only the specific properties checked; keep structural grounding separate from runtime and behavioral evidence.
5. If a lower layer cannot support a proposal, record a gap and revise the smallest affected higher-layer obligation. Do not delete the requirement to force closure. Keep alternatives and bounded attempt budgets.
6. Save each revision, rejected edit, check and source hash; let the research assistant debate/research the precise unresolved question, then continue. The assistant proposes and writes, while coordinator-owned checks decide whether evidence supports the claim.

A minimum first experiment should show one satisfiable intent and one missing-capability intent, compare staged decomposition/grounding against direct generation using the same catalog and budget, and inspect actual native artifacts. Report structural outcomes and gaps only. Neither model fluency nor successful native JSON construction proves useful behavior or complete higher-layer emergence.

## Source and feasibility limitations

The native offline builder may use static metadata defaults: `_resolve_output_types` and `_resolve_input_types` contain Message fallbacks. Dynamic fields can require server-side template regeneration, as `needs_server_update` documents. Therefore preserve declared, inferred/defaulted, dynamically unresolved, and runtime-verified evidence tiers. Do not silently call missing dynamic configuration “valid.” The offline builder also does not by itself certify the user's intended DAG or our upper-layer contracts. [Type resolution](/Users/x/projects/langflow/src/lfx/src/lfx/graph/flow_builder/connect.py:223), [dynamic update marker](/Users/x/projects/langflow/src/lfx/src/lfx/graph/flow_builder/component.py:489).

Do not call this an unmodified stock Langflow assistant after replacing its prompt/toolkit. Describe it precisely: **native Langflow AgentComponent with selected native flow-builder primitives and a Swarms layer-controller profile**. Disclose local source commit, index hash, selected types, proxy/model actually used, prompt/profile version, allowed tools, private document IDs, exact checks and unimplemented guarantees. No external workflow standard is needed to establish these local seams; adopting a standard's subflow semantics later requires a separate explicit mapping rather than claiming Langflow implements our five layers.

## Native adapter and finite layer-contract review

Read-only review of `services/paper6-assistant/layer_builder.py`, its two runtime tools, `layer_contract_engine.py`, example normalizer, and mutation tests confirms the native adapter calls the real offline builder with a deep-copied three-type registry, bounded spec/graph/configuration fields, no RunFlow/GenerateComponent capability, and writes only through the existing artifact broker. No material active-canvas or provider-execution authority issue was found. Its advertised scope is appropriately static and its upper-layer groupings are explicitly authored proposals.

Three material checker false positives were reproduced using only in-memory copies of the saved instance:

1. Remove `O-control` from `flow-triage.openObligations`: accepted. The flow checker preserves inherited component obligations but does not preserve obligations whose target is the flow itself. Apply the same own-target retention condition to every layer, including processes and configuration where applicable.
2. Replace the draft Agent's configurationRefs with the review Agent's references: accepted. The checker establishes reference existence, not that each referenced configuration targets its owning component. Require `configuration.target == component.id` for every component configuration reference.
3. Reverse `coordination.order`: accepted despite the grounded draft→review handoff. Set equality establishes coverage, not valid order. For the finite sequential contract, require unique members and an order consistent with every grounded handoff, or explicitly disclose that declared order is not checked. This does not demand scheduler execution or general hierarchy generation.

The existing native artifact and normalized examples were not changed. These findings concern acceptance-checker coverage, not evidence that the current saved example is malformed. The 81 assertions and twelve detected mutations should not be presented as exhaustive semantic validation until these specific gaps are addressed. No experiment, model call, service operation, or implementation edit was performed by this reviewer.

### Correction disposition: three finite-contract gaps closed

The coordinator added own-target obligation retention for flows/processes, configuration ownership checks, and unique ordering with native-handoff precedence. I repeated the exact three in-memory corruptions against the revised checker: all now fail with the corresponding scoped-obligation, configuration-ownership, and coordination-order errors. The unchanged baseline passes **87 structural assertions**, retains **10 open obligations**, and explicitly reports readiness blocked by those obligations. The coordinator reports fifteen mutation variants detected; this reviewer independently repeated the three findings above. No remaining material blocker was identified in this bounded native-adapter/layer-contract review. Claims remain authored structural conformance, not learned emergence, scheduler implementation, task behavior, or human approval.

### Final finite-schema snapshot

Read-only reinspection of the current adapter/checker found no material regression to the documented finite specimen. Closed top-level, plane, entity, requirement and obligation vocabularies now reject unsupported extra predicates. Recorded native handles/endpoints/declarations/type overlap and specimen DAG are checked. Composite `publicInterfaces` explicitly reference native fields/outputs separately from crossing-wire exposures, and flows propagate their identifiers; this is public-interface declaration fidelity, not proof of API adequacy or usefulness.

Directly evaluating both saved normalized revisions against the current checker gives **139 structural assertions per revision, passed, 10 open obligations**. Their bounded `construction_trace` terminates at `ask_for_missing_evidence`; its own text correctly calls decomposition an inspection of authored proposals, and grounds components against a previously saved native witness. The test source has four unit-test methods, including finite stage gates, and nineteen corruption variants. This review did not rerun the entire unit suite or make a model call.

Current disposition: no material delivery blocker found within the documented finite schema. Native component-graph construction is genuine; upper-layer packaging and semantics are authored, checked proposals. The deterministic trace evaluates that candidate rather than autonomously generating the five layers. Public API declarations, structural assertion counts, and a native artifact do not establish task behavior, runtime orchestration, policy approval, learned emergence, or general instance generation.
