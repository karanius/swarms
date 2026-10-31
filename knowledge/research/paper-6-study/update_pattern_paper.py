"""Integrate the bounded exploratory study; preserve the original abstract and map cells."""
import hashlib,json
from pathlib import Path
import nbformat
from nbclient import NotebookClient
import os
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'knowledge/research/paper-6-corpus';PAPER=ROOT/'knowledge/research/notebooks/Paper 6 - Rule Mining from Langflow Templates.ipynb'
n=nbformat.read(PAPER,4);abstract=n.cells[0].source
backup=Path(__file__).with_name('paper-6-before-pattern-study.ipynb')
if not backup.exists():nbformat.write(n,backup)
data=json.loads((BASE/'patterns/index.json').read_text());stats=data['stats'];verify=json.loads((BASE/'patterns/verification.json').read_text());r=data['rules'][0]
content={
1:'''**Research question:** Can small, source-linked pairs of recorded connections around the same Langflow component occurrence be discovered and presented with reproducible support, observed absences and inspectable original examples?

This is a bounded exploratory study of connected relationships. It does not yet ask the algorithm to generate composites. The new focused visualization complements the existing corpus overview; the original map remains available.

| Scope item | Implemented scope | Not established |
|---|---|---|
| Layer | Component occurrences and recorded named-port relations | Composite, Flow or Process generation |
| Pattern | Two distinct incident-edge signatures sharing one center occurrence | Arbitrary subgraph mining or useful abstraction boundaries |
| Configuration | Existing source metadata retained; no configuration values used | Configuration dependency discovery or credential validity |
| Association | One observed edge feature associated with a second in the same neighborhood | Causation, mandatory wiring or task success |
| User artifact | Searchable diagrams, supporting/without-head examples, highlighted originals and sources | A user-study finding about comprehension |

**Practical objective:** Replace an undirected search through a large visual overview with one inspectable local relationship at a time. Any future promotion to Composite must add purpose, boundary and obligation evidence.''',
2:'''The study inherits the machine's distinction between component types, scoped occurrences, assemblies and higher-plane representations. Paper 6 now adds empirical corpus analysis; it does not retroactively validate the prior generation theories.

| Prior work / source | Contribution used | Limit of use |
|---|---|---|
| Papers 1–5 | Vocabulary, iteration, boundary and evidence discipline | Their broader generation claims are not tested here |
| [Langflow component documentation](https://docs.langflow.org/components/) | Context for typed ports and saved component configuration | Historical exports may differ; recorded names do not certify active or compatible ports |
| [mlxtend FP-Growth](https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/) and [association rules](https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/) | Existing itemset miner and conditional co-occurrence metrics | A basket association has only the semantics we explicitly encode |
| gSpan and AMIE literature dossier below | Distinguishes structural motifs from relational implications | Neither engine is run in this experiment |
| Typed composition and evolutionary sources below | Potential later validation and search mechanisms | No formal contract proof, Prolog learner, evolutionary experiment or NEAT adaptation is implemented |

The original graphs, source origins and corpus topology remain separate from the derived association catalog. Static graph designs are not execution logs.''',
3:'''These are bounded expectations and falsification criteria, not preregistered statistical hypotheses. Corpus-wide exploration and prior map exposure mean there is no untouched evaluation set in this study.

| ID | Expectation / question | What would challenge it | Observed status |
|---|---|---|---|
| H1 | At least some incident-edge pairs recur in five or more assessable neighborhoods and span multiple recorded source groups | No pair passes the fixed counting threshold, or all are confined to one group | Observed descriptively; 570 directional associations span at least two recorded groups |
| H2 | Scores and diagram witnesses can be traced to exact scoped source occurrences | A count, source, center or edge does not match its persisted evidence | Nine controlled checks and a separate full recount passed; this is implementation evidence |
| H3 | A pooled lift score may overstate interestingness because encoded features imply the center type | Conditioning on center type leaves all comparisons unchanged | The leading Agent example changes from 11.83× pooled lift to 1.11× within-Agent lift; no universal claim |
| H4 | Recurrence identifies useful reusable composites | Task or boundary evidence fails, or usefulness is unmeasured | Not tested; recurrence alone is insufficient |

No p-values, significance claims or confidence intervals are asserted. Neither a high observed confidence nor a source-group count establishes a universal rule.''',
4:'''The analysis uses the frozen topology extraction from the archived Langflow corpus. Byte-identical source files are represented once, while all origins remain attached. Nested graph objects remain separate and may still be dependent.

| Population / grouping | Observed count / policy |
|---|---|
| Corpus format policy | Langflow only; Flowise, mixed and unknown remain separate in the inventory |
| Nonfixture extracted graph objects | 1,149 |
| Component occurrences in those objects | 8,528 |
| Assessable edge-bearing neighborhoods | 8,258 |
| No incident edge | 137; excluded from this edge-conditioned population, not counted as negatives |
| Unknown incident endpoint/type/port or self-loop bucket | 133; whole neighborhood excluded |
| Above 24 distinct incident features | 0 in this run; exclusion bound retained in protocol |
| Recorded source groups | 209; union of all repository/origin links over exact duplicates, including fixture origins before filtering |
| Largest recorded group | 499 nonfixture graphs |
| Evaluation exposure | Entire included corpus exploratory; no held-out/generalization assessment |

Groups are provenance safeguards, not proof of independent authorship. Modified copies and shared tutorials may remain across groups; broad repository unions may also over-merge unrelated examples. Unknown revision/license information remains explicit in the corpus inventory. Freeze data in `patterns/index.json` records corpus/index hashes, an aggregate digest of every derived graph file, script hash, parameters and runtime package versions.''',
5:'''A transaction is one **graph-scoped center component occurrence with at least one recorded incident edge**. All its incident records must have resolved non-note endpoints, non-Unknown type labels and named source/target handles. Self-loop and unresolved neighborhoods are excluded. This is saved-handle resolution, not declared-port membership, active-output verification or type checking.

| Record | Fields | Meaning |
|---|---|---|
| Neighborhood | graph ID, center occurrence ID/type, binary item set, raw edge witnesses | One scoped transaction; never joins separate component occurrences |
| Edge feature | center type, incoming/outgoing direction, neighbor type, output name, input name | Retains direction and named ports; ignores configuration values and pools versions |
| Association | first feature A, additional feature B, counts, confidence, lifts, graph/group breadth | Observational conditional relationship |
| Example | transaction, source graph, center ID, all matching edge IDs, one preview edge per feature | Preview contains two actual connections and two or three distinct nodes |
| Source | every original URL/path/revision and origin count | Byte deduplication does not discard origins |

Multiple raw edges with one feature count once in the transaction, but every raw witness is retained. Two features may reuse the same outside occurrence; the preview uses the actual identity, not three invented nodes.

For N assessable neighborhoods, n(A) with the first feature and n(A,B) with both, support is n(A,B)/N and observed confidence is n(A,B)/n(A). Center-conditioned lift is confidence divided by n(B)/N_center, where N_center counts assessable neighborhoods of the shared center type. These are positive-count ratios; confidence is not a calibrated behavioral probability. “Without B” means no B record around that assessable center, not that B is impossible.''',
6:'''The implementation uses `mlxtend` FP-Growth on binary sparse neighborhood transactions, followed by one-item-to-one-item association rules. Connection signatures encode their center type, so a co-occurring pair necessarily shares that type; a separate assertion verifies this. The original transaction guarantees the same occurrence, not merely the same type.

| Parameter / control | Fixed value or treatment |
|---|---|
| Minimum joint count | 5 neighborhoods; exact count reasserted after mining |
| Maximum itemset size | 2 |
| Maximum distinct incident features | 24; larger neighborhoods excluded and counted |
| Rule confidence filter | 0; all qualifying directed pair associations retained |
| Catalog display cap | 1,000; all 890 fit in this run; full summaries downloadable |
| Ranking | Joint source-group breadth, joint graph count, joint neighborhood count, confidence, stable ID |
| Confidence denominator | Assessable neighborhoods containing A |
| Lift shown in UI | Within the common center type; pooled engine lift retained separately |
| Connection semantics | Observed target selection plus wiring, not wiring conditioned on target availability |

The study does not run gSpan, AMIE, AnyBURL, PyClause, Prolog induction or evolutionary search. PyClause/AnyBURL remain the planned subsequent relational stage, informed by these patterns rather than fed only the most frequent facts. A later controlled comparison must test whether association-guided encoding helps relative to an unguided baseline.''',
7:'''The implementation consists of a source-preserving extractor, a bounded miner, a separate evidence verifier, a focused visualization and notebook integration. Downloaded node code is never imported or executed; resource values and credentials are not features.

| Artifact | Responsibility |
|---|---|
| `build_topology.py` | Static extraction used by the unchanged corpus overview and pattern study |
| `mine_patterns.py` | Scope/filtering, binary features, provenance unions, FP-Growth, exact scoring and witness catalog |
| `verify_patterns.py` | Separate recount and recorded-edge preview verification against persisted inputs |
| `patterns/index.json`, `all-rules.json`, `rules/`, `transactions.json` | Frozen analysis, complete rule summaries, witness data and transactions |
| `pattern-explorer/` | New interface; existing `corpus-explorer/` remains unchanged |
| `pattern-requirements.txt`, `pattern-environment.lock` | Selected package pins and actual resolved environment |

The API serves a fixed analysis index or a validated rule ID present in the current complete rule list. Old per-rule files from previous runs are not eligible to be served merely because they remain on disk. Source examples load the existing graph-data endpoint. The notebook figure is a local host-owned embed and requires no notebook kernel to explore.''',
8:f'''Verification separates implementation correctness from scientific generalization. The experiments use saved source data; no workflow, model call or task-success experiment is run.

| Check | Evidence / outcome | What it cannot establish |
|---|---|---|
| Controlled neighborhood checks | 9 passed: separate centers, binary duplicate edges, shared neighbors, unknown exclusions, zero-degree handling, no invented inactive outputs, hand-counted confidence/lift, all-origin grouping, engine reference counts | Reliability over every possible export |
| Existing extraction checks | 8 passed for the prior topology extractor | Active outputs or runtime validity |
| Separate catalog recount | {verify['rulesRecounted']} rules recounted | Unseen-family prediction |
| Actual preview-edge audit | {verify['witnessPreviewsChecked']:,} previews across {verify['sourceGraphsChecked']} source graphs checked | Behavioral correctness |
| Freeze check | Topology index and aggregate graph-file digest match | Authenticity beyond the archived provenance |
| Frontend build / browser checks | Recorded in the delivery evidence after interaction verification | User comprehension or general performance benchmarks |

All examples are exposed for exploration. A future generalization experiment needs newly frozen source families and a separate tuning/evaluation policy; these exploratory results must not be relabeled held out.''',
9:f'''The completed pass yielded the following descriptive results. These counts refer to the specified filtered corpus and transaction encoding, not all possible workflow patterns.

| Observed result | Count |
|---|---:|
| Distinct incident-edge features | {stats['distinctFeatures']:,} |
| Frequent itemsets of size one or two | {stats['frequentItemsets']:,} |
| Repeated two-feature connection pairs | {stats['repeatedConnectedPairs']} |
| Directional A→B associations | {stats['directedAssociationRules']} |
| Associations spanning at least two recorded source groups | 570 |
| Associations confined to one recorded group | 320 |
| Runtime of recorded final mining pass | {stats['runtimeSeconds']} seconds; one local observation, not a benchmark |

**Worked result:** Around an Agent occurrence, ChatInput.message → Agent.input_value occurs in 357 assessable neighborhoods. In 242 of those, Agent.response → ChatOutput.input_value also occurs: 67.8% observed confidence. The additional connection is absent in 115 recorded neighborhoods. Joint witnesses span 242 graph objects and 50 recorded source groups. The 115 without-head neighborhoods occupy 109 graphs; some graphs have both kinds of centers, so graph counts cannot simply be added.

The new explorer displays these actual examples and absent-head observations, not invented positive/negative tasks. Each diagram uses recorded occurrence IDs and port labels. Source aliases and duplicated origins remain inspectable.''',
10:'''The evidence supports an inspectable connection-association catalog, not general composite formation. Several competing explanations remain plausible.

| Claim or tempting interpretation | Critical response | Required next evidence |
|---|---|---|
| High confidence means the second connection is necessary | It may reflect typical examples, target choice or common output conventions | Purpose-specific requirements and independent cases |
| Repeated pair means a composite | Boundary, required inputs, resources and usefulness have not been established | Explicit formation contract and boundary checks |
| Many graphs mean many independent examples | Mirrors, nested exports, versions and multiple centers are dependent | Better lineage grouping and fresh external families |
| A large lift means a remarkable discovery | Center labels constrain which features can coexist | Appropriate center-conditioned baseline |
| Missing head is an error | It is only absent from that saved neighborhood | A stated requirement before any violation judgment |

For the leading Agent association, pooled lift is 11.83× while within-Agent lift is 1.11×. The pooled score compares features that already imply Agent against a population dominated by other center types. We show the narrower baseline to avoid overstating the relationship. This example illustrates a confound; it is not a full method comparison.''',
11:'''Implementation learning is recorded without rewriting the study as a predicted success.

| Issue learned or checked | Disposition | Remaining limit |
|---|---|---|
| Whole-workflow baskets can join unrelated pieces | Transactions now share an actual center occurrence | Only a local two-feature view |
| Repeated raw edges can inflate support | Binary features; preserve every raw witness separately | Multiplicity is not modeled as a predictor |
| Two connections need not mean three nodes | Alias-aware preview selects real endpoints | Pair summaries still pool alias configurations |
| Named handles can be mistaken for validated ports | Wording restricted to saved named-handle evidence | Activation/type compatibility unverified |
| Byte deduplication can sever family links | Union all retained origins, including fixture origins, before filtering | Modified-copy links incomplete |
| A hash of the index alone does not freeze graph data | Add aggregate digest over every loaded graph file | Raw originals remain necessary for reproduction |
| A rule file can outlive a rerun | API validates IDs against the current full rule list | Old local files are not a version-history service |
| A “without” tab can show a previous positive example | Category change selects its own first example or an explicit empty state | No inferred missing edge is drawn as real |

Future work should compare richer neighborhoods, explicit configuration relations and relational learners only after fixing the new question and evidence conditions. Evolution remains a candidate search mechanism, not an assumed improvement.''',
12:'''| Threat | Effect | Current handling / residual limit |
|---|---|---|
| Selection into public templates | Popular tutorials and demonstrations dominate | No claim about all real Langflow deployments |
| Exact-byte deduplication only | Semantically identical modified graphs can remain | Preserve source groups; no claim of semantic uniqueness |
| One large provenance group | 499 graphs share a grouped origin component | Report breadth separately; not independent-sample inference |
| Unknowns excluded | Difficult or historical neighborhoods may be underrepresented | Publish 133 exclusions and exact criteria |
| Zero-degree population excluded | Confidence is conditional on a recorded incident edge | Do not generalize to all component occurrences |
| Version pooling and custom types | Same labels need not mean same implementation | Inspect exact source/occurrence version; no runtime claim |
| Pair language and hub bound | Larger or cyclic patterns can be missed | Scope explicitly limited; self-loop bucket excluded |
| Whole-corpus exploration | Selection and interpretation use the same data | No test accuracy or generalization result |
| Schema-level ports | Saved names may be stale or dynamically inactive | Do not call these connections type-validated |
| Observed absence | Missing B may reflect intended task differences or incomplete designs | Not a behavioral counterexample or prohibited connection |

There are no validated new composites and no evidence yet that an association-guided encoding outperforms a relational baseline.''',
13:'''The implemented outcome is a source-backed local pattern explorer that makes concrete connection evidence inspectable. It adds a focused view while preserving the original corpus overview.

| Question | Supported outcome | Open question |
|---|---|---|
| Do repeated local connection pairs exist under this encoding? | Yes: 445 qualifying pairs and 890 directional associations | Stability under other encodings and source populations |
| Can counts and diagrams be audited? | Separate recount and source-edge checks passed | Wider extraction robustness and user evaluation |
| Are these useful composites? | Not established | Purpose, resources, boundary and behavioral evidence |
| Should they guide PyClause/AnyBURL? | Plausible proposed use | Controlled comparison with an unguided representation |

**Next justified step:** Inspect selected patterns and their absences, define what a useful candidate boundary means for one task, and design the relational encoding without discarding rare necessary facts. Do not promote catalog items to the Composite plane automatically.''',
14:'''**Review disclosure:** The methodological review is internal AI review, not external academic peer review. The reviewer did not execute the miner; execution and verification reports are separate artifacts.

| Review finding | Response / evidence |
|---|---|
| Count at the same scoped center; handle fanout and aliasing | Binary occurrence transactions, actual two-edge previews, nine controlled checks |
| Preserve duplicate origins for grouping | Provenance union runs over all extracted graphs before fixture filtering |
| Do not confuse saved handles with active type-safe ports | Qualified throughout method, UI and limits |
| Hash actual graph data | Aggregate graph digest added and rechecked |
| Recompute support threshold and evidence counts | Minimum joint count asserted; separate full recount |
| Avoid stale results and fabricated diagrams | Current-ID API guard and exact preview edge IDs |

Primary implementation references: [FP-Growth](https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/), [association rule metrics](https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/). Planned subsequent stage: [PyClause](https://pyclause.readthedocs.io/en/latest/feature/learning.html) and [AnyBURL](https://web.informatik.uni-mannheim.de/AnyBURL/). The earlier fourteen-source research dossier is retained below as background; its direct-relational-first recommendation predates the current association-first decision.

**Reproduction:** Use the recorded Python environment, rebuild topology only if deliberately changing the corpus snapshot, run `mine_patterns.py`, then `verify_patterns.py` and the controlled tests. Snapshot hashes must match before comparing outputs. Raw source files stay unchanged and local. No mining result is claimed beyond this bounded exploration.'''}
for c in n.cells:
 if c.metadata.get('paper6_template'):
  num=int(c.source.splitlines()[0].split()[1].rstrip('.'));heading=c.source.splitlines()[0];c.source=heading+'\n\n'+content[num];c.metadata['paper6_study_written']=True
# Update earlier planning notes without changing the original abstract.
for c in n.cells:
 if c.metadata.get('paper6_association_first'):
  c.source=c.source.replace('This is the new first experiment; no mining has run yet.','This plan is now implemented in the bounded connected-neighborhood study in Sections 4–13. Results are exploratory; the relational stage remains planned.')
 if c.metadata.get('paper6_strategy'):
  c.source=c.source.replace('These are planned phases, not completed results.','These are the overall phases. The bounded exploratory connected-pattern study below completes an initial slice; it does not complete composite generation or generalization evaluation.')
 if c.metadata.get('paper6_dossier'):
  c.source=c.source.replace('## Main finding','## Historical literature synthesis — before the association-first experiment',1)
# Remove only our own prior generated study additions on rerun.
n.cells=[c for c in n.cells if not c.metadata.get('paper6_pattern_generated')]
pos=next(i for i,c in enumerate(n.cells) if c.metadata.get('paper6_topology'))
n.cells[pos:pos]=[nbformat.v4.new_markdown_cell('## Connected pattern explorer\n\n[Open the focused pattern explorer](/pattern-explorer/).',metadata={'paper6_pattern_generated':True}),nbformat.v4.new_markdown_cell('### How to use this figure\n\nChoose an association on the left. The mint connection is the first observed feature; the violet connection is the additional feature. Compare examples with both connections and examples without the additional connection, then open an original workflow with the witness highlighted. These are actual source edges, not generated composites. The original corpus overview remains below.',metadata={'paper6_pattern_generated':True})]
status=nbformat.v4.new_markdown_cell('### Current study status\n\nThe original proposal abstract above is preserved. The paper now includes an executed **exploratory connected-pattern association study**, a new focused visualization, measured distributions and a separate evidence recount. PyClause/AnyBURL, composite generation, evolutionary search and behavioral testing remain future work.',metadata={'paper6_pattern_generated':True})
n.cells.insert(1,status)
# Execute only display/verification cells, never workflows or the entire paper.
mini=nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("from pathlib import Path\nimport json, hashlib\nfrom IPython.display import display, Image\nrepo = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'knowledge/research/paper-6-corpus/patterns/index.json').exists())\nbase = repo / 'knowledge/research/paper-6-corpus'\nanalysis = json.loads((base / 'patterns/index.json').read_text())\nverification = json.loads((base / 'patterns/verification.json').read_text())\nassert hashlib.sha256((base / 'topology/index.json').read_bytes()).hexdigest() == analysis['freeze']['topologyIndexSha256']\nprint(json.dumps({'analysis': analysis['stats'], 'verification': verification}, indent=2))"),nbformat.v4.new_code_cell("display(Image(filename=str(base / 'patterns/figures/coverage.png')))\ndisplay(Image(filename=str(base / 'patterns/figures/association-distribution.png')))" )])
os.environ['JUPYTER_PATH']=str(ROOT/'services/research-notebook/.runtime')
NotebookClient(mini,timeout=120,kernel_name='research-python',resources={'metadata':{'path':str(ROOT)}}).execute()
for c in mini.cells:c.metadata['paper6_pattern_generated']=True
loc=next(i for i,c in enumerate(n.cells) if c.metadata.get('paper6_template') and c.source.startswith('## 9.'))
n.cells[loc+1:loc+1]=[nbformat.v4.new_markdown_cell('### Executed frozen-output inspection and measured figures\n\nThese cells read the recorded analysis and render its actual figures. They do not rerun mining or execute any workflow. To reproduce mining, use the versioned script and frozen inputs described in Section 14.',metadata={'paper6_pattern_generated':True}),*mini.cells]
assert n.cells[0].source==abstract
nbformat.validate(n);nbformat.write(n,PAPER)
print('Updated fourteen sections; preserved abstract and old map; embedded new figure; executed two frozen-output cells.')
if __name__=='__main__':pass
