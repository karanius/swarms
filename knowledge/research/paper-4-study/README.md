# Paper 4 — Implementing the Boundary Resolution Controller

Open `../notebooks/Paper 4 - Implementing the Boundary Resolution Controller.ipynb` in Research and run its four cells in order. Retain this directory beside the notebooks in the repository. Python with IPython and Matplotlib is available in the existing Research environment.

This is a bounded structural controller subset of Paper 2, not the completed all-layer machine. It supports direct component selection, declared recursive structural refinements, typed graph composition, resource-reference obligations, packaging, prerequisite-aware scheduling, finite alternative branches, charged global budgets and scoped outcomes. Behavioral and activation judgments remain unknown.

## Evidence

- `protocol.json`: final criteria and revision disclosures.
- `controller.py`, `cases.py`, `assessor.py`, `run_study.py`: executable modules.
- `freezes/`: hash-addressed exact source/protocol snapshots created before each round.
- `round-1/`, `round-2/`: earlier observations preserved before assessor/trace changes.
- `observations/`: final 84 main method–case results, 54 exploratory budget-sweep executions, seven deliberate artifact corruptions, four evidence-helper conditions and aggregate acceptance checks.

All 28 cases are same-author/exposed. “Evaluation” denotes registry role, not independent held-out access. The separate assessor is code-level separation, not academic peer review. Two policy variants match all references; the no-frontier comparator misses two reachable cases safely. No invalid accepted artifact was detected by the specified checks. See the manuscript for the narrower warranted conclusions.

The notebook calls these modules directly. The experiment generates specifications and local evidence only: no models, external tools, Langflow runs, credentials or deployment. Running again overwrites current observations deterministically; preserve a versioned copy before future changes. Source freezes and earlier round records are not overwritten.

## Theory provenance

`theory-paper2.md` and `theory-source.json` preserve the Paper 2 Markdown content used as the manuscript's theoretical reference, captured after the final study for archival identity. This capture is not represented as a pre-execution registration.
