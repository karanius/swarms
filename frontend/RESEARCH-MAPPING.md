# Research node mapping

Audited checkout: e0c74454. There is no standalone Research node class. This UI uses the Agent-based research example in examples/cli/research_agent_example.sh, not HeavySwarm (which is a multi-phase team).

Source: swarms/structs/agent.py constructor at line 289. Research task maps to Agent.run(task); instructions to system_prompt; model to model_name; loop controls to max_loops (positive integer or auto); planning to plan_enabled; output to output_type. Output enum source: swarms/utils/output_types.py. Optional max_tokens and temperature remain unset when blank. MCP URLs map to mcp_urls.

No Python callable tool registry, MCP connection, inference, execution, or upstream input mapping is implemented. Model availability and provider-specific parameters are not verified by this frontend. Settings are stored per node in React state; they survive closing the panel but reset on page reload. Export configuration downloads constructor arguments and the separate run task as JSON, not executable Python.

The app deliberately exposes a focused subset of Agent options, not its entire constructor. Tool permissions, credentials, memory, provider setup and advanced stopping callbacks are not represented as working controls.
