# Paper 11: architecture proposals from retrieved evidence

Run the setup and controls cells in **Paper 11 — Evidence-Backed Instance Architecture**. Enter requirements and choose **Propose architecture**. Results show capability slots, provisional choices, rejected alternatives, unresolved dependencies, archived ports/configuration/dependencies, semantic-link hypotheses and a machine-readable proposal. **Revise with exclusion** records a child after an explicit candidate rejection, retaining its parent.

This is not an executable instance builder. It reuses Paper 10 retrieval without modifying it, importing or running archived code, purchasing services or deploying anything. Hard constraint conflicts and structurally unresolved sources are rejected. Unknown runtime/hardware fit remains provisional. Type overlap is not semantic compatibility. No adapters, conversions, physical composites or successful deployments are invented.

The media relation profile is authored research theory. Other domains receive candidate slots and explicit missing-relationship-profile gaps, without invented connections. Image-or-video alternatives count as one logical obligation. Source wiring witnesses are separate from authored semantic relations: a witnessed original edge does not prove the intended architecture's semantics.

The local-video study is exposed development evidence. The unqualified first-hit baseline makes known constraint-conflicting assignments; the qualified procedure rejects them, leaving real gaps rather than maximizing apparent coverage. Unknown locality, Apple Silicon/memory support, billing, licensing, API access and behavior remain unresolved until qualified. Initial proposals are always design-only, never automatically accepted.

## Reproduce

```sh
services/research-notebook/.venv/bin/python -B knowledge/research/paper-11-study/test_architecture.py
services/research-notebook/.venv/bin/python -B knowledge/research/paper-11-study/evaluate.py
```

Existing Research dependencies and Paper 10's local index/model are used. `EVALUATION.json` retains executed proposal, revision and baseline observations. Notebook JSON outputs preserve proposal history; `ArchitectureDesigner.restore` validates a saved history against current source contracts. Live widgets require running the setup/control cells after reopening. Runtime history is per kernel, not a new database or remote service.

## Lightweight app

Open http://127.0.0.1:5193/ (also linked near the top of Paper 11).
Launch from the repository root:

    services/research-notebook/.venv/bin/python -B knowledge/research/paper-11-study/app_server.py

One HTML page uses the existing ArchitectureDesigner, not a second algorithm.
Submit a request, inspect candidates/reasons/sources, review gaps, exclude a piece to revise, and download the complete session history as JSON.
Session history is in server memory, expires after a day, and is lost on restart. Download before closing. The app is local-only and never executes archived code.
The HTTP server serializes requests to preserve the existing SQLite connection's thread ownership; this is a single-user research app.

Verification:

    services/research-notebook/.venv/bin/python -B knowledge/research/paper-11-study/test_app.py

Live tests cover proposal/revision, retained parents, session isolation, invalid inputs, origin/host rejection, unauthenticated requests, and nonpublic file paths. The existing 22 engine tests remain applicable.

## Decision-support upgrade

`design_adviser.py` adds material clarification questions, complete requested OR-path comparison, bounded gap diagnoses, and concrete investigation tasks with acceptance evidence. `architecture.py` now ranks admissible candidates using an authored ordering (declared relevance, fewer external dependencies/configuration obligations, primitive scope), retains exclusions across revisions, and seals the derived support in the proposal digest. The app retrieves up to 30 qualified candidates per capability. Media semantic handoffs remain authored; domains without a profile get no invented wiring.

The app exposes request context, comparison, an SVG dependency view, categorized blockers and the next technical task before the long evidence list. A selected approach updates the diagram, blockers and summary together. Input edits visibly leave the previous assessment unchanged until re-submitted. Optional memory/duration values constrain investigation targets, never certify hardware fitness.

`test_decision_support.py` covers OR-path integrity, real source references, clarification, unknown domains, gap categories, no runtime promotion, exclusion/context carryover and tamper rejection. `evaluate_decisions.py` records four exposed development scenarios in `DECISION-EVALUATION.json`. Paper 11 includes the executed scenario table and explicit limitations. This evaluates inspectability and output consistency, not independent human comprehension or generated-system success.
