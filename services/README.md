# EXO alongside Swarm Canvas

EXO source checkout: services/exo (upstream exo-explore/exo, commit 75d8ad2; shallow clone).

Start from the Swarms repository:

```sh
./services/start-exo.sh
```

Dashboard/API: http://127.0.0.1:52416/
Canvas: http://127.0.0.1:5173/

The launcher uses a separate EXO_HOME under services/exo-runtime, discovery namespace swarms-canvas, and offline mode. Workers and cache scanning are enabled; missing model weights cannot be downloaded.

Dashboard and inference verified through the UI on October 13, 2026. The source MLX build required an unavailable Metal compiler. The environment instead uses the published MLX 0.32.3 / mlx-metal 0.32.3 wheels, together with the upstream-configured mlx-lm and mflux forks. The launcher uses --no-sync to preserve this working environment. A dependency snapshot is stored in exo-runtime/verified-requirements.txt. Runtime logs and state are ignored by services/.gitignore.

## Reuse official model downloads

The checkout's discover_existing_model_dirs function automatically includes ~/.exo/models as a read-only root if that directory exists and differs from this service's own model directory. It merges with explicitly configured read-only roots. Existing complete weights are resolved before writable download locations, using EXO's existing completeness check. No files are copied and the official cache is not writable through this root.

Verified resolution of mlx-community/Llama-3.2-3B-Instruct-4bit, mlx-community/Qwen3-0.6B-8bit, and mlx-community/Qwen3.6-35B-A3B-8bit to the official cache. Llama was launched from the dashboard and returned a chat response at 94.5 tokens/sec with the instance marked READY. Offline mode prevents new model downloads. Model placement remains a dashboard action. The official EXO.app service was stopped at the user's request; the Swarms checkout is the active EXO service.

## Repeat verification

```sh
EXO_HOME="$PWD/services/exo-runtime" services/exo/.venv/bin/python services/verify-exo-cache.py
```

This checks discovery edge cases, the real resolver and loader paths, live completed-download announcements, absence of duplicate weights, and presence of an inference runner. Evidence is saved in services/evidence. The existing cache resolution and rescan regression suites passed 26 tests. Discovery covers the official ~/.exo/models cache and explicitly configured read-only roots; it does not search arbitrary unrelated model folders.
