"""Bounded explicit feature-rule learning, retrospective masking and design proposals.
No downloaded node code, configuration value, workflow or model is executed.
"""
from __future__ import annotations
import collections,hashlib,itertools,json,os,platform,re,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'knowledge/research/paper-6-corpus'
OUT=BASE/'relational'
IMPLEMENTATION_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
CONFIG={'splitSalt':'paper6-relational-v1:','evaluationModulo':5,'evaluationBucket':0,'attempts':3,'secondsPerAttempt':20,'workers':1,'minimumJoint':5,'minimumSourceGroups':2,'minimumConfidence':.5,'minimumCenterLift':1.05,'guidedPairs':100,'maximumCases':1000,'scope':'retrospective source-group separated exploration; previously exposed corpus'}
def digest(x):return hashlib.sha256((x if isinstance(x,bytes) else str(x).encode())).hexdigest()
def canonical(x):return json.dumps(x,separators=(',',':'),ensure_ascii=True)
def token(feature):return 'f'+digest(feature)[:24]
def entity(t):return 'o'+t['id']
def is_eval(family):return int(digest(CONFIG['splitSalt']+family)[:8],16)%CONFIG['evaluationModulo']==CONFIG['evaluationBucket']
def parse_rule(text,vocabulary):
 # A deliberately narrow allowlist prevents graph-bridging clauses and occurrence memorization.
 m=re.fullmatch(r'has_feature\(([XY]),(f[a-f0-9]{24})\) <= has_feature\(([XY]),(f[a-f0-9]{24})\)',text.strip())
 if not m or m[1]!=m[3] or m[2]==m[4] or m[2] not in vocabulary or m[4] not in vocabulary:return None
 head,body=vocabulary[m[2]],vocabulary[m[4]]
 if json.loads(head)[0]!=json.loads(body)[0]:return None
 return body,head

def exact_rules(train,families):
 inv=collections.defaultdict(set);centers=collections.Counter(t['centerType'] for t in train)
 for i,t in enumerate(train):
  for f in t['items']:inv[f].add(i)
 pairs=set()
 for t in train:
  pairs.update(itertools.combinations(sorted(set(t['items'])),2))
 rows=[]
 for a,b in sorted(pairs):
  joint=inv[a]&inv[b];fs={families[train[i]['graph']] for i in joint};gs={train[i]['graph'] for i in joint}
  for body,head in [(a,b),(b,a)]:
   body_n=len(inv[body]);confidence=len(joint)/body_n;center_n=centers[json.loads(body)[0]];head_n=len(inv[head]);lift=confidence/(head_n/center_n)
   r={'id':digest(canonical([body,head]))[:24],'body':body,'head':head,'bodyCount':body_n,'jointCount':len(joint),'headCount':head_n,'centerCount':center_n,'confidence':confidence,'centerLift':lift,'jointFamilies':len(fs),'jointGraphs':len(gs),'trainingExamples':[train[i]['id'] for i in sorted(joint)]}
   if len(joint)>=CONFIG['minimumJoint'] and len(fs)>=CONFIG['minimumSourceGroups'] and confidence>=CONFIG['minimumConfidence'] and lift>=CONFIG['minimumCenterLift']:rows.append(r)
 return rows,inv

def guidance_pairs(train,families):
 import pandas as pd
 from mlxtend.preprocessing import TransactionEncoder
 from mlxtend.frequent_patterns import fpgrowth
 te=TransactionEncoder();mat=te.fit([t['items'] for t in train]).transform([t['items'] for t in train],sparse=True)
 df=pd.DataFrame.sparse.from_spmatrix(mat,columns=te.columns_)
 fi=fpgrowth(df,min_support=(CONFIG['minimumJoint']-.000001)/len(train),use_colnames=True,max_len=2)
 rows=[]
 for items in fi.itemsets:
  if len(items)!=2:continue
  pair=tuple(sorted(items));matches=[t for t in train if set(pair)<=set(t['items'])]
  rows.append({'pair':list(pair),'neighborhoods':len(matches),'graphs':len({t['graph'] for t in matches}),'families':len({families[t['graph']] for t in matches})})
 rows.sort(key=lambda r:(-r['families'],-r['graphs'],-r['neighborhoods'],canonical(r['pair'])))
 return rows[:CONFIG['guidedPairs']],len(rows)

def make_cases(evaluation,families):
 cases=[]
 for t in evaluation:
  if len(t['items'])<2:continue
  target=min(t['items'],key=lambda f:digest(t['id']+':'+f))
  cases.append({'id':t['id'],'entity':entity(t),'graph':t['graph'],'center':t['center'],'centerType':t['centerType'],'family':families[t['graph']],'target':target,'visible':[f for f in t['items'] if f!=target]})
 return sorted(cases,key=lambda c:digest(c['id']))[:CONFIG['maximumCases']]

def eligible(r):return r['confidence']>=CONFIG['minimumConfidence']
def apply_direct(rules,visible,center):
 scores={};reasons=collections.defaultdict(list);visible=set(visible)
 for r in rules:
  if r['body'] in visible and r['head'] not in visible and json.loads(r['head'])[0]==center:
   scores[r['head']]=max(scores.get(r['head'],0),r['confidence']);reasons[r['head']].append(r['id'])
 return sorted(scores,key=lambda f:(-scores[f],f)),dict(scores),dict(reasons)

def native_answers(rules,train,cases,vocab):
 from clause import Options
 from c_clause import Loader,QAHandler
 if not rules:return [[] for c in cases]
 opts=Options();opts.set('loader.verbose',False);opts.set('loader.num_threads',1);opts.set('loader.c_num_unseen',0);opts.set('qa_handler.verbose',False);opts.set('qa_handler.num_threads',1);opts.set('qa_handler.topk',-1);opts.set('qa_handler.disc_at_least',-1);opts.set('qa_handler.num_top_rules',-1);opts.set('qa_handler.hard_stop_at',-1);opts.set('qa_handler.aggregation_function','maxplus');opts.set('qa_handler.filter_w_data',True)
 facts=[(entity(t),'has_feature',token(f)) for t in train for f in t['items']]+[(c['entity'],'has_feature',token(f)) for c in cases for f in c['visible']]
 loader=Loader(opts.get('loader'));loader.load_data(data=facts)
 clauses=[f"has_feature(X,{token(r['head'])}) <= has_feature(X,{token(r['body'])})" for r in rules]
 loader.load_rules(rules=clauses,stats=[[r['bodyCount'],r['jointCount']] for r in rules])
 qa=QAHandler(opts.get('qa_handler'));qa.calculate_answers(queries=[(c['entity'],'has_feature') for c in cases],loader=loader,direction='tail')
 answers=qa.get_answers(as_string=True);result=[]
 for c,ans in zip(cases,answers):
  native={vocab[f]:score for f,score in ans};ranked,scores,reasons=apply_direct(rules,c['visible'],c['centerType'])
  assert set(native)==set(scores),(c['id'],set(native)^set(scores))
  for f in scores:assert abs(native[f]-scores[f])<1e-9,(native[f],scores[f])
  result.append([{'feature':f,'score':scores[f],'rules':reasons[f]} for f in ranked])
 assert len(result)==len(cases)
 return result

def metrics(cases,predictions):
 assert len(cases)==len(predictions),'Prediction count does not match case count'
 rows=[];groups=collections.defaultdict(list)
 for c,p in zip(cases,predictions):
  top=p[0]['feature'] if p else None;hit=top==c['target'];groups[c['family']].append(int(hit));rows.append({'case':c['id'],'target':c['target'],'prediction':top,'recovered':hit,'answers':len(p),'score':p[0]['score'] if p else None,'ruleIds':p[0].get('rules',[]) if p else []})
 answered=sum(r['prediction'] is not None for r in rows);hits=sum(r['recovered'] for r in rows)
 return {'cases':len(cases),'answered':answered,'recovered':hits,'coverage':answered/len(cases) if cases else None,'recoveryPerCase':hits/len(cases) if cases else None,'recoveryPerAnswer':hits/answered if answered else None,'familyMacroRecovery':sum(sum(v)/len(v) for v in groups.values())/len(groups) if groups else None,'families':len(groups)},rows

def run_engine(data,path,seconds=20):
 if path.exists():raise RuntimeError('Refusing stale rule artifact; use a fresh invocation directory')
 path.parent.mkdir(parents=True,exist_ok=True)
 log=path.parent/'process.log'
 cmd=[sys.executable,str(Path(__file__).resolve()),'engine-worker',str(data),str(path),str(seconds)]
 with log.open('w') as out:
  start=time.perf_counter();p=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
  try:p.wait(timeout=75)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   raise RuntimeError('Bounded AnyBURL process timed out')
 if p.returncode or not path.exists():raise RuntimeError(f'AnyBURL output missing or worker failed; inspect {log}')
 return {'seconds':round(time.perf_counter()-start,3),'returncode':p.returncode,'ruleFileSha256':digest(path.read_bytes()),'ruleFile':str(path.relative_to(ROOT)),'log':str(log.relative_to(ROOT))}

def engine_worker(data,output,seconds):
 from clause import Learner,Options
 opts=Options();opts.set('learner.mode','anyburl');opts.set('learner.anyburl.time',int(seconds));opts.set('learner.anyburl.raw.WORKER_THREADS',1);opts.set('learner.anyburl.raw.MAX_LENGTH_CYCLIC',2);opts.set('learner.anyburl.raw.MAX_LENGTH_ACYCLIC',1);opts.set('learner.anyburl.java_options',['-Xmx512m','-Dfile.encoding=UTF-8'])
 Learner(options=opts.get('learner')).learn_rules(path_data=data,path_output=output)
 if not Path(output).exists():raise RuntimeError('Learner returned without its rules artifact')

def catalog_from_training(train_graphs):
 result=collections.defaultdict(list)
 for g in train_graphs:
  for n in g['nodes']:
   descriptor={k:n.get(k,[]) for k in ['type','version','inputs','outputs','resourceRequirements']}
   row={'descriptor':descriptor,'graph':g['id'],'node':n['id'],'sources':g['sources']}
   if not any(x['descriptor']==descriptor for x in result[n['type']]):result[n['type']].append(row)
 return dict(result)

def proposal(case,prediction,rules_by_id,catalog):
 if prediction['prediction'] is None:return None
 target=json.loads(prediction['prediction']);rs=[rules_by_id[i] for i in prediction['ruleIds']];visible=set(case['visible']);body=next((r['body'] for r in rs if r['body'] in visible),None)
 if not body:return None
 features=[json.loads(body),target];center=features[0][0]
 def choose(kind,required_in,required_out):
  return next((r for r in catalog.get(kind,[]) if all(any(p['name']==x for p in r['descriptor']['inputs']) for x in required_in) and all(any(p['name']==x for p in r['descriptor']['outputs']) for x in required_out)),None)
 cin=[f[4] for f in features if f[1]=='in'];cout=[f[3] for f in features if f[1]=='out'];cr=choose(center,cin,cout)
 if not cr:return {'case':case['id'],'status':'unresolved-catalog','reason':'No single training descriptor declares all center ports','prediction':prediction['prediction']}
 nodes=[{'id':'center','origin':'observed center role; training descriptor binding proposed',**cr}];edges=[]
 for i,f in enumerate(features):
  row=choose(f[2],[f[4]] if f[1]=='out' else [],[f[3]] if f[1]=='in' else [])
  if not row:return {'case':case['id'],'status':'unresolved-catalog','reason':'No training neighbor descriptor declares the needed port','prediction':prediction['prediction']}
  nid='neighbor'+str(i);nodes.append({'id':nid,'origin':'symbolic occurrence; identity/aliasing unresolved',**row})
  src,tgt=(('center',nid) if f[1]=='out' else (nid,'center'));edges.append({'source':src,'target':tgt,'sourcePort':f[3],'targetPort':f[4],'status':'visible-feature role' if i==0 else 'learned-feature proposal'})
 exposures=[];type_checks=[];resources=[]
 for n in nodes:
  for p in n['descriptor']['inputs']:
   if p.get('required') and not any(e['target']==n['id'] and e['targetPort']==p['name'] for e in edges):exposures.append({'node':n['id'],'field':p['name'],'judgment':'unresolved configured/default/external input; not proven absent'})
  resources.extend({'node':n['id'],**r,'judgment':'binding unknown; no values read'} for r in n['descriptor']['resourceRequirements'])
 for e in edges:
  src=next(n for n in nodes if n['id']==e['source']);tgt=next(n for n in nodes if n['id']==e['target']);o=next(p for p in src['descriptor']['outputs'] if p['name']==e['sourcePort']);i=next(p for p in tgt['descriptor']['inputs'] if p['name']==e['targetPort']);ot=set(o.get('types',[]));it=set(i.get('types',[]));type_checks.append({'edge':e,'judgment':'declared-label-overlap' if ot&it else 'unknown' if not ot or not it else 'declared-label-conflict','outputTypes':sorted(ot),'inputTypes':sorted(it)})
 return {'case':case['id'],'status':'proposal-only','prediction':prediction['prediction'],'ruleIds':prediction['ruleIds'],'nodes':nodes,'edges':edges,'requiredExposures':exposures,'resources':resources,'typeChecks':type_checks,'structuralChecks':{'connected':True,'acyclic':True,'portsDeclared':True,'allKnownTypesOverlap':all(t['judgment']=='declared-label-overlap' for t in type_checks)},'purpose':'unresolved; no bounded task inferred','limits':['Fresh symbolic neighbors do not establish whether original occurrences should alias','Training saved declarations are not certified native components or active outputs','No workflow execution, behavior validation or library promotion']}

def main():
 OUT.mkdir(exist_ok=True)
 batch=OUT/'engine-batches'/str(time.time_ns());batch.mkdir(parents=True)
 (batch/'implementation.py').write_bytes(Path(__file__).read_bytes())
 protocol_bytes=(Path(__file__).parent/'RELATIONAL-PROTOCOL.md').read_bytes();(batch/'protocol.md').write_bytes(protocol_bytes)
 source=(BASE/'patterns/transactions.json').read_bytes();data=json.loads(source);tx=data['transactions'];families=data['families'];train=[t for t in tx if not is_eval(families[t['graph']])];evaluation=[t for t in tx if is_eval(families[t['graph']])];cases=make_cases(evaluation,families)
 assert not ({families[t['graph']] for t in train}&{families[t['graph']] for t in evaluation})
 train_graph_ids={t['graph'] for t in train};train_graphs=[json.loads((BASE/'topology/graphs'/f'{g}.json').read_text()) for g in sorted(train_graph_ids)]
 vocabulary={token(f):f for t in train for f in t['items']};assert len(vocabulary)==len({f for t in train for f in t['items']})
 facts=sorted({(entity(t),'has_feature',token(f)) for t in train for f in t['items']});training=OUT/'train-features.tsv';training.write_text('\n'.join('\t'.join(f) for f in facts)+'\n')
 exact,inv=exact_rules(train,families);by_pair={(r['body'],r['head']):r for r in exact};guided,total_pairs=guidance_pairs(train,families);pairset={tuple(r['pair']) for r in guided}
 runs=[];learned={};raw_syntax=collections.Counter();sets=[]
 for attempt in range(CONFIG['attempts']):
  path=batch/f'feature-run-{attempt+1}'/'rules.txt';r=run_engine(training,path,CONFIG['secondsPerAttempt']);local=set();native_rows=[]
  for line in path.read_text().splitlines():
   parts=line.split('\t');text=parts[-1];parsed=parse_rule(text,vocabulary)
   if not parsed:raw_syntax['outside-accepted-language']+=1;continue
   raw_syntax['same-subject-feature-implication']+=1;local.add(parsed)
   if parsed in by_pair:
    item={**by_pair[parsed],'clause':text,'nativeStatistics':[float(x) for x in parts[:3]],'learnedRuns':[]}
    learned.setdefault(item['id'],item)['learnedRuns'].append(attempt+1)
  sets.append(local);runs.append({**r,'rawLines':len(path.read_text().splitlines()),'acceptedLanguageUnique':len(local),'thresholdQualified':sum(p in by_pair for p in local)})
 rules=sorted(learned.values(),key=lambda r:r['id']);guided_rules=[r for r in rules if tuple(sorted([r['body'],r['head']])) in pairset]
 arms={'anyburl':rules,'association_guided':guided_rules,'exact_counting':exact};results={};preds={};metrics_all={}
 for name,rr in arms.items():
  answers=native_answers(rr,train,cases,vocabulary);stats,rows=metrics(cases,answers);results[name]=rows;preds[name]=answers;metrics_all[name]={'rules':len(rr),**stats}
 # Baseline uses only the center-type training feature prevalence.
 center_counts=collections.defaultdict(collections.Counter)
 for t in train:center_counts[t['centerType']].update(set(t['items']))
 base=[]
 for c in cases:
  counter=center_counts[c['centerType']];fs=sorted((f for f in counter if f not in c['visible']),key=lambda f:(-counter[f],f));den=sum(t['centerType']==c['centerType'] for t in train);base.append([{'feature':f,'score':counter[f]/den} for f in fs])
 st,rows=metrics(cases,base);metrics_all['center_frequency']={'rules':0,**st};results['center_frequency']=rows
 catalog=catalog_from_training(train_graphs);rules_by_id={r['id']:r for r in rules};proposals=[p for c,r in zip(cases,results['anyburl']) if (p:=proposal(c,r,rules_by_id,catalog))]
 # Secondary representation probe: actual typed-port occurrence edges, no shared type entities.
 edge_vocab={};wire_facts=[]
 for g in train_graphs:
  nodes={n['id']:n for n in g['nodes']}
  for e in g['edges']:
   if not e['resolved'] or not e['sourcePort'] or not e['targetPort'] or e['source'] not in nodes or e['target'] not in nodes or 'Unknown' in [e['sourceType'],e['targetType']]:continue
   signature=canonical([e['sourceType'],e['sourcePort'],e['targetType'],e['targetPort']]);rel='r'+digest(signature)[:20];edge_vocab[rel]=json.loads(signature);wire_facts.append(('n'+digest(g['id']+':'+e['source'])[:32],rel,'n'+digest(g['id']+':'+e['target'])[:32]))
 wire=OUT/'train-wires.tsv';wire.write_text('\n'.join('\t'.join(x) for x in sorted(set(wire_facts)))+'\n');wire_path=batch/'wire-probe'/'rules.txt'
 try:probe={'status':'completed',**run_engine(wire,wire_path,20)}
 except RuntimeError as error:
  log=wire_path.parent/'process.log';text=log.read_text() if log.exists() else '';probe={'status':'infrastructure-failure','reason':'Java heap exhausted under the fixed 512MB limit' if 'OutOfMemoryError' in text else str(error),'log':str(log.relative_to(ROOT)),'ruleFile':None}
 b_rules=[]
 for line in (wire_path.read_text().splitlines() if wire_path.exists() else []):
  text=line.split('\t')[-1]
  if not re.search(r'\bn[a-f0-9]{32}\b',text):b_rules.append(line)
 probe.update({'rawRules':len(wire_path.read_text().splitlines()) if wire_path.exists() else None,'withoutOccurrenceConstants':len(b_rules) if wire_path.exists() else None,'scope':'Training-only feasibility probe; different task, no masked-link performance comparison'})
 jar=ROOT/'services/research-notebook/.runtime/PyClause/clause/bin/AnyBURL-23-1.jar';commit=subprocess.check_output(['git','-C',str(ROOT/'services/research-notebook/.runtime/PyClause'),'rev-parse','HEAD'],text=True).strip()
 summary={'config':CONFIG,'freeze':{'transactionsSha256':digest(source),'previousFreeze':data['freeze'],'implementationSha256':IMPLEMENTATION_SHA256,'protocolSha256':digest(protocol_bytes),'batch':str(batch.relative_to(ROOT)),'trainingFactsSha256':digest(training.read_bytes()),'pyclauseCommit':commit,'anyburlJarSha256':digest(jar.read_bytes()),'python':platform.python_version()},'split':{'trainNeighborhoods':len(train),'evaluationNeighborhoods':len(evaluation),'trainGraphs':len(train_graph_ids),'evaluationGraphs':len({t['graph'] for t in evaluation}),'trainFamilies':len({families[t['graph']] for t in train}),'evaluationFamilies':len({families[t['graph']] for t in evaluation}),'familyOverlap':0,'cases':len(cases),'maskedTargetInTrainingVocabulary':sum(token(c['target']) in vocabulary for c in cases),'unmaskedEvaluationNeighborhoods':len(evaluation)-len(cases)},'learning':{'runs':runs,'languageCounts':dict(raw_syntax),'exactQualifiedRules':len(exact),'engineQualifiedUnion':len(rules),'guidedQualifiedRules':len(guided_rules),'trainingFrequentPairs':total_pairs,'shortlistedPairs':len(guided),'wireProbe':probe,'pairwiseLanguageJaccard':[(len(a&b)/len(a|b) if a|b else None) for a,b in itertools.combinations(sets,2)]},'metrics':metrics_all,'proposals':{'total':len(proposals),'catalogUnresolved':sum(p['status']!='proposal-only' for p in proposals),'allDeclaredTypeLabelsOverlap':sum(p.get('structuralChecks',{}).get('allKnownTypesOverlap',False) for p in proposals),'withDeclaredTypeConflict':sum(any(t['judgment']=='declared-label-conflict' for t in p.get('typeChecks',[])) for p in proposals)},'limits':['Retrospective separated evaluation; corpus previously exposed','Feature clauses serialize associations, not arbitrary topology discovery','Masks hide one recorded feature; other plausible completions are not behavioral errors','Association guidance is a post-learning shortlist, not proven faster AnyBURL input','Proposal identity, aliasing, configuration, active ports, semantics and usefulness remain unresolved','Native scores are replaced by independently recounted exact counts for the accepted language']}
 for file,content in [('summary.json',summary),('rules.json',rules),('exact-rules.json',exact),('guidance.json',guided),('cases.json',cases),('predictions.json',results),('proposals.json',proposals),('vocabulary.json',vocabulary),('wire-vocabulary.json',edge_vocab),('catalog.json',catalog)]: (OUT/file).write_text(json.dumps(content,indent=2))
 (OUT/'wire-transferable-rules.txt').write_text('\n'.join(b_rules))
 print(json.dumps({'split':summary['split'],'learning':summary['learning'],'metrics':metrics_all,'proposals':summary['proposals']},indent=2))
 return summary
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='engine-worker':engine_worker(*sys.argv[2:])
 else:main()
