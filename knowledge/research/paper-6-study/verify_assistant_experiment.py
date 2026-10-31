"""Coordinator acceptance checker; imports no agent implementation predicates."""
import json,hashlib,copy,collections
from pathlib import Path
BASE=Path(__file__).resolve().parent
ART=BASE/'assistant-workspace/artifacts'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(path):
 result=json.loads(path.read_text());oracle=json.loads((BASE/'assistant-reference-oracle.json').read_text())['expected']
 inputs=json.loads((ART/'inputs/cases-v1.json').read_text());original={c['case_id']:c for c in inputs['cases']}
 catalog=json.loads((BASE/'native-starter-catalog.json').read_text());cat={c['type']:c for c in catalog['components']}
 failures=[];checks=0
 def check(ok,case,reason):
  nonlocal checks
  checks+=1
  if not ok:failures.append({'case':case,'reason':reason})
 def transform(x,mapping):
  if isinstance(x,list):return [transform(v,mapping) for v in x]
  if isinstance(x,dict):
   return {k:(mapping.get(v,v) if k in ('node','source','target','required_agent','old','new') and isinstance(v,str) else transform(v,mapping)) for k,v in x.items()}
  return x
 records=result['records'];check(len(records)==96,'inventory','96 distinct states')
 check(len({(r['base_case_id'],r['variant']) for r in records})==96,'inventory','unique case/variant keys')
 for name,h in result['source_hashes'].items():
  p=BASE/'assistant-workspace'/name if name.startswith(('context/','artifacts/')) else ART/name
  check(p.exists() and digest(p)==h,'freeze',name)
 for r in records:
  cid=r['base_case_id'];tag=cid+':'+r['variant'];expected=oracle[cid];d=r['decisions']['ledger'];state=r['input'];post=d['post_state'];mapping=r['mapping']
  truth=copy.deepcopy(original[cid])
  if r['variant']=='rename':
   truth=transform(truth,mapping)
   for n in truth['nodes']:n['id']=mapping.get(n['id'],n['id'])
   check(len(set(mapping.values()))==len(mapping),tag,'bijective rename')
  elif r['variant']=='permutation':
   for key in ('nodes','edges','bindings','node_type_assertions'):truth[key]=list(reversed(truth.get(key,[])))
   for key in ('route_assertions','capabilities'):truth['intent'][key]=list(reversed(truth['intent'].get(key,[])))
  elif r['variant']=='duplicate':truth['bindings']=[copy.deepcopy(b) for b in truth['bindings'] for _ in range(2)]
  check(state==truth,tag,'input transformation fidelity')
  check(d['action']==expected['action'],tag,'action expected '+expected['action']+' observed '+d['action'])
  kinds={b['kind'] for b in d['blockers']}
  check(set(expected['requiredBlockerKinds'])<=kinds,tag,'mandatory blockers')
  check({p['op'] for p in d['patches']}<=set(expected['allowedPatchKinds']),tag,'patch authorization scope')
  check(len(d['runtime_unknowns'])>=3,tag,'runtime uncertainty retained')
  check(post['intent']['id']==state['intent']['id'],tag,'intent identity preserved')
  if not d['patches']:check(post==state,tag,'no unreported mutation')
  if d['patches'] and not isinstance(state.get('revision'),dict):check(False,tag,'patch without revision request')
  if d['patches'] and isinstance(state.get('revision'),dict):
   rev=state['revision'];check(rev['authorized'],tag,'explicit authorization')
   check(len(d['patches'])==1 and d['patches'][0]==rev,tag,'exact requested patch')
   if rev['op']=='rename_node':
    check({n['id'] for n in post['nodes']}==({n['id'] for n in state['nodes']}-{rev['old']}|{rev['new']}),tag,'rename identities')
    check(len(post['edges'])==len(state['edges']) and len(post['bindings'])==len(state['bindings']),tag,'rename preserves evidence multiplicity')
    expected_post=transform(state,{rev['old']:rev['new']})
    for n in expected_post['nodes']:n['id']={rev['old']:rev['new']}.get(n['id'],n['id'])
    expected_post['revision']=None
    check(post==expected_post,tag,'exact rename transition')
   elif rev['op']=='revoke_model':
    check(post['nodes']==state['nodes'] and post['edges']==state['edges'],tag,'revoke leaves graph intact')
    check(all(b['state']=='revoked' for b in post['bindings'] if b['node']==rev['node'] and b['field']=='model'),tag,'revoke invalidates model witness')
    expected_post=copy.deepcopy(state);expected_post['revision']=None
    for b in expected_post['bindings']:
     if b['node']==rev['node'] and b['field']=='model':b['state']='revoked'
    check(post==expected_post,tag,'exact revoke transition')
   elif rev['op']=='route_through_agent':
    check(post['nodes']==state['nodes'] and post['bindings']==state['bindings'],tag,'rewire no invented components/bindings')
    check(len(post['edges'])==len(state['edges'])+1,tag,'replace one direct edge by two')
    ns={n['id']:n['type'] for n in state['nodes']}
    direct=[e for e in state['edges'] if ns.get(e['source'])=='ChatInput' and ns.get(e['target'])=='ChatOutput' and e['output']=='message' and e['input']=='input_value']
    check(len(direct)==1,tag,'unique route precondition')
    if len(direct)==1:
     edge=direct[0];remaining=[e for e in state['edges'] if e!=edge]
     signatures=lambda edges:collections.Counter((e['source'],e['output'],e['target'],e['input']) for e in edges)
     expected_edges=remaining+[{'source':edge['source'],'output':'message','target':rev['node'],'input':'input_value'},{'source':rev['node'],'output':'response','target':edge['target'],'input':'input_value'}]
     check(signatures(post['edges'])==signatures(expected_edges),tag,'exact authorized route endpoints and ports')
     check(all(e in post['edges'] for e in remaining),tag,'unrelated edges unchanged')
     check(len({e['id'] for e in post['edges']})==len(post['edges']),tag,'unique resulting edge identities')
     expected_post=copy.deepcopy(state);expected_post.pop('edges');expected_post['revision']=None
     check({k:v for k,v in post.items() if k!='edges'}==expected_post,tag,'rewire changes no other state')
  # Independently check every successful static decision against actual pinned fields.
  if d['action'] in ('SPEC_GROUNDED','REVISE'):
   nodes={n['id']:n['type'] for n in post['nodes']};wires=set()
   for e in post['edges']:
    src=cat[nodes[e['source']]];dst=cat[nodes[e['target']]]
    out=next(p for p in src['outputs'] if p['name']==e['output']);inp=next(p for p in dst['inputs'] if p['name']==e['input'])
    ot=set(out['declaredTypes'] or [out['returnAnnotation']]);it=set(inp['types'])
    check(bool(ot&it),tag,'successful wire annotation compatibility');wires.add((e['target'],e['input']))
   for node,typ in nodes.items():
    for f in cat[typ]['inputs']:
     if f['required']:
      witnesses=[b for b in post['bindings'] if b['node']==node and b['field']==f['name'] and b['state']=='attested' and b['kind'] in f['types'] and b['tier']=='synthetic-assumption']
      check((node,f['name']) in wires or bool(witnesses),tag,'required field witness '+node+'.'+f['name'])
 for cid in oracle:
  rows=[r for r in records if r['base_case_id']==cid]
  for method in ('B0','B1','ledger'):
   signatures={(r['decisions'][method]['action'],tuple(sorted(b['kind'] for b in r['decisions'][method]['blockers']))) for r in rows}
   check(len(signatures)==1,cid+':'+method,'metamorphic action/blocker invariance')
 report={'checks':checks,'failures':failures,'passed':not failures,'authorship':'coordinator-authored internal acceptance, not external or unseen generalization','resultSha256':digest(path),'oracleSha256':digest(BASE/'assistant-reference-oracle.json')}
 return report
if __name__=='__main__':
 import sys
 p=Path(sys.argv[1]) if len(sys.argv)>1 else ART/'obligation-results.json'
 print(json.dumps(verify(p),indent=2))
