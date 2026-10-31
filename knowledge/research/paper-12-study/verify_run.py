"""Independent artifact checks; does not trust the producer's passed label."""
from pathlib import Path
import json,subprocess,hashlib,re,math,wave,array
from PIL import Image,ImageChops,ImageStat
from pipeline import FF,validate_plan,captions,digest

def verify(folder):
 folder=Path(folder).resolve();record=json.loads((folder/'run.json').read_text());plan=validate_plan(json.loads((folder/'plan.json').read_text()));final=folder/'final.mp4'
 if digest(final)!=record['output_sha256']:raise ValueError('Final hash mismatch')
 decode=subprocess.run([str(FF),'-v','error','-i',str(final),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True,timeout=90)
 if decode.returncode or decode.stderr.strip():raise ValueError('Independent full decode failed: '+decode.stderr)
 durations=[];rms=[];gpu=[];similarities=[]
 for i,scene in enumerate(plan['scenes']):
  report=json.loads((folder/f'tts-{i}.json').read_text());audio=Path(report['audio'])
  if not audio.resolve().is_relative_to(folder):raise ValueError('Audio outside run')
  if digest(audio)!=report['evidence']['audio_sha256']:raise ValueError('Audio hash mismatch')
  with wave.open(str(audio)) as f:
   durations.append(f.getnframes()/f.getframerate());samples=array.array('h',f.readframes(f.getnframes()))
  level=math.sqrt(sum(v*v for v in samples)/len(samples))/32768;rms.append(level)
  if level<.001:raise ValueError('Silent output')
  evidence=report['evidence']['gpu_execution_evidence'];gpu.append(evidence['transformer_forward_calls'])
  if not evidence['transformer_forward_calls'] or not any('mps' in x for x in evidence['observed_parameter_devices']):raise ValueError('Neural MPS execution not observed')
  sample=folder/f'playback-frame-{i}.png'
  with Image.open(sample).convert('RGB') as actual,Image.open(folder/f'scene-{i}.png').convert('RGB') as expected:
   diff=ImageChops.difference(actual,expected);mse=sum(v*v for v in ImageStat.Stat(diff).rms)/3;psnr=99 if mse==0 else 10*math.log10(255*255/mse);similarities.append(psnr)
   if psnr<25:raise ValueError('Decoded scene does not match generated illustration/caption')
 if (folder/'captions.srt').read_text()!=captions(plan['scenes'],durations):raise ValueError('Caption text/timing differs from measured scene audio')
 result={'independent_full_decode':True,'output_sha256':digest(final),'scene_audio_seconds':durations,'audio_rms':rms,'observed_transformer_calls':gpu,'decoded_scene_psnr_db':similarities,'captions_match_generated_text_and_audio_boundaries':True,'not_proven':['speech pronunciation/naturalness','word-level synchronization','commercial rights','general video generation','OS network isolation']}
 (folder/'independent-verification.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 import sys
 print(json.dumps(verify(sys.argv[1]),indent=2))
