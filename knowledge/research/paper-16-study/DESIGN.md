---
name: Paper 16 voice performance controls
description: Native Jupyter controls for auditioning cataloged emotion references and generated speech.
---

## Overview

The shipped extension is an operating surface inside the existing Paper 16 research notebook. It uses native Jupyter output and ipywidgets; it introduces no custom brand, theme, or replacement interface. Its purpose is to help the researcher choose the next emotion to investigate by making reference availability and research evidence visible beside generation controls.

Implementation: `controls.py`. Host notebook: `../notebooks/Paper 16 - Expanding the Voice Performance Library.ipynb`. The activation cell must run after opening or restarting the notebook, with a live Research Python kernel. Saved notebook output alone does not activate the buttons.

## Colors

Colors inherit the notebook and widget theme. Generate audio uses the native primary button treatment. No project-specific color tokens are defined or asserted here.

## Typography

Typography inherits Jupyter and ipywidgets. A native HTML heading introduces the panel; short explanatory paragraphs, field labels, table headings, status text, and output labels provide hierarchy. Strong emphasis identifies validation, failure, and completion messages.

## Layout

The panel is a full-width vertical widget stack capped at 800 px. Its order is introduction, speaker selector, reference inventory, emotion selector, script, collapsed generation settings, actions, status, and output. The script field is 100 px high. Speaker, emotion, and script labels reserve 90 px; their inputs occupy the available width.

The inventory lists neutral, anger, happiness, sadness, and surprise for the selected speaker in Emotion / Reference / Evidence columns. The actions share a wrapping row with an 8 px gap. The inventory and form stay together in the notebook flow; there is no separate navigation or dashboard.

## Components

- **Reference inventory:** Checks whether each reference file exists. Speaker 0012 neutral and anger identify their use in the user-approved Paper 15 comparison; other entries state that they have not yet been evaluated for that speaker in Paper 16. A separate note lists warm reassurance, curiosity, skepticism, disappointment, and restrained frustration as not yet cataloged. Availability is not an emotional-fidelity guarantee.
- **Selection and script:** Native dropdowns choose speaker and emotion. A multiline script starts with an editable example. Empty scripts and scripts over 500 characters receive corrective status messages before generation.
- **Generation settings:** A collapsed accordion contains seed (default 7, range 0–2147483647) and steps (default 10, range 1–64).
- **Reference preview:** Listen to reference requests automatic playback of the selected source recording and displays a player with an explicit input-recording label. It replaces stale generation status with a reference-specific message and a visible Play fallback if browser autoplay is blocked. It replaces only the reference output; the separate generated player and saved takes remain intact.
- **Generate audio:** Verifies the reference file and its recorded SHA-256 before calling the local VoxCPM2 generation path with reference audio and transcript, seed, and steps. It uses audio continuation without a written emotion instruction. During generation, the selection, script, settings, and both action buttons are disabled and a loading message is shown.
- **Result and recovery:** Successful output displays an embedded audio player, duration, and Download WAV link. Each generated WAV is also copied into `../notebooks/paper-16-audio` and downloaded through a same-origin `/research-jupyter/files/paper-16-audio/` URL. Each take uses a unique name and saves selection metadata beside the generation artifacts. Output remains experimental and requires listening for delivery and exact words. Failure preserves the script, displays a bounded error detail, and advises checking the local VoiceStudio backend before retrying. Controls are restored afterward; missing selected reference files disable both actions.

## Do's and Don'ts

- Preserve native notebook controls and theme inheritance.
- Keep source recordings and generated recordings explicitly labeled.
- Distinguish file availability, prior comparison evidence, and listener evaluation.
- Require live-kernel activation and real local generation for an interactive audition.
- Do not describe a selected emotion or a completed generation as proof of emotional fidelity.
- Do not add custom styling, branding, or a replacement application shell to this narrow extension.

Review disposition: ship, with no required fixes. Visual review artifacts: `review/inventory.png` and `review/controls.png`.


Reference and latest generated recording have separate, labeled players. Preview replaces only the reference player. Generation replaces the generated player only after successful creation; all takes remain saved. Re-running the control cell in the same kernel carries forward current settings and the latest recording without inference.


## Versioned model comparison workbench

The additional comparison cell uses comparison_controls.py with take_backends.py and take_media.py. It preserves the original reference controls above it. This is an Operate surface within desktop Jupyter; no new theme or standalone app is introduced.

Reading order: four-model asset/control inventory, explicit model-column checkboxes, collapsed new-take form, live status, then delivery rows with model columns. Each take repeats its model and requested delivery, so identity remains clear after scrolling. A comparison row requires identical text, requested speaker reference and delivery. No quality equivalence or speaker fidelity is implied. More than two columns may scroll horizontally in the notebook pane.

Each recording has an independent Version selector, labeled native audio player, applied settings and raw download. IndexTTS strength is visible; script/reference/seed and other model-specific controls are disclosed in a native accordion. Numeric text controls update continuously so pending edits reach the kernel before generation. Applied settings always refer to the currently playing saved version. Draft edits show a pending notice and persist separately from immutable take metadata.

Generate new version appends a unique recording with a parent/root relationship. The original remains selectable. Failure retains previous media and drafts; missing media affects only its player. Generation disables action and input widgets. New model columns offer an explicit Generate matching take action for empty cells. Unsupported control names are rejected by the adapters.

Model distinctions: IndexTTS has native emotion-reference strength and duration scaling; VoxCPM2 exposes steps/guidance/direction; F5 exposes native speed/steps/guidance/sway/crossfade; Dia exposes seed and optional reference continuation. Neither VoxCPM2 nor Dia receives a fake speed or emotion-strength slider. Eight-vector IndexTTS mixing is outside the implemented controls. No model promotion follows from a successful generation.

Verification: real per-take generations, version playback selection, per-model native requests and preserved raw hashes; isolated failure/draft/missing-file tests are reported separately from inference proof. Earlier papers and Money production defaults stay unchanged.

## Updated comparison layout after user review

The previous delivery-by-model column matrix is superseded. Selecting all models made each output/reference pair too narrow and hard to follow. Keep delivery/script grouping, then give each selected model its own full-width section. Within that section, generated speech and source reference appear side by side when width permits, wrapping only on narrow displays. IndexTTS shows both identity and emotion references; no-reference generations explicitly say none was used. Every source is resolved from the saved take, independently playable and hash-checked.

Use blue for AI output and amber for voice sample, but rely on explicit INPUT/OUTPUT headings, visible scripts and named Play buttons as the primary distinction. All players share the same waveform and metrics component. Starting any recording pauses other recordings through a local BroadcastChannel, avoiding overlapping voices. No generation occurs during playback, selection or analysis.

Verification: all four model sections each measured 1066 px wide in the current desktop notebook, with scrollWidth equal to clientWidth. Both custom Play buttons worked: starting the reference paused the generated take at 0.56 s while reference playback advanced. Existing five take-state/failure tests pass. Screenshot: review/full-width-model-layout.png.

## Reference role clarification
IndexTTS identity input is olive, emotion guidance is purple, and generated output is blue. Single-reference engines retain amber input and blue output. Labels and independent Play buttons state each role. Neutral IndexTTS explicitly notes when both input roles use the same recording. Verified live in notebook execution 14: identity and emotion players start, with the other player paused; five state regression checks pass. Recordings unchanged. Visual evidence: review/index-reference-roles.png.

## Shared sequential audition
All four models is the default creation selection, with shared speaker, emotion and script. Expand model reference previews to play actual inputs before generation. IndexTTS has separate neutral identity and chosen emotion; other engines use the selected performance reference. Generation runs IndexTTS, VoxCPM2, F5, Dia sequentially, preserving successful output when another fails. Queue status persists in last-queue.json. A real anger-reference queue saved four decodable outputs (3.00, 2.40, 2.20, 1.81 seconds); Dia passed automatic word recovery. Six state tests pass including failure continuation. The live widget temporarily showed Loading widget after the run; reexecuting its display cell restored controls and saved results without regeneration. Evidence: review/shared-audition-restored.png. Emotional quality remains unreviewed.


### Reload stabilization verification

The old kernel accumulated saved widget instances (1,298 models) and remained CPU-active without speech inference. Missing saved widget state also left controls at Loading widget. The main audition now loads compact current matches only; historical versions and advanced controls are instantiated on demand. Playback uses content-addressed local WAV URLs rather than embedding audio bytes in widget iframe fragments. Automatic widget-state saving is enabled, and the obsolete single-model output is replaced by a pointer to the shared workspace.

After restarting only Paper 16’s kernel and rendering its main display once, the saved state contains 215 widget models. A subsequent browser reload restored the controls without cell execution. The IndexTTS output played after reload (playback time advanced, no media error). The kernel then measured 0.0% CPU and approximately 58 MB RSS. Six state/queue regression tests passed. Existing recording files and per-record drafts were retained. This verifies the current reload, not an indefinite guarantee against all future widget failures. Screenshot: review/streamlined-reload-verified.png.


### Canonical reference library
See reference-library-audit.md and reference-library-audit.json. The shared manifest retains all 50 existing references; qualification focuses on speaker 0012. Thirteen library/control tests pass. Historical inputs resolve for 19 takes. Unknown performance annotations remain null and no reference is promoted. The notebook annotation-status panel was displayed, expanded and saved.
