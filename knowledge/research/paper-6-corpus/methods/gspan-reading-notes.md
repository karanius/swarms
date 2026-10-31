# gSpan reading notes

Primary copy: [gSpan: Graph-Based Substructure Pattern Mining](https://sites.cs.ucsb.edu/~xyan/papers/gSpan.pdf), Xifeng Yan and Jiawei Han, University of Illinois at Urbana-Champaign. The downloaded 26-page author-hosted manuscript displays September 3, 2002 on its first page. Local file: `gspan-original.pdf`; exact SHA256 and collection timestamp are in `manifest.json`.

The abstract proposes frequent subgraph mining using a lexicographic ordering and a canonical minimum DFS code, avoiding the candidate-generation stage of earlier approaches. Canonical representations distinguish structural patterns despite different vertex identifiers. This is a structural frequency method; the paper does not establish that recurring workflow subgraphs are safe, useful, or valid software abstractions.

For this corpus, a later experimental design would first define what constitutes one graph transaction, choose node and edge labels, preserve directed dataflow and port distinctions, and state how isolated/note nodes and nested exports are handled. Exact-byte duplicates and forks must not silently inflate support. Support should distinguish occurrences within a graph from the number of independent graph transactions containing a pattern. The present inventory's type-pair hash is not a minimum DFS code or an isomorphism test.

Potential use: generate recurring structural candidates for review. It cannot alone infer runtime semantics, credential safety, interface contracts, production adoption, causal effectiveness, or composite validity. A workflow-specific directed/attributed graph encoding and a validated implementation would be separate future work. No mining has been performed.

Inspection note: the first page was rendered and visually inspected because this historical PDF has a broken text encoding in ordinary `pdftotext` output. These initial notes are grounded in the title page and abstract, not a claim of a full technical reproduction. The raw PDF is preserved unchanged; the attempted extracted text remains a local auxiliary file.
