# Paper 6 isolated assistant: native runtime research

Status: source/dependency inspection only. No model call, service start, package installation, Langflow source edit, or runtime isolation claim was made by this research task. The only written file is this report.

## Recommendation

Reuse **Langflow's `AgentComponent` and its native `create_agent_runnable()` path**, with a research-specific prompt and a newly constructed allowlist of scoped `StructuredTool` objects. Invoke the returned LangGraph runnable directly with explicit message history. Do not call the stock FlowBuilderAssistant factory or the stock assistant HTTP endpoint merely with a new session ID.

This is a **research profile built from the same native agent machinery**, not an unchanged copy of the stock flow-builder service. The native builder itself instantiates this exact component at [flow_builder_assistant.py:611](/Users/x/projects/langflow/src/backend/base/langflow/agentic/flows/flow_builder_assistant.py:611). Its native component now delegates to LangChain `create_agent`, retaining Langflow's model-call budget, tool-call-ID handling and retry middleware. See [agent.py:551](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent.py:551) and [agent.py:627](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent.py:627).

The local Langflow backend being down does not prevent importing this library in an isolated worker process. It does prevent claiming the stock assistant endpoint is working. No live inference has been verified in this report.

## Why not the stock factory/service

`async get_graph(provider=None, model_name=None, api_key_var=None, iterations_limit=None) -> Graph` always calls `build_toolkit()` and assembles ChatInput → AgentComponent → ChatOutput. The toolkit includes component add/remove/configure/connect, full-flow building, `RunFlow`, template use and native filesystem tools. This is the wrong authority set for a paper-only assistant, even with a new conversation ID. [factory](/Users/x/projects/langflow/src/backend/base/langflow/agentic/flows/flow_builder_assistant.py:571), [tool assembly](/Users/x/projects/langflow/src/backend/base/langflow/agentic/flows/flow_builder_assistant.py:518).

The stock streaming service also resets/reads working canvas state and pulls the flow from the supplied `FLOW_ID`. Its conversation buffer is partitioned by `(user_id, session_id)`, not by a Jupyter document. A distinct session alone does not remove canvas access. [history](/Users/x/projects/langflow/src/backend/base/langflow/agentic/services/assistant_service.py:204), [streaming signature](/Users/x/projects/langflow/src/backend/base/langflow/agentic/services/assistant_service.py:609), [canvas initialization](/Users/x/projects/langflow/src/backend/base/langflow/agentic/services/assistant_service.py:726).

## Exact programmatic seam

### Imports and construction

The following is a source-derived construction recipe for the implementing parent to smoke-test, not a claim that this task executed it:

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import StructuredTool
from lfx.components.models_and_agents import AgentComponent

# The local proxy owns credentials. A local placeholder is not an upstream secret.
llm = ChatOpenAI(
    model=advertised_proxy_model,
    base_url="http://127.0.0.1:8787/v1",
    api_key="local-proxy",
    use_responses_api=True,
    streaming=True,
    timeout=120,
    max_retries=0,
)

# Nonempty private identity avoids dereferencing an absent LFX graph for user_id.
component = AgentComponent(_user_id="paper6-research-worker")
component.set(
    model=llm,
    tools=scoped_tools,
    system_prompt=research_prompt,
    max_iterations=12,
    handle_parsing_errors=True,
    add_current_date_tool=False,
    add_calculator_tool=False,
    n_messages=0,
)
runnable = component.create_agent_runnable(allow_interrupts=False)
result = await runnable.ainvoke(
    {"messages": [*explicit_history, HumanMessage(content=current_request)]},
    config={"recursion_limit": 58},  # >= 12*4+10; keep explicit and bounded
)
```

The model name supplied in the task is `gpt-6.1-sol`; discover the actual advertised model through the parent-owned proxy adapter rather than silently changing global proxy settings. `ChatOpenAI` installed in the Langflow venv supports `use_responses_api`, `streaming`, and `reasoning_effort` fields; that is interface inspection, not acceptance by the provider. Avoid choosing a reasoning effort or temperature not requested/known compatible without checking actual model behavior.

Relevant source facts:

- `AgentComponent._resolve_selected_model` explicitly accepts `BaseLanguageModel` instances. [agent.py:374](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent.py:374).
- `ModelInput.normalize_value` passes a non-list/non-string value through, including a connected model object. [inputs.py:236](/Users/x/projects/langflow/src/lfx/src/lfx/inputs/inputs.py:236).
- Native `get_llm` returns a supplied `BaseLanguageModel` object directly. [instantiation.py:124](/Users/x/projects/langflow/src/lfx/src/lfx/base/models/unified_models/instantiation.py:124).
- `_get_llm` evaluates `self.user_id` before that passthrough. A component without a bound `_user_id` or graph will fail because `user_id` falls back to `self._vertex.graph.user_id`. [agent.py:412](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent.py:412), [custom_component.py:214](/Users/x/projects/langflow/src/lfx/src/lfx/custom/custom_component/custom_component.py:214).
- Constructor configuration accepts `_user_id`; BaseComponent stores it. [component.py:242](/Users/x/projects/langflow/src/lfx/src/lfx/custom/custom_component/component.py:242), [base_component.py:31](/Users/x/projects/langflow/src/lfx/src/lfx/custom/custom_component/base_component.py:31).
- `component.set(**kwargs)` routes known input names through `set_input_value`, supporting native input validation. [component.py:590](/Users/x/projects/langflow/src/lfx/src/lfx/custom/custom_component/component.py:590), [component.py:1177](/Users/x/projects/langflow/src/lfx/src/lfx/custom/custom_component/component.py:1177).

### Why invoke the returned runnable directly

`message_response()` calls `get_agent_requirements()`, which fetches graph-backed history, adds built-in tools and configures callbacks. Its `run_agent()` builds a Langflow Message, adapts event streams, calls `send_message`, and can update a stored message. That is useful for the existing Langflow UI, but it couples this worker to services unnecessary for an isolated Jupyter collaboration. [requirements](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent.py:435), [message_response](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent.py:922), [run_agent](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent.py:674).

The direct runnable accepts the standard `{"messages": [...]}` state. The native source confirms this shape and exposes `astream_events(..., version="v2")` for token/tool events. Use that API when live UI events are needed; persist only real received events. [native stream call](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent.py:734), [message-building helper](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent_helpers/messages_input_builder.py:19).

Calling `create_agent_runnable(allow_interrupts=False)` deliberately omits the stock Langflow approval/checkpointer UI path for this newly scoped assistant. Tool permissions must instead be enforced by the new broker. The returned agent has no persistent state unless the caller saves and supplies it; create no shared singleton messages list. Preserve AI/tool call IDs and complete tool-result pairs if serializing history. The native optional checkpointer keys on a graph `run_id`, not simply the chat session; don't imply that session ID creates native checkpoint persistence. [tool approval](/Users/x/projects/langflow/src/lfx/src/lfx/components/models_and_agents/agent_helpers/tool_approval.py:26).

## Scoped tools

`StructuredTool.from_function(func=None, coroutine=None, name=None, description=None, return_direct=False, args_schema=None, infer_schema=True, ...)` is present in the installed `langchain_core`. Native Langflow filesystem tools use this exact factory with explicit Pydantic argument schemas and closure-bound user identity. [read tool](/Users/x/projects/langflow/src/lfx/src/lfx/components/files_and_knowledge/filesystem.py:536), [write tool](/Users/x/projects/langflow/src/lfx/src/lfx/components/files_and_knowledge/filesystem.py:559).

Recommended research broker capabilities (design inference, not existing Langflow tools):

| Capability | Suggested enforcement |
|---|---|
| Read progressive context | Enumerated context IDs or workspace-relative paths with source/hash/range metadata |
| Read source evidence | Allowlisted immutable roots; bounded text/JSON, no credentials or config values |
| Write paragraphs/references | Paper6-only notebook-cell API or versioned research draft path, optimistic base hash |
| Write artifacts | Dedicated artifacts subtree, size/content policy, recorded hashes/revisions |
| Run experiments | Predefined bounded runner or separately isolated execution process; explicit timeout/memory/output limits |
| Research sources | Read-only HTTP broker with public-URL policy, provenance records and no arbitrary credential forwarding |

Do not attach the builder's canvas tools, generic shell tool, or unrestricted filesystem tool to the research profile.

### Path safety is necessary but not a process sandbox

At minimum, reject absolute/drive/UNC paths and traversal, validate resolved containment, refuse symlink/hardlink escapes, use no-follow opening where possible, and bind each closure to its immutable workspace identity. Native filesystem implementation already documents per-user binding, no-follow operations and hardlink refusal, but its default shared namespace must not be mistaken for per-paper isolation. [binding](/Users/x/projects/langflow/src/lfx/src/lfx/components/files_and_knowledge/filesystem.py:475), [root policy](/Users/x/projects/langflow/src/lfx/src/lfx/components/files_and_knowledge/filesystem.py:754), [containment](/Users/x/projects/langflow/src/lfx/src/lfx/components/files_and_knowledge/filesystem.py:891).

**Critical:** allowing the model to write a Python script and run it as the local user bypasses tool-level path limits: that script can read outside the workspace and contact networks. For an initial enforced boundary, allow only fixed reviewed experiment commands with validated arguments, or separately sandbox arbitrary execution. A dedicated Jupyter kernel / working directory is not an OS sandbox. State the delivered isolation boundary accurately.

Similarly, an editable prompt saying “only access Paper6” is not enforcement. Do not expose user-configurable arbitrary `base_url` destinations to this broker's model client or read/write tools.

## Runtime provenance and compatibility observed

Local source checkout: `/Users/x/projects/langflow`, commit `aeb10d96bb2ea797696613af931e91ddf51f3320`; `git status --short` returned clean during inspection.

Installed environment inspected at `/Users/x/projects/langflow/.venv/bin/python`:

| Package | Observed version |
|---|---|
| Python | 3.12.15 |
| lfx | 1.13.0 |
| langflow | 1.13.0 |
| langchain | 1.3.14 |
| langchain-openai | 1.4.1 |
| langgraph | 1.2.14 |

Importing `ChatOpenAI` for interface inspection emitted a “PyTorch was not found” tokenizer/model utility warning. That does not establish inability to call a remote tool-calling model. No inference was attempted here.

The notebook service has a separate environment. Prefer an isolated worker using the already provisioned Langflow environment rather than blindly replacing the notebook kernel's packages. Bind its configuration/cache/log state to the research worker and don't load the Langflow checkout's `.env` or existing canvas database. Settings source exposes a configuration directory and a do-not-track setting, but the parent must verify effective environment names/behavior before claiming they take effect. [paths settings](/Users/x/projects/langflow/src/lfx/src/lfx/services/settings/groups/paths.py:10), [telemetry settings](/Users/x/projects/langflow/src/lfx/src/lfx/services/settings/groups/telemetry.py:17).

## Required parent verification before claiming completion

1. Native component import/construction and one real tool-call round trip through the proxy.
2. Two sessions/workspaces cannot read each other's records; path traversal/symlink/hardlink/absolute-path attacks fail.
3. No active canvas/flow database mutation and no stock builder tools attached.
4. Progressive context is actually requested/read and source attribution survives tool calls.
5. A real assistant write creates a persisted, recoverable paragraph/artifact with revision evidence.
6. Reopen/restart preserves transcript and writes without replaying destructive tools.
7. Experiment runner boundary is tested separately; distinguish controlled static checks from arbitrary code isolation.
8. Native model errors, timeout, cancellation and tool failures appear honestly in Jupyter.
9. Collaboration conclusions are checked against observed experiments, not produced by agreement or optimistic writing.

---

## Internal implementation review — first delivered source inspection

Reviewed source: `services/paper6-assistant/workspace.py`, `sandbox_runner.py`, `runtime.py`, `server.py`, and `frontend/server/paper6-assistant.mjs`. This review is read-only except this appended report; no attack, model call, execution test or service restart was performed. The parent reports a successful native tool round trip through Chat Completions and five passing integration tests. Those observations were not independently rerun here.

### R1 — Artifact broker has a validate/open race across the execution boundary (P1)

At inspection, `Workspace.safe()` checks symlinks and resolved containment, then returns a pathname. `read_artifact()` later opens that pathname with `read_text`; `write_artifact()` and `atomic()` create/replace through pathname parents without descriptor pinning or no-follow opening. Meanwhile, an executing notebook is allowed to mutate the same persistent artifacts subtree.

A concurrent notebook can replace a previously validated artifact parent with a symlink between validation and the **unsandboxed broker's** actual filesystem operation. This would let broker operations carry authority the notebook process does not have. Rejecting a symlink that already exists at validation time does not close the race. `list_artifacts()` similarly traverses and hashes without descriptor containment and without coordination with an active experiment.

Sources at inspection: [safe/read/write](/Users/x/projects/swarms/services/paper6-assistant/workspace.py:42), [atomic](/Users/x/projects/swarms/services/paper6-assistant/workspace.py:10), [sandbox persistent write grant](/Users/x/projects/swarms/services/paper6-assistant/sandbox_runner.py:11).

Required disposition before a race-safe isolation claim: pin directory/file descriptors and use no-follow operations throughout artifact access, or redesign execution around a private per-run scratch tree with a safe output-import step. A threading RLock around broker code alone does not stop a separate process changing directories. A static symlink-denial test is insufficient; add a controlled directory-swap test or an equivalent descriptor-level invariant test.

### R2 — Broad process permission defeats stronger process/cancellation isolation claims (P1)

The notebook policy contains `(allow process*)`. This is broader than the fork/exec permission needed to start Python: it also grants process-signaling operations. Same-user notebook code can attempt to signal processes outside its experiment tree, including the research broker or Jupyter service. This is inconsistent with treating the process as fully isolated from the active application.

The same grant permits child creation. A child can create a separate session/process group, while the watchdog kills only `p.pid`'s original process group. Therefore the current `killpg` implementation is not a complete descendant-stop guarantee for arbitrary notebook code.

Sources: [policy](/Users/x/projects/swarms/services/paper6-assistant/sandbox_runner.py:11), [watchdog](/Users/x/projects/swarms/services/paper6-assistant/sandbox_runner.py:41).

Required disposition: narrowly allow only necessary process operations, constrain signals to the experiment itself if needed, and either deny child process creation or supervise descendants through a boundary they cannot escape. Because this runner executes an in-process IPython shell rather than launching a Jupyter kernel, denying notebook-created child processes may be a viable initial contract. Verify against a disposable external child and a deliberately detached experiment child; do not test against real application processes.

### R3 — Cancel-before-start can strand `running=True` (P1 lifecycle defect)

`turn()` sets `running=True`, creates the task and returns. `cancel()` cancels and awaits the task, but cleanup exists only inside `_run` after it starts and enters its `try`. If cancellation arrives before task startup—or before its protected block—the task raises `CancelledError` without `_run`'s `finally`. `cancel()` does not catch that cancellation or settle state, leaving the runtime marked running and future turns rejected.

This follows from the reachable coroutine scheduling order; no provider call is required to exercise it. Sources: [turn scheduling](/Users/x/projects/swarms/services/paper6-assistant/runtime.py:99), [run try/finally](/Users/x/projects/swarms/services/paper6-assistant/runtime.py:104), [cancel](/Users/x/projects/swarms/services/paper6-assistant/runtime.py:135).

Required disposition: a cancel operation must settle state even if the task never starts, with a deterministic immediate turn→cancel test. Also account for `asyncio.to_thread(execute,...)`: canceling its awaiting coroutine does not stop the thread. The cancel flag is useful, but cleanup/final experiment status should be awaited or reported as pending until the process is actually stopped. Otherwise `experiment_started` can remain without a matching final event.

### R4 — Time/cell budgets are not memory, process-count or output budgets (P2)

The runner limits notebook cell count, source size and elapsed time, but it does not set process memory/output/file-size limits. `capture_output()` accumulates notebook output, and `Popen.communicate()` accumulates subprocess output; truncating strings only in the returned result happens afterward. A notebook can consume substantial host memory or write huge artifacts before its timeout. Subsequently `list_artifacts()` hashes complete files with `read_bytes()`, which can stall or exhaust the unsandboxed broker.

Sources: [cell capture](/Users/x/projects/swarms/services/paper6-assistant/sandbox_runner.py:26), [communicate](/Users/x/projects/swarms/services/paper6-assistant/sandbox_runner.py:47), [artifact hashing](/Users/x/projects/swarms/services/paper6-assistant/workspace.py:52).

Disposition: implement streaming/output quotas and an execution resource envelope or explicitly describe this version as time-bounded only. Bound artifact hashing/reading and avoid state polling reading arbitrary-size generated files into memory.

### R5 — Broad runtime read prefixes need precise wording (P2 scope)

The policy allows reads throughout `/opt/homebrew`, `/private/etc`, `/Library/Frameworks`, `/usr` and `/dev`, as well as the full dedicated workspace. This is broader than a Python-standard-library-only grant. A project/database/service configuration located under one of those prefixes is not protected by the directory policy, even though normal `/Users/x/projects/...` paths outside the workspace are denied.

Do not claim every credential or every other project is unreadable from just the existing outside-file test. Either narrow to needed runtime/library resources or state the exact read allowlist. This is a policy-scope observation, not a claim that a specific secret was read.

### R6 — Source extraction truncation should be represented explicitly (P2 research accuracy)

`fetch_public` caps stored extracted text at80,000 characters and returns at most14,000 characters directly to the model. The source record does not explicitly record whether extraction was truncated or the complete extracted character count. The model can read the stored artifact later, but that artifact may itself contain only the initial part of the paper.

Source: [reference fetch](/Users/x/projects/swarms/services/paper6-assistant/runtime.py:29), [reference tool](/Users/x/projects/swarms/services/paper6-assistant/runtime.py:84).

Disposition: record total extracted length, stored length, truncation, page coverage for PDFs and a clear partial/full-text evidence label. This prevents a partial extraction from being interpreted as whole-paper review.

### Positive findings and claim boundaries

- Native `AgentComponent` is actually imported and used; the component receives scoped tools rather than the stock canvas toolkit.
- The tool list contains no canvas tools and exposes no coordinator merge operation.
- Draft section writes use content hashes and preserve history. Canonical merges are coordinator-only and compare the canonical base hash before writing.
- Context resources are enumerated, copied progressively and linked to sources/hashes; arbitrary read paths are not exposed by the context registry.
- Broker authorization and same-origin/host checks exist, and the model endpoint is fixed server-side rather than supplied by the agent.
- The execution profile is deny-default for network; the parent-reported existing-file/write/localhost tests are useful evidence, but they do not resolve the races and process authority above.
- The runtime prompt correctly rejects guaranteed positive/significant results and distinguishes this native research profile from the live canvas builder.

No blocker was found in the intended **coordinator-only canonical merge** design itself. The highest-priority remaining issues concern the artifact broker/process boundary and cancellation lifecycle. This review is internal source review, not external security certification or academic peer review.
