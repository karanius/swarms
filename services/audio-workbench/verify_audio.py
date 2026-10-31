"""Independent file/chain/meter checks; run using Money's prepared environment."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,soundfile as sf
SOURCE=Path('/Users/x/projects/money/runtimes/f5-tts');sys.path.insert(0,str(SOURCE))
from polish import comparison_measure
folder=Path(sys.argv[1]);result=json.loads((folder/'result.json').read_text());out=result['outputs'];checks={};sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for kind in [k for k in ['voice','master','enhance'] if k in out]:
 a,sr=sf.read(out[kind]['audio']);assert np.isfinite(a).all() and np.sqrt(np.mean(a*a))>.001;checks[kind]={'seconds':len(a)/sr,'sample_rate':sr,'peak':float(np.max(np.abs(a))),'sha256':sha(out[kind]['audio'])}
if 'master' in out:
 assert out['master']['report']['source_sha256']==out['master']['report']['original_copy_sha256']
 if 'voice' in out:assert checks['voice']['sha256']==out['master']['report']['source_sha256']
if 'enhance' in out:
 if 'enhance' in out:assert out['enhance']['report']['source_sha256']==out['enhance']['report']['original_copy_sha256']
 if 'master' in out:assert checks['master']['sha256']==out['enhance']['report']['source_sha256']
if 'voice' in out:assert out['voice']['report']['gpu_execution_evidence']['transformer_forward_calls']>0
if 'enhance' in out:assert out['enhance']['report']['inference_evidence']['forward_calls']>0
for kind in [k for k in ['master','enhance'] if k in out]:
 before=comparison_measure(out[kind]['before']);after=comparison_measure(out[kind]['after']);difference=abs(float(before['input_i'])-float(after['input_i']));assert difference<=.25
 checks[kind]['independent_matched_difference_lu']=difference
if 'master' in out:
 master=comparison_measure(out['master']['audio']);cfg=out['master']['report']['settings'];assert abs(float(master['input_i'])-cfg['target_lufs'])<=.5 and float(master['input_tp'])<=cfg['true_peak_db']+.15
 checks['master']['independent_master_measurement']=master
preserved=json.loads((Path(__file__).parent/'preserved-money.json').read_text());assert all(sha(p)==h for p,h in preserved.items())
checks['money_settings_and_latest_pointers_unchanged']=True
(folder/'independent-verification.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
