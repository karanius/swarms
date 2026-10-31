"""Independent validation of produced files; does not trust a passed status label."""
from pathlib import Path
import json,subprocess,re,hashlib,sys
import numpy as np
from PIL import Image
from pipeline import FF,SR,FPS,ROOT,D,sha

def verify(folder):
 folder=Path(folder).resolve();record=json.loads((folder/'run.json').read_text());timeline=json.loads((folder/'timeline.json').read_text());story=json.loads((folder/'story.json').read_text());final=folder/'One Small Light.mp4'
 assert len(timeline)==4 and sha(final)==record['output_sha256']
 result={'passed':False,'full_decode':False,'scenes':[]}
 decoded=subprocess.run([str(FF),'-v','error','-i',str(final),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True,timeout=120)
 assert decoded.returncode==0 and not decoded.stderr.strip(),decoded.stderr
 result['full_decode']=True
 progress=subprocess.run([str(FF),'-v','error','-i',str(final),'-map','0:v:0','-an','-progress','pipe:1','-nostats','-f','null','-'],capture_output=True,text=True,timeout=120)
 assert progress.returncode==0
 frames=[int(x) for x in re.findall(r'^frame=(\d+)$',progress.stdout,re.M)]
 assert frames and frames[-1]==sum(e['frames'] for e in timeline)
 result['decoded_video_frames']=frames[-1]
 def audio(path):
  p=subprocess.run([str(FF),'-v','error','-i',str(path),'-ar',str(SR),'-ac','1','-f','f32le','-'],capture_output=True,timeout=90);assert p.returncode==0
  return np.frombuffer(p.stdout,dtype='<f4')
 mixed=audio(folder/'soundtrack.wav');delivered=audio(final)
 assert abs(len(delivered)/SR-record['duration_seconds'])<.09
 length=min(len(mixed),len(delivered));correlation=float(np.corrcoef(mixed[:length],delivered[:length])[0,1]);assert correlation>.98,correlation
 result['delivery_soundtrack_correlation']=correlation
 assert np.isfinite(delivered).all() and max(abs(delivered))<1
 for i,entry in enumerate(timeline):
  stage=folder/f'audio-{i}';out=json.loads((stage/'outputs.json').read_text());request=json.loads((stage/'request.json').read_text());scene=story['scenes'][i];cast=story['voices'][scene['speaker']]
  cfg=request['ordered'][1]['config'];expected=f"esd:{cast['speaker_id']}:{scene['emotion']}"
  assert cfg['reference']==expected and out['voice']['report']['settings']['reference_audio']==expected
  assert out['voice']['report']['gpu_execution_evidence']['transformer_forward_calls']>0
  assert out['enhance']['report']['inference_evidence']['forward_calls']>0
  assert sha(out['voice']['audio'])==out['master']['report']['source_sha256']==out['master']['report']['original_copy_sha256']
  assert sha(out['master']['audio'])==out['enhance']['report']['source_sha256']==out['enhance']['report']['original_copy_sha256']
  assert sha(entry['audio'])==sha(out['enhance']['audio'])==entry['audio_sha256']
  a=audio(entry['audio']);assert abs(len(a)/SR-(entry['speech_end']-entry['speech_start']))<.001
  start=round(entry['speech_start']*SR);chunk=mixed[start:start+len(a)];difference=float(np.max(abs(chunk-a)));assert difference<.0041,difference
  assert float(np.sqrt(np.mean(a*a)))>.001
  assert entry['speech_start']>=entry['start'] and entry['speech_end']<=entry['start']+entry['duration']
  assert abs(entry['duration']*FPS-entry['frames'])<1e-6
  if i:assert abs(entry['start']-timeline[i-1]['start']-timeline[i-1]['duration'])<1e-6
  # Two observed frames from the final file must differ, proving motion reached delivery.
  frames=[]
  for j,offset in enumerate([entry['duration']*.35,entry['duration']*.65]):
   target=folder/f'verified-frame-{i}-{j}.png'
   p=subprocess.run([str(FF),'-y','-v','error','-ss',str(entry['start']+offset),'-i',str(final),'-frames:v','1',str(target)],capture_output=True);assert p.returncode==0
   im=Image.open(target).convert('RGB');assert im.size==(1280,720);frames.append(np.asarray(im,dtype=np.float32))
  motion=float(np.mean(abs(frames[0]-frames[1])));assert motion>.1,motion
  # Re-read files independently with the preexisting meter/lineage verifier.
  meter=subprocess.run(['/Users/x/.local/share/money/f5-tts/venv/bin/python','-B',str(ROOT/'services/audio-workbench/verify_audio.py'),str(stage)],capture_output=True,text=True,timeout=60);assert meter.returncode==0,meter.stderr
  result['scenes'].append({'speaker':scene['speaker'],'gender':cast['gender'],'intended_emotion':scene['emotion'],'reference':expected,'enhanced_seconds':len(a)/SR,'on_screen_seconds':entry['duration'],'mixed_dialogue_max_difference':difference,'decoded_motion_mean_difference':motion,'lineage_and_independent_meter':True})
 preserved=json.loads((D/'preserved-papers.json').read_text());assert all(sha(path)==digest for path,digest in preserved.items())
 result.update(passed=True,prior_papers_unchanged=True,dialogue_source='enhanced outputs, with a quiet original tone bed',duration_seconds=len(delivered)/SR,output_sha256=sha(final),not_established=['perceived emotional fidelity','perfect pronunciation or speaker consistency','commercial licensing clearance','general video generation','audience appeal'])
 (folder/'independent-verification.json').write_text(json.dumps(result,indent=2)+'\n');return result
