# Shared recording analysis

React component: frontend/src/audio-analysis/AudioAnalysis.jsx, using @wavesurfer/react and wavesurfer.js. Rebuild with `node frontend/src/audio-analysis/build.mjs` from the repository root. Native notebook integration: audio_analysis.py, used by comparison_controls.py and controls.py (including reference previews and newly generated recordings). The compiled local component is served by the existing frontend; no CDN or external audio transfer.

Each iframe carries precisely the selected playback WAV bytes in its URL fragment. Fragment data is not sent to the HTTP server. No inference or file rewriting occurs during analysis. Version selection replaces the source and recalculates measurements. Raw downloads remain separate from gain-matched playback copies.

Waveform amplitude is fixed at full scale, with normalisation disabled. Time uses 40 px/s, with horizontal scrolling for longer clips. The component shows duration, native-sample RMS dBFS and sample peak dBFS, sample count at or above 0.999 full scale, and a 20 ms RMS envelope on a fixed -60 to 0 dBFS scale. Quiet frames use -40 dBFS; this is not voice activity detection. No LUFS, true-peak, emotion, identity or intelligibility inference is claimed.

Verified: known sine RMS/peak, silence and full-scale sample counts; five version-state/failure-recovery tests pass; browser playback advances; selecting IndexTTS original versus Version 2 changes measured duration from 2.75 to 3.30 s. Screenshot: review/waveform-analysis.png. Existing recordings are not regenerated.

Library documentation: https://github.com/katspaugh/wavesurfer.js and https://github.com/katspaugh/wavesurfer-react .

## Reference/output comparison standard

Every model card now includes generated audio and its recorded source reference simultaneously, each with an independent player and the same analysis component. Generated audio is blue; source references are amber, with explicit text labels. The pair wraps on narrow model columns and appears side by side where space permits. Both update to the selected saved version; pending editor changes do not substitute another reference. IndexTTS exposes both the neutral identity reference and the emotion reference. No-reference takes state that none was used. References resolve from saved run manifests, with source hash checks, rather than inferred UI defaults. The top reference controller displays the selected source without requiring the Listen button.
