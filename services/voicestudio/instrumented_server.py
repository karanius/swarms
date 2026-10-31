"""Research-only per-request evidence wrapper; upstream checkout is unmodified."""
from pathlib import Path
import sys,os,json,time,threading,hashlib
D=Path(__file__).resolve().parent;SOURCE=D/'upstream';sys.path[:0]=[str(SOURCE/'backend'),str(SOURCE)]
import torch,psutil
record=None;guard=threading.Lock();TRACE=Path(os.environ['OMNIVOICE_DATA_DIR']).parent/'inference-events.jsonl'
def observe(module,args):
 global record
 if record is None:return
 record['torch_forward_calls']+=1
 if len(record['torch_devices'])<8:
  devices=set()
  for p in module.parameters(recurse=False):devices.add(str(p.device))
  for a in args:
   if isinstance(a,torch.Tensor):devices.add(str(a.device))
  record['torch_devices']=sorted(set(record['torch_devices'])|devices)
handle=torch.nn.modules.module.register_module_forward_pre_hook(observe)
def mlx_stats():
 try:
  import mlx.core as mx
  return {'default_device':str(mx.default_device()),'active_bytes':int(mx.get_active_memory()),'peak_bytes':int(mx.get_peak_memory())}
 except Exception as exc:return {'unavailable':type(exc).__name__}
from main import app
class ResearchEvidence:
 def __init__(self,app):self.app=app
 async def __call__(self,scope,receive,send):
  global record
  if scope['type']!='http' or scope.get('path') not in ('/generate','/v1/audio/speech'):return await self.app(scope,receive,send)
  # Calls in this study are serialized. Evidence is not a kernel-level GPU trace.
  started=time.monotonic();entry={'started_unix':time.time(),'path':scope['path'],'torch_forward_calls':0,'torch_devices':[],'rss_before':psutil.Process().memory_info().rss,'mlx_before':mlx_stats(),'response_bytes':0,'status':None}
  record=entry
  async def observed_send(message):
   if message['type']=='http.response.start':entry['status']=message['status']
   if message['type']=='http.response.body':entry['response_bytes']+=len(message.get('body',b''))
   await send(message)
  try:await self.app(scope,receive,observed_send)
  finally:
   entry.update(elapsed_seconds=time.monotonic()-started,rss_after=psutil.Process().memory_info().rss,mlx_after=mlx_stats());record=None
   with guard:
    with TRACE.open('a') as f:f.write(json.dumps(entry)+'\n')
app.add_middleware(ResearchEvidence)
if __name__=='__main__':
 import uvicorn
 uvicorn.run(app,host='127.0.0.1',port=int(os.environ['OMNIVOICE_PORT']),log_level='info')
