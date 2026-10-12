# Node configuration audit

Source audit of checkout e0c74454. Frontend build and browser configuration/export checks passed. Python inference and file execution were not run.

| Node | Actual implementation | Aligned behavior |
| --- | --- | --- |
| Research | Agent, with research example prompt | Agent constructor defaults: one loop, planning false, retries 3, tool retries 3, automatic context, compression true, memory/state saving false. Research example uses auto loops; that example mode is not the Agent constructor default. |
| Read | read_file_tool | Single required file_path; supplied Agent context; UTF-8 reading, context truncation and error strings. No parser configuration. |
| Compare | Agent with analyst example prompt | App question/material/criteria/layout compile to task; no native Compare class or deterministic comparison scoring. |
| Write | Agent with writer example prompt | Agent conversation output default restored. Optional file output is a separate proposed adapter step, not an Agent parameter. |
| Parallel | ConcurrentWorkflow | Nonempty Agent roster, shared task, automatic workers, store error policy, conversation saving true. max_loops unused and excluded. |
| Review | AgentJudge | Built-in evaluator prompt, weighted prompt criteria, one evaluation round; internal Agent gets one loop. return_score false; reward heuristic is not an approval gate. Agent options forwarded through kwargs. |
| Repeat | RoundRobinSwarm | One full round by default, insertion order, accumulated history. Fixed repetition, not conditional graph retry. |

Models and reasoning effort retain the explicitly selected app presets rather than historical Python model defaults. They remain unverified against a live backend. Input bindings, memberships and conditional edges remain app conventions requiring adapters.

This is a focused supported UI schema, not a full exposure of the Agent's large constructor. Callbacks, callable tools, provider credentials, backend objects, handoffs, marketplace options and model-specific advanced parameters are not represented as working settings. Adding them requires dedicated integration, not generic text fields.

One-time alignment updates defaults, current and saved node configuration while retaining chosen models, instructions, tasks and layout. Existing Compare/Write output format and Repeat round values are replaced with library defaults as requested.
