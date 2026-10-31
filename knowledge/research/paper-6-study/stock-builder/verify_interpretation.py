"""Separate coordinator checker over frozen stock graph and analyst proposals."""
import json,hashlib,copy
from pathlib import Path
BASE=Path(__file__).resolve().parent;ART=BASE.parent/'assistant-workspace/artifacts'
def verify(proposal,flow):
 data=flow['data'];nodes={n['id']:n for n in data['nodes']};edges={e['id']:e for e in data['edges']};issues=[];count=0
 def test(ok,message):
  nonlocal count
  count+=1
  if not ok:issues.append(message)
 test(len(nodes)==len(data['nodes']),'unique native occurrence IDs');test(len(edges)==len(data['edges']),'unique native wire IDs')
 test({x['nodeId'] for x in proposal['componentRoles']}==set(nodes),'all native occurrences preserved')
 for r in proposal['componentRoles']:test(r['nodeId'] in nodes and nodes[r['nodeId']]['data']['type']==r['type'],'native role/type fidelity')
 refs={w['ref']:w for w in proposal['nativeWires']};test({w['edgeId'] for w in refs.values()}==set(edges),'every native wire preserved exactly')
 for w in refs.values():
  edge=edges[w['edgeId']];sh=edge['data']['sourceHandle'];th=edge['data']['targetHandle']
  test((w['source'],w['sourcePort'],w['target'],w['targetPort'])==(edge['source'],sh['name'],edge['target'],th['fieldName']),'exact native endpoints/ports')
  test(bool(set(sh.get('output_types',[]))&set(th.get('inputTypes',[]))),'recorded static type overlap')
 groups={g['id']:g for g in proposal['proposedComposites']};members=[]
 for gid,g in groups.items():
  m=set(g['memberNodeIds']);members+=list(m);test(bool(m) and m<=set(nodes),'valid composite members')
  internal={e['id'] for e in edges.values() if e['source'] in m and e['target'] in m};cut={e['id'] for e in edges.values() if (e['source'] in m)!=(e['target'] in m)}
  test({refs[r]['edgeId'] for r in g['internalWireRefs']}==internal,'exact induced internal wires')
  test(set(g['crossingEdgeIds'])==cut,'complete cut export')
  test({refs[x['wireRef']]['edgeId'] for x in g['exports']}==cut,'all crossing wires mapped to interfaces')
  for x in g['exports']:
   w=refs[x['wireRef']];out=w['source'] in m
   test(x['direction']==('output' if out else 'input') and x['nodeId']==w['source' if out else 'target'] and x['port']==w['sourcePort' if out else 'targetPort'],'export direction/member/port')
  for x in g['publicInterfaces']:
   nid=x['nodeId'];test(nid in m,'public interface belongs to composite')
   if nid in nodes:
    template=nodes[nid]['data']['node'];test(x.get('field') in template['template'] if x['direction']=='input' else x.get('port') in {p['name'] for p in template['outputs']},'public native field/output exists')
  test(g['status']=='proposed','composite remains analyst proposal')
 test(set(members)==set(nodes) and len(members)==len(set(members)),'complete nonduplicating primary partition')
 f=proposal['proposedFlow'];test(set(f['compositeRefs'])==set(groups),'flow references all proposed groups')
 inherited=set().union(*(set(g['unknownObligations']) for g in groups.values()));test(set(f['unknownObligations'])>=inherited,'flow retains all composite obligations')
 expected={e['id'] for e in edges.values() if any(e['source'] in groups[a]['memberNodeIds'] and e['target'] in groups[b]['memberNodeIds'] for a in groups for b in groups if a!=b)}
 test({refs[h['wireRef']]['edgeId'] for h in f['dataHandoffs']}==expected,'all inter-composite handoffs retained')
 for h in f['dataHandoffs']:
  w=refs[h['wireRef']];test(w['source'] in groups[h['from']]['memberNodeIds'] and w['target'] in groups[h['to']]['memberNodeIds'],'handoff direction')
 test(f['status']=='proposed' and all(f.get(k) for k in ('controlProposal','terminationProposal','failureProposal')),'coordination semantics explicit and proposed')
 p=proposal['proposedProcess'];test(p['flowRefs']==[f['id']],'process immediate flow reference');test(set(p['gaps'])>=set(f['unknownObligations']),'process retains flow obligations');test(p['status']=='proposed' and p['accountability']['binding'] is None,'no invented human authority')
 test(set(proposal['alternativeInterpretation']['memberNodeIds'])==set(nodes),'alternative covers same identities, not cloned occurrences')
 required_rows={'Accept ticket description','Propose category, urgency and short reply','Separate critique of unsupported claims','Present suggestion for human consideration','Do not send messages/update tickets','Build only; do not execute/test','Built-in components; no custom code generation','State essential assumptions/missing requirements'}
 names=[r['requirement'] for r in proposal['requirementCoverage']]
 test(required_rows<=set(names),'retain declared original-task coverage rows')
 test(len(names)==len(set(names)),'unique coverage row identities')
 for r in proposal['requirementCoverage']:test(not r.get('behaviorVerified',False),'no requirement claimed behaviorally verified')
 return {'checks':count,'passed':not issues,'issues':issues,'scope':'Internal structural interpretation check only, not a complete validator or semantic purpose test'}
if __name__=='__main__':
 import sys
 proposal=json.load(open(ART/(sys.argv[1] if len(sys.argv)>1 else 'stock-first-analysis.json')));run=BASE/json.load(open(BASE/'latest.json'))['run'];flow=json.load(open(run/'flow.json'));print(json.dumps(verify(proposal,flow),indent=2))
