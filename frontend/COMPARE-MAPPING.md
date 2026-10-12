# Compare node mapping

Source audit: Agent constructor in swarms/structs/agent.py:289 and Agent.run at line 2542; output formats in swarms/utils/output_types.py. examples/multi_agent/sequential_workflow/research_analyse_write.py demonstrates an analyst as a configured Agent. examples/single_agent/demos/insurance_agent.py includes document comparison in an agent prompt. No standalone generic Compare class was found.

The comparison node uses Agent with model_name, system_prompt, max_loops and output_type. Question, supplied material, criteria and layout are app-owned prompt fields compiled into run(task). They are not native scoring, schema or comparison parameters. The UI shows incoming edge labels but does not pass upstream results yet. No ranking algorithm, weighted scoring or enforced output schema is claimed.

Per-node settings live in React state and reset on reload. Export includes constructor arguments and compiled run task; no Python execution or provider verification occurs.
