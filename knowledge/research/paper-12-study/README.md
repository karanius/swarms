# Paper 12 — From Proposed Capabilities to a Verified Local Video

This implements one bounded still-image design from Paper 11 using locally generated diagram scenes, neural narration, measured scene captions and MP4 assembly. It does not execute downloaded Langflow graphs. INSTANCE.json records which capabilities are newly implemented versus actual reused code/models. A template-derived reference is never counted as executed reuse.

Run from the Swarms repository root:

    services/research-notebook/.venv/bin/python -B knowledge/research/paper-12-study/pipeline.py --brief 'Explain how a request becomes a design and then tested software.'

Use a unique --run name to identify a run. Existing run folders are never overwritten. Results are under .runtime, with plan, source model response, scene images, speech, settings, SRT, MP4, full decode log, sampled playback frames and chronological run.json. The notebook records and displays executed evidence.

Requirements use existing local runtimes: Research Python/Pillow, Ollama llama3.2:3b, the pinned Money F5 environment and bundled encoder. No new weights or packages are downloaded. Paths are explicit single-host dependencies; portable installation is not established.

## Evidence boundaries

- Illustrations are a structured visual implementation: local LLM-generated labels rendered as diagrams. No diffusion images or generative motion footage.
- Voice dispatch on MPS is instrumented by the reused F5 adapter. Signal checks and decoding do not establish speech accuracy or naturalness.
- SRT and visible captions have scene-level measured boundaries. They are not word-aligned ASR output.
- The pretrained F5 weights use a noncommercial license. These are research demonstrations, not a commercially cleared content pipeline. See REFERENCES.json and INSTANCE.json.
- Application calls are local and model assets load offline; no claim of OS-enforced network isolation.
- First run failed while trying to record model metadata after producing audio. The adapter now snapshots its lock metadata into its isolated output root; the failed run remains saved.
