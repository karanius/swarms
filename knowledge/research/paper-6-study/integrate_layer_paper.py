"""Coordinator reviewed integration of Study E; prior abstract/outputs unchanged."""
import json,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'services/paper6-assistant'))
from workspace import Workspace,PAPER,atomic,sha
BASE=Path(__file__).resolve().parent
EXTRA={
7:'''### Study E implementation — native construction and finite layer checks

The dedicated research assistant now has a scoped adapter to the actual `lfx.graph.flow_builder.builder.build_flow_from_spec` used by native builder tools. It can inspect three unchanged native types and build private graph artifacts, without installing the stock canvas prompt/toolkit, loading user overlays, executing components, resolving credentials, or mutating the active canvas. A coordinator-pinned registry snapshot and native source/registry hashes accompany the build. `layer_builder.py` uses explicit registry injection and bounded configuration fields.

| Artifact | Role | Interpretation |
|---|---|---|
| `assistant-workspace/artifacts/tower-native-v1-compact.json` | Assistant-built actual 4-node/3-wire native graph | Static native assembly witness, not behavior |
| `assistant-workspace/artifacts/layer-contract-proposal.md`, `layer-contract-v1.json`, `tower-instance-v1.json` | Assistant's critical proposal | Preserved authored ontology, not discovered hierarchy |
| `layers/instance-v1.json`, `instance-v2.json` | Coordinator-normalized shared contract | Same occurrence identities; proposed prompt revision only |
| `layer_contract_engine.py` | Closed finite schema, native/cut/API/obligation/order checks and bounded stage gates | Structural diagnostic, not complete semantic validation |
| `layers/verification.json`, `construction-trace.json` | Recount and decision trace | Explicit blocked readiness and evidence questions |
| `layers/layer-results.ipynb` | Real executed code, tables, layer diagram and fault checks | Saved evidence is reproduced below |

Hashes have distinct bases: the native artifact's revision is SHA256 of saved bytes; `nativeGraphSha256` is SHA256 of the wrapper serialized with sorted JSON keys. These are not interchangeable hashes or different graph identities. The original interrupted attempt is preserved separately. One request used prose instead of the native compact grammar; its turn was canceled, tool documentation/error reporting corrected, and a fresh compact native build succeeded. That operational failure is not a mining or layer-generation finding.
''',
8:'''### Study E checks and stopping rules

This is a coauthored development example, not an evaluation sample. The native builder produced real static node/edge JSON; the higher grouping, purposes and policies were authored and normalized. The checker verifies reference identity, native fields/handles/type overlap, the specimen's DAG policy, exact induced/crossing wires, public input/output declarations, lower/scoped obligation retention, configuration ownership, handoff order, requirement references, and no runtime promotion.

The final finite check performs 139 assertions per revision, with 10 open obligations. Nineteen deliberately corrupted artifacts test sensitivity to specified errors; four test methods cover the positive case, corruption family, revision footprint, and finite stage gates. These are engineering coverage counts, not independent observations, success rates or significance estimates. Early checks missed scoped-obligation retention, configuration ownership and order compatibility; fault injection and a separate source reviewer exposed them, and the checker was repaired before final recount. Preserve those corrections as development history.

The deterministic trace inspects authored decompositions top-down, checks the saved native witness bottom-up, and stops with questions. It does not infer the hierarchy from a request autonomously. An explicit finite budget and repeated-state guard prevent endless gate traversal. Invalid structure stops with rejection. Passing the structural gate does not resolve purpose, runtime, policy or human authority.
''',
11:'''### Study E development and revision evidence

The collaboration moved from interview/debate to source research, native static construction, normalization, checking, revision and manuscript writing. One manuscript-writing turn reached the native agent call budget after saving five sections; a narrower continuation completed the conclusion. This operational limit was recorded and subsequent runtime reporting distinguishes budget exhaustion from successful completion. Native Langflow source inspection identified a pure builder seam that needs no canvas HTTP backend; official component/subflow documentation clarified that human approval is not realized by merely nesting graphs. The research profile gained native discovery/build functions while keeping its separate paper draft and workspace authority.

The native builder created one four-occurrence graph; two Agent occurrences remain distinct. Two composites, one flow and one process interpret those same identities. In revision2 only a proposed draft prompt and revision metadata change; requirements, obligations, all occurrence IDs and the native graph stay identical. This is a middle-out specification revision, not a prompt applied to an executable workflow or an approved triage policy.

A separate runtime/source reviewer reproduced three checker false positives; all were corrected and their corruptions now fail. Additional checks close the accepted vocabulary and distinguish a public API from graph cuts. The final trace stops at missing evidence, retaining all ten obligations. A newly discovered obligation is progress in accuracy even when the open count does not shrink. No mutation, test or reviewed assertion converts this one authored specimen into a reliable general generator.
''',
14:'''### Study E provenance and review disclosure

Primary local-source findings are in `layer-builder-research.md`, with exact native source locations and checkout commit. The upper-plane ontology is ours; Langflow's component graph called a “flow” is not automatically the Flows plane. Official references: [Components overview](https://docs.langflow.org/components/) and [Run Flow documentation](https://docs.langflow.org/next/run-flow). The latter's nested-human-approval constraint is a prospective execution consideration, not a feature exercised here; version compatibility must be checked before adopting it.

Reproduction: run `build_layer_example.py` to normalize the preserved native witness; run `python -m unittest discover -s knowledge/research/paper-6-study -p test_layer_contract_engine.py -v`; use the existing research Python environment to execute `build_layer_notebook.py`. The saved paper cells recount source artifacts and display the diagram without invoking a model, provider, native component or ticket action. The native build itself is evidenced separately in the assistant's tool events and graph artifact with native IDs and engine/registry provenance. Raw registry code remains unchanged and is not executed by these builders.

`assistant-workspace/artifacts/tower-review.md` records the collaborating assistant's critical review. `layer-builder-research.md` records a separate internal source reviewer, including replicated checker defects and their disposition. This is internal AI-assisted authorship and software checking, not external academic peer review. The finite checker cannot establish API usefulness, real-time scheduling, confidentiality enforcement, human authorization or behavior. Negative mining findings and Study D's original acceptance disagreement remain unchanged.
'''
}
def main():
 ws=Workspace();original=json.loads(PAPER.read_text());oldcode=[c for c in original['cells'] if c['cell_type']=='code']
 for num,text in EXTRA.items():
  cur=ws.section(num);ws.write_section(num,cur['markdown'].rstrip()+'\n\n<!-- layer-engine-extension -->\n'+text,cur['revision'])
 for num in (1,5,6,9,12,13):
  cur=ws.section(num);text=cur['markdown']
  marker='<!-- layer-extension -->'
  # The assistant may use a different explicit Study E marker; normalize only the new suffix.
  pos=text.find('### Study E')
  if pos>=0:
   head=text[:pos];tail=text[pos:].replace('This does not yet define every unwired public API endpoint.','The final normalized schema also checks explicit native public input/output declarations and propagates them to the flow; that establishes endpoint existence, not full API adequacy.').replace('Cut equality covers actual wires, not every unwired public interface or resource dependency.','Cut equality covers actual wires; the final schema additionally checks public native input/output declarations, but neither establishes API adequacy or every resource dependency.').replace('87 structural assertions','139 structural assertions').replace('87 checks','139 checks').replace('fifteen','nineteen').replace('15 corrupted','19 corrupted').replace('15 deliberate','19 deliberate')
   ws.write_section(num,head+tail,cur['revision'])
 numbers=ws._load('draft-base.json',{})['changedSections']
 for num in numbers:
  prefix=f'## {num}. ';prior=next(''.join(c['source']) for c in original['cells'] if ''.join(c['source']).startswith(prefix));assert ws.section(num)['markdown'].startswith(prior),'Prior section changed'
 ws.publish_checked_sections(numbers)
 n=json.loads(PAPER.read_text());study=json.loads((BASE/'layers/layer-results.ipynb').read_text())
 for c in study['cells']:c.setdefault('metadata',{})['paper6_layer_study_e']=True
 assert not any(c.get('metadata',{}).get('paper6_layer_study_e') for c in n['cells'])
 index=next(i for i,c in enumerate(n['cells']) if ''.join(c['source']).startswith('## 8. '));n['cells'][index:index]=study['cells']
 status=next(c for c in n['cells'] if ''.join(c['source']).startswith('### Current study status'))
 status['source']=(''.join(status['source'])+'\n\n**Study E update:** The paper now defines Configuration, Components, Composite, Flows and Processes, with separate relation meanings and explicit promotion gates. The isolated assistant used actual native Langflow builder machinery to create 4 component occurrences and 3 wires. Higher packaging (2 composites, 1 flow, 1 process) is proposed. Two identity-preserving revisions pass 139 finite structural checks each; 10 obligations remain open. The bounded deterministic trace ends by asking for evidence. This is an authored partial tower, not autonomous hierarchy discovery or an executed triage system.\n').splitlines(keepends=True)
 assert n['cells'][0]==original['cells'][0]
 assert [c for c in n['cells'] if c['cell_type']=='code' and not c.get('metadata',{}).get('paper6_layer_study_e')]==oldcode
 atomic(PAPER,json.dumps(n,indent=1));atomic(ws.root/'paper-draft.ipynb',PAPER.read_text());atomic(ws.root/'draft-base.json',json.dumps({'canonicalSha256':sha(PAPER.read_bytes()),'changedSections':[]}));ws.event('layer_study_checked_merge',sha256=sha(PAPER.read_bytes()),cells=len(study['cells']))
 print('Merged Study E; original abstract and',len(oldcode),'prior code cells/outputs preserved')
if __name__=='__main__':main()
