import sys,tempfile,hashlib,uuid,copy
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import batch_queue as q
with tempfile.TemporaryDirectory() as d:
 root=Path(d);raw=root/'voice.wav';raw.write_bytes(b'fixture audio');ref={'path':'same-reference.wav','sha256':'reference-hash','transcript':'Reference words.'};pid=str(uuid.uuid4());request={'profile':{'reference':ref},'text':'You are safe here.','seed':65,'steps':10,'guidance':2,'performance_direction':q.NEUTRAL_DIRECTION,'mode':'performance'}
 neutral={'id':'saved-neutral','state':'saved','engine':'VoxCPM2','request':request,'audio':{'path':str(raw),'listening_path':str(raw),'sha256':hashlib.sha256(raw.read_bytes()).hexdigest()}}
 state={'busy':False,'profiles':[{'id':pid,'reference':ref}],'auditions':[neutral]}
 assert q.matching_neutral(state,pid,request['text'],65,10,2)==neutral
 for text,seed,steps,guidance in [('Different words.',65,10,2),(request['text'],66,10,2),(request['text'],65,12,2),(request['text'],65,10,3)]:assert q.matching_neutral(state,pid,text,seed,steps,guidance) is None
 altered=copy.deepcopy(state);altered['profiles'][0]['reference']={**ref,'sha256':'different'};assert q.matching_neutral(altered,pid,request['text'],65,10,2) is None
 q.ROOT=root;q.ACTIVE=None;calls=[]
 def upstream(path,data=None):
  if path.endswith('/state'):return state
  calls.append(data);r={'id':'new-emotion','state':'saved'};state['auditions'].append(r);return r
 with patch.object(q,'upstream',upstream),patch.object(q.threading.Thread,'start',lambda self:None):
  b=q.start({'token':str(uuid.uuid4()),'count':2,'seed_mode':'fixed','seed':65,'recipe':{'text':request['text'],'profile_id':pid,'steps':10,'guidance':2,'performance_direction':'Joyful'}});q.run(q.ACTIVE)
 assert len(calls)==1 and calls[0]['performance_direction']=='Joyful'
 assert b['items'][0]['id']=='saved-neutral' and b['items'][0]['reused']
 raw.write_bytes(b'changed');assert q.matching_neutral(state,pid,request['text'],65,10,2) is None
 print('PASS: matching baseline reused; only emotion dispatched; changed inputs/reference/corrupt audio rejected')
