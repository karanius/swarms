"""Recount actual stock request outputs and checked analyst layer interpretation."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
def build():
 setup='''from pathlib import Path
import json,sys,hashlib,collections
from IPython.display import display,Markdown
ROOT = next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'knowledge/research/paper-6-study').exists())
study=ROOT/'knowledge/research/paper-6-study'; subject=study/'stock-builder'; art=study/'assistant-workspace/artifacts'
sys.path.insert(0,str(subject))
from verify_interpretation import verify
run=subject/json.loads((subject/'latest.json').read_text())['run']
stream=subject/json.loads((subject/'latest-stream.json').read_text())['run']
flow=json.loads((run/'flow.json').read_text())
proposal=json.loads((art/'stock-first-analysis-v2.json').read_text())
first=json.loads((art/'stock-first-analysis.json').read_text())
initial=verify(first,flow); checked=verify(proposal,flow)
print('First analyst check:',json.dumps(initial))
print('Revised analyst check:',json.dumps(checked))
assert checked['passed'] and not initial['passed']
events=[json.loads(x) for x in (stream/'events.jsonl').read_text().splitlines()]
print('Normal stock stream event counts:',dict(collections.Counter(e['event'] for e in events)))
print('Observed tool starts:',[e.get('tool') for e in events if e.get('event')=='tool_start'])
assert json.loads((stream/'source-before.json').read_text())==json.loads((stream/'source-after.json').read_text())
print('13 selected local source files unchanged during normal-stream observation. Not a pristine-upstream claim.')
print('Headless run was persisted privately; normal-stream graph was a proposal. No active user canvas changed.')
'''
 table='''rows=['| Evidence item | Observed | What this does not establish |','|---|---|---|']
rows += ['| First plain request | 4 native components / 3 wires, two Agent stages | Correct behavior |','| Second fresh stock stream | Same type-level shape, 117 events, build_flow tool start | General reliability or statistical independence |','| Selected models | Saved OpenAI/model selections in the generated Agents | Valid resources or runtime success |','| Source context | Drafter instructed to copy original ticket for reviewer | Independent or faithful original-source preservation |','| Upper layers | Analyst proposes two composites, one flow and one process | Builder-generated hierarchy or best abstraction |','| Interpretation revision | A lost inherited obligation restored; raw graph unchanged | Fix to builder or runtime behavior |']
display(Markdown('\\n'.join(rows)))
rows=['| Composite proposal | Native member types | Purpose hypothesis | Open obligations |','|---|---|---|---|']
node_types={n['id']:n['data']['type'] for n in flow['data']['nodes']}
for g in proposal['proposedComposites']:rows.append('| '+' | '.join([g['id'],', '.join(node_types[n] for n in g['memberNodeIds']),g['purpose'],', '.join(g['unknownObligations'])])+' |')
display(Markdown('\\n'.join(rows)))
'''
 corpus='''from corpus_compare import analyze
matches=analyze(flow)
rows=['| Exact recorded relationship | Supporting distinct graph objects | Meaning |','|---|---:|---|']
for r in matches['edges']:
    q=r['query'];rows.append(f"| {q['sourceType']}.{q['sourcePort']} → {q['targetType']}.{q['targetPort']} | {r['matchingDistinctGraphObjects']} | Observed occurrence, not purpose/safety |")
for r in matches['neighborhoods']:
    rows.append(f"| All incident signatures at one {r['query']['centerType']} occurrence | {r['matchingDistinctGraphObjects']} | Local coexistence, not a reusable composite |")
display(Markdown('\\n'.join(rows)))
print('Exact graph support preserves source IDs and examples in first-corpus-comparison.json. Related/copied graphs may remain.')
'''
 plot='''import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
fig,ax=plt.subplots(figsize=(12,5.7))
labels=['ChatInput\\nTicket intake','Agent\\nDrafting instructions','Agent\\nReview instructions','ChatOutput\\nPresentation']
for i,label in enumerate(labels):
    x=i*2.7
    ax.add_patch(FancyBboxPatch((x,1.1),2.25,.7,boxstyle='round,pad=.06',facecolor='#c8e4d9',edgecolor='#476960'))
    ax.text(x+1.125,1.45,label,ha='center',va='center',fontsize=10)
    if i<3:ax.annotate('',(x+2.64,1.45),(x+2.3,1.45),arrowprops={'arrowstyle':'->','color':'#2c776c','lw':2})
ax.text(0,2.25,'OBSERVED: unchanged local Langflow Assistant chose these components and wires',fontsize=12,fontweight='bold')
for x,w,label in [(0,4.95,'PROPOSED: draft capability'),(5.4,4.95,'PROPOSED: critique / presentation capability')]:
    ax.add_patch(FancyBboxPatch((x,.1),w,.55,boxstyle='round,pad=.05',facecolor='#e7e9ed',edgecolor='#778394',linestyle='--'))
    ax.text(x+w/2,.37,label,ha='center',va='center',fontsize=10)
ax.text(0,-.6,'Analyst flow: coordination / termination / failure contract remains proposed.\\nAnalyst process: accountable human, policy and completion remain unbound.\\nAlternative: all four components could form one reviewed-suggestion composite.',fontsize=11,va='top')
ax.set(xlim=(-.2,10.5),ylim=(-1.5,2.8));ax.axis('off');fig.tight_layout();plt.show()
'''
 test='''import unittest
from test_interpretation import InterpretationTests
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(InterpretationTests))
assert result.wasSuccessful()
print('Ten targeted corruptions detected. First analyst omission remains preserved; revised check is finite structural evidence.')
'''
 invoke='''# Optional next request to the UNMODIFIED stock service, not a simulation.
# Disabled by default: reading/reproducing the paper does not spend model calls.
RUN_NEW_STOCK_REQUEST=False
if RUN_NEW_STOCK_REQUEST:
    from run_stock import call
    with call('/auto_login') as response: local_auth=json.load(response)['access_token']
    instruction="Build a ticket-triage suggestion flow using built-in components. Do not run it or send/update tickets. Choose components and wiring yourself."
    with call('/agentic/assist/run',{'instruction':instruction,'provider':'OpenAI','model_name':'gpt-6.1-sol'},local_auth,timeout=600) as response:
        for raw in response:
            if raw.startswith(b'data: '): print(raw.decode().strip())
else:
    print('New stock generation not invoked. Existing real outputs above are preserved for inspection.')
'''
 n=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell('### Executable Study F — unchanged builder subject and research interpretation\n\nThe first natural-language request supplied no components, edges or compact graph recipe. The local stock assistant prompt/toolkit were left unchanged. Two separate native API observations are retained; upper-layer interpretation is explicitly the analyst’s proposal. These cells recount saved evidence and do not run a ticket workflow.'),*[nbformat.v4.new_code_cell(s) for s in (setup,table,corpus,plot,test,invoke)]],metadata={'kernelspec':{'name':'python3','display_name':'Research Python','language':'python'}})
 NotebookClient(n,timeout=90,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute();nbformat.write(n,BASE/'stock-results.ipynb');return n
if __name__=='__main__':build()
