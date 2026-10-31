"""Execute validated graph stages through Money's existing engines, in isolation."""
import os,sys,json,time,importlib.util,hashlib,gc
from pathlib import Path
os.environ.update(MPLBACKEND='Agg',HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1',TRANSFORMERS_OFFLINE='1',F5_RUNTIME_ROOT='/Users/x/.local/share/money/f5-tts')
SOURCE=Path('/Users/x/projects/money/runtimes/f5-tts');sys.path.insert(0,str(SOURCE))
def load(name):
 spec=importlib.util.spec_from_file_location('aw_'+name,SOURCE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if sys.argv[1]=='catalog':
 import tomllib
 from voice_presets import catalog,find
 cfg=tomllib.loads((SOURCE/'config.toml').read_text());rows=[dict(r,token='esd:'+r['speaker_id']+':'+r['emotion'],variant='active') for r in catalog()['presets']]+[dict(r,token='esd-original:'+r['speaker_id']+':'+r['emotion'],variant='original') for r in catalog('original')['presets']]
 print('CATALOG='+json.dumps({'defaults':{k:cfg[k] for k in ['steps','speed','seed','reference_audio','cross_fade_duration','cfg_strength','sway_sampling_coef']},'presets':[{'id':r['token'],'label':f"Voice {r['speaker_id']} · {r['gender']} · {r['emotion']} · {r['variant']}",'path':str(Path(os.environ['F5_RUNTIME_ROOT'])/'datasets/esd'/r['path']),'sha256':r['sha256'],'transcript':r['transcript']} for r in rows],'profiles':list(json.loads((SOURCE/'polish-config.json').read_text())['profiles']),'master_defaults':json.loads((SOURCE/'polish-config.json').read_text()),'enhance_defaults':json.loads((SOURCE/'enhance-config.json').read_text()),'source':str(SOURCE)}));sys.exit()
if sys.argv[1]=='inspect':
 import soundfile as sf,numpy as np
 path=Path(sys.argv[2]);info=sf.info(path)
 if not 1<=info.duration<=600:raise ValueError('Use 1–600 seconds of audio')
 wav,_=sf.read(path,dtype='float32',always_2d=True)
 if not np.isfinite(wav).all() or float(np.sqrt(np.mean(wav**2)))<1e-5:raise ValueError('Use audible finite audio')
 print(json.dumps({'seconds':info.duration,'sample_rate':info.samplerate,'channels':info.channels}));sys.exit()
folder=Path(sys.argv[1]).resolve();request=json.loads((folder/'request.json').read_text());started=time.monotonic()
def emit(event,**data):
 with (folder/'events.jsonl').open('a') as f:f.write(json.dumps({'event':event,'elapsed_seconds':round(time.monotonic()-started,3),**data})+'\n')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(name,value):
 target=folder/name;temp=folder/(name+'.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(target)
outputs={};text=request['text'];audio=request.get('input_audio')
try:
 for node in request['ordered']:
  if request.get('start_at') and ['text','voice','master','enhance'].index(node['id'])<['text','voice','master','enhance'].index(request['start_at']):continue
  ident=node['id'];kind=node['type'];cfg=node['config'];emit('stage_started',node=ident,kind=kind)
  if kind=='text':outputs[ident]={'text':text};emit('stage_finished',node=ident,kind=kind);continue
  stage=folder/ident;stage.mkdir()
  if kind=='voice':
   import tomllib
   g=load('generate');g.PROJECT=stage
   for lock in ['models.lock.json','esd.lock.json']:(stage/lock).write_bytes((SOURCE/lock).read_bytes())
   settings=tomllib.loads((SOURCE/'config.toml').read_text());settings.update(text=text,steps=cfg['steps'],speed=cfg['speed'],seed=cfg['seed'],reference_audio=cfg['reference'])
   settings.update({k:cfg[k] for k in ('cross_fade_duration','cfg_strength','sway_sampling_coef') if k in cfg})
   if cfg['reference'].startswith('upload:'):
    ref=Path(request['reference_audio']);target=stage/'reference.wav';target.write_bytes(ref.read_bytes());settings['reference_audio']=str(target);settings['reference_text']=cfg['reference_text']
   elif cfg['reference']=='bundled':settings['reference_text']='Some call me nature, others call me mother nature.'
   else:
    from voice_presets import resolve
    _,row=resolve(cfg['reference']);settings['reference_text']=row['transcript']
   audio,report=g.generate(settings,publish_latest=False);report['settings']=settings;outputs[ident]={'audio':audio,'report':report};g.MODEL=None;gc.collect()
   import torch
   torch.mps.empty_cache()
  elif kind=='master':
   p=load('polish');p.PROJECT=stage
   settings=json.loads((SOURCE/'polish-config.json').read_text());settings.update({k:cfg[k] for k in ('sample_rate','target_lufs','true_peak_db','loudness_range') if k in cfg});settings['profiles'][cfg['profile']].update({k:v for k,v in cfg.items() if k not in ('profile','sample_rate','target_lufs','true_peak_db','loudness_range')});(stage/'polish-config.json').write_text(json.dumps(settings))
   report=p.polish(audio,profile=cfg['profile'],output_root=stage,publish_latest=False);audio=report['master'];outputs[ident]={'audio':audio,'report':report,'before':report['before'],'after':report['after'],'comparison':report['comparison'],'original':report['original']}
  elif kind=='enhance':
   e=load('enhance');e.PROJECT=stage
   settings=json.loads((SOURCE/'enhance-config.json').read_text());settings.update({k:v for k,v in cfg.items() if k not in ('evaluations','denoise')});(stage/'enhance-config.json').write_text(json.dumps(settings));(stage/'enhance.lock.json').write_bytes((SOURCE/'enhance.lock.json').read_bytes())
   report=e.enhance_recording(audio,nfe=cfg['evaluations'],denoise_strength=cfg['denoise'],output_root=stage,publish_latest=False);audio=report['output'];outputs[ident]={'audio':audio,'report':report,'before':report['before'],'after':report['after'],'comparison':report['comparison'],'original':report['original']}
  else:raise ValueError('Unknown engine')
  save('outputs.json',outputs);emit('stage_finished',node=ident,kind=kind,audio_sha256=sha(audio))
 emit('finished',audio_sha256=sha(audio));save('result.json',{'status':'passed','outputs':outputs,'final':audio})
except Exception as exc:
 emit('failed',error=str(exc));save('result.json',{'status':'failed','error':str(exc)});raise
