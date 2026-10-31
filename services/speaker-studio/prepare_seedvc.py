"""Explicit, resumable model preparation. Inference itself stays offline."""
from pathlib import Path
import hashlib,json,shutil,subprocess
RUNTIME=Path('/Users/x/.local/share/swarms/seed-vc/source')
ASSETS=json.loads(Path(__file__).with_name('seedvc-assets.json').read_text())
LOCAL={'campplus_cn_common.bin':RUNTIME/'campplus_cn_common.bin',
       'bigvgan_generator.pt':Path('/Users/x/.local/share/swarms/indextts-paper16/checkpoints/hf_cache/bigvgan/bigvgan_generator.pt')}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare():
 for a in ASSETS:
  root=RUNTIME/a['cache']/('models--'+a['repo'].replace('/','--'))
  blob=root/'blobs'/a['blob'];blob.parent.mkdir(parents=True,exist_ok=True)
  valid=lambda p:p.is_file() and p.stat().st_size==a['size'] and (not a['sha256'] or sha(p)==a['sha256'])
  if not valid(blob):
   local=LOCAL.get(a['file'])
   if local and valid(local):shutil.copyfile(local,blob)
   else:
    part=blob.with_suffix('.incomplete')
    print('Downloading '+a['repo']+'/'+a['file']+' ('+str(a['size'])+' bytes)',flush=True)
    subprocess.run(['curl','--fail','--location','--retry','2','--connect-timeout','20','--max-time','900',
      '--continue-at','-','--output',str(part),'https://huggingface.co/'+a['repo']+'/resolve/'+a['revision']+'/'+a['file']],check=True)
    if not valid(part):raise RuntimeError('Downloaded asset failed integrity verification: '+a['file'])
    part.replace(blob)
  target=root/'snapshots'/a['revision']/a['file'];target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():target.symlink_to(blob)
  (root/'refs').mkdir(exist_ok=True);(root/'refs/main').write_text(a['revision'])
  print('Verified '+a['repo']+'/'+a['file'],flush=True)
if __name__=='__main__':prepare()
