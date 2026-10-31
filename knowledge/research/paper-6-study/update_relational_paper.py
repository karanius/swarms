"""Execute the real rule-learning notebook block, then integrate bounded results."""
import base64,copy,hashlib,json,os
from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[3];STUDY=ROOT/'knowledge/research/paper-6-study';BASE=ROOT/'knowledge/research/paper-6-corpus';PAPER=ROOT/'knowledge/research/notebooks/Paper 6 - Rule Mining from Langflow Templates.ipynb'
nb=nbformat.read(PAPER,4);backup=STUDY/'paper-6-before-relational-study.ipynb'
if not backup.exists():nbformat.write(nb,backup)
# Replace only this extension's generated cells on rerun; keep the prior two code cells.
nb.cells=[c for c in nb.cells if not c.metadata.get('paper6_relational')]
def cell(kind,text):
 c=nbformat.v4.new_code_cell(text) if kind=='code' else nbformat.v4.new_markdown_cell(text);c.metadata['paper6_relational']=True;return c
code=[
cell('markdown','''### Executable study C — explicit rule learning and masked-feature recovery

These cells execute the pinned PyClause/AnyBURL learner, source-separated masking, comparisons, symbolic proposal writer and independent recount. Running the study starts three20-second feature-learning attempts and one bounded wiring probe, then saves a new engine batch. It runs static corpus analysis only, never downloaded component code or agents. Existing graphs are evidence viewers.

The raw-wiring probe may fail under its512MB heap cap; that failure is recorded separately, not counted as zero rules. The notebook keeps all learning logs and failure artifacts. No thresholds are adjusted from results.'''),
cell('code','''from pathlib import Path
import sys, json, contextlib
from IPython.display import display, Markdown
import pandas as pd
repo = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "knowledge/research/paper-6-study/relational_experiment.py").exists())
study_dir = repo / "knowledge/research/paper-6-study"
sys.path.insert(0, str(study_dir))
import relational_experiment as experiment
print("Effective frozen protocol parameters:")
display(pd.DataFrame([{"Parameter": k, "Value": str(v)} for k, v in experiment.CONFIG.items()]))
'''),
cell('code','''# Real learning and evaluation, not a canned-output demo.
# Source-scoped facts contain no saved configuration values or credentials.
run_log = repo / "knowledge/research/paper-6-corpus/relational/notebook-execution.log"
with run_log.open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
    study_result = experiment.main()
print("Completed real learning and query application; raw engine logs and a fresh batch are saved.")
display(pd.DataFrame([study_result["split"]]))
'''),
cell('code','''# Independently reconstruct source features, masks, rule counts, metrics and proposals.
import verify_relational
verification = verify_relational.main()
import unittest
suite = unittest.TestSuite()
for pattern in ("test_relational.py", "test_relational_artifacts.py"):
    suite.addTests(unittest.defaultTestLoader.discover(str(study_dir), pattern=pattern))
report = unittest.TextTestRunner(verbosity=1).run(suite)
assert report.wasSuccessful(), "Contract or corruption test failed"
print(f"{report.testsRun} contract/corruption tests passed; {verification['verifiedCases']} masked cases independently checked.")
'''),
cell('code','''# One comparison table; abstentions stay in the all-case denominator.
names = {"anyburl":"AnyBURL rules", "association_guided":"Association shortlist", "exact_counting":"Exact-counting baseline", "center_frequency":"Center-frequency baseline"}
comparison = pd.DataFrame([{"Method": names[k], "Rules": v["rules"], "Cases": v["cases"], "Answered": v["answered"], "Recovered": v["recovered"], "Recovery / all cases": v["recoveryPerCase"], "Recovery / answered": v["recoveryPerAnswer"], "Mean family recovery": v["familyMacroRecovery"]} for k,v in study_result["metrics"].items()])
display(comparison.style.format({"Recovery / all cases":"{:.1%}","Recovery / answered":"{:.1%}","Mean family recovery":"{:.1%}"}))
print("Wire probe:", study_result["learning"]["wireProbe"]["status"], study_result["learning"]["wireProbe"].get("reason", "Completed within budget"))
print("Vocabulary coverage:", study_result["split"]["maskedTargetInTrainingVocabulary"], "/", study_result["split"]["cases"], "masked targets appear in training; all cases remain scored.")
'''),
cell('code','''# Descriptive charts from the just-executed study; no independence or significance claim.
import matplotlib.pyplot as plt
import numpy as np
keys = list(names)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
labels = [names[k] for k in keys]
recovered = np.array([study_result["metrics"][k]["recovered"] for k in keys])
answered = np.array([study_result["metrics"][k]["answered"] for k in keys])
n_cases = study_result["split"]["cases"]
axes[0].barh(labels, recovered, label="Recorded target recovered", color="#479987")
axes[0].barh(labels, answered-recovered, left=recovered, label="Different top prediction", color="#bba16a")
axes[0].barh(labels, n_cases-answered, left=answered, label="Abstained", color="#b7c0cc")
for i,n in enumerate(recovered): axes[0].text(n+2,i,str(n),va="center",fontsize=9)
axes[0].set_xlabel("Masked cases; every case retained")
axes[0].set_title("Recovery, other predictions and abstention")
axes[0].legend(loc="upper center", bbox_to_anchor=(.5,-.19), fontsize=8)
axes[1].barh(labels, [study_result["metrics"][k]["recoveryPerCase"] for k in keys], color="#6189aa", label="All-case recovery")
axes[1].plot([study_result["metrics"][k]["familyMacroRecovery"] for k in keys], range(len(keys)), "o", color="#8a588e", label="Mean family recovery")
axes[1].set_xlim(0,1)
axes[1].set_xlabel("Descriptive fraction; no confidence interval implied")
axes[1].set_title("Case and source-family denominators differ")
axes[1].legend(loc="upper center", bbox_to_anchor=(.5,-.19), fontsize=8)
for ax in axes: ax.spines[["top","right"]].set_visible(False)
fig.tight_layout()
fig_dir = repo / "knowledge/research/paper-6-corpus/relational/figures"
fig_dir.mkdir(exist_ok=True)
fig.savefig(fig_dir / "recovery-comparison.png", dpi=160, bbox_inches="tight")
plt.show()
'''),
cell('code','''# Inspect explicit clauses with both training evidence and separated-source observations.
artifact = repo / "knowledge/research/paper-6-corpus/relational"
rules = json.loads((artifact / "rules.json").read_text())
cases = json.loads((artifact / "cases.json").read_text())
transactions = json.loads((repo / "knowledge/research/paper-6-corpus/patterns/transactions.json").read_text())
def connection(feature):
    center, direction, neighbor, out_port, in_port = json.loads(feature)
    return f"{neighbor}.{out_port} -> {center}.{in_port}" if direction=="in" else f"{center}.{out_port} -> {neighbor}.{in_port}"
def in_evaluation(t):
    return experiment.is_eval(transactions["families"][t["graph"]])
assessment = [t for t in transactions["transactions"] if in_evaluation(t)]
illustrations = sorted(rules,key=lambda r:(-r["jointFamilies"],-r["jointCount"],r["id"]))[:5]
rule_rows=[]
for r in illustrations:
    body=[t for t in assessment if r["body"] in t["items"]]
    joint=[t for t in body if r["head"] in t["items"]]
    rule_rows.append({"IF recorded":connection(r["body"]),"THEN candidate feature":connection(r["head"]),"Train joint/body":f"{r['jointCount']}/{r['bodyCount']}","Train families":r["jointFamilies"],"Eval joint/body":f"{len(joint)}/{len(body)}","Eval observed absences":len(body)-len(joint)})
display(pd.DataFrame(rule_rows))
print("Top five illustrations selected by training breadth; these are conditional observations, not mandatory wiring rules.")
proposals = json.loads((artifact / "proposals.json").read_text())
predictions = json.loads((artifact / "predictions.json").read_text())["anyburl"]
recovered_cases={p["case"] for p in predictions if p["recovered"]}
sample=next((p for p in proposals if p["case"] in recovered_cases and p["status"]=="proposal-only"),None)
if sample:
    print("Illustrative recovered-feature design, not an approved composite:")
    display(pd.DataFrame([{"Role":n["id"],"Type":n["descriptor"]["type"],"Version":n["descriptor"]["version"],"Training source occurrence":n["node"],"Source":n["sources"][0]["sourceUrl"]} for n in sample["nodes"]]))
    display(pd.DataFrame(sample["edges"]))
    display(pd.DataFrame(sample["requiredExposures"]))
    print("Purpose, aliasing, configured values and runtime activation remain unresolved. Full provenance and all proposals are saved as JSON.")
''')]
# Execute exactly the new block. Preserve original outputs and original kernel-side experiment history.
os.environ['JUPYTER_PATH']=str(ROOT/'services/research-notebook/.runtime')
block=nbformat.v4.new_notebook(cells=copy.deepcopy(code),metadata={'kernelspec':{'name':'research-python','display_name':'Research Python','language':'python'}})
NotebookClient(block,timeout=300,kernel_name='research-python',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.write(block,STUDY/'paper-6-relational-executed.ipynb')
s=json.loads((BASE/'relational/summary.json').read_text());v=json.loads((BASE/'relational/verification.json').read_text());m=s['metrics'];split=s['split']
insert=next(i for i,c in enumerate(nb.cells) if c.source.startswith('## 8. Test Design'))
nb.cells[insert:insert]=block.cells
texts={
'## 1. Research Question and Scope':'''### Study C: explicit rule-learning question

Can a bounded learner recover a hidden saved connection feature from other visible local features on retrospective source-separated examples? Can the prediction be written as a schema-based symbolic group proposal with unresolved obligations? This is the current implemented bridge toward generation, alongside the earlier descriptive catalog and boundary workbench. The existing figures inspect evidence; no fourth graph is introduced.''',
'## 3. Hypotheses, Alternatives, and Falsification':'''### Study C alternatives and failure criteria

The protocol fixed the split, rule language, support/group/confidence/lift filters, masking policy and comparison arms before the final execution. It was not preregistered, the corpus was already exposed, and engineering corrections are logged. Compare AnyBURL against exact counting in the same restricted language, a training-association shortlist, and a center-frequency baseline. A masked feature outside the training vocabulary remains a scored case. Failure to beat the frequency baseline on all-case recovery challenges any claim that the learned rules improve overall recovery. Unanswered cases and an infrastructure failure must remain distinct from incorrect or invalid designs.''',
'## 5. Representation and Operational Definitions':'''### Study C data structures

| Record | Fields / meaning | Isolation rule |
|---|---|---|
| Feature fact | (graph-scoped center occurrence, has_feature, feature constant) | One occurrence subject; no type-level subject merge |
| Feature constant | (centerType, direction, neighborType, outputPort, inputPort) | Direction and ports retained; not a component identity |
| Accepted clause | has_feature(X,fB) <= has_feature(X,fA) | Same X, one body atom, distinct known constants, same center type |
| Training rule evidence | Exact body/joint counts, center lift, source-group breadth, witness IDs | Training transactions only |
| Masked case | One hidden feature, all other visible features, source graph/family | Entire target feature removed, not just one duplicate edge |
| Symbolic proposal | Center + fresh neighbor roles, planned ports, training declaration references | Purpose/configuration/aliasing unresolved; no automatic promotion |

This rule language is a relational serialization of the association problem. It is not arbitrary topology or semantic-rule discovery. Shared feature constants would permit cross-center paths in a richer clause language; the accepted one-body same-X clauses forbid that path.''',
'## 6. Rule-Mining Method and Baselines':f'''### Study C: actual PyClause/AnyBURL method

Use the complete frozen assessable transaction set, then split whole recorded source groups by SHA256 of a fixed salt and group ID modulo5. Bucket0 is assessment; all other buckets train. The resulting split has {split['trainNeighborhoods']} training neighborhoods from {split['trainGraphs']} graphs/{split['trainFamilies']} groups and {split['evaluationNeighborhoods']} assessment neighborhoods from {split['evaluationGraphs']} graphs/{split['evaluationFamilies']} groups; group overlap is zero. This is retrospective separation, not pristine held out. Graphs with no assessable transaction do not enter this split.

PyClause is pinned to commit `{s['freeze']['pyclauseCommit']}` and its shipped AnyBURL JAR is hashed. Three serial20-second attempts use one worker and a512MB Java heap. Admit only same-subject single-body feature implications; independently recount their training evidence and require joint>=5, >=2 source groups, confidence>=0.5 and within-center lift>=1.05. Native sampled learner statistics are retained but are not substituted for the exact recount.

| Arm | Learning / selection | What comparison means |
|---|---|---|
| AnyBURL | Union of three bounded runs, restricted language and exact filters | Learned rule coverage in this language |
| Association shortlist | Same learned rules restricted to top100 unordered training-only FP-Growth pairs | Post-learning shortlist tradeoff, not faster learning |
| Exact counting | Enumerate the same feature implications with the same filters | Whether the stochastic learner recovers the directly countable language |
| Center frequency | Most prevalent unseen feature around the center type | A baseline without conditioning on a second connection |

Every learner receives all training facts. The preliminary all-corpus association catalog is not used to select these rules. Query application uses native PyClause with zero U_c unseen smoothing, known answers filtered, all stopping disabled, and independently checked maximum-confidence scores. The final top-one tie-break is canonical feature text, not native frequency tie ordering.

The secondary typed-port occurrence-edge probe is a separate feasibility question; its infrastructure failure is not a head-to-head prediction score.''',
'## 7. Implementation and Reproducibility':'''### Study C implementation

The executable cells directly call `relational_experiment.main()`, then `verify_relational.main()`. The saved code is `relational_experiment.py`; artifacts live in `paper-6-corpus/relational/`. Every invocation uses a fresh engine-batch directory and stores source/protocol snapshots, configs, raw rules and logs. Existing rule paths are rejected before launch, preventing failed reruns from accepting stale files. A timeout terminates the process group, with a kill fallback. Freeze metadata pins transaction/training facts, protocol/code, upstream revision and JAR hashes. Raw workflow code and saved configuration values are never executed or inspected.

On this Mac, upstream documents Windows/Linux support rather than macOS support. The native extension was built using a local Apple Clang/OpenMP adapter and installed libomp; the official source was not modified. Native import and fixed-center query application passed. This local compatibility result is not a claim of upstream-supported macOS deployment.

Primary artifacts: `RELATIONAL-PROTOCOL.md`, `relational_experiment.py`, `verify_relational.py`, `test_relational.py`, `test_relational_artifacts.py`, `relational-engine-research.md`, `summary.json`, `rules.json`, `cases.json`, `predictions.json`, `proposals.json`, `verification.json`, and the executed notebook block. Code cells below perform real learning; their saved output is not a simulated demo.''',
'## 8. Test Design and Evaluation Protocol':f'''### Study C masking, measures and verification

There are {split['cases']} deterministic masked cases among assessment neighborhoods with at least two features. Each target is chosen by a stable case/feature hash; all copies of its feature are removed. A fixed1000-case cap was not reached. {split['maskedTargetInTrainingVocabulary']} targets occur in training vocabulary; the other {split['cases']-split['maskedTargetInTrainingVocabulary']} remain in the denominator. The {split['unmaskedEvaluationNeighborhoods']} other assessment neighborhoods are not scored in this task. No behavioral negatives are created from missing saved edges.

| Check | Implemented verification |
|---|---|
| Rule and graph isolation | Same-X language allowlist; source-family partition; original occurrence IDs |
| Native application | Native candidate sets/scores compared against direct one-body application for every rule arm/case |
| Source fidelity | Rebuild every transaction from original extracted edge witnesses and verify frozen derived-file hashes |
| Counts and comparisons | Independent training support/lift, train-only guidance, all four arms and rate/macro denominators |
| Proposed designs | Training-only descriptors/origins, exact body/head signatures, required exposures, resource fields and type judgments |
| Robustness tests |12 contract tests, including16-answer regression and stale-output rejection |
| Verifier challenge | Eight deliberately corrupted artifacts must be rejected |

Overall recovery divides by all {split['cases']} cases; answered-only recovery divides by the arm's answered cases. Macro-family recovery averages the case fraction within each represented group; source groups do not establish independence. No significance or generalization claim is made. A different top prediction can be a plausible alternative even when it does not recover the one saved target.''',
'## 9. Results and Evidence':f'''### Study C: executed results

| Method | Qualified rules | Answered / {split['cases']} | Recovered recorded target | Recovery / all cases | Recovery / answered | Mean family recovery |
|---|---:|---:|---:|---:|---:|---:|
'''+'\n'.join(f"| {label} | {m[k]['rules']} | {m[k]['answered']} | {m[k]['recovered']} | {m[k]['recoveryPerCase']:.1%} | {m[k]['recoveryPerAnswer']:.1%} | {m[k]['familyMacroRecovery']:.1%} |" for k,label in [('anyburl','AnyBURL'),('association_guided','Association shortlist'),('exact_counting','Exact counting'),('center_frequency','Center frequency')])+f'''

AnyBURL's union contains {s['learning']['engineQualifiedUnion']} qualified implications; exact enumeration contains {s['learning']['exactQualifiedRules']}. Identical task scores, when observed, apply only to this restricted language and run budget. Original sampled per-rule statistics remain in `rules.json`; per-run counts and pairwise overlap remain in `summary.json`.

The rule arm recovered {m['anyburl']['recovered']} targets from {m['anyburl']['answered']} answers, while abstaining on {split['cases']-m['anyburl']['answered']} cases. It did **not** beat the center-frequency baseline on all-case or macro-family recovery. The training-association shortlist reduced the catalog to {m['association_guided']['rules']} rules but reduced coverage and total recovery; no speedup of learning was measured.

{split['cases']-split['maskedTargetInTrainingVocabulary']} of {split['cases']} masked feature signatures were absent from training. That diagnostic helps explain a coverage barrier without excusing it or dropping cases. Exact signature features can fragment across custom names and changed type/port labels across versions. Version itself is not an encoded feature token.

The rule writer returned {s['proposals']['total']} symbolic designs; {s['proposals']['allDeclaredTypeLabelsOverlap']} had declared type-label overlap at both proposed edges and {s['proposals']['catalogUnresolved']} lacked a training descriptor. These three-role/two-edge proposals are connected and acyclic by construction. That does not demonstrate discovery of correct group boundaries or alias identities, active ports, configuration, bounded purpose or task usefulness.

**Secondary probe:** {s['learning']['wireProbe']['status']}: {s['learning']['wireProbe'].get('reason','completed')}. It failed during relation-index preparation, before a scored raw-wiring result. This is not evidence that wiring rules do not exist. No learning-budget or heap-size change was used to conceal the failure.

The executed comparison table, plots, example clauses, witnesses and one explicitly symbolic design appear in the code-output block under Section7. No new network visualization is introduced.''',
'## 10. Critical Discussion and Defense':'''### Study C interpretation

The useful result is a working, auditable rule-learning and proposal path plus a bounded negative result: the accepted rules do not improve overall masked-target recovery over a center-frequency baseline. Better answered-only recovery reflects selective coverage and must not be marketed as overall superiority. The small clause language is directly countable, so a heavier stochastic learner has not demonstrated an advantage over exact counting here.

The association shortlist exposes a coverage/catalog-size tradeoff rather than establishing improved generation. The raw-wiring memory failure shows that representation and relation cardinality can dominate runtime even for a modest triple count; it does not compare the scientific quality of the two representations. Neither phase learns purpose or the correct collective boundary.''',
'## 11. Learning, Revisions, and Follow-Up':'''### Study C learning and revision ledger

| Observation / review finding | Correction or justified next question |
|---|---|
| Native stopping defaults could truncate candidate sets | Disable all stopping;16-answer regression plus complete native/direct comparison |
| Upstream wrapper may exit zero on Java failure | Fresh output directories, output existence and stale-file rejection |
| Initial verifier omitted some metric/proposal checks | Reconstruct baseline/rates, exact synthesized signatures, types/resources; corrupt artifacts deliberately |
| Raw port-edge probe exhausted512MB | Keep failure logs; do not count it as zero rules or silently raise the budget |
| Many assessment signatures absent in training | Study canonicalization and broader evidence before promising transfer |
| Narrow learner does not beat exact enumeration | Keep exact counting as a serious baseline; do not assume a larger engine is automatically better |
| Group purpose and alias identity remain unresolved | Add explicit intent/contracts before calling a symbolic design a useful composite |

Next research should target representation coverage and a task-defined composite contract, while retaining the current protocol as the baseline. This paper does not begin another unbounded graph-building effort.''',
'## 12. Limitations, Bias, and Threats to Validity':'''### Study C limitations

The split is retrospective; the source corpus was already explored. Group hashing creates unequal numbers of graphs and neighborhoods, copied/modified designs may cross undetected, and no population-level inference follows. Native random seeds were not controlled; repeated20-second runs are stochastic observations. The accepted feature rules serialize associations; their utility does not establish richer topology learning. Masked saved-edge features measure source-pattern recovery, not behavior, necessity or the only valid design. Proposal descriptors are chosen from saved training declarations, can pool differing implementations under a type label, and are not certified native Langflow contracts. Fresh symbolic neighbors leave aliasing unresolved; acyclicity is a construction property, not a learned guarantee. Memory failure is infrastructural. No experiment executes a workflow, evaluates a user task or creates a higher plane.''',
'## 13. Outcomes and Conclusion':f'''### Updated conclusion after executable rule learning

Paper6 now contains an actual PyClause/AnyBURL experiment with {s['learning']['engineQualifiedUnion']} qualified local implications, source-linked evidence, retrospective masked-feature comparisons and {s['proposals']['total']} schema-based symbolic proposals. The independent recount checked {v['verifiedCases']} cases and original source witnesses. The main answer is cautious: the rules can support a selective proposal mechanism, but they do not outperform the frequency baseline on total recovery, do not resolve novel feature coverage, and do not establish meaningful composites. This gives an executable baseline and concrete failure conditions for further research, not a general instance generator.''',
'## 14. Review, References, and Reproducibility Appendix':'''### Study C review and primary references

Internal AI static review checked official interfaces and the protocol, identified QA stopping, stale-artifact and verifier-coverage risks, and logged their fixes. The review is recorded in `relational-engine-research.md`; it is not external academic peer review. Twelve contract tests and eight corruption tests passed in the executed notebook, alongside the independent source/metric/proposal recount. No behavioral evaluation or pristine held-out claim is made.

Official references: [PyClause learning wrappers](https://pyclause.readthedocs.io/en/latest/feature/learning.html), [PyClause source and supported installation platforms](https://github.com/symbolic-kg/PyClause), [AnyBURL official project](https://web.informatik.uni-mannheim.de/AnyBURL/). Pinned source, JAR hashes, build adapter, environment lock, frozen protocol, fresh-batch configs/logs and per-case evidence support reproduction. Native AnyBURL confidence, exact neighborhood confidence and the center-conditioned association lift are separately named rather than treated as identical.'''
}
for c in nb.cells:
 if c.cell_type!='markdown':continue
 if c.source.startswith('### Current study status'):
  c.source=c.source.replace('PyClause/AnyBURL, composite generation, evolutionary search and behavioral testing remain future work.','PyClause/AnyBURL feature-rule learning and masked-feature comparisons are now executed below; general composite generation, evolutionary search and behavioral testing remain future work.')
 if c.source.startswith('## 6.'):
  c.source=c.source.replace('The study does not run gSpan, AMIE, AnyBURL, PyClause, Prolog induction or evolutionary search. PyClause/AnyBURL remain the planned subsequent relational stage, informed by these patterns rather than fed only the most frequent facts. A later controlled comparison must test whether association-guided encoding helps relative to an unguided baseline.','Earlier association study: gSpan, AMIE, PyClause/AnyBURL, Prolog induction and evolution were not run in that stage. The subsequent bounded PyClause/AnyBURL experiment is now reported as Study C below; gSpan, AMIE, Prolog induction and evolution remain unexecuted.')
 if c.source.startswith('## 13.'):
  c.source=c.source.replace('| Should they guide PyClause/AnyBURL? | Plausible proposed use | Controlled comparison with an unguided representation |','| Should they guide PyClause/AnyBURL? | Study C tests a post-learning shortlist | No demonstrated learning speedup or general generation benefit |')
  c.source=c.source.replace('**Next justified step:** Inspect selected patterns and their absences, define what a useful candidate boundary means for one task, and design the relational encoding without discarding rare necessary facts. Do not promote catalog items to the Composite plane automatically.','**Earlier next-step proposal:** Inspect selected patterns and define task-specific boundaries. Study C now implements the first explicit feature-rule experiment; automatic Composite promotion remains unjustified.')
 if c.source.startswith('## 14.'):
  c.source=c.source.replace('Planned subsequent stage: [PyClause]','Subsequent Study C uses [PyClause]')
 for heading,text in texts.items():
  if c.source.startswith(heading):
   c.source=c.source.split('\n\n<!-- relational-extension -->')[0]+'\n\n<!-- relational-extension -->\n'+text
for c in nb.cells:
 if c.source.startswith('### Current study status'):
  a=s['metrics']['anyburl'];b=s['metrics']['center_frequency']
  c.source=c.source.split('\n\n**Latest executed finding:**')[0]+f"\n\n**Latest executed finding:** {a['rules']} qualified local rules recovered {a['recovered']} of {a['cases']} hidden connection features; the center-frequency baseline recovered {b['recovered']}. The rules were more selective, not better on overall recovery. Section7 contains the real executable cells; Section9 interprets the results. Purpose, configuration and useful-composite validation remain open."
old=nbformat.read(backup,4)
assert nb.cells[0].source==old.cells[0].source
for title in ['## Connected pattern explorer','## Candidate group explorer','## Interactive corpus topology']:
 assert next(c.source for c in nb.cells if c.source.startswith(title))==next(c.source for c in old.cells if c.source.startswith(title))
nbformat.validate(nb);nbformat.write(nb,PAPER)
print(json.dumps({'status':'executed and integrated','newCodeCells':sum(c.cell_type=='code' for c in block.cells),'metrics':m,'verification':v},indent=2))
