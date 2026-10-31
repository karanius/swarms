"""Acted-reference performance transfer with independent identity and emotion inputs."""
from pathlib import Path
import copy,fcntl,json,shutil,subprocess,time
import scene
import voice_designer as designer

def catalog():
 libraries=json.loads((scene.STUDY/'scene-libraries.json').read_text());out={}
 for lib in libraries.values():
  for voice in lib.get('voices',lib.get('roles',{})).values():
   for emotion,ref in voice.get('performances',{}).items():
    if ref['id'] not in out:out[ref['id']]={**copy.deepcopy(ref),'emotion':emotion,'speaker':voice['speaker_id'],'library':lib['id'],'label':lib['name'].split(' · ')[0]+' · '+voice['speaker_id']+' · '+emotion,'terms':lib['terms']}
 return out

def resolve(value,identity):
 if value=='identity':ref=copy.deepcopy(identity);ref.setdefault('id','character-audition:'+ref['audition_id']);ref.update(emotion='neutral',label='Fixed character identity · neutral guidance',terms='Locally designed synthetic reference')
 else:
  ref=catalog().get(value)
  if not ref:raise ValueError('Choose an available performed emotion reference. No substitute is selected automatically.')
 if scene.digest(ref['path'])!=ref['sha256']:raise ValueError('The emotion reference changed')
 return ref

def default_reference(style):
 if style=='neutral':return 'identity'
 for ident,ref in catalog().items():
  if ref['speaker']=='crema:1006' and ref['emotion']==style:return ident
 return ''

def request(identity,name,text,style,reference_id,strength,seed,duration_scale=1.0):
 if not 0<=float(strength)<=1:raise ValueError('Emotion strength must be between zero and one')
 if not .5<=float(duration_scale)<=2:raise ValueError('Duration scale must be between 0.5 and 2')
 q=designer.validate({'text':text,'seed':seed},reference_profile={'name':name,'reference':identity})
 q.update(mode='reference_performance',target_style=style,emotion_reference=resolve(reference_id,identity),strength=float(strength),duration_scale=float(duration_scale),performance_direction='')
 return q

def run(r,release_queue=True):
 folder=designer.AUDITIONS/r['id'];q=r['request'];started=time.time();r['engine']='IndexTTS 2.5';r['assessment']='Acted emotion reference transfer; words, identity and delivery require separate checks.'
 try:
  r['state']='running';scene.dump(folder/'audition.json',r)
  vector=q.get('emotion_vector')
  if vector is not None and (not isinstance(vector,list) or len(vector)!=8 or any(type(v) not in (int,float) or not 0<=v<=1 for v in vector)):raise ValueError('Native emotion vector requires eight finite values between zero and one')
  identity=copy.deepcopy(q['profile']['reference']);identity.setdefault('id','character-reference:'+str(identity.get('audition_id',identity.get('sha256'))));guide=q['emotion_reference']
  for ref in [identity,guide]:
   if scene.digest(ref['path'])!=ref['sha256']:raise ValueError('A pinned input recording changed')
  # The key "guide" avoids a neutral-condition collision replacing the identity sample.
  native_fields={'engine':'IndexTTS 2.5','text':q['text'],'identity':identity,'emotion':guide,'emotion_mode':q.get('emotion_mode','audio'),'emotion_vector':q.get('emotion_vector'),'emotion_reference_applied':not bool(q.get('emotion_vector')),'emo_alpha':q['strength'],'seed':q['seed'],'duration_scale':q['duration_scale'],'use_emo_text':False,'use_random':False}
  scene.dump(folder/'native-fields.json',native_fields)
  with (scene.STUDY/'take-generation.lock').open('a') as lock:
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:raise RuntimeError('The notebook is generating. Wait until it finishes.')
   engine=scene.module('character_index_bridge',scene.STUDY/'indextts_experiment.py')
   native=engine.run(text=q['text'],speaker='designed-character',seed=q['seed'],duration_scale=q['duration_scale'],conditions=[{'emotion':'guide','strength':q['strength'],**({'emo_vector':q['emotion_vector']} if q.get('emotion_vector') else {})}],reference_overrides={'neutral':identity,'guide':guide})
   scene.dump(folder/'native-result.json',native);raw=folder/'voice.wav';shutil.copyfile(native['takes'][0]['path'],raw)
   decoded=subprocess.run([str(scene.B.INDEX_RUNTIME/'venv/bin/python'),str(scene.STUDY/'take_media.py'),str(raw),str(folder)],capture_output=True,text=True,check=True,timeout=90)
   r['audio']=json.loads(decoded.stdout);scene.dump(folder/'speech-request.json',{'text':q['text']})
   check=subprocess.run([designer.PYTHON,str(scene.STUDY/'speech_check.py'),str(folder/'speech-request.json'),str(raw)],capture_output=True,text=True,timeout=120)
   r['word_check']=json.loads(check.stdout) if check.returncode==0 else {'error':'Automatic word check unavailable; listening required'}
   r['model_provenance']={k:native['request'][k] for k in ['code_revision','model_revision','device','precision']};r['state']='saved'
 except Exception as exc:r['state']='failed';r['error']=str(exc)
 finally:
  r['elapsed_seconds']=time.time()-started;scene.dump(folder/'audition.json',r)
  import asset_passport
  asset_passport.capture(r)
  if release_queue:scene.QUEUE.release()
