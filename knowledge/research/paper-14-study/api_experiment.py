"""Serialized, auditable native VoiceStudio API experiment. No automatic retries."""
from pathlib import Path
import argparse, hashlib, json, time, wave, contextlib
import numpy as np
import requests

ROOT = Path(__file__).resolve().parent

def generate(name, text, engine='mlx-audio', instruct=None, seed=42, ref_audio=None, ref_text=None, num_step=None):
    out = ROOT / 'runs' / name
    out.mkdir(parents=True, exist_ok=False)
    fields = dict(text=text, engine=engine, seed=str(seed), effect_preset='raw',
                  wav_bits='24', max_chunk_chars='0', pronounce='false')
    if instruct:
        fields['instruct'] = instruct
    if ref_text:
        fields['ref_text'] = ref_text
    if num_step is not None:
        fields['num_step'] = str(num_step)
    recorded=dict(fields)
    if ref_audio:
        recorded['reference']={'path':str(ref_audio),'sha256':hashlib.sha256(Path(ref_audio).read_bytes()).hexdigest()}
    (out/'request.json').write_text(json.dumps(recorded, indent=2))
    started = time.time()
    result = dict(started_unix=started, endpoint='http://127.0.0.1:5196/generate')
    try:
        # Multipart is explicit, matching the upstream endpoint contract.
        with contextlib.ExitStack() as stack:
            files={k:(None,v) for k,v in fields.items()}
            if ref_audio:
                files['ref_audio']=(Path(ref_audio).name,stack.enter_context(open(ref_audio,'rb')),'audio/wav')
            response = requests.post(result['endpoint'], files=files, timeout=(10,900))
        result.update(status=response.status_code, headers=dict(response.headers),
                      elapsed_seconds=time.time()-started)
        if response.status_code != 200:
            (out/'error.txt').write_text(response.text)
            response.raise_for_status()
        audio = out/'native.wav'
        audio.write_bytes(response.content)
        with wave.open(str(audio), 'rb') as wav:
            rate, channels, width = wav.getframerate(), wav.getnchannels(), wav.getsampwidth()
            raw = wav.readframes(wav.getnframes())
        if width == 3:
            triples = np.frombuffer(raw, dtype=np.uint8).reshape(-1,3).astype(np.int32)
            values = triples[:,0] | (triples[:,1]<<8) | (triples[:,2]<<16)
            values = (values ^ 0x800000) - 0x800000
            samples = values.astype(np.float64)/8388608
        elif width in (2,4):
            samples = np.frombuffer(raw, dtype='<i'+str(width)).astype(np.float64)/(2**(8*width-1))
        else:
            raise ValueError('Unsupported PCM width: '+str(width))
        samples = samples.reshape(-1,channels)
        finite = bool(np.isfinite(samples).all())
        result['audio'] = dict(path=str(audio), sha256=hashlib.sha256(response.content).hexdigest(),
            sample_rate=rate, frames=len(samples), channels=samples.shape[1],
            duration_seconds=len(samples)/rate, finite=finite,
            peak=float(np.max(np.abs(samples))), rms=float(np.sqrt(np.mean(samples**2))))
        if not finite or not len(samples) or result['audio']['rms'] < 1e-6:
            raise ValueError('Empty, nonfinite or effectively silent audio')
        result['integrity_passed'] = True
        return result
    except Exception as exc:
        result['error'] = repr(exc)
        raise
    finally:
        result['elapsed_seconds'] = time.time()-started
        (out/'result.json').write_text(json.dumps(result,indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('name'); parser.add_argument('text')
    parser.add_argument('--engine', default='mlx-audio')
    parser.add_argument('--instruct')
    args=parser.parse_args()
    print(json.dumps(generate(args.name,args.text,args.engine,args.instruct),indent=2))
