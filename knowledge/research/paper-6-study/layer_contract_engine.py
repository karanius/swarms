"""Finite structural layer contract checker. No graph construction or model calls.

Accepted document is an authored contract over native occurrences, not emergence.
"""
import copy,hashlib,json

def wire(edge):
 return (edge['source'],edge['data']['sourceHandle']['name'],edge['target'],edge['data']['targetHandle']['fieldName'])
def cut(edges,members):return [e['id'] for e in edges if (e['source'] in members)!=(e['target'] in members)]
def check(document,native):
 errors=[];assertions=0
 def require(ok,reason):
  nonlocal assertions
  assertions+=1
  if not ok:errors.append(reason)
 graph=native['nativeFlow']['data'];nodes={n['id']:n for n in graph['nodes']};edges={e['id']:e for e in graph['edges']};layers=document['layers'];comps={n['id']:n for n in layers['components']};groups={g['id']:g for g in layers['composites']};flows={f['id']:f for f in layers['flows']};processes=layers['processes'];configs={c['id']:c for c in layers['configuration']};obligations={o['id']:o for o in document['obligations']}
 allowed={'schemaVersion','id','revision','parentRevision','revisionTrace','nativeGraphArtifact','nativeGraphSha256','runtimeExecuted','authorship','layers','requirements','obligations'}
 require(set(document)==allowed,'closed document schema')
 require(set(layers)=={'configuration','components','composites','flows','processes'},'closed plane vocabulary')
 entity_fields={'configuration':{'id','target','field','status','resourceRef','proposedValue','evidence'},'components':{'id','nativeType','definitionRef','role','configurationRefs','openObligations','status'},'composites':{'id','definitionRef','members','purpose','internalEdges','exposures','openObligations','status','acceptance','publicInterfaces'},'flows':{'id','members','handoffs','interfaces','coordination','openObligations','status'},'processes':{'id','members','outcome','roles','completion','openObligations','status'}}
 for plane,items in layers.items():
  for item in items:require(set(item)==entity_fields.get(plane,set()),'closed entity schema '+item['id'])
 for req in document['requirements']:require(set(req)=={'id','text','realizedBy','openObligations'},'closed requirement schema '+req['id'])
 for o in document['obligations']:require(set(o)=={'id','kind','target','status','question','evidenceTier'},'closed obligation schema '+o['id'])
 for edge in edges.values():
  src=nodes.get(edge['source']);dst=nodes.get(edge['target']);require(src is not None and dst is not None,'native edge endpoint')
  if src and dst:
   sh=edge['data']['sourceHandle'];th=edge['data']['targetHandle']
   require(sh['id']==src['id'] and th['id']==dst['id'],'native handle identity')
   require(sh['name'] in {p['name'] for p in src['data']['node']['outputs']},'native output declaration')
   require(th['fieldName'] in dst['data']['node']['template'],'native input declaration')
   require(bool(set(sh.get('output_types',[]))&set(th.get('inputTypes',[]))),'native recorded type overlap')
 # Finite DAG policy for this specimen, not a claim that all Langflow graphs are acyclic.
 indegree={n:0 for n in nodes};adj={n:[] for n in nodes}
 for e in edges.values():
  if e['source'] in nodes and e['target'] in nodes:adj[e['source']].append(e['target']);indegree[e['target']]+=1
 queue=[n for n in nodes if indegree[n]==0];seen=[]
 while queue:
  n=queue.pop();seen.append(n)
  for target in adj[n]:
   indegree[target]-=1
   if indegree[target]==0:queue.append(target)
 require(len(seen)==len(nodes),'native specimen DAG')
 require(set(comps)==set(nodes),'exact native occurrence coverage')
 ids=[x['id'] for values in layers.values() for x in values];require(len(ids)==len(set(ids)),'globally distinct plane identities')
 require(document['nativeGraphSha256']==hashlib.sha256(json.dumps(native,sort_keys=True).encode()).hexdigest(),'pinned native graph content')
 for nid,c in comps.items():
  require(nid in nodes and c['nativeType']==nodes[nid]['data']['type'],'native type identity '+nid)
  require(c['definitionRef']==c['nativeType'],'definition reference '+nid)
  require(set(c['configurationRefs'])<=set(configs),'configuration references '+nid)
  require(all(configs[k]['target']==nid for k in c['configurationRefs'] if k in configs),'configuration ownership '+nid)
  require(set(c['openObligations'])<=set(obligations),'component obligations exist '+nid)
  require(set(c['openObligations'])>={o['id'] for o in obligations.values() if o['target']==nid},'component retains scoped obligations '+nid)
  if c['nativeType']=='Agent':
   require(any(o['target']==nid and o['kind']=='model_binding' and o['status']=='open' for o in obligations.values()),'model binding explicitly unresolved '+nid)
 for cfg in configs.values():
  target=cfg['target'];require(target in nodes,'configuration target '+cfg['id'])
  if target in nodes:require(cfg['field'] in nodes[target]['data']['node']['template'],'native configuration field '+cfg['id'])
  require(cfg['status'] in ['proposed','unresolved'],'no inferred verified configuration '+cfg['id'])
 memberships=[]
 for gid,g in groups.items():
  m=set(g['members']);memberships+=list(m);require(bool(m) and m<=set(comps),'composite lower members '+gid)
  internal={e['id'] for e in edges.values() if e['source'] in m and e['target'] in m}
  require(set(g['internalEdges'])==internal,'induced internal edge fidelity '+gid)
  boundary=set(cut(edges.values(),m));require({x['edgeId'] for x in g['exposures']}==boundary,'complete crossing boundary '+gid)
  require(len(g['exposures'])==len(boundary),'no duplicate boundary exposure '+gid)
  for expose in g['exposures']:
   edge=edges.get(expose['edgeId']);require(edge is not None,'exposure has source edge')
   if edge:
    require(expose['direction']==('output' if edge['source'] in m else 'input'),'exposure direction '+gid)
    require(expose['node']==(edge['source'] if edge['source'] in m else edge['target']),'exposure member identity '+gid)
    require(expose['port']==(wire(edge)[1] if edge['source'] in m else wire(edge)[3]),'exposure native port '+gid)
  for interface in g['publicInterfaces']:
   n=nodes.get(interface['node']);require(interface['node'] in m,'public interface member '+gid)
   if n:
    template=n['data']['node'];declared=template['template'] if interface['kind']=='native-field' else {p['name']:p for p in template['outputs']} if interface['kind']=='native-output' else {}
    require(interface['port'] in declared,'public interface native field/port '+gid)
    require((interface['direction'],interface['kind']) in [('input','native-field'),('output','native-output')],'public interface direction/type '+gid)
  require(bool(g['publicInterfaces']),'explicit public boundary '+gid)
  inherited=set().union(*(set(comps[n]['openObligations']) for n in m)) if m<=set(comps) else set()
  require(set(g['openObligations'])>=inherited|{o['id'] for o in obligations.values() if o['target']==gid},'composite retains lower and scoped obligations '+gid)
  require(g['status']=='proposed' and bool(g['purpose']),'composite purpose remains proposed '+gid)
 require(len(memberships)==len(set(memberships)) and set(memberships)==set(comps),'partition covers without alias collapse')
 for fid,f in flows.items():
  require(set(f['members'])<=set(groups) and bool(f['members']),'flow immediate members '+fid)
  require(set(f['interfaces'])=={i['id'] for g in f['members'] if g in groups for i in groups[g]['publicInterfaces']},'flow propagates public interfaces '+fid)
  inherited=set().union(*(set(groups[g]['openObligations']) for g in f['members'] if g in groups))
  require(set(f['openObligations'])>=inherited|{o['id'] for o in obligations.values() if o['target']==fid},'flow retains inherited and scoped obligations '+fid)
  require(all(key in f['coordination'] and bool(f['coordination'][key]) for key in ['order','termination','failure']),'explicit coordination semantics '+fid)
  require(set(f['coordination']['order'])==set(f['members']),'coordination covers members '+fid)
  require(f['status']=='proposed','flow not falsely promoted '+fid)
  require(len(f['coordination']['order'])==len(set(f['coordination']['order'])),'unique coordination order '+fid)
  for h in f['handoffs']:
   edge=edges.get(h['edgeId']);require(edge is not None and h['from'] in groups and h['to'] in groups,'handoff references '+fid)
   if edge and h['from'] in groups and h['to'] in groups:
    require(edge['source'] in groups[h['from']]['members'] and edge['target'] in groups[h['to']]['members'],'handoff source grounding '+fid)
    order=f['coordination']['order'];require(h['from'] in order and h['to'] in order and order.index(h['from'])<order.index(h['to']),'coordination order respects native handoff '+fid)
  expected={e['id'] for e in edges.values() if any(e['source'] in groups[a]['members'] and e['target'] in groups[b]['members'] for a in f['members'] for b in f['members'] if a!=b)}
  require({h['edgeId'] for h in f['handoffs']}==expected,'all inter-composite wires mapped '+fid)
 for p in processes:
  require(bool(p['members']) and set(p['members'])<=set(flows),'process immediate members '+p['id'])
  inherited=set().union(*(set(flows[f]['openObligations']) for f in p['members'] if f in flows));require(set(p['openObligations'])>=inherited|{o['id'] for o in obligations.values() if o['target']==p['id']},'process retains lower and scoped obligations '+p['id'])
  require(bool(p['outcome']) and bool(p['completion']) and bool(p['roles']),'process adds outcome/accountability contract')
  require(p['status']=='proposed' and any(obligations[o]['kind']=='human_approval' for o in p['openObligations'] if o in obligations),'human approval not replaced by Agent review')
 for requirement in document['requirements']:
  require(bool(requirement['realizedBy']) or bool(requirement['openObligations']),'requirement not silently dropped '+requirement['id'])
  require(set(requirement['realizedBy'])<=set(ids),'requirement realization references '+requirement['id'])
  require(set(requirement['openObligations'])<=set(obligations),'requirement obligation references '+requirement['id'])
 require(all(o['status']=='open' for o in obligations.values()),'open obligations preserved without invented proof')
 require(document['runtimeExecuted'] is False,'no runtime execution claim')
 return {'structuralAssertions':assertions,'passed':not errors,'errors':errors,'openObligations':len(obligations),'readiness':'blocked by explicit obligations','limits':'Authored structural contract, not learned hierarchy, useful behavior, scheduler implementation or human approval'}

def apply_revision(document,patch):
 """One explicit proposed prompt revision with immutable IDs and parent linkage."""
 if set(patch)!={'op','configurationId','proposedValue','requirementId'} or patch['op']!='propose_configuration':raise ValueError('Unsupported revision')
 out=copy.deepcopy(document);matches=[c for c in out['layers']['configuration'] if c['id']==patch['configurationId']]
 if len(matches)!=1:raise ValueError('Ambiguous configuration identity')
 if patch['requirementId'] not in {r['id'] for r in out['requirements']}:raise ValueError('Unknown requirement')
 field=matches[0]
 if field['field']!='system_prompt':raise ValueError('Only proposed nonsecret prompt revision allowed')
 if not isinstance(patch['proposedValue'],str) or len(patch['proposedValue'])>4000:raise ValueError('Bounded proposed text required')
 field['proposedValue']=patch['proposedValue'];field['status']='proposed';out['parentRevision']=document['revision'];out['revision']=document['revision']+1
 out['revisionTrace'].append({'patch':patch,'claim':'Proposed specification change; not applied to native runtime or approved policy'})
 return out

def construction_trace(document,native,budget=12):
 """Execute finite stage gates over authored proposals; does not infer semantics.

The native graph was constructed separately by the native builder tool. This
 trace evaluates the saved candidate, rather than claiming repeated generation.
 """
 if budget<1:raise ValueError('Positive finite budget required')
 trace=[];seen=set();fingerprint=hashlib.sha256(json.dumps(document,sort_keys=True).encode()).hexdigest()
 stages=[('decompose','processes'),('decompose','flows'),('decompose','composites'),('decompose','components'),('decompose','configuration'),('ground','components'),('check','composites'),('check','flows'),('check','processes')]
 report=check(document,native)
 if not report['passed']:return {'trace':trace,'stop':'structural_rejection','errors':report['errors'],'claim':'No readiness promotion'}
 for mode,plane in stages:
  key=(fingerprint,mode,plane)
  if len(trace)>=budget:return {'trace':trace,'stop':'budget_exhausted','claim':'No readiness promotion'}
  if key in seen:return {'trace':trace,'stop':'repeated_state','claim':'No readiness promotion'}
  seen.add(key)
  units=document['layers'][plane]
  if mode=='decompose':status='authored_proposal_inspected';meaning='Read explicit authored requirements/membership; not autonomous decomposition discovery'
  elif plane=='components':status='native_static_witness' if report['passed'] else 'structural_rejection';meaning='Saved native builder artifact checked; no component executed'
  else:status='blocked' if document['obligations'] else 'structurally_checked_only';meaning='Upper purpose/control/accountability remains proposed; no runtime promotion'
  trace.append({'step':len(trace)+1,'mode':mode,'plane':plane,'unitIds':[x['id'] for x in units],'status':status,'meaning':meaning})
 questions=[{'obligation':o['id'],'question':o['question']} for o in document['obligations']]
 return {'trace':trace,'stop':'ask_for_missing_evidence' if questions else 'static_scope_complete','questions':questions,'structuralPass':report['passed'],'claim':'Executed deterministic gates over authored candidate; not learned multilayer generation'}
