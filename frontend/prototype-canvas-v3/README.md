# V3 isolated workbench

Open `/prototype-canvas-v3/`, or use V3 in the original page's version navigation.

This directory is an independent copy of V2's editable canvas, library, style, sequence, catalog, and native adapter sources. Its official template JSON and license are independently copied under `frontend/public/langflow-templates-v3/`. It does not import V2 application modules or read/write V2 Custom storage.

- Custom storage: `swarms.v3.custom-library.v1` (starts empty; no automatic migration from V2).
- Native adapter build: `node frontend/prototype-canvas-v3/langflow-adapter/build.mjs`.
- Generated adapter: `frontend/public/langflow-native-v3/` (ignored by Git).
- Dedicated backend flow: its identity is in this copy's `langflow-adapter/entry.tsx`; provision a separate flow for another installation.
- Fresh mounts start empty. Imports and explicit additions affect this workbench; higher-plane Custom items remain design snapshots, as in V2.

V1/V2 retain their original page, application files, catalog, storage, and backend flow. The original page gains only a navigation button to V3.

## Shared infrastructure boundary

V3 shares React Flow dependencies, the running Langflow engine and its unchanged component implementations, authentication, and provider/resource configuration. This is isolation of editable workbench code, graph data, generated adapter, catalogs, and local saves—not a separate server, account, credential store, or operating-system environment. Changing shared Langflow provider settings can affect other versions. V3 does not create an independent canonical Instance JSON registry yet; that remains future development.

## Swift template

Components → Our Agents → Swift · Template adds a visual reference to the Swift JSON template. It has no runtime, executable code, model invocation or Run control. The native Langflow components retain their own existing behavior.

`components/swift-definition.json` declares resource references, the architecture table, versioned document references, and references to separate assembly/deployment scripts. Documentation is stored once under `/swift-agent/documents/` with content hashes; it is not copied into every node. The node links to the documentation and raw JSON. Saving the canvas retains the lightweight template record.

The separate assembly script creates native Chat Input, Agent and Chat Output nodes from their live definitions. The deployment launcher saves a new independent Langflow flow, then opens its original chat controller. The model uses the existing API Proxy provider configuration; no credentials are stored in the template. The earlier Langflow-agent experiment was a runtime proof, not the Swift template's implementation. To refresh document references intentionally, run `python3 frontend/prototype-canvas-v3/scripts/update-swift-docs.py`, then rebuild the V3 adapter.

V3 offers read-only Nodes/JSON views of the same canvas graph. The visible Composite label retains its existing saved plane identifier. Instance navigation is rendered inside the active React Flow viewport so it follows canvas pan and zoom; the main Library stays outside for browsing.

Library and Instance trays open only by click. Repeating the click, clicking outside, or pressing Escape closes them. Closing a tray resets its nested categories. Machine Sequence uses the same click/outside/Escape lifecycle.

## Workbench layout and controls

V3 has a collapsible, scrolling Library panel; one top toolbar; an unobstructed canvas region; and a resizable chat dock. Chat uses its own flex-layout space rather than covering the graph. Close and reopen it with the toolbar Chat control; the separator supports pointer dragging and arrow keys. The save panel dismisses on outside click or Escape.

The Instance stack remains in canvas coordinates. Drag its header to move it, and collapse or expand it with its header control. Moving it updates the layout shown in the read-only JSON view. Native nodes retain their original Langflow rendering and configuration controls. The proposed additional cable wrapper and delete control are on hold.
