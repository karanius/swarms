"""Durable sequential audition batches. Model work stays in the existing studio."""
import hashlib,json,secrets,threading,time,uuid
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[2]/'services/speaker-studio/.runtime/santa-batches'
ROOT.mkdir(parents=True,exist_ok=True)
LOCK=threading.RLock();ACTIVE=None

def upstream(path,data=None):
 req=Request('http://127.0.0.1:5197'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json','Origin':'http://127.0.0.1:5197'})
 try:
  with urlopen(req,timeout=20) as r:return json.load(r)
 except HTTPError as e:
  try:message=json.load(e).get('error','Studio rejected generation')
  except Exception:message='Studio rejected generation'
  raise ValueError(message)
def save(b):
 p=ROOT/(b['id']+'.json');tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(b,indent=2));tmp.replace(p)
def load(value):
 try:value=str(uuid.UUID(value))
 except Exception:raise ValueError('Unknown batch')
 return json.loads((ROOT/(value+'.json')).read_text())
def integer(value,lo,hi,label):
 if isinstance(value,bool) or not isinstance(value,(int,float)) or int(value)!=value or not lo<=value<=hi:raise ValueError(label+' is out of range')
 return int(value)
NEUTRAL_DIRECTION='Neutral, natural conversational delivery, without added emotion.'
def matching_neutral(state,profile_id,text,seed,steps,guidance):
 profile=next((p for p in state.get('profiles',[]) if p['id']==profile_id),None)
 if not profile:return None
 reference=profile.get('reference',{})
 if not reference.get('sha256'):return None
 for r in state.get('auditions',[]):
  req=r.get('request',{});ref=(req.get('profile') or {}).get('reference',{})
  if r.get('state')!='saved' or r.get('engine')!='VoxCPM2' or req.get('mode')!='performance':continue
  if (req.get('text'),req.get('seed'),req.get('steps'),req.get('guidance'),req.get('performance_direction'))!=(text,seed,steps,guidance,NEUTRAL_DIRECTION):continue
  if any(ref.get(k)!=reference.get(k) for k in ('path','sha256','transcript')):continue
  audio=r.get('audio',{});path=Path(audio.get('path',''))
  if not path.is_file() or not Path(audio.get('listening_path','')).is_file():continue
  if not audio.get('sha256') or hashlib.sha256(path.read_bytes()).hexdigest()!=audio['sha256']:continue
  return r
 return None

def start(q):
 global ACTIVE
 token=str(uuid.UUID(q.get('token','')))
 with LOCK:
  if (ROOT/(token+'.json')).exists():return load(token)
  if ACTIVE and ACTIVE['state'] in ('queued','running','stopping'):raise ValueError('An audition batch is already running')
  count=integer(q.get('count',1),1,50,'Count');mode=q.get('seed_mode','fixed')
  if mode not in ('fixed','increment','random'):raise ValueError('Unknown seed mode')
  seed=integer(q.get('seed',42),0,2147483647,'Seed');inc=integer(q.get('increment',1),1,2147483647,'Increment')
  recipe=q.get('recipe',{});text=str(recipe.get('text','')).strip();description=str(recipe.get('description','')).strip()
  profile_id=recipe.get('profile_id');direction=str(recipe.get('performance_direction','')).strip()
  target_style=recipe.get('target_style')
  if target_style is not None and target_style not in ('anger','joy','sadness'):raise ValueError('Choose Anger, Joy or Sadness; other deliveries need an acting reference first')
  if profile_id:
   profile_id=str(uuid.UUID(profile_id))
   if count!=2 or mode!='fixed' or not 1<=len(direction)<=1500:raise ValueError('Emotion comparisons require two fixed-seed takes and a delivery direction')
  if not 5<=len(text)<=500 or (not profile_id and not 5<=len(description)<=1500):raise ValueError('Check the audition sentence and voice brief')
  steps=integer(recipe.get('steps',10),1,64,'Steps');guidance=recipe.get('guidance',2)
  if isinstance(guidance,bool) or not isinstance(guidance,(int,float)) or not .1<=guidance<=8:raise ValueError('Guidance is out of range')
  state=upstream('/api/designer/state')
  if state['busy']:raise ValueError('Another studio generation is running; wait until it finishes')
  b={'id':token,'created':time.time(),'state':'queued','count':count,'seed_mode':mode,'initial_seed':seed,'next_seed':seed,'increment':inc,'recipe':{'text':text,'description':description,'steps':steps,'guidance':guidance},'items':[],'cancel_requested':False,'dispatching':False}
  if profile_id:b['recipe']={'text':text,'profile_id':profile_id,'steps':steps,'guidance':guidance};b['performance_direction']=direction;b['neutral_direction']=NEUTRAL_DIRECTION
  if target_style:
   b['strategy']='acted_conversion';b['target_style']=target_style
   if recipe.get('reference_id') is not None:b['reference_id']=recipe['reference_id']
  if profile_id:
   cached=matching_neutral(state,profile_id,text,seed,steps,guidance)
   if cached:b['items'].append({'id':cached['id'],'seed':seed,'state':'saved','reused':True})
  save(b);ACTIVE=b;threading.Thread(target=run,args=(b,),daemon=True).start();return dict(b)
def run(b):
 try:
  with LOCK:b['state']='running';save(b)
  while True:
   with LOCK:
    pending=next((i for i in b['items'] if i['state'] not in ('saved','failed')),None)
    if not pending and (b['cancel_requested'] or len(b['items'])>=b['count']):
     b['state']='stopped' if b['cancel_requested'] else 'complete';save(b);return
   if pending:
    state=upstream('/api/designer/state');record=next((r for r in state['auditions'] if r['id']==pending['id']),None)
    if not record:raise ValueError('A submitted audition could not be found; batch stopped to avoid duplication')
    with LOCK:
     pending['state']=record['state'];save(b)
     if record['state']=='failed':raise ValueError(record.get('error','Audition failed'))
    if record['state']!='saved':time.sleep(1);continue
    continue
   with LOCK:
    seed=secrets.randbelow(2147483648) if b['seed_mode']=='random' else b['next_seed']
    b['dispatching']=True;save(b)
   payload={**b['recipe'],'seed':seed}
   if b.get('performance_direction'):payload['performance_direction']=b['performance_direction'] if len(b['items'])==1 else b.get('neutral_direction','')
   route='/api/designer/run'
   if b.get('strategy')=='acted_conversion' and len(b['items'])==1:
    route='/api/designer/convert-performance';payload['target_style']=b['target_style'];payload['performance_direction']=''
    if 'reference_id' in b:payload['reference_id']=b['reference_id']
   record=upstream(route,payload)
   with LOCK:
    b['dispatching']=False;b['items'].append({'id':record['id'],'seed':seed,'state':record['state']})
    b['next_seed']=(seed+b['increment'])%2147483648 if b['seed_mode']=='increment' else seed
    save(b)
 except Exception as e:
  with LOCK:b['state']='failed';b['error']=str(e);save(b)
def stop(value):
 with LOCK:
  b=ACTIVE if ACTIVE and ACTIVE['id']==value else load(value)
  if b['state'] in ('queued','running','stopping'):b['cancel_requested']=True;b['state']='stopping';save(b)
  return dict(b)
def recover():
 global ACTIVE
 for p in sorted(ROOT.glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True):
  b=json.loads(p.read_text())
  if b['state'] not in ('queued','running','stopping'):continue
  ACTIVE=b
  if b.get('dispatching'):
   b['state']='failed';b['error']='Service restarted during submission. Check saved auditions before retrying to avoid duplicates.';save(b)
  else:threading.Thread(target=run,args=(b,),daemon=True).start()
  break
recover()
