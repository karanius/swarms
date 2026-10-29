# Paper 5 — Iterative Instance Revision

The algorithm is the subject; the ticket-triage instance is the working example. See `../notebooks/Paper 5 - Iterative Instance Revision.ipynb`.

## Reproduce the notebook

1. Run `npm ci --ignore-scripts` in this directory to install pinned Ajv 8.18.0.
2. Open Paper 5 through Research and run its five code cells using a Python kernel with IPython and Matplotlib and local Node.js on PATH.
3. The cells run the pinned revision study, fifteen temporary-store tests and six exploratory layer-formation cases. Saved tables/plots reopen without execution.

The `implementation/` tree captures the same revision core/store and test-fixture dependency closure used by the live app at capture. Its use avoids depending on uncommitted application scaffolding. It is an experimental source snapshot, not a second editable authority for the live app. Notebook experiments never apply a policy to the live instance. The UI demonstration separately created proposed revision 6 from revision 5; see `observations/live-integration.json`.

## Scope

- Structured policy -> explicit requirement realization -> directed impact closure -> narrow patch -> preservation checks -> guarded revision persistence.
- Fourteen exposed revision cases × three methods; six corrupted candidates; fifteen Node checks.
- Exploratory layer-formation model starts from pinned component metadata, supplied responsibility tags/profiles and relationships. Two composites and one flow can form; process formation stops without a supplied lifecycle contract.
- Six exposed formation cases. Initial one-candidate expected count was wrong and its failed assessment is retained.

These are same-author development observations, not independent peer review. Higher semantics are supplied, not inferred uniquely from native types. Candidate caps truncate enumeration. Behavior, approval, predicate extraction, general synthesis and scaling to hundreds of items remain unestablished.

## Evidence

`protocol.json`, source `freezes/`, `round-1/`, baseline snapshots and `observations/` retain revisions, all failures, final comparisons and the live integration record. Re-running overwrites current observation outputs; version them before changing rules/code. No credentials, models or deployed applications are used by the research scripts.

The live app retains original native component definitions. Components are shown with native names first (Chat Input, Agent, Agent, Chat Output), with instance roles below; composites remain on their own plane.
