"""Checked coauthor merge plus real executed Study D cells; preserves prior evidence."""
import sys,json,copy,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'services/paper6-assistant'))
from workspace import Workspace,PAPER,atomic,sha
BASE=ROOT/'knowledge/research/paper-6-study'
def main():
 ws=Workspace();before=json.loads(PAPER.read_text());original_cells=copy.deepcopy(before['cells'])
 # Reject a replacement-style draft: every pre-existing numbered section remains verbatim.
 for num in (1,6,7,8,9,10,11,12,13,14):
  prefix=f'## {num}. ';old=next(''.join(c['source']) for c in before['cells'] if ''.join(c['source']).startswith(prefix));new=ws.section(num)['markdown']
  assert new.startswith(old),f'Prior section {num} changed unexpectedly'
 ws.publish_checked_sections([1,6,7,8,9,10,11,12,13,14])
 paper=json.loads(PAPER.read_text())
 presentation=json.loads((BASE/'assistant-results.ipynb').read_text())
 for c in presentation['cells']:c.setdefault('metadata',{})['paper6_assistant_study_d']=True
 assert not any(c.get('metadata',{}).get('paper6_assistant_study_d') for c in paper['cells']),'Already integrated; inspect instead of duplicating'
 index=next(i for i,c in enumerate(paper['cells']) if ''.join(c['source']).startswith('## 8. '))
 paper['cells'][index:index]=presentation['cells']
 status=next(c for c in paper['cells'] if ''.join(c['source']).startswith('### Current study status'))
 status['source']=['### Current study status\n\nThe original proposal abstract above is preserved. This completed bounded research account includes the corpus topology, connected-pattern and candidate-boundary explorers; executed association and PyClause/AnyBURL studies; and Study D, an assistant-authored static obligation/revision diagnostic. The dedicated native Langflow research assistant below has its own conversation, progressive context, writable draft/artifacts and bounded notebook execution. Jupyter remains the research host.\n\n**Findings:** 205 local feature rules recovered 34/402 masked targets, versus 43/402 for center frequency. Exact counting matched the 205 rules; a 512MB typed-wire probe failed before a scored result. Study D produced 24 authored base decisions plus 72 transformations; original action agreement was 23/24, with one preserved ASK-versus-REJECT_SCOPE disagreement. Of 927 final checker assertions, 923 passed; four representation-level label mismatches remain. These counts establish neither significance nor useful composite generation.\n\n**Limits:** synthetic three-type conformance, assumption-tier bindings, no task-runtime validation, and known schema/identity/route limitations. Prior results, first failures, provenance and original explorers remain inspectable. The next scientific requirement is an independently specified task-and-evidence contract; no general multilayer generator is claimed.\n']
 # Label stale planning text explicitly while preserving its contents.
 for c in paper['cells']:
  t=''.join(c['source'])
  if t.startswith('### Earlier strategy — Association Discovery Before Relational Mining'):
   c['source']=t.replace('Only its association-discovery slice is implemented; Sections 1–14 define the actual executed scope.','Its association-first intention was later implemented in the bounded Studies A/C below; Study D adds a separate authored diagnostic. Statements of future work in this historical block describe that earlier planning state.').splitlines(keepends=True)
 assert paper['cells'][0]==original_cells[0],'Original title/abstract changed'
 # Every earlier code cell and its actual outputs remain intact and in order.
 oldcode=[c for c in original_cells if c['cell_type']=='code'];newcode=[c for c in paper['cells'] if c['cell_type']=='code' and not c.get('metadata',{}).get('paper6_assistant_study_d')]
 assert oldcode==newcode,'Prior execution evidence changed'
 atomic(PAPER,json.dumps(paper,indent=1))
 # Synchronize the merged draft so its future base contains the new canonical cells.
 atomic(ws.root/'paper-draft.ipynb',PAPER.read_text());atomic(ws.root/'draft-base.json',json.dumps({'canonicalSha256':sha(PAPER.read_bytes()),'changedSections':[]}))
 ws.event('checked_presentation_integrated',cells=len(presentation['cells']),canonicalSha256=sha(PAPER.read_bytes()))
 print(json.dumps({'canonical':str(PAPER),'sha256':sha(PAPER.read_bytes()),'priorCodeCellsPreserved':len(oldcode),'addedExecutedCodeCells':sum(c['cell_type']=='code' for c in presentation['cells'])},indent=2))
if __name__=='__main__':main()
