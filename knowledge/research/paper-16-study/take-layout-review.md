# Independent native-notebook layout review

Disposition: no blocking layout issues in the reviewed desktop Jupyter surface.

Reviewed `DESIGN.md`, `comparison_controls.py`, `review/model-inventory-final.png` and `review/take-comparison-final.png`. This is a rendered-layout and source review, not a keyboard or screen-reader runtime test.

- Reading order is coherent: four-model inventory → column selection → collapsed creation form → status → aligned delivery/model comparison. The inventory visibly lists IndexTTS 2.5, VoxCPM2, F5-TTS v1 Base and Dia 1.6B (MLX), with asset status and native-control distinctions.
- Rows visibly bind delivery, reference identity and script; columns name models. Each take repeats model and delivery, maintaining context as the intentionally wide matrix scrolls. The partially visible fourth column is consistent with the documented horizontal-scroll design, not a missing model.
- Density is appropriate for a research notebook: inventory spacing supports scanning, saved audio and version selection precede applied settings, and detailed editing stays collapsed. Independent controls are grouped within each recording. Native players fit their columns.
- Applied/pending boundary is explicit in source: applied text derives from selected saved metadata, while edited controls produce an “Edits pending” message explaining that playback remains saved audio. History uses an independent Version selector; generation appends a version. Failure status preserves audio and edits; missing-media text is local to the affected player. Screenshots show the normal saved state; pending and failure appearances were assessed from source only.
- Accessibility source facts: inventory uses native table/header elements; widget inputs have descriptions; generation buttons have text labels; audio elements have model/delivery `aria-label` attributes; no essential distinction depends on custom color. Matrix grouping is visual CSS Grid with textual headings, not semantic table row/column associations. Status and pending HTML are not explicit live regions. These limit claims of assistive-technology coverage, but no material desktop-layout blocker is demonstrated. Runtime keyboard navigation, announcement behavior and contrast across notebook themes remain unverified.

No code or browser changes made.
