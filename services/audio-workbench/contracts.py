"""Typed, bounded graph contracts; canvas data never becomes arbitrary code."""
import math
RANGES={
 'voice':{'cross_fade_duration':(0,1),'cfg_strength':(0,10),'sway_sampling_coef':(-1,1)},
 'master':{'sample_rate':(24000,96000),'target_lufs':(-30,-9),'true_peak_db':(-6,-1),'loudness_range':(1,20),'highpass_hz':(20,200),'mud_db':(-12,6),'presence_db':(-6,12),'ratio':(1,10),'threshold_db':(-50,0),'attack_ms':(.1,100),'release_ms':(10,1000),'deess_intensity':(0,1)},
 'enhance':{'threads':(1,16),'temperature':(0,1),'seed':(0,2147483647),'max_seconds':(1,120)}}
def advanced(kind,cfg,base):
 extra=set(cfg)-base
 if not extra<=set(RANGES[kind])|({'solver'} if kind=='enhance' else set()):raise ValueError('Unsupported advanced setting')
 for key in extra:
  value=cfg[key]
  if key=='solver':
   if value not in ('euler','midpoint','rk4'):raise ValueError('Invalid solver')
  else:
   lo,hi=RANGES[kind][key]
   if type(value) not in (int,float) or not math.isfinite(value) or not lo<=value<=hi:raise ValueError('Invalid '+key)
   if key in ('threads','seed','max_seconds','sample_rate') and type(value)is not int:raise ValueError('Use an integer for '+key)
   if key=='sample_rate' and value not in (24000,44100,48000,96000):raise ValueError('Unsupported sample rate')
KINDS={'text','voice','master','enhance'}
def compile_graph(payload,presets):
 if not isinstance(payload,dict):raise ValueError('Expected a graph request')
 text=payload.get('text');nodes=payload.get('nodes');edges=payload.get('edges')
 if not isinstance(text,str) or not 5<=len(text.strip())<=1800:raise ValueError('Enter 5–1800 characters of narration')
 if not isinstance(nodes,list) or not 2<=len(nodes)<=4 or not isinstance(edges,list):raise ValueError('Use 2–4 audio components')
 by={};types=set()
 for n in nodes:
  if not isinstance(n,dict) or n.get('type') not in KINDS:raise ValueError('Unknown component')
  ident=n.get('id');kind=n['type']
  if ident!=kind or ident in by or kind in types:raise ValueError('Use one component of each kind, with its matching ID')
  cfg=n.get('config',{});
  if not isinstance(cfg,dict):raise ValueError('Invalid component settings')
  if kind=='voice':
   if not {'reference','steps','speed','seed'}<=set(cfg):raise ValueError('Invalid voice settings')
   advanced(kind,cfg,{'reference','steps','speed','seed','reference_text'})
   if not isinstance(cfg['reference'],str):raise ValueError('Invalid reference')
   if cfg['reference'].startswith('upload:') and (not isinstance(cfg.get('reference_text'),str) or not 1<=len(cfg['reference_text'].strip())<=2000):raise ValueError('Enter the exact reference transcript')
   if cfg['reference'] not in presets|{'bundled'}:raise ValueError('Choose a prepared voice reference')
   if type(cfg['steps']) is not int or not 8<=cfg['steps']<=64:raise ValueError('Choose 8–64 voice steps')
   if type(cfg['speed']) not in (float,int) or not .3<=cfg['speed']<=2:raise ValueError('Voice speed must be 0.3–2')
   if type(cfg['seed']) is not int or not 0<=cfg['seed']<2**31:raise ValueError('Invalid voice seed')
  if kind=='master':
   if cfg.get('profile') not in ('Gentle','Balanced','Present'):raise ValueError('Choose a mastering profile')
   advanced(kind,cfg,{'profile'})
  if kind=='enhance':
   advanced(kind,cfg,{'evaluations','denoise'})
   if not {'evaluations','denoise'}<=set(cfg) or type(cfg['evaluations']) is not int or cfg['evaluations'] not in (16,32,64) or type(cfg['denoise']) not in (int,float) or not 0<=cfg['denoise']<=1:raise ValueError('Invalid enhancement settings')
  if kind=='text' and cfg:raise ValueError('Text settings belong in the narration input')
  by[ident]={'id':ident,'type':kind,'config':cfg};types.add(kind)
 if not {'text','voice'}<=types:raise ValueError('Narration input and voice generation are required')
 allowed={('text','voice'),('voice','master'),('master','enhance')};actual=[]
 for e in edges:
  if not isinstance(e,dict):raise ValueError('Invalid wire')
  pair=(e.get('source'),e.get('target'))
  if pair not in allowed or pair[0] not in by or pair[1] not in by or pair in actual:raise ValueError('Connect Text → Voice → Master → Enhance; each wire has a distinct audio contract')
  actual.append(pair)
 expected=[('text','voice')]+([('voice','master')] if 'master'in types else [])+([('master','enhance')] if 'enhance'in types else [])
 if set(actual)!=set(expected):raise ValueError('Connect every component; enhancement requires a mastered recording')
 order=[by[k] for k in ['text','voice','master','enhance'] if k in by]
 return {'text':text.strip(),'ordered':order,'edges':edges,'scope':'Audio engine graph only; no arbitrary commands or downloaded template code'}
