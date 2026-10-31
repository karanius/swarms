## Consolidated experiment record and findings to date

This section distinguishes technical execution, the user's listening observations, and interpretations. It does not replace the original recordings or retroactively turn unscored trials into successful acting demonstrations.

| Experiment | What changed / what stayed fixed | Established outcome | Listening outcome and limit |
|---|---|---|---|
| Initial 32-take audition pilot | Two engines, two speakers, two texts, four requested styles. VoxCPM2: fixed neutral reference plus written direction. F5: same-speaker expressive references. | All planned takes generated and passed technical checks; matched listening copies preserved. | The user reported mood differentiation but found the acting inadequate. No complete per-take ratings or word/identity verification were recorded. |
| Short relief/disbelief reference | New line: “You came back. I thought I'd lost you.” VoxCPM2, existing male neutral reference, seed 7, 10 steps, written direction requesting relief and disbelief. | 3.04-second real generated recording; not captured live-assistant audio and not downloaded media. | The user described it as better. This is encouraging feedback on one take, not proof of reliable emotion control. |
| Dynamic passage | One continuous call; distinct sentences and semantic cues paired with directions for urgency, pleading, recognition, hurt and relief. Same engine, reference, seed and step count as subsequent switching test. | 11.36-second recording. No sentence splicing or manual acting edits. | No explicit detailed listener rating was recorded. The content and punctuation themselves suggest an emotional arc, so this is not an isolated test of instruction control. |
| Opposite-tone neutral control | “I need you to stay right here.” repeated three times, neutral direction, same engine/reference/seed/steps. | 5.44-second recording. | Comparison control; exact repetition delivery remains unverified by transcription. |
| Opposite-tone directed take | Identical repeated words; requested controlled anger → tender reassurance → controlled anger in one call. | 5.28-second recording. Both conditions statically matched to −23 LUFS, with no compression or segment splicing. | The user reported the neutral and directed takes sounded the same. This experiment did not demonstrate useful within-passage emotional switching. |
| File and embedding audit | Compared saved files, byte contents and the notebook's embedded audio payloads. | Two distinct recordings with different durations and hashes; notebook payloads match the intended separate files. | Rules out a saved-file/notebook overwrite or duplicate embedding. It does not independently verify delivery through the live voice-chat player. |
| Acoustic comparison | Same two matched files; duration, amplitude-gated Yin pitch, RMS dynamics, waveform correlation and aligned MFCC features. | Neutral vs directed: duration 5.44/5.28 s; median pitch 174.9/181.6 Hz; pitch IQR 55.1/58.0 Hz; active-frame RMS spread 11.27/11.79 dB. | Modest overall differences and broadly similar contours are consistent with weak perceived contrast. These diagnostics do not classify emotions or independently prove absence of every local delivery difference. |

### Why the two continuous-passage tests differ
The generation mechanism did not change: one native VoxCPM2 API request with raw application effects, a fixed existing voice reference and written delivery instructions. The dynamic passage used different sentences, emotion-bearing meanings, punctuation and sentence-specific direction. The opposite-tone test held the words identical, placing more of the burden on instruction-following alone. The first cannot be treated as independent proof of a notation-based performance controller.

### Findings supported now
1. We can generate local, source-traceable speech and direct it through written instructions and/or references. The existence of these controls is established; reliable obedience to them is not.
2. The short relief sample received positive comparative feedback from the user. That result is local to one example.
3. The identical-word switching experiment failed to demonstrate the intended perceptual contrast for this listener. Successful API calls, distinct hashes and small signal differences do not override that outcome.
4. There is no evidence here that the arrow notation itself is parsed as a formal acting language. It is a human-readable summary; actual conditioning was prose.
5. Mastering was not used to manufacture acting differences in these tests. The comparison gain was static and preserves internal dynamics. Better technical audio quality and better acting remain separate goals.

### What remains unresolved
We have not shown reliable phrase-level emotion trajectories, recognizable anger-versus-reassurance contrast on demand, speaker identity continuity, exact text preservation, transfer of an externally supplied performance to new words, seed robustness or a superior model. No YouTube/podcast recording or live-assistant audio was captured for these experiments. No performance-transfer engine was installed or tested. The current evidence does not justify collecting a large reference library or replacing the approved production voice.

### Next discriminating experiment — proposed, not executed
Generate the identical sentence independently under neutral, controlled-anger and tender-reassurance directions, keeping the reference and sampling settings fixed. Audition the isolated lines before joining them. This separates the ability to produce contrasting single-line deliveries from the ability to switch within a continuous passage. If isolated contrast also fails, evaluate a verified performance-transfer/voice-conversion mechanism with an appropriate performed source; do not treat additional elaborate global directions as an established fix.

The current record is an exploratory study with one listener's qualitative feedback. There is no blinded listening panel, automatic emotion validation, independently verified transcript alignment or statistical significance claim.

