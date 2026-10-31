from pathlib import Path
import json,nbformat

D=Path(__file__).resolve().parent
P=D.parent/'notebooks/Paper 10 - Capability Search for Instance Building.ipynb'
if P.exists():
    prior=nbformat.read(P,4)
    if prior.metadata.get('paper10_algorithm_revision',1)>=2:raise RuntimeError('Revision-2 notebook is maintained in place; do not overwrite it with the historical generator')
    if prior.metadata.get('paper10_generator')!='capability-search-v1':raise RuntimeError('Existing user notebook will not be overwritten')
n=nbformat.v4.new_notebook(metadata={'kernelspec':{'display_name':'Research Python','language':'python','name':'research-python'},'language_info':{'name':'python','version':'3.12'},'paper10_generator':'capability-search-v1'})
def md(s):n.cells.append(nbformat.v4.new_markdown_cell(s))
def code(s):n.cells.append(nbformat.v4.new_code_cell(s))
md('''# Paper 10 — Capability Search for Instance Building
## Find the pieces before building the instance

**Purpose.** Search our preserved Langflow corpus using a capability question. Return whole templates, archived component definitions and observed connected groups with original sources, port declarations, configuration requirements, dependencies and explicit fit limits. This paper is exclusively a search-engine study: it does not assemble or deploy instances.

**Abstract.** Filename search misses reusable functions whose names differ from the user's question. We construct a local hybrid retrieval engine over a frozen, provenance-backed corpus. Exact-byte duplicate copies, fixtures and incompatible formats are excluded from the searchable source set; every included source is hash-verified. Field-aware lexical retrieval and existing local embeddings are fused, with an explicit small capability vocabulary and an evidence screen. Results retain real wiring and boundary connections. An exposed eight-query development comparison measures expected component-type presence in the top six template results; source and failure-path checks qualify the engine separately. Retrieval does not establish component compatibility, composite validity, profitable opportunities or execution success.

### Search the library
Run the next two cells, type a question and click **Search library**. Select **Whole templates**, **Components**, or **Connected groups** to inspect one kind. **Explain capabilities** separates recognized multi-capability questions and shows gaps. No corpus template or archived code is executed.
''')
code('''import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from IPython.display import display,JSON,Markdown
import pandas as pd
repo=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'knowledge/research/paper-10-study/search_engine.py').exists())
study=repo/'knowledge/research/paper-10-study'
sys.path.insert(0,str(study))
from search_engine import CorpusSearch,render_results
engine=CorpusSearch()
display(pd.DataFrame([{'Record kind':k,'Searchable records':v} for k,v in engine.stats['kinds'].items()]))
print('All indexed sources match the corpus snapshot:',engine.corpus_current)
print('Local embedding model matches the indexed binding:',engine.embedding_current)
print('Definitions are archived variants, not a count of installed current components or validated composites.')
''')
code('''from notebook_ui import show_search
search_controls=show_search(engine)
# For a plain code-cell search without widgets, use:
# render_results(engine.search("Find company pricing and competitor research", kind="template"))
''')
md('''## 1. Research question, hypotheses and critical alternatives

**Question:** Can a source-grounded capability search retrieve useful building-piece candidates that filename matching misses, while preserving the distinction between an observed graph and a validated composite?

| Hypothesis | Test | What would refute or limit it |
|---|---|---|
| H1: capability retrieval improves coverage | Same eight authored queries, template search space and top-six cutoff across filename, field-lexical and hybrid arms | No advantage, or advantages that disappear under manual relevance review |
| H2: results are grounded | Resolve source hashes, graph pointers, actual nodes and boundary edges | A result or connection cannot be traced to an original file |
| H3: the engine states gaps | Unknown query, incomplete monetization evidence, private-account request, unavailable embeddings | It invents capabilities or silently claims full coverage |
| H4: results support inspection | Inputs, outputs, configuration names and dependencies are directly inspectable | These fields require invention or saved secrets are exposed |

**Alternatives:** filename search may be sufficient; rich lexical fields may provide most of the benefit; embeddings may add little or introduce false matches. A returned graph can contain a reference component without being appropriate for the task. Human relevance and eventual assembly benefit are distinct future evaluations.
''')
md('''## 2. Corpus scope, provenance and data model

The source snapshot contains 2,942 collected records including duplicates, fixtures and incompatible formats. The engine uses **1,148 distinct eligible non-fixture Langflow contents**. It does not advertise 2,942 independent usable templates. All recorded origins of an included byte-identical file are retained.

| Record | Definition | Does not mean |
|---|---|---|
| Template | Original preserved workflow graph with its description and recorded nodes/edges | Verified reusable composite or successful execution |
| Component | Distinct archived definition signature; occurrences point back to source graphs | Installed current component or independently tested building block |
| Connected group | Two-to-four-node one-hop neighborhood with actual internal and crossing edges | Meaningful composite boundary or inferred higher plane |
| Search match | Text/embedding-ranked candidate with matched evidence | Calibrated probability, semantic proof or compatible connection |

Saved operational inputs, credential values and executable component code are excluded. Selected redacted prompt and schema descriptions are indexed as untrusted capability evidence. The engine reads archived definitions as data. Required settings are marked for binding review rather than declared missing from the original. Notes, prompts and descriptions can be incomplete or misleading; they are never executed as instructions.
''')
code('''display(JSON(engine.stats,expanded=False))
print('Index derivation failures:',len(engine.stats['failures']))
''')
md('''## 3. Method: retrieval, evidence and fit

| Stage | Implemented mechanism | Limitation |
|---|---|---|
| Extract | Verify bytes; resolve archived graph pointers; retain types, fields, declared dependencies and ports | Archived definitions may not match the present Langflow library |
| Normalize | Exclude fixture/incompatible records, collapse exact file copies, keep every recorded origin | Forks and similar graphs can still be dependent examples |
| Retrieve | SQLite FTS5 field-aware BM25 plus local Nomic embeddings | Semantic similarity alone does not establish a capability |
| Rank | Weighted reciprocal-rank fusion, direct/capability evidence screen, structural-variant display diversification | Authored heuristic, not a learned or calibrated probability |
| Explain | Matched terms/facets, source links and recorded configuration/graph boundaries | No automatic purpose, behavior or type-compatibility proof |
| Answer | Separate recognized capability facets and report missing/adjacent evidence | Small explicit ontology, not universal decomposition |

Embedding inference stays on the existing local service. A missing or changed model binding produces an explicit lexical fallback. Changed original source files are withheld from results; a changed collection index produces a rebuild warning. Similar displayed versions remain individually inspectable and are not counted as independent designs.

**Monetization guard:** company pricing, ad-spend KPIs or financial analysis are not evidence of creator earnings. Search has no access to private channel analytics. A retrieved financial pattern may be useful, but a supported audience/revenue connector, realistic costs and evaluation are still needed.
''')
md('''## 4. Executed questions and inspectable results

The examples below are actual searches over the local index. These static outputs remain readable after a kernel stops. Use the search controls for new questions; if reopening, rerun the setup and controls cells to restore interactivity.
''')
code('''question="Find audience feedback, competitor pricing and monetization pieces"
answer=engine.answer(question,k=2)
for capability,section in answer['sections'].items():
    display(Markdown('### '+capability.title()))
    render_results(section)
display(JSON({'question':answer['question'],'scope':answer['scope'],'gaps_by_capability':{k:v['gaps'] for k,v in answer['sections'].items()}},expanded=False))
''')
md('''## 5. Connected-group verification

This is a small recorded group from a real source, not a new composite or another layer. The diagram displays only its observed internal edges. Crossing edges and required configuration remain in the accompanying table/card. Node position is a layout choice, not hierarchy or execution order. Two nodes of the same type remain separate occurrences.
''')
code('''group_answer=engine.search("YouTube comments and transcripts",kind="connected_group",k=1)
group=group_answer['results'][0]
assert engine.verify_source(group['id'])
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
nodes=group['nodes'];position={n['node_id']:(i*2,0.4 if i%2 else 0) for i,n in enumerate(nodes)}
fig,ax=plt.subplots(figsize=(10,3.2))
for n in nodes:
    x,y=position[n['node_id']];ax.text(x,y,n['type']+'\\n'+n['node_id'][-8:],ha='center',va='center',fontsize=8,bbox={'boxstyle':'round,pad=.5','facecolor':'#edf2ff','edgecolor':'#4263eb'})
for edge in group['edges']:
    a,b=position[edge['source']],position[edge['target']]
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,shrinkA=40,shrinkB=40,connectionstyle='arc3,rad=.2'))
    ax.text((a[0]+b[0])/2,(a[1]+b[1])/2-.3,(edge['source_port'] or '?')+' → '+(edge['target_port'] or '?'),fontsize=7,ha='center')
ax.set_xlim(-1,max(x for x,y in position.values())+1);ax.set_ylim(-1,1.1);ax.axis('off');ax.set_title('Observed connected group — not a validated composite');plt.tight_layout();plt.show();plt.close(fig)
display(pd.DataFrame([{'Boundary':'incoming',**e} for e in group['boundary']['inputs']]+[{'Boundary':'outgoing',**e} for e in group['boundary']['outputs']]))
render_results(group_answer)
''')
md('''## 6. Verification and fault cases

Checks cover credential/code exclusion, raw port preservation, unresolved ports, complete indexing, unknown terms, invalid filters, query isolation, result kinds, source hashes, multi-capability gaps, actual connected-group boundaries and inspection immutability. A pass qualifies these properties, not semantic task success. No downloaded template is executed.
''')
code('''import unittest
suite=unittest.defaultTestLoader.discover(str(study),pattern='test_search.py')
test_result=unittest.TextTestRunner(verbosity=1).run(suite)
assert test_result.wasSuccessful()
print('Source/retrieval checks passed:',test_result.testsRun)
''')
md('''## 7. Baseline comparison and results

Eight authored development questions ask about video speech, audience comments, company profiles, page reading, document chunks, typed JSON, relational querying and web evidence. Each arm searches templates and returns at most six results. The recorded measure is whether a reference component type occurs in those results. This is an exposed, weak relevance proxy. No held-out data, independent reviewer or assembly-time advantage is claimed.
''')
code('''evaluation=json.loads((study/'EVALUATION.json').read_text())
display(pd.DataFrame(evaluation['rows'])[['case','arm','reference_type_present_at_6','returned','seconds']])
counts=pd.Series(evaluation['hits'],name='Reference-type hits in 8 development cases')
display(counts.to_frame())
fig,ax=plt.subplots(figsize=(7,3));counts.plot.bar(ax=ax,color=['#adb5bd','#748ffc','#4263eb']);ax.set_ylim(0,8);ax.set_ylabel('Cases, not percentage accuracy');ax.set_title('Top-six template retrieval: exposed development comparison');plt.xticks(rotation=0);plt.tight_layout();plt.show();plt.close(fig)
print(evaluation['scope'])
''')
md('''## 8. Counterarguments, learning and limits

Rich metadata explains much of the observed advantage over filenames; embeddings are not assumed to be the only cause. Matching a component type can count an irrelevant workflow as a hit. Similar template families reduce independence. The hand-authored capability vocabulary can miss unfamiliar domains, and descriptions or prompts can exaggerate behavior. Credentials, provider APIs, costs, current component versions, actual compatibility, license suitability and safe execution still need qualification before reuse.

The engine must be allowed to return no match or partial coverage. In particular, finding a pricing extractor does not supply monetization probabilities. A financial KPI pattern is an adjacent reusable calculation, not a creator revenue predictor. Source-linked inspection is the deliverable.

## 9. Conclusion and next evaluation

The delivered engine searches the preserved corpus by capability and exposes original sources and recorded contracts. The development comparison and source checks support this bounded retrieval implementation. They do not establish a generally reliable instance generator or a faster assembly process. A subsequent evaluation should use independently authored capability questions and human relevance judgments, then measure whether retrieved pieces reduce verified assembly effort. No instance is built in this paper.

## 10. Review and reproducibility disclosures

Internal implementation and automated checks only; no external peer review. Code, index report and evaluation are under `paper-10-study`. Derived index/cache/vectors are local and rebuildable. Earlier papers are preserved by hash. The search UI uses ordinary Jupyter widgets and does not alter Jupyter's application interface.
''')
nbformat.validate(n);nbformat.write(n,P);print(P)
