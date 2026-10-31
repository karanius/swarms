# Langflow static corpus inventory

Snapshot: 2026-10-29T17:45:06.343423+00:00. Rerun with `python3 knowledge/research/paper-6-corpus/index_corpus.py` from the repository root. This script only reads raw artifacts and manifests and rewrites derived inventory outputs. Collector manifests may continue growing; their snapshot hashes are recorded in the index.

**2942 provenance records; 1374 distinct verified byte contents.** There are 307 exact-byte duplicate groups and 1568 provenance records beyond the first copy. Copies retain every source record. These are source graph artifacts, not a count of independent production templates.

| Collector | Artifact records | Source records | Reported failures |
| --- | ---: | ---: | ---: |
| community-github | 2767 | 376 | 7 |
| official | 129 | 10 | 1 |
| public-catalog | 46 | 579 | 57 |

## Static inspection

- artifacts: 2942
- statusCounts: {'graph-artifact': 2942}
- graphFormatCounts: {'langflow': 2836, 'unknown': 51, 'mixed-or-ambiguous': 1, 'flowise': 54}
- miningEligibleStaticCandidates: 1593
- uniqueLangflowVerifiedByteContents: 1276
- uniqueMiningEligibleByteContents: 1148
- verifiedArtifacts: 2942
- uniqueVerifiedByteContents: 1374
- duplicateByteGroups: 307
- duplicateProvenanceRecordsBeyondFirst: 1568
- provenanceCompleteArtifacts: 2942
- provenanceIncompleteArtifacts: 0
- sourceBackedVerifiedArtifacts: 2942
- unknownRevisionArtifacts: 3
- fixtureArtifacts: 1246
- nonfixtureArtifacts: 1696
- recognizedGraphObjects: 3475
- nonemptyGraphObjects: 3475
- malformedGraphShapes: 1
- malformedJsonArtifacts: 0
- emptyGraphObjects: 0
- graphObjectsWithStructuralIssues: 31
- licenseLabels: {'MIT': 2093, 'unknown': 774, 'Apache-2.0': 70, 'GPL-3.0': 5}

`index.json` contains complete source records, collector queries, all collector-reported failures, caps, inaccessible sources, and coverage metadata. `index.csv` is the compact artifact inventory. `sources.csv` records every item origin, including every exact-byte duplicate; unknown repository/revision/license stays explicit. Mandatory provenance checks require the local file reference, original URL/path, collection time, SHA256, and license metadata. Items failing these checks are flagged and excluded from the source-backed count. Official collector coverage is detailed in `collectors/official/REPORT.md`; other collector reports supply their collection limits. Licenses without collected text or explicit metadata remain unknown; public accessibility does not establish reuse permission. SPDX labels are copied only from explicit collector declarations; no license identity is inferred from accessibility or text. Collected license references and missing references are recorded for review; no code/content licensing conclusion is made.

## Recognition and limitations

Graph-shaped objects are recognized recursively as objects containing both `nodes` and `edges` arrays, including nested exported flows and JSON-encoded strings. Langflow format requires node.data.node.template dictionary evidence. Flowise format is identified by its input/output-anchor schema or agentFlow input schema; mixed and unknown formats remain explicit. Format evidence counts are retained per graph. Empty graphs are recorded separately. The miningEligible flag is only a conservative static candidate flag: it excludes Flowise, mixed/unknown formats, fixtures, missing provenance, structural problems, and unknown non-note node schemas; it does not validate behavior, rights, independence, or component boundaries. Invalid JSON, missing files, hash mismatches, and files without recognized graphs have explicit statuses. Graphs with non-object nodes/edges, missing or duplicated node IDs, or dangling edge endpoints retain structural issue counts. Fixture classification uses source path and collector metadata; it is a provenance hint, not a production-status determination. Component configuration, credentials, and code values are never printed by this indexer.

The optional typed topology hash includes component-type counts and directed type-pair counts only. It is deliberately lossy: matching hashes are merely candidates for later inspection, not graph isomorphism, semantic equivalence, independent templates, or validated composite boundaries. Exact-byte identity also does not establish independent authorship. Counts do not estimate completeness across the internet. Undiscovered, removed, private, rate-limited, capped, dynamically generated, or nonstandard exports remain outside measured coverage.

Downloaded component code was never imported, evaluated, or executed. Raw files remain immutable and local. This inventory performs no rule mining. Methods papers and reading notes are in `methods/`; paper hashes and primary URLs are in its manifest.

## Reported inaccessible sources, failures, and limits


### community-github

- {"repository": "FatimaTabassum743/LangFlow-WorkFlows", "error": "gh: Git Repository is empty. (HTTP 409)\n"}
- {"repository": "sadmanali/cerebra-ui", "path": "frontend_test/performance/reports/home-page-1762184656444.json", "error": "The read operation timed out"}
- {"repository": "4944Virginia/langflow-mcp-ultimate-workflow", "error": "gh: Git Repository is empty. (HTTP 409)\n"}
- {"repository": "marreiro23/Langflow-Docker", "error": "gh: Git Repository is empty. (HTTP 409)\n"}
- {"repository": "nta-jeremy/rag-langflow-nta", "error": "gh: Git Repository is empty. (HTTP 409)\n"}
- {"repository": "Luv-Ratan4/ADVANCED-python-ai-multi-agent-project", "error": "gh: Git Repository is empty. (HTTP 409)\n"}
- {"repository": "LuisOctavioGSeror/langflow_example", "error": "gh: Git Repository is empty. (HTTP 409)\n"}

### official

- {"repository": "https://github.com/langflow-ai/langflow-examples", "error": "Repository not found via git ls-remote; no collection claimed."}

### public-catalog

- {"url": "https://github.com/philnash/git-ai-message/blob/main/langflow/AI%20Commit%20Writer.json", "error": "Expecting value: line 7 column 1 (char 8)", "discoveryUrl": "https://www.langflow.org/blog/ai-generated-commit-messages-langflow-git-mcp"}
- {"url": "https://github.com/cuga-project/cuga-agent/blob/main/docs/examples/langflow/CUGA%20Langflow%20Demo%20-%20Conference%20Preparation.json", "error": "Expecting value: line 7 column 1 (char 8)", "discoveryUrl": "https://www.langflow.org/blog/robust-enterprise-ai-agent-workflow-langflow-cuga"}
- {"url": "https://github.com/philnash/docling-langflow-pdf-to-markdown/blob/main/flow/pdf-to-markdown.json", "error": "Expecting value: line 7 column 1 (char 8)", "discoveryUrl": "https://www.langflow.org/blog/convert-pdf-to-markdown-docling-langflow"}
- {"url": "https://huggingface.co/spaces/Stevross/langflowise/resolve/f4c7aecdc8bd4ee8a4d73c0e1d7ab9839e2985b2/packages/components/tsconfig.json", "error": "Expecting ',' delimiter: line 4 column 40 (char 93)", "discoveryUrl": "https://huggingface.co/spaces/Stevross/langflowise"}
- {"url": "https://huggingface.co/spaces/Stevross/langflowise/resolve/f4c7aecdc8bd4ee8a4d73c0e1d7ab9839e2985b2/packages/server/tsconfig.json", "error": "Expecting ',' delimiter: line 4 column 28 (char 81)", "discoveryUrl": "https://huggingface.co/spaces/Stevross/langflowise"}
- {"url": "https://huggingface.co/api/spaces/tauqeerq/Mera-langflow-v2", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Aslxickrrk/apollo-langflow-backend", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/roshiai/langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Cody95/langflow-agent", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/ICEMAN99/langflow-master", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/asdf08970/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/matsyama/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Fatima1868/langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/kenshi1807/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Fatima1868/Langflow-trial-2", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Maxbrkl/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/zhangyy130/langflow_zh", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Magakantshe/langflow-maga", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Hagar-23/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/xStyNWx/orbit-langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/bacelarfabio/langflow-cafes-serenatto", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/kklarke/langflow-backend", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/prttysav4ge/evaluador-tesis-langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/SAHIL-AGARWAL/my-langflow-backend", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/kartikasari/langflow-app", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/anu-082006/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/srivatsavdamaraju02/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/ubachan/langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/tasneemaddd/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Jokerf1/udl-langflow-backend", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/3akel3ak/finsight-langflow-engine", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/johnnie26/langflow-serenatto", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/adwit2312/video-summarizer-langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/uhunkler/langflow-master", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Kione04/my-langflow-app", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/MatthewsLevy/langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/shakil0608/langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/EstherCardote/langflow-serenatto", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/varunm2004/my-langflow-app", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Varun95/langflow-ui-for-DA", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Abdurrehman999/langflow1", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/thfjgkjlj/langflowproject", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/AMoeed002/langflowspace", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/AMoeedA/langflowModel", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/ubaidkhokhar/langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Kainat043/LangflowSpace", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/hegedus/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/Zakirev/LangflowBackend", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/weiyun660/Langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/AMoeed002/langflowwspace", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/tjtijo/langflow", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/tjtijo/langflow2", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://huggingface.co/api/spaces/pratik-chemate/langflow-agent", "error": "HTTP Error 429: Too Many Requests"}
- {"url": "https://langflow.store", "error": "TLS certificate verification failed; no bypass attempted"}
- {"url": "https://api.langflow.store", "error": "TLS certificate hostname mismatch; no bypass attempted"}
- {"url": "https://www.langflow.org/blog/langflow-micro-tutorials-batch-web-loader", "error": "Article says Download Flow (gist), but migrated page contains no gist URL"}
- {"url": "https://huggingface.co/api/datasets?search=langflow&limit=100", "error": "Search examined; sample repository file lists contain parquet training datasets, excluded as unrelated"}

## Methods papers

- [gSpan: Graph-Based Substructure Pattern Mining](https://sites.cs.ucsb.edu/~xyan/papers/gSpan.pdf): local `gspan-original.pdf`, SHA256 `2ebacfc0869404fa1e12b70e807239819d0910b0bffee0056544a8d3ff54ea53`, verified=True; notes `gspan-reading-notes.md`.
- [Fast and Exact Rule Mining with AMIE 3](https://www.luisgalarraga.de/docs/amie3.pdf): local `amie3-author.pdf`, SHA256 `6c0f4748ee97f03bd914de44f2de4949d5e4600f403f16519fb60bd5945f0d08`, verified=True; notes `amie3-reading-notes.md`.

The public-catalog collector explicitly excludes 18 Flowise-format files retained only as local evidence; its manifest is authoritative. Hugging Face HTTP 429 metadata failures are gaps; no rate-limit bypass was attempted.
