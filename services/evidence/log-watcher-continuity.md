# Continuous watcher verification — October 13, 2026

- Live /status reported running=true, lastError=null; successive polling counts advanced while no logs were arriving.
- Controlled recovery test: first collection raised ConnectionError; later polls succeeded; worker continued until explicit stop.
- Installed macOS LaunchAgent local.swarms.log-pipeline with KeepAlive and RunAtLoad.
- Twice killed only the watcher process with SIGKILL; launchd automatically replaced it.
- Browser remained open across the second crash; displayed updated check 11 timestamp, then backend poll count 12.
- Added labeled synthetic Langfuse smoke-test trace 6a164fa23a0c4a2d90f04b04b40ac749 after recovery. Observation 2d08726eaac64bfd appeared in the collector at 10:00:55 and reviewer at 10:01:09; poll count 14, running=true, no error. No browser reload for this recovery test.
- Production frontend build passed.

Limits: no reboot or sleep test. Dependency errors retry, not guaranteed useful inference. Small-model interpretations remain visibly unverified. Watching without new records does not imply repeated model work. Upstream polling remains bounded to latest 100 observations within 24 hours.
