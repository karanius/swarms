# Official Langflow static graph corpus

Collected 2026-10-29T17:32:21.498562+00:00. **129 original source artifacts**, with all SHA256 hashes verified. The 122 Langflow artifacts were also byte-compared against exact local Git objects.

The clean local Langflow checkout and live upstream main both resolved to `aeb10d96bb2ea797696613af931e91ddf51f3320` at collection. Collection used committed Git objects rather than mutable working files. Related official organization repositories were downloaded by exact commit tarball, with concurrency capped at three. No source dependencies were installed, and no downloaded component code was executed or imported. Raw corpus remains local.

| Official repository | Exact revision | Candidate files scanned | Graph artifacts |
| --- | --- | ---: | ---: |
| [langflow](https://github.com/langflow-ai/langflow) | `aeb10d96bb2ea797696613af931e91ddf51f3320` | 2162 | 122 |
| [.github](https://github.com/langflow-ai/.github) | `e190cbcbe692e24467e1db5a1b0d2230a22cf279` | 2 | 0 |
| [langflow-embedded-chat](https://github.com/langflow-ai/langflow-embedded-chat) | `2c412cd047afc25681c2c4fe4c3a1c80a479a953` | 4 | 0 |
| [langflow-railway](https://github.com/langflow-ai/langflow-railway) | `d335be57e16cf2209d0732bc0d1dee2fbb2f5368` | 2 | 0 |
| [langflow-helm-charts](https://github.com/langflow-ai/langflow-helm-charts) | `91508ee3bc5d3b86de3b8d08eaba3541ba87d387` | 5 | 1 |
| [mcp-sse-shim](https://github.com/langflow-ai/mcp-sse-shim) | `b2fb43660c0b7e5dec85d10cc900a7cceb7bc83f` | 1 | 0 |
| [langflow-bundles](https://github.com/langflow-ai/langflow-bundles) | `68428ce16729a385fe1bcc0f1ec91fd5f5f420b9` | 1 | 1 |
| [langflow-client-ts](https://github.com/langflow-ai/langflow-client-ts) | `41cf45dbf2de016cd6bc80b033256028e68cb8ad` | 9 | 0 |
| [langflow-twilio-voice](https://github.com/langflow-ai/langflow-twilio-voice) | `f717cb34e1b0d744a534a4bfb5c6092fc9dc853d` | 4 | 1 |
| [openrag](https://github.com/langflow-ai/openrag) | `8ca47268c9a21b3a33656580a5b8e8ef13e46423` | 118 | 4 |

## Classification

- documentation-example: 4
- repository-graph: 11
- starter-template: 28
- test-fixture: 86

Each artifact preserves its complete original source bytes and original path below `raw/<repository>/<revision>/`. `manifest.json` records repository URL, pinned source URL, exact revision, source path, byte size, SHA256, collection timestamp, and license references. Full source license and notice files are retained under `licenses/`. A license reference describes source licensing; no independent legal conclusion is asserted. Duplicate files remain separate when their provenance differs.

## Coverage and exclusions

The complete tracked official Langflow tree was scanned recursively, including starter_projects, versioned starter snapshots, nested test fixtures, docs, and examples. Graph detection accepts a nonempty object with `nodes` and `edges` arrays anywhere inside a parsed JSON structure. All `.json`, `.jsonc`, `.ipynb`, `.md`, and `.mdx` paths were considered. Markdown/MDX fenced JSON graphs are detected and the entire original document would be retained; none matched in this snapshot. JSONC files are parsed as strict JSON, so comment-bearing JSONC would be excluded. Empty graphs are excluded. A supplementary scan found no excluded Langflow JSON containing nonempty `nodes` arrays.

The official GitHub organization inventory is preserved in `organization-inventory.json`. All ten repositories other than `desktop-updates` were scanned; `desktop-updates` is an application release/update repository and was excluded from graph collection. No graph artifacts matched in five of the scanned repositories. The guessed historical `langflow-ai/langflow-examples` repository was inaccessible (repository not found), recorded under failures. No claim is made to cover private repositories, historical commits, arbitrary dynamically generated flows, non-JSON embedded flow code, remotely linked third-party examples, or every template on the internet.

Primary discovery: [official organization](https://github.com/langflow-ai), [official Langflow main](https://github.com/langflow-ai/langflow), [OpenRAG](https://github.com/langflow-ai/openrag). Exact per-file primary links are in the manifest.
