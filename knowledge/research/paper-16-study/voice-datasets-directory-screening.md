# One expressive speaker — directory screening

31 October 2026. User objective: one coherent, well-performed English reference set that can later support alternate character voices. Preserve the recorder and existing reference library; this investigation does not install or replace anything.

## Coverage

Read the full [user-provided directory](https://github.com/jim-schwoebel/voice_datasets), containing 83 speech-list bullets and 11 audio-event/music bullets in the fetched revision. Counts are list entries, not distinct usable datasets: some entries are directories or duplicate collections. Screened all entries by fit, then followed original documentation for plausible candidates. This is not an audio audition or independent validation of every listing. Source checksum, inspected primary pages and access limitations are in voice-datasets-directory-screening.json.

Noise/music collections, digit/command corpora, speech separation, generic recognition and celebrity-identification resources do not directly provide the required annotated acting range. Non-English acted collections may have future cross-language uses; they are not the initial English speaker set. Public availability does not establish voice cloning or commercial reuse permission.

## Decision

**From this directory, prioritise one CREMA-D actor for an audition.** Its [official repository](https://github.com/CheyneyComputerScience/CREMA-D) provides actor identities, six emotional categories, intended intensity, transcript sentence codes, and audio-only listener votes. Unlike selecting a filename labelled anger, we can filter for recordings listeners actually heard as anger. Licensing is ODbL for the database and DbCL for individual contents; preserve both and examine the proposed use rather than assuming unrestricted personality cloning. Short, constrained sentences may limit naturalistic acting and reference continuation. No specific actor is selected without listening.

**Keep EMNS as the outside-directory comparator.** [OpenSLR](https://www.openslr.org/136/) describes one British English speaker with emotion, intensity and natural-language delivery descriptions, and lists Apache 2.0. It is a closer annotation-design fit, but this review has not heard its audio. Previous preference for EMNS was based on documentation, not an established quality winner.

## Other plausible candidates and why they do not close the gap yet

| Candidate | Primary evidence / remaining issue |
|---|---|
| JL Corpus | [Author repository](https://github.com/tli725/JL-Corpus) offers primary and secondary emotions and reports a perception study, but explicitly describes the raw download as unchecked/unannotated and says a verified release will follow. Do not silently treat raw material as qualified. Current Kaggle contents and licence remain unverified. |
| RAVDESS | [Official release](https://zenodo.org/records/1188976) provides professional actors, eight speech categories, normal/strong performances and perceptual validation. Only two statements per actor; neutral has no strong condition. CC BY-NC-SA and separate commercial licensing. Strong controlled audition candidate, weaker as a broad production reference library. |
| EmoV-DB | [Creators](https://github.com/numediart/EmoV-DB) provide longer actor-specific emotional synthesis material and alignment tools, with neutral, amused, anger, disgust and sleepy styles. [Dataset terms](https://raw.githubusercontent.com/numediart/EmoV-DB/master/LICENSE.md) explicitly restrict use to non-commercial purposes. Not a complete solution for the revenue-focused application. |
| IEMOCAP | [USC release](https://sail.usc.edu/iemocap/iemocap_release.htm) has improvised/scripted actor interactions, transcripts, alignments and multiple annotators. Requires access request and licence review; not a frictionless openly reusable drop-in. |
| MSP-IMPROV | [Creators](https://www.lab-msp.com/MSP/MSP-Improv.html) document acted interaction with academic release conditions and a separate commercial licence. More access friction than the desired starting collection. |
| GEMEP | [Author-hosted description](https://www.unige.ch/cisa/files/5814/6721/0641/Banziger__Scherer_-_2010_-_Introducing_the_Geneva_Multimodal_Emotion_Portrayal_GEMEP_Corpus.pdf) uses pseudo-speech; nuanced acting does not make it a straightforward English transcript-conditioned reference set. Main page was blocked. |
| Keio-ESD | [Provider](https://research.nii.ac.jp/src/en/Keio-ESD.html) describes one Japanese male speaker, 47 emotional categories, and recorded words. Broad labels alone do not solve our English sentence-performance requirement. |
| LJ Speech | [Creator page](https://keithito.com/LJ-Speech-Dataset/) provides a large public-domain single-speaker transcript collection. Its metadata does not provide the desired acted emotion/intensity library. |
| Movie/TV-derived emotion corpora | Source footage plus emotion labels does not automatically provide clean, reusable single-speaker generation references. Audio and underlying content rights still need independent assessment. |
| TESS, SAVEE, EmoFilm | Candidate leads retained, but primary access failed in this investigation. Do not report them as individually verified or quality-ranked. |

## Next concrete proof

Choose candidates from one CREMA-D actor using audio-only label agreement; compare neutral and contrasting emotional clips with exact transcripts and intensity metadata visible. Audit duration, clipping, noise and speaker consistency. Run a held-out sentence through one generator before expanding or transforming the voice. Compare that audition with a small EMNS selection. Keep failures. Neither catalogue coverage nor published emotion-recognition ratings prove reference-transfer quality in our speech generators.

No audio has been auditioned, no new data downloaded, and no reference promoted in this directory review.
