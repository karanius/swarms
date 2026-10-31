# V3 live system context

The toolbar JSON view is a read-only, event-driven system-context projection. It contains the known V3 library inventory, all plane graphs/layouts, Swift template references, observed instance/deployment metadata, resource and documentation references, controller observations, and explicit unresolved gaps. Requirements and decisions remain linked to their source documents until structured records exist; proposed higher-layer labels are not presented as executable capabilities.

Native flow-store changes and viewport events notify the view through `subscribeContext`; higher-plane graphs, layout changes, Custom library saves and checkpoints update through React state. Notifications are coalesced over 80 milliseconds. The view remains available when the backend is unavailable, with connection coverage recorded explicitly.

Heavy component code and private conversation history are not inlined. Native component definitions remain live/unpinned references, documentation retains integrity-addressed references, and known secret configuration fields become credential references. This is an inspectable projection, not a completed canonical compiler/registry, formal schema validation, or a guarantee that every unstructured text field contains no user-entered secret.

**Save context checkpoint** is distinct from **Save assembly**. It writes an immutable, numbered snapshot to `swarms.v3.system-context-checkpoints.v1` in this browser. Prior versions are retained; no automatic retention deletion occurs. Invalid existing storage disables checkpoint saving and is preserved. Storage quota failures report an error and preserve prior checkpoints. Browser storage is local persistence, not a backend registry or Git publication.

Tests: `node --test frontend/prototype-canvas-v3/system-context.test.mjs`.

## Shared consumer contract

While V3 is mounted, `window.v3SystemContext` is a frozen, read-only access surface shared by future Swift, Langflow Assistant, and Harness² adapters. `getSnapshot()` returns the latest sanitized working manifest (or `null` before capture); `subscribe(listener)` receives subsequent complete snapshots and returns an unsubscribe function. Each read and notification is a separate clone, so a consumer cannot mutate the canonical working projection or another consumer's input. Consumer failures do not interrupt publication. Access is removed on unmount. The projection updates even when the JSON view is closed.

Consumers should record the manifest `id`, `workingRevision`, and `updatedAt` with their work, use the same source, and resolve authorized references separately. This interface does **not** inject context into Swift or Langflow Assistant prompts and does not integrate Harness². Their conversation memories remain separate and are excluded from this record. Persisted checkpoints remain explicit local snapshots of the shared record, not separate documents per consumer.
