# Character Library interface

## Scope

A browser-only interface preview at `/characters`, with a library, character home, voice-design workspace, creation form and links to earlier experiments. No generation, model selection, performance approval or backend voice-profile creation is wired here. Existing recordings and research work remain in their original pages.

Character drafts retain the original `paper16.character-library.ui.v1` local-storage key. Name, description and the optional voice brief are browser-local. The voice brief can be saved or cleared and survives reload; it does not claim that a model can produce the requested qualities. Save is disabled when there are no changes. Create audition remains disabled with an explicit unconnected explanation.

## Visual direction

Design read: a visual overhaul of a creative audio workspace for developing character voices, using a compact studio-product aesthetic. The design-taste-frontend skill is applied to redesign, typography, palette and interaction, rather than marketing-page hero imagery or scroll effects.

- DESIGN_VARIANCE: 6. Structured sidebar and asymmetric working panels, preserving routes and task order.
- MOTION_INTENSITY: 3. Short hover/press feedback only, gated by reduced-motion preference. No automatic or continuous animation.
- VISUAL_DENSITY: 4. Compact navigation, clearly grouped controls, readable empty states.
- Self-hosted Geist, weights 400/500/600. Phosphor regular icons rendered from the existing official React package at build time. No runtime framework added to the existing HTML service. Licence notices ship with these assets.
- Cool light neutrals or charcoal dark neutrals, one warm accent. Theme follows system preference initially; an accessible manual switch persists the choice.
- Main palette: light canvas `#f3f4f5`, text `#222629`, accent `#b34925`; dark canvas `#191c1f`, text `#edf0f2`, accent `#ed9c7a`.
- Radius scale: 12px work panels, 8px controls, 5px status labels. Panels represent real task boundaries, not decorative marketing cards.
- A compact sidebar, breadcrumbs and character-section links maintain navigation. Below 640px, the sidebar becomes a compact header; work panels stack below 850px.

## Routes and files

`characters.html` loads `character-ui/characters.css` and `character-ui/characters.js`. The server permits only known UI assets and font files under `/character-ui/`.

- `/characters`: library.
- `?view=new`: create a browser draft.
- `?id=…`: character overview and detail editing.
- `?view=design&id=…`: UI-only voice brief and empty audition area.
- `?view=experiments`: original designer, audition archive, Scene Studio, recording wizard and Paper 16 notebook. Legacy pages retain links back.

## Verification

Browser checks covered preserved character details, light/dark switching, 390px layout without horizontal overflow, a single page H1, brief save/reload/clear, disabled generation, and navigation between the overview, library and creation form. Console inspection found no page errors. Static JavaScript/Python syntax and the UI asset routes pass. Text, helper, placeholder, active-navigation and enabled-button token contrasts exceed 4.5:1 in both themes; see `contrast-check.json`.

Screenshots and evidence are in `knowledge/research/paper-16-study/character-ui-redesign/`. No Lighthouse result is claimed: no Lighthouse capability was available through the permitted browser tools. Marketing-only preflight items such as hero photography, logo walls and scroll choreography do not apply to this product workspace.
