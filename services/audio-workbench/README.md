# Programmable Money voice engines

Open http://127.0.0.1:5194/.

The React Flow surface wraps existing Money engines, not new audio algorithms:

- Narration input → validated text.
- F5 generation → PCM audio and instrumented inference report; prepared voice/emotion, seed, speed and sampling steps.
- Master audio → original, master and loudness-matched A/B files; Gentle/Balanced/Present profiles.
- Optional Resemble Enhance → mastered original, enhanced output and matched A/B; evaluation count and denoise strength.

The server compiles a bounded typed chain. Disconnects, wrong-direction wires, enhancement without a master, unprepared references, arbitrary engines and unsupported settings fail before execution. This is a four-component catalog, not an arbitrary graph compiler or native Langflow component registration.

Each run executes in a separate process group, writes isolated artifacts and emits actual stage events. Cancellation signals only that run's process group. Money's saved configuration and latest-output pointers are not changed. Files are served only from the requesting session's run. Source code and existing model assets are reused in place, without new weight downloads.

Start from the Swarms repository root:

    services/research-notebook/.venv/bin/python -B services/audio-workbench/server.py

And from `frontend`:

    ./node_modules/.bin/vite --config audio-workbench/vite.config.js

The UI runs on loopback 5194 and proxies its engine requests to loopback 5195. Research and the main canvas are unchanged.

## Limits

F5 generation is MPS-dispatched; enhancement runs on CPU using Money's existing configuration. Matched listening is provided because signal metrics cannot decide the best-sounding version. Enhancement may change identity, texture or pronunciation. Both active and original ESD references, the bundled research voice, and validated custom-reference upload with an exact transcript are exposed. No licensing clearance or claim of commercial readiness is added. Money's original UI remains available for its other reference-management features.

Runtime artifacts are under `.runtime`. Browser sessions/runs are held by the local server; download audio before restarting it. Files remain on disk. This first adapter is single-user and serializes inference rather than supporting parallel engine jobs.

## Using and verifying

Select a node to edit its settings, then run the graph. Disable enhancement to compare the simpler chain. Save graph downloads settings as JSON; Load saved graph validates it before applying it. Reference preview plays the selected prepared sample. Outputs belong to the submitted run and are retained when canvas settings change.

Run contract and HTTP checks from the repository root:

    services/research-notebook/.venv/bin/python -m unittest discover -s services/audio-workbench -p 'test_*.py'

Independently verify a completed run with Money's existing Python environment:

    /Users/x/.local/share/money/f5-tts/venv/bin/python -B services/audio-workbench/verify_audio.py services/audio-workbench/.runtime/<run-id>

This checks actual WAVs, source-copy hashes, inference evidence, loudness and original Money settings/pointers. The Paper 12 notebook links this workbench and records the measured results.

## Full audio controls

See [CONTROLS.md](CONTROLS.md) for the source-to-workbench audit, advanced parameter coverage, independent stage actions, upload limits, and session/export behavior. The full-controls verification records real custom-reference generation, non-default DSP/neural settings, uploaded-recording processing and enhancement-only processing.
