# Paper 6 corpus topology explorer

The map is a static analysis tool. It does not execute workflows or mine association/relational rules. It is embedded in Paper 6 after the live inventory, with a full-page link at `/corpus-explorer/`.

## Views and counting

- The overview uses component-type labels and directed type-pair edges. Edge weight counts distinct byte-content graph objects containing the pair once. Shared types are a projection, not shared runtime occurrences. Different code/versions may use the same type label.
- Each original graph retains scoped node IDs, declared ports, saved positions and every recorded edge. Parallel edges between the same occurrences share one drawn line; the inspector lists all underlying port connections.
- Exact file duplicates share a representative with all source origins retained. Nested graph objects are separate. Graphs with only fixture origins are off by default; mixed-origin duplicates retain their origins and are not excluded merely because a fixture copy exists.
- The minimum-graph threshold controls displayed overview edges and therefore affects clustering. Select 1 to expose every recorded type pair. Isolates under the current threshold remain visible. Counts do not assert independent source families.
- Louvain communities are computed on an undirected weighted projection of the displayed directed type pairs with a fixed random seed. The original directed graph is retained. Cluster layouts are deterministic spatial arrangements, not measured semantics or discovered composites.
- Flowise, mixed and unclassified artifacts remain in the corpus index but are excluded from this Langflow explorer.

## Recorded verification

Extraction from the pinned index produced **1,331 graph objects** from **1,276 distinct Langflow byte contents**, containing **9,420 non-note component occurrences** and **8,530 recorded edges**. There were zero file extraction failures. Default nonfixture view: **1,149 graph objects**. This differs from the earlier 1,148 eligible-file count because graph objects and files are different units and this explorer preserves flagged Langflow graphs rather than applying mining eligibility.

Unknowns remain visible: **59 occurrences lack a component-type field** and **109 edge records have a handle that could not be parsed**. These counts are occurrences/events, not numbers of independent graphs. Such edges retain endpoints and unknown port labels; original source exports remain unchanged. Node code and configuration values are never exported. Credential/external binding field names and requiredness can be inspected without values.

Eight controlled extraction tests passed: occurrence scope, handle parsing, exclusion of code/values, unresolved endpoint preservation, parallel-edge preservation, malformed handle reporting, unknown component typing, and nested graph-key distinction. A production build of the explorer passed. Browser verification: overview renders, ChatInput selection narrows to supporting workflows, source search works, AssemblyAI detail renders seven components/five edges with 21 preserved origins, and recorded ports are available in the inspector. Embedded notebook display was checked separately.

## Reproduction

From the repository root:

```sh
python3 knowledge/research/paper-6-study/build_topology.py
python3 -m unittest discover -s knowledge/research/paper-6-study -p test_topology.py -v
```

The extractor hashes each representative against the pinned corpus index and walks nested/encoded graph JSON using the static corpus walker. Generated data is at `knowledge/research/paper-6-corpus/topology/`. Original source files stay local and unchanged. The local Vite server exposes only the fixed index or a validated hexadecimal graph identifier; no arbitrary-file endpoint exists.

Runtime libraries are pinned in the frontend lockfile: Sigma.js 3.0.2, Graphology and graphology-communities-louvain. The initial installed Sigma 4 API differed from the selected renderer API; the renderer was pinned to 3.0.2 and rebuilt. No claim of benchmark performance or mining quality is made.
