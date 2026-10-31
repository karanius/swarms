"""Explicit, resumable HTTPS asset downloads; no model SDK network retries."""
from pathlib import Path
import os,json,time,subprocess,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[1];STUDY=ROOT/'knowledge/research/paper-14-study';CACHE=Path('/Users/x/.local/share/swarms/voicestudio/cache');CACHE.mkdir(exist_ok=True)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
state={'stage':'downloading','started_unix':time.time(),'models':[]}
def save():(STUDY/'downloads.json').write_text(json.dumps(state,indent=2)+'\n')
for name in ['dia-metadata.json','dac-metadata.json','voxcpm-metadata.json']:
 meta=json.loads((STUDY/name).read_text());repo=meta['id'];revision=meta['sha']
 if meta.get('gated'):raise RuntimeError('External access agreement required: '+repo)
 home=CACHE/('models--'+repo.replace('/','--'));snapshot=home/'snapshots'/revision;snapshot.mkdir(parents=True,exist_ok=True);files=[]
 for entry in meta['siblings']:
  rel=entry['rfilename']
  if rel=='.gitattributes':continue
  target=snapshot/rel;target.parent.mkdir(exist_ok=True,parents=True);expected=entry.get('lfs',{}).get('sha256') or entry.get('lfs',{}).get('oid');size=entry.get('size',0)
  if target.is_file() and target.stat().st_size==size and (not expected or digest(target)==expected):
   files.append({'file':rel,'bytes':size,'sha256':digest(target)});continue
  partial=target.with_name(target.name+'.partial');url=f'https://huggingface.co/{repo}/resolve/{revision}/{rel}'
  state.update(current_model=repo,current_file=rel,expected_file_bytes=size,received_file_bytes=partial.stat().st_size if partial.exists() else 0);save();print('FETCH',repo,rel,size,flush=True)
  with (STUDY/'download-errors.log').open('ab') as log:
   args=['curl','-4','--fail','--silent','--show-error','--location','--proto','=https','--proto-redir','=https','--connect-timeout','10','--max-time','1800','--retry','1','--retry-delay','2','--continue-at','-','--output',str(partial),url]
   proc=subprocess.Popen(args,stderr=log)
   while proc.poll() is None:
    state['received_file_bytes']=partial.stat().st_size if partial.exists() else 0;save();time.sleep(2)
  if proc.returncode:state.update(stage='failed',error='HTTPS transfer failed',exit_code=proc.returncode);save();raise RuntimeError('Asset transfer failed; inspect download-errors.log')
  if partial.stat().st_size!=size:raise RuntimeError('Asset size mismatch: '+rel)
  actual=digest(partial)
  if expected and actual!=expected:raise RuntimeError('Model hash mismatch: '+rel)
  partial.replace(target);files.append({'file':rel,'bytes':size,'sha256':actual});print('VERIFIED',repo,rel,flush=True)
 refs=home/'refs';refs.mkdir(exist_ok=True);(refs/'main').write_text(revision)
 state['models'].append({'repo':repo,'revision':revision,'snapshot':str(snapshot),'files':files,'bytes':sum(x['bytes'] for x in files)});save()
state.update(stage='complete',finished_unix=time.time());save();print('SELECTED ASSETS VERIFIED',flush=True)
