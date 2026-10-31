"""Pinned, resumable official asset acquisition for the isolated Paper 16 trial."""
from pathlib import Path
import subprocess,json,hashlib,time
S=Path(__file__).resolve().parent
R=Path('/Users/x/.local/share/swarms/indextts-paper16')
def curl(url,target):
 target.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(['curl','-4','--fail','--silent','--show-error','--location','--proto','=https','--proto-redir','=https','--connect-timeout','15','--max-time','1800','--retry','1','--continue-at','-','--output',str(target),url],check=True)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
specs=[
 ('IndexTeam/IndexTTS-2.5','c39ce5ba981572cb187443877ff559dfb246ce63','checkpoints',lambda n: '/' not in n and n!='.gitattributes'),
 ('facebook/w2v-bert-2.0',None,'checkpoints/hf_cache/w2v-bert-2.0',lambda n:n in ('config.json','preprocessor_config.json','model.safetensors','README.md')),
 ('funasr/campplus',None,'checkpoints/hf_cache',lambda n:n=='campplus_cn_common.bin'),
 ('nvidia/bigvgan_v2_22khz_80band_256x',None,'checkpoints/hf_cache/bigvgan',lambda n:n in ('config.json','bigvgan_generator.pt','LICENSE'))
]
state={'stage':'metadata','models':[]}
def save():(S/'indextts-downloads.json').write_text(json.dumps(state,indent=2))
for repo,rev,local,choose in specs:
 meta_path=S/('indextts-meta-'+repo.replace('/','--')+'.json')
 if not meta_path.exists():curl('https://huggingface.co/api/models/'+repo+('/revision/'+rev if rev else '')+'?blobs=true',meta_path)
 meta=json.loads(meta_path.read_text());rev=meta['sha']
 if meta.get('gated'):raise RuntimeError('Gated model: '+repo)
 model={'repo':repo,'revision':rev,'files':[]};state['models'].append(model)
 for e in meta['siblings']:
  name=e['rfilename']
  if not choose(name):continue
  p=R/local/name;expected=e.get('lfs',{}).get('sha256');size=e.get('size')
  state.update(stage='downloading',repo=repo,file=name,expected_bytes=size);save()
  if not p.exists() or (size and p.stat().st_size!=size) or (expected and digest(p)!=expected):
   partial=p.with_name(p.name+'.partial')
   print('FETCH',repo,name,size,flush=True)
   curl(f'https://huggingface.co/{repo}/resolve/{rev}/{name}',partial)
   if size and partial.stat().st_size!=size:raise RuntimeError('Size mismatch '+name)
   if expected and digest(partial)!=expected:raise RuntimeError('Hash mismatch '+name)
   partial.replace(p)
  model['files'].append({'file':name,'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p)})
  print('VERIFIED',name,p.stat().st_size,flush=True);save()
state.update(stage='complete');save()
