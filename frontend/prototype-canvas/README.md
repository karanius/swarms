# Recursive composition canvas prototype

A React Flow workspace with two versions:

- **V1:** the conceptual library and two proposed instance towers.
- **V2:** an independent library, original Langflow nodes and controls, the assistant, and a right-side Machine Sequence tray. The former Full Flow tray is named Flows in V2.

Higher library layers remain proposed entries, not executable assemblies. Historical diagrams are preserved in `current-diagram.js` and `market-growth-program.js`; they are not the current canvas contents.

## Run

Install the frontend dependencies with `npm ci` from `frontend`, then run `npm run dev`. Open `/prototype-canvas/?version=2` on the printed address.

V2 additionally requires the existing Langflow backend on port 7860 and its frontend source/dependencies in the sibling `langflow/src/frontend` directory. Build the native adapter from the Swarms root:

```sh
node frontend/prototype-canvas/langflow-adapter/build.mjs
```

Set `LANGFLOW_FRONTEND_PATH` if the Langflow frontend lives elsewhere. Generated adapter files are ignored. No Langflow checkout, credentials, or runtime database is included. V2 currently opens the dedicated local backend flow identified in `langflow-adapter/entry.tsx`; another installation needs that identifier updated to its own flow.

## Machine Sequence

Hover or focus the right-side control to see eleven expandable steps from [Instance Builder Sequence](../../INSTANCE-BUILDER-SEQUENCE.md). Click to keep the tray open; Escape closes it. It displays the intended workflow, not live execution progress.

## Saved example and limits

[Support Ticket Triage Desk](examples/support-ticket-triage.json) exports the tested nine-node, ten-connection example for import into Langflow. Its model configuration refers to the existing local API Proxy setup; credentials are configured separately. The assistant generated a new context helper alongside original Langflow components.

The local backend has a checkpoint of that example. Further canvas edits are not automatically saved; refreshing reloads the backend checkpoint. Reusable composites and higher-layer execution are not implemented.

Browser verification covered native component placement, connections and execution; assistant editing and fresh generation; urgent/routine routing on two fixtures; toolbar interactions; and the sequence tray's eleven steps, descriptions, hover opening and Escape dismissal. These examples do not establish general synthesis or routing reliability.
