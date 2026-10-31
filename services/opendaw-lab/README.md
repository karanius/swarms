# openDAW voice-engineering qualification

Separate local proof for Paper 16's voice studio. Uses the published openDAW SDK and actual WASM engine, not substitute Web Audio EQ nodes.

Run `npm ci`, then `npm run dev` in this directory. Open http://127.0.0.1:5201/. Requires the existing voice bridge at port 5198 to serve the fixed Doctor Doom test recording. It does not start, stop or modify that service.

The page imports the original WAV into an in-memory openDAW Project, creates Tape playback and a Revamp EQ device, and applies control changes as box-graph transactions. It uses a copied project for offline rendering, leaving live playback and its telemetry connection separate. The exported file is a 48 kHz stereo float WAV.

## Proven

- Real engine boot in a cross-origin-isolated browser.
- Original Doctor Doom recording decoded: 115,200 frames / 2.4 seconds.
- Frequency/gain/Q controls change the Revamp device; bypass toggles it.
- Gain change reached the project while the engine reported playing; nonzero spectrum output observed.
- Actual offline export decoded again successfully: 115,200 frames, stereo, 48 kHz.
- A -12 dB bell at 1,200 Hz, Q 1 produced a nonzero RMS difference from bypass (see evidence/qualification.json).
- Repeated offline rendering at the same settings produced identical float samples in this test.

Evidence: `evidence/doctor-doom-eq.wav` and `evidence/qualification.json`.

## Boundaries

This is an isolated engineering proof, not integration into the character UI or a finished workstation. No preset or emotion generation was added. No microphone permission is required. The test recording is fixed in vite.config.js; generic asset selection, saved processing recipes/passports, library handoffs, broader effects and production packaging remain future work. Human listening must judge whether processing sounds desirable.

The sample loader is an in-memory SDK adapter; the project, Revamp device, parameter synchronization, realtime playback and offline renderer are openDAW implementations. The upstream loader callback must be delivered asynchronously to match engine subscription teardown semantics. Start the DOM animation dispatcher to receive transport telemetry. Export must use a project copy because a live project's telemetry receiver cannot be connected to two engines.

SDK pinned in package-lock.json; upstream source inspected at commit 1cf03564714398ada11e82585e2aa2e4091fd504. License: openDAW packages AGPL-3.0-or-later; preserve upstream licenses. No distribution or public deployment is performed by this test.

## Live vocal shaping

The saved-voice editor now adds independent pitch and formant sliders using the official MIT-licensed `signalsmith-stretch@1.3.2` WASM/AudioWorklet package. The path is openDAW Tape + Revamp -> Signalsmith live processor -> comparison gain -> output. Original A uses the original buffer with a matching processor-latency delay; Edited B uses the processing chain. A/B changes crossfade over a short gain ramp.

Export renders a frozen openDAW project copy, then the matching pitch/formant settings through Signalsmith in an OfflineAudioContext. Whole-recording RMS comparison measurements attenuate the louder path, with a shared -1 dBFS sample-peak ceiling. They do not alter exported processing levels. A/B buttons wait for current measurements. Source content is never overwritten.

`evidence/shaping-qualification.json` records final checks. Source waveform remains the original; spectrum, spectrogram and meter show the selected audible monitoring path. Changing controls may need a brief transition because pitch/formant processing has about 120 ms latency in the tested configuration. Larger shifts can introduce audible artifacts.

