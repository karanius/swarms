# Paper 13: Two Voices, One Integrated Local Video

The notebook is the primary interface and execution record. No separate app is created.

`Paper 13 - Two Voices One Integrated Local Video.ipynb` contains the editable cast/script, actual production call, independent checks, embedded video and scene sheet.

## Engines and picture

- Female prepared speaker 0015 uses sadness and surprise references.
- Male prepared speaker 0012 uses neutral and happiness references.
- Each turn runs through the existing audio workbench worker: F5 on MPS → Balanced master → Resemble Enhance on CPU.
- Original procedural animation follows the speech timeline. It is not diffusion footage, facial animation or lip-sync.
- Each scene has a 0.35-second lead and at least 0.5 seconds after speech; scene durations are quantized to 24 fps.
- Complete-turn captions remain on screen; they are not claimed to be word-aligned.
- A quiet original three-tone bed is mixed below the enhanced voices. Enhanced source files remain unchanged.

The run folder retains script, worker snapshot, actual engine requests, stage reports/audio/originals, logs, timeline, generated pictures, silent picture edit, continuous soundtrack, final MP4 and independent verification. Earlier papers and Money's configuration/latest pointers are hash-checked for preservation.

## Reproduce

Open the notebook with the existing Research Python kernel and run its cells. It uses existing external local model assets and creates a new timestamped run. The code does not install or download weights. Voice inference and rendering take actual time. Existing runtime engines, Pillow, NumPy, FFmpeg and the notebook environment are prerequisites.

`verify.py` independently decodes the delivered video, checks audio correlation and scene timing, verifies real neural execution and original→master→enhanced hashes, checks visible motion in decoded frames, and invokes the independent audio meter on each turn. Technical checks do not prove perceived emotion, pronunciation, artistic quality or commercial clearance. The models and prepared voice samples retain their existing research/noncommercial constraints.
