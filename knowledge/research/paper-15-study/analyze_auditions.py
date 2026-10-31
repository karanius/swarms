"""Signal diagnostics and static-gain listening copies; no emotion scores."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import soundfile as sf
import librosa
sys.path.insert(0,'/Users/x/projects/money/runtimes/f5-tts')
from polish import comparison_measure,match_loudness

STUDY=Path(__file__).resolve().parent
def analyze():
    plan=json.loads((STUDY/'plan.json').read_text());rows=[]
    for condition in plan['conditions']:
        for engine in ('voxcpm2','f5'):
            name=engine+'-'+condition['id'];folder=STUDY/('runs' if engine=='voxcpm2' else 'f5-runs')/name
            if not (folder/'result.json').exists():continue
            result=json.loads((folder/'result.json').read_text())
            if engine=='voxcpm2':
                if not result.get('integrity_passed'):continue
                path=Path(result['audio']['path']);timing=result['elapsed_seconds']
            else:
                if result.get('status')!='passed':continue
                path=Path(result['outputs']['voice']['audio']);timing=result['outputs']['voice']['report']['total_seconds']
            audio,rate=sf.read(path,always_2d=True);mono=audio.mean(axis=1)
            assert np.isfinite(audio).all() and np.sqrt(np.mean(audio**2))>1e-6
            level=comparison_measure(path)
            y=librosa.resample(mono,orig_sr=rate,target_sr=16000)
            # Diagnostic estimate only: amplitude gating is not a speech detector.
            f0=librosa.yin(y,fmin=65,fmax=450,sr=16000,frame_length=1024,hop_length=256)
            rms=librosa.feature.rms(y=y,frame_length=1024,hop_length=256)[0]
            active=rms>max(.005,float(rms.max())*.08)
            pitch=f0[:len(active)][active]
            rows.append(dict(name=name,engine=engine,condition=condition,path=str(path),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),sample_rate=rate,
                duration_seconds=len(audio)/rate,reported_generation_seconds=timing,
                peak=float(np.max(np.abs(audio))),loudness=level,
                low_energy_frame_fraction=float(1-active.mean()),
                estimated_pitch_median_hz=float(np.median(pitch)) if len(pitch) else None,
                estimated_pitch_iqr_hz=float(np.percentile(pitch,75)-np.percentile(pitch,25)) if len(pitch) else None,
                listening_scores=None))
    # A shared conservative level prevents the largest peaks from clipping.
    target=min([-23.0]+[float(r['loudness']['input_i'])-max(0,float(r['loudness']['input_tp'])+1.5) for r in rows])
    target=round(target,1);dest=STUDY/'listening';dest.mkdir(exist_ok=True)
    for row in rows:
        matched=dest/(row['name']+'.wav')
        row['matched_measurement']=match_loudness(row['path'],matched,target,48000)
        row['matched_path']=str(matched);row['matched_target_lufs']=target
        row['matched_sha256']=hashlib.sha256(matched.read_bytes()).hexdigest()
    (STUDY/'analysis.json').write_text(json.dumps(rows,indent=2))
    print(len(rows),'takes measured; listening target',target,'LUFS')

if __name__=='__main__':analyze()
