# Swarms Langfuse

Dedicated local six-service Langfuse deployment, running alongside the canvas and EXO. Compose project: swarms-langfuse. Dashboard: http://127.0.0.1:3000. Object storage: http://127.0.0.1:9090. Databases and queues are not published to the host.

Start: `./services/start-langfuse.sh` from the repository root. Stop without removing saved data: `docker compose -f services/langfuse/compose.yaml stop`.

Credentials and API keys are generated in `.env`, ignored by Git, with file permissions 0600. The initial administrator is admin@swarms.local; its password is LANGFUSE_ADMIN_PASSWORD in that file. The initialized organization is Swarms and project is Swarm Canvas. Do not expose secret keys in frontend code.

Storage volumes and the network belong to swarms-langfuse. The existing ScoreDust Langfuse containers and volumes are untouched. The network uses explicit subnet 10.243.17.0/24 because Docker's default address pools are exhausted. This deployment reuses installed images; the verified application version is 4.47.0.

Verification: `python3 services/langfuse/verify.py`. Creates a labeled synthetic infrastructure observation, sends it through OTLP, then retrieves it through Observations API v2. Direct OTLP ingestion includes x-langfuse-ingestion-version: 4. Legacy trace ingestion/read APIs are not used.

Verified October 13, 2026: four backing services healthy, web and worker running; public health status OK; synthetic trace accepted and retrieved with ID 9cef2e49f89141fa8c4bb4f2bd931aa0. Canvas HTTP remained 200. This establishes service ingestion and retrieval, not instrumentation of real Swarms execution.

## Swarms agent integration

Native support verified in this checkout: Agent accepts mcp_configs with streamable_http and authentication headers (swarms/structs/agent.py); MCPManager discovers and calls remote tools (swarms/tools/mcp_manager.py); SkillsManager reads skills_dir/*/SKILL.md (swarms/agents/skills_manager.py). Skills are prompt instructions, not a shell executor or permission enforcement system. There is no need to install LangChain to use these capabilities.

Installed official skill at services/agent-skills/langfuse, including its references. The upstream source checkout is services/langfuse/agent-skills. Project-local CLI version 1.2.4 is pinned in cli/package-lock.json; invoke `./services/langfuse-cli.sh api observations list --help`. Its wrapper reads credentials locally; credentials are never sent to the browser or model prompt. Installing the CLI does not automatically grant agents terminal execution.

services/langfuse/swarms_integration.py supplies native Agent options and a local-only OpenTelemetry exporter. services/swarm_loop.py uses these options for its four role agents, records the workflow parent and each real Agent.run invocation, and flushes completed traces. Swarms' own outbound telemetry remains disabled. This captures agent inputs, raw returned outputs, hierarchy and exceptions; complete per-generation token/tool spans are not yet instrumented. All native Langfuse MCP tools, including writes, are exposed to these agents; Langfuse project authentication controls their scope.

Verified: native Swarms Agent discovered 86 MCP tools and loaded the Langfuse skill; MCP listObservations returned stored local observations; CLI observation reads succeeded; a labeled configuration-test AGENT span was exported and retrieved. Runner starts on 127.0.0.1:52417 with this configuration. These checks did not launch a model-driven workflow, test autonomous use of the tools, or evaluate feedback-driven improvement.

Per-node access now defaults to denied. Grants are persisted in pipeline-runtime/grants.json under keys scoped by canvas pipeline and node ID. /grants routes expose enabled and the allowed capability list. Agents receive only granted wrapper tools, not the raw authenticated MCP endpoint; wrappers check the current grant before MCP discovery and again before execution. Supported capabilities are read execution records, read scores, and write numeric scores. No skill is automatically attached; its installation remains available. Context records supplied through a provider wire are separate from direct MCP tool permissions. The existing continuous watcher still supplies its scheduled record batches through code; this change controls direct Langfuse tool use and does not convert that watcher into a general graph executor.

Verified default denial, only allowed tools exposed, granted read success, cross-node isolation, and denial after revoking an already-created tool. Browser enabled/disabled per-node controls and was left denied. Changes apply to the next invocation; revocation prevents subsequent tool calls but cannot retract an already-sent request. These controls are for this local application, not an OS sandbox against malicious Python code or arbitrary shell access.
