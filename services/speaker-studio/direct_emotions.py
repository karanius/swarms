"""One-pass generation from a kept emotional character reference; promotion is evidence-gated."""
import copy,json,re,threading,time,uuid
import scene,voice_designer as d,performance_bridge as bridge,emotion_checkpoints as checkpoints
ROOT=d.DATA/'direct-emotions';ROOT.mkdir(exist_ok=True)
LOCK=threading.RLock()
def save(p):scene.dump(ROOT/(p['id']+'.json'),p)
def load(value):return json.loads((ROOT/(str(uuid.UUID(value))+'.json')).read_text())
def public(p):
 normal=lambda text:' '.join(re.findall(r"[^\W_]+(?:['’][^\W_]+)*",text.casefold()))
 p=copy.deepcopy(p);qualified={'VoxCPM2':set(),'IndexTTS 2.5':set()}
 for run in p['runs']:
  r=d.get(run['id']);run.update(state=r['state'],error=r.get('error'),word_check=r.get('word_check'),elapsed_seconds=r.get('elapsed_seconds'))
  if r['state']=='saved' and r.get('word_check',{}).get('exact_words') and run.get('verdict')=='keep' and not run.get('deleted') and normal(run['text'])!=normal(p['reference']['transcript']):qualified[run['engine']].add(normal(run['text']))
 p['qualifying_by_engine']={k:len(v) for k,v in qualified.items()};p['qualifying_sentences']=max(p['qualifying_by_engine'].values());p['status']='qualified' if p['qualifying_sentences']>=3 else 'experimental'
 return p
def listing():
 with LOCK:return {'profiles':sorted((public(json.loads(path.read_text())) for path in ROOT.glob('*.json')),key=lambda p:p['created'],reverse=True)}
def promote(q):
 with LOCK:
  source=q['source_id'];r=d.get(source);approval=None;s=None
  checkpoint_id=q.get('checkpoint_id') or r['request'].get('checkpoint_id')
  if checkpoint_id:
   s=checkpoints.load(checkpoint_id)
   for a in s['attempts']:
    if a.get('conversion_id')==source and a.get('final_decision')=='keep':approval={'actor_approval':a['actor_approval'],'reviews':a['reviews']}
    for h in a.get('conversion_history',[]):
     if h['id']==source and h.get('decision')=='keep':approval={'actor_approval':a['actor_approval'],'reviews':a['reviews']}
  if not approval:
   if q.get('accept_reference') is not True:raise ValueError('Keep a converted character result before creating a direct emotion profile')
   if r['request'].get('mode') not in ('acted_conversion','reference_performance') or r['request'].get('target_style') not in ('anger','joy','sadness','happiness'):raise ValueError('This older recording has no recorded emotional-reference route; use a checkpoint result')
   approval={'selection':'Selected as an experimental direct reference; emotion and identity are not approved by this selection','created':time.time()}
  if r['state']!='saved' or not r.get('word_check',{}).get('exact_words'):raise ValueError('The reference must have readable audio and a successful word check')
  style=s['style'] if s else r['request']['target_style']
  if style=='happiness':style='joy'
  for path in ROOT.glob('*.json'):
   p=json.loads(path.read_text())
   if p['source_id']==source:return public(p)
  identity=d.save_profile({'audition_id':source,'name':'Santa · '+style+' · direct reference'})
  p={'id':str(uuid.uuid4()),'schema':'direct-emotion/1','created':time.time(),'name':'Santa · '+style,
     'checkpoint_id':s['id'] if s else None,'source_id':source,'style':style,'identity_profile':identity,
     'reference':copy.deepcopy(identity['reference']),'approval_snapshot':approval,'default_seed':r['request']['seed'],
     'runs':[],'deleted':False,'source_elapsed_seconds':r.get('elapsed_seconds')}
  actor=d.get(r['actor_audition_id']) if r.get('actor_audition_id') else None
  if actor:p['development_elapsed_seconds']=(r.get('elapsed_seconds') or 0)+(actor.get('elapsed_seconds') or 0)
  save(p);return public(p)
def command(q):
 with LOCK:
  p=load(q['id']);action=q['action']
  if action=='generate':
   if p.get('deleted'):raise ValueError('Restore this profile before generating')
   token=str(uuid.UUID(q['token']))
   if any(r['token']==token for r in p['runs']):return public(p)
   text=str(q.get('text','')).strip()
   if len(re.findall(r"[^\W_]+(?:['’][^\W_]+)*",text))>35:raise ValueError('Use no more than 35 words')
   engine=q.get('engine','vox')
   if engine not in ('vox','index'):raise ValueError('Choose a supported direct engine')
   seed=checkpoints.integer(q.get('seed',p['default_seed']),'Seed')
   request=d.validate({'text':text,'seed':seed,'steps':q.get('steps',10),'guidance':q.get('guidance',2)},reference_profile=p['identity_profile'])
   snapshot={k:copy.deepcopy(v) for k,v in p.items() if k not in ('runs','deleted')}
   qualification=q.get('qualification')
   if qualification is not None:
    if not isinstance(qualification,dict) or type(qualification.get('case')) is not int or not 1<=qualification['case']<=3:raise ValueError('Invalid qualification case')
    qualification={'suite':str(uuid.UUID(qualification['suite'])),'case':qualification['case'],'total':3}
    request['qualification']=copy.deepcopy(qualification)
   request.update(emotion_route='direct',direct_emotion_profile=snapshot,target_style=p['style'],source_emotion_id=p['source_id'])
   if engine=='index':
    duration=q.get('duration_scale',1.0)
    if type(duration) not in (int,float) or not .5<=duration<=2:raise ValueError('Duration scale must be between 0.5 and 2')
    guide=copy.deepcopy(p['reference']);guide.update(id='kept-character:'+p['source_id'],label='Kept Santa · '+p['style'],emotion=p['style'],terms='Locally generated character reference; parent sources are linked in the passport')
    request.update(mode='reference_performance',emotion_reference=guide,strength=1.0,duration_scale=duration,performance_direction='')
   if not scene.QUEUE.acquire(False):raise ValueError('Another recording is running; wait until it finishes')
   try:
    r=d.create_record(request);r['engine']='IndexTTS 2.5' if engine=='index' else 'VoxCPM2';scene.dump(d.AUDITIONS/r['id']/'audition.json',r)
    p['runs'].append({'id':r['id'],'token':token,'text':request['text'],'engine':r['engine'],'seed':seed,'created':time.time(),'verdict':None,'reviews':[],'deleted':False,'qualification':qualification})
    save(p);threading.Thread(target=bridge.run if engine=='index' else d.run,args=(r,),daemon=True).start()
   except Exception:scene.QUEUE.release();raise
  elif action=='review':
   run=next((r for r in p['runs'] if r['id']==q.get('recording_id')),None)
   if not run:raise ValueError('Choose a recording from this direct profile')
   r=d.get(run['id']);choice=q.get('choice')
   if r['state']!='saved':raise ValueError('Wait for the recording to finish')
   if choice not in ('keep','emotion','identity','quality','words'):raise ValueError('Choose an assessment')
   if choice=='keep' and not r.get('word_check',{}).get('exact_words'):raise ValueError('The word check needs review; this take cannot qualify the direct profile')
   run['verdict']=choice;run['reviews'].append({'choice':choice,'created':time.time()});save(p)
  elif action=='purge':
   run=next((r for r in p['runs'] if r['id']==q.get('recording_id')),None)
   if not run or not run.get('deleted'):raise ValueError('Only trashed recordings can be removed from this workspace')
   run['workspace_removed']=True;save(p)
  elif action=='trash':
   if type(q.get('deleted')) is not bool:raise ValueError('Choose delete or restore')
   if q.get('recording_id'):
    run=next((r for r in p['runs'] if r['id']==q['recording_id']),None)
    if not run:raise ValueError('Unknown recording')
    if run.get('workspace_removed'):raise ValueError('This recording was removed from the workspace; archive files remain')
    if d.get(run['id'])['state'] in ('queued','running'):raise ValueError('Wait for generation before deleting')
    run['deleted']=q['deleted']
   else:
    if any(d.get(run['id'])['state'] in ('queued','running') for run in p['runs']):raise ValueError('Wait for generation before deleting')
    p['deleted']=q['deleted']
   save(p)
  else:raise ValueError('Unknown direct emotion action')
  return public(p)
def recover():
 with LOCK:
  for path in ROOT.glob('*.json'):
   p=json.loads(path.read_text())
   for run in p['runs']:
    r=d.get(run['id'])
    if r['state'] in ('queued','running'):
     r.update(state='failed',error='Studio restarted during direct generation. Inspect this attempt before retrying.');scene.dump(d.AUDITIONS/r['id']/'audition.json',r)
