# CREMA-D: building one actor's evidence-backed reference profile

## Verdict

CREMA-D can supply a **versioned reference bank**, not a complete theatrical personality or a trained voice model by itself. Its advantage is separating intended acting from audience perception. Its main limitations for our use are short clips, a constrained sentence set, uncertain model-transfer performance and use-specific rights questions.

The source revision and file hashes are pinned in `source-manifest.json`. Metadata ingestion and validation are implemented in `audit.py`; `prepare_candidate.py` downloads and measures the proposed actor's clips. No existing Paper 16 references or recordings were replaced. Seven audit tests passed. Actual actor auditions and novel-sentence generation remain pending.

## What the columns actually mean

[Official aggregation code](https://github.com/CheyneyComputerScience/CREMA-D/blob/master/tabulateVotesV2.r) groups responses by clip and presentation mode. Its CSV row key encodes `100000 × queryType + clipNumber`. Decode that key explicitly; row order is not a reliable model of the dataset. Mode 1 is audio-only, 2 face-only and 3 audiovisual. The word “movie” is a stimulus identifier; the speech WAV has the corresponding basename.

The six letter columns count chosen emotion categories. `numResponses` is their total; `agreement` is the largest count divided by that total. `emoVote` retains tied winners. `meanHappyResp`, for example, averages intensity **only among listeners who chose happy**. It is not the probability of happiness. A missing conditional group uses -1, which must become missing/null. `meanEmoResp` mixes ratings across selected categories. Normalised columns adjust each rater's observed rating range; they are not calibrated cross-model emotion controls. Intensity is a perceptual judgment, not audio volume.

Intended emotion/intensity from the filename, perceived distribution, uncertainty, and technical audio quality must remain separate fields. Never collapse them into one “quality” number.

## Executed whole-dataset checks

The pinned CSV has 22,326 modality rows for 7,442 clips and 91 actors. Every row passed count-sum, majority/tie and agreement checks, and joined to the official clip-number/filename table. Audio majority labels agree with the separate VoiceVote summary. We did not reaggregate individual raw rater responses or independently reproduce normalisation.

There are 644 tied audio-only majorities. Exactly 3,099 clips have a unique audio majority matching the intended category. For 3,654 clips, the set of audio-only majority labels differs from the audiovisual majority. These are computed metadata facts, not sound-quality judgments.

Example: `1001_IEO_HAP_LO` was intended happy/low, yet six of nine audio listeners selected neutral and three selected happy. Happy's mean intensity describes those three happy voters only. Treating the filename or that mean alone as evidence of a strong happy reference would be wrong.

## One candidate actor, selected transparently

The exploratory filter requires at least seven audio votes, a unique majority matching the intended category and at least 60% target votes. These are **candidate-selection parameters**, not validated acceptance thresholds. Actor ranking prioritises coverage of all six emotions, then the weakest emotion's best Wilson lower bound, then eligible count. Wilson intervals here are descriptive: shared raters, selection effects and the limited sample sizes restrict their interpretation.

Under this policy, 25 actors have at least one candidate in all six categories. Actor 1006 ranks first. Of 82 source clips, 38 pass the exploratory filter: anger 8, disgust 3, fear 2, happy 6, neutral 12, sad 7. This is policy-dependent, not proof that this actor sounds best. Selection used performance evidence, not demographic preference.

The top three per category (only two for fear) yielded 17 downloaded WAVs. All decode, contain non-silent PCM, and have recorded hashes. They are 16 kHz, about 2.30–3.90 seconds long. One has samples near full scale; that is a retake/review flag, not proof of audible distortion. Noise, breath, expressiveness and word correctness have not been listened to. See `candidate-table.md` and `actor-candidate.json`.

## Profile contract

Keep one actor identity with many reference entries, rather than one anonymous “angry voice.” Each entry records:

- Dataset/revision, actor, clip ID, source URL, exact downloaded hash and original filename.
- Script mapping and its verification status; any subsequent ASR or human correction must preserve the original mapping.
- Intended emotion and intended intensity, independently of perceived category counts and conditional intensity.
- Audio-only vote count, ties, target share, descriptive uncertainty and source normalisation method.
- Technical measurements, duration, sample rate, clipping flags and known limitations.
- Listening judgments, acceptance/rejection history and every generation test linking output to the exact reference.

Use statuses: ingested → technical checks passed → auditioned → reference approved → model/task qualified. Approval is scoped to a reference and tested use; it does not imply general commercial clearance or universal emotional transfer. The current profile remains **candidate_not_approved**, with no selected identity anchor and no fabricated listening or generation results.

## How it fits the four generators

Choose a clean neutral anchor after audition. IndexTTS receives that identity reference plus a selected emotional clip from the same actor. VoxCPM2, F5 and reference-conditioned Dia receive the selected performance through their adapters; they do not all support independent identity/emotion inputs. Save actual role bindings and request parameters for every run. Keep native model controls separate from dataset ratings.

The short durations deserve explicit checks. Dia's documented reference guidance prefers longer conditioning; do not silently concatenate different emotions or invent a transcript. F5's current preset-ID route also needs an adapter for custom references. These downloaded candidates are not yet connected to the current ESD-only notebook selection. A JSON manifest alone is not that integration.

## Adoption gates

1. Audition neutral and contrasting emotions blind to labels. Review the full source clip and the exact transcript; flag artifacts and ambiguous performances. Inspect all available candidates before choosing the anchor.
2. Keep more than one useful reference per emotion where supported, retaining distinct performances/intensities. Do not pretend the six categories cover reassurance, sarcasm or every theatrical intent.
3. Test at least three fresh target sentences with two fixed seeds per reference/model. Save every output and failure. Check exact words, identity, naturalness and emotional contrast separately. ASR and acoustic measurements are supporting diagnostics.
4. Validate the chosen selection on further held-out text; distinguish development selection from validation. Compare with the current ESD reference and a small EMNS sample before claiming improvement.
5. Only then expose approved actor/reference options in Paper 16 and map each into VoiceStudio/native generator profiles. Character-voice transformations require a separate test that preserves acting and identity consistency; they do not follow from emotion voting data.

[Dataset terms](https://github.com/CheyneyComputerScience/CREMA-D/blob/master/LICENSE.txt) specify ODbL for the database and DbCL for individual contents. Preserve attribution and terms, and examine the intended voice-generation use separately. This audit does not assert that a public dataset grants unrestricted identity imitation or settles every commercial right.

## Delivered versus remaining

Delivered: pinned source evidence, complete metadata audit, reproducible candidate ranking, one actor's downloaded reference bank, signal checks, structured profile and tested parser. Remaining: listening, transcript confirmation, identity anchor selection, real model transfer, custom-reference adapters, user-facing adoption and any voice transformations. No “fully adopted” claim is made before those gates pass.
