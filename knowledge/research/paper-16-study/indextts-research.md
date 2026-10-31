# IndexTTS native speaker / emotion comparison

Verified 2026-10-30 from the official IndexTeam Hugging Face models and index-tts repository. This is source research only; no model, environment, or inference was installed or run.

## Recommendation and immutable pins

For Paper16's native two-reference comparison, use **IndexTTS-2.5**, official code tag **v2.5.0**, commit **39207d91c30899cad1e7c1b9eb678c241f678e55**, and official weights **IndexTeam/IndexTTS-2.5**, revision **c39ce5ba981572cb187443877ff559dfb246ce63**. Preserve a lockfile and separately record every auxiliary model revision: pinning the primary weights does not pin first-run auxiliary downloads. The older IndexTTS-2 model can be pinned to **740dcaff396282ffb241903d150ac011cd4b1ede** if a v2-specific baseline is required. Pin model and code independently; package metadata still says version 2.0.0 at the v2.5.0 tag.

Sources: [release tag API](https://api.github.com/repos/index-tts/index-tts/git/ref/tags/v2.5.0), [v2 model API](https://huggingface.co/api/models/IndexTeam/IndexTTS-2), [v2.5 model API](https://huggingface.co/api/models/IndexTeam/IndexTTS-2.5), [pinned package metadata](https://github.com/index-tts/index-tts/blob/39207d91c30899cad1e7c1b9eb678c241f678e55/pyproject.toml).

## Native API and actual separation

Both versions expose **separate native inputs**: `spk_audio_prompt` for speaker identity and `emo_audio_prompt` for emotional reference, with `emo_alpha` controlling emotional-reference strength. This is a native conditioning path, not postprocessing or a derived pitch/energy heuristic. Source support proves API availability, not successful perceptual disentanglement on a given clip.

| Detail | IndexTTS-2 | IndexTTS-2.5 |
|---|---|---|
| Import | `from indextts.infer_v2 import IndexTTS2` | `from indextts.infer_v2_5 import IndexTTS2` |
| Language argument | no explicit `lang` parameter | required `lang`, e.g. `EN` |
| Precision flag | `use_fp16` | `use_bf16` |
| Text emotion initialization | `use_qwen_emo=True` by default at pinned release | `use_qwen_emo=False` by default |
| Speed | no `duration_factor` in explicit infer signature | `duration_factor`, documented 0.5–2.0; >1 slows speech |

Sources: [pinned v2 implementation](https://github.com/index-tts/index-tts/blob/39207d91c30899cad1e7c1b9eb678c241f678e55/indextts/infer_v2.py), [pinned v2.5 implementation](https://github.com/index-tts/index-tts/blob/39207d91c30899cad1e7c1b9eb678c241f678e55/indextts/infer_v2_5.py), [official usage](https://github.com/index-tts/index-tts/blob/39207d91c30899cad1e7c1b9eb678c241f678e55/README.md).

Recommended Mac initialization / request contract (not runtime-tested):

```python
from indextts.infer_v2_5 import IndexTTS2

tts = IndexTTS2(
    cfg_path=str(model_dir / "config.yaml"), model_dir=str(model_dir),
    device="mps", use_bf16=False, use_cuda_kernel=False,
    use_deepspeed=False, use_accel=False, use_torch_compile=False,
    use_qwen_emo=False,
)
tts.infer(
    spk_audio_prompt=str(speaker_wav), emo_audio_prompt=str(emotion_wav),
    emo_alpha=0.8, text=script, lang="EN", output_path=str(output_wav),
    use_random=False,
)
```

For an isolated baseline use the **same speaker clip** with `emo_audio_prompt` omitted. Run the controlled condition with the chosen emotion reference. Use one emotion source at a time: passing a vector or text-emotion mode clears the audio-emotion reference in source. Without external emotion audio, the speaker clip is reused as the emotion reference and alpha becomes 1.0. `use_random=False` only disables random selection of emotional prototypes; it does not establish fully deterministic waveform generation. Retain generation settings and RNG state as separate provenance.

The vector order is happy, angry, sad, afraid, disgusted, melancholic, surprised, calm. Text emotion needs the optional QwenEmotion initialization; v2.5 raises if requested without it. Speaker and emotion clips are loaded/cut to at most 15 seconds in v2.5. Caches identify references by path: replacing a clip in place can leave old conditioning cached; use content-addressed paths or reinitialize the engine.

Source: [pinned v2.5 inference and cache logic](https://github.com/index-tts/index-tts/blob/39207d91c30899cad1e7c1b9eb678c241f678e55/indextts/infer_v2_5.py).

## Mac / MPS and dependency boundaries

The official implementation explicitly selects MPS when available and disables reduced precision and custom CUDA kernels on its automatic MPS path. Explicit `device="mps"` bypasses that automatic precision choice, so explicitly set `use_bf16=False` (or `use_fp16=False` for v2). This is **source-level MPS accommodation**, not verified end-to-end compatibility or a throughput promise. The official v2.5 model card lists NVIDIA GPU requirements; report the tension rather than claiming official Mac runtime qualification. Keep CPU fallback as a visible change of device, never silently label it MPS success.

Source: [pinned device selection](https://github.com/index-tts/index-tts/blob/39207d91c30899cad1e7c1b9eb678c241f678e55/indextts/infer_v2_5.py), [official model card](https://huggingface.co/IndexTeam/IndexTTS-2.5/blob/c39ce5ba981572cb187443877ff559dfb246ce63/README.md).

Python range is **>=3.10,<3.12**. Major pinned dependencies include torch/torchaudio 2.8.*, transformers 4.52.1, tokenizers 0.21.0, accelerate 1.8.1, NumPy 2.2.6, librosa 0.10.2.post1 and descript-audiotools 0.7.2. Mac uses `wetext`, Linux `WeTextProcessing`; PyTorch's CUDA index is selected only on Linux/Windows. Use the base dependency set on Mac, **not `--all-extras`**: extras include DeepSpeed, FlashAttention and NVIDIA CUDA libraries. Gradio web UI is optional; Paper16 does not need it. `ffmpeg-python` is only a Python dependency and does not prove a system FFmpeg executable exists.

First inference can fetch w2v-bert-2.0, MaskGCT semantic codec, CAMPPlus and BigVGAN into `checkpoints/hf_cache`; primary model download alone is not offline readiness. Place all code environments, primary weights and caches inside the isolated runtime boundary. The official v2.5 HF repository is roughly 5.49 GB, before auxiliary models and runtime packages.

Sources: [pinned dependency declarations](https://github.com/index-tts/index-tts/blob/39207d91c30899cad1e7c1b9eb678c241f678e55/pyproject.toml), [model files](https://huggingface.co/IndexTeam/IndexTTS-2.5/tree/c39ce5ba981572cb187443877ff559dfb246ce63), [official model card](https://huggingface.co/IndexTeam/IndexTTS-2.5/blob/c39ce5ba981572cb187443877ff559dfb246ce63/README.md).

## License facts to preserve

This is the custom **bilibili Model Use License Agreement**, not an Apache/MIT assumption. The pinned license covers published model weights and final code. It requires a separate written license above either 100 million monthly active users or RMB 1 billion prior-year annual revenue for the user or affiliates; retain notices and the agreement in copies. Section 3.4(c) restricts using the model or derivatives to improve other AI models except IndexTTS derivatives or noncommercial AI models. Distributed derivatives require the stated nonendorsement notice. Third-party data/weights retain their own authorization requirements. The license says its Chinese version prevails. These are direct document observations, not a legal conclusion about a deployment.

Source: [pinned full license](https://github.com/index-tts/index-tts/blob/39207d91c30899cad1e7c1b9eb678c241f678e55/LICENSE).

## Acceptance evidence still required

A successful import, MPS selection, or model load is insufficient. Record actual output WAV, device, elapsed synthesis time, decoded waveform duration, code/weight revisions, reference hashes and full conditioning settings. Listen to speaker-only and separate-emotion outputs against the same script. Report speaker retention and transferred affect independently; do not infer either from API names or a completed progress indicator. No such runtime or listening proof was collected for this research note.
