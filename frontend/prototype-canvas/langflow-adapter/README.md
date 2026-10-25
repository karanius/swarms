# Native Langflow adapter

Imports the original GenericNode, NoteNode, edge renderer, graph stores, CanvasControls and AssistantPanel from the local Langflow frontend. The surrounding adapter supplies our canvas, library drag-and-drop, API routing and sticky-note placement. No original Langflow component source is modified, and no editor iframe is used.

Build from the Swarms root:

```sh
node frontend/prototype-canvas/langflow-adapter/build.mjs
```

The default source is the sibling `langflow/src/frontend` checkout with dependencies already installed. Override it with `LANGFLOW_FRONTEND_PATH`. Output is generated into `frontend/public/langflow-native` and ignored by Git. Rebuild when the upstream source or adapter changes.

Original styles are scoped to the native surface and its portals. Controls stay in the same document so Langflow's focus and dismissal handling receives their actual targets. The adapter uses Langflow's zoom limits.

The tray supports dragging all 208 entries in the current catalog, using their live Langflow definitions. Assistant-generated graphs can also render other generic nodes, including the If-Else and generated context helper used in the tested triage example. This does not establish complete compatibility with every component or advanced setting.

Vite forwards same-origin `/api` requests to Langflow on port 7860. Normal browser authentication is required. The dedicated backend flow identifier is currently configured in `entry.tsx`; other installations must use their own flow. API Proxy model configuration remains in the backend. General autosave, execution of saved higher-plane blocks and full settings-page navigation are outside this integration. Named assembly designs can be saved to the browser-local Custom library.

## Verification

- Native placement, field editing, port connections, backend execution and output inspection.
- Three-node summarization through API Proxy.
- Assistant proposal acceptance updated the V2 Agent; the result was a headline plus two bullet points.
- Fresh generation produced a working Plain-English Rewriter, preserving names, dates and numbers on a supplied fixture.
- A nine-node triage graph routed an outage fixture to the urgent branch and an invoice fixture to the routine branch; both retained the original ticket and produced drafts without sending messages.
- Zoom, sticky notes, collapse/expand, help-menu opening, assistant input and normal panel dismissal.

No general synthesis reliability, universal component parity or autonomous business capability is claimed by these bounded tests.

## Execution memory policy

V2 defaults to isolated executions through `execution-memory.mjs`. Its adapter wraps Langflow's existing `buildFlow` entry point; it does not modify original component implementations. Each invocation generates a fresh `v2-run-<uuid>` session, forwards the canvas Chat Input text when no explicit input was supplied, and sets Chat Input/Output session fields consistently. Agent `n_messages` is set to zero, with distinct per-agent context IDs. Explicit graph edges still carry data between agents.

The snapshot used by local Custom-library saving retains this policy and disables automatic Agent history loading, but clears execution-specific session/context IDs. It does not export the separate chat-history database or builder-assistant conversations. Existing chat records are preserved under Langflow's retention/storage behavior; isolation is not deletion. Existing explicit external-memory components are not stripped or disabled by this policy. Instance knowledge retention and opt-in conversational memory remain future configuration work, not implemented scope controls.

Policy checks:

```sh
node --test frontend/prototype-canvas/langflow-adapter/execution-memory.test.mjs
```
