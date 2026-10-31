"""Local, immutable self-recording library and optional VoiceStudio profile export."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import base64,hashlib,io,json,os,secrets,subprocess,threading,time,uuid,wave,zipfile
from urllib.parse import urlparse,parse_qs
import scene
import voice_designer
import character_workflow as characters
import performance_bridge
import sentence_policy
ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('SPEAKER_STUDIO_DATA',str(ROOT/'.runtime')));DATA.mkdir(exist_ok=True,parents=True)
HOST='127.0.0.1:5197';ORIGIN='http://'+HOST;LOCK=threading.RLock()
FFMPEG='/Users/x/.local/share/money/f5-tts/venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
LESSONS=[
 {'id':'neutral','name':'Neutral','direction':'Speak naturally, as if explaining something to a friend. No added emotion.','text':'Let me explain what happened. I arrived a little early, opened the door, and put the package on the table. Then I waited for you.'},
 {'id':'reassurance','name':'Warm reassurance','direction':'Someone you care about is frightened. Slow down, soften the edges, and make them feel supported.','text':'You do not have to figure everything out right now. Take a breath. I am here with you, and we can work through this together.'},
 {'id':'anger','name':'Controlled anger','direction':'You have been let down repeatedly. Be firm and restrained, not loud for its own sake.','text':'I asked you to tell me before changing the plan. You knew how much this mattered. I need you to understand why I cannot accept this.'},
 {'id':'happiness','name':'Joy','direction':'Good news has just arrived. Let genuine delight rise through the sentence.','text':'We did it. After all those attempts, it finally worked. I cannot wait to tell everyone. This is the moment we have been waiting for.'},
 {'id':'sadness','name':'Quiet sadness','direction':'Something meaningful has ended. Keep it intimate; leave room for pauses.','text':'I thought we would have more time. The room feels different without you here. I keep finding little things I wanted to tell you.'},
 {'id':'surprise','name':'Surprised discovery','direction':'You discover something unexpected and gradually realise its importance.','text':'Wait a second. That was here the whole time? I walked past it every day and never noticed. This changes everything.'},
 {'id':'curiosity','name':'Curiosity','direction':'You are sincerely intrigued. Ask to understand, rather than sounding suspicious.','text':'How did you find that out? I would love to know what made you look there. Can you walk me through the part I am missing?'},
 {'id':'frustration','name':'Restrained frustration','direction':'A small problem keeps returning. Let the irritation show without becoming shouting.','text':'It happened again. I checked every setting, started over, and followed the instructions. Somehow we are right back where we began.'},
]
def read_profile(ident):
 if not ident or any(c not in '0123456789abcdef-' for c in ident):raise ValueError('Invalid profile')
 return json.loads((DATA/ident/'profile.json').read_text())
def save(p):
 folder=DATA/p['id'];folder.mkdir(exist_ok=True);tmp=folder/'profile.tmp';tmp.write_text(json.dumps(p,indent=2));tmp.replace(folder/'profile.json')
def public(p):
 return {**p,'clips':[{**r,'url':f"/media/{p['id']}/{r['id']}.wav"} for r in p['clips']]}
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def reply(self,code,data,kind='application/json'):
  b=json.dumps(data).encode() if kind=='application/json' else data
  self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(b)
 def allowed(self,write=False):
  if self.headers.get('Host')!=HOST:return False
  return not write or self.headers.get('Origin')==ORIGIN or (self.headers.get('Origin') is None and self.headers.get('X-Studio-Client')=='local-test')
 def do_GET(self):
  if not self.allowed():return self.reply(403,{'error':'Local host required'})
  path=urlparse(self.path).path
  try:
   if path=='/api/designer/direct-emotions':
    import direct_emotions
    return self.reply(200,direct_emotions.listing())
   if path=='/api/designer/emotion-checkpoints':
    import emotion_checkpoints
    return self.reply(200,emotion_checkpoints.listing())
   if path=='/api/designer/passport':
    import asset_passport
    args=parse_qs(urlparse(self.path).query);return self.reply(200,asset_passport.get(args.get('id',[''])[0]))
   if path=='/api/designer/passport-media':
    import asset_passport
    args=parse_qs(urlparse(self.path).query);return self.reply(200,asset_passport.reference_media(args.get('id',[''])[0],args.get('node',[''])[0]),'audio/wav')
   if path=='/api/designer/acting-references':
    import acted_conversion
    return self.reply(200,acted_conversion.references())
   if path=='/api/scene/manifest':
    args=parse_qs(urlparse(self.path).query);return self.reply(200,scene.get(args['id'][0]))
   if path=='/api/scene/config':return self.reply(200,scene.config())
   if path=='/character-reference':
    args=parse_qs(urlparse(self.path).query);ref=performance_bridge.catalog().get(args.get('reference_id',[''])[0])
    if not ref or scene.digest(ref['path'])!=ref['sha256']:raise ValueError('Emotion reference unavailable')
    return self.reply(200,Path(ref['path']).read_bytes(),'audio/wav')
   if path=='/api/characters':return self.reply(200,characters.state())
   if path=='/api/character':
    args=parse_qs(urlparse(self.path).query);return self.reply(200,characters.public(characters.load(args.get('id',[''])[0])))
   if path=='/character-export':
    args=parse_qs(urlparse(self.path).query);return self.reply(200,characters.export(args.get('id',[''])[0]),'application/zip')
   if path=='/api/designer/state':return self.reply(200,voice_designer.listing())
   if path=='/api/designer/profile':
    args=parse_qs(urlparse(self.path).query);return self.reply(200,voice_designer.profile(args.get('id',[''])[0]))
   if path=='/designer-media':
    args=parse_qs(urlparse(self.path).query);return self.reply(200,voice_designer.media(args.get('id',[''])[0],args.get('original',['0'])[0]=='1').read_bytes(),'audio/wav')
   if path=='/api/scene/experiments':return self.reply(200,scene.experiments())
   if path=='/reference-media':
    args={k:v[0] for k,v in parse_qs(urlparse(self.path).query).items()};return self.reply(200,scene.reference_preview(**args).read_bytes(),'audio/wav')
   if path=='/compare-media':
    args={k:v[0] for k,v in parse_qs(urlparse(self.path).query).items()};return self.reply(200,scene.comparison_media(**args).read_bytes(),'audio/wav')
   if path=='/scene-media':
    args={k:v[0] for k,v in parse_qs(urlparse(self.path).query).items()};return self.reply(200,scene.media(**args).read_bytes(),'audio/wav')
   if path.startswith('/character-ui/'):
    name=path.removeprefix('/character-ui/')
    allowed={'characters.css':'text/css; charset=utf-8','characters.js':'text/javascript; charset=utf-8','geist-400.woff2':'font/woff2','geist-500.woff2':'font/woff2','geist-600.woff2':'font/woff2'}
    if name not in allowed:return self.reply(404,{'error':'Not found'})
    return self.reply(200,(ROOT/'character-ui'/name).read_bytes(),allowed[name])
   if path=='/characters':return self.reply(200,(ROOT/'characters.html').read_bytes(),'text/html; charset=utf-8')
   if path=='/record':return self.reply(200,(ROOT/'record.html').read_bytes(),'text/html; charset=utf-8')
   if path=='/design/auditions':return self.reply(200,(ROOT/'design.html').read_bytes(),'text/html; charset=utf-8')
   if path=='/design':return self.reply(200,(ROOT/'wizard.html').read_bytes(),'text/html; charset=utf-8')
   if path=='/':return self.reply(200,(ROOT/'index.html').read_bytes(),'text/html; charset=utf-8')
   if path=='/api/library':return self.reply(200,{'lessons':LESSONS,'profiles':[public(json.loads(p.read_text())) for p in sorted(DATA.glob('*/profile.json'))]})
   if path.startswith('/media/'):
    _,_,ident,name=path.split('/');p=read_profile(ident)
    if not any(name==r['id']+'.wav' for r in p['clips']):raise ValueError('Unknown clip')
    return self.reply(200,(DATA/ident/name).read_bytes(),'audio/wav')
   if path.startswith('/export/'):
    p=read_profile(path.split('/')[-1]);buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
     z.writestr('profile.json',json.dumps(p,indent=2));z.writestr('recording-plan.json',json.dumps(LESSONS,indent=2))
     for r in p['clips']:
      for name in [r['id']+'.wav',r['id']+'.original']:z.write(DATA/p['id']/name,name)
    return self.reply(200,buf.getvalue(),'application/zip')
   return self.reply(404,{'error':'Not found'})
  except (ValueError,FileNotFoundError):return self.reply(404,{'error':'Recording not found'})
 def do_POST(self):
  if not self.allowed(True):return self.reply(403,{'error':'Same-origin recording workspace required'})
  try:
   size=int(self.headers.get('Content-Length','0'))
   if size<=0 or size>30000000:raise ValueError('Upload must be smaller than 30 MB')
   q=json.loads(self.rfile.read(size));path=urlparse(self.path).path
   with LOCK:
    if path=='/api/character/sentence-check':return self.reply(200,sentence_policy.inspect(q.get('text','')))
    if path=='/api/characters':return self.reply(201,characters.create(q))
    if path=='/api/character/action':return self.reply(200,characters.mutate(q))
    if path=='/api/character/loop':
     import guided_loop
     return self.reply(202,guided_loop.command(q))
    if path=='/api/character/generate':return self.reply(202,characters.generate(q))
    if path=='/api/character/publish':return self.reply(201,characters.package(q))
    if path=='/api/designer/direct-emotions':
     import direct_emotions
     return self.reply(201,direct_emotions.promote(q))
    if path=='/api/designer/direct-emotion-action':
     import direct_emotions
     return self.reply(200,direct_emotions.command(q))
    if path=='/api/designer/emotion-checkpoints':
     import emotion_checkpoints
     return self.reply(201,emotion_checkpoints.create(q))
    if path=='/api/designer/emotion-checkpoint-action':
     import emotion_checkpoints
     return self.reply(200,emotion_checkpoints.command(q))
    if path=='/api/designer/convert-performance':
     import acted_conversion
     return self.reply(202,acted_conversion.start(q))
    if path=='/api/designer/run':return self.reply(202,voice_designer.start(q))
    if path=='/api/designer/profile':return self.reply(201,voice_designer.save_profile(q))
    if path=='/api/scene/compare':return self.reply(201,scene.compare(q))
    if path=='/api/scene/compare-assessment':return self.reply(200,scene.assess_compare(q))
    if path=='/api/scene/run':return self.reply(202,scene.start(q))
    if path=='/api/scene/ratings':return self.reply(200,scene.ratings(q))
    if path=='/api/profile':
     name=str(q.get('name','')).strip()[:100]
     if not name:raise ValueError('Enter a speaker name')
     p={'id':str(uuid.uuid4()),'name':name,'created':time.time(),'source':'self_recorded','schema_version':1,'status':'draft','clips':[],'accepted':{},'transformations':[]};save(p);return self.reply(201,public(p))
    p=read_profile(q['profile_id'])
    if path=='/api/clip':
     lesson=next((x for x in LESSONS if x['id']==q['emotion']),None)
     if not lesson:raise ValueError('Unknown recording step')
     if q.get('transcript')!=lesson['text']:raise ValueError('Script changed; use the displayed recording script')
     intensity=float(q['intensity'])
     if not 0<=intensity<=1:raise ValueError('Intensity is outside range')
     raw=base64.b64decode(q['audio'],validate=True)
     if not 100<len(raw)<=20000000:raise ValueError('Recording is empty or too large')
     ident=str(uuid.uuid4());folder=DATA/p['id'];source=folder/(ident+'.original');target=folder/(ident+'.wav');source.write_bytes(raw)
     try:
      subprocess.run([FFMPEG,'-v','error','-nostdin','-i',str(source),'-t','120','-ac','1','-ar','24000','-c:a','pcm_s16le',str(target)],check=True,capture_output=True,timeout=30)
      with wave.open(str(target)) as w:frames=w.readframes(w.getnframes());duration=w.getnframes()/w.getframerate()
      import array,math
      samples=array.array('h',frames);peak=max(abs(x) for x in samples)/32768;rms=math.sqrt(sum((x/32768)**2 for x in samples)/len(samples))
      if duration<1 or rms<.0001:raise ValueError('Recording is too short or silent. Please record again.')
     except Exception as e:raise ValueError('Recording could not be read or was silent. Please try again.') from e
     r={'id':ident,'emotion':lesson['id'],'direction':lesson['direction'],'transcript':{'text':lesson['text'],'status':'scripted_not_verified'},'self_rated_intensity':intensity,'notes':str(q.get('notes',''))[:2000],'created':time.time(),'source_mime':str(q.get('mime',''))[:100],'source_sha256':hashlib.sha256(raw).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'duration_seconds':duration,'sample_rate':24000,'peak':peak,'rms':rms,'clipped_samples':sum(abs(x)>=32760 for x in samples),'review_status':'unreviewed'}
     p['clips'].append(r);p['status']='draft';save(p);return self.reply(201,public(p))
    if path=='/api/keep':
     r=next((x for x in p['clips'] if x['id']==q['clip_id']),None)
     if not r:raise ValueError('Unknown take')
     if not q.get('words_checked') or not q.get('performance_checked'):raise ValueError('Listen and confirm wording and performance before keeping this take')
     r['review_status']='self_reviewed';r['reviewed_at']=time.time();p['accepted'][r['emotion']]=r['id'];save(p);return self.reply(200,public(p))
    if path=='/api/finish':
     if any(l['id'] not in p['accepted'] for l in LESSONS):raise ValueError('Keep one reviewed take for every step before finishing')
     p['status']='self_reviewed_library';p['completed']=time.time();save(p);return self.reply(200,public(p))
    if path=='/api/voicestudio':
     # Each native VoiceStudio profile has one reference. Export only on explicit request.
     r=next((x for x in p['clips'] if x['id']==q['clip_id'] and x['review_status']=='self_reviewed'),None)
     if not r:raise ValueError('Keep and review the take first')
     if r.get('voicestudio_profile_id'):return self.reply(200,{'profile_id':r['voicestudio_profile_id'],'existing':True})
     import urllib.request
     boundary='Studio'+secrets.token_hex(16);chunks=[]
     for k,v in {'name':p['name']+' — '+r['emotion'],'ref_text':r['transcript']['text'],'kind':'clone','language':'English'}.items():chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
     chunks.extend([f'--{boundary}\r\nContent-Disposition: form-data; name="ref_audio"; filename="reference.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode(),(DATA/p['id']/(r['id']+'.wav')).read_bytes(),f'\r\n--{boundary}--\r\n'.encode()])
     req=urllib.request.Request('http://127.0.0.1:5196/profiles',data=b''.join(chunks),headers={'Content-Type':'multipart/form-data; boundary='+boundary})
     try:
      with urllib.request.urlopen(req,timeout=90) as resp:created=json.load(resp)
     except Exception as e:raise ValueError('VoiceStudio profile export is unavailable. Your local library is safe.') from e
     r['voicestudio_profile_id']=created['id'];save(p);return self.reply(200,{'profile_id':created['id']})
   return self.reply(404,{'error':'Not found'})
  except (ValueError,KeyError,FileNotFoundError) as e:return self.reply(400,{'error':str(e)})
  except Exception:return self.reply(500,{'error':'Could not save. Existing recordings are preserved.'})
if __name__=='__main__':
 server=ThreadingHTTPServer(('127.0.0.1',5197),Handler)
 characters.recover()
 import emotion_checkpoints
 emotion_checkpoints.recover()
 import direct_emotions
 direct_emotions.recover()
 print('Speaker recording studio: '+ORIGIN,flush=True)
 server.serve_forever()
