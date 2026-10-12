# Read node mapping

Audited source: swarms/structs/autonomous_loop_utils.py, read_file_tool at line 814 and read_file schema at line 399. The autonomous loop registers it in swarms/agents/autonomous_loop.py.

Its single user argument is file_path. An Agent instance is required and supplied by an execution adapter, not the user. Relative paths resolve through agent._get_agent_workspace_dir(); absolute paths are used directly. It reads with UTF-8, truncates output using agent.context_length and agent.model_name, and logs the read to short_memory. Exceptions return text error messages.

No PDF/DOCX parser, OCR, page ranges, encoding selector, extraction criteria, multi-file input, or user-controlled truncation argument exists on this function. The GUI therefore exposes only file_path and describes those fixed behaviors. No files are uploaded, read, or checked by the browser. Per-node settings reset on reload. Export is a JSON mapping, not an executable Python program.
