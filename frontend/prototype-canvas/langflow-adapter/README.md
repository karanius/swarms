# Native Langflow adapter

Imports the original GenericNode, NoteNode, edge renderer, graph stores, CanvasControls and AssistantPanel from the local Langflow frontend. The surrounding adapter supplies our canvas, library drag-and-drop, API routing and sticky-note placement. No original Langflow component source is modified, and no editor iframe is used.

Build from the Swarms root:

```sh
node frontend/prototype-canvas/langflow-adapter/build.mjs
```

The default source is the sibling `langflow/src/frontend` checkout with dependencies already installed. Override it with `LANGFLOW_FRONTEND_PATH`. Output is generated into `frontend/public/langflow-native` and ignored by Git. Rebuild when the upstream source or adapter changes.

Original styles are scoped to the native surface and its portals. Controls stay in the same document so Langflow's focus and dismissal handling receives their actual targets. The adapter uses Langflow's zoom limits.

The tray supports dragging Chat Input, Agent and Chat Output. Assistant-generated graphs can also render other generic nodes, including the If-Else and generated context helper used in the tested triage example. This does not establish complete compatibility with every component or advanced setting.

Vite forwards same-origin `/api` requests to Langflow on port 7860. Normal browser authentication is required. The dedicated backend flow identifier is currently configured in `entry.tsx`; other installations must use their own flow. API Proxy model configuration remains in the backend. General autosave, composite packaging and full settings-page navigation are outside this integration.

## Verification

- Native placement, field editing, port connections, backend execution and output inspection.
- Three-node summarization through API Proxy.
- Assistant proposal acceptance updated the V2 Agent; the result was a headline plus two bullet points.
- Fresh generation produced a working Plain-English Rewriter, preserving names, dates and numbers on a supplied fixture.
- A nine-node triage graph routed an outage fixture to the urgent branch and an invoice fixture to the routine branch; both retained the original ticket and produced drafts without sending messages.
- Zoom, sticky notes, collapse/expand, help-menu opening, assistant input and normal panel dismissal.

No general synthesis reliability, universal component parity or autonomous business capability is claimed by these bounded tests.
