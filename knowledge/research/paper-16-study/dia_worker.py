"""Study-only Dia worker using a pinned official implementation and checkpoint."""
import os,sys,json,time,hashlib,importlib.util
from pathlib import Path
S=Path(__file__).resolve().parent;CACHE=Path('/Users/x/.local/share/swarms/voicestudio/cache');CHECKPOINT=Path('/Users/x/.local/share/swarms/paper16-dia/Dia-1.6B-fp16')
os.environ.update(HF_HUB_OFFLINE='1',HF_HUB_CACHE=str(CACHE),HF_HUB_DISABLE_TELEMETRY='1')
import mlx.core as mx,mlx_audio.tts.models,numpy as np,soundfile as sf
request_path=Path(sys.argv[1]);request=json.loads(request_path.read_text());folder=request_path.parent
name='mlx_audio.tts.models.dia';spec=importlib.util.spec_from_file_location(name,S/'dia-upstream-fix/_entry.py',submodule_search_locations=[str(S/'dia-upstream-fix')]);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
from mlx_audio.tts.utils import load_model
model=load_model(str(CHECKPOINT));mx.random.seed(int(request['settings']['seed']))
from dia_input import format_input
use_ref=bool(request['settings'].get('use_reference'))
text,transcript=format_input(request['text'],request['reference']['transcript'] if use_ref else None)
kwargs={'text':text,'verbose':False}
if use_ref:kwargs.update(ref_audio=request['reference']['path'],ref_text=transcript)
(folder/'dia-formatted-input.json').write_text(json.dumps({k:v for k,v in kwargs.items() if k!='verbose'},indent=2))
chunks=[]
for result in model.generate(**kwargs):chunks.append(np.array(result.audio));rate=result.sample_rate
if not chunks:raise RuntimeError('Dia produced no audio')
path=folder/'native.wav';sf.write(path,np.concatenate(chunks),rate,subtype='PCM_24')
(folder/'dia-native-result.json').write_text(json.dumps({'path':str(path),'sample_rate':rate,'checkpoint':'mlx-community/Dia-1.6B-fp16','revision':'4575dd9622ffa7dd14cc4342e1aac4bb7841904d','implementation_commit':'0018b2e470224a166cfe5e6a41e79b1d8be9c5e7','settings':request['settings'],'reference_used':bool(request['settings'].get('use_reference'))},indent=2))
