import tempfile,time,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import batch_queue as q
with tempfile.TemporaryDirectory() as d:
 q.ROOT=Path(d);q.ACTIVE=None;calls=[];records=[]
 def upstream(path,data=None):
  if path.endswith('/state'):return {'busy':False,'auditions':records}
  assert all(r['state']=='saved' for r in records)
  calls.append(data);r={'id':str(len(calls)),'state':'saved'};records.append(r);return r
 with patch.object(q,'upstream',upstream),patch.object(q.threading.Thread,'start',lambda self:None):
  b=q.start({'token':'c8b86bd0-16d1-43e5-a501-198913d135a5','count':2,'seed_mode':'fixed','seed':65,'recipe':{'text':'You are safe here.','profile_id':'441c4405-8daa-4522-b863-db6e2eeac8e8','performance_direction':'Warm reassurance','steps':10,'guidance':2}})
  q.run(q.ACTIVE)
 assert len(calls)==2
 assert calls[0]['performance_direction']=='Neutral, natural conversational delivery, without added emotion.'
 assert calls[1]['performance_direction']=='Warm reassurance'
 assert {k:v for k,v in calls[1].items() if k!='performance_direction'}=={k:v for k,v in calls[0].items() if k!='performance_direction'}
 assert q.ACTIVE['state']=='complete'
 print('PASS: two sequential takes, identical voice/text/settings, explicit neutral and emotion directions, with identical voice/text/settings')
