"""Pinned, isolated Seed-VC invocation. No transcription/resynthesis fallback."""
from pathlib import Path
import argparse, json, os, subprocess, sys

RUNTIME = Path('/Users/x/.local/share/swarms/seed-vc')
REVISION = '51383efd921027683c89e5348211d93ff12ac2a8'

def convert(source, target, output, seed, settings=None):
    settings = settings or {'steps':30,'cfg':.7,'length_adjust':1.0}
    if type(settings.get('steps')) is not int or not 10<=settings['steps']<=100 or type(settings.get('cfg')) not in (int,float) or not 0<=settings['cfg']<=1 or type(settings.get('length_adjust')) not in (int,float) or not .5<=settings['length_adjust']<=2:
        raise ValueError('Check conversion steps, guidance and length ranges')
    source, target, output = map(Path, (source, target, output))
    if not source.is_file() or not target.is_file():
        raise ValueError('An input recording is missing')
    revision = subprocess.check_output(['git', '-C', str(RUNTIME/'source'), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != REVISION:
        raise ValueError('The tested voice-conversion version has changed')
    output.mkdir(parents=True, exist_ok=True)
    request = {'source': str(source), 'target': str(target), 'output': str(output),
               'seed': int(seed), 'revision': revision, 'steps': settings['steps'], 'cfg': settings['cfg'],
               'length_adjust': settings['length_adjust'], 'f0_condition': False, 'auto_f0_adjust': False}
    request_path = output/'conversion-request.json'
    request_path.write_text(json.dumps(request, indent=2))
    env = {**os.environ, 'PYTORCH_ENABLE_MPS_FALLBACK': '1', 'HF_HUB_DISABLE_TELEMETRY': '1',
           'DO_NOT_TRACK': '1', 'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1'}
    with (output/'conversion.log').open('w') as log:
        result = subprocess.run([str(RUNTIME/'venv/bin/python'), str(Path(__file__).resolve()),
                                 'worker', str(request_path)], cwd=RUNTIME/'source',
                                env=env, stdout=log, stderr=subprocess.STDOUT, timeout=1200)
    if result.returncode:
        raise RuntimeError('Voice conversion failed. Earlier recordings are safe; diagnostic log was saved.')
    files = list(output.glob('vc_*.wav'))
    if len(files) != 1:
        raise RuntimeError('Voice conversion did not produce one unambiguous recording')
    return files[0], request

def worker(path):
    q = json.loads(Path(path).read_text())
    sys.path.insert(0, str(RUNTIME/'source'))
    import random, numpy as np, torch
    random.seed(q['seed']); np.random.seed(q['seed']); torch.manual_seed(q['seed'])
    import inference
    inference.main(argparse.Namespace(source=q['source'], target=q['target'], output=q['output'],
        diffusion_steps=q['steps'], length_adjust=q['length_adjust'], inference_cfg_rate=q['cfg'],
        f0_condition=q['f0_condition'], auto_f0_adjust=q['auto_f0_adjust'], semi_tone_shift=0,
        checkpoint=None, config=None, fp16=False))

if __name__ == '__main__':
    if sys.argv[1] == 'worker': worker(sys.argv[2])
