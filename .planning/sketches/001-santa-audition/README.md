---
sketch: 001
name: santa-audition
question: Should Santa’s audition input and result sit side by side or follow top to bottom?
winner: null
tags: [voice-design, audition, layout]
---

# Santa audition sketch

Two visual variants using the existing charcoal/coral direction, Geist typography and Santa brief.
A keeps input and result side by side; B reads step by step. Switch layouts without losing the preview sentence. All result interactions explicitly simulate UI states only. No audio, network generation, persistence or approvals.

Open http://127.0.0.1:5198/001-santa-audition/

Check whether sentence → audition → decision feels clear. Existing studio and browser-local character drafts are untouched.

Revision: emotion and delivery are separate inputs. Emotion choices are proposed creative directions, not claims of engine support. Result labels record both chosen values.

Revision: two-stage identity then performance flow. The performance tab is locked until a placeholder candidate is selected. Reset returns to unselected identity. All choices remain temporary sketch state.

Revision: structured identity fields assemble a readonly live brief. Name, age, pitch, tone, texture, accent and optional extras are the source of truth; edits invalidate a previously selected mock identity. No generation or persistence.

## Live identity audition connection

User authorised connecting Part 1 and producing an audition. `live.js` now replaces the identity mock with the existing local VoxCPM2 designer API, a one-sentence script, immutable take records, native audio controls, original WAV download, and explicit user-selected profile saving. Browser fields and tracked take IDs persist on this origin. Performance remains a labelled visual preview; no performance inference has been connected.

Run from the repository root: `python3 .planning/sketches/serve.py`. This loopback-only server replaces the original static preview listener on 5198 and forwards only designer state/media/run/profile endpoints to 5197. It validates Host and POST Origin, limits bodies to 16 KB and does not expose other studio mutations. Existing studio/contract services were not restarted or modified.

Checked: JS syntax, Python compilation, real UI generation request, cross-origin POST rejected (403), unrelated scene route rejected (404). Listening approval is still required.

Default identity audition seed is fixed at 42 by user request. It does not increment with take count; previously saved recordings retain their original recipes.

Advanced controls: installed VoxCPM2 adapter uses num_step=10 and guidance_scale=2.0 by default (backend/engines/voxcpm2_subprocess/main.py). Exposed within existing designer limits: 1–64 steps, 0.1–8 guidance. Values persist and are included in requests and saved-take labels. Restore tested, no new generation.

## Single and batch generation
Both modes now submit a durable batch recipe to the loopback queue. Batch count is 1–50; one audition completes before the next starts. Fixed reuses the seed, increment advances by the chosen amount (wraps at 2^31), and random draws a fresh seed per item. Steps/guidance/description/script are frozen at submission; controls lock until the batch ends. Stop finishes the current take and skips the rest. Batch state survives browser reload and normal service restart; ambiguous interrupted submissions fail rather than being repeated.

Verification: controlled upstream fixtures cover three-item fixed/increment/random sequences, recipe preservation, sequential scheduling and duplicate submission tokens. UI count and seed modes checked. No real batch inference was run for this feature change; prior single real audition/playback was verified separately.

## Compact auditions
Auditions now use compact rows: custom Play/Pause, seek, duration, seed/steps/guidance, Use voice, WAV and word-check status. Details retains date/state, script, voice brief, recognised words and the full native audio player including volume. Delete writes a persistent recoverable trash marker scoped to this workspace; audio bytes and other studio records remain intact. Undo and Trash/Restore are available. Real browser delete/undo and playback checked; the original two samples were restored. No audio generated for this change.
