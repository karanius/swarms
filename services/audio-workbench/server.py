"""Loopback audio engine service; the React Flow graph is compiled, not eval'd."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from http.cookies import SimpleCookie
import base64,shutil
import json,secrets,subprocess,threading,os,signal,re,time,hashlib
from urllib.parse import unquote
from contracts import compile_graph
ROOT=Path(__file__).resolve().parent;RUNTIME=ROOT/'.runtime';RUNTIME.mkdir(exist_ok=True)
PY=Path('/Users/x/.local/share/money/f5-tts/venv/bin/python');ORIGIN='http://127.0.0.1:5194';HOST='127.0.0.1:5195'
raw=subprocess.check_output([str(PY),'-B',str(ROOT/'worker.py'),'catalog'],text=True);CATALOG=json.loads(next(x[8:] for x in raw.splitlines() if x.startswith('CATALOG=')));PRESETS={x['id'] for x in CATALOG['presets']};SESSIONS={};JOBS={};LOCK=threading.Lock()
def snapshot(job):
 folder=job['folder'];proc=job['process'];events=[]
 if (folder/'events.jsonl').exists():
  for line in (folder/'events.jsonl').read_text().splitlines():
   try:events.append(json.loads(line))
   except ValueError:pass
 result=json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else None
 status='cancelled' if (folder/'cancelled.json').exists() else ('running' if proc.poll() is None else (result or {}).get('status','failed'))
 outputs=json.loads((folder/'outputs.json').read_text()) if (folder/'outputs.json').exists() else {}
 public={}
 for ident,value in outputs.items():
  if ident=='text':continue
  public[ident]={'report':value['report'],'files':{k:f'/engine/media/{job["id"]}/{ident}/{k}' for k in ('audio','before','after','comparison','original') if value.get(k)}}
 return {'id':job['id'],'status':status,'events':events,'outputs':public,'error':(result or {}).get('error') if status=='failed' else None,'graph':job['graph']}
class Handler(BaseHTTPRequestHandler):
 def reply(self,status,data,cookie=None):
  b=json.dumps(data).encode();self.send_response(status)
  for k,v in {'Content-Type':'application/json','Content-Length':str(len(b)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}.items():self.send_header(k,v)
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers();self.wfile.write(b)
 def session(self):
  c=SimpleCookie(self.headers.get('Cookie',''));v=c.get('audio_workbench');return SESSIONS.get(v.value if v else '')
 def do_GET(self):
  if self.headers.get('Host')!=HOST:return self.reply(403,{'error':'Invalid local host'})
  if self.path=='/session':
   session=self.session();token=None
   if session is None:
    if len(SESSIONS)>100:return self.reply(503,{'error':'Session capacity reached'})
    token=secrets.token_urlsafe(32);session={'jobs':[],'uploads':{},'defaults':None};SESSIONS[token]=session
   return self.reply(200,{'catalog':{**CATALOG,'presets':[{k:v for k,v in p.items() if k in ('id','label','transcript')} for p in CATALOG['presets']]},'uploads':[{k:v for k,v in u.items() if k!='path'} for u in session['uploads'].values()],'defaults':session['defaults'],'sources':{kind:next((j for j in reversed(session['jobs']) if kind in snapshot(JOBS[j])['outputs']),None) for kind in ('voice','master')},'latest':session['jobs'][-1] if session['jobs'] else None},cookie=f'audio_workbench={token}; HttpOnly; SameSite=Strict; Path=/' if token else None)
  session=self.session()
  if session is None:return self.reply(401,{'error':'Reload the workbench to reconnect'})
  if self.path.startswith('/reference/'):
   ident=unquote(self.path[len('/reference/'):]);entry=session['uploads'].get(ident) or next((p for p in CATALOG['presets'] if p['id']==ident),None)
   if not entry:return self.reply(404,{'error':'Prepared reference not found'})
   file=Path(entry['path'])
   if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=entry['sha256']:return self.reply(409,{'error':'Prepared reference integrity check failed'})
   data=file.read_bytes();self.send_response(200);self.send_header('Content-Type','audio/wav');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','private, no-store');self.end_headers();self.wfile.write(data);return
  m=re.fullmatch(r'/state/([a-f0-9]{24})',self.path)
  if m:
   if m[1] not in session['jobs']:return self.reply(404,{'error':'Run not found'})
   return self.reply(200,snapshot(JOBS[m[1]]))
  m=re.fullmatch(r'/media/([a-f0-9]{24})/(voice|master|enhance)/(audio|before|after|comparison|original)',self.path)
  if m:
   if m[1] not in session['jobs']:return self.reply(404,{'error':'Audio not found'})
   job=JOBS[m[1]];p=job['folder']/'outputs.json'
   try:file=Path(json.loads(p.read_text())[m[2]][m[3]]).resolve()
   except (KeyError,OSError,ValueError):return self.reply(404,{'error':'Audio is not ready'})
   if not file.is_relative_to(job['folder']) or not file.is_file():return self.reply(404,{'error':'Audio not found'})
   data=file.read_bytes();start,end=0,len(data)-1;partial=False
   r=self.headers.get('Range')
   if r:
    match=re.fullmatch(r'bytes=(\d+)-(\d*)',r)
    if not match:return self.reply(416,{'error':'Unsupported byte range'})
    start=int(match[1]);end=min(int(match[2]) if match[2] else end,end);partial=True
    if start>end:return self.reply(416,{'error':'Range outside file'})
   self.send_response(206 if partial else 200);self.send_header('Content-Type','audio/wav');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1));self.send_header('Cache-Control','private, no-store')
   if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{len(data)}')
   self.end_headers();self.wfile.write(data[start:end+1]);return
  return self.reply(404,{'error':'Not found'})
 def do_POST(self):
  if self.headers.get('Host')!=HOST or self.headers.get('Origin')!=ORIGIN:return self.reply(403,{'error':'Use the local audio workbench'})
  session=self.session()
  if session is None:return self.reply(401,{'error':'Reload to reconnect'})
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=(30_000_000 if self.path=='/upload' else 30000) or not self.headers.get('Content-Type','').startswith('application/json'):raise ValueError('Invalid JSON request')
   data=json.loads(self.rfile.read(length))
   if self.path=='/upload':
    if len(session['uploads'])>=30:raise ValueError('Upload limit reached for this session')
    content=base64.b64decode(data['audio'],validate=True)
    if not 44<=len(content)<=20_000_000:raise ValueError('Use an audio file under 20 MB')
    token='upload:'+secrets.token_hex(12);folder=RUNTIME/'uploads';folder.mkdir(exist_ok=True);file=folder/(token[7:]+'.wav');file.write_bytes(content)
    try:
     result=subprocess.run([str(PY),'-B',str(ROOT/'worker.py'),'inspect',str(file)],capture_output=True,text=True,timeout=30)
     if result.returncode:raise ValueError('Use 1–600 seconds of valid audible audio; WAV, FLAC or supported sound files')
     info=json.loads(result.stdout)
    except Exception:
     file.unlink(missing_ok=True);raise
    entry={'id':token,'label':str(data.get('name','Uploaded recording'))[:120],'path':str(file),'sha256':hashlib.sha256(content).hexdigest(),**info};session['uploads'][token]=entry
    return self.reply(201,{k:v for k,v in entry.items() if k!='path'})
   presets=PRESETS|set(session['uploads'])
   if self.path=='/defaults':
    compile_graph(data,presets);session['defaults']=data;return self.reply(200,{'saved':True})
   if self.path=='/validate':return self.reply(200,{'valid':True,'compiled':compile_graph(data,presets)})
   if self.path=='/run':
    graph=compile_graph(data,presets)
    start=data.get('start_at');stop=data.get('stop_after');input_audio=None
    if stop is not None and stop not in {n['id'] for n in graph['ordered']}:raise ValueError('Invalid ending stage')
    if start and stop and ['text','voice','master','enhance'].index(start)>['text','voice','master','enhance'].index(stop):raise ValueError('Ending stage precedes starting stage')
    if start:
     if start not in ('master','enhance') or start not in {n['id'] for n in graph['ordered']}:raise ValueError('Invalid starting stage')
     source=data.get('source',{})
     if source.get('upload') in session['uploads'] and start=='master':input_audio=Path(session['uploads'][source['upload']]['path'])
     elif source.get('job') in session['jobs']:
      prior=JOBS[source['job']];stage='voice' if start=='master' else 'master'
      try:input_audio=Path(json.loads((prior['folder']/'outputs.json').read_text())[stage]['audio']).resolve()
      except (OSError,KeyError):raise ValueError('Complete the required source stage first')
      if not input_audio.is_relative_to(prior['folder']):raise ValueError('Invalid source artifact')
     else:raise ValueError('Select an uploaded recording or a completed source stage')
    reference=next(n for n in graph['ordered'] if n['type']=='voice')['config']['reference']
    ref=session['uploads'].get(reference)
    if ref and ref['seconds']>30:raise ValueError('Use a custom voice reference under 30 seconds')
    with LOCK:
     if any(j['process'].poll() is None for j in JOBS.values()):return self.reply(409,{'error':'An audio graph is already running. Wait or stop your run.'})
     ident=secrets.token_hex(12);folder=(RUNTIME/ident).resolve();folder.mkdir();worker_graph=dict(graph)
     if stop:worker_graph['ordered']=graph['ordered'][:next(i+1 for i,n in enumerate(graph['ordered']) if n['id']==stop)]
     if start:
      target=folder/'input.wav';shutil.copyfile(input_audio,target);worker_graph.update(start_at=start,input_audio=str(target))
     if ref:worker_graph['reference_audio']=ref['path']
     (folder/'request.json').write_text(json.dumps(worker_graph,indent=2));log=(folder/'worker.log').open('w')
     (folder/'worker.snapshot.py').write_bytes((ROOT/'worker.py').read_bytes())
     process=subprocess.Popen([str(PY),'-B',str(folder/'worker.snapshot.py'),str(folder)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();JOBS[ident]={'id':ident,'folder':folder,'process':process,'graph':graph};session['jobs'].append(ident)
    return self.reply(202,{'id':ident})
   if self.path=='/cancel':
    ident=data.get('id')
    if ident not in session['jobs']:raise ValueError('Run not found')
    job=JOBS[ident]
    if job['process'].poll() is None:os.killpg(job['process'].pid,signal.SIGTERM);(job['folder']/'cancelled.json').write_text('{}')
    return self.reply(200,snapshot(job))
   return self.reply(404,{'error':'Not found'})
  except (ValueError,TypeError,KeyError) as exc:return self.reply(400,{'error':str(exc)})
  except Exception:return self.reply(500,{'error':'The local audio service could not complete this request; inspect the retained run log.'})
if __name__=='__main__':print('Audio engine service listening on loopback',flush=True);ThreadingHTTPServer(('127.0.0.1',5195),Handler).serve_forever()
