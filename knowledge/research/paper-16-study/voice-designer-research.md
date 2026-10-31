# Voice designer foundation — primary-source review

Checked 31 October 2026. Scope: design and save reusable synthetic voices for the local Scene Studio. Conversation, character personality and scene production are separate work. No implementation or model installation was performed in this review.

## Recommendation

Start with **OpenBMB/VoxCPM2 through the existing local adapter**, using its native free-form voice-design input. First prove one new voice can be auditioned, saved as an immutable reference sample, and reused on unseen text. Add a **Voice Designer** page only around controls that reach that engine. Treat **Qwen3-TTS VoiceDesign** as the next comparison candidate. Keep **OmniVoice** a research-only comparison rather than the commercial default because its pretrained weights have non-commercial terms.

This ordering is an integration recommendation, not an audio-quality ranking. In this workspace VoxCPM2 is installed and reference-conditioned generation has been tested; its reference-free design mode has not yet been qualified. The other design paths are not demonstrated by the existing scene tests.

## Candidate comparison

| Project | Actual design interface | Mac route and present qualification | Reuse and limits |
|---|---|---|---|
| [OpenBMB/VoxCPM](https://github.com/OpenBMB/VoxCPM#-voice-design), VoxCPM2 | Natural-language description at the beginning of synthesis text; no reference required. Reference cloning and reference-plus-style guidance are distinct modes. | Official demo supports `mps`; automatic device selection uses MPS on Apple Silicon. Existing local model/adapter is the smallest next test. | Keep the approved generated WAV and exact transcript as the identity reference for later cloning. The reference does not guarantee exact speaker retention. |
| [QwenLM/Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS#voice-design) | VoiceDesign model takes target text, language and a natural-language instruction. The Base model performs cloning; CustomVoice is another variant, not interchangeable with VoiceDesign. | Main official examples use CUDA and FlashAttention. Existing VoiceStudio source mentions an MLX conversion, but this is not proof of a working local VoiceDesign installation. Qualify the chosen Mac implementation separately. | Official [design-then-clone example](https://github.com/QwenLM/Qwen3-TTS#voice-design-then-clone) generates an identity sample, builds a reusable clone prompt and generates additional lines. That is a useful pattern for our profile lifecycle. |
| [k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice) | Structured speaker attributes, not unrestricted descriptive prose. | Official README gives an Apple Silicon `mps` route. No new design inference was performed here. | Its limited attribute vocabulary is convenient for truthful categorical controls, but is not a general voice-editing system. |

## Controls must be engine-specific

VoxCPM2's official examples expose a fixed seed, guidance and inference steps. Preserve those plus the exact description and model version, but do not promise bit-identical results across devices or software versions. Its documented design and cloning modes provide a plausible audition → save reference → reuse loop. They are not a numeric age, pitch or timbre editor. [Official usage](https://github.com/OpenBMB/VoxCPM#-voice-design), [Apple Silicon device support](https://github.com/OpenBMB/VoxCPM#web-demo).

OmniVoice accepts one token per category: gender, age band, pitch band, style, English accent and Chinese dialect. Its documented style option is whisper; its pitch values are qualitative bands. The documentation warns that some combinations can be ignored. It does not establish arbitrary raspiness, precise frequency or exact age control. [Official voice-design specification](https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md).

The checked-in VoiceStudio mapper at `/Users/x/projects/swarms/services/voicestudio/upstream/backend/core/describe_voice.py` projects prose into those six OmniVoice categories and explicitly reports unsupported words such as raspy as unmatched. **Do not pass a VoxCPM2 free-form description through that mapper or its tag sanitizer.** The VoxCPM2 adapter in `/Users/x/projects/swarms/services/voicestudio/upstream/backend/services/tts_backend.py` separately declares free-form voice-design support. Local code capability is not runtime proof that design follows every requested trait.

VoiceStudio's profile router already has a design-profile lifecycle that materializes and stores a reference sample. This can inform our storage interface, but its category-based path must not silently narrow a free-form Vox design request. Its optional RVC module is disabled unless configured with a conversion model and dependency; finding that file does not prove voice conversion works on this Mac.

## Licence boundary

- VoxCPM repository and the official [VoxCPM2 model card](https://huggingface.co/openbmb/VoxCPM2) identify Apache 2.0.
- Qwen repository and the official [VoiceDesign model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign) identify Apache 2.0.
- OmniVoice repository code is Apache 2.0, but its official [model-card licence section](https://huggingface.co/k2-fsa/OmniVoice#license) states the pretrained model is CC-BY-NC. Code and weights must not be conflated.

These labels are not blanket clearance for every reference recording, persona, likeness or output use. Keep a designed profile's provenance separate from dataset-derived references.

## Proposed acceptance test before the page is called usable

1. Use the installed Vox engine without any reference recording to audition two deliberately contrasting original voice descriptions, keeping script and generation settings fixed.
2. Save requests, exact model/revision, seed/settings, WAVs, hashes and transcripts. Record the native input actually applied; expose unsupported controls instead of silently ignoring them.
3. Check the words and playback, then ask the user whether the requested contrast is audible. Signal checks do not establish apparent age or vocal identity.
4. Freeze one selected sample as a new profile. Generate at least two unseen sentences from that saved sample and judge identity consistency and delivery separately.
5. Only then add the lightweight designer page with describe, audition, compare, name and save actions. Preserve every audition; changing a description makes a new candidate rather than modifying an approved identity in place.

Editing an existing voice's identity while preserving its performance would require a separately qualified conversion/transformation workflow. It must not be presented as already solved by text-based voice design.
