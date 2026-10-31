# Money audio controls: integration audit

The comparison source is Money's `runtimes/f5-tts/generate.py` interface and its three engine configuration files. Engines remain reused in place; configuration overrides are written into each isolated run, not Money's files.

| Original capability / setting | Workbench control |
|---|---|
| Narration, sampling steps, speed, seed | Narration / Voice inspectors; all integer steps 8–64 |
| Active English ESD references | Voice selector, active variant entries |
| Preserved original ESD references | Voice selector, original entries |
| Speaker and emotion selection | Each entry explicitly names both; 50 choices per variant |
| Reference playback and exact transcript | Voice inspector |
| Custom reference upload | Voice inspector, 1–30 seconds, exact transcript required |
| Crossfade, guidance and sway | Voice advanced controls |
| Save settings | Download/load graph JSON and session workbench defaults; Money defaults untouched |
| Generate speech independently | Generate speech only |
| Uploaded recording for mastering | Process an existing recording, validated upload and source selector |
| Use generated recording | Latest generated speech source |
| Gentle / Balanced / Present | Master profile selector; selecting profile clears its DSP overrides |
| High-pass, low-mid and presence EQ | Master advanced controls |
| Compression ratio, threshold, attack, release | Master advanced controls |
| De-essing intensity | Master advanced controls |
| Sample rate, target loudness, peak ceiling, loudness range | Master advanced controls |
| Master without speech generation | Master recording only |
| Matched versus actual-volume playback | Listening checkbox, originals and processed files |
| Original, processed, matched sequence and download | Result players and WAV downloads |
| Enhancement evaluations and denoise | Enhancement inspector |
| Solver, temperature, seed, CPU threads, maximum duration | Enhancement advanced controls |
| Enhance an existing master without regeneration | Enhance master only / Enhance latest master |
| Reports and inference measurements | Expandable per-stage evidence |
| Stop active processing | Stop run |

## Installed-engine boundaries

The installed generation checkpoint is pinned F5TTS_v1_Base on MPS. Enhancement is pinned Resemble Enhance on CPU. Changing to an uninstalled model or unsupported device is not represented as a working option. Master output remains mono; enhancement outputs its native 44.1 kHz. No new assets are downloaded implicitly.

Uploads remain local and session-scoped, up to 20 MB. Reference uploads must be at most 30 seconds; mastering accepts up to 10 minutes, while optional enhancement is capped at 120 seconds (or a smaller configured maximum). A long master can therefore succeed while enhancement stops with an explicit duration error. Files that the installed decoder cannot read are rejected.

Session defaults survive page reload while the server stays running. Graph JSON is the portable settings export; an uploaded-reference token refers to this server session and requires re-upload after session loss. Original Money defaults and reference catalogs are unchanged. The workbench does not provide a model installer, custom training, or commercial licensing clearance.
