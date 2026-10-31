# VoxCPM2 documentation audit: emotion control with a saved voice

Reviewed 2026-10-31. Scope: official documentation, model card, and upstream examples/source. No models installed, services changed, or audio generated during this audit. Upstream main observed at commit `cce58a5b59303c9bd63d12f23afe6a49a4a80c59`; hosted documentation can change independently. Installed-runtime equivalence must be checked separately.

## Finding

VoxCPM2 documents a real style-control path for a cloned voice. However, it is a different conditioning path from transcript-guided continuation. A comparison that uses continuation for neutral and reference-only cloning for emotion cannot isolate the effect of the direction alone. This is a test-design problem, not proof that the model cannot produce emotion.

## Documented generation contracts

| Mode | Inputs | Meaning |
|---|---|---|
| Voice design | `text="(description)spoken words"`; no audio | Invent a voice from natural-language attributes. |
| Controllable cloning | `reference_wav_path`; optional parenthesized style instruction in `text` | Extract speaker timbre, then request delivery changes without a reference transcript. |
| Hi-Fi / Ultimate cloning | `reference_wav_path` plus `prompt_wav_path` and exact `prompt_text` | Continue the reference performance with higher fidelity to its existing details. |

The official demo deliberately disables Control Instruction when Ultimate Cloning is selected. Its generation wrapper passes an empty control in that case. With no continuation transcript, the demo formats the style as a parenthesized prefix. Both English and Chinese control instructions are supported. A documented English cloning example uses `slightly faster, cheerful tone`; a long narrative instruction is not a required syntax.

Sources: [Usage Guide: generation modes](https://voxcpm.readthedocs.io/en/latest/usage_guide.html#three-generation-modes), [official app at pinned commit](https://github.com/OpenBMB/VoxCPM/blob/cce58a5b59303c9bd63d12f23afe6a49a4a80c59/app.py), [official repository quick start](https://github.com/OpenBMB/VoxCPM#quick-start).

## What the API actually distinguishes

`reference_wav_path` supplies the cloning reference, structurally separated through reference-audio tokens. `prompt_wav_path` and `prompt_text` must occur together; the core API rejects an unmatched pair. These paths are separately passed into the prompt-cache builder. A generic HTTP field called `instruct` is an application-adapter concept: the documented native API expresses this instruction in `text`. Confirm the adapter's final native arguments, not just the HTTP request.

Source: [core API source at pinned commit](https://github.com/OpenBMB/VoxCPM/blob/cce58a5b59303c9bd63d12f23afe6a49a4a80c59/src/voxcpm/core.py).

## Reference and control quality

The official cookbook recommends at least five seconds of clean reference audio; the usage guide gives a practical range of 5–30 seconds. This is practical guidance, not a hard API rejection rule. A two-to-four-second audition may run, but it does not satisfy that recommendation. Do not loop or concatenate unrelated performances merely to claim a longer reference.

The cookbook treats emotion, speed, and delivery as cloning controls, while warning that cloning is not arbitrary identity transformation. It offers concise style examples and recommends sparse supported nonverbal tags, such as `[laughing]`, rather than invented notation. These are optional expressive tools, not calibrated emotion-strength measurements.

Source: [official cookbook](https://voxcpm.readthedocs.io/en/latest/cookbook.html#cloning-a-masterpiece-voice-cloning).

## Limits of what the documentation establishes

The model card acknowledges variable voice-design/style results and recommends trying 1–3 generations. It does not promise that named emotions are perceptually separated on every speaker, sentence, or seed. It also warns of language-dependent performance and instability with long or highly expressive inputs. English is supported; the presence of Chinese examples does not establish that English emotion control is unsupported.

Source: [official model card: limitations](https://huggingface.co/openbmb/VoxCPM2#limitations).

The native API exposes CFG and diffusion steps; these are general generation parameters, not a calibrated anger/joy intensity scale. Its exposed seed is for reproducibility. Neither a fixed seed nor a successful WAV establishes convincing acting.

Source: [official API reference](https://voxcpm.readthedocs.io/en/latest/reference/api.html), [core source](https://github.com/OpenBMB/VoxCPM/blob/cce58a5b59303c9bd63d12f23afe6a49a4a80c59/src/voxcpm/core.py).

## Recommended diagnostic sequence (inference from the contracts above)

1. Obtain one clean, unlooped 5–10-second example of the selected character, preserving the existing short candidate for comparison.
2. Reproduce the documented controllable-cloning path directly: reference audio only, no prompt transcript or prompt-audio continuation. Log exact native arguments and reference hash.
3. Hold reference, text, seed, CFG, steps, denoising, normalization, and retries constant. Generate reference-only neutral with no instruction, reference-only joy with a concise instruction, and reference-only reassurance with a concise instruction. Keep any Hi-Fi continuation baseline separately labelled.
4. First judge a clear contrast on identical, emotionally flexible wording. Separately reproduce one official expressive example as a capability check; that second test is not a fair emotion-only comparison because its words differ.
5. If delivery still overlaps, repeat a small fixed seed set and inspect the final argument mapping. Do not relabel weak output as successful emotion. Only after this check consider changing reference, settings, or engine.

A waveform difference, ASR success, or different file hash is insufficient. Human listening must independently assess intended feeling, voice identity, wording, and naturalness. These criteria are experimental acceptance rules, not guarantees made by the documentation.
