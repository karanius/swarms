# Canonical performance reference audit

## Finding

The library is traceable, but is not a qualified acting library. Do not equate a matching file hash with a correct emotion, exact transcript, or stable perceived identity.

The audit verified all 50 enhanced reference clips against their recorded hashes and linked each to its original preset and source WAV, also hash-verified. These cover ten dataset speakers and five source emotion categories. Qualification focuses on speaker 0012; other speakers and recordings remain available. All 19 existing take-library recordings resolve to canonical reference files with matching saved hashes and speaker identifiers. This validates manifests, not what a model actually learned from those files.

## Source limitations

The [original ESD documentation](https://github.com/HLTSingapore/Emotional-Speech-Data), checked 31 October 2026, describes parallel transcripts and five categorical emotions. It restricts the dataset to research and requests a licence form. This audit establishes no commercial permission. The existing local mirror provenance and revision are retained in every reference entry.

The selected sentence's transcript is inherited, including unusual wording. It has not been independently verified, corrected, or force-aligned. Dataset speaker IDs are provenance assertions, not independently verified voice identity. Intensity, intent, arousal, valence, emphasis and pauses were not supplied. They remain null. No machine-inferred emotion rating is presented as human evidence.

The playback references are enhanced derivatives (mastering, Resemble Enhance, resampling and added trailing silence). Their processing history and original/source paths are recorded. Enhancement could change performance cues; it is a potential confound, not an annotation improvement.

## Implemented contract

`reference-library.json` is the shared canonical catalog. `reference-library.schema.json` validates structure and bounds; `reference_library.py` resolves catalog entries and model roles. IndexTTS now reads that catalog instead of an independent Paper 14 snapshot. Vox, F5 and Dia receive the same selected performance reference; IndexTTS additionally receives neutral identity conditioning. Dia without continuation records no reference bindings. New takes save role-specific canonical IDs, exact hashes and library version. Existing historical records are not rewritten.

The notebook shows annotation status beside its shared audition. It explicitly labels all source references candidate/unrated. Six library tests verify integrity, consistent model bindings, no-reference behavior, explicit unknowns, invalid intensity rejection and duplicate rejection. Seven existing control/queue tests pass with stubbed inference. No new native generation was needed or claimed for the metadata audit.

## Qualification checklist — not yet completed

1. Start with speaker 0012, one neutral identity anchor and the five candidate source clips.
2. Compare each source original, unenhanced preset and enhanced derivative. Check exact words and record corrections as a versioned annotation, preserving source metadata.
3. Listen without the emotion title first. Record perceived emotion, intensity, confidence, performance intent and any artifacts. Only a documented listening judgment may fill these fields.
4. Reject mismatched, ambiguous, damaged or poorly performed clips. A categorical dataset label never automatically promotes a reference.
5. Check each accepted candidate on at least three fresh target lines and two fixed seeds, preserving all outputs and failures. Score exact wording, identity, naturalness and intended delivery separately.
6. Compare models using the same target, canonical performance reference and recorded native settings. IndexTTS's extra neutral identity reference is an explicit experimental difference.
7. Only claim qualification for the tested speaker, reference, model and task range. Keep untested styles separate. Broader production use requires eligible source material and separate rights review.

## Current result

Engineering/provenance foundation implemented. Perceptual qualification remains open. No reference is promoted and no model is declared a winner. User distrust of the current emotional annotations is consistent with this audit.
