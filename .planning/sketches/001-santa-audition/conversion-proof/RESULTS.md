# Actor-to-Santa conversion: first offline test

The offline conversion ran successfully on Apple Silicon using Seed-VC source revision `51383efd921027683c89e5348211d93ff12ac2a8`. This is speech-to-speech conversion, not transcription followed by TTS. The actor recording supplies the performance and words; selected Santa Take 25 supplies target identity.

## Verified

- Pinned model preparation is separate from inference; assets are size checked and large weights SHA-256 checked. Existing identical BigVGAN weights were reused.
- Inference ran with HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1. A live process socket inspection found no network sockets.
- Conversion used MPS, seed 65, 30 diffusion steps, CFG 0.7, length adjustment 1.0, no automatic pitch adjustment, float32.
- Offline ASR recovered exactly: “Maybe tomorrow it will be cold.”
- Converted audio is finite, non-silent, and has no samples at or above 0.999 full scale.
- Actor duration: 3.7704 s; converted: 3.7616 s. RMS-envelope correlation: 0.888. These support timing retention, not emotion correctness.
- Listening copies use the existing common loudness target. Originals remain intact.

## Not established

The anger and Santa identity require a listener comparison. This test has not established reliable emotional control on new words. At the time of the isolated test, Stage 3 still used VoxCPM2 written direction. It has since been explicitly connected to the conversion workflow described below. No reassurance reference was substituted with a different emotion.

## Separate service recovery

VoiceStudio port 5196 was not running, which caused the screenshot failure. The scoped launcher restored it. An actual retry saved recording d6dfb3c2-a420-4331-a70a-0612b9a7dfca (3.36 s), passed exact-word ASR, and returned playable WAV bytes over the existing media endpoint. The neutral was reused, not regenerated. Existing queue, reference-binding and 35-word-limit tests passed.

## Sources

- https://github.com/Plachtaa/seed-vc
- CREMA-D reference provenance and audio-only ratings: see inputs.json
- Actual file hashes and acoustic measurements: verification.json

## App integration after listener feedback

The user confirmed the isolated converted recording sounded angry. The existing app button is now connected to an IndexTTS actor-performance stage followed by Seed-VC timbre conversion. Anger and Joy were both generated through the actual UI button with the existing sentence; each stage passed word checks, and the existing neutral was reused. Inputs, outputs and hashes are captured in `../acted-integration-results.json`. Emotion and Santa identity on these new sentences still require listening. Warm reassurance is disabled until its own acting reference exists. Earlier written-direction comparisons remain saved with explicit labels.
