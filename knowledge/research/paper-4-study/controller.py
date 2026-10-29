"""Bounded Paper 2 controller prototype over an explicit structural refinement DSL.
No network, model, generated-application execution, or credential access.
"""
from copy import deepcopy
from hashlib import sha256
import json

VERSION='p4-controller-1.1'

def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def cyclic(edges):
    graph={}
    for a,b in edges: graph.setdefault(a,[]).append(b)
    active=set(); done=set()
    def visit(v):
        if v in active: return True
        if v in done: return False
        active.add(v)
        if any(visit(w) for w in graph.get(v,[])): return True
        active.remove(v);done.add(v);return False
    return any(visit(v) for v in list(graph))


def obligation(oid,owner,kind,**kw):
    return dict(id=oid,owner=owner,kind=kind,status='open',needs=[],**kw)


def initialize(case):
    U={}; J={}; Q={'nodes':{},'edges':[],'bindings':{},'representations':{},'refinements':{}}
    for order,r in enumerate(case['requirements']):
        oid=r['id'];U[oid]=obligation(oid,oid,'realize',cap=r.get('cap'),
            in_type=r['in'],out_type=r['out'],locality=r.get('locality'),
            order=order,mandatory=r.get('mandatory',True),depth=0)
        U[oid]['needs']=list(r.get('needs',[]))
        if r.get('conflict'): U[oid]['kind']='conflict'
        J[oid]={'judgment':'unknown','criterion':'structural realization','scope':case['baseline_version']}
        J['behavior:'+oid]={'judgment':'unknown','criterion':'future behavioral evidence',
                           'support':list(r.get('support',[])), 'contradiction':list(r.get('contradiction',[])),
                           'scope':case['baseline_version']}
    roots=list(U)
    U['package']=obligation('package','instance','package',order=999,mandatory=True,depth=0)
    U['package']['needs']=roots
    return {'Q':Q,'J':J,'U':U,'roots':roots,'branch':'root'}


def structural_invariants(state,case):
    """Guard accepted patches; reference assessor additionally checks outputs."""
    Q,U,J=state['Q'],state['U'],state['J']
    for r in case['requirements']:
        if r['id'] not in U or r['id'] not in J: return False,'lost-requirement'
        if J.get('behavior:'+r['id'],{}).get('judgment')!='unknown': return False,'behavior-overclaim'
    nodes=Q['nodes']
    if len(nodes)>case['limits']['nodes']: return False,'node-limit'
    if cyclic([(e[0],e[2]) for e in Q['edges']]): return False,'component-cycle'
    for a,op,b,ip in Q['edges']:
        if a not in nodes or b not in nodes: return False,'dangling-edge'
        if nodes[a]['outputs'].get(op)!=nodes[b]['inputs'].get(ip,{}).get('type'): return False,'edge-type'
    for rep in Q['representations'].values():
        if any(x not in nodes for x in rep['members']): return False,'lost-member'
    return True,None


def candidate_key(c):
    ranks={'bind':0,'select':1,'compose':2,'package':3,'decompose':4,'return':5}
    return (0,ranks.get(c['action'],5),c.get('residual_count',0),0,c.get('edit_count',1),c['key'])


def proposals(s,o,case):
    """Explicit finite proposer. No expected answers are accepted by this API."""
    Q=s['Q'];cap=o.get('cap'); kind=o['kind']; proposals=[]
    if kind=='realize':
        for d in case['library']:
            if d['cap']==cap:
                guards={'layer':d['layer']=='components','input':d['inputs']['in']['type']==o['in_type'],
                        'output':d['outputs']['out']==o['out_type'],
                        'locality':o['locality'] is None or d['locality']==o['locality']}
                proposals.append({'key':'select:'+d['id'],'action':'select','definition':d,'guards':guards})
        if o['depth']<case['limits']['depth']:
            for rule in case['rules']:
                if rule['cap']==cap:
                    guards={'in':rule['in']==o['in_type'],'out':rule['out']==o['out_type'],
                            'bridge':rule['bridge']=='met','nonempty':bool(rule['steps']),
                            'dag':not cyclic(rule['edges'])}
                    proposals.append({'key':'decompose:'+rule['id'],'action':'decompose','rule':rule,'guards':guards,
                                      'residual_count':len(rule['steps']),'edit_count':len(rule['steps'])})
    elif kind=='bind':
        resource=case['resources'].get(o['resource'])
        if resource is not None:
            proposals=[{'key':'bind:'+o['resource'],'action':'bind','resource':o['resource'],
                        'guards':{'described':resource.get('described') is True}}]
    elif kind in ('leaf-complete','join'):
        proposals=[{'key':kind+':'+o['id'],'action':'compose','guards':{'ready':True}}]
    elif kind=='package':
        proposals=[{'key':'package:instance','action':'package','guards':{'legal_target':case['profile']=='components-to-composite-dag@1'}}]
    return sorted(proposals,key=candidate_key)


def boundary_key(o):
    impact=0 if o['kind']=='conflict' else (1 if o['kind']=='bind' or o.get('cap','defined') is None else 2)
    return (0 if o.get('mandatory',True) else 1,impact,o['order'],o['id'])


def apply_candidate(s,o,c,case):
    s=deepcopy(s);Q,U,J=s['Q'],s['U'],s['J'];o=U[o['id']];action=c['action']
    if action=='select':
        d=c['definition'];oid='occ:'+o['id']
        Q['nodes'][oid]={'id':oid,'definition':d['id'],'layer':d['layer'],'inputs':deepcopy(d['inputs']),
                        'outputs':deepcopy(d['outputs']),'config':deepcopy(d['config']),
                        'dependencies':list(d['resources']),'locality':d['locality'],'cap':d['cap']}
        o['kind']='leaf-complete';o['occurrences']=[oid]
        for res in d['resources']:
            bid=o['id']+'/bind/'+res
            if bid not in U:
                U[bid]=obligation(bid,o['owner'],'bind',resource=res,order=o['order'],mandatory=True,depth=o['depth'])
                J[bid]={'judgment':'unknown','criterion':'described resource reference','scope':case['library_version']}
            o['needs'].append(bid)
        o['entry']=[oid,'in'];o['exit']=[oid,'out']
    elif action=='bind':
        Q['bindings'][o['resource']]={'reference':o['resource'],'version':case['resources'][o['resource']]['version'],
                                    'activation':'unknown'}
        o['status']='met'
        J[o['id']]={'judgment':'met','criterion':'described reference, no authentication','scope':case['library_version']}
    elif action=='decompose':
        rule=c['rule'];o['kind']='join';o['rule']=rule['id'];o['needs']=[];o['child_keys']={}
        for step in rule['steps']:
            sid=o['id']+'/'+rule['id']+'/'+step['key'];o['child_keys'][step['key']]=sid;o['needs'].append(sid)
            U[sid]=obligation(sid,o['owner'],'realize',cap=step['cap'],in_type=step['in'],out_type=step['out'],
                             locality=o['locality'],order=o['order'],mandatory=True,depth=o['depth']+1)
            J[sid]={'judgment':'unknown','criterion':'structural realization','scope':case['baseline_version']}
        Q['refinements'][o['id']]={'rule':rule['id'],'children':list(o['needs']),
                                  'bridge':'met','criterion':'declared structural refinement axiom; not behavioral implication'}
    elif action=='compose':
        if o['kind']=='join':
            rule=next(r for r in case['rules'] if r['id']==o['rule'])
            children={key:U[sid] for key,sid in o['child_keys'].items()}
            for a,b in rule['edges']:
                edge=children[a]['exit']+children[b]['entry']
                if edge not in Q['edges']: Q['edges'].append(edge)
            o['entry']=children[rule['entry']]['entry'];o['exit']=children[rule['exit']]['exit']
            o['occurrences']=sorted({v for child in children.values() for v in child['occurrences']})
            Q['representations']['local:'+o['id']]={'layer':'composite','members':o['occurrences'],
                                                  'entry':o['entry'],'exit':o['exit'],'rule':rule['id']}
        o['status']='met'
        J[o['id']]={'judgment':'met','criterion':'structural realization only','scope':case['baseline_version']}
    elif action=='package':
        member_ids=sorted(Q['nodes']);edges=Q['edges'];all_edges=edges+case.get('ambient_edges',[])
        occupied={(e[2],e[3]) for e in all_edges}
        crossings=[e for e in all_edges if (e[0] in member_ids)!=(e[2] in member_ids)]
        exposed=[[nid,p] for nid,n in Q['nodes'].items() for p,v in n['inputs'].items()
                 if v['required'] and (nid,p) not in occupied]
        Q['representations']['instance-composite']={'layer':'composite','members':member_ids,
            'required_unbound_inputs':sorted(exposed),'crossings':crossings,
            'configuration':{nid:n['config'] for nid,n in Q['nodes'].items()},
            'dependency_refs':sorted({d for n in Q['nodes'].values() for d in n['dependencies']}),
            'root_interfaces':{rid:{'entry':U[rid]['entry'],'exit':U[rid]['exit']} for rid in s['roots']}}
        o['status']='met';J[o['id']]={'judgment':'met','criterion':'recorded package boundary','scope':case['baseline_version']}
    return s


def run(case,method='boundary',limit=None):
    """method boundary: DFS with Paper 2 priority; fifo: BFS/insertion scheduling;
    greedy: priority scheduler with no alternate frontier. All share guarded DSL.
    """
    case=deepcopy(case);case.pop('oracle',None)
    initial=initialize(case);s=initial;frontier=[];visited=set();trace=[];budget=limit or case['limits']['attempts']
    remaining=budget;maxfront=0;omitted=0;backtracks=0
    last_gap=None
    def event(kind,**kw): trace.append({'event':len(trace),'kind':kind,'remaining':remaining,**kw})
    def charge(kind,**kw):
        nonlocal remaining
        if remaining<=0: return False
        remaining-=1;event(kind,**kw);return True
    def result(outcome,gap=None):
        return {'case':case['id'],'method':method,'version':VERSION,'outcome':outcome,'gap':gap,
                'baseline':case['baseline_version'],'library':case['library_version'],'state':s,
                'trace':trace,'attempts':budget-remaining,'budget':budget,'backtracks':backtracks,
                'frontier_max':maxfront,'omitted_branches':omitted,'visited_count':len(visited),
                'residuals':[deepcopy(o) for o in s['U'].values() if o['status']!='met']+
                  [{'id':'behavior:'+r['id'],'owner':r['id'],'phase':'behavior','status':'unknown'} for r in case['requirements']]+
                  [{'id':'activation:'+r,'phase':'activation','status':'unknown'} for r in s['Q']['bindings']]}
    def backtrack(gap):
        nonlocal s,backtracks,last_gap
        last_gap=gap;event('branch-blocked',gap=gap,branch=s['branch'])
        if not frontier: return False
        if not charge('restore-frontier'): return None
        s=frontier.pop(0) if method=='fifo' else frontier.pop()
        backtracks+=1;event('restored',branch=s['branch']);return True
    if case['profile']!='components-to-composite-dag@1': return result('blocked-within-horizon','unsupported-profile')
    if not s['roots']: return result('awaiting-clarification','empty-scope')
    if cyclic([(dep,o['id']) for o in s['U'].values() for dep in o['needs']]):
        return result('blocked-within-horizon','prerequisite-cycle')
    while True:
        if s['U']['package']['status']=='met': return result('design-closed')
        if remaining<=0: return result('partial','budget-exhausted')
        key=digest({'Q':s['Q'],'U':s['U'],'J':s['J']})
        if key in visited:
            moved=backtrack('repeated-state')
            if moved is None: return result('partial','budget-exhausted')
            if not moved: return result('blocked-within-horizon','repeated-state')
            continue
        visited.add(key)
        unresolved=[o for o in s['U'].values() if o['status']!='met']
        missing=[d for o in unresolved for d in o['needs'] if d not in s['U']]
        if missing:
            moved=backtrack('missing-prerequisite:'+missing[0])
            if moved is None: return result('partial','budget-exhausted')
            if not moved: return result('blocked-within-horizon',last_gap)
            continue
        ready=[o for o in unresolved if all(s['U'][d]['status']=='met' for d in o['needs'])]
        if not ready:
            moved=backtrack('unresolved-prerequisites')
            if moved is None: return result('partial','budget-exhausted')
            if not moved: return result('blocked-within-horizon',last_gap)
            continue
        o=ready[0] if method=='fifo' else min(ready,key=boundary_key)
        event('boundary-selected',obligation=o['id'],owner=o['owner'],priority=list(boundary_key(o)),branch=s['branch'])
        if o['kind']=='conflict':
            moved=backtrack('mandatory-conflict:'+o['id'])
            if moved is None: return result('partial','budget-exhausted')
            if not moved: return result('blocked-within-horizon',last_gap)
            continue
        if o['kind']=='realize' and o['cap'] is None:
            event('clarification',obligation=o['id'],question='Which explicit capability is required?')
            return result('awaiting-clarification','ambiguous-capability:'+o['id'])
        if not charge('propose',obligation=o['id']): return result('partial','budget-exhausted')
        all_candidates=proposals(s,o,case)
        cap=case['limits']['candidates'];batch=all_candidates[:cap]
        omitted+=max(0,len(all_candidates)-len(batch))
        event('proposal-batch',obligation=o['id'],candidates=[{'key':c['key'],'action':c['action'],'guards':c['guards']} for c in batch],omitted=max(0,len(all_candidates)-len(batch)))
        admitted=[]
        for c in batch:
            if not charge('assess',candidate=c['key'],obligation=o['id']): return result('partial','budget-exhausted')
            if not all(c['guards'].values()):
                event('rejected',candidate=c['key'],guards=c['guards']);continue
            nxt=apply_candidate(s,o,c,case)
            good,why=structural_invariants(nxt,case)
            if not good: event('rejected',candidate=c['key'],invariant=why);continue
            nxt['branch']=s['branch']+'/'+c['key']
            event('admissible',candidate=c['key'],guards=c['guards'],ordering_key=list(candidate_key(c)))
            admitted.append((c,nxt))
        if not admitted:
            reason=('missing-resource:'+o['resource']) if o['kind']=='bind' else 'unsupported-boundary:'+o['id']
            moved=backtrack(reason)
            if moved is None: return result('partial','budget-exhausted')
            if not moved: return result('blocked-within-horizon',last_gap)
            continue
        if method!='greedy':
            alternates=admitted[1:]
            if method!='fifo': alternates=list(reversed(alternates))
            for c,nxt in alternates:
                if len(frontier)<case['limits']['frontier']: frontier.append(nxt)
                else: omitted+=1;event('frontier-pruned',candidate=c['key'])
            maxfront=max(maxfront,len(frontier))
        else: omitted+=len(admitted)-1
        c,nxt=admitted[0]
        if not charge('apply',candidate=c['key'],action=c['action'],before=digest(s),after=digest(nxt)):
            return result('partial','budget-exhausted')
        s=nxt


def reassess_evidence(record,current_versions):
    """Scoped helper: do not count stale, absent, or conflicting support as met."""
    stale=any(current_versions.get(k)!=v for k,v in record['versions'].items())
    if stale: return {'judgment':'unknown','reason':'stale-context','support':record['support'],'contradiction':record['contradiction']}
    if record['support'] and not record['contradiction']: status='met'
    elif record['contradiction'] and not record['support']: status='violated'
    else: status='unknown'
    return {'judgment':status,'reason':'conflict' if record['support'] and record['contradiction'] else 'scoped-evidence',
            'support':record['support'],'contradiction':record['contradiction']}
