"""Loopback-only audition workspace; narrowly scoped bridge to existing studio."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json,re
import batch_queue
import threading,time
TRASH_FILE=Path(__file__).resolve().parents[2]/'services/speaker-studio/.runtime/santa-trash.json'
PURGED_FILE=TRASH_FILE.with_name('santa-removed.json')
TRASH_LOCK=threading.RLock()
ROOT=Path(__file__).resolve().parent
HOST='127.0.0.1:5198'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def end_headers(self):
  self.send_header('Cross-Origin-Opener-Policy','same-origin');self.send_header('Cross-Origin-Embedder-Policy','require-corp');self.send_header('Permissions-Policy','cross-origin-isolated=(self "http://127.0.0.1:5201")');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');super().end_headers()
 def reply(self,status,data,kind='application/json'):
  body=json.dumps(data).encode() if kind=='application/json' else data
  self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def bridge(self,body=None):
  path=urlsplit(self.path).path
  if path=='/acting-reference':
   from urllib.parse import parse_qs,quote
   args=parse_qs(urlsplit(self.path).query);style=args.get('style',[''])[0];ident=args.get('reference_id',[''])[0]
   emotion={'anger':'anger','joy':'happiness','sadness':'sadness'}.get(style)
   try:
    catalog=batch_queue.upstream('/api/designer/acting-references')
    ref=next((r for r in catalog['references'] if r['id']==ident and r['emotion']==emotion),None)
    if not ref:return self.reply(404,{'error':'Choose a sample matching the selected emotion'})
    with urlopen('http://127.0.0.1:5197/character-reference?reference_id='+quote(ident,safe=''),timeout=10) as response:return self.reply(200,response.read(),'audio/wav')
   except (ValueError,HTTPError,URLError):return self.reply(404,{'error':'Acting reference unavailable'})
  allowed={'/api/designer/state','/api/designer/direct-emotions','/api/designer/emotion-checkpoints','/api/designer/acting-references','/api/designer/passport','/api/designer/passport-media','/designer-media'} if body is None else {'/api/designer/run','/api/designer/profile','/api/designer/emotion-checkpoints','/api/designer/emotion-checkpoint-action','/api/designer/direct-emotions','/api/designer/direct-emotion-action'}
  if path not in allowed:return self.reply(404,{'error':'Not found'})
  try:
   req=Request('http://127.0.0.1:5197'+self.path,data=body,headers={'Content-Type':'application/json','Origin':'http://127.0.0.1:5197'})
   with urlopen(req,timeout=20) as response:return self.reply(response.status,response.read(),response.headers.get('Content-Type','application/octet-stream').replace('application/json','application/json; charset=utf-8'))
  except HTTPError as error:return self.reply(error.code,error.read(),'application/json; charset=utf-8')
  except (URLError,TimeoutError):return self.reply(503,{'error':'Local voice studio is unavailable. Earlier recordings remain saved.'})
 def do_GET(self):
  if self.headers.get('Host')!=HOST:return self.reply(403,{'error':'Local host required'})
  path=urlsplit(self.path).path
  if path=='/api/audition/batch':
   from urllib.parse import parse_qs
   try:return self.reply(200,batch_queue.load(parse_qs(urlsplit(self.path).query).get('id',[''])[0]))
   except (ValueError,FileNotFoundError):return self.reply(404,{'error':'Unknown batch'})
  if path=='/api/designer/state':
   try:
    data=batch_queue.upstream(path)
    with TRASH_LOCK:
     data['trashed_ids']=list(json.loads(TRASH_FILE.read_text()) if TRASH_FILE.exists() else {})
     removed=set(json.loads(PURGED_FILE.read_text()) if PURGED_FILE.exists() else [])
     data['auditions']=[r for r in data['auditions'] if r['id'] not in removed]
    return self.reply(200,data)
   except Exception:return self.reply(503,{'error':'Local voice studio is unavailable'})
  if path.startswith('/api/') or path in ('/designer-media','/acting-reference'):return self.bridge()
  allowed={'/001-santa-audition/','/001-santa-audition/index.html','/001-santa-audition/live.js','/001-santa-audition/passport.js','/001-santa-audition/checkpoints.js','/001-santa-audition/direct-emotions.js','/001-santa-audition/ui-consistency.js','/001-santa-audition/anger-pipeline.js','/themes/default.css','/themes/geist-400.woff2'}
  if path not in allowed:return self.reply(404,{'error':'Not found'})
  super().do_GET()
 def do_POST(self):
  if self.headers.get('Host')!=HOST or self.headers.get('Origin')!='http://'+HOST:return self.reply(403,{'error':'Same-origin workspace required'})
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=16000:return self.reply(413,{'error':'Request too large'})
   body=self.rfile.read(size);json.loads(body)
  except (ValueError,json.JSONDecodeError):return self.reply(400,{'error':'Invalid request'})
  path=urlsplit(self.path).path
  if path=='/api/designer/run':
   words=re.findall(r"[^\W_]+(?:['’][^\W_]+)*",str(json.loads(body).get('text','')))
   if len(words)>35:return self.reply(400,{'error':f'Use no more than 35 words; this input has {len(words)}.'})
  try:
   if path=='/api/audition/emotion':
    q=json.loads(body);text=str(q.get('text','')).strip().replace('..','…')
    if q.get('target_style') not in ('anger','joy','sadness'):raise ValueError('Choose Anger, Joy or Sadness. Warm reassurance needs its own acting reference first.')
    if len(re.findall(r"[^\W_]+(?:['’][^\W_]+)*",text))>35:raise ValueError('Use no more than 35 words per comparison')
    refs=batch_queue.upstream('/api/designer/acting-references')['references']
    emotion={'anger':'anger','joy':'happiness','sadness':'sadness'}[q['target_style']]
    if not any(r['id']==q.get('reference_id') and r['emotion']==emotion for r in refs):raise ValueError('Choose an acting sample for this emotion')
    state=batch_queue.upstream('/api/designer/state')
    if state['busy']:raise ValueError('Another studio generation is running; wait until it finishes')
    source=next((r for r in state['auditions'] if r['id']==q.get('source') and r['state']=='saved'),None)
    if not source:raise ValueError('Choose a saved voice candidate')
    profile=batch_queue.upstream('/api/designer/profile',{'audition_id':source['id'],'name':'Santa emotion reference · '+source['id'][:8]})
    settings=source['request']
    return self.reply(202,batch_queue.start({'token':q.get('token'),'count':2,'seed_mode':'fixed','seed':settings['seed'],'increment':1,'recipe':{'profile_id':profile['id'],'text':text,'steps':settings['steps'],'guidance':settings['guidance'],'performance_direction':q.get('direction',''),'target_style':q['target_style'],'reference_id':q['reference_id']}}))
   if path=='/api/audition/batch':return self.reply(202,batch_queue.start(json.loads(body)))
   if path=='/api/audition/stop':return self.reply(200,batch_queue.stop(json.loads(body).get('id','')))
   if path=='/api/audition/empty-trash':
    q=json.loads(body)
    ids=q.get('ids',[])
    if not isinstance(ids,list) or not ids or len(ids)>500:raise ValueError('Choose trashed takes to remove')
    ids=[str(__import__('uuid').UUID(v)) for v in ids]
    with TRASH_LOCK:
     trash=json.loads(TRASH_FILE.read_text()) if TRASH_FILE.exists() else {}
     if any(v not in trash for v in ids):raise ValueError('Only trashed takes can be removed')
     removed=set(json.loads(PURGED_FILE.read_text()) if PURGED_FILE.exists() else [])
     removed.update(ids)
     tmp=PURGED_FILE.with_suffix('.tmp');tmp.write_text(json.dumps(sorted(removed)));tmp.replace(PURGED_FILE)
     for v in ids:trash.pop(v,None)
     tmp=TRASH_FILE.with_suffix('.tmp');tmp.write_text(json.dumps(trash));tmp.replace(TRASH_FILE)
    return self.reply(200,{'removed_ids':ids})
   if path=='/api/audition/trash':
    q=json.loads(body);value=str(__import__('uuid').UUID(q.get('id','')))
    if q.get('deleted') is not True and q.get('deleted') is not False:raise ValueError('Choose delete or restore')
    record=next((r for r in batch_queue.upstream('/api/designer/state')['auditions'] if r['id']==value),None)
    if not record or record['state'] not in ('saved','failed'):raise ValueError('Only completed auditions can be removed')
    with TRASH_LOCK:
     trash=json.loads(TRASH_FILE.read_text()) if TRASH_FILE.exists() else {}
     if q['deleted']:trash[value]=time.time()
     else:trash.pop(value,None)
     tmp=TRASH_FILE.with_suffix('.tmp');tmp.write_text(json.dumps(trash));tmp.replace(TRASH_FILE)
    return self.reply(200,{'id':value,'deleted':q['deleted']})
  except (ValueError,FileNotFoundError) as e:return self.reply(400,{'error':str(e)})
  self.bridge(body)
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',5198),Handler).serve_forever()
