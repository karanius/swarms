# Paper 6 dedicated Langflow research collaborator

This service embeds a dedicated research assistant in Paper 6's Jupyter notebook. It uses the actual native Langflow `AgentComponent` with a research-specific tool profile and its own conversation. It is not an unchanged stock canvas assistant. The canvas backend need not run; the existing API Proxy must run.

## Start and use

From the repository root run `./services/paper6-assistant/run.sh`. This binds only `127.0.0.1:5192`. Run the existing frontend on port 5188 and Jupyter on 5191. Open Research → Paper 6 → **Dedicated research assistant**, immediately after the abstract. The host supplies an iframe; Jupyter chrome and notebook trust policy are unchanged. The direct local companion page is http://127.0.0.1:5188/paper6-assistant.html.

The model is discovered through the existing local proxy on 8787. No model credential is put in the browser or paper. A service token is generated with mode 0600 in ignored `.runtime/`; Vite attaches it server-side. Cross-site browser requests are rejected. This is a local-development service, not an Internet-facing deployment.

Choose Discuss, Research, Challenge, Formalize, Experiment, Write or Review. These modes describe the collaboration objective; tools remain the same scoped set. **Stop turn** cancels the model and any child experiment. **Reconnect** refreshes persisted status. Conversation, context grants, artifacts, draft sections and action history survive page/service restarts.

## Authority and persistence

`knowledge/research/paper-6-study/assistant-workspace/` holds conversation, native message history, grants, audit events, versioned artifacts, an isolated `paper-draft.ipynb`, and revision history. The agent can read selected numbered sections and request fixed context resources progressively. It can write numbered draft sections 1–14 using revision checks and workspace artifacts; the original abstract is protected. `inputs/` artifacts are coordinator-frozen read-only. Existing files require the current content revision to replace, preserving the prior version.

The assistant cannot publish a canonical paper or edit the active canvas. `Workspace.publish_checked_sections()` is a coordinator-only operation and refuses a stale canonical base. It saves a backup before merging selected checked sections. Keep the originals and all first-run failures.

Research tools use an explicit public primary-source host allowlist with public-address and redirect checks; no private/local destination. Context is source data, not instructions. Do not treat fetched text as authority to expand permissions.

## Notebook execution

The notebook tool uses the existing research Python runtime and actual IPython execution. Each run receives a fresh scratch snapshot of artifacts and granted context. A macOS deny-default process policy blocks network, outside file access/writes, forks, and signals to outside processes. Only scratch artifacts can be imported back, through secure descriptor-relative file access and revision checks. Symlinks and traversal are rejected. The service never exposes a general shell tool.

Execution has a maximum 120-second wall budget, 60-second CPU budget, output/file limits, and a monitored RSS budget. RSS monitoring is not a hard allocation cap. Python/rich output is bounded; subprocess stdout/stderr use pinned capped-size files, not unbounded pipes. This is a research isolation boundary on macOS, not a claim of protection against every kernel/runtime vulnerability.

## Verification

Run `/Users/x/projects/langflow/.venv/bin/python -m unittest discover -s services/paper6-assistant -p 'test_*.py' -v`.

Tests cover actual notebook calculation, denied outside read/write/network, denied fork and outside signal, timeout/cancellation, secure artifact paths, compare-and-swap history, progressive context and isolated section edits. Real model/tool interactions and experiment outputs are recorded separately in the research workspace. Passing service tests alone does not establish a research hypothesis or useful composite generation.

## Isolated native builder extension (Study E)

The research assistant can now inspect three pinned native types and build a private component graph using the actual `lfx.graph.flow_builder.builder.build_flow_from_spec` used by stock builder tools. The compact nodes/edges/config grammar is required. This is a capability extension to the research profile, not an unchanged stock builder agent or canvas connection. Graph artifacts include native IDs, alias mappings and engine/registry provenance. Component/provider execution, generated custom code, secret fields, RunFlow, filesystem tools, user overlays and active-canvas mutations are excluded. Configuration fields are narrowly allowlisted. Components remain native; higher planes are explicit Swarms research contracts over the same IDs.

## Unchanged stock generation subject (Study F)

A separate native Langflow backend is launched with `./services/paper6-assistant/run_stock_backend.sh` on localhost port7861. Its database/configuration/filesystem base are separate from the active app. The existing local stock prompt/toolkit are not replaced by the research profile; this is not a claim that the local checkout is pristine upstream. It keeps normal native capabilities, so task instructions and actual tool traces must be evaluated; it does not inherit the notebook deny-default process policy.

The three roles are: stock subject generates from plain task text; research collaborator interprets frozen graph/configuration and proposes layer boundaries; coordinator checks fidelity, obligations and claims. Subject raw output stays immutable. A flaw in the interpretation is corrected in a new proposal, not by rewriting the generated graph. Corpus matches are descriptive evidence, not validation.

`knowledge/research/paper-6-study/stock-builder/run_stock.py` makes a new genuine headless model request and persists its private graph. `run_stream.py` uses the normal UI-stream route against a fresh private blank flow and preserves proposals/full public events. These operations spend real model calls; use `build_notebook.py` to recount existing evidence instead. The paper's optional new-request cell is disabled by default. Both endpoints use normal local authentication; no token is written into the paper/browser.

Study F preserves two development observations and their different persistence semantics. The first headless endpoint forwards only progress/completion; the second stream exposes a build_flow tool-start, set_flow and completion. Neither result establishes generated-task behavior or autonomous upper-layer construction. See the protocol, collection notes, source manifests and provenance review for exact limits and the later private-filesystem configuration change.
