"""Native per-take adapters. Every generation writes a new immutable run."""
from pathlib import Path
import contextlib,hashlib,importlib.util,json,os,shutil,subprocess,time,uuid
S=Path(__file__).resolve().parent;ROOT=S.parents[2]
INDEX_RUNTIME=Path('/Users/x/.local/share/swarms/indextts-paper16')
MONEY=Path('/Users/x/.local/share/money/f5-tts')
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
reference_library=module('paper16_reference_library',S/'reference_library.py')
def refs():return reference_library.catalog()
def inventory():
 downloaded=json.loads((ROOT/'knowledge/research/paper-14-study/downloads.json').read_text())['models']
 models={m['repo']:m for m in downloaded}
 def present(repo):
  m=models[repo];return all((Path(m['snapshot'])/f['file']).is_file() and (Path(m['snapshot'])/f['file']).stat().st_size==f['bytes'] for f in m['files'])
 f5assets=json.loads((MONEY/'assets.json').read_text())
 f5ok=all(Path(f5assets[k]['path']).is_file() for k in f5assets if k.startswith(('SWivid/F5-TTS','charactr/vocos')))
 ip=json.loads((S/'indextts-downloads.json').read_text())
 iok=ip['stage']=='complete' and all(Path(f['path']).is_file() for m in ip['models'] for f in m['files'])
 return [
 {'id':'index','name':'IndexTTS 2.5','ready':iok,'controls':'Separate identity/emotion references, emotion strength, duration scale, seed.','note':'Local notebook adapter; Apple GPU tested.'},
 {'id':'vox','name':'VoxCPM2','ready':present('openbmb/VoxCPM2'),'controls':'Reference, steps, guidance, seed, optional written direction.','note':'VoiceStudio local API; no native emotion-strength slider.'},
 {'id':'f5','name':'F5-TTS v1 Base','ready':f5ok,'controls':'Reference, speed, steps, guidance, sway, crossfade, seed.','note':'Money engine; no native emotion-strength slider.'},
 {'id':'dia','name':'Dia 1.6B (MLX)','ready':Path('/Users/x/.local/share/swarms/paper16-dia/Dia-1.6B-fp16/model.safetensors').is_file(),'controls':'Script, seed and optional audio continuation. Speaker tags belong in the script.','note':'Study-isolated MLX fp16 adapter with corrected speaker continuation and automatic word check. Original recordings retained.'}]

DEFAULTS={
 'index':{'seed':7,'strength':1.0,'duration_scale':1.0},
 'vox':{'seed':7,'steps':10,'guidance':2.0,'direction':''},
 'f5':{'seed':7,'steps':32,'guidance':2.0,'speed':1.0,'sway':-1.0,'crossfade':.15},
 'dia':{'seed':7,'use_reference':True},
}
def default_settings(model):return dict(DEFAULTS[model])

def validate(model,text,speaker,emotion,settings,reference_override=None):
 if model not in DEFAULTS:raise ValueError('Unknown model')
 unknown=set(settings)-set(DEFAULTS[model])
 if unknown:raise ValueError('Unsupported native controls for '+model+': '+', '.join(sorted(unknown)))
 if not isinstance(text,str) or not 1<=len(text.strip())<=500:raise ValueError('Use 1–500 characters')
 if not 0<=int(settings.get('seed',7))<=2147483647:raise ValueError('Seed is outside range')
 ref=reference_override if reference_override is not None else refs().get(f'esd:{speaker}:{emotion}')
 if not ref:raise ValueError('Unknown reference')
 if hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest()!=ref['sha256']:raise ValueError('Reference file changed')
 if model=='index' and not 0<=float(settings.get('strength',1))<=1:raise ValueError('Strength must be between 0 and 1')
 if model=='index' and not .5<=float(settings.get('duration_scale',1))<=2:raise ValueError('Duration scale must be 0.5–2')
 if model in ('vox','f5') and not 1<=int(settings.get('steps',10 if model=='vox' else 32))<=64:raise ValueError('Steps must be 1–64')
 if model in ('vox','f5') and not 0.1<=float(settings.get('guidance',2))<=8:raise ValueError('Guidance must be 0.1–8')
 if model=='f5':
  if not .3<=float(settings.get('speed',1))<=2:raise ValueError('Speed must be 0.3–2')
  if not -1<=float(settings.get('sway',-1))<=1:raise ValueError('Sway must be -1–1')
  if not 0<=float(settings.get('crossfade',.15))<=.5:raise ValueError('Crossfade must be 0–0.5 seconds')
 return ref

def generate(model,text,speaker,emotion,settings,parent_id=None,reference_override=None,identity_override=None):
 ref=validate(model,text,speaker,emotion,settings,reference_override)
 identity=identity_override or (refs().get(f'esd:{speaker}:neutral') if reference_override is None else ref)
 if model=='index' and hashlib.sha256(Path(identity['path']).read_bytes()).hexdigest()!=identity['sha256']:raise ValueError('Identity reference changed')
 settings={**default_settings(model),**settings}
 if not next(m for m in inventory() if m['id']==model)['ready']:raise RuntimeError('Model assets are unavailable; no implicit download will be attempted')
 name='take-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8];folder=S/'runs'/name;folder.mkdir()
 request={'model':model,'text':text.strip(),'speaker':speaker,'emotion':emotion,'settings':settings,'applied_settings':settings,'parent_id':parent_id,'reference':ref,'reference_bindings':([dict(role=role,reference_id=r['id'],**{k:r[k] for k in ('path','sha256','transcript')}) for role,r in ([('identity',identity),('emotion',ref)] if model=='index' else [] if model=='dia' and not settings.get('use_reference',True) else [('performance',ref)])] if reference_override is not None else reference_library.bindings(model,speaker,emotion,settings)),'created':time.time(),'voice_conditioning':'uncontrolled' if model=='dia' and not settings.get('use_reference') else 'reference'}
 (folder/'take-request.json').write_text(json.dumps(request,indent=2))
 tick=time.time()
 try:
  if model=='index':
   native=module('take_index',S/'indextts_experiment.py').run(text=text.strip(),speaker=speaker,seed=int(settings.get('seed',7)),conditions=[{'emotion':emotion,'strength':float(settings.get('strength',1))}],duration_scale=float(settings.get('duration_scale',1)),reference_overrides={'neutral':identity,emotion:ref} if reference_override is not None else None)
   source=Path(native['takes'][0]['path']);request['native_run']=native['run_dir']
  elif model=='dia':
   env={**os.environ,'HF_HUB_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1'}
   with (folder/'inference.log').open('w') as log:
    subprocess.run(['/Users/x/.local/share/swarms/voicestudio/venv/bin/python',str(S/'dia_worker.py'),str(folder/'take-request.json')],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
   native=json.loads((folder/'dia-native-result.json').read_text());source=Path(native['path']);request['native_backend']=native
  elif model=='f5':
   cfg={'steps':int(settings.get('steps',32)),'speed':float(settings.get('speed',1)),'seed':int(settings.get('seed',7)),'reference':ref['id'],'cfg_strength':float(settings.get('guidance',2)),'sway_sampling_coef':float(settings.get('sway',-1)),'cross_fade_duration':float(settings.get('crossfade',.15))}
   if reference_override is not None:cfg.update(reference='upload:scene-reference',reference_text=ref['transcript'])
   worker={'text':text.strip(),'ordered':[{'id':'voice','type':'voice','config':cfg}],**({'reference_audio':ref['path']} if reference_override is not None else {})}
   (folder/'request.json').write_text(json.dumps(worker,indent=2))
   env={**os.environ,'HF_HUB_DISABLE_TELEMETRY':'1','ORT_DISABLE_TELEMETRY':'1'}
   with (folder/'inference.log').open('w') as log:
    subprocess.run([str(MONEY/'venv/bin/python'),str(ROOT/'services/audio-workbench/worker.py'),str(folder)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1200)
   source=Path(json.loads((folder/'result.json').read_text())['final'])
  else:
   import requests
   if model=='dia':
    current=requests.get('http://127.0.0.1:5196/engines/tts',timeout=15).json()
    if current.get('active_model')!='mlx-community/Dia-1.6B':raise RuntimeError('The MLX backend is not currently Dia; no model switching or download was performed')
   formatted=text.strip()
   if model=='dia' and not formatted.endswith(('[S1]','[S2]')):formatted+=' [S2]'
   fields={'text':formatted,'engine':'voxcpm2' if model=='vox' else 'mlx-audio','seed':str(settings.get('seed',7)),'effect_preset':'raw','wav_bits':'24','max_chunk_chars':'0','pronounce':'false'}
   if model=='vox':
    fields.update(num_step=str(settings.get('steps',10)),guidance_scale=str(settings.get('guidance',2)))
    direction=str(settings.get('direction','')).strip()
    if direction:fields['instruct']=direction
    else:fields['ref_text']=ref['transcript']
   # Dia intentionally receives neither reference nor ignored generic controls.
   with contextlib.ExitStack() as stack:
    files={k:(None,str(v)) for k,v in fields.items()}
    if model=='dia' and settings.get('use_reference'):fields['ref_text']=ref['transcript'];files['ref_text']=(None,ref['transcript'])
    if model=='vox' or (model=='dia' and settings.get('use_reference')):files['ref_audio']=(Path(ref['path']).name,stack.enter_context(Path(ref['path']).open('rb')),'audio/wav')
    (folder/'api-fields.json').write_text(json.dumps(fields,indent=2))
    response=requests.post('http://127.0.0.1:5196/generate',files=files,timeout=(10,900))
   if response.status_code!=200:(folder/'api-error.txt').write_text(response.text)
   response.raise_for_status();source=folder/'native.wav';source.write_bytes(response.content)
  media=subprocess.run([str(INDEX_RUNTIME/'venv/bin/python'),str(S/'take_media.py'),str(source),str(folder)],capture_output=True,text=True,check=True,timeout=60)
  record={**request,**json.loads(media.stdout),'id':name,'elapsed_seconds':time.time()-tick,'assessment':'Unrated; generation is not validation'}
  if model=='dia':
   check=subprocess.run(['/Users/x/.local/share/swarms/voicestudio/venv/bin/python',str(S/'speech_check.py'),str(folder/'take-request.json'),str(source)],capture_output=True,text=True,timeout=90)
   if check.returncode==0:
    record['word_check']=json.loads(check.stdout);record['assessment']='Exact words recovered by local ASR; delivery unreviewed' if record['word_check']['exact_words'] else 'Word check failed; experimental audio, not validated speech'
   else:record['word_check']={'error':'Local speech check unavailable; listening required'}
  export=ROOT/'knowledge/research/notebooks/paper-16-audio'/(name+'.wav');shutil.copy2(source,export);record['url']='/research-jupyter/files/paper-16-audio/'+export.name
  (folder/'take-result.json').write_text(json.dumps(record,indent=2))
  return record
 except Exception as exc:
  (folder/'take-error.json').write_text(json.dumps({'error':str(exc),'elapsed_seconds':time.time()-tick},indent=2));raise
