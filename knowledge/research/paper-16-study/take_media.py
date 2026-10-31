"""Validate and prepare a static-gain listening copy, leaving source audio intact."""
from pathlib import Path
import hashlib,json,subprocess,sys
import numpy as np,soundfile as sf
FFMPEG='/Users/x/.local/share/money/f5-tts/venv/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
def prepare(source,folder):
 source=Path(source);folder=Path(folder);a,sr=sf.read(source)
 if not a.size or not np.isfinite(a).all() or np.sqrt(np.mean(a*a))<1e-6:raise ValueError('Audio is empty, nonfinite or silent')
 log=subprocess.run([FFMPEG,'-hide_banner','-i',str(source),'-af','loudnorm=I=-23:TP=-2:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
 meter=json.loads(log[log.rfind('{'):log.rfind('}')+1])
 gain=10**(min(-23-float(meter['input_i']),-2-float(meter['input_tp']))/20)
 if not np.isfinite(gain):raise ValueError('Cannot measure listening level')
 target=folder/'listening.wav';sf.write(target,a*gain,sr,subtype='PCM_24')
 return {'path':str(source),'listening_path':str(target),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'duration_seconds':len(a)/sr,'sample_rate':sr,'gain':gain,'loudness':meter}
if __name__=='__main__':print(json.dumps(prepare(sys.argv[1],sys.argv[2])))
