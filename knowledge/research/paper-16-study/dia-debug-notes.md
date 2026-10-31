# Dia intelligibility investigation

User reported the original Dia comparison recording was not meaningful. Acceptance is intelligible, correct target words, not successful WAV creation. All original takes are retained.

Target: “I need you to stay right here.” Seed 7.

Local diagnostic ASR: Systran/faster-whisper-tiny.en, revision 0d3d19a32d3338f10357c0889762bd8d64bbdeba, stored externally under ~/.local/share/swarms/paper16-asr. Fixed English, beam 5, no VAD, no text prompting. It recovers the exact sentence from IndexTTS and VoxCPM2 positive controls. It returns no text for the original reference-conditioned Dia take and the fresh no-reference take. ASR is fallible and supplements listening; no recognised words is not itself proof of silence.

Codec isolation: DAC encode/decode round-trip of the positive-control sentence is transcribed correctly. This weighs against a general codec failure.

Isolated official implementation trial: two files from Blaizzy/mlx-audio commit 0018b2e470224a166cfe5e6a41e79b1d8be9c5e7 (Dia cache/prefill update) are loaded only in the study worker. Installed VoiceStudio and its upstream checkout are unmodified. Existing checkpoint still fails the exact-word check (ASR: “Mm-hmm.”). The code update is therefore not an established fix.

Next controlled variable: official mlx-community/Dia-1.6B-fp16 conversion, pinned revision 4575dd9622ffa7dd14cc4342e1aac4bb7841904d. External path ~/.local/share/swarms/paper16-dia/Dia-1.6B-fp16. Expected weights SHA256 b0a027738bc5a2361f2134f3bf372e4a5923133b13a31c326425c715a32127a6, 3222361673 bytes. No global model selection change. Outcome pending.

Sources:
- https://github.com/Blaizzy/mlx-audio/pull/1037
- https://github.com/Blaizzy/mlx-audio/commit/0018b2e470224a166cfe5e6a41e79b1d8be9c5e7
- https://huggingface.co/mlx-community/Dia-1.6B-fp16/tree/4575dd9622ffa7dd14cc4342e1aac4bb7841904d

## Official documentation audit

Read the Nari Labs README Generation Guidelines and example/voice_clone.py, the original HF model card, the MLX Dia model page and fp16 conversion card. Important mismatch: Nari recommends moderate length (shorter than ~5 s can be unnatural; longer than ~20 s can rush); alternating speaker tags, exact tagged audio-prompt transcripts, 5–10 s reference audio, and a closing speaker tag. The original short single sentence is not a suitable sole model-qualification test. The adapter's repeated same-speaker tag across reference and target also deserves a controlled correction. These are documented protocol issues, not yet established causes of our unintelligible output.

- https://github.com/nari-labs/dia#dia
- https://raw.githubusercontent.com/nari-labs/dia/main/example/voice_clone.py
- https://blaizzy.github.io/mlx-audio/models/tts/dia/

Further observation: the original checkpoint leaves `training` empty; the installed configuration defaults its activation dtype to bfloat16. The newer conversion explicitly sets float16 weights and activations. Precision is another difference to isolate if the new conversion improves intelligibility; it is not yet attributed as root cause.


## Verified repair

The original VoiceStudio adapter with the longer, documented-format passage recovered every expected word. This shows the old engine can produce intelligible speech and the cache/checkpoint update alone should not be claimed as the cause.

The new study-isolated fp16 worker, corrected same-speaker continuation and closing tag recovered the original short sentence at seed 7 and a second sentence at seed 11. Both pass the local exact-word check; punctuation is ignored. Corrected short take appended as Version 2 of the failed original. A separate new row holds the second sentence. Native request, formatted text, backend pin, raw audio, listening copy and word-check output are preserved per run. Every new Dia generation now runs this local diagnostic and displays pass/fail and transcript, without hiding a failed recording. No emotional fidelity or identity test is claimed.

Tests: five formatting regressions and five existing take-state/recovery regressions pass. Browser version selection updates waveform and duration; corrected audio playback started. See dia-repair-verification.json and review/dia-repair.png.
