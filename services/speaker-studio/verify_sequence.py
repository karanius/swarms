"""Real sequential scene/adapter verification. No listener scores are invented."""
from pathlib import Path
import json,time,urllib.request
S=Path(__file__).resolve().parents[2]/'knowledge/research/paper-16-study';ledger=S/'scene-sequence-verification.json'
def api(path,data=None):
 q=urllib.request.Request('http://127.0.0.1:5197'+path,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json','Origin':'http://127.0.0.1:5197'})
 with urllib.request.urlopen(q,timeout=30) as r:return json.load(r)
plan=[('crema','index',None),('ravdess','index',None),('emns','index',None),('esd','vox',None),('esd','f5',None),('esd','dia',None),('esd','index','the-empty-seat-v1')]
# Single-line custom-reference smoke tests do not claim complete scenes.
plan += [(lib,model,None) for model in ['vox','f5','dia'] for lib in ['crema','ravdess','emns']]
report=json.loads(ledger.read_text()) if ledger.exists() else {'plan':'Three IndexTTS library scenes, three full ESD model scenes, held-out ESD scene, then custom-reference single-line adapter checks. Technical proof only.','runs':[],'listening':'Unrated; no library winner selected.'}
for i,(lib,model,scene) in enumerate(plan):
 key=f'{i}:{lib}:{model}:{scene}'
 previous=next((r for r in report['runs'] if r['key']==key),None)
 if previous and previous.get('state') not in ['queued','running']:continue
 if previous:ident=previous['id']
 else:
  q={'library':lib,'model':model}
  if scene:q['scene_id']=scene
  if i>=7:q['line_ids']=['01']
  r=api('/api/scene/run',q);ident=r['id'];previous={'key':key,'id':ident,'library':lib,'model':model,'kind':'single_line_adapter_check' if i>=7 else 'complete_scene','state':r['state']};report['runs'].append(previous);ledger.write_text(json.dumps(report,indent=2));print('START',key,flush=True)
 while True:
  r=next(r for r in api('/api/scene/experiments') if r['id']==ident)
  if r['state'] not in ['queued','running']:
   previous.update(state=r['state'],mix=bool(r.get('mix')),lines={k:{'state':v['state'],'error':v.get('error'),'word_check':v.get('record',{}).get('word_check')} for k,v in r['lines'].items()});ledger.write_text(json.dumps(report,indent=2));print('DONE',key,r['state'],flush=True);break
  time.sleep(2)
print('All planned technical runs attempted; listening remains open.',flush=True)
