"""Run the bounded pilot serially; preserve every completed take and failure."""
from pathlib import Path
import json, subprocess, sys, time, hashlib
from api_experiment import generate

STUDY=Path(__file__).resolve().parent
ROOT=STUDY.parents[2]
MONEY_PYTHON='/Users/x/.local/share/money/f5-tts/venv/bin/python'

def run():
    plan=json.loads((STUDY/'plan.json').read_text())
    ledger=[]
    for condition in plan['conditions']:
        for engine in ('voxcpm2','f5'):
            name=engine+'-'+condition['id']
            folder=STUDY/('runs' if engine=='voxcpm2' else 'f5-runs')/name
            existing=folder/'result.json'
            if existing.exists():
                result=json.loads(existing.read_text())
                passed=result.get('integrity_passed') or result.get('status')=='passed'
                if not passed:
                    ledger.append(dict(name=name,state='preserved_failure'));continue
                ledger.append(dict(name=name,state='preserved_completed'));continue
            print('GENERATE',name,flush=True)
            started=time.time()
            try:
                if engine=='voxcpm2':
                    ref=condition['voxcpm_reference']
                    generate(name,condition['text'],engine=engine,instruct=condition['instruction'],
                             seed=plan['seed'],ref_audio=ref['path'],ref_text=ref['transcript'],num_step=10)
                else:
                    folder.mkdir(parents=True,exist_ok=False)
                    request=dict(text=condition['text'],ordered=[dict(id='text',type='text',config={}),
                        dict(id='voice',type='voice',config=dict(reference=condition['f5_reference']['id'],
                            steps=32,speed=1.0,seed=plan['seed'],cross_fade_duration=.15,
                            cfg_strength=2.0,sway_sampling_coef=-1.0))])
                    (folder/'request.json').write_text(json.dumps(request,indent=2))
                    with (folder/'worker.log').open('w') as log:
                        subprocess.run([MONEY_PYTHON,str(ROOT/'services/audio-workbench/worker.py'),str(folder)],
                                       stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
                    with (folder/'verification.log').open('w') as log:
                        subprocess.run([MONEY_PYTHON,str(ROOT/'services/audio-workbench/verify_audio.py'),str(folder)],
                                       stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30)
                ledger.append(dict(name=name,state='completed',elapsed_seconds=time.time()-started))
                print('COMPLETED',name,flush=True)
            except Exception as exc:
                ledger.append(dict(name=name,state='failed',error=repr(exc),elapsed_seconds=time.time()-started))
                print('FAILED',name,repr(exc),flush=True)
            (STUDY/'execution-ledger.json').write_text(json.dumps(ledger,indent=2))
    (STUDY/'execution-ledger.json').write_text(json.dumps(ledger,indent=2))

if __name__=='__main__':run()
