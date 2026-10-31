# Official Langflow starter templates

This collection contains all 27 JSON starter projects and four downloadable documentation workflows from the pinned official Langflow revision recorded in `../../prototype-canvas/official-templates.json`. Original JSON bytes are preserved. The upstream MIT license is retained at `official/LICENSE`.

These are **unverified imported candidates**, organized by function under V2 → Composite Components → Official Templates. Placement is provisional: a template may be packaged as one capability or belong at Flows depending on its eventual contract. Importing does not define that boundary, demonstrate runtime compatibility, or implement execution of saved higher-plane blocks.

Each catalog entry records its immutable source URL, Git blob hash, SHA-256, node/edge counts, component types, secret-field configuration requirements (names only), and upstream tested version when present. This metadata is an inventory, not a complete behavioral contract or canonical Library JSON. No credentials are configured automatically and no workflow is executed during collection or opening.

All 31 entries are shown in one searchable list; scroll within the tray to browse. Click a template to verify its hash and open its original graph on the Components canvas. Undo import restores the previous component graph. Existing Custom-library items are preserved. Model/provider and integration configuration may be required before running. Original upstream search behavior is retained; importing Deep Research Agent does not include our separate Lite search repair.

From the Swarms repository root:

```sh
node frontend/prototype-canvas/scripts/import-official-templates.mjs --local /Users/x/projects/langflow
node --test frontend/prototype-canvas/scripts/official-templates.test.mjs
```

Local mode makes independent byte-for-byte copies and verifies them against the local Git revision, without network requests. Internal assistant graphs, API-response examples, and test fixtures are not cataloged as reusable workflow templates. Alternatively, pass a pinned Git revision to download starter templates only; omitting arguments resolves upstream main at collection time. Updating this collection is an explicit repository change; it does not upgrade existing saved Custom items.

Next promotion work: inspect native dependencies, define the external capability boundary, bind permitted resources, run representative and failure checks, attach bounded evidence, then create a versioned reusable item. Keep original downloads separate from repaired or configured variants.
