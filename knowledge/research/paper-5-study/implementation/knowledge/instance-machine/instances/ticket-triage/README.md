# Ticket triage — first iterative instance

Open V3 → Instance, or `/prototype-canvas-v3/?view=instance` on the existing local canvas server.

This is a canonical, repository-file-backed design draft. `head.json` points to one immutable revision document under `revisions/`. The view, layer graph, requirement coverage, questions, and JSON are projections of that same document. Library definitions live separately in `library.json`, pinned from the existing official Langflow template copy. No upstream native definition is edited.

## What is present

- Intent-specific Process, Flow and Composite responsibility records.
- Four distinct component occurrences referencing three pinned native definitions: Chat Input, Agent (used twice), Chat Output.
- Same-occurrence membership and named Message connections.
- Configuration references below Components; no credential storage or activation.
- Requirement discovery status, realization links and explicit unresolved boundaries.
- Successive authoring revisions from intent through proposed decomposition and grounded realization.
- A design-only checkpoint verified through the visible UI; business questions remain unanswered.

These are authored proposals, not an autonomous Paper 4 generation run. The controller-to-real-library adapter remains a recorded gap. Flow/Process semantics, business policy and behavior remain open. No generated application is executed or deployed.

## Editing and preservation

`/instance-api` reads the current document/library/history. The V3 instance controls send narrow actions against a known base revision. The local Vite plugin serializes mutations, validates envelope shape with Ajv 8.18.0 and semantic references/interfaces, writes a new revision, then atomically updates the head pointer. A stale base returns a conflict instead of overwriting another change. Earlier revisions are read only.

Requester answers are not invented. Selecting categories retains the missing decision-rule gap. Requesting an integration retains the missing connector gap. Selecting API Proxy records a reference and retains native binding/activation unknowns. Confirming a requirement accepts intended scope, not its behavioral truth. A checkpoint changes neither requirements nor answers.

Files are saved to disk. This feature does not introduce automatic Git publishing, a production multi-user registry, arbitrary JSON editing, a general compiler, or new authentication.

## Verification

- Nine storage/projection tests cover immutable history, concurrent/stale writes, scope preservation, missing integration/binding gaps, corrupted references and revision-cycle rejection.
- The actual V3 entry builds.
- Runtime same-origin rejection, stale-base conflict and unsupported-action rejection were checked without changing business answers.
- Visible browser checks cover checkpoint save, reopen, historical read-only revision, intent-only empty state, composite-member inspection and canonical JSON.

The shape schema checks the envelope; the semantic validator checks the represented links and mappings. Neither proves task behavior or completeness of the requirements. Tests mutate temporary copies rather than answering questions in the real instance.
