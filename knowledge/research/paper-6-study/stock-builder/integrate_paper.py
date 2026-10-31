"""Append checked Study F, keeping prior manuscript and saved outputs intact."""
import json,sys,copy
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3];sys.path.insert(0,str(ROOT/'services/paper6-assistant'))
from workspace import Workspace,PAPER,atomic,sha
ADDITIONS={
6:'''### Study F — three-role request-to-graph protocol

Study E supplied a compact graph recipe. It cannot establish how the normal Langflow Assistant selects components from natural language. Study F therefore treats the unchanged existing local assistant as a separate generation subject. The stock factory prompt and toolkit are not replaced by the Paper6 research profile. “Unchanged” describes the experiment interval, not a pristine upstream checkout.

| Role | Input and authority | Output/evidence gate |
|---|---|---|
| Native generation subject | Plain task text; normal local stock prompt/toolkit; separate backend/database/user workspace | Raw events, component/configuration graph and response, frozen before interpretation |
| Research collaborator | Frozen output, original request, native metadata, corpus and layer contracts | Purpose/boundary hypotheses, alternatives and gaps; no rewriting raw output |
| Coordinator/checker | Same frozen artifacts and explicit invariants | Source/graph fidelity, exact cuts and interfaces, inherited obligations and evidence-bounded claims |

The task requests ticket intake, category/urgency/reply suggestion, a separate critique stage, and presentation for human consideration, using built-ins only and without sending, updating or running the generated flow. It supplies no component types, aliases, edges, compact recipe or upper-layer grouping. The first native headless route persists a private graph; a second fresh normal UI-stream request uses the same task and no history to obtain fuller observability. These are two development observations with different API application semantics, not an efficacy comparison or independent evaluation sample.

The collaboration cycle is freeze request → stock generation → preserve raw result → native/configuration inspection → corpus comparison → research interpretation and alternatives → separate structural checking → narrow analyst revision or genuinely necessary task-level follow-up → writing/review. A failed analyst gate does not authorize rewriting the builder's graph or changing original task criteria. No further subject revision was needed merely to impose our preferred grouping. Stronger source-preservation or organizational approval requirements remain proposed follow-ups.
''',
7:'''### Study F implementation and actual native interfaces

`stock-builder/run_stock.py` invokes the standard local `/api/v1/agentic/assist/run` endpoint. `run_stream.py` uses the normal `/assist/stream` endpoint against a fresh blank private flow. The route reaches native `run_assistant_and_persist`/streaming service and the stock flow-builder factory; selected source files are hashed around the normal-stream observation. The subject is a separately launched existing Langflow backend, not an AgentComponent research profile with a borrowed builder primitive.

| Artifact | Meaning |
|---|---|
| `stock-builder/request.txt`, `PROTOCOL.md` | Frozen plain task and three-role protocol |
| `stock-builder/runs/` with latest manifests | Unmodified raw events, request, first persisted graph and separate streamed graph proposal |
| `stock-builder/effective-runtime.json`, `PROVENANCE-REVIEW.md` | Sanitized configuration observation and internal source review |
| `stock-builder/first-graph-inspection.json` | Redacted native fields/ports projection; omitted values are not assumed absent |
| `stock-builder/first-corpus-comparison.json` | Exact recorded motif support with provenance/examples |
| `assistant-workspace/artifacts/stock-first-analysis*.json` | Original and revised analyst upper-plane proposals over native identities |
| `stock-builder/verify_interpretation.py`, test and result files | Separate finite fidelity/inheritance checker and sensitivity evidence |
| `stock-builder/stock-results.ipynb` | Recount, table, diagram and optional genuine next-request cell |

The first collector misread the terminal-event key/envelope. Raw events survived; the real terminal and private graph were recovered from that same run without regenerating to repair collection metadata. The separate UI-stream request was already chosen for tool observability. Native headless autoapply and a normal UI proposal must not be conflated. Jupyter's optional next-request cell is disabled by default, so reading/reproducing this paper does not spend new model calls or execute a task workflow.
''',
8:'''### Study F checks and claim boundaries

The first headless route exposed three public progress/completion records; it does not expose a complete tool trace. Its no-run statement is requested and self-reported. The separate normal-stream observation contains 117 events, including one `build_flow` tool-start, one `set_flow` update, and completion. No `run_flow` or `generate_component` tool-start appears in that recorded stream. This supports a bounded trace statement; pipeline success/verified fields are not task-success evidence.

The interpreter checker compares actual native occurrence/type identities, every wire/port, static type overlap, induced internal edges, exact cut exports, public endpoint existence, nonduplicating primary membership, handoffs and obligation inheritance. The first analyst proposal failed one of49checks because a composite's human-authority obligation was absent from its parent flow. The process retained it. A new proposal version restores inheritance; the raw graph and original interpretation remain unchanged. The revised proposal passes 51 checks, and ten targeted corruptions are rejected by two test methods. The reviewer also found that empty coverage rows passed the earlier checker. The final two added assertions retain the declared original-task row set and unique row identities; this checks retention of an authored segmentation, not semantic completeness. Counts describe internal engineering coverage, not a general validator or statistical accuracy estimate.

Source hashes establish that 13 selected local files stayed stable during the normal-stream window; they do not attest every loaded dependency or pristine upstream provenance. Existing local source changes predate this experiment. Application storage/user isolation is distinct from the notebook deny-default OS policy. Initial filesystem tools used their default base with a fresh authenticated namespace; the retained launcher subsequently specifies a private base for future requests. No filesystem tool-start appears in the normal-stream trace. No generated component/provider behavior or human approval was tested.
''',
9:'''### Study F observations — what the unchanged builder chose

| Observation | First private headless output | Separate normal-stream output |
|---|---|---|
| Native component types | ChatInput, Agent, Agent, ChatOutput | Same type-level sequence, different occurrence IDs |
| Recorded wires | Three named-port Message-compatible edges | Three edges in a proposed graph |
| Model settings | OpenAI/model selection saved on both Agents | Saved model selections; availability untested |
| Application semantics | Persisted in private backend database | Proposed for review; not added to active user canvas |
| Tool observability | Three public progress/completion events |117events; observed tool start: build_flow |

The first builder configured drafting and critique instructions rather than merely adding role labels. In particular, the drafter is instructed to reproduce ORIGINAL TICKET for the reviewer. This is an observed instruction-level design choice, not guaranteed faithful copying or an independent source path. The original task did not explicitly demand an independently preserved second path; imposing that later as a failed original requirement would be retrospective strengthening. Provisional category/urgency choices are assumptions, not approved organizational policy. Presentation for human consideration is not an implemented approval/audit process.

Exact recorded source-graph comparisons find ChatInput.message→Agent.input_value in 345 distinct graph objects, Agent.response→Agent.input_value in 63, and Agent.response→ChatOutput.input_value in 439. The full incident signatures of the draft/review neighborhoods coexist at a single recorded center in 48/43 distinct graph objects. Full support IDs and example sources are retained. Related designs/mirrors may remain; frequency establishes neither independence, purpose, safety nor mined-guidance benefit.

The research collaborator proposes two composite boundaries, a coordination Flow and an accountable Process over those actual IDs. An alternative single reviewed-suggestion composite contains all four occurrences. Current evidence cannot choose the superior reusable boundary. Upper-plane packaging is analyst-authored, not an output the stock builder produced. The corrected 51-check interpretation preserves that uncertainty and its unresolved resource, instruction, source, policy, retention, behavior, control and authority obligations.
''',
12:'''### Study F threats and limits

Two authored development requests with the same task are not generalization evidence. The second stream improves observability but must not supply missing trace evidence retroactively to the first run. The subject is the existing local implementation configured through the usual provider interface, not a clean-upstream benchmark or proof that every request is produced exactly. Source-file stability is weaker than a complete loaded-process attestation.

The source copier and drafter are the same model stage. Instructions to echo evidence may omit, alter or truncate it; no task execution measured those failures or established fidelity. Conversely, an independent-source route and organizational approval system were not mandatory in the original request. They are important prospective conditions for stronger claims, not reasons to falsify a weaker request after seeing the graph.

The corpus comparison is descriptive and exact-name/port based; no alias expansion, representative sampling, causal claim or guidance intervention is made. The analyst grouping has a plausible one-composite alternative, and configured role prompts do not establish reusable purpose. The finite interpreter checker omits many semantic, dynamic-field, cardinality, concurrency and operational-safety properties. A structural pass cannot promote runtime, human or policy gates. The generated graph, analyst interpretation and proposed higher-layer system are three different evidence objects.
''',
14:'''### Study F orchestration and review record

The research collaborator first criticized the protocol, then inspected frozen raw output and separated prompt-level semantics from behavior, proposed boundary alternatives, revised a checker-identified inheritance omission, and synthesized the results before writing the question/conclusion. The coordinator retained raw native artifacts, performed exact corpus comparisons, authored a separate checker and fault tests, and integrated checked text/code. An internal source reviewer verified the native route and source-stability scope and identified configuration/trace evidence requirements. This is AI-assisted internal review, not external academic peer review.

Reproduce the saved recount with the existing research Python environment and `stock-builder/build_notebook.py`; run the two interpreter tests through Python unittest. `run_stock.py` and `run_stream.py` make genuine new model requests and are separate from the recount. `services/paper6-assistant/run_stock_backend.sh` launches the unchanged local backend with private storage settings and the usual provider connection. Its later explicit filesystem-base setting is documented separately from initial observations. Never overwrite original graph/events to repair an interpretation.

Primary local sources: the unchanged experiment factory at `langflow/agentic/flows/flow_builder_assistant.py`; standard route in `agentic/api/router.py`; headless persistence in `agentic/utils/assistant_runner.py`; and native builder tools. Exact locations/manifests and qualification are in `stock-builder/PROVENANCE-REVIEW.md`. Studies A–E, the original abstract, prior negative results and Study D's acceptance disagreement remain preserved. No new GitHub publication or task deployment is claimed.
'''
}
def main():
 ws=Workspace();old=json.loads(PAPER.read_text());oldcode=[c for c in old['cells'] if c['cell_type']=='code']
 for number,text in ADDITIONS.items():
  c=ws.section(number);ws.write_section(number,c['markdown'].rstrip()+'\n\n<!-- stock-subject-study-f -->\n'+text,c['revision'])
 numbers=ws._load('draft-base.json',{})['changedSections']
 for number in numbers:
  prior=next(''.join(c['source']) for c in old['cells'] if ''.join(c['source']).startswith(f'## {number}. '));assert ws.section(number)['markdown'].startswith(prior)
 ws.publish_checked_sections(numbers);n=json.loads(PAPER.read_text());extra=json.loads((BASE/'stock-results.ipynb').read_text())
 assert not any(c.get('metadata',{}).get('paper6_stock_study_f') for c in n['cells'])
 for c in extra['cells']:c.setdefault('metadata',{})['paper6_stock_study_f']=True
 index=next(i for i,c in enumerate(n['cells']) if ''.join(c['source']).startswith('## 8. '));n['cells'][index:index]=extra['cells']
 status=next(c for c in n['cells'] if ''.join(c['source']).startswith('### Current study status'));status['source']=(''.join(status['source'])+'\n\n**Study F correction:** A separate unchanged local Langflow Assistant now receives natural-language tasks without a component/wiring recipe. Two raw native API observations are preserved. Research interpretation and independent structural checking follow generation; they do not rewrite it. The first 49-check interpretation exposed one inherited-obligation omission; a new interpretation version passes while retaining higher-plane proposals and behavioral unknowns. The executed Study F cells distinguish subject output, corpus comparisons and analyst packaging.\n').splitlines(keepends=True)
 assert n['cells'][0]==old['cells'][0];assert [c for c in n['cells'] if c['cell_type']=='code' and not c.get('metadata',{}).get('paper6_stock_study_f')]==oldcode
 atomic(PAPER,json.dumps(n,indent=1));atomic(ws.root/'paper-draft.ipynb',PAPER.read_text());atomic(ws.root/'draft-base.json',json.dumps({'canonicalSha256':sha(PAPER.read_bytes()),'changedSections':[]}));ws.event('stock_subject_study_merged',sha256=sha(PAPER.read_bytes()),cells=len(extra['cells']))
 print('Merged Study F, preserving',len(oldcode),'prior code cells/outputs and original abstract')
if __name__=='__main__':main()
