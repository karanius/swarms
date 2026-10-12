# Parallel team mapping

Source: swarms/structs/concurrent_workflow.py constructor at line 90; reliability_check requires nonempty agents; _resolve_max_workers uses explicit max_workers or member count capped by MAX_CONCURRENT_AGENTS; _run submits each agent with the same task and collects results. run at line 604 saves conversation. max_loops is documented as unused and not exposed.

Mapped controls: name, description, max_workers, on_error (store or raise), output_type, autosave and run(task). show_dashboard stays false because that is a Python terminal display. auto_save is a separate legacy metadata parameter; the UI only exposes autosave, which enables WorkspaceManager persistence.

Outgoing agent-backed nodes represent proposed members in our canvas convention; this does not compile a graph or create Python agents. Research, Compare and Write use Agent; Read is a file tool and cannot directly be a member. Export keeps bindings separate from constructor arguments instead of pretending IDs are Agent instances.

No synthesis, per-member task dispatch, timeout, deterministic cancellation, runtime execution or browser persistence is claimed. Thread-pool context shutdown can wait for other work even when on_error raises. Settings reset on reload.
