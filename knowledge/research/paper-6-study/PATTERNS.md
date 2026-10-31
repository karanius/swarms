# Connected patterns — Paper 6 delivery

The new local visualization is `/pattern-explorer/`, embedded separately in Paper 6 under **Connected pattern explorer**, ahead of the original corpus topology figure. The existing corpus explorer is unchanged.

## What is implemented

- Static, port-named incident-edge extraction from existing source graphs.
- Binary neighborhood transactions keyed by one actual component occurrence in one graph.
- FP-Growth with max itemset size2, minimum joint count5, and a maximum24 distinct incident-feature bound.
- All890 directional associations from445 repeated connection pairs, with exact counts, center-conditioned lift and provenance-group breadth.
- Positive witnesses and observed body-without-head examples. The latter are not behavioral failures or prohibited connections.
- An actual two-connection preview using one source edge for each feature. Two outside roles may alias one occurrence; diagrams keep that identity. For a body-without-head example, only one recorded edge is shown.
- Full source workflow with the preview highlighted, exact connection records and every origin URL/path/revision.
- Current-result-only rule API: malformed IDs return400 and IDs absent from the current complete catalog return404. Old per-rule files cannot be served as current results.

## Observed scope and outcome

1,149 nonfixture graph objects contain8,528 component occurrences. The final study uses8,258 assessable edge-bearing neighborhoods;137 have no recorded incident edge and133 are excluded for unknown incident endpoint/type/port or self-loop. No neighborhood exceeded the24-feature bound in this run.

The final catalog has890 directed associations, of which570 span at least two recorded provenance groups and320 are single-group. Source grouping unions all repository identities and exact-duplicate origins—including fixture origins—before filtering. It does not establish independent authorship or catch all modified copies. The largest group contains499 graphs.

The leading Agent example has242 joint neighborhoods out of357 body neighborhoods,67.8% observed confidence. It is supported by242 graphs and50 recorded groups. Its additional connection is absent in115 neighborhoods across109 graphs. Some graphs contain both kinds of centers. Global lift11.83 versus within-Agent lift1.11 illustrates why the conditioning population must be stated.

Named saved handles are not necessarily declared, currently active or type-compatible ports. Versions are pooled. All data is exploratory; there is no held-out evaluation, causal inference, validated composite, runtime workflow test, AnyBURL/PyClause run or evolutionary experiment.

## Reproduce

Use the research notebook environment with `pattern-requirements.txt`; `pattern-environment.lock` captures the actual resolved package environment. From the repo root:

```sh
services/research-notebook/.venv/bin/python knowledge/research/paper-6-study/mine_patterns.py
services/research-notebook/.venv/bin/python knowledge/research/paper-6-study/verify_patterns.py
services/research-notebook/.venv/bin/python -m unittest discover -s knowledge/research/paper-6-study -p test_patterns.py -v
services/research-notebook/.venv/bin/python knowledge/research/paper-6-study/make_pattern_figures.py
```

Inputs are the pinned corpus topology, not the flattened type overview. The freeze records corpus/index hashes, a combined digest of every loaded derived graph, script hash, parameters and package versions. The miner saves full transaction/witness data as well as the ranked catalog. It never executes downloaded component code. A pandas sparse fill-value FutureWarning is recorded by the pinned environment; the run completes and exact recount verifies the outputs.

## Verification

Nine controlled mining tests passed. A separate implementation recounted all890 rules and checked62,265 preview witnesses across981 source graphs, including source edges and frozen input hashes. The dedicated frontend production build and dependency compatibility check passed. Browser checks cover: pattern selection, positive/without-head switching, original workflow expand/collapse, exact ports, source links, catalog search, empty results, pagination, and notebook embedding. These establish the bounded artifact's operation, not general scientific validity or user comprehension.

Paper6 preserves its original abstract and corpus map figure, updates all fourteen study sections, retains historical literature separately, and includes two executed frozen-output/figure cells. Original source files remain local and unchanged. Internal AI review dispositions are recorded in `pattern-review.md`; this is not external academic peer review.
