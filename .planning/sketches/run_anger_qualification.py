"""Resume-safe sequential qualification; listening verdicts are never inferred."""
import json,time,uuid,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
BASE='http://127.0.0.1:5198'
ROOT=Path(__file__).resolve().parents[2]/'services/speaker-studio/.runtime/voice-designer/qualification'
ROOT.mkdir(exist_ok=True)
PLAN=ROOT/'anger-three-lines-v1.json'
def api(path,data=None):
 request=Request(BASE+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json','Origin':BASE})
 with urlopen(request,timeout=30) as response:return json.load(response)
def save(plan):
 tmp=PLAN.with_suffix('.tmp');tmp.write_text(json.dumps(plan,indent=2));tmp.replace(PLAN)
p=next(p for p in api('/api/designer/direct-emotions')['profiles'] if p['source_id']=='86ccdc99-2527-46e4-84fb-d93c635ef073')
assert not p['deleted']
settings={'seed':65,'steps':10,'guidance':2,'engine':'vox'}
if PLAN.exists():
 plan=json.loads(PLAN.read_text());assert plan['profile_id']==p['id'] and plan['reference_sha256']==p['reference']['sha256'] and plan['settings']==settings
else:
 plan={'suite':str(uuid.uuid4()),'profile_id':p['id'],'source_id':p['source_id'],'reference_sha256':p['reference']['sha256'],'settings':settings,'state':'preparing',
       'cases':[{'number':i+1,'text':text,'token':str(uuid.uuid4()),'recording_id':None,'listening_assessment':'pending'} for i,text in enumerate([
         'Those gifts were meant for everyone, and I will not let you take them all.',
         'I asked you to wait outside until I was ready.',
         'You broke your promise, and I need you to put this right.'
       ])]}
 save(plan)
assert hashlib.sha256(Path(p['reference']['path']).read_bytes()).hexdigest()==plan['reference_sha256']
for case in plan['cases']:
 if not case['recording_id']:
  result=api('/api/designer/direct-emotion-action',{'id':p['id'],'action':'generate','token':case['token'],'text':case['text'],**settings,'qualification':{'suite':plan['suite'],'case':case['number']}})
  case['recording_id']=next(r['id'] for r in result['runs'] if r['token']==case['token']);plan['state']='generating';save(plan)
  print('Started qualification line',case['number'],flush=True)
 until=time.monotonic()+1000
 while True:
  current=next(x for x in api('/api/designer/direct-emotions')['profiles'] if x['id']==p['id'])
  run=next(r for r in current['runs'] if r['id']==case['recording_id'])
  if run['state'] in ('saved','failed'):break
  if time.monotonic()>until:raise TimeoutError('The same submitted recording remains active; inspect it before resuming')
  time.sleep(2)
 case.update(state=run['state'],word_check=run.get('word_check'),elapsed_seconds=run.get('elapsed_seconds'),listening_assessment=run.get('verdict') or 'pending')
 if run['state']=='failed':plan['state']='generation_failed';save(plan);raise RuntimeError(run.get('error','Generation failed'))
 passport=api('/api/designer/passport?id='+case['recording_id']);root=next(n for n in passport['passport']['nodes'] if n['id']==passport['passport']['root']);q=root['request']
 assert q['profile']['audition_id']==plan['source_id'] and q['profile']['reference']['sha256']==plan['reference_sha256']
 assert q['emotion_route']=='direct' and all(q[k]==settings[k] for k in ('seed','steps','guidance')) and q['text']==case['text']
 assert q['qualification']=={'suite':plan['suite'],'case':case['number'],'total':3}
 assert all(a['status']=='match' for a in passport['integrity']['assets'])
 case.update(passport_id=passport['passport']['passport_id'],lineage_verified=True,playback_path=root['audio']['listening_path']);save(plan)
 print('Saved qualification line',case['number'],'words checked:',bool((run.get('word_check')or{}).get('exact_words')),flush=True)
verdicts=[c['listening_assessment'] for c in plan['cases']]
plan['state']='qualified_by_listener' if all(v=='keep' for v in verdicts) else 'awaiting_listener_assessment' if 'pending' in verdicts else 'needs_improvement'
save(plan)
print('Three recordings saved. Listening assessment state:',plan['state'],flush=True)
