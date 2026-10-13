# Swarm Canvas

Frontend-only React Flow canvas with seven reusable block types: Research, Read documents, Compare, Write, Parallel team, Review, and Repeat.

## Run

```sh
npm install
npm run dev
```

Drag a block from the left tray, or click it to add it. Move nodes and connect their handles. Select a node or connection and press Delete or Backspace to remove it. Use the controls to zoom and fit the canvas.

The canvas starts empty, with all seven block types available in the tray. Connections are visual only; this frontend does not execute agents or call any backend. Changes remain in memory and reset on reload. Light and dark appearance follow your system preference.

```sh
npm run build
```

## Settings and workflow library

The bottom-left gear opens eight categories of per-node defaults and Saved workflows. Defaults are saved in browser localStorage and copied into newly added nodes. Apply defaults to canvas explicitly replaces node configuration values without changing layout or edges. The first opening seeds the library with a snapshot of the current canvas named Research and decision assistant. Save, update, load and delete workflow snapshots in the library; loading restores configurations, positions and connections. Ordinary canvas edits are not automatically persisted, so update/save the workflow before reloading.

Storage is browser-local, not server-side. No keys or credentials are collected. Node member IDs and ordering are canvas-specific and belong to saved workflows, not reusable default settings. Tool settings and Python autosave remain configuration only until backend execution is implemented.

Selected canvas nodes expose a horizontal toolbar: Node settings, MCP, Skills, CLI, Credentials, and Tracing. Connection panels show project runtime configuration, node attachment, and live Langfuse health. Credential values are never returned to the browser. The local Vite integration-config endpoint supplies status from services/langfuse; deployment outside Vite needs an equivalent server endpoint. These views inspect configuration; edits still use the node forms or runtime configuration files.

Pipeline selection: the workspace checks live log-watcher status before rendering the canvas. The running log pipeline is the initial live selection; the user can explicitly switch to Draft canvas. Selection is pinned in browser storage, and each pipeline has a separate persisted graph and recent input/output history. Connection loss retains that pipeline's graph instead of displaying the research example. Replayed event IDs are deduplicated. Live graphs cannot be dragged, reconnected, or keyboard-deleted; draft mode supports editing. The top-right selector distinguishes running, stopped, disconnected, and draft states. Selecting a design from the pattern tray opens draft mode. Only the log runtime is registered as a live pipeline here; the previous deployment demo is not auto-started or auto-selected.

Visual observability programming: choose Observability → Agent in the workspace selector. Four typed pieces expose Langfuse source → record selection → preview → analyst. Source/selector/preview wires are initially present; connect preview output to the analyst input to enable execution. Deleting any required edge disables the run. Time/category changes invalidate the prior snapshot. Read records loads up to ten completed observations from the latest bounded Langfuse query. Select a wire or Open preview to inspect source IDs, failure text, source links, and exact JSON payload. Agent execution posts an immutable server snapshot ID; backend returns the exact task/context used. Local credentials stay on the backend. This is one functioning visual connection pattern, not a general workflow compiler. Original continuous log watcher remains separate and keeps running.

The separate Observability → Agent canvas was removed. Observability is now a Logs provider node in the existing tray, draggable onto live or draft canvases. Read logs selects a server-side Langfuse snapshot; connect its output directly to an agent's dedicated lower-left logs-context port. The wire opens the log preview and an on-demand Run agent with logs action using local EXO. Inputs and returned outputs appear on the target node. Disconnect/remove controls delete the context binding. Reconnecting the watcher preserves provider nodes and their wires. This adds an explicit manual context input; it does not alter the continuous pipeline's scheduled agent calls.

Logs providers now feed the Input tray directly through its logs-context handle. Mounted providers poll every five seconds; newly selected record IDs are deduplicated and appended before any model invocation. The wire supplies context only, not MCP permission and not automatic inference. Disconnecting hides that provider's supplied entries and prevents new delivery. Existing explicit execution actions remain on demand. Verified a new labeled synthetic ERROR observation appeared automatically in the failure analyst Input tray while output count stayed unchanged and MCP remained denied. Feed currently runs while the canvas is open and uses the existing preview limit of ten records per request; this is not a lossless server-side subscription.

Input composer UX: a wider two-column panel places task, connected source cards, grouped field controls, Essentials/All fields presets, and additional notes beside a persistent final-input preview. Readable view labels actual values; Exact input uses the shared composition function. Source inclusion and source order are per-node settings. Supported parts are task, notes, and connected Logs providers, not arbitrary placeholder sources. Analyze accepts the ordered included snapshot IDs, filters fields server-side, and receives the same composed task. Verified exact preview equaled a real /analyze response agentInput, notes included, excluded sources removed, and selected fields respected. Light/dark screenshots are in services/evidence; desktop and 390px-wide mobile layouts showed no horizontal overflow.

Source mixer visual prototype: connected Langfuse sources share a compact service grid with labeled GitHub, Slack, and Documents examples. Selecting a tile shows only that service's content controls; include switches update the assembled preview. Task/notes editing and individual log-field controls are secondary. The actual-agent-input view calls the original composition helper and excludes all example services; examples exist only in modal-local UI state and are not persisted as grants, wired into the backend, or sent to inference. Verified four visible tiles, selection changes, exclusion/reinclusion, actual-input isolation, light/dark rendering, and 390px layout without horizontal overflow. Build passed.
