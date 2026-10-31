"""Independent recount of saved rule experiment artifacts and source evidence.
Does not import the learning, masking, proposal or scoring implementation.
"""
import collections,hashlib,json,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'knowledge/research/paper-6-corpus';OUT=BASE/'relational'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 summary=read(OUT/'summary.json');source=(BASE/'patterns/transactions.json').read_bytes();d=json.loads(source);assert sha(source)==summary['freeze']['transactionsSha256'];cfg=summary['config'];tx=d['transactions'];families=d['families']
 assert sha((Path(__file__).parent/'relational_experiment.py').read_bytes())==summary['freeze']['implementationSha256'];assert sha((Path(__file__).parent/'RELATIONAL-PROTOCOL.md').read_bytes())==summary['freeze']['protocolSha256']
 ev=lambda t:int(sha((cfg['splitSalt']+families[t['graph']]).encode())[:8],16)%cfg['evaluationModulo']==cfg['evaluationBucket']
 train=[t for t in tx if not ev(t)];evaluation=[t for t in tx if ev(t)];trainids={t['id'] for t in train};fgtrain={families[t['graph']] for t in train};fgeval={families[t['graph']] for t in evaluation};assert not(fgtrain&fgeval)
 byid={t['id']:t for t in tx};graphs={};source_witnesses=0
 # Rebuild every transaction's saved features without trusting its item/witness lists.
 for t in tx:
  if t['graph'] not in graphs:graphs[t['graph']]=read(BASE/'topology/graphs'/f"{t['graph']}.json")
  g=graphs[t['graph']];n=next(n for n in g['nodes'] if n['id']==t['center']);features=collections.defaultdict(list)
  for e in g['edges']:
   if e['source']!=n['id'] and e['target']!=n['id']:continue
   assert e['resolved'] and e['sourcePort'] and e['targetPort'] and e['source']!=e['target']
   direction='out' if e['source']==n['id'] else 'in';neighbor=e['targetType'] if direction=='out' else e['sourceType'];f=json.dumps([n['type'],direction,neighbor,e['sourcePort'],e['targetPort']],separators=(',',':'),ensure_ascii=True);features[f].append(e['id']);source_witnesses+=1
  assert set(features)==set(t['items']);assert dict(features)==t['edgeWitnesses']
 # Verify combined derived-graph digest against the earlier frozen input.
 idx=read(BASE/'topology/index.json');combined=''
 for g in idx['graphs']:
  b=(BASE/'topology/graphs'/f"{g['id']}.json").read_bytes();combined+=g['id']+sha(b)
 assert sha(combined.encode())==d['freeze']['derivedGraphFilesSha256']
 assert sha((OUT/'train-features.tsv').read_bytes())==summary['freeze']['trainingFactsSha256']
 rules=read(OUT/'rules.json');exact=read(OUT/'exact-rules.json');vocab=read(OUT/'vocabulary.json');ruleids={r['id']:r for r in rules};checked=0
 for r in [*rules,*exact]:
  body=[t for t in train if r['body'] in t['items']];joint=[t for t in body if r['head'] in t['items']];heads=[t for t in train if r['head'] in t['items']];center=json.loads(r['body'])[0];pop=[t for t in train if t['centerType']==center]
  assert len(body)==r['bodyCount'] and len(joint)==r['jointCount'] and len(heads)==r['headCount'] and len(pop)==r['centerCount']
  conf=len(joint)/len(body);lift=conf/(len(heads)/len(pop));assert math.isclose(conf,r['confidence']) and math.isclose(lift,r['centerLift']);assert r['trainingExamples']==[t['id'] for t in joint]
  groups={families[t['graph']] for t in joint};assert len(groups)==r['jointFamilies'];assert len(joint)>=cfg['minimumJoint'] and len(groups)>=cfg['minimumSourceGroups'] and conf>=cfg['minimumConfidence'] and lift>=cfg['minimumCenterLift']
  assert all(t['id'] in trainids for t in joint)
  if 'clause' in r:
   m=re.fullmatch(r'has_feature\(([XY]),(f[a-f0-9]{24})\) <= has_feature\(([XY]),(f[a-f0-9]{24})\)',r['clause']);assert m and m[1]==m[3] and vocab[m[2]]==r['head'] and vocab[m[4]]==r['body']
  checked+=1
 # Independently enumerate training pairs and reproduce the bounded guidance ranking.
 paircounts=collections.defaultdict(list)
 for t in train:
  items=sorted(set(t['items']))
  for i,a in enumerate(items):
   for b in items[i+1:]:paircounts[(a,b)].append(t)
 eligible=[]
 for pair,ts in paircounts.items():
  if len(ts)>=cfg['minimumJoint']:eligible.append({'pair':list(pair),'neighborhoods':len(ts),'graphs':len({t['graph'] for t in ts}),'families':len({families[t['graph']] for t in ts})})
 eligible.sort(key=lambda r:(-r['families'],-r['graphs'],-r['neighborhoods'],json.dumps(r['pair'],separators=(',',':'),ensure_ascii=True)));assert read(OUT/'guidance.json')==eligible[:cfg['guidedPairs']]
 cases=read(OUT/'cases.json');expected=[]
 for t in evaluation:
  if len(t['items'])<2:continue
  f=min(t['items'],key=lambda x:sha((t['id']+':'+x).encode()));expected.append((t['id'],f))
 expected=sorted(expected,key=lambda p:sha(p[0].encode()))[:cfg['maximumCases']];assert [(c['id'],c['target']) for c in cases]==expected
 for c in cases:
  t=byid[c['id']];assert c['graph']==t['graph'] and c['center']==t['center'] and c['centerType']==t['centerType'] and c['family']==families[t['graph']] and c['entity']=='o'+t['id'];assert ev(t) and c['visible']==[f for f in t['items'] if f!=c['target']];assert c['target'] not in c['visible']
 predictions=read(OUT/'predictions.json');guide={tuple(x['pair']) for x in eligible[:cfg['guidedPairs']]};arms={'anyburl':rules,'association_guided':[r for r in rules if tuple(sorted([r['body'],r['head']])) in guide],'exact_counting':exact}
 for name,rs in arms.items():
  rows=predictions[name];assert len(rows)==len(cases)
  for c,row in zip(cases,rows):
   scores={}
   for r in rs:
    if r['body'] in c['visible'] and r['head'] not in c['visible']:scores[r['head']]=max(scores.get(r['head'],0),r['confidence'])
   rank=sorted(scores,key=lambda x:(-scores[x],x));top=rank[0] if rank else None
   assert row['prediction']==top and row['recovered']==(top==c['target']) and row['answers']==len(rank)
  m=summary['metrics'][name];assert sum(r['recovered'] for r in rows)==m['recovered'];assert sum(r['prediction'] is not None for r in rows)==m['answered']
 # Baseline and every reported denominator are independently reconstructed.
 center_counts=collections.defaultdict(collections.Counter);center_population=collections.Counter()
 for t in train:center_counts[t['centerType']].update(set(t['items']));center_population[t['centerType']]+=1
 for c,row in zip(cases,predictions['center_frequency']):
  count=center_counts[c['centerType']];rank=sorted((f for f in count if f not in c['visible']),key=lambda f:(-count[f],f));assert row['prediction']==(rank[0] if rank else None);assert row['recovered']==(row['prediction']==c['target']);assert row['answers']==len(rank)
 for name,rows in predictions.items():
  m=summary['metrics'][name];hits=sum(r['recovered'] for r in rows);answered=sum(r['prediction'] is not None for r in rows);groups=collections.defaultdict(list)
  assert len(rows)==len(cases)
  for c,r in zip(cases,rows):assert r['case']==c['id'] and r['target']==c['target'];groups[c['family']].append(int(r['recovered']))
  expected={'cases':len(cases),'answered':answered,'recovered':hits,'coverage':answered/len(cases),'recoveryPerCase':hits/len(cases),'recoveryPerAnswer':hits/answered if answered else None,'familyMacroRecovery':sum(sum(v)/len(v) for v in groups.values())/len(groups),'families':len(groups)}
  for k,v in expected.items():assert m[k]==v,(name,k,m[k],v)
 for run in [*summary['learning']['runs'],summary['learning']['wireProbe']]:
  if run.get('ruleFile'):assert sha((ROOT/run['ruleFile']).read_bytes())==run['ruleFileSha256']
  else:assert run['status']=='infrastructure-failure' and (ROOT/run['log']).exists()
 # Inspect proposals against training-only source descriptors and exact edge-role signatures.
 proposals=read(OUT/'proposals.json');cby={c['id']:c for c in cases};proposal_checks=0;exposures=0
 for p in proposals:
  assert p['case'] in cby
  if p['status']!='proposal-only':continue
  assert len({n['id'] for n in p['nodes']})==3 and len(p['edges'])==2
  for n in p['nodes']:
   assert n['graph'] in {t['graph'] for t in train};g=graphs[n['graph']];source_node=next(x for x in g['nodes'] if x['id']==n['node']);assert n['descriptor']=={k:source_node.get(k,[]) for k in ['type','version','inputs','outputs','resourceRequirements']};assert n['sources']==g['sources']
  nodes={n['id']:n['descriptor'] for n in p['nodes']};incoming={(e['target'],e['targetPort']) for e in p['edges']};required={(i,pin['name']) for i,n in nodes.items() for pin in n['inputs'] if pin.get('required') and (i,pin['name']) not in incoming};assert {(x['node'],x['field']) for x in p['requiredExposures']}==required;exposures+=len(required)
  for e in p['edges']:
   assert e['source']!=e['target'];src=nodes[e['source']];tgt=nodes[e['target']];assert any(o['name']==e['sourcePort'] for o in src['outputs']);assert any(i['name']==e['targetPort'] for i in tgt['inputs'])
  features=[]
  for e in p['edges']:
   if e['source']=='center':f=[nodes['center']['type'],'out',nodes[e['target']]['type'],e['sourcePort'],e['targetPort']]
   else:f=[nodes['center']['type'],'in',nodes[e['source']]['type'],e['sourcePort'],e['targetPort']]
   features.append(json.dumps(f,separators=(',',':'),ensure_ascii=True))
  c=cby[p['case']];assert features[0] in c['visible'] and features[1]==p['prediction'];assert any(ruleids[r]['body']==features[0] and ruleids[r]['head']==features[1] for r in p['ruleIds'])
  judgments=[]
  for e,check in zip(p['edges'],p['typeChecks']):
   o=next(x for x in nodes[e['source']]['outputs'] if x['name']==e['sourcePort']);i=next(x for x in nodes[e['target']]['inputs'] if x['name']==e['targetPort']);ot=set(o.get('types',[]));it=set(i.get('types',[]));judgment='declared-label-overlap' if ot&it else 'unknown' if not ot or not it else 'declared-label-conflict';assert check['judgment']==judgment and check['outputTypes']==sorted(ot) and check['inputTypes']==sorted(it);judgments.append(judgment)
  assert p['structuralChecks']=={'connected':True,'acyclic':True,'portsDeclared':True,'allKnownTypesOverlap':all(j=='declared-label-overlap' for j in judgments)}
  resources=[{'node':n['id'],**r,'judgment':'binding unknown; no values read'} for n in p['nodes'] for r in n['descriptor']['resourceRequirements']];assert p['resources']==resources
  assert p['purpose'].startswith('unresolved');proposal_checks+=1
 result={'status':'passed','recountedRulesIncludingBaseline':checked,'reconstructedTransactions':len(tx),'checkedIncidentWitnesses':source_witnesses,'sourceGraphs':len(graphs),'verifiedCases':len(cases),'proposalSpecifications':proposal_checks,'requiredExposureRecords':exposures,'sourceFamilyOverlap':0,'qualification':'independent implementation recount; same corpus and developer, not external peer review or independent behavioral evaluation'}
 (OUT/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()
