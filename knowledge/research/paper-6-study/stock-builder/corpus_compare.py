"""Exact recorded wiring comparison, not purpose/safety validation."""
import json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent;CORPUS=BASE.parent.parent/'paper-6-corpus'
def analyze(flow):
 data=flow['data'];nodes={n['id']:n['data']['type'] for n in data['nodes']};transactions=json.load(open(CORPUS/'patterns/transactions.json'))['transactions'];index=json.load(open(CORPUS/'topology/index.json'));graphs={g['id']:g for g in index['graphs']};edge_features=[]
 for e in data['edges']:
  sh=e['data']['sourceHandle'];th=e['data']['targetHandle'];edge_features.append((e['id'],nodes[e['source']],sh['name'],nodes[e['target']],th['fieldName']))
 queries=[]
 def row(label,matched):
  ids=sorted(matched);examples=[]
  for gid in ids[:5]:
   g=graphs[gid];examples.append({'graphId':gid,'name':g['name'],'source':g.get('source'),'fileContentSha256':g.get('sha256')})
  return {'query':label,'matchingDistinctGraphObjects':len(ids),'supportingGraphIds':ids,'examples':examples,'meaning':'Exact recorded feature occurrence, not independent designs or useful composite evidence'}
 for eid,st,sp,tt,tp in edge_features:
  support=set()
  for t in transactions:
   for feature in t['items']:
    c,d,n,s,o=json.loads(feature);sig=(c,s,n,o) if d=='out' else (n,s,c,o)
    if sig==(st,sp,tt,tp):support.add(t['graph'])
  queries.append(row({'edgeId':eid,'sourceType':st,'sourcePort':sp,'targetType':tt,'targetPort':tp},support))
 neighborhoods=[]
 for nid,typ in nodes.items():
  items=set()
  for e in data['edges']:
   if nid not in (e['source'],e['target']):continue
   out=e['source']==nid;sh=e['data']['sourceHandle'];th=e['data']['targetHandle'];neighbor=nodes[e['target'] if out else e['source']]
   items.add(json.dumps([typ,'out' if out else 'in',neighbor,sh['name'],th['fieldName']],separators=(',',':')))
  if len(items)>=2:
   support={t['graph'] for t in transactions if t['centerType']==typ and items<=set(t['items'])};neighborhoods.append(row({'centerNode':nid,'centerType':typ,'allIncidentFeatureItems':sorted(items),'rule':'all generated incident signatures coexist at one recorded center'},support))
 return {'edges':queries,'neighborhoods':neighborhoods,'corpusTransactionSha256':hashlib.sha256((CORPUS/'patterns/transactions.json').read_bytes()).hexdigest(),'scope':'Existing frozen descriptive nonfixture neighborhood dataset; exact type/port spellings, no alias expansion','limits':['Frequency is not correctness or requirement fulfillment','Mirrors/related examples may remain; graph objects are not independent designs','No new rules learned, no guidance intervention or performance claim']}
if __name__=='__main__':
 run=BASE/json.load(open(BASE/'latest.json'))['run'];result=analyze(json.load(open(run/'flow.json')));(BASE/'first-corpus-comparison.json').write_text(json.dumps(result,indent=2));print([(x['query']['sourceType'],x['query']['targetType'],x['matchingDistinctGraphObjects']) for x in result['edges']]);print([(x['query']['centerType'],x['matchingDistinctGraphObjects']) for x in result['neighborhoods']])
