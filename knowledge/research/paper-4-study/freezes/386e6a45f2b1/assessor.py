"""Separate artifact assessor; no calls to controller guard/packaging functions."""
from copy import deepcopy


def check(case,result):
    errors=[];expected=case['oracle'];s=result['state'];Q=s['Q'];U=s['U'];J=s['J'];nodes=Q['nodes']
    if result['outcome']!=expected['outcome']:errors.append('outcome')
    if expected.get('gap_prefix') and not (result.get('gap') or '').startswith(expected['gap_prefix']):errors.append('gap')
    if result['attempts']>case['limits']['attempts']:errors.append('budget')
    charged=[e for e in result['trace'] if e['kind'] in ('propose','assess','apply','restore-frontier')]
    if len(charged)!=result['attempts']: errors.append('budget-accounting')
    if any(a['remaining']<b['remaining'] for a,b in zip(result['trace'],result['trace'][1:])):errors.append('budget-restored')
    if [e['event'] for e in result['trace']]!=list(range(len(result['trace']))):errors.append('trace-continuity')
    for r in case['requirements']:
        if r['id'] not in U or r['id'] not in J:errors.append('requirement-loss')
        if J.get('behavior:'+r['id'],{}).get('judgment')!='unknown':errors.append('behavior-overclaim')
    if result['outcome']=='design-closed':
        if len(nodes)!=expected.get('nodes',len(nodes)):errors.append('node-count')
        if len(Q['edges'])!=expected.get('edges',len(Q['edges'])):errors.append('edge-count')
        if any(U[r['id']]['status']!='met' for r in case['requirements']):errors.append('unmet-root')
        if any(o['status']!='met' for o in U.values()):errors.append('unmet-design')
        if expected.get('backtrack') and not result['backtracks']:errors.append('missing-backtrack')
        catalog={d['id']:d for d in case['library']}
        for nid,n in nodes.items():
            d=catalog.get(n['definition'])
            if not d:errors.append('invented-definition');continue
            if n['inputs']!=d['inputs'] or n['outputs']!=d['outputs'] or n['config']!=d['config']:errors.append('definition-mutation')
            if n['dependencies']!=d['resources']:errors.append('dependency-mutation')
            for res in n['dependencies']:
                if res not in Q['bindings']:errors.append('binding-loss')
                elif Q['bindings'][res]['activation']!='unknown':errors.append('activation-overclaim')
        incoming=set();graph={nid:[] for nid in nodes}
        for a,op,b,ip in Q['edges']:
            if a not in nodes or b not in nodes:errors.append('dangling-edge');continue
            if nodes[a]['outputs'].get(op)!=nodes[b]['inputs'].get(ip,{}).get('type'):errors.append('type')
            incoming.add((b,ip));graph[a].append(b)
        indegree={nid:0 for nid in nodes}
        for children in graph.values():
            for dst in children:indegree[dst]+=1
        queue=[v for v,d in indegree.items() if d==0];count=0
        while queue:
            v=queue.pop();count+=1
            for dst in graph[v]:
                indegree[dst]-=1
                if indegree[dst]==0:queue.append(dst)
        if count!=len(nodes):errors.append('cycle')
        for a,op,b,ip in case.get('ambient_edges',[]): incoming.add((b,ip))
        expected_unbound=sorted([[nid,p] for nid,n in nodes.items() for p,v in n['inputs'].items() if v['required'] and (nid,p) not in incoming])
        rep=Q['representations'].get('instance-composite',{})
        if sorted(rep.get('members',[]))!=sorted(nodes):errors.append('membership')
        if rep.get('required_unbound_inputs')!=expected_unbound:errors.append('boundary-loss')
        if len(rep.get('crossings',[]))!=expected.get('crossings',0):errors.append('crossing-loss')
        for nid,n in nodes.items():
            if rep.get('configuration',{}).get(nid)!=n['config']:errors.append('config-loss')
        if set(rep.get('dependency_refs',[]))!={d for n in nodes.values() for d in n['dependencies']}:errors.append('dependency-loss')
        for rid,ref in Q['refinements'].items():
            if ref['bridge']!='met':errors.append('unsupported-bridge')
            if any(x not in U for x in ref['children']):errors.append('lost-refinement-child')
    return {'passed':not errors,'errors':sorted(set(errors)),
            'invalid_accepted':result['outcome']=='design-closed' and bool(errors)}


def mutation_checks(case,good):
    mutations={}
    bad=deepcopy(good);bad['state']['Q']['representations']['instance-composite']['required_unbound_inputs']=[];mutations['drop-boundary']=check(case,bad)
    bad=deepcopy(good);bad['state']['J']['behavior:'+case['requirements'][0]['id']]['judgment']='met';mutations['invent-behavior-proof']=check(case,bad)
    bad=deepcopy(good);del bad['state']['U'][case['requirements'][0]['id']]
    # avoid closed-branch lookup of the missing requirement by flagging nonclosure
    bad['outcome']='partial';mutations['drop-requirement']=check(case,bad)
    bad=deepcopy(good);bad['attempts']=case['limits']['attempts']+1;mutations['overrun-budget']=check(case,bad)
    bad=deepcopy(good);bad['state']['Q']['edges'][0][1]='nonexistent';mutations['bad-endpoint']=check(case,bad)
    return mutations
