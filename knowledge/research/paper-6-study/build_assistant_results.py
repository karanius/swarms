"""Integrate checked, executable Study D presentation cells without rerunning Study C."""
import json,copy
from pathlib import Path
import nbformat
from nbclient import NotebookClient
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
def build():
 setup='''from pathlib import Path
import json, sys, collections
from IPython.display import display, Markdown
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'knowledge/research/paper-6-study').exists())
study = ROOT / 'knowledge/research/paper-6-study'
art = study / 'assistant-workspace/artifacts'
sys.path.insert(0, str(study))
from verify_assistant_experiment import verify
results = json.loads((art / 'obligation-results.json').read_text())
assessment = verify(art / 'obligation-results.json')
base = [r for r in results['records'] if r['variant'] == 'base']
assert len(base) == 24 and len(results['records']) == 96
print('Preserved first run:', assessment['resultSha256'])
print('Independent checker assertions:', assessment['checks'])
print('Unresolved original acceptance differences:', len(assessment['failures']))
print('24 base cases + 72 transformations; not 96 independent observations.')
'''
 table='''rows = ['| Case | Ports only | Required fields | Ledger action | Blockers |', '|---|---|---|---|---|']
for r in base:
    d = r['decisions']
    rows.append('| ' + ' | '.join([r['base_case_id'], d['B0']['action'], d['B1']['action'], d['ledger']['action'], ', '.join(b['kind'] for b in d['ledger']['blockers']) or 'None at static tier']) + ' |')
display(Markdown('\\n'.join(rows)))
print('Original action agreement: 23/24 base cases; C17 disagrees on ASK versus REJECT_SCOPE.')
print('All mandatory blocker, checked witness, authorized patch and action/blocker metamorphic assertions pass.')
print('These are internal authored conformance cases, not efficacy or generalization evidence.')
'''
 chart='''import matplotlib.pyplot as plt
counts = collections.Counter(r['decisions']['ledger']['action'] for r in base)
labels = ['ASK','SPEC_GROUNDED','REJECT_SCOPE','REVISE']
fig, ax = plt.subplots(figsize=(9, 3.7))
values = [counts[x] for x in labels]
bars = ax.barh(labels[::-1], values[::-1], color=['#557b99','#bd8c53','#5d997f','#806d9e'])
for bar in bars: ax.text(bar.get_width()+.15, bar.get_y()+bar.get_height()/2, str(int(bar.get_width())), va='center')
ax.set(xlabel='Authored base cases (n = 24)', xlim=(0,16), title='Study D: observed ledger actions, not accuracy or usefulness')
ax.spines[['top','right']].set_visible(False)
fig.tight_layout(); plt.show()
'''
 example='''# Reproduce every saved base decision from the frozen agent-authored implementation.
import importlib.util, hashlib
spec = importlib.util.spec_from_file_location('paper6_obligation_reproduction', art / 'obligation_ledger.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
catalog = json.loads((study / 'native-starter-catalog.json').read_text())
for name, expected in results['source_hashes'].items():
    path = study / 'assistant-workspace' / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
for record in base:
    for method in ['B0','B1','ledger']:
        assert module.evaluate(record['input'],catalog,method) == record['decisions'][method]
print('Reproduced 72/72 base-case method decisions exactly from pinned code and inputs.')
print('No workflow, provider, Langflow component, or language model was executed in this reproduction.')
for cid in ['C03','C14','C20','C21']:
    r = next(r for r in base if r['base_case_id']==cid)
    d = r['decisions']['ledger']
    print(cid, d['action'], 'patches:', [p['op'] for p in d['patches']], 'blockers:', [b['kind'] for b in d['blockers']])
'''
 n=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell('### Executable study D — assistant-authored obligation and revision diagnostics\n\nA native Langflow research assistant wrote the implementation and experiment. A separate coordinator wrote the fixtures, withheld acceptance manifest and checker. This is internal collaboration, not external peer review. Original disagreements and code are preserved. The cells below independently recount and reproduce saved evidence; no task workflow is run.'),*[nbformat.v4.new_code_cell(x) for x in (setup,table,chart,example)]],metadata={'kernelspec':{'name':'python3','display_name':'Research Python','language':'python'}})
 NotebookClient(n,timeout=90,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
 nbformat.write(n,BASE/'assistant-results.ipynb')
 return n
if __name__=='__main__':build()
