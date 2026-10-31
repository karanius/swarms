import json,pathlib,hashlib,collections
p=pathlib.Path(__file__).parent;d=json.loads((p/'manifest.json').read_text());bad=[];counts=collections.Counter()
def hints(j):
 if isinstance(j,dict):
  if 'last_tested_version' in j or 'endpoint_name' in j:return True
  if isinstance(j.get('nodes'),list):
   for n in j['nodes']:
    nd=n.get('data',{}) if isinstance(n,dict) else {}
    if isinstance(nd,dict) and isinstance(nd.get('node'),dict) and ('template' in nd['node'] or 'base_classes' in nd['node']):return True
  return any(hints(v) for v in j.values() if isinstance(v,(dict,list)))
 if isinstance(j,list):return any(hints(v) for v in j)
 return False
for a in d['artifacts']:
 b=(p/a['file']).read_bytes()
 if hashlib.sha256(b).hexdigest()!=a['sha256']:bad.append(a['file'])
 a['langflowSchemaEvidence']='langflow-export-metadata-or-node-template' if hints(json.loads(b)) else 'generic-node-edge-graph-needs-review'
 a['sourceFamily']='ACRT-EVAL-derived-repository' if a['repository'].startswith('ACRT-EVAL/') else 'community-origin-or-mirror-unresolved'
 counts[a['langflowSchemaEvidence']]+=1
(p/'manifest.json').write_text(json.dumps(d,indent=2))
(p/'byte-integrity.json').write_text(json.dumps({'artifactsChecked':len(d['artifacts']),'sha256Mismatches':bad,'schemaEvidenceCounts':counts},indent=2))
print('Checked',len(d['artifacts']),'mismatches',len(bad),'schema',dict(counts))
