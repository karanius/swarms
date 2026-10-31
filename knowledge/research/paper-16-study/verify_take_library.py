"""Independent checks of real saved outputs, lineage and preservation."""
from pathlib import Path
import hashlib,json
import numpy as np,soundfile as sf
S=Path(__file__).resolve().parent;ROOT=S.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
data=json.loads((S/'take-library.json').read_text());records=data['records'];ids=[r['id'] for r in records]
assert len(ids)==len(set(ids))
checks=[]
for r in records:
 assert sha(r['path'])==r['sha256'],r['id']
 for field in ('path','listening_path'):
  audio,sr=sf.read(r[field]);assert audio.size and np.isfinite(audio).all() and np.sqrt(np.mean(audio*audio))>1e-6
  assert np.max(np.abs(audio))<=1
 if r.get('parent_id'):assert r['parent_id'] in ids
 checks.append({'id':r['id'],'model':r['model'],'duration_seconds':r['duration_seconds'],'valid_audio':True,'parent_id':r.get('parent_id')})
assert set(r['model'] for r in records)=={'index','vox','f5','dia'}
original=next(r for r in records if r['id']=='initial-index-0')
duration_take=next(r for r in records if r.get('settings',{}).get('duration_scale')==1.2)
ratio=duration_take['duration_seconds']/original['duration_seconds'];assert abs(ratio-1.2)<.1
assert any(r['model']=='index' and r.get('parent_id')=='initial-index-1' and r['settings']['strength']==.8 for r in records)
vox=next(r for r in records if r['model']=='vox' and r.get('parent_id'))
assert vox['settings']['steps']==12
api=json.loads((Path(vox['path']).parent/'api-fields.json').read_text());assert api['num_step']=='12'
for file in (S/'preservation.json',ROOT/'services/audio-workbench/preserved-money.json'):
 for path,digest in json.loads(file.read_text()).items():assert sha(path)==digest,path
report={'records':checks,'all_four_engines_have_real_outputs':True,'originals_intact':True,'duration_scale_observed_ratio':ratio,'changed_vox_steps_sent':12,'paper_1_to_15_unchanged':True,'money_defaults_and_latest_unchanged':True,'perceptual_ratings':None,'limits':'Dia continuation length flagged; no automatic word/identity/emotion validation. Models have different control semantics.'}
(S/'take-controls-verification.json').write_text(json.dumps(report,indent=2))
print('PASS:',len(records),'real takes; all four models; lineage, native edited settings, playable finite audio and preservation checked')
