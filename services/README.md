# EXO alongside Swarm Canvas

EXO source checkout: services/exo (upstream exo-explore/exo, commit 75d8ad2; shallow clone).

Start from the Swarms repository:

```sh
./services/start-exo.sh
```

Dashboard/API: http://127.0.0.1:52416/
Canvas: http://127.0.0.1:5173/

The launcher uses a separate EXO_HOME under services/exo-runtime, discovery namespace 1.0.71 (libp2p-compatible runtime), and offline mode. Workers and cache scanning are enabled; missing model weights cannot be downloaded.

Dashboard and inference verified through the UI on October 13, 2026. The source MLX build required an unavailable Metal compiler. The environment instead uses the published MLX 0.32.3 / mlx-metal 0.32.3 wheels, together with the upstream-configured mlx-lm and mflux forks. The launcher uses --no-sync to preserve this working environment. A dependency snapshot is stored in exo-runtime/verified-requirements.txt. Runtime logs and state are ignored by services/.gitignore.

## Reuse official model downloads

The checkout's discover_existing_model_dirs function automatically includes ~/.exo/models as a read-only root if that directory exists and differs from this service's own model directory. It merges with explicitly configured read-only roots. Existing complete weights are resolved before writable download locations, using EXO's existing completeness check. No files are copied and the official cache is not writable through this root.

Verified resolution of mlx-community/Llama-3.2-3B-Instruct-4bit, mlx-community/Qwen3-0.6B-8bit, and mlx-community/Qwen3.6-35B-A3B-8bit to the official cache. Llama was launched from the dashboard and returned a chat response at 94.5 tokens/sec with the instance marked READY. Offline mode prevents new model downloads. Model placement remains a dashboard action. The official EXO.app service was stopped at the user's request; the Swarms checkout is the active EXO service.

## Repeat verification

```sh
EXO_HOME="$PWD/services/exo-runtime" services/exo/.venv/bin/python services/verify-exo-cache.py
```

This checks discovery edge cases, the real resolver and loader paths, live completed-download announcements, absence of duplicate weights, and presence of an inference runner. Evidence is saved in services/evidence. The existing cache resolution and rescan regression suites passed 26 tests. Discovery covers the official ~/.exo/models cache and explicitly configured read-only roots; it does not search arbitrary unrelated model folders.

## DeepSeek Harness with EXO

Source: services/deepseek-harness, upstream deepseek-ai/deepseek-harness, commit d743267388. Installed dependencies with the frozen lockfile and built runtime artifacts using `pnpm run build --artifacts-only`.

Start with `./services/start-harness.sh`. It runs the supported dsh Web profile on 127.0.0.1:3080, with isolated DSH_HOME in services/harness-runtime. The launch output includes the local login URL. The default model is the already-loaded EXO Llama-3.2-3B-Instruct-4bit instance on port 52416; EXO must be running first. Configuration is in services/harness-exo.patch.yml. Local dummy authentication satisfies the adapter; EXO does not require a cloud credential. External OTel telemetry is disabled; local Session Log, Trajectory, and Host network capture are enabled.

Verified October 13: real model calls returned HTTP 200 from EXO. Session Log displayed provider/model, context capacity, turn/step events, streaming text, usage, and finish status; records survived a browser reload. NodeJS Inspector's Network tab showed the exact local endpoint and response status. Screenshots and findings are in services/evidence/harness-exo-observability.md. This connects Harness to EXO, not Swarms canvas execution.

## Stateful Swarms demonstration

Run `./services/start-swarm-loop.sh` alongside EXO and the canvas. Port 52417 streams real RoundRobinSwarm agent turns through `/run`. Four Agents use EXO's local OpenAI-compatible endpoint and share Swarms conversation history across three rounds. The frontend uses `/swarm-api` through Vite. The objective is a supplied-facts deployment comparison; there is no external research or arbitrary canvas compilation. The Stop control closes the stream, and the backend checks cancellation between agent calls. An already-running inference call may finish. One run is allowed at a time.

DeepSeek Harness was stopped and disconnected from EXO at the user’s request. The launcher no longer applies the EXO overlay or supplies its local credential. Historical verification and session data are retained.

## Two-Mac compatibility repair

The current vendored source uses Zenoh and cannot join the installed v1.0.71 libp2p peer. The service launcher therefore runs the installed official engine at /Applications/EXO.app/Contents/Resources/exo/exo, using this repository's EXO_HOME and port 52416. The vendored source is retained but is not the active engine. It sets namespace 1.0.71, reuses the official cache read-only, uses the bundled macmon helper, and prompts mDNS peer announcements on startup. Verified M3 Max and M3 Pro discovery and GPU, temperature, and power telemetry. This requires EXO.app to remain installed.

## Langfuse

The Swarms-owned deployment is in services/langfuse. Start with `./services/start-langfuse.sh`; dashboard http://127.0.0.1:3000. It has independent volumes and credentials. See services/langfuse/README.md for sign-in, verification, and non-destructive shutdown.

## Live log pipeline

Start `./services/start-log-pipeline.sh`, then open http://127.0.0.1:5173/?example=logs. The dedicated local service runs on 52418. It reads actual Langfuse observations and shows collect, clean/order, categorize, explain, and review stages on the canvas. Collector/cleaner are code; interpretation stages are real Swarms Agents using EXO Llama 3.2 3B at 52415. The controller stops the watcher; an in-flight model call can finish.

This bounded demonstration polls the latest 100 observations in a rolling 24-hour window every 15 seconds, processing up to eight unseen completed observations at a time. It is not a lossless high-volume ingestion system. Observation content hashes are checkpointed in services/langfuse/pipeline-runtime/seen.sqlite; findings and source records remain in that ignored directory. Monitoring inference is not exported to Langfuse, so the watcher does not analyze its own model traces.

Verified all five stages processed existing real connection-error observations. A subsequent explicitly synthetic smoke-test observation was picked up without resetting the watcher checkpoint and completed all five stages. Source counts and IDs come directly from code; AI interpretation is visibly marked unverified because the small local model incorrectly described some supplied fields. No automatic corrections are applied. Evidence screenshot: services/evidence/live-log-pipeline.png.

Watcher continuity: starts automatically with its service, independently of an open browser. Recoverable collection/model errors emit a retry state and retry after 15 seconds without checkpointing failed batches. Browser event streams reconnect automatically. /status reports running, pollCount, lastPoll, lastError, and intervalSeconds. Verified an injected connection failure recovered into successful idle polls; a new labeled smoke-test observation was processed across all five stages while pollCount advanced from 3 to 4. Idle status reads Watching logs. The service remains subject to machine/process shutdown; it is not installed as a system login daemon.

## Supervised log watcher

macOS LaunchAgent local.swarms.log-pipeline now supervises port 52418 with RunAtLoad and KeepAlive. Installation definition: work/install-log-watcher-service.py; installed plist: ~/Library/LaunchAgents/local.swarms.log-pipeline.plist. Logs live under services/langfuse/pipeline-runtime/service*.log. Stop the supervised service with `launchctl bootout gui/$(id -u)/local.swarms.log-pipeline`; start it with `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.swarms.log-pipeline.plist`. Do not launch a second raw instance while the supervised instance owns the port.

Verified two forced worker-process SIGKILL failures: replacement listener appeared automatically. The open browser recovered without reload; durable poll count advanced to 14. A fresh synthetic observation 2d08726eaac64bfd was collected at 10:00:55 and reached the evidence-review output at 10:01:09. The collector displays actual idle checks, record counts and next-check interval. UI checks backend health every five seconds and reconnects an event stream silent for 25 seconds. Earlier injected collection failure recovery test also passed. Mac login/reboot behavior is configured but not exercised. Power-off, sleep, unavailable Langfuse/EXO, or explicit stop prevent actual processing; dependency outages are retried and not represented as successful work.

Visual observability input: /preview and /analyze on the log service implement on-demand context snapshots. The browser selects time range/category, previews records, and gates execution on the source→selector→preview→agent graph. /analyze binds the task to the exact server-held snapshot, not a separate reread. Snapshots are memory-resident (latest 50), expire on service restart, and use local EXO at 52415. Verified through browser handle dragging: disconnected analyst disabled; connected analyst ran; returned exact agentInput ended with the displayed preview payload; changing category invalidated context; errors-only preview returned only ERROR records. Generated explanations remain unverified and do not modify observed runs.
