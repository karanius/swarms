"""Isolated official Dia cache/prefill fix, no changes to installed VoiceStudio."""
import os
from pathlib import Path
S=Path(__file__).resolve().parent;CACHE=Path('/Users/x/.local/share/swarms/voicestudio/cache')
os.environ.update(HF_HUB_OFFLINE='1',HF_HUB_CACHE=str(CACHE),HF_HUB_DISABLE_TELEMETRY='1')
import importlib.util,sys,json,time,uuid
import mlx.core as mx
import mlx_audio.tts.models
name='mlx_audio.tts.models.dia';spec=importlib.util.spec_from_file_location(name,S/'dia-upstream-fix/_entry.py',submodule_search_locations=[str(S/'dia-upstream-fix')]);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
from mlx_audio.tts.utils import load_model
import soundfile as sf,numpy as np
folder=S/'runs'/('dia-fixed-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]);folder.mkdir()
model_path=Path(sys.argv[1]) if len(sys.argv)>1 else next((CACHE/'models--mlx-community--Dia-1.6B/snapshots').iterdir());alias=model_path if 'Dia' in model_path.name else Path('/Users/x/.local/share/swarms/paper16-asr/Dia-1.6B');alias.symlink_to(model_path,target_is_directory=True) if not alias.exists() else None;model=load_model(str(alias));mx.random.seed(7)
text=sys.argv[2] if len(sys.argv)>2 else 'I need you to stay right here.';chunks=[]
for r in model.generate(text='[S1] '+text+' [S2]',verbose=False):chunks.append(np.array(r.audio));rate=r.sample_rate
path=folder/'native.wav';sf.write(path,np.concatenate(chunks),rate,subtype='PCM_24')
record={'id':folder.name,'path':str(path),'text':text,'model':'dia','speaker':'0012','emotion':'neutral','settings':{'seed':7,'use_reference':False},'source':'Isolated official Dia cache/prefill fix; generated speaker, no reference','created':time.time()};(folder/'take-result.json').write_text(json.dumps(record,indent=2));(S/'dia-fixed-result.json').write_text(json.dumps(record,indent=2));print(path)
