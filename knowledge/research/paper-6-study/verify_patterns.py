"""Independent evidence recount from persisted transactions and original edge records."""
import collections,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'paper-6-corpus'
def main():
 data=json.loads((BASE/'patterns/index.json').read_text());assert hashlib.sha256(Path(__file__).with_name('mine_patterns.py').read_bytes()).hexdigest()==data['freeze']['extractorSha256'];full=json.loads((BASE/'patterns/all-rules.json').read_text());saved=json.loads((BASE/'patterns/transactions.json').read_text());transactions=saved['transactions'];families=saved['families'];top=json.loads((BASE/'topology/index.json').read_text())
 assert hashlib.sha256((BASE/'topology/index.json').read_bytes()).hexdigest()==data['freeze']['topologyIndexSha256']
 current=hashlib.sha256(''.join(w['id']+hashlib.sha256((BASE/'topology/graphs'/f"{w['id']}.json").read_bytes()).hexdigest() for w in top['graphs']).encode()).hexdigest()
 assert current==data['freeze']['derivedGraphFilesSha256']
 tmap={t['id']:t for t in transactions};assert len(tmap)==len(transactions);graphs={}
 checked=0
 for summary in full:
  r=json.loads((BASE/'patterns/rules'/f"{summary['id']}.json").read_text());a=json.dumps(r['body'],separators=(',',':'));b=json.dumps(r['head'],separators=(',',':'))
  body={t['id'] for t in transactions if a in t['items']};joint={t for t in body if b in tmap[t]['items']};without=body-joint
  assert len(body)==r['bodyCount'] and len(joint)==r['jointCount'] and len(without)==r['withoutHeadCount']
  assert {w['transaction'] for w in r['examples']}==joint and {w['transaction'] for w in r['withoutHeadExamples']}==without
  assert len(joint)>=5;assert abs(r['confidence']-len(joint)/len(body))<1e-12
  center_n=sum(t['centerType']==r['body'][0] for t in transactions);head_n=sum(b in t['items'] for t in transactions)
  assert abs(r['lift']-r['confidence']/(head_n/center_n))<1e-12
  assert len({families[tmap[t]['graph']] for t in joint})==r['jointFamilyCount']
  for w in r['examples']+r['withoutHeadExamples']:
   if w['graph'] not in graphs:graphs[w['graph']]=json.loads((BASE/'topology/graphs'/f"{w['graph']}.json").read_text())
   g=graphs[w['graph']];assert all(s['sourceUrl'] for s in g['sources']);found=[]
   for e in g['edges']:
    if e['id'] not in w['previewEdgeIds']:continue
    assert w['center'] in [e['source'],e['target']]
    feature=[e['sourceType'],'out',e['targetType'],e['sourcePort'],e['targetPort']] if e['source']==w['center'] else [e['targetType'],'in',e['sourceType'],e['sourcePort'],e['targetPort']]
    found.append(feature)
   assert r['body'] in found
   assert (r['head'] in found)==(w['transaction'] in joint)
   assert len(found)==(2 if w['transaction'] in joint else 1)
   checked+=1
 report={'status':'passed','rulesRecounted':len(full),'witnessPreviewsChecked':checked,'sourceGraphsChecked':len(graphs),'hashes':'topology index and every derived graph file digest matched frozen analysis','limits':'Static count and provenance checks, not independent behavioral evaluation or academic review.'}
 (BASE/'patterns/verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
