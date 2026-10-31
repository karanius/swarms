# Unexpected dependency telemetry during setup

The user observed a LuLu connection alert for the new Python 3.11 VoiceStudio backend, process 95712, to `mobile.events.data.microsoft.com`. The process ID and executable matched our launched service. It was stopped; no firewall permission was granted by the agent.

The installed ONNX Runtime 1.29.0 libraries contain this endpoint and the `ORT_DISABLE_TELEMETRY` runtime switch. The app-level VoiceStudio analytics opt-out and Hugging Face telemetry opt-out did not cover this separate native dependency.

The launcher now sets `ORT_DISABLE_TELEMETRY=1` before Python initializes, following Microsoft's full process-lifetime opt-out. This is stronger than calling the Python telemetry-disable API after import, because an initialization event may already be emitted before that API call. No claim is made about the contents of any attempted transmission or whether any data was sent before the firewall alert.

Primary source: https://github.com/microsoft/onnxruntime/blob/main/docs/Privacy.md

Runtime validation and any further network findings must be recorded separately before claiming offline behavior. Model downloads require Hugging Face network access; synthesis after prepared assets should be assessed separately.

## First inference: additional AudioSeal dependency
The first Dia request completed synthesis in 11.333 seconds, then spent 49.770 seconds in an unsuccessful AudioSeal generator download via `torch.hub.load_state_dict_from_url`. Hugging Face offline flags do not govern that generic HTTPS loader. The application logged the failure and returned the original synthetic waveform (HTTP 200). This first audio must not be represented as invisibly watermarked.

The required generator was subsequently retrieved through explicit, bounded HTTPS at AudioSeal revision `3c19eba53390776cf2cc9ed5f6c9ac67ce72ecba`, verified against the upstream LFS SHA256, and placed in the dedicated runtime cache. `audioseal-prepared.json` records the file. The launcher now assigns `AUDIOSEAL_CACHE_DIR` to that isolated cache; this takes effect on the next backend restart. Existing installer work is allowed to finish before restart. No global cache or firewall rules were modified.
