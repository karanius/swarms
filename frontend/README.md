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
