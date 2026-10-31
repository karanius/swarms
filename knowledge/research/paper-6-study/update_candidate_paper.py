"""Add the bounded candidate boundary study without changing prior figures/abstract."""
import base64,copy,hashlib,json
from pathlib import Path
import nbformat
ROOT=Path(__file__).resolve().parents[3]
PAPER=ROOT/'knowledge/research/notebooks/Paper 6 - Rule Mining from Langflow Templates.ipynb'
STUDY=ROOT/'knowledge/research/paper-6-study'
BASE=ROOT/'knowledge/research/paper-6-corpus'
nb=nbformat.read(PAPER,as_version=4)
backup=STUDY/'paper-6-before-candidate-study.ipynb'
if not backup.exists():nbformat.write(nb,backup)
audit=json.loads((BASE/'candidates/audit.json').read_text());s=audit['stats']
nb.cells=[c for c in nb.cells if not c.metadata.get('paper6_candidate')]
def md(text):
 c=nbformat.v4.new_markdown_cell(text);c.metadata['paper6_candidate']=True;return c
at=next(i for i,c in enumerate(nb.cells) if ''.join(c.source).startswith('## Interactive corpus topology'))
nb.cells[at:at]=[
md('''## Candidate group explorer

[Open candidate groups in a full page](/candidate-explorer/). This third, independent figure studies proposed group membership and boundaries on actual source workflows. The original corpus map and repeated-connection explorer remain available.'''),
md('''### From repeated connections to a proposed collective

Choose a starting pair and one real example. The dashed boundary encloses the current selection; mint nodes and wires are internal, amber wires cross the boundary, and gray nodes provide outside context. Click components, use the named checkboxes, or expand by one hop. The induced internal graph and boundary tables update together. Dragging changes layout only.

Write a proposed bounded purpose, inspect required fields and potential terminal outputs, then download the candidate specification if useful. Edits are temporary until downloaded. This is a component-plane research view: no library promotion, task execution, automatic purpose inference or claim of emergent composites.

| Representation | Meaning | Must not be mistaken for |
|---|---|---|
| Selected component occurrence IDs | Members of one proposed group in one source graph | Merged type identities across workflows |
| All source edges with both endpoints selected | Induced internal topology | Only the two motivating edges |
| Recorded edges entering/leaving the selection | Proposed interface obligations at the cut | Complete runtime interface or validated ports |
| Required input declaration without incoming saved wire | Configuration/default/binding review needed | Proof that a value is absent |
| Unconsumed output declaration | Possible terminal exposure | Confirmed active output |
| Purpose text | Human-supplied proposal | A purpose mined from connectivity |
| Observed / proposed / unknown / blocked | Separate structural observations, intent, unresolved work and selection problems | A composite approval score |
''')]
additions={
'## 1. Research Question and Scope':'''### Added boundary question

For one recorded occurrence group suggested by an association, can we preserve its identities, expose every recorded crossing wire, and distinguish structural observations from unknown configuration and purpose? The candidate-group explorer addresses this narrower bridge toward composite formation. It does not claim to discover useful group boundaries automatically.''',
'## 3. Hypotheses, Alternatives, and Falsification':'''### Boundary-study expectations and challenges

A repeated pair need not stand alone. We challenge that interpretation by computing the complete induced subgraph and every incident crossing wire. A candidate can also be cyclic despite the two-feature seed being connected. Any omitted crossing edge, invented occurrence, falsely claimed missing value, or support count applied to an edited group would contradict the implementation contract. These are post hoc engineering checks, not preregistered scientific hypotheses.''',
'## 5. Representation and Operational Definitions':'''### Candidate boundary algebra

Given a saved directed graph G=(V,E) and selected occurrence set S ⊆ V:

- Internal edges E[S] = {(u,v)∈E : u∈S ∧ v∈S}.
- Incoming cut δ⁻(S) = {(u,v)∈E : u∉S ∧ v∈S}.
- Outgoing cut δ⁺(S) = {(u,v)∈E : u∈S ∧ v∉S}.
- Outside edges E[V\\S] have neither endpoint selected.

The four sets partition source edge records, including parallel records. Unresolved incident records stay flagged. Connectivity is weak connectivity of E[S]; acyclicity is checked separately using a topological traversal. Neither proves semantics, active ports or behavioral correctness. A seed uses actual endpoints of one witness edge per feature; it may have two or three members. Expanding is S ← S ∪ N(S), using recorded immediate neighbors only.

| Candidate field | Stored content | Judgment |
|---|---|---|
| graph, source file hash, source pointer | Exact saved-graph reference | Observed provenance |
| members | IDs, types, versions | Observed scoped identities |
| internal, incoming, outgoing | Full source edge records | Observed topology |
| unresolved | Incident endpoint/handle uncertainty | Unknown boundary completeness |
| unconnectedInputs, terminalOutputs, resources | Declarations, requiredness, dynamic flags; no values | Review obligations / proposed exposures |
| purpose | Editable bounded job statement | Proposed |
| checks | Nonempty, connected, acyclic, readable edges, purpose, configuration, ports, usefulness | No aggregate approval score |
| sources | Every recorded origin | Provenance, not independence |
''',
'## 6. Rule-Mining Method and Baselines':'''### Candidate inspection stage after association discovery

Collapse the two directional association summaries into one unordered feature pair for browsing (445 starting pairs). Choose an actual joint witness, seed membership from its recorded endpoints, and compute the entire induced subgraph and its cut. Manual membership changes recompute those records. This is a deterministic inspection mechanism, not another learned rule set or an automatic optimum partition. The original association support remains attached only to the starting pair, never the edited group. No additional mining algorithm comparison has been run.''',
'## 7. Implementation and Reproducibility':'''### Candidate-stage artifacts

The shared pure implementation is `frontend/candidate-explorer/model.mjs`; the React Flow view is `/candidate-explorer/`. Run `node --test knowledge/research/paper-6-study/test_candidates.mjs` for controlled invariants, and `node knowledge/research/paper-6-study/audit_candidates.mjs` for the frozen representative audit. The latter records model/input hashes and per-graph results in `paper-6-corpus/candidates/audit.json`. No downloaded component code, configuration values, credentials or model calls are executed or read. Candidate JSON is downloaded explicitly; source workflows are not edited.''',
'## 8. Test Design and Evaluation Protocol':'''### Boundary-stage verification

Eight controlled tests check incoming/internal/outgoing partitioning, disconnected required fields, potential terminal outputs, occurrence aliasing and one-hop expansion, cycle/disconnection detection, unknown edges, empty selection/source immutability, and parallel edges. A separate audit applies independent endpoint predicates to every edge in 445 representative graphs/seeds, confirms witness inclusion and member identity, and retains every source origin. This covers one ranked representative per unordered pair, not all occurrences or arbitrary edited selections. Browser checks cover selection, expansion/reset, purpose editing, source disclosure, search and notebook embedding. These are engineering checks; they do not constitute independent evaluation of composite usefulness.''',
'## 9. Results and Evidence':f'''### Candidate-group boundary audit

| Observed result | Count | Interpretation |
|---|---:|---|
| Representative starting groups audited | {s['candidates']} | One ranked witness per unordered feature pair |
| Groups with at least one crossing wire | {s['withCrossingWires']} | Most seeds depend on or serve outside context |
| Groups with a required field lacking incoming saved wire | {s['withRequiredUnwired']} | Values/defaults uninspected; not proven missing |
| Groups with an unresolved incident endpoint/handle | {s['withUnresolvedIncident']} | For this representative subset only |
| Weakly connected groups | {s['connected']} | Expected from shared-center seeds; not a discovery of usefulness |
| Acyclic induced groups | {s['acyclic']} | Five seeds contain a cycle once all induced edges are included |
| Controlled boundary-model tests | 8 / 8 | Implementation checks, not task outcomes |

Categories overlap. Counts are descriptive and do not estimate prevalence of independently designed composites. The 443 crossing-wire groups and five cyclic groups show why a repeated pair should not automatically be packaged as a self-contained DAG.

![Representative candidate boundary audit](attachment:candidate-audit.png)

**Worked source example:** In the selected NVIDIA RTX Remix graph, Chat Input, Agent and Chat Output yield three selected occurrences and two internal wires. Three other recorded wires enter Agent from Prompt, FAISS and MCPTools. Agent.model is a required declaration with no saved incoming wire; its configured value is unknown here. One-hop expansion selects six occurrences, changes those former crossing wires into internal wires, and reveals two incoming wires to FAISS from documentation and embeddings. That is boundary refinement, not proof of a completed composite.''',
'## 10. Critical Discussion and Defense':'''### What this additional view establishes

A pair is a starting clue, not a complete collective. Inspecting the full induced subgraph can reveal extra internal connections and cycles; inspecting the cut reveals dependencies hidden by the tiny preview. Expanding a group changes its interface but does not tell us whether expansion improves cohesion, purpose or reuse. No score is optimized. The human-proposed purpose remains distinguishable from the mined evidence, and all unknown resource/configuration/behavior judgments remain open.''',
'## 11. Learning, Revisions, and Follow-Up':'''### New learning from boundary inspection

The old visual summaries are preserved. The new view addresses their main limitation by tying one editable selection to its exact internal graph and cut. Future work must define how purpose, configuration and behavioral evidence justify a boundary; compare proposed groupings; and evaluate the learned relational rules. A next-layer Composite representation must reference these occurrences rather than manufacture new identities. This implementation has not created that plane.''',
'## 12. Limitations, Bias, and Threats to Validity':'''### Candidate-stage limits

The representative audit is selected by the existing exploratory ranking, not a fresh random sample or held-out test. The 445 groups are dependent and may originate from copied designs. Configuration values are deliberately absent; declarations cannot establish runtime requirements or output activation. The viewer uses saved type/version labels and does not certify native component implementations. Whole-workflow selection may be disconnected or cyclic. Manual purpose text does not validate usefulness. Browser edits are temporary until explicit JSON download; downloading does not promote anything into the library.''',
'## 13. Outcomes and Conclusion':'''### Updated outcome

Paper 6 now offers three complementary research views: a corpus overview, repeated local connection evidence, and a candidate-group boundary workbench. The new workbench makes the next question inspectable—what belongs inside a proposed collective, and what must remain exposed—while keeping purpose and missing validation explicit. It is progress toward studying composite formation, not a demonstration of autonomous emergence or higher-layer generation.''',
'## 14. Review, References, and Reproducibility Appendix':'''### Boundary extension disclosure

This extension received controlled tests, a separate edge-partition recount, and in-app interaction checks. The earlier internal AI review concerned the association study; it is not retroactively a review of this new extension. No external academic review, behavioral evaluation or held-out inference is claimed. Supporting files: `candidate-explorer/model.mjs`, `test_candidates.mjs`, `audit_candidates.mjs`, `candidates/audit.json`, and `CANDIDATES.md`.
'''
}
for c in nb.cells:
 for heading,text in additions.items():
  if c.source.startswith(heading):
   if '\n\n<!-- candidate-extension -->' in c.source:c.source=c.source.split('\n\n<!-- candidate-extension -->')[0]
   c.source+='\n\n<!-- candidate-extension -->\n'+text
 if c.source.startswith('### Current study status'):
  c.source+='\n\nThe candidate-group boundary explorer is now also implemented: editable source-scoped membership, complete induced edges and crossing-wire tables, unknown configuration judgments, and an audited 445-representative study. It does not infer purpose or approve composites.' if 'candidate-group boundary explorer is now also' not in c.source else ''
for c in nb.cells:
 if '![Representative candidate boundary audit]' in c.source:
  c.attachments={'candidate-audit.png':{'image/png':base64.b64encode((BASE/'candidates/audit-figure.png').read_bytes()).decode()}}
nbformat.write(nb,PAPER)
old=nbformat.read(backup,as_version=4)
assert nb.cells[0].source==old.cells[0].source
for tag in ['paper6_topology','paper6_topology_evidence']:
 assert [c.source for c in nb.cells if c.metadata.get(tag)]==[c.source for c in old.cells if c.metadata.get(tag)]
print('Updated Paper 6; original abstract and both old figure cells preserved.')
