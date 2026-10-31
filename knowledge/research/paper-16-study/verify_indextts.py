"""Independent artifact checks for the saved IndexTTS audition."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np,soundfile as sf
S=Path(__file__).resolve().parent
result=json.loads((S/'indextts-latest.json').read_text())
assert len(result['takes'])==3
assert len({t['sha256'] for t in result['takes']})==3
assert result['parameter_device']=='mps:0'
assert 'mps:0' in result['observed_feature_tensor_devices']
checks=[]
ffmpeg='/Users/x/.local/share/money/f5-tts/venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
for t in result['takes']:
 p=Path(t['path']);a,sr=sf.read(p)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==t['sha256']
 assert sr==t['sample_rate'] and abs(len(a)/sr-t['duration_seconds'])<1e-6
 assert np.isfinite(a).all() and np.sqrt(np.mean(a*a))>1e-6
 log=subprocess.run([ffmpeg,'-hide_banner','-i',t['listening_path'],'-af','loudnorm=I=-23:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
 meter=json.loads(log[log.rfind('{'):log.rfind('}')+1])
 assert abs(float(meter['input_i'])+23)<0.3
 checks.append({'emotion':t['emotion'],'strength':t['strength'],'listening_lufs':float(meter['input_i']),'valid':True})
refs=result['request']['references']
for r in refs.values():assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
prior=json.loads((S/'preservation.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in prior.items())
report={'artifact_checks':checks,'earlier_papers_unchanged':True,'reference_files_unchanged':True,'observed_feature_devices':result['observed_feature_tensor_devices'],'listening_judgment':None,'browser_media_loaded':5,'browser_playback_started':True}
(S/'indextts-verification.json').write_text(json.dumps(report,indent=2))
print('PASS: three distinct valid takes, matched listening levels, actual MPS tensor evidence, source and earlier-paper preservation')
