# Paper 7 — local production feasibility

Research snapshot: 2026-10-30. This is a proposed production architecture, not an installed or benchmarked pipeline. No model downloads, inference, service changes, publishing or account access occurred in this investigation.

## Recommendation

Start with original software/workflow explainers: a locally drafted script, locally synthesized narration, original diagrams and genuine recordings of a controlled demonstration, assembled deterministically into video. This exploits the existing machine and produces verifiable subject matter. Screen captures are original local captures, diagrams are generated graphics, and neither should be described as AI-generated photographic footage. Fully generated motion footage is optional research, not a dependency of the business plan.

Use a local 8B-class language model through MLX LM, Kokoro through MLX Audio, and a pinned FFmpeg rendering environment. Research can involve online primary sources and hosted research assistants; the intended script/audio/visual/render production path runs locally. Online distribution and platform analytics are separate services. Local generation does not imply offline research or passive income.

## Current host and reusable material

| Item | Current evidence | What this establishes | Limit |
|---|---|---|---|
| Host | `sysctl`: Mac15,8; Apple M3 Max; 68,719,476,736 memory bytes | 64 GiB unified-memory Apple Silicon host | No throughput, thermal or usable-free-memory measurement |
| Tools on PATH | `/opt/homebrew/bin/ollama`, `/opt/homebrew/bin/uv` | Executables available | No inference or running-service proof |
| FFmpeg/ffprobe | Neither resolved by `command -v` in current shell | Not available on this PATH | Could exist inside an environment/container; no broad scan performed |
| Existing video project | `/Users/x/projects/money/runtimes/daily-video/README.md` | Documents scripts, synthetic narration, animated presenter, captions, source ledger, manifest and video checks | Documentation is not a fresh execution; three-topic bounded inventory; scheduler documented disabled; no account connected |
| Other local project material | `runtimes/moneyprinterturbo`, `runtimes/laya`, `runtimes/f5-tts` inventory paths | Existing implementation/evidence may be reusable after audit | Presence is not current readiness or permission to change services |

The existing daily-video approach uses an illustrated presenter and diagrams, not generated photorealistic footage. Its README explicitly distinguishes technical file checks from editorial correctness. Preserve this distinction and the disabled scheduler.

## Constrained shortlist and rights boundary

| Stage | Candidate | Primary evidence / permission | Mac feasibility and decision |
|---|---|---|---|
| Script and structured scene plan | MLX LM + Qwen3-8B | [MLX LM](https://github.com/ml-explore/mlx-lm) is MIT and targets Apple Silicon; [Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B) identifies Apache-2.0 weights | Leading candidate. Pin upstream model revision, quantization recipe, prompt and seed. 4-bit 8B raw weights are roughly 4GB by arithmetic, not an actual process-memory estimate; cache/context/framework add memory. No local quality/speed result yet. |
| Narration | Kokoro-82M through MLX Audio | [Original model card](https://huggingface.co/hexgrad/Kokoro-82M) declares Apache-2.0; [MLX Audio](https://github.com/Blaizzy/mlx-audio) is MIT and documents Apple Silicon/Kokoro | Leading candidate with stock voices. Verify exact converted checkpoint and upstream lineage separately; runtime MIT does not license every supported model. No speech benchmark run. |
| Voice alternative | F5-TTS | [Official repository](https://github.com/SWivid/F5-TTS#license): code MIT; pretrained models CC-BY-NC, separately documented [checkpoint licenses](https://github.com/SWivid/F5-TTS/blob/main/src/f5_tts/infer/SHARED.md) | Official noncommercial pretrained weights excluded from revenue pipeline. Apple Silicon instructions exist, but execution support cannot remove model restrictions. A separately licensed checkpoint needs independent verification. |
| Still imagery | FLUX.1-schnell, optional | [Official card](https://huggingface.co/black-forest-labs/FLUX.1-schnell): Apache-2.0 and 12B parameters | Secondary candidate, not necessary for first content. [Diffusers MPS documentation](https://huggingface.co/docs/diffusers/main/en/optimization/mps) describes Apple Silicon execution; it is not proof of this model's performance on this host. Pin compatible versions and measure. Do not substitute another FLUX variant under this permission. |
| Motion visuals | Local diagrams, controlled demonstrations, captions and deterministic animation | Original scene specifications and self-created local recordings | Primary route. Inspect captured screens for credentials/private data. Respect software, fonts, music, icons and third-party asset terms; own the demonstrations and explain what is real versus illustrated. |
| Full text-to-video | Wan2.1, deferred feasibility study | [Official repository](https://github.com/Wan-Video/Wan2.1) provides implementation and hardware guidance | Published NVIDIA/VRAM figures are not Mac benchmarks. Unified memory is not CUDA support. Do not put full generative video on the critical path without a reproducible Apple-compatible run, measured costs and exact checkpoint-license audit. |
| Final assembly | FFmpeg / ffprobe | [Official legal page](https://ffmpeg.org/legal.html): LGPL2.1+ baseline, optional components change build to GPL | Pin executable/build configuration and dependencies. Rendering videos and redistributing a linked program/binary are distinct licensing questions. Inspect actual build; no current FFmpeg binary verified. |

An Apache/MIT label is not a guarantee that every output is free of third-party rights. Preserve notices where required; inspect exact distribution terms. Reference-voice cloning requires explicit authority to use that person's recording and voice for this purpose. Do not clone public figures or treat an uploaded reference clip as permission. Stock voice selection avoids introducing a personal reference recording, but still needs model and output-use review.

## Proposed local pipeline

| Step | Input → output | Automation / acceptance gate |
|---|---|---|
| Source dossier | Primary links, dates, claims → approved factual outline | Retrieval can be automated; factual review records uncertainty and source freshness. No unsupported facts passed straight to narration. |
| Script | Outline → script + scene JSON | Local LLM proposes hook, explanation and call-to-action; schema validation and claim-to-source mapping; human editorial approval. |
| Demonstration | Scene JSON → local controlled captures or original diagrams | Use a reproducible sample project; generated charts require real source data or explicit illustrative labels. Never invent a successful demonstration. |
| Narration | Approved script → WAV + voice manifest | Local Kokoro; pronunciation, clipping and intelligibility checks; exact model/voice tracked. |
| Timing and render | Scenes/audio → video + captions + thumbnail | Deterministic composition, burned-in/sidecar captions, full decode, dimensions/duration/audio checks. Captions must be checked against spoken words. |
| Release package | Approved video → export folder | Human reviews usefulness, factual accuracy, rights and disclosure. Upload is a later authorized integration, not part of this research run. |

Keep launchers, lockfiles, scene schemas and manifests in the repo. Keep model weights, environments and caches in a dedicated removable runtime outside Git. Run LLM, TTS and image generation sequentially initially so shared GPU memory and cancellation remain manageable. Preserve intermediate files and resumable stages; do not start multiple unbounded model workers.

Every artifact should identify source claims, prompt, model revision/quantization, voice, input hashes, scene assets and their origins, tool versions, start/end times, QA decisions and final file hashes. Failed production must remain a recorded failure, not silently replaced with an unrelated clip.

## What must be measured before a publishing commitment

The first authorized implementation milestone should produce one useful 60–120 second explainer, locally and reproducibly. This is a proposed test duration, not a measured capacity. Measure each stage's wall time, peak memory, output size, retries and human review minutes; record narration intelligibility, technical accuracy, originality and retention-relevant editorial quality separately. Measure energy with a suitable meter if cost matters; do not substitute an assumed laptop wattage for observation. Price amortized hardware, electricity, storage, human review and failed renders. A successful MP4 proves media assembly; it does not prove audience demand, platform eligibility or profit.

Unresolved: exact installed model set and licenses; reproducible MLX/Kokoro environment; chosen voice; FFmpeg location/build; runtime throughput/quality; audience/topic demand; platform monetization and synthetic-media policy; local model ability to write accurate useful scripts. The architecture is plausible and bounded; revenue viability remains unproven.

## Evidence and reproducibility

All linked primary pages accessed 2026-10-30. `sources/local/repository-revisions.json` records fetched upstream HEADs where available; these document the research snapshot, not an installed version. Before implementation use immutable commit/model revisions and archive the license text alongside the selected artifact. The source manifest records claims, limits and local read-only observations. No claim of current production readiness follows from a repository README.
