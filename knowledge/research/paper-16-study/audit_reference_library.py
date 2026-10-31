"""Read-only provenance and historical-conditioning audit; never relabel old takes."""
from pathlib import Path
import json,importlib.util,hashlib
S=Path(__file__).resolve().parent
def module(name):
 s=importlib.util.spec_from_file_location(name,S/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run():
 lib=module('reference_library');resolve=module('take_references');data=lib.load();lib.validate(data)
 by_hash={r['audio']['sha256']:r['id'] for r in data['references']};out=[]
 for record in json.loads((S/'take-library.json').read_text())['records']:
  row={'take_id':record['id'],'model':record['model'],'bindings':[]}
  try:
   for role,ref in resolve.references(record):
    path=resolve.verified_path(ref);sha=hashlib.sha256(path.read_bytes()).hexdigest()
    row['bindings'].append({'role':role,'canonical_id':by_hash.get(sha),'hash_matches':sha==ref.get('sha256'),'speaker_matches':by_hash.get(sha,'').split(':')[1:2]==[record['speaker']]})
   row['status']='linked' if row['bindings'] and all(x['canonical_id'] and x['hash_matches'] and x['speaker_matches'] for x in row['bindings']) else 'unconditioned' if not row['bindings'] else 'review_required'
  except Exception as e:row['status']='unresolved';row['reason']=str(e)
  out.append(row)
 report={'reference_count':len(data['references']),'focus_speaker':data['focus_speaker'],'focus_references':sum(r['speaker_id']==data['focus_speaker'] for r in data['references']),'integrity':'All source, original and enhanced hashes verified','annotation_gaps':{'intensity':'not supplied','performance_details':'not supplied','human_transcript_review':'not performed','reference_listening_ratings':'not performed'},'historical_takes':out,'summary':{k:sum(r['status']==k for r in out) for k in ['linked','unconditioned','review_required','unresolved']}}
 (S/'reference-library-audit.json').write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':print(json.dumps({k:v for k,v in run().items() if k!='historical_takes'},indent=2))
