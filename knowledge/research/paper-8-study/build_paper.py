"""Create the design-stage Paper 8; never run collection or change other papers."""
from pathlib import Path
import base64,json,hashlib
import nbformat as nb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[3]
D=Path(__file__).resolve().parent
OUT=ROOT/'knowledge/research/notebooks/Paper 8 - Market Intelligence Instance.ipynb'
cells=[]
def md(text):cells.append(nb.v4.new_markdown_cell(text))
md('''# Paper 8 — Designing the Market Intelligence Instance
## From Processes to Configuration: a critical-thinking research blueprint
**Design-stage manuscript and research template · 30 October 2026**

### Provisional abstract
This paper specifies a Market Intelligence instance within Paper 7's shared Operations plane. The instance is intended to turn a bounded business question into an inspectable opportunity dossier: a defined audience problem, source-linked observations, competing explanations, existing solutions, uncertainty, and recommendations for further investigation. We develop the design top down through Processes, Flows, Composites, Components and Configuration, then propose bottom-up grounding and evaluation before operational use. The central hypothesis is that explicit evidence contracts, counterevidence search and versioned decision gates can make intelligence more traceable and less vulnerable to unsupported confidence than free-form synthesis. This is a proposed architecture and study protocol. No new market observations, component implementation, collection runs, demand validation or experimental results are reported here. Results and conclusions remain open pending evidence.

**Research status:** design only. **Business role:** inform Content Strategy; do not choose the entire business, publish content, spend money, open accounts or declare a profitable niche. **Existing papers:** preserved.''')
md('''## 1. Problem, research question and scope
**Primary question:** How can a Market Intelligence instance systematically investigate audience problems and competing solutions, preserve evidence and uncertainty, and supply a decision-ready dossier under explicit time, cost, privacy and quality limits?

| Scope element | Proposed boundary | Out of scope / unknown |
|---|---|---|
| Business context | Mostly automated social-media business with local content generation and no meetings | Revenue viability is not established |
| Unit of investigation | One audience × job/problem × language/geography × time window | Audience, language and geography remain unselected |
| Inputs | Operations research brief and limits; optional feedback and performance observations | No inferred jurisdiction, budget or customer identity |
| Outputs | Versioned opportunity dossier, alternatives, counterevidence, unresolved questions and next-step recommendation | No guaranteed demand score or automatic strategy decision |
| Source access | Lawful public primary material or explicitly authorized account data | No private scraping, consent bypass, paid access or hidden personal-data collection |
| Automation | Reproducible preparation, extraction and synthesis with visible review gates | No autonomous public communications or transactions |
| Local constraint | Design local analysis/synthesis where feasible; network retrieval remains online | No installed model, capacity or inference performance claim |

**Success for this paper:** a substantial, reviewable instance design plus a falsifiable implementation/evaluation plan. Success of the future business is a separate question.''')
md('''## 2. Relationship to Paper 7 and the shared Operations plane
Market Intelligence is one of seven specialization instances. It retains its own state, artifacts and five planes while using shared goals, budgets, identity and evidence conventions. It can revise its internal design without rewriting the other towers. A handoff is a contract between instances, not an additional layer.

| Direction | Contract | Authority and evidence boundary |
|---|---|---|
| Operations → Intelligence | Research purpose, constraints, owner, permitted sources, budget/time envelope | Unknown limits produce a clarification request; no invented authority |
| Audience Care → Intelligence | Deidentified recurring problems, corrections and questions | Preserve source authority and consent; a complaint is an observation, not market prevalence |
| Finance/Performance → Intelligence | Cohort metrics and resource constraints | Preserve denominator, period, missingness and exposure; metrics do not prove causality |
| Intelligence → Content Strategy | Opportunity dossier with evidence and alternatives | Strategy accepts, rejects or requests more evidence; recommendation is not an order |
| Intelligence → Finance | Actual research cost and owner-effort events | Include failed retrieval, review and maintenance; internal transfers are not revenue |
| Intelligence → Operations | Status, exceptions, conflicting constraints and open obligations | Escalate decisions outside delegated scope |

The Operations plane coordinates all instances. Its policies do not remove domain checks or evidence requirements. Shared library definitions remain distinct from configured instance occurrences.''')
md('''## 3. Hypotheses, alternatives and refutation
| ID | Proposed hypothesis | Evidence that could support it | Evidence that challenges it |
|---|---|---|---|
| H1: traceability | Structured claim/evidence contracts reduce unsupported assertions | Independent reviewers can recover sources and identify unsupported claims more reliably than a free-form comparison | Missing sources, wrong entailment, confident synthesis despite contradictions |
| H2: independence | Source-family deduplication produces a more honest view of corroboration | Copied/syndicated observations cease to inflate counts while genuinely different evidence remains | Over-merging independent reports or missing disguised duplicates |
| H3: challenge | Explicit counterevidence search changes weak recommendations | Relevant existing solutions and disconfirming evidence alter or block recommendations | Ritual objections that do not affect conclusions; cherry-picked sources |
| H4: decision utility | A dossier helps Strategy make a bounded next decision | A reviewer can explain audience, problem, alternatives, gaps and justified next action | An impressive summary that cannot support a specific decision |
| H5: automation | Local-assisted preparation lowers recurring owner effort without degrading evidence quality | Measured active effort falls against a matched manual/partly automated reference | Correction and verification exceed the predeclared envelope |

**Alternative explanations:** improvement may come from extra reviewer time rather than the architecture; sources may be easier in one case; apparent agreement can reflect shared model bias; source visibility is not willingness to watch or pay. A more complex pipeline may perform worse than a careful manual dossier.

**Null positions:** the instance may not improve decisions; some questions may remain unanswerable from accessible public evidence; useful output may be an honest 'insufficient evidence.' No hypothesis is accepted by this design document.''')
md('''## 4. Critical-thinking method and decision logic
| Stage | Question | Required record | Gate |
|---|---|---|---|
| Frame | What decision will this investigation inform? | Audience/job scope, assumptions, definitions and exclusions | Clarify an ambiguous brief before collection |
| Plan | What would count for or against the claim? | Source strategy, inclusion rules, counterevidence queries and limits | Freeze a bounded plan; allow documented amendments |
| Observe | What was actually seen? | Source-linked raw excerpt/measurement, context, date and limitations | Retrieval success alone is not evidence quality |
| Distinguish | Is this observation independent and relevant? | Source-family links, duplicates, relevance and freshness | Do not count copied claims as independent support |
| Infer | What does the evidence warrant? | Claim-to-evidence relation, alternatives and contradictions | No causal or prevalence inference beyond the source |
| Challenge | How could this conclusion be wrong? | Strongest alternative solution and counterargument | Revise, qualify or reject unsupported claims |
| Decide | What should happen next? | Continue / narrow / ask / stop recommendation and reasons | Strategy/Operations own decisions outside this mandate |
| Learn | What should change in the next revision? | Error, correction and cost log | Preserve earlier decisions and evidence |

Use explicit judgments **supported, contradicted, mixed, insufficient, stale or inaccessible**. These are review statuses, not calibrated probabilities. Frequency, search interest, viewer behavior, purchase behavior and profitability are different constructs and must not be collapsed into a single 'demand' label.''')
md('''## 5. Process plane — accountable Market Intelligence operations
A process has a purpose, owner, recurrence/trigger, decision rights and exit criteria. It coordinates flows; it is not simply a long prompt.

| Process | Trigger / purpose | Inputs → outputs | Ownership / exit |
|---|---|---|---|
| P1: Investigation governance | New or revised business question | Research brief + limits → accepted plan or clarification | Intelligence owner; Operations resolves conflicting scope/budget |
| P2: Opportunity investigation | Accepted plan | Planned source work → observations and claim set | Evidence reviewer; record exclusions, gaps and contrary evidence |
| P3: Challenge and dossier release | Candidate interpretation ready | Claims + alternatives → accepted/rejected dossier revision | Independent review role where feasible; no release with unresolved material provenance failures |
| P4: Freshness and revision | Source change, audience feedback, correction or review date | Existing dossier + new evidence → impact assessment and new revision | Intelligence owner; preserve superseded evidence and notify Strategy |
| P5: Cost/privacy stewardship | Every collection/review attempt or access issue | Real events → cost ledger, access/retention decisions and exceptions | Finance receives costs; owner handles access-sensitive exceptions |

**Process invariants:** no claim without traceable evidence or an explicit assumption label; no hidden discarded contrary evidence; no unauthorized access or side effects; budget exhaustion ends in a bounded partial result; missing data never silently becomes zero; model output is synthesis, not a primary source.

**Required owner decisions:** audience, language/geography, decision to inform, acceptable evidence standard, research time/cash cap, privacy/retention limits and who may accept a dossier. Until supplied, these remain open obligations rather than guessed values.''')
md('''## 6. Flow plane — work sequences, parallelism and recovery
| Flow | Sequence and dependencies | Failure / return path | Output contract |
|---|---|---|---|
| F1: Brief intake | Validate purpose → expose unknowns → accept or ask → freeze revision | Ambiguous or unauthorized brief → Operations clarification | Research plan with scope and limits |
| F2: Evidence acquisition | Plan queries → retrieve permitted sources → preserve observations → classify access failures | Timeouts/rate limits → bounded retry; blocked access → record, do not bypass | Source/observation register with successes and failures |
| F3: Normalize and assess | Parse → normalize → source-family deduplicate → assess relevance/freshness | Ambiguous extraction → quarantine/manual review | Normalized evidence and family links |
| F4: Synthesize and challenge | Build claims → compare existing solutions → seek contrary evidence → qualify recommendation | Unsupported or conflicting claim → targeted collection or insufficient result | Claim matrix and alternative explanations |
| F5: Review and handoff | Check dossier → reviewer decision → versioned handoff → consumer acknowledgment | Rejection → preserve submitted revision and return explicit obligations | Accepted dossier or reasoned rejection |
| F6: Refresh | Detect expiry/change → impact trace → reopen relevant claims → revise → notify consumers | Unavailable source → mark stale/inaccessible; retain history | Superseding dossier and change report |

Queries against independent source families can run in parallel within a shared quota. Interpretation waits for relevant evidence and records what is absent. Retries have a maximum count/time and cancellation. Duplicate delivery must not create duplicate observations, costs or handoffs. These are proposed requirements, not implemented queue guarantees.

An individual investigation has an acyclic dependency history. Learning across investigations loops through **new revisions**, rather than modifying the same evidence retrospectively. This preserves iterative top-down, bottom-up and middle-out development.''')
md('''## 7. Composite plane — bounded capability contracts
These are proposed composites. They become grounded composites only after real components/resources, exposed inputs, outputs and checks exist.

| Candidate composite | Inputs | Outputs | Required checks / boundary |
|---|---|---|---|
| C1: Brief-to-plan | Research question, constraints, prior decisions | Query plan, inclusion/exclusion criteria and missing fields | No invented scope; limits explicit |
| C2: Source-to-observations | Permitted URL/document + retrieval policy | Captured content reference, observations and retrieval status | Actual source, timestamp, privacy and license/access context |
| C3: Evidence normalization | Source records and observations | Canonical records, units and source-family assignments | Preserve raw context; reversible transformations; uncertain duplicates marked |
| C4: Problem/solution comparison | Audience/job and evidence | Competing solutions, gaps and counterarguments | Search for good existing answers, not only opportunity claims |
| C5: Claim assessment | Proposed claim + evidence references | Support/contradiction/uncertainty judgment | Evidence actually entails claim; do not confuse repetition with support |
| C6: Dossier assembly | Reviewed claim matrix, alternatives, costs and gaps | Structured opportunity dossier plus readable report | No unsupported summary; all required fields present or explicitly unknown |
| C7: Change-impact analysis | New observation or correction + artifact lineage | Affected claims/consumers and proposed revision | Unrelated accepted artifacts remain stable |

**Boundary example:** C5 does not decide which niche the business adopts. It judges what evidence supports a claim. A missing source remains an unresolved dependency. C6 must expose that gap rather than fabricate a complete-looking dossier. A shared language model can support multiple composites, but each occurrence has separate task context, evidence and review results.''')
md('''## 8. Component plane — ground the design without inventing native blocks
The native component catalog has not been verified for Paper 8. The table lists **roles to bind**, not existing Langflow components. Native names, versions, port schemas and configuration fields must be obtained from the actual pinned catalog before a graph is produced. Custom resources/adapters must be labeled separately; do not modify native definitions to make the design appear grounded.

| Required role | Candidate implementation category | Required interface / proof | Current status |
|---|---|---|---|
| Structured brief input | Verified native input/schema block or explicit adapter | Brief schema, validation errors and identity | Unbound |
| Permitted retrieval | Authorized retrieval tool/resource plus native tool adapter if available | URL allow policy, timeout, source capture and access failures | Unbound; no retrieval run |
| Parsing/normalization | Deterministic parser/resource | Raw-to-normalized lineage, units and uncertain extraction | Unbound |
| Duplicate-family analysis | Deterministic comparison plus review | Exact duplicate evidence, family/uncertain links | Unbound; no clustering success claimed |
| Synthesis | Verified native model/prompt occurrence with local model binding | Structured outputs, evidence references, model/version and actual inference | Unbound; no model selected or benchmarked |
| Contract validation | Deterministic schema/consistency resource | Required fields, references and actionable errors | Proposed, not implemented |
| Artifact persistence | Scoped versioned store/resource | Identity, immutable revisions, hashes and access boundaries | Proposed, not implemented |
| Human review and handoff | Explicit approval state and transport adapter | Reviewer authority, acceptance/rejection and duplicate-safe acknowledgment | Proposed, not implemented |

**Grounding sequence:** inspect pinned native definitions → map each role → record unsupported roles → choose bounded adapters only where needed → validate typed connections and exposed configuration → test component behavior → validate composite contracts. A native Agent block is still a component even when given a sophisticated role; an authored role name does not promote it to Composite.''')
md('''## 9. Configuration plane — explicit, versioned and reviewable
| Configuration group | Required fields / binding | Validation / privacy boundary | Current value |
|---|---|---|---|
| Research scope | Audience, job/problem, language, geography, time window, decision owner | Explicit confirmation; no geographic inference from device | Undecided |
| Evidence policy | Allowed sources, inclusion/exclusion, source-family rules, freshness and quotation limits | Preserve access terms and contrary evidence | Proposed policy; details to freeze |
| Execution bounds | Time/cash cap, request quota, retries, timeout, cancellation and concurrency | Stop on cap/authorization failure; no hidden continued collection | Undecided |
| Model/resource binding | Exact local model/checkpoint revision, license, runtime, resource limits and prompts | Commercial rights and actual runtime evidence required | Unbound |
| Schemas | Brief, observation, claim, dossier, event and handoff versions | Reject invalid/mixed versions; migrate explicitly | Proposed below |
| Data handling | Access classification, personal-data minimization, retention and deletion owner | No account secrets or customer identities in notebooks | Owner policy required |
| Decision rules | Supported/contradicted/mixed/insufficient/stale/inaccessible; acceptance rubric | No uncalibrated numeric confidence presented as probability | Provisional statuses |
| Evaluation | Cases, reference judgments, exposure log, reviewer protocol and comparison | Freeze before judging results; record changes | Designed in Section 12; not run |

Configuration is not a dumping ground for evidence or hidden business assumptions. Credentials remain external secret references. Unknown required values should block the relevant transition and produce one targeted clarification request, while independent safe design work can continue.''')
# Embedded, self-contained static design illustration.
fig,ax=plt.subplots(figsize=(12,8.8),facecolor='#111b26');ax.set_facecolor('#111b26')
items=[('OPERATIONS PLANE','Shared goals, authority, budgets and inter-instance handoffs'),('MARKET INTELLIGENCE INSTANCE','Evidence-backed opportunity dossiers; uncertainty preserved'),('PROCESSES','Govern investigation, review, refresh, cost and privacy'),('FLOWS','Intake → acquire → normalize → challenge → handoff → revise'),('COMPOSITES','Bounded evidence, claim, dossier and impact capabilities'),('COMPONENTS','Actual native catalog roles + explicit resources/adapters; unbound'),('CONFIGURATION','Scope, schemas, policies, limits, model bindings and access')]
for i,(title,detail) in enumerate(items):
 y=7.6-i*1.05;fc='#244d50' if i<2 else '#263c52'
 ax.add_patch(FancyBboxPatch((.2,y),11.3,.80,boxstyle='round,pad=.03,rounding_size=.08',facecolor=fc,edgecolor='#75b9b1' if i<2 else '#627f98'))
 ax.text(5.85,y+.54,title,ha='center',color='#edf8fa',weight='bold',fontsize=12)
 ax.text(5.85,y+.20,detail,ha='center',color='#c8dbe6',fontsize=10)
 if i<6:ax.annotate('',xy=(5.85,y-.20),xytext=(5.85,y-.04),arrowprops={'arrowstyle':'->','color':'#8bbdb7'})
ax.text(5.85,.42,'Top-down specification now • bottom-up grounding later • proposed architecture, not execution',ha='center',color='#bfdbdf',fontsize=10)
ax.set_xlim(0,11.8);ax.set_ylim(.1,8.7);ax.axis('off');fig.tight_layout()
img=D/'market-intelligence-planes.png';fig.savefig(img,dpi=150,facecolor=fig.get_facecolor(),bbox_inches='tight');plt.close(fig)
cell=nb.v4.new_markdown_cell('![Market Intelligence instance from Processes down to Configuration](attachment:market-intelligence-planes.png)')
cell['attachments']={'market-intelligence-planes.png':{'image/png':base64.b64encode(img.read_bytes()).decode()}}
cells.append(cell)
md('''## 10. Data structures and opportunity dossier contract
These are proposed schemas to implement, not validated production API contracts. All artifacts carry identity, schema version, revision, owner, real creation time, access classification and source lineage where applicable.

| Record | Required domain fields | Integrity rules |
|---|---|---|
| Research brief | Decision question, audience/job, constraints, allowed access, limits, acceptance owner | Unknowns explicit; authority separate from model suggestion |
| Source | URL/path, publisher, retrieval time/status, content reference/hash, access context and family | Source availability and license status recorded; no fabricated retrieval |
| Observation | Source ID, exact location/context, observed statement or metric, units/period, limitations | Preserve raw observation; distinguish quotation from interpretation |
| Claim | Statement, observation IDs, judgment, opposing evidence, inference scope and reviewer | No orphan citations; model synthesis is not primary evidence |
| Alternative | Competing solution/explanation, supporting and opposing evidence, unresolved comparison | Include strong existing solutions, not straw alternatives |
| Opportunity dossier | Audience/job, evidence summary, alternatives, differentiation hypothesis, uncertainty, recommendation, costs and open obligations | No profitable-niche label; handoff version explicit |
| Event/cost | Attempt identity, timestamps, status, resource usage, owner minutes and cost basis | Retain failures; avoid duplicated events and shared-cost double counting |
| Review/handoff | Artifact revision, criteria, reviewer authority, decision/reason, recipient acknowledgment | Rejection preserved; duplicate handoffs idempotent by design |

### Dossier reader view
| Reader question | Required dossier answer |
|---|---|
| Who has what problem? | Explicit audience/job scope, evidence and uncertainty |
| What already solves it? | Existing solutions, their strengths and any demonstrated gap |
| Why might our content help? | Differentiation hypothesis tied to evidence, not a promise |
| What would change our mind? | Strongest counterevidence, alternative explanation and falsification plan |
| What do we not know? | Missing, inaccessible, stale or contradictory information |
| What should happen next? | Bounded continue / narrow / ask / stop recommendation with costs and owner |

**Example skeleton — not a market finding:** audience `[undecided]`; problem `[to investigate]`; observations `[]`; alternatives `[]`; supported claims `[]`; recommendation `insufficient evidence`; next action `confirm research brief`. An empty evidence set must never be rendered as evidence of no demand.''')
md('''## 11. Implementation plan and design gates
| Milestone | Work | Acceptance evidence | Remains unproven |
|---|---|---|---|
| M1: freeze one brief | Resolve scope, access, budget, owner and acceptance rubric | Complete versioned brief or explicit blocked obligations | Demand |
| M2: ground contracts | Verify native catalog and role/resource bindings; implement record validation | Pinned definitions, port schemas and meaningful validation failures | End-to-end intelligence quality |
| M3: one bounded investigation | Implement intake → source/observations → dossier with costs and cancellation | Real trace, source-linked output, all failed attempts and unknowns | Generalization and business value |
| M4: independent challenge | Compare with manual/free-form reference under declared constraints | Reviewer decisions, contrary evidence, correction and effort logs | Profitable niche or causal revenue improvement |
| M5: handoff/refresh | Strategy accepts/rejects dossier; replay a correction or stale source | Versioned acknowledgment and impact trace; unrelated state stable | Full autonomous Operations |

Choose the minimum reliable implementation per contract. Deterministic validation and preservation do not need model judgment; synthesis and interpretation may use a local model but require evidence checks. Use the unaltered builder later to propose a native graph in isolation, preserve its raw result and verify bindings independently. No such builder run has occurred for Paper 8.

A production scheduler, account integration or autonomous publishing system is not required to complete the first intelligence capability. Developing a single useful slice should still respect all five plane contracts.''')
md('''## 12. Evaluation, counterexamples and defense plan — not run
| Case family | Challenge | Expected defensible behavior |
|---|---|---|
| Strong independent support | Multiple genuinely different observations | Supported claim within source scope; independence explained |
| Copied popularity | Many pages repeat one original claim | Family-aware counts; no false corroboration |
| Existing solution already sufficient | Good current tutorials solve the task | Revise/reject claimed content gap rather than invent differentiation |
| Contradictory evidence | Sources disagree materially | Preserve conflict and qualify conclusion |
| Missing/inaccessible evidence | No reliable retrieval or account signal | Insufficient/inaccessible status, not zero or invented data |
| Stale/version-specific evidence | A tool or audience context changes | Mark affected claim stale; create revision and notify consumer |
| Malicious source content | Retrieved text contains instructions unrelated to evidence | Treat source as data; do not grant tools or authority |
| Privacy/access boundary | Restricted source or personal identifier appears | Minimize/quarantine/escalate; no access bypass |
| Budget exhaustion | Collection cannot finish inside cap | Bounded partial dossier and cost record |
| Revision/replay | Duplicate events or changed evidence | No duplicate counts/costs; trace affected claims and retain history |

### Measures and comparison
| Measure | Operational definition to freeze | What it cannot establish |
|---|---|---|
| Claim grounding | Fraction of reviewed claims actually supported by cited observations, plus denominator and disagreements | Market truth beyond accessible evidence |
| Citation recovery | Reviewer can locate correct source/context for each claim | Claim validity by itself |
| Duplicate handling | Family judgments compared against independent reference decisions | Perfect source independence |
| Counterevidence coverage | Relevant contrary cases found/missed against a defined review set | Exhaustive knowledge of the internet |
| Decision usability | Reviewer can identify audience, alternatives, uncertainty and next action under a fixed rubric | Willingness to watch or pay |
| Effort/cost | All attempts and active owner minutes per accepted dossier | Future automation at scale |
| Revision fidelity | Correctly updated affected artifacts; unchanged unrelated state | Runtime reliability without implementation tests |

Compare structured workflow with manual/partly automated or free-form synthesis using the same research question and accessible source opportunity. Report resource differences rather than hiding extra review time. Freeze criteria before observing results; record every protocol change. Development cases must not be relabeled held out. Later fresh evaluation needs independent or previously unexposed cases and disclosed sampling limits. No case count, accuracy, confidence interval or statistical significance is invented here.''')
md('''## 13. Results, learning and hypothesis defense — reserved
No experiments or new market collection have been run for this paper. Do not populate these fields from illustrative examples.

| Result field | Status / future evidence |
|---|---|
| Brief and corpus/source snapshot | Not selected; record version and inclusion log |
| Implemented native graph/resources | Not implemented; record pinned definitions and adapters |
| Per-case observations | Not run; retain failures and reviewer disagreements |
| Comparative results / uncertainty | Not measured; specify denominator and appropriate uncertainty before reporting |
| Compute and operator cost | Not measured; disclose tariffs/valuation versus observations |
| Hypothesis outcome | Undetermined per H1–H5; supported, challenged or inconclusive only after evidence |
| Lessons and revisions | Record failed assumption, changed rule, reason and fresh check |
| Threats to interpretation | Source selection, duplicates, reviewer/model bias, exposure and time differences |

**Defense prompts:** What is the strongest objection? What evidence would favor the alternative? Did the architecture help, or did we add labor? Could another reviewer reconstruct the conclusion? What claim must be narrowed? A successful result is a justified conclusion, including rejection or inconclusiveness—not forced confirmation.''')
md('''## 14. Limitations, conclusion, references and review template
### Current limitations and provisional conclusion
This manuscript specifies the intended Market Intelligence instance; it does not instantiate its native graph, validate its source access, run local inference, establish audience demand or prove decision improvement. The five-plane breakdown is an authored engineering proposal. The seven-instance business architecture remains provisional. Completing a dossier cannot establish revenue or profitability without separate audience/commercial evidence.

The next bounded development step is to freeze one research brief and map its required roles to actual components/resources. Build upward only where the lower contracts are supported. Preserve unanswered questions and failed hypotheses as part of the record.

### Reference and provenance register
| Reference class | Entry / intended use | Current status |
|---|---|---|
| Internal architectural basis | Paper 7 — Local AI Social Media Business; shared Operations plane and seven-instance view | Existing project design, not external evidence |
| External methods literature | Traceability, evidence synthesis, source dependence, market intelligence and evaluation | To research; no fabricated citations |
| Native interfaces | Actual pinned Langflow component definitions and builder interfaces | To inspect for this instance |
| Market sources | Dated original sources collected under an accepted brief | None collected for this paper |
| Model/tool rights | Exact selected model/checkpoint, source revision, license and access terms | Unselected/unverified |

For every future source record title, author/publisher, exact URL or path, access time, version when available, claim supported, assumptions, limitations and artifact reference. Repetition is not independent corroboration. Do not use a model-generated reference without verification.

### Review and response template
| Finding | Reviewer / scope | Evidence | Severity / claim affected | Response and revision | Verification |
|---|---|---|---|---|---|
| Not yet reviewed | Independent review pending | — | — | — | — |

No external academic peer review or independent design review is claimed. Notebook structure and figure inspection are delivery checks, not scientific evaluation.''')
notebook=nb.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Research Python','language':'python','name':'research-python'},'language_info':{'name':'python'},'paper8':{'status':'design-only','experiments_run':False,'market_observations_collected':False}})
nb.validate(notebook);nb.write(notebook,OUT)
print(OUT)
