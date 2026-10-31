"""Launch only the pinned native API; never clear ports or install assets here."""
from pathlib import Path
import os,json,subprocess,sys
D=Path(__file__).resolve().parent;cfg=json.loads((D/'runtime.json').read_text());source=D/'upstream'
revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
if revision!=cfg['revision']:raise SystemExit('Upstream revision differs from the approved manifest')
runtime=Path(cfg['runtime']);runtime.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,OMNIVOICE_DATA_DIR=str(runtime/'data'),OMNIVOICE_CACHE_DIR=str(runtime/'cache'),OMNIVOICE_ENGINES_DIR=str(runtime/'engines'),OMNIVOICE_PORT=str(cfg['port']),OMNIVOICE_BIND_HOST=cfg['host'],OMNIVOICE_TTS_BACKEND=cfg['initial_engine'],OMNIVOICE_MLX_AUDIO_MODEL=cfg['initial_model'],OMNIVOICE_ANALYTICS_DISABLED='1',HF_HUB_DISABLE_TELEMETRY='1',ORT_DISABLE_TELEMETRY='1',ANONYMIZED_TELEMETRY='False',MPLBACKEND='Agg')
# Do not set an HF token, change global caches, or enable remote providers.
env.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
env['AUDIOSEAL_CACHE_DIR'] = str(runtime/'cache')
env['OMNIVOICE_VOXCPM_MODEL'] = str(runtime/'cache/models--openbmb--VoxCPM2/snapshots/32279effe8c19989596f05d353d1447f51d9e915')
env['PYTHONPATH'] = str(D/'instrumentation') + (os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
env['OMNIVOICE_STUDY_VOXCPM_TRACE'] = '1'
os.chdir(source)
os.execve(cfg['python'],[cfg['python'],str(D/'instrumented_server.py')],env)
