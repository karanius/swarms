"""Enforced Paper6 resource broker: fixed context registry, CAS writes and audit trail."""
from __future__ import annotations
import hashlib,json,os,re,secrets,threading,time
from pathlib import Path
from secure_files import SecureTree
ROOT=Path(__file__).resolve().parents[2]
PAPER=ROOT/'knowledge/research/notebooks/Paper 6 - Rule Mining from Langflow Templates.ipynb'
DEFAULT=ROOT/'knowledge/research/paper-6-study/assistant-workspace'
def sha(data):return hashlib.sha256(data if isinstance(data,bytes) else data.encode()).hexdigest()
def atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.'+secrets.token_hex(5)+'.tmp');tmp.write_text(data);os.replace(tmp,path)
class Workspace:
 def __init__(self,root=DEFAULT):
  self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True);self.lock=threading.RLock()
  for name in ['artifacts','context','history','runs']: (self.root/name).mkdir(exist_ok=True)
  self.registry={
   'native_catalog':ROOT/'knowledge/research/paper-6-study/native-starter-catalog.json',
   'assistant_runtime':ROOT/'knowledge/research/paper-6-study/assistant-runtime-research.md',
   'study_protocol':ROOT/'knowledge/research/paper-6-study/RELATIONAL-PROTOCOL.md',
   'study_results':ROOT/'knowledge/research/paper-6-corpus/relational/summary.json',
   'study_verification':ROOT/'knowledge/research/paper-6-corpus/relational/verification.json',
   'study_implementation':ROOT/'knowledge/research/paper-6-study/relational_experiment.py',
   'study_checker':ROOT/'knowledge/research/paper-6-study/verify_relational.py',
   'engine_research':ROOT/'knowledge/research/paper-6-study/relational-engine-research.md',
   'association_method':ROOT/'knowledge/research/paper-6-study/PATTERNS.md',
   'corpus_transactions':ROOT/'knowledge/research/paper-6-corpus/patterns/transactions.json',
   'learned_rules':ROOT/'knowledge/research/paper-6-corpus/relational/rules.json',
   'assessment_cases':ROOT/'knowledge/research/paper-6-corpus/relational/cases.json',
   'training_catalog':ROOT/'knowledge/research/paper-6-corpus/relational/catalog.json',
   'candidate_boundaries':ROOT/'knowledge/research/paper-6-study/CANDIDATES.md',
   'literature':ROOT/'knowledge/research/paper-6-corpus/literature-review.md',
   'prior_paper1':ROOT/'knowledge/research/notebooks/Paper 1 - From Components to Instances.ipynb',
   'prior_paper2':ROOT/'knowledge/research/notebooks/Paper 2 - Boundary Resolution.ipynb',
  }
  self.artifacts=SecureTree(self.root/'artifacts')
  self.grants=self._load('grants.json',{})
  if not (self.root/'paper-draft.ipynb').exists():
   atomic(self.root/'paper-draft.ipynb',PAPER.read_text());atomic(self.root/'draft-base.json',json.dumps({'canonicalSha256':sha(PAPER.read_bytes()),'changedSections':[]}))
 def _load(self,name,default):
  p=self.root/name;return json.loads(p.read_text()) if p.exists() else default
 def event(self,kind,**data):
  with self.lock:
   record={'at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'type':kind,**data}
   with (self.root/'events.jsonl').open('a') as f:f.write(json.dumps(record,default=str)+'\n')
  return record
 def safe(self,name,area='artifacts'):
  if not isinstance(name,str) or not name or len(name)>220:raise ValueError('Use a short relative artifact name')
  q=Path(name)
  if q.is_absolute() or any(p in ['..','.'] or p.startswith('.') for p in q.parts):raise ValueError('Only relative visible workspace paths are allowed')
  base=self.root/area;p=base/q
  # Reject symlinks even when they happen to point back inside the allowed root.
  for node in [base,*p.parents,p]:
   if node.is_symlink():raise ValueError('Symlinks are not allowed')
  if not p.resolve().is_relative_to(base.resolve()):raise ValueError('Path is outside the research workspace')
  return p
 def list_artifacts(self):
  rows=[]
  for name in self.artifacts.names():
   try:data=self.artifacts.read(name);rows.append({'path':name,'bytes':len(data),'revision':sha(data)})
   except (OSError,ValueError):continue
  return rows
 def read_artifact(self,path,offset=0,limit=18000):
  self.safe(path);text=self.artifacts.read(path).decode();return {'path':path,'revision':sha(text),'content':text[max(0,offset):max(0,offset)+min(60000,max(1,limit))],'totalCharacters':len(text)}
 def write_artifact(self,path,content,expected_revision=''):
  self.safe(path)
  if Path(path).parts[0]=='inputs':raise ValueError('Coordinator-frozen input artifacts are read-only')
  if len(content.encode())>2_000_000:raise ValueError('Artifact exceeds2MB limit')
  with self.lock:
   inventory=self.list_artifacts()
   if sum(x['bytes'] for x in inventory)+len(content.encode())>100_000_000 or len(inventory)>=150:raise ValueError('Workspace artifact budget reached; ask the coordinator to archive results')
   try:previous=self.artifacts.read(path).decode()
   except FileNotFoundError:previous=None
   if previous is not None:
    if expected_revision!=sha(previous):raise ValueError('Stale artifact: read its current revision before replacing it')
    atomic(self.root/'history'/f'{time.time_ns()}-{Path(path).name}',previous)
   elif expected_revision:raise ValueError('Artifact does not exist at the supplied revision')
   self.artifacts.put(path,content);revision=sha(content);self.event('artifact_written',path=path,revision=revision,bytes=len(content.encode()))
   return {'path':path,'revision':revision,'bytes':len(content.encode())}
 def context_menu(self):return [{'name':k,'available':True,'granted':k in self.grants} for k in self.registry]+[{'name':'paper6_section','available':True,'detail':'Read individual numbered sections1–14 on demand'}]
 def grant_context(self,name):
  if name not in self.registry:raise ValueError('Unknown context resource; ask the coordinator to add it explicitly')
  source=self.registry[name];content=source.read_text()
  if source.suffix=='.ipynb':
   n=json.loads(content);content='\n\n'.join(''.join(c['source']) for c in n['cells'] if c['cell_type']=='markdown')
  filename=name+('.json' if source.suffix=='.json' else '.md')
  previous=self.root/'context'/filename
  if previous.exists() and sha(previous.read_bytes())!=sha(content):atomic(self.root/'history'/f'{time.time_ns()}-context-{filename}',previous.read_text())
  atomic(self.root/'context'/filename,content)
  self.grants[name]={'file':filename,'source':str(source.relative_to(ROOT)),'sha256':sha(content),'grantedAt':time.time()};atomic(self.root/'grants.json',json.dumps(self.grants,indent=2));self.event('context_granted',name=name,source=str(source.relative_to(ROOT)),sha256=sha(content));return {'name':name,'revision':sha(content),'characters':len(content),'file':'context/'+filename}
 def read_context(self,name,offset=0,limit=18000):
  if name not in self.grants:return {'error':'Context not yet granted. Call request_context with this listed resource name.'}
  text=(self.root/'context'/self.grants[name]['file']).read_text();self.event('context_read',name=name,offset=offset)
  return {'name':name,'source':self.grants[name]['source'],'revision':sha(text),'content':text[max(0,offset):max(0,offset)+min(60000,max(1,limit))],'totalCharacters':len(text)}
 def section(self,number,draft=True):
  if not 1<=number<=14:raise ValueError('Section must be1–14; the original abstract is preserved')
  p=self.root/'paper-draft.ipynb' if draft else PAPER;n=json.loads(p.read_text());prefix=f'## {number}. '
  matches=[c for c in n['cells'] if c['cell_type']=='markdown' and ''.join(c['source']).startswith(prefix)]
  if len(matches)!=1:raise ValueError('Section structure is ambiguous')
  text=''.join(matches[0]['source']);return {'section':number,'revision':sha(text),'markdown':text,'source':'Paper6 isolated draft' if draft else 'Paper6 canonical manuscript'}
 def write_section(self,number,markdown,expected_revision):
  with self.lock:
   current=self.section(number)
   if current['revision']!=expected_revision:raise ValueError('Stale section: reread before updating')
   if re.search(r'<\s*(script|iframe|object|embed|form|input|button|svg|math|style|link|meta|base)\b|<[^>]+\bon\w+\s*=|javascript:',markdown,re.I):raise ValueError('Paper sections accept prose/Markdown, not active HTML or browser actions')
   if not markdown.startswith(f'## {number}. ') or len(markdown.encode())>200000:raise ValueError('Preserve the numbered section heading and keep content under200KB')
   n=json.loads((self.root/'paper-draft.ipynb').read_text());c=next(c for c in n['cells'] if c['cell_type']=='markdown' and ''.join(c['source']).startswith(f'## {number}. '));atomic(self.root/'history'/f'{time.time_ns()}-section-{number}.md',current['markdown']);c['source']=markdown.splitlines(keepends=True);atomic(self.root/'paper-draft.ipynb',json.dumps(n,indent=1))
   base=self._load('draft-base.json',{});base['changedSections']=sorted(set(base.get('changedSections',[])+[number]));atomic(self.root/'draft-base.json',json.dumps(base));self.event('paper_section_written',section=number,revision=sha(markdown));return {'section':number,'revision':sha(markdown),'status':'saved in isolated paper draft; not yet merged'}
 def publish_checked_sections(self,numbers):
  # Coordinator-owned operation, intentionally not an agent tool.
  with self.lock:
   base=self._load('draft-base.json',{});original=PAPER.read_bytes()
   if sha(original)!=base['canonicalSha256']:raise ValueError('Canonical paper changed since draft creation; reconcile before publishing')
   n=json.loads(original);draft=json.loads((self.root/'paper-draft.ipynb').read_text())
   for number in numbers:
    text=self.section(number)['markdown'];c=next(c for c in n['cells'] if c['cell_type']=='markdown' and ''.join(c['source']).startswith(f'## {number}. '));c['source']=text.splitlines(keepends=True)
   atomic(self.root/'history'/f'{time.time_ns()}-canonical-before-merge.ipynb',original.decode());atomic(PAPER,json.dumps(n,indent=1));base['canonicalSha256']=sha(PAPER.read_bytes());base['changedSections']=[x for x in base['changedSections'] if x not in numbers];atomic(self.root/'draft-base.json',json.dumps(base));self.event('checked_sections_merged',sections=numbers,revision=base['canonicalSha256']);return base
