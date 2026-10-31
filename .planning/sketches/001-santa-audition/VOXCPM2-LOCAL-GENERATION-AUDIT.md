# VoxCPM2 local generation audit

Scope: read-only audit of Santa Stage 3 generation against official documentation. No inference, installations, service changes, or UI changes were performed for this audit.

## Findings

1. Installed engine package is VoxCPM 2.0.3, found in the engine-specific `.venv`. This is VoxCPM2, not the earlier model API.
2. The selected Take 25 reference is exactly 4.0 seconds at 48 kHz. Official guidance recommends a clean reference of at least 5 seconds, with 5–30 seconds a practical range. Below guidance does not prove causation; padding silence would not add speaker evidence.
3. Our actual neutral request includes reference audio and transcript with no instruction. Executing the installed adapter mapping produces `reference_wav_path`, `prompt_wav_path`, and `prompt_text`: continuation/Hi-Fi mode.
4. Our directed requests include the same reference and transcript plus `instruct`. The adapter correctly prefixes `(instruction)` to the target text and drops the prompt audio/transcript while retaining `reference_wav_path`: controllable cloning.
5. Consequently the neutral-versus-directed experiment changes conditioning mode as well as the instruction. The earlier claim that only the direction changed was incomplete. Joy-versus-reassurance uses the same controllable mode, so that particular contrast is not explained by the neutral-mode mismatch.
6. Saved joy and reassurance request records contain distinct instructions. Their generated WAV hashes differ; both neutral outputs have identical hashes. Different hashes prove separate signals, not different emotional performance.
7. Source mapping follows the official control syntax. This audit has not independently captured the live sidecar kwargs for every historical request; saved native fields plus current installed mapping are the available evidence.
8. The user reports no meaningful audible distinction. No emotion result is qualified by ASR checks or file hashes.

## Next controlled experiment

Use reference-only controllable cloning for every arm, including neutral. Hold reference, sentence, seed, diffusion steps, guidance, normalization and playback processing fixed. Compare concise neutral, joyful, and reassuring directions. Record final model kwargs and mode explicitly. Check exact words, identity, and emotional contrast separately.

Repeat with a clean 5–10-second recording of the same approved character. Do not extend it merely by padding or repeating the same waveform. Qualify the longer reference as the same character before using it.

Include a clearly documented control instruction such as faster pace to test basic instruction-following separately from subtle emotion. Failure of one subtle distinction is not evidence that no control works. Do not add longer prompts or strength knobs as assumed fixes. Repeat a small fixed seed set only after mode and reference checks; follow official recommendations without treating them as a guarantee.

No new test was generated during this audit. The next experiment remains pending.

## Primary sources

- [Official Usage Guide](https://voxcpm.readthedocs.io/en/latest/usage_guide.html): reference versus prompt inputs, control syntax, Hi-Fi instruction limitation, defaults, reference duration.
- [Official cookbook](https://voxcpm.readthedocs.io/en/latest/cookbook.html): clean five-second-plus cloning references, concise controls, English and Chinese instructions.
- [Official model card](https://huggingface.co/openbmb/VoxCPM2): cloning examples and variability limitations.

## Local evidence

- `services/speaker-studio/voice_designer.py`: forwards `performance_direction` as `instruct`, reference and transcript.
- `services/voicestudio/upstream/backend/engines/voxcpm2_subprocess/main.py`, `generation_kwargs`: current mapping executed without loading weights.
- `services/voicestudio/upstream/backend/services/tts_backend.py`: in-process backend shares this mapping.
- `.planning/sketches/batch_queue.py`: saved paired requests, direction on second arm only.

### Saved experiment details

```json
[
  {
    "batch": "36136e22-aefa-4bef-ad8d-c4d562d498a5",
    "role": "neutral",
    "id": "0888a674-6a85-44ab-b136-1ad03b6b6cd4",
    "reference": "82a4a0db-dfd8-4389-8b9b-c6553ab5d92f",
    "mode": "Hi-Fi continuation",
    "duration_seconds": 3.84,
    "sha256": "36e0122aefa5a1344a206929899b0121fe219822bf8a0f3682ae76fc21aad899",
    "request": {
      "text": "You haven’t been forgotten, and I’m here to help you.",
      "description": "",
      "seed": 65,
      "steps": 10,
      "guidance": 2.0,
      "profile": {
        "id": "102fa787-8065-4a3c-b4b4-5e9af8a72002",
        "created": 1793451197.4404302,
        "name": "Santa emotion reference · 82a4a0db",
        "audition_id": "82a4a0db-dfd8-4389-8b9b-c6553ab5d92f",
        "engine": "VoxCPM2",
        "design_request": {
          "text": "Well now, I’ve been looking forward to meeting you.",
          "description": "Santa Claus has a voice that is older-sounding, rich and resonant in the baritone range, full-bodied, warm and rounded, with a restrained gravelly edge and a natural American accent. Strong chest resonance, clear conversational speech and dry humour, with a kindly, grounded presence and an easy, hearty laugh. Keep the sound solid and resonant rather than airy or heavily raspy.",
          "seed": 65,
          "steps": 10,
          "guidance": 2.0,
          "performance_direction": "",
          "mode": "voice_design"
        },
        "reference": {
          "path": "/Users/x/projects/swarms/services/speaker-studio/.runtime/voice-designer/auditions/82a4a0db-dfd8-4389-8b9b-c6553ab5d92f/voice.wav",
          "sha256": "b609b09561e6e2973d7fe54a357856e79f053550faa6e098e04ed82144e24ef0",
          "transcript": "Well now, I’ve been looking forward to meeting you."
        },
        "word_check": {
          "transcript": "Well now, I've been looking forward to meeting you.",
          "expected": "Well now, I’ve been looking forward to meeting you.",
          "exact_words": true,
          "method": "Offline Faster-Whisper tiny.en, fixed English, beam 5, no VAD or text prompt",
          "limitation": "ASR is fallible; exact words do not validate emotion or voice identity"
        },
        "selection": "Saved from this audition. No automatic emotion, apparent age or identity approval.",
        "scene_casting": "Not connected; this profile can be reused on the designer page."
      },
      "performance_direction": "",
      "mode": "profile_reuse"
    }
  },
  {
    "batch": "36136e22-aefa-4bef-ad8d-c4d562d498a5",
    "role": "Gentle and reassuring, speaking to someone who feels forgotten; warmth and care without sounding cheerful or excited.",
    "id": "3a0eb77e-5e1c-4e1f-acad-5c1bdb177ecc",
    "reference": "82a4a0db-dfd8-4389-8b9b-c6553ab5d92f",
    "mode": "controllable cloning",
    "duration_seconds": 3.52,
    "sha256": "25077185fef0ae9c8d1a6da4171c3c3ee52dad59bda2290a7c5161f67fe2f17a",
    "request": {
      "text": "You haven’t been forgotten, and I’m here to help you.",
      "description": "",
      "seed": 65,
      "steps": 10,
      "guidance": 2.0,
      "profile": {
        "id": "102fa787-8065-4a3c-b4b4-5e9af8a72002",
        "created": 1793451197.4404302,
        "name": "Santa emotion reference · 82a4a0db",
        "audition_id": "82a4a0db-dfd8-4389-8b9b-c6553ab5d92f",
        "engine": "VoxCPM2",
        "design_request": {
          "text": "Well now, I’ve been looking forward to meeting you.",
          "description": "Santa Claus has a voice that is older-sounding, rich and resonant in the baritone range, full-bodied, warm and rounded, with a restrained gravelly edge and a natural American accent. Strong chest resonance, clear conversational speech and dry humour, with a kindly, grounded presence and an easy, hearty laugh. Keep the sound solid and resonant rather than airy or heavily raspy.",
          "seed": 65,
          "steps": 10,
          "guidance": 2.0,
          "performance_direction": "",
          "mode": "voice_design"
        },
        "reference": {
          "path": "/Users/x/projects/swarms/services/speaker-studio/.runtime/voice-designer/auditions/82a4a0db-dfd8-4389-8b9b-c6553ab5d92f/voice.wav",
          "sha256": "b609b09561e6e2973d7fe54a357856e79f053550faa6e098e04ed82144e24ef0",
          "transcript": "Well now, I’ve been looking forward to meeting you."
        },
        "word_check": {
          "transcript": "Well now, I've been looking forward to meeting you.",
          "expected": "Well now, I’ve been looking forward to meeting you.",
          "exact_words": true,
          "method": "Offline Faster-Whisper tiny.en, fixed English, beam 5, no VAD or text prompt",
          "limitation": "ASR is fallible; exact words do not validate emotion or voice identity"
        },
        "selection": "Saved from this audition. No automatic emotion, apparent age or identity approval.",
        "scene_casting": "Not connected; this profile can be reused on the designer page."
      },
      "performance_direction": "Gentle and reassuring, speaking to someone who feels forgotten; warmth and care without sounding cheerful or excited.",
      "mode": "performance"
    }
  },
  {
    "batch": "21a18b3c-f7be-4969-a528-108ad3a49026",
    "role": "neutral",
    "id": "b4e00dd4-38d3-4b74-b5ae-eca2f7b973ac",
    "reference": "82a4a0db-dfd8-4389-8b9b-c6553ab5d92f",
    "mode": "Hi-Fi continuation",
    "duration_seconds": 3.84,
    "sha256": "36e0122aefa5a1344a206929899b0121fe219822bf8a0f3682ae76fc21aad899",
    "request": {
      "text": "You haven’t been forgotten, and I’m here to help you.",
      "description": "",
      "seed": 65,
      "steps": 10,
      "guidance": 2.0,
      "profile": {
        "id": "102fa787-8065-4a3c-b4b4-5e9af8a72002",
        "created": 1793451197.4404302,
        "name": "Santa emotion reference · 82a4a0db",
        "audition_id": "82a4a0db-dfd8-4389-8b9b-c6553ab5d92f",
        "engine": "VoxCPM2",
        "design_request": {
          "text": "Well now, I’ve been looking forward to meeting you.",
          "description": "Santa Claus has a voice that is older-sounding, rich and resonant in the baritone range, full-bodied, warm and rounded, with a restrained gravelly edge and a natural American accent. Strong chest resonance, clear conversational speech and dry humour, with a kindly, grounded presence and an easy, hearty laugh. Keep the sound solid and resonant rather than airy or heavily raspy.",
          "seed": 65,
          "steps": 10,
          "guidance": 2.0,
          "performance_direction": "",
          "mode": "voice_design"
        },
        "reference": {
          "path": "/Users/x/projects/swarms/services/speaker-studio/.runtime/voice-designer/auditions/82a4a0db-dfd8-4389-8b9b-c6553ab5d92f/voice.wav",
          "sha256": "b609b09561e6e2973d7fe54a357856e79f053550faa6e098e04ed82144e24ef0",
          "transcript": "Well now, I’ve been looking forward to meeting you."
        },
        "word_check": {
          "transcript": "Well now, I've been looking forward to meeting you.",
          "expected": "Well now, I’ve been looking forward to meeting you.",
          "exact_words": true,
          "method": "Offline Faster-Whisper tiny.en, fixed English, beam 5, no VAD or text prompt",
          "limitation": "ASR is fallible; exact words do not validate emotion or voice identity"
        },
        "selection": "Saved from this audition. No automatic emotion, apparent age or identity approval.",
        "scene_casting": "Not connected; this profile can be reused on the designer page."
      },
      "performance_direction": "",
      "mode": "profile_reuse"
    }
  },
  {
    "batch": "21a18b3c-f7be-4969-a528-108ad3a49026",
    "role": "Genuine delight and bright energy, with a natural smile in the voice.",
    "id": "efdd97bd-fcb0-411f-8551-73d4774431e5",
    "reference": "82a4a0db-dfd8-4389-8b9b-c6553ab5d92f",
    "mode": "controllable cloning",
    "duration_seconds": 3.52,
    "sha256": "27fca5b7327dbcd38cda614d47ff5920515d2effd57350f6394fe38000b581b5",
    "request": {
      "text": "You haven’t been forgotten, and I’m here to help you.",
      "description": "",
      "seed": 65,
      "steps": 10,
      "guidance": 2.0,
      "profile": {
        "id": "102fa787-8065-4a3c-b4b4-5e9af8a72002",
        "created": 1793451197.4404302,
        "name": "Santa emotion reference · 82a4a0db",
        "audition_id": "82a4a0db-dfd8-4389-8b9b-c6553ab5d92f",
        "engine": "VoxCPM2",
        "design_request": {
          "text": "Well now, I’ve been looking forward to meeting you.",
          "description": "Santa Claus has a voice that is older-sounding, rich and resonant in the baritone range, full-bodied, warm and rounded, with a restrained gravelly edge and a natural American accent. Strong chest resonance, clear conversational speech and dry humour, with a kindly, grounded presence and an easy, hearty laugh. Keep the sound solid and resonant rather than airy or heavily raspy.",
          "seed": 65,
          "steps": 10,
          "guidance": 2.0,
          "performance_direction": "",
          "mode": "voice_design"
        },
        "reference": {
          "path": "/Users/x/projects/swarms/services/speaker-studio/.runtime/voice-designer/auditions/82a4a0db-dfd8-4389-8b9b-c6553ab5d92f/voice.wav",
          "sha256": "b609b09561e6e2973d7fe54a357856e79f053550faa6e098e04ed82144e24ef0",
          "transcript": "Well now, I’ve been looking forward to meeting you."
        },
        "word_check": {
          "transcript": "Well now, I've been looking forward to meeting you.",
          "expected": "Well now, I’ve been looking forward to meeting you.",
          "exact_words": true,
          "method": "Offline Faster-Whisper tiny.en, fixed English, beam 5, no VAD or text prompt",
          "limitation": "ASR is fallible; exact words do not validate emotion or voice identity"
        },
        "selection": "Saved from this audition. No automatic emotion, apparent age or identity approval.",
        "scene_casting": "Not connected; this profile can be reused on the designer page."
      },
      "performance_direction": "Genuine delight and bright energy, with a natural smile in the voice.",
      "mode": "performance"
    }
  }
]
```
