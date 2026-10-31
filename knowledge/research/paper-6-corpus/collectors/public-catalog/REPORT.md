# Public catalog collection

Collected 46 accepted graph-bearing Langflow JSON artifacts, representing 43 distinct byte hashes. Original bytes are unchanged; every accepted file passed SHA256 re-verification and JSON parsing. No component code was imported or executed.

## Sources and scope

- Official website [sitemap](https://www.langflow.org/sitemap.xml): examined all 84 listed blog articles, following explicit JSON/gist links. Obtained 3 standalone website JSON downloads and 2 revision-pinned gist JSON files. Follow-up added 3 commit-pinned official-blog-linked GitHub graph files.
- [Hugging Face public Spaces search](https://huggingface.co/api/spaces?search=langflow&limit=1000): discovered 540 Spaces and queried their public metadata/file inventories with four workers. Accepted 38 Langflow JSON files; graph downloads use immutable Space commit revisions. Most Spaces contain only a deployment scaffold.
- Primary website graphs: [GPT-5 routing](https://www.langflow.org/flows/gpt5-flow.json), [deep research](https://www.langflow.org/flows/deep-research-flow.json), [tool guards](https://www.langflow.org/flows/ProtectingAgentWithToolGuards-template.json).
- Primary gist collections: [newsletter helper](https://gist.github.com/philnash/3d665cedee01dbc759d8f16f31283224), [CodeFlow](https://gist.github.com/philnash/ce56510d486f2f5c11bd25b6b68505de).

## Provenance and licensing

manifest.json records source URL, discovery URL, original source path, immutable revision when available, license identifier/status, byte length, collection timestamp, and SHA256 per artifact. Website downloads have no immutable publisher revision: their SHA256 fixes the collected snapshot. HF licenses are declarations from Space cards, not an independent legal assessment. Missing/unknown licenses are explicitly retained as unknown; public accessibility does not imply reuse permission. Robots files and search/sitemap discovery responses are saved under evidence/.

## Exclusions and gaps

- 18 downloaded JSON graphs from Stevross/langflowise are Flowise customNode/inputParams workflows. Original bytes are quarantined under evidence/excluded-flowise, with provenance under excludedArtifacts, and excluded from accepted artifacts.
- 540 HF candidates were bounded by the public search response. 48 metadata/file requests returned HTTP 429; no retries or limit bypass were attempted. Failures are enumerated in manifest.json.
- https://langflow.store failed certificate validation and https://api.langflow.store failed certificate hostname validation. No TLS bypass, login, authorization change, or private catalog access was attempted.
- The migrated 2023 Batch Web Loader article retains the text “Download Flow (gist)” but no downloadable gist URL.
- Three official-blog links target non-org GitHub repositories and were collected during the authorized follow-up: philnash/git-ai-message, cuga-project/cuga-agent, philnash/docling-langflow-pdf-to-markdown. Original HTML candidate failures remain as historical evidence. Their successful follow-up downloads use immutable Git commit URLs, preserve original blog discovery and linked URLs, and include exact-revision license text under evidence/.
- HF dataset search exposed training/parquet datasets; these were excluded as unrelated rather than downloaded.

## Reproducibility

collect.py contains the bounded public discovery/downloader. Its generic graph detector initially accepts any nonempty nodes/edges object; the explicit Flowise exclusion was applied during final schema review. Re-running discovery may change snapshots and includes that known review requirement. File names are sanitized and content-hash-prefixed; no archive extraction occurred.

## Bounded follow-up result

Added 3 graph JSON files: AI Commit Writer (philnash/git-ai-message), CUGA conference preparation (cuga-project/cuga-agent), and PDF to Markdown (philnash/docling-langflow-pdf-to-markdown). Final accepted count: 46 artifact records, 43 distinct byte hashes. All hashes re-verified. License files were downloaded as inert text at the exact artifact revisions.

The HF manifest has **48 HTTP 429 failures** (correcting the earlier informal count of 49). Initial HTTPError records retained error text but did not capture Retry-After/reset headers. Therefore cooldown eligibility cannot be established from recorded evidence; no HF retry was made under the instruction to retry only after a stated cooldown had elapsed. These 48 gaps remain unresolved, with eligibility explicitly unknown. No account, network, permission, TLS, or access-control changes were made.
