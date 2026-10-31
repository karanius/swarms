"""Resolve recorded references, never pending editor selections."""
from pathlib import Path
import json,hashlib
S=Path(__file__).resolve().parent

def references(record):
 model=record['model'];settings=record.get('applied_settings',record.get('settings',{}))
 if model=='dia' and not settings.get('use_reference',True):return []
 if 'reference_bindings' in record:
  roles={'identity':'Voice identity reference','emotion':'Emotion reference','performance':'Source reference'}
  return [(roles[b['role']],b) for b in record['reference_bindings']]
 if model=='index':
  folder=Path(record.get('native_run',Path(record['path']).parent))
  result=folder/'result.json'
  if not result.exists():raise ValueError('Original reference manifest is unavailable')
  refs=json.loads(result.read_text())['request']['references']
  return [('Voice identity reference',refs['neutral']),('Emotion reference',refs[record['emotion']])]
 ref=record.get('reference')
 if ref is None and record['id'].startswith('initial-vox-'):
  source=json.loads((S.parent/'paper-15-study/reference-guidance-analysis.json').read_text())
  condition=next(c for c in source['conditions'] if ('anger' if c['condition']=='angry-reference' else 'neutral')==record['emotion'])
  ref={**condition['request']['reference'],'transcript':condition['request']['ref_text']}
 if not ref:raise ValueError('This recording has no saved reference metadata')
 return [('Source reference',ref)]

def verified_path(ref):
 path=Path(ref['path'])
 if not path.is_file():raise ValueError('Saved reference file is missing')
 if ref.get('sha256') and hashlib.sha256(path.read_bytes()).hexdigest()!=ref['sha256']:raise ValueError('Reference file differs from the saved generation manifest')
 return path
