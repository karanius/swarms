"""Sealed lineage from saved generation snapshots, with separate live integrity checks."""
from pathlib import Path
from urllib.parse import quote
import copy,hashlib,json,threading,time
import voice_designer as designer

LOCK=threading.RLock()
SCHEMA='voice-asset-passport/1'
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def file_hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stage(mode):return {'voice_design':1,'profile_reuse':2,'performance':3,'reference_performance':3,'acted_conversion':3}.get(mode)
def build(value):
 nodes={};edges=[];warnings=[];visiting=set()
 def edge(source,target,role):
  item={'from':source,'to':target,'role':role}
  if item not in edges:edges.append(item)
 def reference(ref):
  ident='reference:'+(ref.get('sha256') or digest(ref))
  snapshot=copy.deepcopy(ref)
  if ident not in nodes:nodes[ident]={'id':ident,'kind':'reference','label':ref.get('label') or ref.get('id') or 'Saved reference','snapshots':[]}
  if snapshot not in nodes[ident]['snapshots']:nodes[ident]['snapshots'].append(snapshot)
  return ident
 def recording(ident):
  node_id='recording:'+ident
  if ident in visiting:
   warnings.append('Cycle in saved ancestry at '+ident);return node_id
  if node_id in nodes:return node_id
  if len(nodes)>200:raise ValueError('Lineage exceeds the supported size')
  try:r=designer.get(ident)
  except (ValueError,FileNotFoundError):
   nodes[node_id]={'id':node_id,'kind':'missing','label':'Unavailable parent recording','recording_id':ident}
   warnings.append('Missing parent recording '+ident);return node_id
  visiting.add(ident);q=copy.deepcopy(r.get('request',{}));mode=q.get('mode','unknown')
  labels={'voice_design':'Designed voice','profile_reuse':'New words with saved voice','performance':'Written-direction take',
          'reference_performance':'Actor performance','acted_conversion':'Converted character voice'}
  n={'id':node_id,'kind':'recording','recording_id':ident,'label':'Direct character performance' if q.get('emotion_route')=='direct' else labels.get(mode,'Recording'),
     'stage':3 if q.get('emotion_route')=='direct' else stage(mode),'created':r.get('created'),'state':r.get('state'),'engine':r.get('engine'),
     'request':q,'model_provenance':copy.deepcopy(r.get('model_provenance')),
     'word_check':copy.deepcopy(r.get('word_check')),'assessment':r.get('assessment'),'error':r.get('error'),
     'audio':copy.deepcopy(r.get('audio')),'play_url':'/designer-media?id='+quote(ident),'artifacts':[]}
  nodes[node_id]=n
  folder=designer.AUDITIONS/ident
  for filename in ('native-fields.json','conversion/conversion-request.json'):
   p=folder/filename
   if p.is_file():n.setdefault('native_snapshots',{})[filename]=json.loads(p.read_text())
  if not n['model_provenance']:warnings.append('Model revision was not recorded for '+ident)
  audio=r.get('audio') or {}
  for role,key in [('original','path'),('listening','listening_path')]:
   path=audio.get(key)
   if not path:continue
   expected=audio.get('sha256') if role=='original' else None
   measured=not bool(expected)
   if measured and Path(path).is_file():expected=file_hash(path)
   n['artifacts'].append({'role':role,'path':path,'sha256':expected,
    'hash_origin':'measured_when_passport_sealed' if measured else 'recorded_at_generation',
    'asset_id':'sha256:'+expected if expected else None})
  if audio:
   n['playback_processing']={k:copy.deepcopy(audio.get(k)) for k in ('gain','loudness','sample_rate','duration_seconds')}
  profile=q.get('profile')
  if profile:
   pid='profile:'+str(profile.get('id','snapshot'))+':'+digest(profile)[:16]
   nodes[pid]={'id':pid,'kind':'profile','label':profile.get('name','Saved voice profile'),'snapshot':profile}
   edge(pid,node_id,'target_voice' if mode=='acted_conversion' else 'voice_identity')
   ref=profile.get('reference',{});parent=profile.get('audition_id') or ref.get('audition_id')
   if parent:edge(recording(parent),pid,'selected_as_identity')
   else:edge(reference(ref),pid,'reference_recording')
  guide=q.get('emotion_reference')
  if guide:
   # For conversion this is upstream recipe context, not an additional Seed-VC audio input.
   edge(reference(guide),node_id,'upstream_acting_recipe' if mode=='acted_conversion' else 'emotion_guidance')
  actor=r.get('actor_audition_id')
  if actor:edge(recording(actor),node_id,'performed_audio_to_convert')
  elif mode=='acted_conversion':warnings.append('Intermediate actor recording was not recorded for '+ident)
  visiting.remove(ident);return node_id
 root=recording(designer.ident(value))
 manifest={'schema':SCHEMA,'root':root,'nodes':list(nodes.values()),'edges':edges,'warnings':warnings,
  'notes':['Generated word checks do not approve acting or identity.',
           'Only saved generation snapshots are used; current interface selections are excluded.',
           'A neutral comparison control is not a synthesis input.',
           'Listening-copy hashes measured at sealing are explicitly distinguished from generation-time hashes.']}
 manifest['passport_id']='sha256:'+digest(manifest)
 return manifest

def seal(value):
 value=designer.ident(value);path=designer.AUDITIONS/value/'passport.json'
 with LOCK:
  if path.exists():return json.loads(path.read_text())
  record=designer.get(value)
  if record['state'] not in ('saved','failed'):raise ValueError('Passport will be sealed when this recording finishes')
  manifest=build(value);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False));tmp.replace(path)
  return manifest

def capture(record):
 """Passport failure must never hide a successfully generated audio recording."""
 try:seal(record['id'])
 except Exception as e:
  (designer.AUDITIONS/record['id']/'passport-error.txt').write_text(str(e))

def get(value):
 manifest=seal(value);check=copy.deepcopy(manifest);claimed=check.pop('passport_id',None)
 if claimed!='sha256:'+digest(check):raise ValueError('The saved passport seal does not match its contents')
 checks=[];seen=set()
 def verify(path,expected,role):
  if not path or (path,expected) in seen:return
  seen.add((path,expected));p=Path(path);actual=file_hash(p) if p.is_file() else None
  checks.append({'path':path,'role':role,'expected_sha256':expected,'actual_sha256':actual,
                 'status':'missing' if actual is None else 'unverified' if not expected else 'match' if actual==expected else 'changed'})
 for n in manifest['nodes']:
  for a in n.get('artifacts',[]):verify(a['path'],a['sha256'],a['role'])
  for r in n.get('snapshots',[]):verify(r.get('path'),r.get('sha256'),'reference')
  if n['kind']=='profile':
   r=n['snapshot'].get('reference',{});verify(r.get('path'),r.get('sha256'),'profile reference')
 comparisons=[]
 for p in (designer.DATA.parent/'santa-batches').glob('*.json'):
  b=json.loads(p.read_text());items=b.get('items',[])
  if any(i['id']==value for i in items):
   comparisons.append({'id':b['id'],'strategy':b.get('strategy'),'seed_mode':b.get('seed_mode'),
    'recipe':b.get('recipe'),'reference_id':b.get('reference_id'),'target_style':b.get('target_style'),
    'items':items,'relationship':'comparison context; other takes are not automatically parent inputs'})
 ancestor_ids={n['recording_id'] for n in manifest['nodes'] if n['kind']=='recording'}
 related=[]
 for path in designer.AUDITIONS.glob('*/audition.json'):
  r=json.loads(path.read_text());q=r.get('request',{});profile=q.get('profile') or {}
  parent=profile.get('audition_id') or profile.get('reference',{}).get('audition_id')
  if q.get('mode')=='profile_reuse' and q.get('emotion_route')!='direct' and parent in ancestor_ids and r['id'] not in ancestor_ids:
   related.append({'id':r['id'],'source_recording_id':parent,'text':q.get('text'),'state':r['state'],
                   'word_check':r.get('word_check'),'relationship':'identity check; not a generation input',
                   'listener_approval':'Not recorded in the generation archive'})
 checkpoints=[]
 for path in (designer.DATA/'emotion-checkpoints').glob('*.json'):
  session=json.loads(path.read_text());linked={session.get('source')}
  for attempt in session.get('attempts',[]):
   linked.update((attempt.get('actor_id'),attempt.get('conversion_id')))
   linked.update(h['id'] for h in attempt.get('conversion_history',[]))
  if ancestor_ids.intersection(linked):checkpoints.append(session)
 return {'passport':manifest,'integrity':{'checked_at':time.time(),'assets':checks},'comparisons':comparisons,'related_identity_tests':related,'checkpoint_history':checkpoints}

def reference_media(value,node_id):
 manifest=seal(value)
 n=next((n for n in manifest['nodes'] if n['id']==node_id and n['kind']=='reference'),None)
 if not n:raise ValueError('Unknown passport reference')
 for ref in n['snapshots']:
  if ref.get('path') and Path(ref['path']).is_file():
   raw=Path(ref['path']).read_bytes()
   if hashlib.sha256(raw).hexdigest()!=ref.get('sha256'):raise ValueError('Reference changed since it was used')
   return raw
 raise FileNotFoundError('The original reference is unavailable')
