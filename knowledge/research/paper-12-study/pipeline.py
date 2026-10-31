"""Local illustrated-video implementation of a Paper 11 capability contract.
No downloaded Langflow component is imported or represented as executed.
"""
from pathlib import Path
import json,hashlib,subprocess,time,wave,sys,urllib.request,re,math,os
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent
F5_PY=Path('/Users/x/.local/share/money/f5-tts/venv/bin/python')
FF=Path('/Users/x/projects/money/runtimes/daily-video/.venv/lib/python3.14/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1')
FONT='/System/Library/Fonts/Supplemental/Arial.ttf';BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
W,H,FPS=1280,720,24

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def command(args,timeout=180):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError('Local command failed: '+p.stderr[-2000:])
 return p

def validate_plan(plan):
 if not isinstance(plan,dict) or set(plan)!={'title','scenes'}:raise ValueError('Expected title and scenes only')
 if not isinstance(plan['title'],str) or not 1<=len(plan['title'])<=70:raise ValueError('Invalid title')
 if not isinstance(plan['scenes'],list) or len(plan['scenes'])!=2:raise ValueError('Exactly two scenes are required')
 for s in plan['scenes']:
  if not isinstance(s,dict) or set(s)!={'headline','narration','steps'}:raise ValueError('Invalid scene fields')
  if not isinstance(s['headline'],str) or not 1<=len(s['headline'])<=55:raise ValueError('Invalid headline')
  if not isinstance(s['narration'],str) or not 5<=len(s['narration'].split())<=28:raise ValueError('Narration must be 5–28 words')
  if not isinstance(s['steps'],list) or len(s['steps'])!=3 or any(not isinstance(x,str) or not 1<=len(x)<=32 for x in s['steps']):raise ValueError('Exactly three short diagram labels required')
 return plan

def plan_local(brief,folder):
 if not isinstance(brief,str) or not 10<=len(brief)<=1000:raise ValueError('Brief must contain 10–1000 characters')
 prompt='Create a two-scene English educational diagram video plan. Output JSON only with title (max 70 characters) and scenes (exactly two). Each scene has headline (max 55 characters), narration (5 to 28 words), steps (exactly three short labels, each max 32 characters). Do not assert statistics, real-world product capabilities or financial outcomes. Describe the supplied process. Brief: '+brief
 body={'model':'llama3.2:3b','stream':False,'format':'json','keep_alive':0,'prompt':prompt,'options':{'temperature':0,'seed':42,'num_predict':650}}
 req=urllib.request.Request('http://127.0.0.1:11434/api/generate',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 started=time.monotonic();response=json.loads(urllib.request.urlopen(req,timeout=150).read());(folder/'model-response.json').write_text(json.dumps(response,indent=2))
 plan=validate_plan(json.loads(response['response']));(folder/'plan.json').write_text(json.dumps(plan,indent=2))
 return plan,{'endpoint':'loopback Ollama','model':response['model'],'eval_count':response.get('eval_count'),'seconds':time.monotonic()-started,'mode':'JSON scene specification; raster image rendered from generated labels. No diffusion or motion model.'}

def wrapped(draw,text,font,max_width):
 lines=[];line=''
 for word in text.split():
  trial=(line+' '+word).strip()
  if draw.textbbox((0,0),trial,font=font)[2]>max_width:
   if not line:raise ValueError('An individual word exceeds the safe image width')
   lines.append(line);line=word
  else:line=trial
 if line:lines.append(line)
 return lines

def draw_scene(scene,index,path):
 im=Image.new('RGB',(W,H),'#f5f1e8');d=ImageDraw.Draw(im)
 title=ImageFont.truetype(BOLD,48);body=ImageFont.truetype(FONT,27);caption=ImageFont.truetype(FONT,30)
 d.text((60,35),'A REQUEST BECOMES A SYSTEM',font=ImageFont.truetype(BOLD,19),fill='#466258')
 for i,line in enumerate(wrapped(d,scene['headline'],title,1150)):d.text((60,100+i*58),line,font=title,fill='#163b30')
 for j,label in enumerate(scene['steps']):
  x=60+j*405;d.rounded_rectangle((x,285,x+350,410),radius=15,fill=('#d3e9dd' if index==0 else '#e1e6f6'))
  lines=wrapped(d,label,body,305)
  if len(lines)>3:raise ValueError('Diagram label overflows')
  for k,line in enumerate(lines):d.text((x+20,305+k*32),line,font=body,fill='#163b30')
  if j<2:
   d.line((x+358,348,x+392,348),fill='#466258',width=4);d.polygon([(x+392,348),(x+382,341),(x+382,355)],fill='#466258')
 d.rectangle((35,510,1245,665),fill='#19392f')
 lines=wrapped(d,scene['narration'],caption,1140)
 if len(lines)>4:raise ValueError('Caption overflows')
 for k,line in enumerate(lines):d.text((60,525+k*34),line,font=caption,fill='#ffffff')
 d.text((60,682),'LOCAL RESEARCH DEMO · SYNTHETIC VOICE · GENERATED DIAGRAM',font=ImageFont.truetype(FONT,15),fill='#466258')
 im.save(path);return {'width':W,'height':H,'sha256':digest(path),'mode':'Programmatic diagram from local model scene plan; narration text burned into each scene.'}

def audio_duration(path):
 with wave.open(str(path)) as f:
  duration=f.getnframes()/f.getframerate()
  if f.getnchannels()!=1 or f.getsampwidth()!=2 or not 1<duration<60:raise ValueError('Unexpected narration PCM contract')
 return duration

def stamp(seconds):
 ms=round(seconds*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
def captions(scenes,durations):
 if len(scenes)!=len(durations) or any(not math.isfinite(x) or x<=0 for x in durations):raise ValueError('Invalid caption timing')
 lines=[];start=0
 for i,(s,duration) in enumerate(zip(scenes,durations),1):
  lines.append(f'{i}\n{stamp(start)} --> {stamp(start+duration)}\n{s["narration"]}\n');start+=duration
 return '\n'.join(lines)

def build(brief,run_name=None):
 name=run_name or time.strftime('%Y%m%d-%H%M%S')
 if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',name):raise ValueError('Unsafe run name')
 folder=D/'.runtime'/name;folder.mkdir(parents=True,exist_ok=False);started=time.monotonic()
 log={'status':'running','brief':brief,'events':[],'network_scope':'Application requests only loopback Ollama. F5 loads pinned local assets in offline mode. Not an OS-level network-isolation proof.'}
 def event(stage,**data):
  log['events'].append({'stage':stage,'elapsed_seconds':round(time.monotonic()-started,3),**data});(folder/'run.json').write_text(json.dumps(log,indent=2)+'\n')
 try:
  event('start');plan,model=plan_local(brief,folder);event('scene_plan',**model);clips=[];durations=[];images=[];audio_reports=[]
  for index,scene in enumerate(plan['scenes']):
   image=folder/f'scene-{index}.png';images.append(draw_scene(scene,index,image));event('image',scene=index,**images[-1])
   text=folder/f'narration-{index}.txt';text.write_text(scene['narration']);report=folder/f'tts-{index}.json'
   p=command([F5_PY,D/'tts_worker.py',text,folder/f'voice-{index}',report],timeout=300);(folder/f'tts-{index}.log').write_text(p.stdout+'\n'+p.stderr)
   result=json.loads(report.read_text());audio=Path(result['audio']);duration=audio_duration(audio);durations.append(duration);audio_reports.append(result);event('narration',scene=index,duration=duration,evidence=result['evidence'])
   clip=folder/f'clip-{index}.mp4';command([FF,'-y','-loop','1','-i',image,'-i',audio,'-t',str(duration),'-r',str(FPS),'-c:v','libx264','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',clip]);clips.append(clip);event('clip_encoded',scene=index,sha256=digest(clip))
  (folder/'captions.srt').write_text(captions(plan['scenes'],durations));listing=folder/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n" for p in clips));final=folder/'final.mp4'
  command([FF,'-y','-f','concat','-safe','0','-i',listing,'-c','copy','-movflags','+faststart',final]);event('assembly',sha256=digest(final))
  check=command([FF,'-v','info','-i',final,'-map','0:v:0','-map','0:a:0','-f','null','-']);(folder/'decode-check.log').write_text(check.stderr)
  if 'Video: h264' not in check.stderr or 'Audio: aac' not in check.stderr:raise ValueError('Expected video/audio streams not found')
  durations_meta=re.findall(r'Duration: (\d+):(\d+):(\d+\.\d+)',check.stderr)
  if not durations_meta:raise ValueError('Final duration not observable')
  h,m,s=map(float,durations_meta[0]);actual=h*3600+m*60+s;expected=sum(durations)
  if abs(actual-expected)>.25:raise ValueError('Video duration differs from audio timeline')
  for index,at in enumerate([0,durations[0]+.1]):command([FF,'-y','-ss',str(at),'-i',final,'-frames:v','1',folder/f'playback-frame-{index}.png'])
  log.update(status='passed',final=str(final),duration_seconds=actual,expected_seconds=expected,output_sha256=digest(final),captions=str(folder/'captions.srt'),visual_mode=model['mode'],scope='Working local illustrated-video prototype; no Langflow source graph executed, no general-purpose image/motion generation, no commercial readiness.')
  event('verified_decode',returncode=check.returncode);return log
 except Exception as exc:
  log.update(status='failed',error=str(exc));event('failed');raise
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--brief',required=True);p.add_argument('--run');a=p.parse_args();print(json.dumps(build(a.brief,a.run),indent=2))
