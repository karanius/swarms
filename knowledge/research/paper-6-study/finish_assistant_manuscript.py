"""Coordinator coauthor additions; writes the isolated draft only, never canonical."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'services/paper6-assistant'))
from workspace import Workspace
ADDITIONS={
1:'''### Study D: from observed wiring to explicit obligations

**Additional research question:** Within a pinned three-type native alphabet and explicitly authored structured intents, can an obligation diagnostic preserve intent and identity, expose missing or conflicting evidence, and return an authorized revision, clarification, scope rejection or assumption-qualified static grounding?

| Input/output boundary | In scope | Remains outside this study |
|---|---|---|
| Intent | Authored route, capabilities and revision fields | Conversational requirement discovery and arbitrary requirements |
| Components | Pinned ChatInput, Agent and ChatOutput metadata | Full native library and custom-component semantics |
| Configuration | Scoped synthetic model-binding attestation | Credentials, resource availability and provider execution |
| Output | Blockers, questions, bounded patches and evidence tiers | A useful or deployed multilayer instance |

Study D is a deliberately authored diagnostic bridge, not a replacement for the mining question. No corpus workflow was assigned a retrospective task intent. The collaborating native Langflow research assistant helped design and implement this test; the coordinator authored the concrete fixtures and a separate checker. Neither this authorship separation nor successful software assertions constitutes external evaluation.
''',
6:'''### Study D method: separate epistemic status from the next action

The native research assistant authored a deterministic Python diagnostic after an interview and protocol debate. An initial proposal to retrofit intents to corpus groups was rejected: saved wiring alone cannot establish purpose. The final protocol instead uses prospectively authored structured cases and an unchanged pinned native catalog.

| Method | Predicates covered | Output contract |
|---|---|---|
| B0 | Named ports, static type overlap, local type contradictions | PORTS_PASS, PORTS_FAIL or PORTS_UNKNOWN only |
| B1 (primary comparator) | B0 plus unconditional required fields, scoped binding witnesses and local conflicts | FIELDS_PASS, FIELDS_FAIL or FIELDS_UNKNOWN only |
| Ledger | Those predicates plus authored intent and limited authorized revisions | ASK, REJECT_SCOPE, REVISE or SPEC_GROUNDED, with retained blockers and runtime unknowns |

For an edge, declared output types are used when present; otherwise a return annotation supplies an explicitly weaker witness. Compatibility requires nonempty overlap with declared input types. For each required field, a compatible wire or scoped, nonconflicting, synthetic-assumption binding must exist. These predicates do not establish activated ports. Agent.model is required in the pinned catalog; a universal API-key requirement is not inferred.

The implementation processes recognized revisions, then checks the resulting state. Revoke reopens the model obligation; rename preserves scoped references; a uniquely authorized direct-route edit uses an existing Agent. Removal contrary to retained intent asks without applying it. This is not a general transactional planner: pre-existing identity conflicts can still interact unsafely with edits outside the tested cases.

The decision priority is unsupported capability → REJECT_SCOPE; other static blockers → ASK; otherwise applied authorized patch → REVISE; otherwise SPEC_GROUNDED. Runtime obligations remain unknown throughout. The original oracle and protocol disagreed on whether an activation-certification request should be rejected or deferred with a question. That difference is retained, not repaired into a perfect score. Mined rules did not enter this diagnostic, so Study D cannot establish their incremental value.
''',
10:'''### Study D defense: what the additional evidence changes

A broader checklist predictably notices facts omitted by a narrower checklist. We therefore interpret B0/B1 as coverage references, not competitors falsely claiming readiness. No causal, statistical or learned-generation advantage follows from the ledger's richer outputs.

| Challenge | Evidence-bounded response |
|---|---|
| Is the oracle ground truth? | No. C17 reveals an unresolved action contract: ASK retains an unknown runtime obligation; REJECT_SCOPE refuses an unavailable certification deliverable. Both avoid an unsupported affirmative claim. |
| Did the code produce useful composites? | Not tested. It diagnosed authored static states in a three-type alphabet. |
| Did the assistant independently validate its own work? | No. It implemented and critiqued the design; the coordinator authored fixtures and a separately coded checker. This remains dependent internal review. |
| Does this rescue the mining result? | No. The original 34/402 recovery versus 43/402 center-frequency result is unchanged. |
| Does keeping runtime unknowns make the result useless? | No. Explicit unresolved obligations are inspectable design outputs; their usefulness and real-task effectiveness remain unmeasured. |

The practical insight is a separation of jobs: repeated wiring can suggest a candidate, while an intent-and-obligation contract determines what may responsibly happen next. Neither substitutes for behavior testing. The unresolved certification label suggests future schemas should separate epistemic status from permitted action and encode whether a required deliverable may be deferred.
''',
11:'''### Study D collaboration and revision record

| Stage | Actual decision or artifact | What was preserved |
|---|---|---|
| Interview | Assistant read results, protocol and verification; wrote collaboration-brief.md | Negative mining results and limits |
| Debate | Retrofitted intents rejected; required-field baseline added | Baseline coverage and authorship disclosures |
| Formalization | Agent wrote protocol-v2.md, obligation_ledger.py, notebook and freeze manifest | Coordinator fixtures; withheld original oracle |
| Pre-run inspection | Artifact/context paths corrected before execution | Decision predicates, input fixtures and protocol |
| Execution | One sandboxed notebook execution invoked through the native research assistant produced the saved first notebook and result JSON | First-run hashes, outputs and warning |
| Checking | Separate checker initially needed path and malformed-patch handling corrections | Original research results unchanged |
| Review | Reviewer exposed a route-checker gap; exact transition checks added | C20 actual result unchanged; faulty mutation now rejected |
| Final recount | 927 assertions, four C17 representation-label differences; eight corrupted-result variants detected | Original 23/24 base action agreement |
| Writing | Assistant wrote draft contributions; coordinator coauthored discussion and checked selected merges | Original abstract, earlier studies and explorer views |

Assertion totals describe engineering coverage, not independent observations. The four mismatch records derive from one base case. The final checker replaces the earlier 899-assertion recount for verification coverage; neither first result nor oracle was changed. A future scope/deferral distinction is proposed rather than applied retroactively.
''',
12:'''### Study D limits and source-inspected counterexamples

| Threat | Consequence for interpretation |
|---|---|
| Jointly designed blueprint and tiny authored suite | Internal conformance only; no independent, representative or held-out efficacy estimate |
| Synthetic model-binding witnesses | Static grounding under assumptions, not available resources or real model behavior |
| Return annotations rather than activated output ports | Compatibility is annotation-tier evidence |
| Unknown additional intent keys lack closed-schema validation | Outside-schema mandatory constraints can be silently ignored; arbitrary requirements are not safely supported |
| Route checks establish limited local existence | No exclusive routing, shared conversation identity or general output semantics guarantee |
| Conflicting duplicate node IDs feed a last-write-wins map | Downstream details can depend on order outside the tested assertion representation |
| Revision prechecks do not resolve every pre-existing conflict | A patch may precede an ASK on an identity-conflicted state; general transactionality is not established |
| Binding identity/cardinality and malformed input contracts incomplete | Multiple positive bindings, orphan assertions and unsupported data require stronger validation |
| Oracle/protocol action ambiguity | Original acceptance differs for C17; no perfect-score claim is warranted |

These code-inspection risks were identified by the collaborating assistant and reviewed as plausible counterexamples; they are **not additional executed experiment outcomes**. The measured suite remains unchanged. The prototype is a research diagnostic, not a safe production generator. Passing type and required-field checks cannot establish task usefulness, higher-layer emergence, provider behavior or the value of the mined rules.
'''
}
def apply():
 ws=Workspace()
 for number,addition in ADDITIONS.items():
  current=ws.section(number)
  marker='<!-- assistant-coauthor-d -->'
  text=current['markdown'].split(marker)[0].rstrip()+'\n\n'+marker+'\n'+addition
  ws.write_section(number,text,current['revision'])
if __name__=='__main__':apply()
