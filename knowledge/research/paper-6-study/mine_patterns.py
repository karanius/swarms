"""Bounded descriptive association mining of scoped observed edge neighborhoods.
All downloaded workflows are treated as data. No node code or model is executed.
"""
import collections,hashlib,itertools,json,platform,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'paper-6-corpus'
CONFIG={'minimumJointNeighborhoods':5,'maxItemsetSize':2,'maximumDistinctIncidentFeatures':24,'maximumDisplayedRules':1000,'scope':'all nonfixture extracted graphs; descriptive exploration; no held-out evaluation','absence':'no matching recorded incident edge in an assessable saved neighborhood; not a behavioral negative'}
def key(v):return json.dumps(v,separators=(',',':'),ensure_ascii=True)
def sha(v):return hashlib.sha256(key(v).encode()).hexdigest()
class Union:
 def __init__(self):self.p={}
 def find(self,x):
  self.p.setdefault(x,x)
  if self.p[x]!=x:self.p[x]=self.find(self.p[x])
  return self.p[x]
 def join(self,a,b):
  a,b=self.find(a),self.find(b)
  if a!=b:self.p[max(a,b)]=min(a,b)
def family_groups(graphs):
 u=Union()
 for g in graphs:
  repos=sorted({s.get('repository') or s.get('sourceUrl') for s in g['sources']})
  for r in repos:u.find(r)
  for r in repos[1:]:u.join(repos[0],r)
 return {g['id']:sha(u.find(g['sources'][0].get('repository') or g['sources'][0]['sourceUrl']))[:16] for g in graphs}
def neighborhoods(graph):
 nodes={n['id']:n for n in graph['nodes']};incident=collections.defaultdict(list)
 for e in graph['edges']:
  incident[e['source']].append(e)
  if e['target']!=e['source']:incident[e['target']].append(e)
 accepted=[];excluded=collections.Counter()
 for nid,n in nodes.items():
  edges=incident[nid]
  if not edges:excluded['no-recorded-incident-edge']+=1;continue
  bad=[];features=collections.defaultdict(list)
  for e in edges:
   if not e['resolved'] or not e['sourcePort'] or not e['targetPort'] or e['sourceType'] in [None,'Unknown'] or e['targetType'] in [None,'Unknown']:
    bad.append(e['id']);continue
   if e['source']==e['target']:bad.append(e['id']);continue
   direction='out' if e['source']==nid else 'in';neighbor=e['targetType'] if direction=='out' else e['sourceType']
   feature=(n['type'],direction,neighbor,e['sourcePort'],e['targetPort'])
   features[key(feature)].append(e['id'])
  if bad:excluded['unknown-endpoint-type-port-or-self-loop']+=1;continue
  if len(features)>CONFIG['maximumDistinctIncidentFeatures']:excluded['neighborhood-size-bound']+=1;continue
  accepted.append({'id':sha([graph['id'],nid])[:24],'graph':graph['id'],'center':nid,'centerType':n['type'],'items':sorted(features),'edgeWitnesses':dict(features)})
 return accepted,excluded

def score_rule(a,b,inv,tx,families,total):
 body=set(inv[a]);joint=body&set(inv[b]);absent=body-set(inv[b]);fjoint={families[tx[i]['graph']] for i in joint};fbody={families[tx[i]['graph']] for i in body}
 center=json.loads(a)[0];center_n=sum(t['centerType']==center for t in tx);head_n=len(inv[b])
 return {'id':sha([a,b])[:24],'body':json.loads(a),'head':json.loads(b),'bodyKey':a,'headKey':b,'bodyCount':len(body),'jointCount':len(joint),'withoutHeadCount':len(absent),'headCount':head_n,'transactionCount':total,'centerTypeNeighborhoods':center_n,'support':len(joint)/total,'centerSupport':len(joint)/center_n,'confidence':len(joint)/len(body),'lift':(len(joint)/len(body))/(head_n/center_n),'bodyGraphCount':len({tx[i]['graph'] for i in body}),'jointGraphCount':len({tx[i]['graph'] for i in joint}),'jointFamilyCount':len(fjoint),'bodyFamilyCount':len(fbody),'joint':sorted(joint),'withoutHead':sorted(absent)}
def prioritize(ids,tx,families):
 # Spread early examples over recorded provenance groups; retain every witness.
 groups=collections.defaultdict(list)
 for i in ids:groups[families[tx[i]['graph']]].append(i)
 order=[]
 while groups:
  for f in sorted(list(groups)):
   order.append(groups[f].pop(0))
   if not groups[f]:del groups[f]
 return order

def main():
 import pandas as pd,mlxtend
 from mlxtend.preprocessing import TransactionEncoder
 from mlxtend.frequent_patterns import fpgrowth,association_rules
 start=time.perf_counter();index_bytes=(BASE/'topology/index.json').read_bytes();index=json.loads(index_bytes)
 graph_bytes=[(w['id'],(BASE/'topology/graphs'/f"{w['id']}.json").read_bytes()) for w in index['graphs']]
 allgraphs=[json.loads(content) for _,content in graph_bytes]
 graph_digest=hashlib.sha256(''.join(gid+hashlib.sha256(content).hexdigest() for gid,content in graph_bytes).encode()).hexdigest()
 families=family_groups(allgraphs);graphs=[g for g in allgraphs if not g['fixture']];tx=[];excluded=collections.Counter();graphmeta={g['id']:g for g in graphs}
 for g in graphs:
  nts,skip=neighborhoods(g);tx.extend(nts);excluded.update(skip)
 if len(tx)<CONFIG['minimumJointNeighborhoods']:raise ValueError('Insufficient assessable neighborhoods')
 inv=collections.defaultdict(list)
 for i,t in enumerate(tx):
  for item in t['items']:inv[item].append(i)
 encoder=TransactionEncoder();matrix=encoder.fit([t['items'] for t in tx]).transform([t['items'] for t in tx],sparse=True)
 df=pd.DataFrame.sparse.from_spmatrix(matrix,columns=encoder.columns_)
 # epsilon avoids dropping exact threshold counts through binary rounding.
 frequent=fpgrowth(df,min_support=(CONFIG['minimumJointNeighborhoods']-.000001)/len(tx),use_colnames=True,max_len=2)
 learned=association_rules(frequent,metric='confidence',min_threshold=0.0,num_itemsets=len(tx))
 rules=[]
 for row in learned.itertuples():
  if len(row.antecedents)!=1 or len(row.consequents)!=1:continue
  a=next(iter(row.antecedents));b=next(iter(row.consequents));r=score_rule(a,b,inv,tx,families,len(tx))
  assert r['body'][0]==r['head'][0]
  assert r['jointCount']>=CONFIG['minimumJointNeighborhoods']
  assert abs(row.confidence-r['confidence'])<1e-10
  # mlxtend's global lift uses all center types; expose center-conditioned lift instead.
  r['globalLift']=float(row.lift)
  r['joint']=prioritize(r['joint'],tx,families);r['withoutHead']=prioritize(r['withoutHead'],tx,families)
  rules.append(r)
 rules.sort(key=lambda r:(-r['jointFamilyCount'],-r['jointGraphCount'],-r['jointCount'],-r['confidence'],r['id']))
 output=BASE/'patterns';(output/'rules').mkdir(parents=True,exist_ok=True)
 def witness(i,r):
  t=tx[i];g=graphmeta[t['graph']];edgeids=t['edgeWitnesses'].get(r['bodyKey'],[])+t['edgeWitnesses'].get(r['headKey'],[])
  return {'transaction':t['id'],'graph':t['graph'],'center':t['center'],'name':g['name'],'family':families[t['graph']],'edgeIds':sorted(set(edgeids)),'previewEdgeIds':sorted(set([t['edgeWitnesses'][r['bodyKey']][0]]+([t['edgeWitnesses'][r['headKey']][0]] if r['headKey'] in t['edgeWitnesses'] else []))),'source':g['sources'][0]['sourceUrl'],'repository':g['sources'][0].get('repository'),'sourceCount':len(g['sources'])}
 catalog=[]
 for r in rules:
  compact={k:v for k,v in r.items() if k not in ['bodyKey','headKey','joint','withoutHead']}
  compact['examples']=[witness(i,r) for i in r['joint']]
  compact['withoutHeadExamples']=[witness(i,r) for i in r['withoutHead']]
  (output/'rules'/f"{r['id']}.json").write_text(json.dumps(compact,separators=(',',':')))
  if len(catalog)<CONFIG['maximumDisplayedRules']:
   catalog.append({k:v for k,v in compact.items() if k not in ['examples','withoutHeadExamples']}|{'representative':compact['examples'][0]})
 # Preserve the complete result set, not only the UI ranking.
 allrules=[{k:v for k,v in r.items() if k not in ['bodyKey','headKey','joint','withoutHead']} for r in rules]
 (output/'all-rules.json').write_text(json.dumps(allrules,separators=(',',':')))
 groups=collections.Counter(families[g['id']] for g in graphs)
 stats={'nonfixtureGraphs':len(graphs),'componentOccurrences':sum(len(g['nodes']) for g in graphs),'assessableNeighborhoods':len(tx),'excludedNeighborhoods':dict(excluded),'distinctFeatures':len(inv),'frequentItemsets':len(frequent),'repeatedConnectedPairs':sum(len(x)==2 for x in frequent.itemsets),'directedAssociationRules':len(rules),'displayedRules':len(catalog),'recordedSourceGroups':len(groups),'largestGroupGraphs':max(groups.values()),'runtimeSeconds':round(time.perf_counter()-start,3)}
 freeze={'derivedGraphFilesSha256':graph_digest,'topologyIndexSha256':hashlib.sha256(index_bytes).hexdigest(),'corpusIndexSha256':index['indexSha256'],'extractorSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'python':platform.python_version(),'mlxtend':mlxtend.__version__,'pandas':pd.__version__,'config':CONFIG}
 result={'schemaVersion':1,'stats':stats,'freeze':freeze,'rules':catalog,'limits':['Exploratory whole-corpus counts; no held-out evaluation or generalization claim.','Known ports here means named saved-edge handles, not declared-port membership, activation or type compatibility.','Neighborhoods with any unknown incident port/type/endpoint, self-loop, or more than 24 features are excluded; selection bias is reported.','Connections are observed saved edges, not validated active outputs or behavior.','Two features share the same center occurrence; their outside neighbor may be shared (two-node pattern) or distinct (three-node pattern).','Source groups union repository identities and all origins of byte-identical files, including fixture origins. They do not prove independent sources or catch every modified copy.','Global lift is confounded by center type; the UI shows lift conditioned on the common center type.','No automatic composites, configuration inference, AnyBURL, PyClause or evolutionary execution in this study.']}
 (output/'index.json').write_text(json.dumps(result,separators=(',',':')))
 (output/'transactions.json').write_text(json.dumps({'freeze':freeze,'transactions':tx,'families':families},separators=(',',':')))
 print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
