"""Notebook composition of the authored whole-business design."""
def add_sections(md,code):
 md('''## 6. Whole-business architecture: seven instances, shared planes
The business is represented as a **system of specialized instances**. Each instance has the same five internal planes: Configuration, Components, Composites, Flows and Processes. The business itself is an enclosing scope, not a renamed content-production instance. **Operations** coordinates these instances; it is not asserted as an additional universal plane or a separate eighth specialist. This domain model is an authored proposal to test, not a discovered natural hierarchy.

The distinction is responsibility: Market Intelligence discovers needs; Content Strategy chooses what to address; Production makes artifacts; Distribution manages channel/release state; Monetization manages revenue routes; Audience Care handles trust and service; Finance and Performance accounts for costs and results. They share evidence and goals without sharing unrestricted control.

| Business lifecycle | Responsible instance | Evidence / outgoing result | Important boundary |
|---|---|---|---|
| Discover a problem | Market Intelligence | Dated opportunity dossier, contrary evidence and uncertainty | Popularity is not demand or payment |
| Decide the promise | Content Strategy | Prioritized viewer outcome and acceptance rubric | Commercial pressure cannot replace editorial usefulness |
| Make the artifact | Production | Private release package, provenance and total attempt cost | Rendering does not prove value |
| Reach the audience | Distribution | Authorized release receipt and metric snapshots | Publication disabled in this study |
| Capture value | Monetization | Eligible route, relevant offer and attributable receipt claim | No eligibility or revenue assumed |
| Maintain trust | Audience Care | Feedback, corrections, optional product support and resolutions | Written asynchronous contact can remain |
| Reconcile and learn | Finance and Performance | Actual costs, reconciled receipts and decision reports | Estimated revenue, payable balance and received cash stay separate |
| Coordinate the whole | Operations | Priorities, caps, approvals and versioned decisions | Coordinates specialists; does not bypass their checks |

**Shared invariants:** original useful content; no calls/meetings by design; local media generation; lawful source/asset use; real event records; explicit unknowns; no automatic publication, purchase or account changes. Online research, distribution and payments are not claimed to run locally. Native Langflow definitions remain unchanged; external local programs need real adapters or resource references.''')
 code('''from pathlib import Path
import sys, json
from IPython.display import display, JSON
import pandas as pd
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_rows", 100)
repo=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/"knowledge/research/paper-7-study/business_system.py").exists())
study=repo/"knowledge/research/paper-7-study"
sys.path.insert(0,str(study))
from business_system import make_system, validate_system
business_system=make_system()
issues=validate_system(business_system)
assert not issues, issues
print("Design consistency only: seven instances, five shared planes and explicit handoff contracts. No production or business success tested.")
display(pd.DataFrame([{"Instance":i["name"],"Owns":i["mandate"],"Consumes":i["inputs"],"Produces":i["outputs"]} for i in business_system["instances"]]))
''')
 md('''### 6.1 Every instance contains the same planes
The following matrix defines proposed contents, not deployed capabilities. Every Components cell remains unresolved until exact native catalog identities, port types and adapter resources are verified. A phrase such as “feedback triage” is a capability contract, not an invented Langflow component. Domain processes may cross instance boundaries through contracts; local component wires do not substitute for business handoffs.

Shared definitions live in the library. A component occurrence belongs to one instance and references a pinned definition; the same definition may be used by multiple occurrences without collapsing their configurations, state or evidence. Resource/model weights are referenced, not copied into every instance. Secrets stay outside notebooks.''')
 code('''plane_rows=[]
for i in business_system["instances"]:
 p=i["planes"]
 plane_rows.append({"Instance":i["name"],"Configuration":p["configuration"]["proposed"],
 "Components":p["components"]["status"],"Composites (proposed)":p["composites"]["proposed_capabilities"],
 "Flows (proposed)":p["flows"]["proposed"],"Processes (proposed)":p["processes"]["proposed"]})
display(pd.DataFrame(plane_rows).melt(id_vars=["Instance"],var_name="Plane",value_name="Proposed contract").sort_values(["Instance","Plane"]).reset_index(drop=True))
display(JSON(business_system,expanded=False))''')
 code('''# Authored architecture figure, not a learned cluster or native graph.
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
fig,ax=plt.subplots(figsize=(14,8))
positions={"market-intelligence":(0,4),"content-strategy":(4,4),"production":(8,4),
"audience-care":(0,1.7),"finance-performance":(4,1.7),"distribution":(8,1.7),"monetization":(4,-.6)}
for i in business_system["instances"]:
 x,y=positions[i["id"]]
 ax.add_patch(FancyBboxPatch((x,y),3.3,1.25,boxstyle="round,pad=.05",facecolor="#eef5fa",edgecolor="#35576b"))
 ax.text(x+1.65,y+.88,i["name"],ha="center",fontsize=10,weight="bold")
 ax.text(x+1.65,y+.36,"Config · Components · Composites\\nFlows · Processes",ha="center",fontsize=8)
# Core value path, and feedback path. Detailed contracts in the table below.
for a,b,color in [("market-intelligence","content-strategy","#176b67"),("content-strategy","production","#176b67"),
("production","distribution","#176b67"),("distribution","finance-performance","#176b67"),
("finance-performance","content-strategy","#a76422"),("audience-care","market-intelligence","#a76422"),
("distribution","audience-care","#a76422"),("monetization","finance-performance","#176b67")]:
 xa,ya=positions[a];xb,yb=positions[b]
 ax.annotate("",xy=(xb+1.65,yb+.65),xytext=(xa+1.65,ya+.65),arrowprops={"arrowstyle":"->","color":color,"lw":1.7,"shrinkA":45,"shrinkB":45},zorder=0)
ax.text(5.6,6.1,"OPERATIONS: shared intent · budgets · approvals · revisions · exceptions",ha="center",fontsize=12,weight="bold")
ax.text(5.6,-1.25,"Selected handoffs shown; full contracts below. Feedback creates new revisions. All seven instances are DESIGN ONLY.",ha="center",fontsize=9)
ax.set_xlim(-.3,11.8);ax.set_ylim(-1.5,6.7);ax.axis("off");plt.tight_layout();plt.show()''')
 md('''### 6.2 Inter-instance handoffs: contracts rather than vague arrows
Every handoff references an immutable artifact revision. The consumer records acceptance, rejection or an unresolved obligation; a successful send is not successful consumption. Duplicate delivery must not duplicate a release, refund or counted receipt. Proposed idempotency keys and state transitions require implementation proof later.

| Common envelope field | Meaning |
|---|---|
| business / instance / artifact identity | Enclosing business, producing occurrence and stable artifact lineage |
| revision / schema version | Exactly what was supplied and which contract applies |
| status / acceptance record | Proposed, checked, approved, rejected, superseded or blocked; who checked what |
| source references / creation time | Evidence lineage, provenance, freshness and real event time |
| owner / idempotency key | Accountable domain and duplicate-delivery identity |
| access classification | Public evidence versus restricted account/customer data; minimize retained personal data |

Optional product transactions include external identifiers, not payment credentials. Customer records are not copied into research or production prompts by default. The contract describes intended data exchange; no message bus, queue, database or integration has been built here.''')
 code('''display(pd.DataFrame([{"Contract":h["id"],"From":h["from"],"To":h["to"],"Artifact":h["artifact_type"],"Acceptance":h["acceptance"],"On rejection":h["rejection"]} for h in business_system["handoff_contracts"]]))''')
 md('''### 6.3 Operations: coordination, authority and shared services
| Concern | Domain ownership | Operations responsibility | Authority boundary |
|---|---|---|---|
| Purpose / priorities | Strategy proposes, Intelligence supplies evidence | Reconcile competing goals and approve a bounded portfolio | No invented demand or income target |
| Budget / capacity | Finance computes, Production reports measured load | Reserve time/cash envelopes and prioritize work | Unknown cap blocks commitment; no spending enabled |
| Release | Production supplies QA, Distribution verifies channel constraints | Route explicit publication authorization | Current release authority disabled; no side effect from a diagram |
| Offers / product changes | Monetization owns terms; Audience Care supplies issues | Resolve commercial/editorial conflicts | No endorsement without actual evidence; no silent support commitments |
| Corrections / incidents | Audience Care triages; affected domain repairs | Pause affected work and coordinate a new version | Preserve old evidence; do not erase an incident by overwriting |
| Financial exceptions | Finance reconciles; Monetization supplies transaction claims | Escalate mismatch, refund or cash shortfall | Refund/payment/account actions require appropriate human authority |
| Shared technical resources | Each domain declares resource needs | Prevent competing unbounded GPU jobs, prioritize and cancel safely | Scheduling proposed; not implemented |
| Governance / rights | Every domain supplies evidence for its artifacts | Maintain policies, license registry and access boundaries | A source URL alone is not rights clearance |

Shared services are capabilities, not extra uncounted business instances: evidence/provenance store, immutable artifact/version registry, access controls, execution/event logs, resource scheduler and policy/rights registry. Each needs a real owner and implementation contract before use. Seven is an initial partition to investigate, not a theorem that every business needs seven instances.

### 6.4 Business state and iterative development
| Business phase | Permitted work in this design | Exit evidence | Failure route |
|---|---|---|---|
| Designed (current) | Research, contracts and hypothetical economics | Coherent provisional plan and explicit unknowns | Revise model or reject candidate |
| Grounded | Verify native catalog/resources, licenses, account eligibility and owner caps | Exact definitions, bindings and constraints | Mark unsupported capability; narrow the promise |
| Private production pilot | Later authorized local attempts; no publication | Original artifact quality, total cost, real operator effort, reproducibility | Return to configuration/composite design; keep failed attempts |
| Bounded audience pilot | Separately authorized publication | Audience-value evidence under fixed limits | Revisit strategy/problem; no scale-by-volume shortcut |
| Revenue evaluation | Eligible actual transactions and complete costs | Reconciled net receipts and economic contribution | Revise route or stop within owner loss/time cap |
| Selective operation | Only proven bounded capabilities activated | Ongoing quality, rights and cost control | Pause affected pathway; create a new revision |

The complete business has feedback loops. It must **not** be forced into one global DAG. A particular artifact's dependency/revision history can be acyclic; performance from one episode informs a *later* brief. Cyclic business learning is represented by time and version, not a same-version causal loop. No causal improvement is established by drawing a feedback arrow.

Top-down: intent → domain responsibilities → processes → flows → bounded capability requirements. Bottom-up: actual configuration/resources → verified native component occurrences → validated composites → coordinated flows → accountable processes. Middle-out revisions remain allowed. Unsupported requirements stay visible rather than being hidden to complete the tower.

### 6.5 Symbolic end-to-end walkthrough, with no fabricated run
| Step | Example proposed artifact | Guard | Why it might return for revision |
|---|---|---|---|
| Intelligence | Dossier: a specific audience struggles with local searchable notes | Real source sample, alternatives, privacy and freshness | Existing tutorials already solve it; no differentiated need |
| Strategy | Brief: show a reproducible private notes workflow | Clear viewer outcome and rubric; cap reserved | Owner expertise, budget or audience not defined |
| Production | Narrated original demonstration, captions and provenance | Real demo works; tool/model/asset rights; measured correction time | Runtime unavailable, inaccurate result, excessive manual repair |
| Monetization | Explicit no-offer state or a relevant approved route | Account eligibility and actual product knowledge | No appropriate offer; no ad access; support burden too high |
| Distribution | Private package with channel metadata/disclosure proposal | Independent QA and publication authorization | Authorization absent: remain private; no accidental default-public upload |
| Audience Care | Categorized feedback/correction dossier | Original release version and evidence; data minimization | Safety/privacy issue escalates; no invented audience feedback |
| Finance | Cost report and later reconciled receipts | All attempts, operator work, unique transaction and period | Missing payout, double-counted money or negative economic result |
| Operations | Continue / revise / stop decision | Compare evidence against predeclared caps and purpose | Pause or revise affected instances; preserve stable ones |

These are hypothetical document transitions. No named workflow, viewer response, payment or production result in this table was observed.

### 6.6 Faults, propagation and stability
| Failure / change | First owner | Affected handoffs | Stable parts / response |
|---|---|---|---|
| License disallows commercial voice | Production / rights review | Release package and cost assumptions | Retain audience evidence; replace binding, regenerate affected media only |
| Demonstration is wrong | Production, triggered by Audience Care | Release/correction record; editorial claims | Pause affected release, preserve evidence and correct; never silently rewrite history |
| Model change raises runtime | Production, Finance | Capacity/cost report → Strategy | Rebudget future briefs; prior measured costs remain unchanged |
| Platform route unavailable | Distribution / Monetization | Release/offer eligibility | Keep reusable private assets; reassess route, do not bypass eligibility |
| Low viewer value | Strategy with Intelligence | Next dossier/brief revision | Do not blame model speed alone; collect contrary evidence |
| Negative economic margin | Finance → Operations | Portfolio/revenue/cap decisions | Reduce cost/scope or stop; no automatic spending to chase losses |
| Product support exceeds no-meetings envelope | Audience Care / Monetization | Product/offer revision | Improve self-serve material or remove route; no hidden custom consulting |

Change requests identify source artifact, impact set, proposed patch, expected invariants, checker result and reviewer decision. Unrelated instance revisions remain stable unless a recorded dependency requires change. Design checks below verify only representation consistency and authorization boundaries; they do not verify the future orchestrator, component correctness or profitable emergence.''')
