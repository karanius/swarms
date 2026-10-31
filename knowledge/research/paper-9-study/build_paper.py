from pathlib import Path
import json,hashlib,base64
import nbformat as nb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
OUT=ROOT/'knowledge/research/notebooks/Paper 9 - JSON Market Intelligence Instance.ipynb'
s=json.loads((D/'market-intelligence.instance.json').read_text())
c=[]
def md(x):c.append(nb.v4.new_markdown_cell(x))
def code(x):c.append(nb.v4.new_code_cell(x))
md('''# Paper 9 — Building the Market Intelligence Instance in JSON
## Contract-first specification, complete dataflow and lifecycle verification
**30 October 2026 · Revision 2: local implementation bound and exercised; business validity unproven**

### Abstract
Paper 8 established the purpose and five-plane architecture of a Market Intelligence instance, but its JSON left source discovery, data routing, review, costs, state guards and artifact typing underspecified. Paper 9 develops a versioned JSON instance contract with explicit capability ports, producer-to-consumer bindings, typed artifact schemas, evidence-decision policies, review authority, persistence requirements and revision-aware lifecycle rules. A local validator checks the declared design and uses controlled fault cases to expose incomplete bindings and unsafe acceptance. The instance remains within Paper 7's unified Operations plane. Revision 2 binds all eleven composites to real pinned native PythonFunction wrappers and explicit trusted local resources, implements the JSON-driven controller and persistence, and exercises public retrieval and existing local-model inference. This is a local review-gated implementation, not a remotely authenticated production service. The live probe remains an insufficient policy-evidence dossier; no market demand, profitable niche or commercial value is established.

**Deliverables:** canonical parameterized instance JSON; typed schemas; eleven compiled native composite wrappers; concrete controller, storage, review and handoff resources; a local CLI; controlled checks and native runtime evidence. **Non-deliverables:** public activity, purchases, account changes, a deployed Content Strategy consumer, multi-user authentication or business validation.''')
md('''## 1. Research question, hypotheses and falsification
**Question:** Can the proposed Market Intelligence instance be specified precisely enough that builders need not invent its external behavior when selecting and wiring its internals?

| Hypothesis | Supporting design evidence | What would challenge it |
|---|---|---|
| H1: complete handoffs | Every required input has a declared, type-compatible producer available before use | Unbound inputs, invented observer outputs, impossible ordering |
| H2: honest evidence | Schemas and review policy distinguish sources, observations, candidate claims and judgments | Supported claims without evidence; inaccessible data converted to zero demand |
| H3: bounded lifecycle | Explicit authority, limits and revision gates block unsupported transitions | A missing setting or string 'true' grants access; retry loops escape caps |
| H4: builder preparation | Each composite has a bounded contract, pinned native wrapper and concrete resource implementation | Builder must guess source discovery, who approves, or how outputs are accepted |

Passing structural checks supports only the stated representation properties. It cannot prove reasoning quality, access-policy enforcement, storage consistency or profitable audience opportunities. A simpler manual process remains a meaningful future comparison.''')
md('''## 2. Audit findings carried forward from Paper 8
| Paper 8 gap | Paper 9 treatment | Residual proof still needed |
|---|---|---|
| Source locations appeared without a producer | Source discovery produces a screened candidate batch | Real search/retrieval adapters and quality evaluation |
| Flow arrows without explicit routing | Named typed ports and exact artifact bindings | Runtime delivery, retries and persistence |
| Claims were judged without explicit claim-formation responsibility | Separate candidate-claim formation and evidence judgment | Real entailment and scope review |
| Assembly stood in for review and handoff | Separate reviewer and versioned handoff contracts | Actual role separation and consumer acknowledgment |
| Costs consumed but not generated | Cross-cutting attempt observer produces cost ledger snapshots | Real timing, tariff, allocation and failure records |
| Record names without data types | Closed JSON Schema artifact definitions and conditional requirements | Cross-artifact identity/content verification and runtime enforcement |
| Lifecycle largely prose | States, events, actors, guards, exception and revision routes | Actual orchestrator semantics and crash recovery |
| Inconsistent business reference | Uses Paper 7's canonical business identity | Future integration test against registry |
| Component internals absent | Eleven pinned native wrappers and named versioned resources now bound | Continued qualification on changed catalog/model/runtime |

The Paper 8 notebook and its JSON remain historical design evidence, unchanged. Paper 9's JSON is the new working contract; it is not silently substituted into old diagrams.''')
md('''## 3. Instance and process contracts
The instance investigates a bounded audience problem and competing solutions for Content Strategy. It recommends continue, narrow, ask, stop or insufficient; it does not autonomously adopt a business or publish/spend.

| Process | Responsibility | Owner role | Important boundary |
|---|---|---|---|
| Governance | Brief, authority and plan | Intelligence owner | Unresolved scope/limits block acquisition |
| Investigation | Discovery, evidence, alternatives, candidate claims and judgment | Intelligence owner | Accessible source evidence is not purchase behavior |
| Review/handoff | Dossier, independent review and acknowledged delivery | Evidence reviewer / declared stage actors | No self-approval or implicit consumer acceptance |
| Refresh/revise | Impact trace and approved child revision | Intelligence owner | Old evidence and unrelated artifacts remain stable |
| Stewardship | Every attempt's costs, access and privacy events | Operations owner | Failed/retried work is not free or invisible |

Roles are bound by the trusted local request interface: the engine authors artifacts and a separately named reviewer submits explicit decisions. These workflow checks are not remote authentication and do not imply independently credentialed human experts. The review process contains separately attributed actions; the lifecycle specifies the actor role for review decisions.''')
code('''from pathlib import Path
import json,sys
from IPython.display import display, JSON
import pandas as pd
repo=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/"knowledge/research/paper-9-study/market-intelligence.instance.json").exists())
study=repo/"knowledge/research/paper-9-study"
sys.path.insert(0,str(study))
from validate_contract import load_spec,load_schema,validate_spec,activation_blockers,validate_artifact,guard_allows,validate_review_acceptance
spec=load_spec()
print("This cell reads the implemented tower specification. It does not start a new live investigation; real probes are recorded separately.")
display(JSON(spec,expanded=False))''')
md('''## 4. Flow contracts and exact data dependencies
A binding identifies an external input, an earlier node output, or the cross-cutting observer. This prevents a graph from looking complete while relying on undeclared information. The displayed order is a proposed schedule; independent work may be parallelized later only if dependencies and budgets remain respected.

The investigation flow goes from intake through discovery, retrieval, normalization, comparison, claim formation, assessment, assembly, review and handoff. Refresh is a separate flow, requiring a parent dossier and change notice. Its output requests a new approved investigation revision; it does not wire a same-version cycle.

Empty evidence is permitted as data, with an insufficient or blocked result. A connector failure must not prevent recording the failure and cost. It must not be converted into a claim of no market demand.''')
code('''pd.set_option("display.max_colwidth",None)
pd.set_option("display.max_rows",100)
composites={x["id"]:x for x in spec["composites"]}
rows=[]
for flow in spec["flows"]:
 for node in flow["nodes"]:
  comp=composites[node["composite_ref"]]
  rows.append({"Flow":flow["id"],"Stage":node["id"],"Capability":comp["name"],"Inputs":json.dumps(node["bindings"]),"Outputs":json.dumps(comp["output_ports"]),"Gate":node.get("additional_gate") or node["entry_gate"]})
display(pd.DataFrame(rows))''')
# diagram: one complete sequence plus cost and policy context; generated from canonical JSON.
fig,ax=plt.subplots(figsize=(14,11),facecolor='#111b26');ax.set_facecolor('#111b26')
for i,node in enumerate(s['flows'][0]['nodes']):
 y=10-i*.88;comp=next(c for c in s['composites'] if c['id']==node['composite_ref'])
 ax.add_patch(FancyBboxPatch((.5,y),7.4,.65,boxstyle='round,pad=.02',facecolor='#263e54',edgecolor='#79b6af'))
 ax.text(4.2,y+.33,comp['name'],ha='center',va='center',color='#edf8f9',fontsize=12,weight='bold')
 if i<9:ax.annotate('',xy=(4.2,y-.2),xytext=(4.2,y-.04),arrowprops={'arrowstyle':'->','color':'#85beb6','lw':1.4})
ax.add_patch(FancyBboxPatch((8.5,6.7),4.5,3.6,boxstyle='round,pad=.03',facecolor='#20494d',edgecolor='#91c9bd'))
ax.text(10.75,9.8,'EVERY STAGE',ha='center',color='white',fontsize=13,weight='bold')
ax.text(10.75,8.5,'Attempt/cost observer\n\nAccess and budget checks\n\nVersioned evidence records\n\nFailure, retry and cancellation',ha='center',va='center',color='#d4e9ed',fontsize=11)
ax.add_patch(FancyBboxPatch((8.5,3),4.5,2.6,boxstyle='round,pad=.03',facecolor='#263e54',edgecolor='#79b6af'))
ax.text(10.75,5.1,'REFRESH FLOW',ha='center',color='white',fontsize=13,weight='bold')
ax.text(10.75,4.1,'Parent dossier + change notice\n↓\nImpact and revision request\n↓\nNew approved brief/revision',ha='center',va='center',color='#d4e9ed',fontsize=11)
ax.text(6.7,.7,'One Operations plane • five internal planes • eleven pinned native wrappers • concrete local resource bindings',ha='center',color='#bdd9df',fontsize=10)
ax.set_xlim(0,13.5);ax.set_ylim(.2,11.2);ax.axis('off');ax.set_title('Market Intelligence instance • declared JSON contract flow',color='white',fontsize=17,weight='bold',pad=18)
fig.tight_layout();im=D/'json-contract-flow.png';fig.savefig(im,dpi=140,facecolor=fig.get_facecolor(),bbox_inches='tight');plt.close(fig)
pic=nb.v4.new_markdown_cell('![Paper 9 JSON contract flow](attachment:json-contract-flow.png)');pic.attachments={'json-contract-flow.png':{'image/png':base64.b64encode(im.read_bytes()).decode()}};c.append(pic)
md('''## 5. Composite interfaces, component grounding and configuration
The canonical JSON contains eleven composite interface contracts. Each names required inputs, outputs, responsibility and acceptance policy. All eleven internal graph references and native occurrence references are populated. Each native PythonFunction wrapper invokes named trusted local resource code through a validated run/stage interface. Resource implementations are explicit; they are not falsely labeled native Langflow blocks. The raw native definitions are unchanged. Exported graph defaults require a real run identifier from the factory, just as a function requires its input arguments. The earlier capability labels are superseded by a more explicit contract set in this paper.

| Plane | What is specified now | What is intentionally unresolved |
|---|---|---|
| Processes | Five responsibilities and local role/decision checks | Per-investigation owner and reviewer identities are request parameters |
| Flows | JSON-driven controller, scoped checkpoints, review pause/resume and revision path | External source availability and supplied research scope |
| Composites | Eleven concrete resource bindings and compiled native wrappers | Meaningful output still depends on actual evidence and review |
| Components | Eleven occurrences of the real native PythonFunction primitive plus pinned resource files | Native/model changes require requalification |
| Configuration | Concrete runtime/storage policies and typed parameter resolver | Audience, question, sources and reviewer are normal per-run inputs, not guessed business choices |

The JSON is a parameterized implementation, not a preselected market investigation. The example request resolves into a complete typed activation configuration below. Missing/invalid request fields block collection. Authored defaults and boundaries are disclosed: sequential retrieval, bounded public-source access, zero paid-service spending, local inference, explicit review, and retained run state until owner cleanup. Unknown electricity and human economic costs remain unknown; a zero direct-spend policy is not a claim of zero economic cost.''')
code('''errors=validate_spec(spec)
assert errors==[], errors
print("Design reference/type/ownership validation errors:",errors)
sys.path.insert(0,str(study/"implementation"))
from configuration import resolve
from validate_contract import validate_activation
request=json.loads((study/"implementation/request.example.json").read_text())
activation=resolve(spec,request)
assert validate_activation(activation)==[]
display(JSON(activation,expanded=False))
print("Example request resolves and passes the activation schema. It is an implementation-probe question, not the user-selected market.")''')
md('''## 6. Artifact schemas and provenance
Artifact definitions use JSON Schema 2020-12 with required fields, closed object properties, explicit arrays/enums, timestamps and conditional requirements. A retrieved source requires a snapshot reference and hash; failed retrieval retains a reason. Supported judgments require evidence, an entailment review and reviewer reference. Acknowledgment requires an acknowledgment record.

These constraints establish record shape, not truth. A validator can require a source reference, but only an artifact registry and inspection can show that the source exists and supports a claim. Conditional 'accepted review' schema checks are supplemented by the complete critical-review rubric check.

| Record group | Purpose | Additional semantic obligation |
|---|---|---|
| Brief/plan/discovery | Scope, query intent and candidate screening | Allowed source/access and bounded search coverage |
| Source/evidence | Actual source capture, observation context, transformations and dependence | Resolve every reference and preserve raw evidence |
| Alternatives/candidate claims/assessments | Separate proposals from judgments | Entailment, scope and contradictory evidence review |
| Dossier/review/receipt | Decision-ready report and attributable acceptance | Exact revision match, reviewer authority and acknowledgment |
| Costs/obligations/change/impact/revision | Honest limits, accounting and controlled change | Real events, no duplicated costs, approved immutable revisions |

The record contracts retain unknown amounts, uncertain independence and empty evidence without inventing values. No source URL is treated as an immutable snapshot. A separate activation schema rejects unresolved or wrongly typed limits and requires real role/runtime bindings; passing this schema still cannot prove that those bindings are authorized or functional. External metrics require source-preserved units/period/context; extending metric-specific schema is required before accepting analytics as a direct connector input.''')
code('''schemas=load_schema()
from jsonschema import Draft202012Validator
Draft202012Validator.check_schema(schemas)
display(pd.DataFrame([{"Artifact type":k,"Required payload fields":", ".join(v["properties"]["payload"]["required"])} for k,v in schemas["$defs"].items()]))
print("Artifact schema grammar valid. Cross-artifact facts and source truth remain separate checks.")''')
md('''## 7. Evidence and decision mechanism
| Stage | Proposed decision procedure | What it cannot infer |
|---|---|---|
| Discover | Run accepted support, counterevidence and existing-solution queries; record candidates/exclusions/limits | Search rank is not demand |
| Normalize | Preserve source and context; record unit/period and reversible transform | A parsed value is not necessarily meaningful |
| Group sources | Flag exact duplicates; review family/syndication links; preserve unknown dependence | Many pages do not imply many independent sources |
| Form claims | Explicitly label observation, inference or hypothesis, with references and scope | Candidate wording is not established fact |
| Assess | Supported, contradicted, mixed, insufficient, stale or inaccessible with reasons | A numeric score or majority vote cannot establish truth |
| Review | Verify provenance, entailment, counterevidence, dependence, scope, costs and privacy | Separate model contexts do not guarantee independent judgment |
| Recommend | Continue/narrow/ask/stop/insufficient within brief and evidence limits | No automatic profitable-niche selection |

Detailed acceptance policies are in the instance JSON. Human or model reviewers must record reasons; factual entailment and material contradictions remain judgment tasks requiring empirical evaluation. Schema checks cannot replace them. This paper does not invent a universal confidence threshold or calibrate unsupported probabilities.''')
md('''## 8. Lifecycle, authority, failure and recovery
The JSON specifies states, events, actor roles, guard references and cross-cutting exception routes. Guard context is Boolean evidence supplied by named systems: configuration/authority/registry/budget/review records. Missing values and text such as 'true' do not grant permission. The local controller enforces type/reference checks, deadline/cancellation, checkpoints, reviewer identity/revision checks, and stage leases. Local trusted callers supply review decisions; this is not an authentication boundary against code running as the same OS user.

| Situation | Required outcome |
|---|---|
| Missing scope | Clarification obligation; no collection |
| Limit/access failure | Record attempt/cost and block; no authorization bypass |
| Retrieval unavailable | Retain failure; allow qualified insufficient output |
| Review fails | Reject or request a child revision; preserve submission |
| Delivery fails | Preserve accepted dossier; bounded duplicate-safe retry |
| New evidence | Impact report, approved new brief and immutable child revision |
| Cancellation | Propagate to leased work, record partial costs and artifacts |

The dossier carries a cost snapshot through assembly. Review and delivery add more cost, so the final run ledger must be linked separately at closure. Do not silently mutate the accepted dossier or pretend its earlier snapshot includes later work. SQLite implements immutable artifacts, compare-and-swap run updates, append-only events, stage leases and a duplicate-safe local outbox. Review waiting pauses the remaining active budget without replenishing it. Structured reviewer feedback creates a child run with reviewed assessments and a reasoned continue/narrow/ask/stop/insufficient recommendation; a continue decision requires at least one supported reviewed claim. Parent artifacts are never overwritten. Cancellation blocks subsequent stages; an in-flight blocking call ends within its timeout. Consumer notifications are local outbox records, not a claim that another instance is already deployed.''')
code('''keys=spec["guards"]["runtime_ready"]["all"]
examples=[("No runtime evidence",{}),("Partial evidence",{keys[0]:True}),("Text is not authority",{k:"true" for k in keys}),("All Boolean fixture inputs",{k:True for k in keys})]
display(pd.DataFrame([{"Controlled example":name,"Guard allows":guard_allows(spec,"runtime_ready",ctx)} for name,ctx in examples]))
print("Fixture inputs only: the final row is not evidence that the real instance is authorized or operational.")''')
md('''## 9. Verification protocol and controlled results
The checks inspect schema grammar, dataflow producer/type/order, process ownership, cost observer coverage, guard references and selected record invariants. Mutation cases deliberately remove discovery, change types, remove review/cost producers, introduce unknown ownership and try to enable business side effects. Record cases test unsupported judgments, incomplete review, missing snapshots and false acknowledgments.

These cases were authored alongside the contract. They are development checks, not held-out evaluation or proof of universal correctness. The notebook reruns the suite below and reports real pass/fail output. No network source, business agent or market experiment is called.''')
code('''import unittest
suite=unittest.defaultTestLoader.discover(str(study),pattern="test_contract.py")
result=unittest.TextTestRunner(verbosity=1).run(suite)
assert result.wasSuccessful(),"Contract checks failed"
print(f"Controlled contract checks: {result.testsRun}; failures: {len(result.failures)}; errors: {len(result.errors)}")''')
md('''## 10. Audit-to-contract conclusion and remaining work
Paper 9 closes the identified *specification* gaps with declared producers, explicit port bindings, separate discovery/claim/review/handoff roles, cost-observer requirements, typed records, guard contexts and revision routes. That is stronger preparation than the Paper 8 outline. It is now a concrete parameterized local implementation package. It is not a fully autonomous or commercially validated business system.

| Readiness boundary | Current result | Next evidence |
|---|---|---|
| JSON design consistency | Typed routing and actual bound-resource hashes checked | Independent audit and changed-environment qualification |
| Artifact shape | Typed schemas and selected checks | Cross-artifact registry/content verification and connector-specific payloads |
| Native grounding | Eleven graphs compiled; all eleven capability wrappers exercised | No full GUI import/run claim; catalog/model changes require new proof |
| Local orchestration | Controller, storage, cancellation, review and local handoff implemented and checked | Broader reliability and multi-user deployment require separate qualification |
| Research quality | Untested | Independent evidence/reviewer cases and manual reference comparison |
| Commercial usefulness | Untested | Audience/strategy decisions and later observed outcomes |

The next use step is to supply a genuine research brief, permitted sources, limits and reviewer. Those inputs do not require inventing missing internals. They do not make the resulting conclusions automatically correct. Public-search capability is optional; the recorded live probe used an explicitly bounded source catalog. More tests of the schema alone cannot establish that the instance performs good market intelligence.

## 11. References and review disclosure
Internal bases: Paper 7's business/Operations model; Paper 8's instance design and audit findings. The JSON Schema dialect is declared in the schema file. No new literature or primary market sources were retrieved for this design task. No external academic peer review is claimed. All checks are local authored engineering verification; judgments of source truth, independence and opportunity remain future evaluation work.

## 12. Full machine-readable deliverables
The instance and artifact schemas are repository files alongside this paper's authoring and validation code. The instance is also displayed above as an expandable object. The following frozen snapshot provides an inspectable full copy of the JSON at this revision. Changing the canonical file later does not retroactively change this recorded snapshot.''')
md('''## 13. Implementation evidence and qualification boundaries
The previous contract-only notebook is preserved under revisions. The current source bindings refer to concrete files and exact hashes. Real native PythonFunction executions traverse the JSON-driven stages; the local model has no tools or code authority, and its exact quotations are checked against captured text.

The live probe retrieved two official documents and used the existing local model. The coordinator accepted the result only as an honest **insufficient implementation-probe dossier**. Local outbox acknowledgment and refresh triggering were controlled mechanism checks, not a live Content Strategy deployment or observed external source change. Independent market evidence and business value remain unproven.

Twenty-four implementation checks cover runtime fixtures alongside the twenty-one original contract checks. A controlled positive feedback case verifies that the system can progress beyond insufficient; wrong-revision feedback and unsupported continue recommendations are rejected. The live policy probe itself remains insufficient. The first live retrieval attempt hit its byte cap; it remains recorded, and the later bounded profile used a larger explicit cap. A review-wait regression was found and fixed before the final qualification.

This closes concrete implementation placeholders within the documented local review-gated operating profile. It does not justify a universal claim of '100% correct market intelligence,' unrestricted internet coverage, autonomous human judgment or production security. Source scope and accountable review are real inputs, not silently fabricated values.''')
code('''import unittest
runtime_suite=unittest.defaultTestLoader.discover(str(study/"implementation"),pattern="test_*.py")
runtime_result=unittest.TextTestRunner(verbosity=1).run(runtime_suite)
assert runtime_result.wasSuccessful()
print("Implementation fixture checks:",runtime_result.testsRun)
for name in ["native-execution-proof.json","tower-native-probe.json","native-complete-proof.json"]:
 display(JSON(json.loads((study/name).read_text()),expanded=False))
print("Native evidence is recorded; this cell does not repeat network retrieval or model inference.")''')
md('```json\n'+json.dumps(s,indent=2)+'\n```')
book=nb.v4.new_notebook(cells=c,metadata={'kernelspec':{'name':'research-python','display_name':'Research Python','language':'python'},'language_info':{'name':'python'},'paper9':{'status':'local-implementation-bound','market_research_run':False,'native_graph_built':True,'full_langflow_gui_run':False}})
nb.validate(book);nb.write(book,OUT)
print(OUT)
