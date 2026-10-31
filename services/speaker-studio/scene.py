"""Scene experiment contract, immutable runs and sequential native workers."""
from pathlib import Path
import copy,hashlib,importlib.util,json,subprocess,threading,time,uuid
ROOT=Path(__file__).resolve().parent;STUDY=ROOT.parents[1]/'knowledge/research/paper-16-study';DATA=ROOT/'.runtime/scenes';DATA.mkdir(parents=True,exist_ok=True)
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
B=module('scene_backends',STUDY/'take_backends.py')
SCRIPT={'id':'the-last-copy-v1','title':'The last copy','description':'An original two-person scene: confrontation, disappointment, discovery and relief. Directions are evaluation targets; reference audio supplies performance conditioning.','roles':{'A':'Robin','B':'Casey'},'lines':[
 {'id':'01','role':'A','emotion':'anger','direction':'Controlled confrontation, hurt underneath.','text':'You promised me it was safe. Please tell me we have not lost everything.'},
 {'id':'02','role':'B','emotion':'sadness','direction':'Quiet regret. Admit the mistake without melodrama.','text':'I checked twice. I really thought the copy was there. I am sorry.'},
 {'id':'03','role':'A','emotion':'neutral','direction':'Attention shifts to a possible explanation.','text':'Wait. Look at the date on that folder. That is yesterday, not today.'},
 {'id':'04','role':'B','emotion':'neutral','direction':'Careful concentration before the revelation.','text':'There is another folder underneath it. Let me open it before we say anything else.'},
 {'id':'05','role':'A','emotion':'happiness','direction':'Relief breaks through, then growing delight.','text':'It is here. Every single recording. We have it all, Casey. We have it all.'},
 {'id':'06','role':'B','emotion':'happiness','direction':'Warm, relieved happiness; reconnect with the other person.','text':'Oh, thank goodness. I thought I had let you down. Come on, let us hear it.'}]}
HELDOUT={'id':'the-empty-seat-v1','title':'The empty seat','description':'Held-out original scene: disappointment, concern, resolution and shared happiness. Not used to select source references.','roles':{'A':'Robin','B':'Casey'},'lines':[
 {'id':'01','role':'A','emotion':'sadness','direction':'A quiet admission of disappointment.','text':'I kept a seat for you. When the lights went down, I thought you had decided not to come.'},
 {'id':'02','role':'B','emotion':'anger','direction':'Firm frustration at the misunderstanding, without shouting.','text':'I would never do that. The train stopped, my phone died, and nobody could tell me what was happening.'},
 {'id':'03','role':'A','emotion':'neutral','direction':'Pause and listen; ask a practical question.','text':'Are you all right? There is still time. They have not started the final part yet.'},
 {'id':'04','role':'B','emotion':'happiness','direction':'Relief and gratitude at being welcomed.','text':'Then let us go in together. I have been waiting all week to share this with you.'}]}
SCENES={s['id']:s for s in [SCRIPT,HELDOUT]}
JOBS={};QUEUE=threading.Lock();LOCK=threading.RLock()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(x,indent=2));tmp.replace(p)
def libraries():
 p=STUDY/'scene-libraries.json'
 if p.exists():
  result=json.loads(p.read_text())
  from character_workflow import casting_voices
  characters=casting_voices()
  if characters:
   voices={**result['crema']['voices'],**characters};first=next(iter(characters.values()));second=next(v for v in result['crema']['voices'].values() if v.get('source_sex')=='Female')
   result['characters']={'id':'characters','name':'My character voices','state':'ready_for_generation','comparison':'two-role','terms':'Character emotion guides retain their recorded source terms; CREMA-D source terms also apply when choosing a dataset actor for the other role.','preferred_model':'vox','roles':{'A':first,'B':second},'voices':voices}
  return result
 refs=B.refs();roles={}
 for role,sp in [('A','0012'),('B','0015')]:roles[role]={'speaker_id':sp,'identity':refs[f'esd:{sp}:neutral'],'performances':{e:refs[f'esd:{sp}:{e}'] for e in ['anger','sadness','neutral','happiness']}}
 return {'esd':{'id':'esd','name':'ESD · existing baseline','state':'ready_for_generation','comparison':'two-role','terms':'Research-only source; perceptual qualification remains open.','roles':roles},'crema':{'id':'crema','name':'CREMA-D · two actors','state':'not_imported','reason':'One actor candidate bank exists; a second actor and scene reference mapping are required.'},'ravdess':{'id':'ravdess','name':'RAVDESS · two actors','state':'not_imported','reason':'References and metadata must be imported and checked. Non-commercial research experiment.'},'emns':{'id':'emns','name':'EMNS · one-role swap','state':'not_imported','reason':'Single-speaker reference set not yet imported. Role B will remain ESD 0015.'}}
def config():return {'capabilities':['label_hidden_compare','reference_preview','role_casting'],'scene':SCRIPT,'scenes':list(SCENES.values()),'libraries':list(libraries().values()),'models':B.inventory(),'defaults':B.DEFAULTS}
def cast_library(lib,casting=None):
 lib=copy.deepcopy(lib)
 if casting is None:return lib
 if not isinstance(casting,dict) or set(casting)!=set(lib['roles']):raise ValueError('Choose one voice for each role')
 if any(not isinstance(v,str) for v in casting.values()):raise ValueError('Speaker profile IDs must be text')
 voices=lib.get('voices',{v['speaker_id']:v for v in lib['roles'].values()})
 if len(set(casting.values()))!=len(casting):raise ValueError('Choose distinct speaker profiles for the two characters')
 for role,ident in casting.items():
  voice=voices.get(ident)
  if voice is None or role not in voice.get('allowed_roles',list(lib['roles'])):raise ValueError('That speaker is unavailable for this role and library')
  lib['roles'][role]=copy.deepcopy(voice)
 return lib
def reference_preview(library,role,emotion=None,identity=None,speaker=None):
 lib=libraries()[library]
 if speaker:
  voice=lib.get('voices',{}).get(speaker)
  if not voice or role not in voice.get('allowed_roles',list(lib['roles'])):raise ValueError('Speaker unavailable for this role')
 else:voice=lib['roles'][role]
 ref=voice['identity'] if identity=='1' else voice['performances'][emotion]
 if digest(ref['path'])!=ref['sha256']:raise ValueError('Reference file changed')
 return Path(ref['path'])
def experiments():
 out=[]
 for p in sorted(DATA.glob('*/experiment.json'),reverse=True):
  r=json.loads(p.read_text());out.append(r)
 return sorted(out,key=lambda r:r['created'],reverse=True)
def get(ident):
 if any(c not in '0123456789abcdef-' for c in ident):raise ValueError('Invalid experiment')
 return json.loads((DATA/ident/'experiment.json').read_text())
def validate(q):
 lib=libraries().get(q.get('library'));model=q.get('model')
 if not lib or lib['state']!='ready_for_generation':raise ValueError((lib or {}).get('reason','Library unavailable'))
 lib=cast_library(lib,q.get('casting'))
 if model not in B.DEFAULTS:raise ValueError('Unknown generator')
 for role in lib['roles'].values():
  if role.get('qualified_engines') and model not in role['qualified_engines']:raise ValueError('This character is qualified for VoxCPM2 only. Choose that generator.')
 settings={**B.default_settings(model),**q.get('settings',{})}
 if q.get('casting') and model=='dia' and not settings.get('use_reference',True):raise ValueError('Enable reference continuation to apply the chosen cast in Dia')
 script=SCENES.get(q.get('scene_id',SCRIPT['id']))
 if script is None:raise ValueError('Unknown scene')
 ids=q.get('line_ids',[l['id'] for l in script['lines']])
 if not ids or len(ids)!=len(set(ids)) or set(ids)-{l['id'] for l in script['lines']}:raise ValueError('Unknown or duplicate scene lines')
 for line in script['lines']:
  if line['id'] not in ids:continue
  role=lib['roles'][line['role']];ref=role['performances'].get(line['emotion'])
  if not ref:raise ValueError('Missing supported performance for '+line['emotion'])
  B.validate(model,line['text'],role['speaker_id'],line['emotion'],settings,ref)
  if digest(role['identity']['path'])!=role['identity']['sha256']:raise ValueError('Identity file changed')
 return lib,settings,ids
def start(q):
 lib,settings,ids=validate(q)
 if not QUEUE.acquire(False):raise ValueError('Another scene generation is running. Wait for it to finish.')
 ident=str(uuid.uuid4());folder=DATA/ident;folder.mkdir()
 try:
  parent=get(q['parent_id']) if q.get('parent_id') else None
  if parent and (parent['library']!=lib['id'] or parent['model']!=q['model'] or parent['scene']['id']!=q.get('scene_id',SCRIPT['id'])):raise ValueError('Retakes must retain library and model')
  if parent and q.get('casting') and q['casting']!={k:v['speaker_id'] for k,v in parent['library_snapshot']['roles'].items()}:raise ValueError('Changing cast requires a new complete scene, not a line retake')
  script=parent['scene'] if parent else SCENES[q.get('scene_id',SCRIPT['id'])]
  if parent:
   lib=parent['library_snapshot']
   for line in script['lines']:
    if line['id'] in ids:
     role=lib['roles'][line['role']];B.validate(q['model'],line['text'],role['speaker_id'],line['emotion'],settings,role['performances'][line['emotion']])
  r={'id':ident,'created':time.time(),'scene':script,'scene_sha256':hashlib.sha256(json.dumps(script,sort_keys=True).encode()).hexdigest(),'library':lib['id'],'library_snapshot':lib,'model':q['model'],'settings':settings,'requested_lines':ids,'parent_id':q.get('parent_id'),'state':'queued','lines':dict(parent.get('lines',{})) if parent else {},'events':[],'assessment':'Unrated; file creation is not acting validation','ratings':{}}
  r['casting']={k:v['speaker_id'] for k,v in lib['roles'].items()}
  dump(folder/'experiment.json',r);threading.Thread(target=run,args=(r,),daemon=True).start();return r
 except Exception:QUEUE.release();raise

def run(r):
 folder=DATA/r['id'];path=folder/'experiment.json';lib=r['library_snapshot']
 try:
  r['state']='running';dump(path,r)
  for line in r['scene']['lines']:
   if line['id'] not in r['requested_lines']:continue
   role=lib['roles'][line['role']];ref=role['performances'][line['emotion']]
   r['current_line']=line['id'];r['events'].append('Generating line '+line['id']+' · '+r['model']);dump(path,r)
   try:
    with (STUDY/'take-generation.lock').open('a') as lock:
     import fcntl
     try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
     except BlockingIOError:raise RuntimeError('Paper 16 is generating another take; retry when it finishes')
     output=B.generate(r['model'],line['text'],role['speaker_id'],line['emotion'],r['settings'],reference_override=ref,identity_override=role['identity'])
    if not output.get('word_check'):
     check=subprocess.run(['/Users/x/.local/share/swarms/voicestudio/venv/bin/python',str(STUDY/'speech_check.py'),str(STUDY/'runs'/output['id']/'take-request.json'),output['path']],capture_output=True,text=True,timeout=120)
     output['word_check']=json.loads(check.stdout) if check.returncode==0 else {'error':'Speech check failed; listening required'}
    r['lines'][line['id']]={'state':'saved','record':output,'source_experiment':r['id']}
   except Exception as e:
    previous=r['lines'].get(line['id']);r['lines'][line['id']]={'state':'failed','error':str(e),'previous':previous}
   dump(path,r)
  if all(r['lines'].get(l['id'],{}).get('state')=='saved' for l in r['scene']['lines']):
   r['events'].append('Assembling complete scene');dump(path,r);assemble(r,folder);r['state']='complete'
  else:r['state']='partial';r['events'].append('Incomplete scene; no complete mix claimed.')
 except Exception as e:r['state']='failed';r['error']=str(e)
 finally:r.pop('current_line',None);dump(path,r);QUEUE.release()
def assemble(r,folder):
 ff='/Users/x/.local/share/money/f5-tts/venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
 args=[ff,'-v','error','-nostdin'];filters=[]
 for i,line in enumerate(r['scene']['lines']):
  args+=['-i',r['lines'][line['id']]['record']['path']]
  filters.append(f'[{i}:a]aresample=24000,aformat=sample_fmts=fltp:channel_layouts=mono,apad=pad_dur=0.30[a{i}]')
 filters.append(''.join(f'[a{i}]' for i in range(len(r['scene']['lines'])))+f'concat=n={len(r["scene"]["lines"])}:v=0:a=1[out]')
 target=folder/'scene-raw.wav';subprocess.run(args+['-filter_complex',';'.join(filters),'-map','[out]','-c:a','pcm_s24le',str(target)],check=True,capture_output=True,timeout=120)
 media=subprocess.run(['/Users/x/.local/share/swarms/indextts-paper16/venv/bin/python',str(STUDY/'take_media.py'),str(target),str(folder)],capture_output=True,text=True,check=True,timeout=120)
 r['mix']=json.loads(media.stdout);r['mix']['raw_sha256']=digest(target);r['mix']['policy']='Raw generated lines resampled to mono 24 kHz; 0.30-second gaps. Listening copy uses static loudness gain; no emotion-altering processing.'
def media(ident,kind,line=None,role=None,emotion=None):
 r=get(ident)
 if kind=='mix':return Path(r['mix']['listening_path'])
 if kind=='raw-mix':return Path(r['mix']['path'])
 if kind=='line':return Path(r['lines'][line]['record']['listening_path'])
 if kind=='identity':return Path(r['library_snapshot']['roles'][role]['identity']['path'])
 if kind=='reference':return Path(r['library_snapshot']['roles'][role]['performances'][emotion]['path'])
 raise ValueError('Unknown scene media')
def ratings(q):
 r=get(q['id'])
 if r['state']!='complete':raise ValueError('Finish the scene before rating the complete performance')
 allowed=['wording','identity','emotion','naturalness','editability'];values=q.get('ratings',{})
 if set(values)!=set(allowed) or any(v not in [1,2,3,4,5] for v in values.values()):raise ValueError('Rate each category 1–5')
 r['ratings']={'listener':'user','values':values,'notes':str(q.get('notes',''))[:2000],'saved':time.time(),'blinded':False};dump(DATA/r['id']/'experiment.json',r);return r

COMPARISONS=DATA/'comparisons';COMPARISONS.mkdir(exist_ok=True)
def compare(q):
 ids=q.get('experiments',[])
 if len(ids)!=2 or len(set(ids))!=2:raise ValueError('Choose two different complete experiments')
 runs=[get(x) for x in ids]
 if any(r['state']!='complete' or not r.get('mix') for r in runs):raise ValueError('Both scenes must have complete playback')
 if json.dumps(runs[0]['scene'],sort_keys=True)!=json.dumps(runs[1]['scene'],sort_keys=True):raise ValueError('Compare the same script')
 import random
 random.SystemRandom().shuffle(ids);ident=str(uuid.uuid4());r={'id':ident,'created':time.time(),'mapping':dict(zip(['A','B'],ids)),'assessment':None,'revealed':False};dump(COMPARISONS/(ident+'.json'),r)
 return {'id':ident,'labels':['A','B'],'note':'Labels hidden; speaker identity can still be audible. Different dataset speakers confound pure library comparisons.'}
def comparison_media(ident,label):
 if any(c not in '0123456789abcdef-' for c in ident):raise ValueError('Invalid comparison')
 r=json.loads((COMPARISONS/(ident+'.json')).read_text());return media(r['mapping'][label],'mix')
def assess_compare(q):
 ident=q['id']
 if any(c not in '0123456789abcdef-' for c in ident):raise ValueError('Invalid comparison')
 path=COMPARISONS/(ident+'.json');r=json.loads(path.read_text())
 if q.get('preference') not in ['A','B','no_clear_difference']:raise ValueError('Choose a preference or no clear difference')
 r['assessment']={'preference':q['preference'],'notes':str(q.get('notes',''))[:2000],'saved':time.time(),'condition_labels_hidden':not r['revealed']};r['revealed']=True;dump(path,r)
 return {'assessment':r['assessment'],'mapping':{label:{'library':get(run)['library'],'model':get(run)['model']} for label,run in r['mapping'].items()}}
