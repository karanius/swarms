"""Generate an acted line first, then convert its timbre into the saved character."""
from pathlib import Path
import copy,json,shutil,subprocess,threading,time
import scene,voice_designer as designer,performance_bridge as bridge,seedvc_runner

STYLES={'anger':'anger','joy':'happiness','sadness':'sadness'}
def references():
 out=[]
 for ref in bridge.catalog().values():
  if ref['emotion'] not in STYLES.values():continue
  if not Path(ref['path']).is_file() or scene.digest(ref['path'])!=ref['sha256']:continue
  out.append({k:ref.get(k) for k in ('id','label','speaker','library','emotion','transcript','terms','sha256')})
 return {'references':out,'defaults':{k:bridge.default_reference(v) for k,v in STYLES.items()}}

def guide_for(style,reference_id=None):
 if style not in STYLES:raise ValueError('No qualified acting reference is connected for that delivery. Choose Anger, Joy or Sadness.')
 value=reference_id if reference_id is not None else bridge.default_reference(STYLES[style]);ref=bridge.catalog().get(value)
 if not ref:raise ValueError('The acting reference is unavailable; no substitute was selected.')
 if ref.get('emotion')!=STYLES[style]:raise ValueError('The selected sample does not match the requested emotion')
 if scene.digest(ref['path'])!=ref['sha256']:raise ValueError('The acting reference changed')
 return copy.deepcopy(ref)

def start(q):
 request=designer.validate(q);guide=guide_for(q.get('target_style'),q.get('reference_id'))
 settings=q.get('conversion_settings') or {'steps':30,'cfg':.7,'length_adjust':1.0}
 if type(settings.get('steps')) is not int or not 10<=settings['steps']<=100 or type(settings.get('cfg')) not in (int,float) or not 0<=settings['cfg']<=1 or type(settings.get('length_adjust')) not in (int,float) or not .5<=settings['length_adjust']<=2:raise ValueError('Check conversion steps, guidance and length ranges')
 if not request['profile']:raise ValueError('Choose a saved character voice')
 if q.get('approved_actor_id'):
  actor=designer.get(q['approved_actor_id']);approval=q.get('actor_approval') or {}
  aq=actor['request']
  if (actor['state']!='saved' or not actor.get('word_check',{}).get('exact_words') or
      aq.get('mode')!='reference_performance' or aq.get('text')!=request['text'] or
      aq.get('emotion_reference',{}).get('sha256')!=guide['sha256'] or
      aq.get('profile',{}).get('reference',{}).get('sha256')!=guide['sha256'] or
      approval.get('actor_id')!=actor['id'] or approval.get('actor_sha256')!=actor['audio']['sha256'] or
      approval.get('emotion') is not True or approval.get('pace_quality') is not True or
      scene.digest(actor['audio']['path'])!=actor['audio']['sha256']):
   raise ValueError('The approved actor recording does not match these inputs')
  request.update(approved_actor_id=actor['id'],actor_approval=copy.deepcopy(approval),checkpoint_id=q.get('checkpoint_id'))
 if not (seedvc_runner.RUNTIME/'venv/bin/python').is_file():raise ValueError('The voice-conversion runtime is unavailable')
 request.update(mode='acted_conversion',target_style=q['target_style'],emotion_reference=guide,
                conversion_revision=seedvc_runner.REVISION,performance_direction='',
                acting_engine='IndexTTS 2.5',conversion_settings=copy.deepcopy(settings))
 if not scene.QUEUE.acquire(False):raise ValueError('Another studio generation is running; wait until it finishes')
 try:
  r=designer.create_record(request);r['engine']='IndexTTS 2.5 → Seed-VC';scene.dump(designer.AUDITIONS/r['id']/'audition.json',r)
  threading.Thread(target=run,args=(r,),daemon=True).start();return r
 except Exception:scene.QUEUE.release();raise

def run(r):
 folder=designer.AUDITIONS/r['id'];q=r['request'];tick=time.time()
 try:
  r.update(state='running',phase='Generating the actor performance');scene.dump(folder/'audition.json',r)
  guide=q['emotion_reference'];identity=q['profile']['reference']
  for ref in (guide,identity):
   if scene.digest(ref['path'])!=ref['sha256']:raise ValueError('A pinned input recording changed')
  if q.get('approved_actor_id'):
   actor=designer.get(q['approved_actor_id'])
   if scene.digest(actor['audio']['path'])!=q['actor_approval']['actor_sha256']:raise ValueError('Approved actor audio changed')
  else:
   actor_q=bridge.request(guide,'Acting control',q['text'],STYLES[q['target_style']],guide['id'],1.0,q['seed'])
   actor=designer.create_record(actor_q);bridge.run(actor,release_queue=False)
  r['actor_audition_id']=actor['id']
  if actor['state']!='saved':raise RuntimeError(actor.get('error','The actor performance failed'))
  if not actor.get('word_check',{}).get('exact_words'):raise RuntimeError('The actor line failed its word check. Its recording is saved for inspection; conversion was not attempted.')
  r['phase']='Converting the actor into your character';scene.dump(folder/'audition.json',r)
  import fcntl
  with (scene.STUDY/'take-generation.lock').open('a') as lock:
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:raise RuntimeError('Another audio job is running; retry after it finishes')
   raw,conversion=seedvc_runner.convert(actor['audio']['path'],identity['path'],folder/'conversion',q['seed'],q['conversion_settings'])
   shutil.copyfile(raw,folder/'voice.wav')
  decoded=subprocess.run([str(scene.B.INDEX_RUNTIME/'venv/bin/python'),str(scene.STUDY/'take_media.py'),str(folder/'voice.wav'),str(folder)],capture_output=True,text=True,check=True,timeout=90)
  r['audio']=json.loads(decoded.stdout);scene.dump(folder/'speech-request.json',{'text':q['text']})
  check=subprocess.run([designer.PYTHON,str(scene.STUDY/'speech_check.py'),str(folder/'speech-request.json'),str(folder/'voice.wav')],capture_output=True,text=True,timeout=120)
  r['word_check']=json.loads(check.stdout) if check.returncode==0 else {'error':'Word check unavailable; listen before approving'}
  if not r['word_check'].get('exact_words'):raise RuntimeError('Converted words need review. The recording and diagnostic evidence are preserved.')
  r.update(state='saved',phase='Ready to listen',assessment='Acted emotion converted into the character. Emotion and identity require your listening.',
           model_provenance={'actor':actor.get('model_provenance'),'conversion':conversion},
           reference_used=True)
 except Exception as e:r.update(state='failed',error=str(e))
 finally:
  r['elapsed_seconds']=time.time()-tick;scene.dump(folder/'audition.json',r)
  import asset_passport
  asset_passport.capture(r);scene.QUEUE.release()
