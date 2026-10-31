# Paper 16 scene studio

Run `sh services/speaker-studio/run.sh` from the repository. Open http://127.0.0.1:5197/. Paper 16’s Compare recordings links here. Keep the existing local VoiceStudio service running for engines that use it.

## Scene comparison

Choose a scene, reference library and generator, inspect each role’s identity and performance recordings, then generate. Only one scene job runs at a time, with lines generated sequentially under the same lock as the notebook. Each run freezes the script, source references, hashes and native settings. Saved experiments are listed newest first.

The original six-line scene, **The last copy**, tests confrontation, regret, discovery and relief. **The empty seat** is a separate held-out script. Directions describe the desired acting; they are not advertised as model controls. ESD is the existing two-role baseline. CREMA-D and RAVDESS use two source actors. EMNS replaces role A only; role B remains ESD. Source speakers differ across datasets, so a library comparison also changes vocal identity. Source terms and annotations remain visible.

A full mix is created only when every line has a saved output. A failed line remains visible; a successful single-line adapter test is intentionally a partial scene. Speech recognition is a diagnostic: disagreement is retained for listening, and matching words never proves convincing acting. Complete mixes use mono 24 kHz PCM with 0.30-second gaps; the listening copy applies static level adjustment. There is no new emotion processing or cinematic sound design.

Regenerate a line to create a new experiment that inherits the other lines. Earlier outputs and their settings are retained. Expand source evidence to inspect the transcript and metadata; open the manifest to inspect exact bindings. The label-hidden comparison plays two complete scenes with the same script as A/B and reveals their labels only after a preference is submitted. Voices may still identify the condition. Scores remain empty until a listener supplies them.

Technical evidence is recorded in `knowledge/research/paper-16-study/scene-sequence-verification.json`. `verify_sequence.py` runs real sequential generations and resumes from that ledger. Unit tests exercise failure handling and contract rules separately from these native runs. No perceptual winner has been selected. TTS-Story, Draft to Take and Pedalboard are saved as deferred candidates and are excluded from this implementation.

## Preserved self-recording wizard

Open http://127.0.0.1:5197/record for the original wizard. Its profiles and takes remain intact.

A single HTML page guides the user through eight authored performance briefs. Each step supplies a script and direction, intended intensity, notes, browser recording or file import, saved playback and self-review. Every successful take gets a new immutable audio file. The manifest retains source bytes/hashes, a 24 kHz mono PCM derivative, script, direction, declared intensity, basic signal measurements and explicit review status. A portable ZIP includes original captures, WAVs, scripts and annotations. Files live under `.runtime/` (ignored by git); changing `SPEAKER_STUDIO_DATA` relocates them. There is no deletion operation.

Microphone access begins only on Record. Stop releases tracks and saves locally. Failed uploads retain a retry buffer while the tab stays open. A tab-close warning protects active capture/unsaved buffers. Two explicit listening checks are required before a take becomes the chosen reference for a step. Finished means self-reviewed, not independent emotion or transcript validation.

VoiceStudio integration: the per-take Save to VoiceStudio button sends a kept WAV and its script to the existing local profile API, creating one clone profile per performance. The returned profile ID is retained to avoid repeats. This path is implemented but not verified with real user audio yet. A local profile archive remains usable when VoiceStudio is offline. The four notebook generators do not yet consume these new self-recorded profiles automatically. Pitch/formant/age/gender transformations are not implemented by this recording wizard.

Verification: `services/research-notebook/.venv/bin/python services/speaker-studio/test_studio.py` uses an isolated temporary library and synthetic tone fixture; checks eight saved/kept steps, incomplete-finish rejection, media access, reopen/export, and cross-origin write rejection. Browser verification covered creating the real empty My voice profile, navigating briefs, and the Paper 16 link. No microphone permission was triggered and no actual microphone recording is claimed.

## Adjustable casting

The scene page has independent Robin and Casey voice-profile selectors. CREMA-D and RAVDESS each expose two source-listed male and two source-listed female actors, enabling mixed casts, two men or two women. Each selected actor supplies both identity and all emotional reference clips for that role; an emotion change does not recast the character. Listen to each identity preview before generating. Source sex metadata is distinct from perceived presentation, speaker similarity and listening approval.

Changing a profile starts a new scene draft. Generate complete scene freezes the cast and its exact source files in a new experiment. A line retake cannot change the cast; earlier scenes and comparison assessments remain untouched. Saved-run labels include the actual cast. Dia requires reference continuation when explicit casting is requested. ESD keeps only its two existing unclassified baseline profiles; EMNS keeps its explicit one-role swap and does not pretend to provide arbitrary casting.

`prepare_casting.py` imports the additional source clips while leaving role defaults unchanged. CREMA-D source sex comes from its VideoDemographics.csv; RAVDESS actor numbering is documented at https://zenodo.org/records/1188976 (odd male, even female). `test_casting.py` exercises the casting contract separately from native inference.

## Voice Designer

Open `/design` from the Scene Studio header. The page uses the already installed VoxCPM2 native free-form description mode through the local VoiceStudio API, bypassing the restricted OmniVoice description mapper. There is no reference audio on a new design request. Describe the voice, edit a short script, set native seed/steps/guidance, and generate an immutable audition. The form draft is saved locally in the browser; auditions and named profiles live in `.runtime/voice-designer` and survive reload.

A named profile pins the original generated WAV, hash and exact transcript. Try current script creates a separate reference-conditioned continuation recording from that pinned sample; it ignores edits to the description. This is a voice-design and audition workspace, not a recording editor, exact age/pitch control, character conversation system or completed scene-casting integration. A saved profile is a selection, not proof of identity retention or acting quality. Original WAV and profile metadata downloads are available.

All native requests, model provenance, decoded audio and word-check diagnostics are retained. One shared studio queue plus the notebook file lock prevents simultaneous generation. Unsupported or failed results remain visible and cannot be saved as profiles. Unit contracts are tested with `services/research-notebook/.venv/bin/python services/speaker-studio/test_voice_designer.py`; real execution evidence is separate in `knowledge/research/paper-16-study/voice-designer-verification.json`. The cited project review is `voice-designer-research.md` in the same study directory.

## Five-stage character voice workflow

The canonical `/design` page is now a persistent wizard, not five independent forms:

1. **Design & refine** uses reference-free VoxCPM2 auditions. Existing auditions can be selected without regeneration.
2. **Fix identity** pins that audition's original WAV, SHA-256, transcript and recipe. Once fixed, another voice requires a new character. A revision retains the pinned identity and starts a fresh performance bank.
3. **Develop performances** keeps this identity reference and adds a separate native delivery direction. Seven initial styles (neutral, reassurance, anger, sadness, happiness, excitement, curiosity) have immutable candidate versions. The global studio queue and notebook file lock serialize inference.
4. **Qualify** uses each selected performance as a continuation reference on two fixed, previously unused target sentences. A listener must explicitly judge words, identity retention and delivery for that exact candidate/check pair. ASR is diagnostic; a flagged check requires a written explanation before a listener can approve its words. Selecting another candidate invalidates the current qualification without deleting its history.
5. **Package & cast** exports drafts or publishes a self-contained, immutable character package after every required style passes listening checks. Packages contain identity/performance/check WAVs, hashes, transcripts, native recipes, model provenance and explicit assessments. Published packages appear in Scene Studio's **My character voices** library with a direct cast handoff. Qualification currently covers VoxCPM2 only; other engines reject that cast until separately qualified. A CREMA-D actor can supply the other role, retaining its source terms.

Projects and packages live under `.runtime/character-workflow`; earlier auditions and basic profiles remain under `.runtime/voice-designer`, accessible at `/design/auditions`. Current project and form drafts survive a browser refresh; the stage and handoffs are stored on the server. On service startup, interrupted queues retain completed recordings and become retryable. Imports have no recovery side effects. Polling uses ordinary HTML, not persistent Jupyter widgets.

`test_character_workflow.py` exercises stage gates, hash binding, stale reviews, failure continuation, restart recovery, draft exclusion, portable packaging, revision isolation and the actual scene casting contract using isolated fixtures. Simulated listener approvals exist only in temporary tests, never the real character library. Native recordings and browser proof are recorded separately in `character-workflow-verification.json`; an implemented publish mechanism does not mean the demonstration character has passed human qualification.

### Corrected performance development: acted reference transfer

The user heard no convincing anger in the first wizard's written-direction candidate or its held-out checks. This is saved against that exact candidate as negative listening feedback, not converted into invented words/identity judgements. Those recordings remain selectable as the earlier method.

Stage 3 now uses **IndexTTS 2.5** with two independent audio inputs: the pinned designed identity and an actual performed emotion guide from the existing source catalog. Emotion strength and duration scale are native controls; written acting notes are retained as the target but are not passed off as performed guidance. The neutral guide uses a separate internal key so it cannot overwrite the identity reference. Every take records both source hashes, transcripts, provenance, native request and generation settings. Stage 4 then uses **VoxCPM2 continuation** from that performed candidate on the held-out lines, testing whether the performance survives reuse. Neither the transfer nor the cross-engine reuse is automatically approved.

Reference previews identify their actual source emotion and terms. Neutral, anger, sadness and happiness have existing guide options. Reassurance, excitement and curiosity have no exact catalog match assigned; they require an explicitly selected guide and remain experiments, rather than silently relabelling another emotion. The built-in seven style slots are currently fixed; arbitrary new style creation is not implemented. Published packages and draft exports retain used emotion guides, source terms and performance-engine provenance. This corrects the original direction-only workflow description above.

The qualification page presents a numbered listening sequence: 1) the designed identity, 2) the acted emotion input, 3) the generated character performance, 4) its first new-sentence continuation, and 5) its second continuation. Each entry identifies input/output, expected words where applicable and the listening question connecting it to prior recordings. Review controls follow the sequence; generation is optional and collapsed. Legacy direction-only candidates explicitly show that recording 2 is absent, rather than fabricating a reference. These presentation changes leave every recording, candidate binding and saved assessment intact.

### One sentence per character take

New designer targets, reference-guided performance targets and qualification targets must each contain exactly one English sentence (5–500 characters). Stage 3 has an editable target with inline boundary feedback; the generation service independently rejects multiple sentences before acquiring the model queue. It never silently truncates or splits a submitted passage. Each valid take applies the fixed identity and emotion guide afresh. Qualification now generates two separate one-sentence checks. Earlier multi-sentence takes and their exact old test pairs remain inspectable, but cannot qualify under the new standard.

The boundary implementation is pinned `pysbd==0.3.4`, following the [official pySBD usage](https://github.com/nipunsadvilkar/pySBD). It handles common English abbreviations, initials and decimals. This is sentence-boundary detection, not a full grammar certificate; missing punctuation or unusual constructions can remain ambiguous. The dependency is recorded in this service's `requirements.txt`, installed into the existing Research Python runtime, and checked by `run.sh`. Restore with `uv pip install --python services/research-notebook/.venv/bin/python -r services/speaker-studio/requirements.txt`.

The user's finding is saved against the previous IndexTTS candidate: the anger source was convincing, the first generated sentence had the intended tone, and the remaining sentences lost it. This supports a per-sentence hypothesis; it does not automatically approve the rebuilt voice. `test_sentence_policy.py` covers boundary cases, rejection before queueing and preservation of legacy evidence.


### Guided qualification (Paper 16)

The default Qualify tab now presents one comparison: an actor control and the selected character saying the same sentence. **Prepare comparison** generates the diagnostic actor control without replacing the character take; **Listen to both** replays saved files sequentially. **Keep** explicitly confirms words, character identity and emotion, then requires two held-out, one-sentence VoxCPM2 checks before listener qualification. ASR never qualifies acting.

**Improve** records the exact candidate/control/trial IDs and offers one explained experiment under `guided-qualify-v1`. Rules are deterministic for saved state: a supported native emotion vector, an alternate acted guide, a modest strength reduction for identity drift, or a bounded seed retry for wording/naturalness. The native vector replaces emotion-audio conditioning; it does not supplement it. The actor control remains audio-guided. Uncertainty means replay; exhausted or unsupported adjustments stop honestly. If emotion disappears in the new-word continuation, the profile stays unqualified and the user returns to performance development; direct generation with another engine is not silently treated as qualified casting.

Each attempt, error and reason remains in history; stale decisions are rejected. Failed controls can be prepared again, missing validation checks can be resumed, and failed improvement attempts require fresh feedback rather than automatically repeating. Draft export includes diagnostic controls. The earlier five-recording breakdown remains under Details. No real listener approval was fabricated during implementation tests.
