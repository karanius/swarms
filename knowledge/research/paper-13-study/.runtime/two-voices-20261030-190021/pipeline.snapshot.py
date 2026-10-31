"""Notebook-first two-voice motion short; real Money engines, no web UI."""
from pathlib import Path
import json,subprocess,time,hashlib,math,sys,wave,array
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
WORKER=ROOT/'services/audio-workbench/worker.py'
PY=Path('/Users/x/.local/share/money/f5-tts/venv/bin/python')
FF=Path('/Users/x/projects/money/runtimes/daily-video/.venv/lib/python3.14/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1')
W,H,FPS,SR=1280,720,24,48000
FONTS={size:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',size) for size in (18,20,24,27,30,34,42,58)}
BOLD={size:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',size) for size in (18,24,34,42,58)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def call(args,timeout=300):
 p=subprocess.run([str(a) for a in args],capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-2000:])
 return p

def validate(story):
 if len(story.get('scenes',[]))!=4:raise ValueError('Four scene protocol')
 speakers=set();emotions={}
 for scene in story['scenes']:
  if scene['speaker'] not in story['voices']:raise ValueError('Unknown speaker')
  if not 5<=len(scene['text'].split())<=20:raise ValueError('Use 5–20 words per turn')
  if scene['emotion'] not in ('neutral','happiness','sadness','anger','surprise'):raise ValueError('Unknown reference emotion')
  speakers.add(scene['speaker']);emotions.setdefault(scene['speaker'],set()).add(scene['emotion'])
 if len(speakers)!=2 or any(len(e)<2 for e in emotions.values()):raise ValueError('Two voices with contrasting intended emotions required')
 if {v['gender'] for v in story['voices'].values()}!={'male','female'}:raise ValueError('Male and female casting required')
 return story

def wrap(draw,text,font,width):
 lines=[];line=''
 for word in text.split():
  candidate=(line+' '+word).strip()
  if draw.textlength(candidate,font=font)>width:lines.append(line);line=word
  else:line=candidate
 if line:lines.append(line)
 return lines

def ease(x):return x*x*(3-2*x)
def lerp(a,b,t):return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
def frame(story,scene,index,t,duration,voice_duration):
 """Authored procedural motion: lantern, stepping stones, two speaker tokens."""
 progress=t/duration;warm=ease(min(1,max(0,(index+progress)/4)))
 top=lerp((12,23,44),(35,38,62),warm);bottom=lerp((32,49,67),(82,66,64),warm)
 gradient=np.zeros((H,W,3),dtype=np.uint8)
 for y in range(H):gradient[y,:,:]=lerp(top,bottom,y/H)
 im=Image.fromarray(gradient);draw=ImageDraw.Draw(im)
 rng=np.random.default_rng(13)
 for x,y,r in zip(rng.integers(40,W-40,60),rng.integers(110,440,60),rng.uniform(.4,1.5,60)):
  glow=int(130+55*math.sin(t*.5+x));draw.ellipse((int(x),int(y),int(x+r*2),int(y+r*2)),fill=(glow,glow,180))
 # Shifting mist / layered hills provide visible motion without implying generated footage.
 shift=12*math.sin(t*.16+index)
 draw.polygon([(0,430),(210+shift,345),(460,415),(760+shift,320),(1100,390),(1280,340),(1280,600),(0,600)],fill=(24,42,55))
 draw.polygon([(0,478),(300,410),(565+shift,470),(900,385),(1280,456),(1280,600),(0,600)],fill=(35,55,66))
 draw.rectangle((0,500,W,600),fill=(18,36,49))
 for j in range(9):
  y=516+j*9;offset=math.sin(t*.6+j)*12;draw.line((150+offset,y,1130+offset,y),fill=(38+j,60+j,70+j),width=1)
 # The path gradually becomes visible; construction is intentionally unfinished.
 count=(index+1)*2
 for j in range(count):
  x=370+j*67;rise=6*math.sin(j*.5)
  draw.rounded_rectangle((x,480-rise,x+53,496-rise),radius=5,fill=lerp((65,91,102),(177,148,98),warm))
 # Distinct cast tokens, not impersonated people or lip-synced avatars.
 for name,cx,col in [('Mira',290,(142,192,206)),('Rowan',1000,(221,176,117))]:
  active=scene['speaker']==name;bob=3*math.sin(t*1.4+(0 if name=='Mira' else 2))
  draw.ellipse((cx-18,419+bob,cx+18,455+bob),fill=col)
  draw.rounded_rectangle((cx-29,455+bob,cx+29,505+bob),radius=14,fill=col)
  if active:draw.arc((cx-36,405+bob,cx+36,477+bob),195,345,fill=(250,232,192),width=3)
 # Lantern pulse and progressive horizontal travel.
 lx=370+min(7.5,index*2+ease(progress)*1.5)*67;ly=435+4*math.sin(t*1.3)
 glow=Image.new('RGBA',(W,H));gd=ImageDraw.Draw(glow)
 for radius,alpha in [(100,10),(65,18),(38,38)]:gd.ellipse((lx-radius,ly-radius,lx+radius,ly+radius),fill=(255,192,95,alpha))
 im=Image.alpha_composite(im.convert('RGBA'),glow.filter(ImageFilter.GaussianBlur(14)));draw=ImageDraw.Draw(im)
 draw.rounded_rectangle((lx-13,ly-20,lx+13,ly+17),radius=5,fill=(255,215,132));draw.arc((lx-11,ly-32,lx+11,ly-10),180,360,fill=(241,211,161),width=3)
 draw.text((54,32),'ONE SMALL LIGHT',font=BOLD[24],fill=(246,234,212))
 draw.text((54,68),'A two-voice local audio study',font=FONTS[18],fill=(158,183,196))
 draw.text((W-165,36),f'{index+1:02} / 04',font=FONTS[20],fill=(174,192,200))
 title=scene['headline'];draw.text((54,142),title,font=BOLD[42],fill=(245,234,214))
 # Exact complete turn stays readable throughout; no unsupported word-alignment claim.
 draw.rounded_rectangle((40,564,1240,684),radius=15,fill=(12,25,36))
 name=f"{scene['speaker'].upper()}  /  {scene['emotion'].upper()} REFERENCE"
 draw.text((62,577),name,font=BOLD[18],fill=(209,183,137))
 lines=wrap(draw,scene['text'],FONTS[27],1150)
 if len(lines)>2:raise ValueError('Caption overflow')
 for k,line in enumerate(lines):draw.text((62,608+32*k),line,font=FONTS[27],fill=(245,241,232))
 draw.text((54,696),'SYNTHETIC VOICES · ORIGINAL PROCEDURAL VISUALS · RESEARCH DEMO',font=FONTS[18],fill=(158,180,191))
 # Brief fade from/to the same background at each scene boundary.
 fade=min(1,t/.22,(duration-t)/.22)
 if fade<1:im=Image.blend(Image.new('RGBA',(W,H),(12,23,44,255)),im,max(0,fade))
 return im.convert('RGB')

def graph_for(story,scene):
 voice=story['voices'][scene['speaker']]
 return {'text':scene['text'],'ordered':[{'id':kind,'type':kind,'config':cfg} for kind,cfg in [('text',{}),('voice',{'reference':f"esd:{voice['speaker_id']}:{scene['emotion']}",'steps':32,'speed':.95,'seed':42,'cross_fade_duration':.15,'cfg_strength':2.,'sway_sampling_coef':-1.}),('master',{'profile':'Balanced'}),('enhance',{'evaluations':32,'denoise':.1})]],'edges':[{'source':'text','target':'voice'},{'source':'voice','target':'master'},{'source':'master','target':'enhance'}]}

def build(story,run_name):
 validate(story)
 if not run_name.replace('-','').replace('_','').isalnum():raise ValueError('Unsafe run name')
 folder=D/'.runtime'/run_name;folder.mkdir(parents=True,exist_ok=False)
 (folder/'story.json').write_text(json.dumps(story,indent=2));started=time.monotonic();record={'status':'running','events':[],'scenes':[]}
 def event(name,**data):
  record['events'].append({'stage':name,'seconds':round(time.monotonic()-started,2),**data});(folder/'run.json').write_text(json.dumps(record,indent=2));print(name,data,flush=True)
 try:
  event('start');(folder/'worker.snapshot.py').write_bytes(WORKER.read_bytes())
  clips=[];timeline=[];cursor=0
  for i,scene in enumerate(story['scenes']):
   stage=folder/f'audio-{i}';stage.mkdir();request=graph_for(story,scene);(stage/'request.json').write_text(json.dumps(request,indent=2))
   event('audio_started',scene=i,speaker=scene['speaker'],emotion=scene['emotion'])
   p=call([PY,'-B',folder/'worker.snapshot.py',stage],timeout=600);(stage/'worker.log').write_bytes(p.stdout+p.stderr)
   result=json.loads((stage/'result.json').read_text());assert result['status']=='passed';audio=Path(result['final'])
   raw=call([FF,'-v','error','-i',audio,'-ar',SR,'-ac',1,'-f','f32le','-']).stdout;samples=np.frombuffer(raw,dtype='<f4').copy()
   voice_duration=len(samples)/SR;frames=math.ceil((voice_duration+.85)*FPS);duration=frames/FPS;lead=.35
   timeline.append({'start':cursor,'duration':duration,'speech_start':cursor+lead,'speech_end':cursor+lead+voice_duration,'frames':frames,'audio':str(audio),'audio_sha256':sha(audio),'request':request,'scene':scene})
   cursor+=duration;event('audio_finished',scene=i,duration=voice_duration)
   clip=folder/f'visual-{i}.mp4';cmd=[str(x) for x in [FF,'-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',FPS,'-i','-','-an','-c:v','libx264','-preset','fast','-crf',20,'-pix_fmt','yuv420p',clip]]
   with (folder/f'encode-{i}.log').open('wb') as log:
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
    try:
     for f in range(frames):
      image=frame(story,scene,i,f/FPS,duration,voice_duration);process.stdin.write(image.tobytes())
      if f==frames//2:image.save(folder/f'scene-{i}.png')
    finally:process.stdin.close()
    if process.wait(timeout=120):raise RuntimeError('Visual encoder failed')
   clips.append(clip);record['scenes'].append(timeline[-1]);event('scene_rendered',scene=i,frames=frames)
  total=round(cursor*SR);dialogue=np.zeros(total,dtype=np.float32)
  for entry in timeline:
   raw=call([FF,'-v','error','-i',entry['audio'],'-ar',SR,'-ac',1,'-f','f32le','-']).stdout;a=np.frombuffer(raw,dtype='<f4');at=round(entry['speech_start']*SR);dialogue[at:at+len(a)]+=a
  # Original quiet tone bed; slow attack/release and speech-side ducking.
  t=np.arange(total,dtype=np.float64)/SR;bed=np.zeros(total)
  for frequency in (130.8128,196.,261.6256):bed+=np.sin(2*np.pi*frequency*t)/3
  envelope=np.minimum(1,t/2)*np.minimum(1,(cursor-t)/2)
  bed*=.004*envelope
  dialogue_track=folder/'dialogue.f32';dialogue_track.write_bytes(dialogue.astype('<f4').tobytes())
  mix=np.clip(dialogue+bed,-.99,.99).astype('<f4');mix_path=folder/'mix.f32';mix_path.write_bytes(mix.tobytes())
  # Keep delivery PCM at actual processed levels; no hidden per-voice regeneration.
  mixwav=folder/'soundtrack.wav';call([FF,'-y','-v','error','-f','f32le','-ar',SR,'-ac',1,'-i',mix_path,'-c:a','pcm_s24le',mixwav])
  listing=folder/'concat.txt';listing.write_text(''.join("file '"+str(x)+"'\n" for x in clips));silent=folder/'picture.mp4';call([FF,'-y','-v','error','-f','concat','-safe',0,'-i',listing,'-c','copy',silent])
  final=folder/'One Small Light.mp4';call([FF,'-y','-v','error','-i',silent,'-i',mixwav,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-t',str(cursor),final])
  (folder/'timeline.json').write_text(json.dumps(timeline,indent=2))
  sheet=Image.new('RGB',(1280,720))
  for i in range(4):sheet.paste(Image.open(folder/f'scene-{i}.png').resize((640,360)),((i%2)*640,(i//2)*360))
  sheet.save(folder/'contact-sheet.png')
  record.update(status='passed',final=str(final),duration_seconds=cursor,output_sha256=sha(final),soundtrack=str(mixwav),scope='Authored procedural motion short, locally generated synthetic dialogue; intended emotion is not guaranteed emotional transfer or commercial clearance.')
  event('finished',duration=cursor);return record
 except Exception as exc:record.update(status='failed',error=str(exc));event('failed',error=str(exc));raise
