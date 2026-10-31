"""Adapter around the existing pinned F5 runtime. Outputs remain in Paper 12."""
import os,sys,json,importlib.util
from pathlib import Path
os.environ['MPLBACKEND']='Agg'
os.environ.update(HF_HUB_OFFLINE='1',HF_DATASETS_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1')
RUNTIME=Path('/Users/x/.local/share/money/f5-tts');SOURCE=Path('/Users/x/projects/money/runtimes/f5-tts')
os.environ['F5_RUNTIME_ROOT']=str(RUNTIME)
sys.path.insert(0,str(SOURCE))
spec=importlib.util.spec_from_file_location('p12_f5_adapter',SOURCE/'generate.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
# This adapter reuses source in place; never changes the other project's config/latest pointer.
module.PROJECT=Path(sys.argv[2]).resolve();module.PROJECT.mkdir(parents=True,exist_ok=True)
(module.PROJECT/'models.lock.json').write_bytes((SOURCE/'models.lock.json').read_bytes())
cfg=module.settings(SOURCE/'config.toml')
cfg.update(reference_audio='bundled',reference_text='Some call me nature, others call me mother nature.',text=Path(sys.argv[1]).read_text(),steps=16)
audio,result=module.generate(cfg,publish_latest=False)
Path(sys.argv[3]).write_text(json.dumps({'audio':audio,'evidence':result,'adapter_source':str(SOURCE/'generate.py'),'reference':'Bundled upstream research sample; no commercial voice/license clearance claimed.'},indent=2)+'\n')
