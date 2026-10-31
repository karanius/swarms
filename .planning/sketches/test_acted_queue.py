"""The second arm must use conversion, never silently return to written-direction TTS."""
import sys,tempfile,uuid
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import batch_queue as q
with tempfile.TemporaryDirectory() as d:
 q.ROOT=Path(d);q.ACTIVE=None;calls=[];records=[]
 def upstream(path,data=None):
  if path.endswith('/state'):return {'busy':False,'auditions':records}
  assert all(r['state']=='saved' for r in records)
  calls.append((path,data));r={'id':str(uuid.uuid4()),'state':'saved'};records.append(r);return r
 def request(style):return {'token':str(uuid.uuid4()),'count':2,'seed_mode':'fixed','seed':65,'recipe':{'text':'You are safe here.','profile_id':str(uuid.uuid4()),'performance_direction':'Acting example','target_style':style,'reference_id':'chosen-anger-sample','steps':10,'guidance':2}}
 with patch.object(q,'upstream',upstream),patch.object(q.threading.Thread,'start',lambda self:None):
  b=q.start(request('anger'));q.run(q.ACTIVE)
  assert q.ACTIVE['state']=='complete'
  assert [r[0] for r in calls]==['/api/designer/run','/api/designer/convert-performance']
  assert calls[1][1]['reference_id']=='chosen-anger-sample'
  assert calls[1][1]['target_style']=='anger' and calls[1][1]['performance_direction']==''
  assert calls[1][1]['profile_id']==calls[0][1]['profile_id']
  assert calls[1][1]['seed']==calls[0][1]['seed']==65
  try:q.start(request('reassurance'));raise AssertionError('Unsupported style accepted')
  except ValueError:pass
 print('PASS: sequential neutral then acted conversion; fixed identity/words/seed; unsupported reference rejected')
