"""Reference-free VoxCPM2 auditions and immutable, user-selected voice profiles."""
from pathlib import Path
import fcntl,hashlib,json,subprocess,threading,time,uuid
import requests
import scene
import sentence_policy

DATA=Path(__file__).resolve().parent/'.runtime/voice-designer'
AUDITIONS=DATA/'auditions';PROFILES=DATA/'profiles'
AUDITIONS.mkdir(parents=True,exist_ok=True);PROFILES.mkdir(exist_ok=True)
PYTHON='/Users/x/.local/share/swarms/voicestudio/venv/bin/python'

def ident(value):
 if not isinstance(value,str) or len(value)!=36 or any(c not in '0123456789abcdef-' for c in value):raise ValueError('Unknown recording')
 return value
def get(value):return json.loads((AUDITIONS/ident(value)/'audition.json').read_text())
def profile(value):return json.loads((PROFILES/(ident(value)+'.json')).read_text())
def listing():
 return {'auditions':sorted((json.loads(p.read_text()) for p in AUDITIONS.glob('*/audition.json')),key=lambda r:r['created'],reverse=True),'profiles':sorted((json.loads(p.read_text()) for p in PROFILES.glob('*.json')),key=lambda r:r['created'],reverse=True),'busy':scene.QUEUE.locked(),'engine':'VoxCPM2','scope':'New synthetic voice design and saved-sample reuse. No pitch/formant editing or scene casting integration.'}
def validate(q, reference_profile=None):
 if q.get('model','voxcpm2')!='voxcpm2':raise ValueError('This designer currently supports VoxCPM2 only')
 text=sentence_policy.require(q.get('text',''));description=str(q.get('description','')).strip()
 if not 5<=len(text)<=500:raise ValueError('Use a script between 5 and 500 characters')
 if not q.get('profile_id') and not reference_profile and not 5<=len(description)<=1500:raise ValueError('Describe the voice in 5–1500 characters')
 settings={'seed':int(q.get('seed',11)),'steps':int(q.get('steps',10)),'guidance':float(q.get('guidance',2))}
 if not 0<=settings['seed']<=2147483647 or not 1<=settings['steps']<=64 or not .1<=settings['guidance']<=8:raise ValueError('Check seed, steps and guidance ranges')
 selected=reference_profile or (profile(q['profile_id']) if q.get('profile_id') else None)
 direction=str(q.get('performance_direction','')).strip()
 if len(direction)>1500 or (direction and not selected):raise ValueError('Performance directions require a fixed voice identity')
 if selected and scene.digest(selected['reference']['path'])!=selected['reference']['sha256']:raise ValueError('The saved voice sample has changed')
 return {'text':text,'description':description if not selected else '',**settings,'profile':selected,'performance_direction':direction,'mode':('performance' if direction else 'profile_reuse') if selected else 'voice_design'}
def start(q):
 request=validate(q)
 if not next(m for m in scene.B.inventory() if m['id']=='vox')['ready']:raise ValueError('VoxCPM2 model files are unavailable; no download was started')
 if not scene.QUEUE.acquire(False):raise ValueError('Another studio generation is running. Wait for it to finish.')
 try:
  r=create_record(request)
  threading.Thread(target=run,args=(r,),daemon=True).start();return r
 except Exception:scene.QUEUE.release();raise
def create_record(request):
 value=str(uuid.uuid4());folder=AUDITIONS/value;folder.mkdir()
 r={'id':value,'created':time.time(),'state':'queued','request':request,'engine':'IndexTTS 2.5' if request['mode']=='reference_performance' else 'VoxCPM2','reference_used':bool(request['profile']),'assessment':'Not rated; a description is guidance, not a guarantee of age, pitch or identity.'}
 scene.dump(folder/'audition.json',r)
 return r
def run(r, release_queue=True):
 folder=AUDITIONS/r['id'];request=r['request'];tick=time.time()
 try:
  r['state']='running';scene.dump(folder/'audition.json',r)
  with (scene.STUDY/'take-generation.lock').open('a') as lock:
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:raise RuntimeError('The notebook is generating audio. Retry when it finishes.')
   fields={'text':request['text'],'engine':'voxcpm2','seed':request['seed'],'num_step':request['steps'],'guidance_scale':request['guidance'],'effect_preset':'raw','wav_bits':'24','max_chunk_chars':0,'pronounce':'false'}
   source=request['profile']
   if source:
    fields['ref_text']=source['reference']['transcript']
    if request.get('performance_direction'):fields['instruct']=request['performance_direction']
   else:fields['instruct']=request['description']
   scene.dump(folder/'native-fields.json',fields)
   files={k:(None,str(v)) for k,v in fields.items()}
   if source:
    with Path(source['reference']['path']).open('rb') as audio:
     files['ref_audio']=(Path(source['reference']['path']).name,audio,'audio/wav');response=requests.post('http://127.0.0.1:5196/generate',files=files,timeout=(10,900))
   else:response=requests.post('http://127.0.0.1:5196/generate',files=files,timeout=(10,900))
   if response.status_code!=200:
    (folder/'native-error.txt').write_text(response.text);raise RuntimeError('VoiceStudio could not generate this audition. Check that its local service and VoxCPM2 are available.')
   raw=folder/'voice.wav';raw.write_bytes(response.content)
   scene.dump(folder/'speech-request.json',{'text':request['text']})
   decoded=subprocess.run([str(scene.B.INDEX_RUNTIME/'venv/bin/python'),str(scene.STUDY/'take_media.py'),str(raw),str(folder)],capture_output=True,text=True,check=True,timeout=90)
   r['audio']=json.loads(decoded.stdout)
   check=subprocess.run([PYTHON,str(scene.STUDY/'speech_check.py'),str(folder/'speech-request.json'),str(raw)],capture_output=True,text=True,timeout=120)
   r['word_check']=json.loads(check.stdout) if check.returncode==0 else {'error':'Automatic word check unavailable; listen to the recording'}
   downloaded=json.loads((scene.STUDY.parents[0]/'paper-14-study/downloads.json').read_text())
   r['model_provenance']=next(m for m in downloaded['models'] if m['repo']=='openbmb/VoxCPM2')
   r['state']='saved'
 except requests.RequestException as exc:
  (folder/'native-error.txt').write_text(str(exc));r['state']='failed';r['error']='VoiceStudio is not responding. Start its local service and retry. Earlier recordings are safe.'
 except Exception as exc:r['state']='failed';r['error']=str(exc)
 finally:
  r['elapsed_seconds']=time.time()-tick;scene.dump(folder/'audition.json',r)
  import asset_passport
  asset_passport.capture(r)
  if release_queue:scene.QUEUE.release()
def save_profile(q):
 r=get(q.get('audition_id',''));name=str(q.get('name','')).strip()
 if not 1<=len(name)<=100:raise ValueError('Give the voice a name, up to 100 characters')
 if r['state']!='saved':raise ValueError('Generate and listen to an audition before saving its voice')
 for p in PROFILES.glob('*.json'):
  existing=json.loads(p.read_text())
  if existing['audition_id']==r['id'] and existing['name']==name:return existing
 value=str(uuid.uuid4());p={'id':value,'created':time.time(),'name':name,'audition_id':r['id'],'engine':'VoxCPM2','design_request':{k:v for k,v in r['request'].items() if k!='profile'},'reference':{'path':r['audio']['path'],'sha256':scene.digest(r['audio']['path']),'transcript':r['request']['text']},'word_check':r.get('word_check'),'selection':'Saved from this audition. No automatic emotion, apparent age or identity approval.','scene_casting':'Not connected; this profile can be reused on the designer page.'}
 scene.dump(PROFILES/(value+'.json'),p);return p
def media(value,original=False):
 r=get(value)
 if r['state']!='saved':raise ValueError('Audio not ready')
 return Path(r['audio']['path'] if original else r['audio']['listening_path'])
