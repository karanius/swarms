"""Durable human gates between actor generation and character conversion."""
import copy,json,re,threading,time,uuid
import scene,voice_designer as designer,performance_bridge as bridge,acted_conversion as conversion
ROOT=designer.DATA/'emotion-checkpoints';ROOT.mkdir(exist_ok=True)
LOCK=threading.RLock()
def save(s):scene.dump(ROOT/(s['id']+'.json'),s)
def load(value):return json.loads((ROOT/(str(uuid.UUID(value))+'.json')).read_text())
def integer(v,label):
 if type(v) is not int or not 0<=v<=2147483647:raise ValueError(label+' must be a whole number between 0 and 2147483647')
 return v
def refresh(s):
 for attempt in s['attempts']:
  for kind in ('actor','conversion'):
   if attempt.get(kind+'_id'):
    r=designer.get(attempt[kind+'_id']);attempt[kind+'_state']=r['state']
    attempt[kind+'_error']=r.get('error');attempt[kind+'_words_checked']=r.get('word_check',{}).get('exact_words',False)
 return s
def listing():
 with LOCK:return {'sessions':sorted((refresh(json.loads(p.read_text())) for p in ROOT.glob('*.json') if not json.loads(p.read_text()).get('workspace_removed')),key=lambda s:s['created'],reverse=True)}
def create(q):
 token=str(uuid.UUID(q['token']))
 with LOCK:
  if (ROOT/(token+'.json')).exists():return refresh(load(token))
  source=designer.get(q['source'])
  if source['state']!='saved' or source['request']['mode']!='voice_design':raise ValueError('Choose a saved designed voice')
  text=str(q.get('text','')).strip().replace('..','…')
  if len(re.findall(r"[^\W_]+(?:['’][^\W_]+)*",text))>35:raise ValueError('Use no more than 35 words')
  profile=designer.save_profile({'audition_id':source['id'],'name':'Emotion checkpoint identity'})
  request=designer.validate({'profile_id':profile['id'],'text':text,'seed':source['request']['seed']})
  guide=conversion.guide_for(q['style'],q['reference_id'])
  s={'id':token,'created':time.time(),'schema':'emotion-checkpoints/1','source':source['id'],
     'profile':copy.deepcopy(request['profile']),'text':request['text'],'style':q['style'],'reference':guide,
     'default_seed':request['seed'],'attempts':[],'events':[]}
  save(s);return s

def command(q):
 with LOCK:
  s=refresh(load(q['id']));action=q['action'];attempt=next((a for a in s['attempts'] if a['token']==s.get('active_attempt') and not a.get('deleted')),next((a for a in reversed(s['attempts']) if not a.get('deleted')),None))
  if action=='purge':
   target=next((a for a in s['attempts'] if a['actor_id']==q.get('actor_id')),None) if q.get('actor_id') else s
   if target is None or not target.get('deleted'):raise ValueError('Only trashed items can be removed from this workspace')
   target['workspace_removed']=True;save(s)
  elif action=='trash':
   if s.get('workspace_removed'):raise ValueError('This test was removed from the workspace; archive files remain')
   if type(q.get('deleted')) is not bool:raise ValueError('Choose delete or restore')
   targets=[a for a in s['attempts'] if not q.get('actor_id') or a['actor_id']==q['actor_id']]
   if q.get('actor_id') and not targets:raise ValueError('Unknown attempt')
   if any(a.get(k+'_state') in ('queued','running') for a in targets for k in ('actor','conversion')):raise ValueError('Wait for generation before deleting')
   if q.get('actor_id'):targets[0]['deleted']=q['deleted']
   else:s['deleted']=q['deleted']
   save(s)
  elif action=='actor':
   if s.get('deleted'):raise ValueError('Restore this checkpoint before generating')
   token=str(uuid.UUID(q['token']))
   if any(a['token']==token for a in s['attempts']):return s
   if any(a.get(k+'_state') in ('queued','running') for a in s['attempts'] for k in ('actor','conversion')):raise ValueError('Wait for the current recording to finish')
   seed=integer(q.get('seed',s['default_seed']),'Actor seed');duration=q.get('duration_scale',1.0)
   if type(duration) not in (int,float) or not .5<=duration<=2:raise ValueError('Duration scale must be between 0.5 and 2')
   ref=s['reference']
   if scene.digest(ref['path'])!=ref['sha256']:raise ValueError('The saved acting sample changed; start a new checkpoint')
   request=bridge.request(ref,'Acting checkpoint',s['text'],conversion.STYLES[s['style']],ref['id'],1.0,seed,duration)
   request.update(checkpoint_id=s['id'],checkpoint_role='actor')
   if not scene.QUEUE.acquire(False):raise ValueError('Another recording is running; wait until it finishes')
   try:
    r=designer.create_record(request)
    attempt={'token':token,'created':time.time(),'actor_id':r['id'],'actor_state':r['state'],'seed':seed,
             'duration_scale':duration,'actor_decision':None,'reviews':[]}
    s['attempts'].append(attempt);s['active_attempt']=token;save(s)
    threading.Thread(target=bridge.run,args=(r,),daemon=True).start()
   except Exception:scene.QUEUE.release();raise
  elif action=='select_actor':
   if any(a.get(k+'_state') in ('queued','running') for a in s['attempts'] for k in ('actor','conversion')):raise ValueError('Wait for the current recording to finish')
   selected=next((a for a in s['attempts'] if a['actor_id']==q.get('actor_id')),None)
   if not selected or selected.get('deleted'):raise ValueError('Choose a saved actor attempt from this checkpoint')
   s['active_attempt']=selected['token'];save(s)
  elif action=='convert':
   if s.get('deleted') or (attempt and attempt.get('deleted')):raise ValueError('Restore this checkpoint or attempt before converting')
   if not attempt or q.get('actor_id')!=attempt['actor_id']:raise ValueError('Choose the current actor recording before approving it')
   token=str(uuid.UUID(q['token']))
   if token==attempt.get('conversion_token') or any(h.get('token')==token for h in attempt.get('conversion_history',[])):return s
   if attempt.get('conversion_state') in ('queued','running'):raise ValueError('Wait for the conversion to finish')
   if attempt.get('conversion_id') and q.get('retry') is not True:raise ValueError('Use conversion retry to preserve the approved actor')
   if designer.profile(s['profile']['id'])!=s['profile']:raise ValueError('The pinned character profile changed; start a new checkpoint')
   actor=designer.get(attempt['actor_id'])
   if actor['state']!='saved' or not actor.get('word_check',{}).get('exact_words'):raise ValueError('The actor recording must finish and pass its word check before conversion')
   seed=integer(q.get('seed',s['default_seed']),'Conversion seed')
   stamp={'actor_id':actor['id'],'actor_sha256':actor['audio']['sha256'],'emotion':True,'pace_quality':True,'created':time.time()}
   if q.get('approve') is not True:raise ValueError('Listen and approve the actor delivery before conversion')
   payload={'profile_id':s['profile']['id'],'text':s['text'],'seed':seed,'target_style':s['style'],
            'reference_id':s['reference']['id'],'approved_actor_id':actor['id'],'actor_approval':stamp,'checkpoint_id':s['id'],'conversion_settings':q.get('settings') or {'steps':30,'cfg':.7,'length_adjust':1.0}}
   r=conversion.start(payload)
   if attempt.get('conversion_id'):
    attempt.setdefault('conversion_history',[]).append({'id':attempt['conversion_id'],'state':attempt['conversion_state'],'seed':attempt['conversion_seed'],'decision':attempt.get('final_decision'),'token':attempt['conversion_token']})
   attempt.update(conversion_token=token,conversion_settings=copy.deepcopy(payload['conversion_settings']),final_decision=None,actor_decision='approved',actor_approval=stamp,conversion_id=r['id'],conversion_state=r['state'],conversion_seed=seed)
   save(s)
  elif action=='review':
   if not attempt:raise ValueError('Generate a recording before reviewing it')
   subject=q.get('subject');choice=q.get('choice')
   if subject not in ('actor','conversion') or choice not in ('keep','emotion','pace_quality','identity','words'):raise ValueError('Choose a listening assessment')
   if q.get('recording_id')!=attempt.get(subject+'_id'):raise ValueError('This review belongs to a different recording')
   if attempt.get(subject+'_state')!='saved':raise ValueError('Wait for the recording to finish before reviewing')
   review={'subject':subject,'choice':choice,'recording_id':q['recording_id'],'created':time.time()}
   attempt['reviews'].append(review)
   if subject=='actor':attempt['actor_decision']=choice
   else:attempt['final_decision']=choice
   save(s)
  else:raise ValueError('Unknown checkpoint action')
  return refresh(s)

def recover():
 """A service restart never silently replays an expensive submitted job."""
 with LOCK:
  for path in ROOT.glob('*.json'):
   s=json.loads(path.read_text())
   for attempt in s['attempts']:
    for kind in ('actor','conversion'):
     if attempt.get(kind+'_id'):
      r=designer.get(attempt[kind+'_id'])
      if r['state'] in ('queued','running'):
       r.update(state='failed',error='Studio restarted during this checkpoint. Inspect the saved attempt, then retry this step.')
       scene.dump(designer.AUDITIONS/r['id']/'audition.json',r)
