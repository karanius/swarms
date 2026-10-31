# Candidate-group boundary inspection

A separate research view at `/candidate-explorer/`, embedded after the repeated-connection explorer in Paper 6. Both earlier explorers are preserved. Uses installed React Flow and the existing source-backed evidence endpoints; no new runtime or network dependency.

The browser chooses one unordered frequent connection pair and a real joint witness. The seed is the actual endpoint set of one edge per feature. `frontend/candidate-explorer/model.mjs` computes the full induced internal graph plus incoming/outgoing cut, retains parallel records and all source origins, and separates unknown incident metadata, unconnected required fields, unconsumed declared outputs and credential-field declarations. Saved values are never inspected. Purpose is editable proposed text. Members remain graph-scoped occurrences; no composite is created or approved.

Membership is editable by clicking nodes or named checkboxes, resetting to seed, one-hop expansion, selecting all or clearing. Drag/zoom are layout operations. Candidate edits are in memory until explicit JSON download, not autosaved to the paper/library. The exported JSON includes source references, edges, declarations, judgments and seed association. Configuration values and credentials are excluded.

## Reproduce

```
node --test knowledge/research/paper-6-study/test_candidates.mjs
node knowledge/research/paper-6-study/audit_candidates.mjs
cd frontend
npx vite build candidate-explorer --outDir ../dist-candidates
```

The audit independently classifies source edges by endpoint membership for one ranked representative of each of 445 unordered pairs. Results: 443 with crossing wires, 322 with unconnected required declarations, 445 weakly connected, 440 acyclic; zero unresolved incident records in that selected subset. Five induced graphs contain a directed cycle. Categories overlap, representatives are selected and dependent, and this is not a held-out test or usefulness evaluation. Eight controlled model tests pass.

The paper-update script preserves a pre-extension notebook backup and the original abstract/map cells. Prior executed mining/figure cells remain unchanged. The new audit figure is descriptive. No workflows, agents, custom node code, model requests, PyClause, AnyBURL or evolutionary learner are executed by this view.
