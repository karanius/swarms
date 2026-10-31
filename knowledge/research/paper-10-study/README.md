# Paper 10: capability search

Open **Paper 10 — Capability Search for Instance Building** in Research. Run its setup/search-controls cell, type a question, and select **Search library**. The default mode separates recognized capability facets; use the dropdown to inspect whole templates, archived component definitions, or connected subsets.

## Request-understanding upgrade (revision 2)

Questions now separate requested capabilities, local/offline/Mac/Apple Silicon constraints, alternatives, and display instructions. A versioned vocabulary covers media generation, input, narration, transcription, subtitles, assembly, research, audience, finance-related evidence, data handling and retrieval. Unknown clauses remain explicitly unmapped; the vocabulary is not universal natural-language understanding.

Each returned piece has `supported`, `partial`, `unknown` or `not_found` evidence status. Supported means an archived declaration, not proven runtime behavior. Local/Mac requirements remain partial when not verified; named external-service components are flagged as conflicts. API existence is not proof of a paid plan. Video assembly not found in a bounded candidate pool is not impossibility. No architecture, ordering, instance composition or build plan is generated.

`request_analysis.py` contains interpretation and qualification. `test_upgrade.py` adds intent, negation, unknown-clause and qualification regressions; `evaluate_upgrade.py` compares the preserved v1 engine against the user's exposed video request. `UPGRADE-EVALUATION.json` records results. The original implementation and pre-upgrade notebook are preserved in `revisions/search-v1/`. Re-run tests with `python -m unittest discover -s knowledge/research/paper-10-study -p 'test_*.py'` in the Research environment.

The index covers 1,148 distinct eligible non-fixture Langflow file contents. It records 1,148 template documents, 2,280 archived component-definition variants, and 4,954 observed connected groups. These are searchable records, not independent designs or validated composites. A component record can collect occurrences across source graphs. Connected groups are bounded one-hop neighborhoods of two to four nodes; they are candidates for inspection, not automatically meaningful units.

Retrieval combines SQLite FTS5 field-aware BM25 with existing local Nomic embeddings. Weighted reciprocal-rank fusion is a ranking heuristic, not a calibrated probability. An explicit capability vocabulary expands common research questions. Unknown terms do not receive an answer solely because an embedding has a nearest neighbor. Similar structural versions are diversified in the display, while remaining individually inspectable.

Every result includes original source/revision/license metadata, actual archived port declarations, saved graph wiring, boundary connections and declared dependencies. Saved operational inputs, credential values and executable component code are excluded. Selected redacted prompt and schema descriptions are indexed as untrusted capability evidence. Required fields are marked for binding review, never assumed absent or correctly configured. No downloaded component code is imported or executed. Current library/version compatibility, license suitability and task performance remain unverified.

**Monetization questions:** company pricing and stock analysis are not evidence of creator earnings. The engine explicitly reports this gap and has no private-account access. It retrieves building pieces, not a profitable business or an assembled instance.

Index source files are SHA-verified during extraction and displayed matches are rechecked. Changed source files are withheld; a changed collection index produces a stale-snapshot warning. If the local embedding service or pinned model is unavailable, the engine reports lexical fallback instead of silently claiming semantic search.

## Reproduce

From the repository root, using the existing Research Python environment:

```sh
services/research-notebook/.venv/bin/python -B knowledge/research/paper-10-study/search_engine.py
services/research-notebook/.venv/bin/python -B knowledge/research/paper-10-study/test_search.py
services/research-notebook/.venv/bin/python -B knowledge/research/paper-10-study/evaluate.py
```

Index rebuild reads the preserved corpus and calls only the existing local embedding endpoint. No model download is automatic. `.runtime/` holds derived SQLite/cache/vector data and can be rebuilt. `INDEX-REPORT.json` and `EVALUATION.json` record the snapshot and exposed development evaluation.

The eight-query benchmark checks whether expected component types occur in the top six template results, using the same template search space. This weak relevance proxy does not establish semantic correctness, independent generalization, faster assembly, compatible wiring or execution success. No corpus templates are run by the benchmark.

Only new Paper 10 resources and the new notebook are authored. Prior notebooks are hash-checked against `preserved-papers.json`.
