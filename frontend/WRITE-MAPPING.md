# Write node mapping

Writer pattern: examples/multi_agent/sequential_workflow/research_analyse_write.py configures a Writer Agent with system_prompt, model_name and max_loops. Agent constructor and run are in swarms/structs/agent.py. Task, source material and writing format compile into run(task); writing format is an instruction, not a native renderer.

File functions: swarms/structs/autonomous_loop_utils.py:698 create_file_tool(agent, file_path, content) and :752 update_file_tool(agent, file_path, content, mode='replace'). Both resolve relative paths against the agent workspace and write UTF-8. Create refuses existing files and creates parent directories. Update requires an existing file; append adds raw text, replace overwrites. Failures return error strings.

The UI exposes a proposed postprocessing mapping to these functions. A future adapter must bind final generated text as content and supply the Agent instance. It is not an implemented pipeline or automatic Agent constructor feature. No file I/O, inference, upstream result propagation, or binary document rendering is implemented. Settings are per-node and reset on reload.
