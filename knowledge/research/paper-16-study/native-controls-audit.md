# Installed native generation controls audit

Audited 2026-10-30 against local source and installed packages only. No model load, download, service start, or synthesis was performed. This establishes parameter wiring, not audible efficacy or deterministic reproducibility.

## Per-take capability matrix

| Control | Full VoxCPM2 (`voxcpm2`) | Installed MLX Dia (`mlx-audio`, model `dia`) |
|---|---|---|
| Seed | Supported: sidecar calls `torch.manual_seed(int(seed))` before generation. | Supported: adapter calls `mx.random.seed(int(seed))`. |
| Sampling steps | `num_step` maps to native `inference_timesteps`, integer clamped 1–64. Direct mapping fallback 10; API omission uses performance profile default instead. | Unavailable in current adapter; not passed to Dia. |
| Guidance | `guidance_scale` maps to native `cfg_value`; request default 2.0. | Unavailable through current adapter. Native private `_generate` has `cfg_scale=3.0`, but public `generate` does not forward it. |
| Speed | Unavailable: discarded by native mapping. | Unavailable: adapter passes `speed`, but installed Dia accepts then ignores it through `**kwargs`. |
| Instruction | Native parenthesized control prefix, including voice traits/emotion/delivery text. It is generative conditioning, not a guaranteed emotion setting. | Unavailable as separate instruction: forwarded by adapter but ignored by installed Dia. Keep speaker tags/nonverbal text in script. |
| Reference | Supported: audio only uses reference cloning; audio plus transcript without controls uses continuation. Audio plus any instruction uses controllable cloning, and transcript is not passed as prompt text. | Audio and reference transcript passed to native generation; transcript prepends to script and audio becomes codec prompt. No 30-second VoxCPM cap applies to Dia in this adapter. |
| Temperature / top-p | Not exposed by this mapping. | Unavailable through VoiceStudio. More subtly, installed public Dia signature declares `temperature=1.3`, `top_p=.95` but does not forward either to `_generate`; adding fields alone would remain ineffective. |
| Exact duration / t-shift / OmniVoice sampling temperatures | Not mapped. | Not mapped. |

Evidence: [generation request fields and defaults](/Users/x/projects/swarms/services/voicestudio/upstream/backend/api/routers/generation.py:1772), [profile default resolution](/Users/x/projects/swarms/services/voicestudio/upstream/backend/api/routers/generation.py:1838), [VoxCPM mapping](/Users/x/projects/swarms/services/voicestudio/upstream/backend/engines/voxcpm2_subprocess/main.py:196), [VoxCPM seed](/Users/x/projects/swarms/services/voicestudio/upstream/backend/engines/voxcpm2_subprocess/main.py:263), [MLX adapter](/Users/x/projects/swarms/services/voicestudio/upstream/backend/services/tts_backend.py:2951), [MLX seed](/Users/x/projects/swarms/services/voicestudio/upstream/backend/services/tts_backend.py:3037), [installed public Dia generation](/Users/x/.local/share/swarms/voicestudio/venv/lib/python3.11/site-packages/mlx_audio/tts/models/dia/dia.py:231), [native private Dia controls](/Users/x/.local/share/swarms/voicestudio/venv/lib/python3.11/site-packages/mlx_audio/tts/models/dia/dia.py:315).

## Reference and execution details

VoxCPM combines instruction and existing leading `(control)` script prefix, strips nested parentheses, and selects continuation only when reference audio plus nonempty reference text exist and no control exists. Reference is always supplied as `reference_wav_path`; continuation additionally sets `prompt_wav_path` and `prompt_text`. It bounds `max_len` to `min(4096,max(256,len(text)*6))` and disables bad-case retries (one attempt). [Source](/Users/x/projects/swarms/services/voicestudio/upstream/backend/engines/voxcpm2_subprocess/main.py:196).

The parent conservatively trims reference near-silence with 50 ms edge padding and caps the first 30 seconds after trimming. Preparation is fail-open, so this cap is not a validation guarantee if preparation fails. VoxCPM trims generated trailing silence and advertises own mastering, skipping generic mastering. [Reference preparation](/Users/x/projects/swarms/services/voicestudio/upstream/backend/services/tts_backend.py:2044), [sidecar wrapper](/Users/x/projects/swarms/services/voicestudio/upstream/backend/engines/voxcpm2_subprocess/__init__.py:38).

MLX Dia receives `[S1]` automatically for untagged script/reference text; existing leading `[S1]`/`[S2]` is retained. Installed Dia splits lines and two-speaker turns internally. For controlled experiments, use single utterances, explicit tags, and `max_chunk_chars=0` so VoiceStudio does not additionally split text and increment seed per chunk. VoiceStudio creates a concrete random seed if omitted. Store the returned actual seed; a fixed seed is a repeatability aid, not proof of identical audio across hardware/package changes. [Tagging](/Users/x/projects/swarms/services/voicestudio/upstream/backend/services/tts_backend.py:2729), [native segmentation](/Users/x/.local/share/swarms/voicestudio/venv/lib/python3.11/site-packages/mlx_audio/tts/models/dia/dia.py:248), [seed materialization](/Users/x/projects/swarms/services/voicestudio/upstream/backend/api/routers/generation.py:2196), [chunk seed](/Users/x/projects/swarms/services/voicestudio/upstream/backend/api/routers/generation.py:1351).

Neither audited speed path performs time stretch. Any later speed adjustment must be labeled **Post-processing: tempo**, preserve the native take, and record method/factor separately. Do not present the current API speed field as native control for these models.

## Installed assets observed

Paper 14 download ledger records complete assets, and the corresponding weight files are present in the external runtime cache `/Users/x/.local/share/swarms/voicestudio/cache`:

| Asset | Revision | Recorded bytes |
|---|---|---:|
| `mlx-community/Dia-1.6B` | `de4fa8c178ca5cc4e9d884b55b03fcfaa0995162` | 6,444,684,602 |
| `mlx-community/descript-audio-codec-44khz` (codec dependency) | `91dff27c81edbb0992be17ac51d2c7d515411a32` | 306,645,112 |
| Full `openbmb/VoxCPM2` | `32279effe8c19989596f05d353d1447f51d9e915` | 4,960,730,347 |

The full VoxCPM launch path explicitly selects that full snapshot; do not confuse it with the catalogue's separate `mlx-community/VoxCPM2-8bit` option. [Download ledger with prior hashes](/Users/x/projects/swarms/knowledge/research/paper-14-study/downloads.json:1), [launch selection](/Users/x/projects/swarms/services/voicestudio/launch.py:12), [MLX catalogue](/Users/x/projects/swarms/services/voicestudio/upstream/backend/services/tts_backend.py:2782). Hashes were not recomputed during this read-only audit.

Existing F5 baseline external runtime `/Users/x/.local/share/money/f5-tts` also contains `SWivid/F5-TTS` v1 Base weight (1,348,435,761 bytes; revision `84e5a410d9cead4de2f847e7c9369a6440bdfaca`) and Vocos weight (54,365,991 bytes; revision `0feb3fdd929bcd6649e0e7c5a688cf7dd012ef21`). Its existing enhancer checkpoint is a processing asset, not another TTS model. [Locked baseline assets](/Users/x/projects/money/runtimes/f5-tts/models.lock.json:1), [baseline integration](/Users/x/projects/swarms/services/audio-workbench/worker.py:5). This is a scoped inventory of these known runtimes, not an assertion that every laptop TTS cache was searched.

## Recommended take schema and honest labels

Persist model ID/revision, engine/package version, script and tags, requested and effective seed, reference hash/transcript, instructions, steps/guidance where supported, chunking, native audio path/hash, then separate processing lineage. For VoxCPM expose **Seed**, **Diffusion steps (1–64)**, **Guidance**, **Voice/delivery instruction**, and **Reference mode**. Use explicit steps rather than an implicit performance profile when comparing takes. For Dia expose **Seed**, **Tagged script**, **Reference audio**, **Reference transcript**. Label remaining fields **Unavailable in installed Dia adapter**, rather than displaying inactive values as applied settings. For both models label speed **Native speed unavailable** and offer independently recorded tempo processing only when requested.
