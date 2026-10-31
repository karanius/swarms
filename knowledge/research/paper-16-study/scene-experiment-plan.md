# Scene comparison protocol — approved sequence

## Objective and scope

Compare reusable performance references through real local speech generation, using one original two-person scene. Preserve the existing recorder and Paper 16 take library. TTS-Story, Draft to Take and Spotify Pedalboard are deferred, not adopted or imported.

The implementation lives in `services/speaker-studio`. The main page is the scene workspace; `/record` preserves the recording wizard. The loopback service runs on port 5197. Paper 16's comparison section links to it.

## Frozen scripts

“The last copy” has six lines: tension, disappointment, focused discovery, then shared relief. “The empty seat” is a held-out four-line scene. Both have fixed text, role IDs and target directions. Run records store the full script snapshot; new runs also store a script hash. Retakes preserve the parent script and source references. Directions are evaluation targets, not automatically supported model inputs.

## Reference sets

- ESD: speakers 0012 and 0015, existing enhanced references. Research-only source, source emotion labels unverified. This is the engineering baseline.
- CREMA-D: actors 1006 and 1058, selected by the documented metadata policy. Audio-only ratings, intended labels and conditional intensity remain separate. These clips are candidates, not listener-approved winners.
- RAVDESS: actors 01 and 02, statement 01, repetition 01, normal neutral and strong target emotions. Source identifiers and CC BY-NC-SA attribution retained. Selective archive retrieval checked ZIP member CRCs and saved audio hashes; no whole-archive checksum claim.
- EMNS: source speaker 3 replaces role A; role B is the exact ESD 0015 baseline. The import uses complete rows with sufficient text and 5–12 second converted clips. Original rows, source audio hashes, descriptions and numeric levels are retained. The source level is not converted to a model strength value. This is a separate one-role comparison.

Every required scene role/emotion must resolve to a verified file. Missing coverage rejects generation; there is no silent neutral substitution. Different source actors and ESD enhancement versus raw sources are confounds. Results compare usable reference packages, not a clean causal estimate of dataset labels alone.

## Native generation and persistence

IndexTTS gets separate identity/performance inputs. VoxCPM2 and F5 receive the selected performance; F5 uses the existing custom-upload path. Dia uses its corrected local reference-continuation worker. Exact canonical IDs, paths, hashes, transcripts, native settings and source results are saved per line. Source intensity is not assumed to match synthesis guidance/strength. Different actor profiles are not treated as the same voice identity across datasets.

One scene queue runs at a time. A shared filesystem lock coordinates with notebook inference. Retakes append a new experiment, retain earlier versions, inherit unchanged line audio and regenerate only requested lines. A failure preserves the other lines and cannot masquerade as a complete new mix.

The raw scene resamples lines to mono 24 kHz and adds 0.30-second gaps. A separate listening copy applies one static gain using the existing loudness/peak measurements. No compressor, emotional EQ or invented acting is used to improve benchmark scores. Raw line outputs and the unmastered mix remain available.

## Checks and interpretation

Structural checks validate reference hashes, role mapping, allowed controls, frozen scripts and requested line IDs. Audio checks verify actual decoded files and complete-scene construction. Local ASR reports exact-word diagnostics for generated lines. Recogniser errors and contraction differences stay visible; ASR is not proof of emotion, identity or exact acoustic performance.

Listener scores remain empty until someone listens: wording, identity/role consistency, emotional performance, naturalness and editability. The label-hidden comparison randomises A/B and records preference before revealing condition labels; audible voice differences may identify conditions. It is not a guarantee of fully blinded listening. Normal labelled assessments are explicitly marked unblinded.

## Execution sequence

1. Renovated scene workspace with reference and output playback; recording wizard preserved.
2. ESD/IndexTTS complete scene, source validation and playback check.
3. CREMA-D, RAVDESS, EMNS complete scenes with the same IndexTTS settings, one at a time.
4. Complete ESD scenes through VoxCPM2, F5 and Dia to check integration, not to assume transfer quality.
5. Held-out ESD/IndexTTS scene.
6. One-line custom-reference checks for the remaining library/model combinations. These do not claim complete scenes.
7. Listener comparison and qualification. No automatic emotional winner. Failed or weak cases remain inspectable.

The runtime ledger is `scene-sequence-verification.json`; saved experiments and mixes live in the studio's ignored `.runtime/scenes` directory. Dataset audio lives under the external local Swarms runtime. Tests use temporary libraries/stubbed synthesis and are reported separately from real model runs.
