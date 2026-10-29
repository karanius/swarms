"""Paper 3 bounded structural study. No network calls or application execution.
Run main(output_dir) to record the synthetic case suite and observations.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

def node(oid, role, inputs=None, outputs=None, **kw):
    return dict(id=oid, definition=f'synthetic/{role}@1', layer='components',
                role=role, inputs=inputs or {}, outputs=outputs or {}, **kw)

def base(cid):
    return dict(id=cid, family='pipeline', profile='components-to-composite-dag@1',
                source=node('source', 'source', {'text': {'type':'Text','required':True}}, {'message':'Message'}),
                sink=node('sink','sink', {'message':{'type':'Message','required':True}}, {'result':'Message'}),
                candidates=[node('worker','transform', {'message':{'type':'Message','required':True}},
                                 {'response':'Message'}, capability='summarize', locality='local',
                                 config={'model_ref':'resource:model@1'}, dependencies=['resource:model@1'])],
                required_capability='summarize', required_locality=None, budget=8,
                ambient_edges=[], additional_members=[], forced_cycle=False,
                oracle={'outcome':'design-closed','boundary':[['source','text']],
                        'crossings':[], 'members':['source','worker','sink']})

def cases():
    dev=[]; evaluation=[]
    c=base('D-clean'); dev.append(c)
    c=base('D-hidden-input'); c['family']='unbound-input'; c['candidates'][0]['inputs']['context']={'type':'Text','required':True}; c['oracle']['boundary'].append(['worker','context']); dev.append(c)
    c=base('D-wrong-first'); bad=deepcopy(c['candidates'][0]); bad['id']='bad'; bad['outputs']['response']='Number'; c['candidates'].insert(0,bad); dev.append(c)
    c=base('E-clean'); evaluation.append(c)
    c=base('E-wrong-first'); bad=deepcopy(c['candidates'][0]); bad['id']='bad'; bad['inputs']['message']['type']='Image'; c['candidates'].insert(0,bad); evaluation.append(c)
    c=base('E-locality'); c['required_locality']='local'; bad=deepcopy(c['candidates'][0]); bad['id']='remote'; bad['locality']='remote'; c['candidates'].insert(0,bad); evaluation.append(c)
    c=base('E-missing'); c['candidates']=[]; c['oracle']={'outcome':'blocked-within-horizon','gap':'missing-capability'}; evaluation.append(c)
    c=base('E-ambiguous'); c['required_capability']=None; c['oracle']={'outcome':'awaiting-clarification','gap':'ambiguous-capability'}; evaluation.append(c)
    c=base('E-budget'); c['budget']=1; bad=deepcopy(c['candidates'][0]); bad['id']='bad'; bad['outputs']['response']='Number'; c['candidates'].insert(0,bad); c['oracle']={'outcome':'partial','gap':'budget-exhausted'}; evaluation.append(c)
    c=base('E-hidden-input'); c['family']='unbound-input'; c['candidates'][0]['inputs']['provenance']={'type':'Text','required':True}; c['oracle']['boundary'].append(['worker','provenance']); evaluation.append(c)
    c=base('E-crossing'); c['ambient_edges']=[['worker','response','external','input']]; c['oracle']['crossings']=deepcopy(c['ambient_edges']); evaluation.append(c)
    c=base('E-distinct-identity'); c['family']='identity'; extra=node('worker-second','transform',{}, {},config={},dependencies=[]); extra['definition']=c['candidates'][0]['definition']; c['additional_members']=[extra]; c['oracle']['members'].append('worker-second'); evaluation.append(c)
    c=base('E-unrelated-node'); c['ambient_edges']=[['outside-a','out','outside-b','in']]; evaluation.append(c)
    c=base('E-profile'); c['profile']='composite-to-enterprise@unknown'; c['oracle']={'outcome':'blocked-within-horizon','gap':'unsupported-profile'}; evaluation.append(c)
    c=base('E-cycle'); c['forced_cycle']=True; c['oracle']={'outcome':'blocked-within-horizon','gap':'unsupported-cycle'}; evaluation.append(c)
    c=base('E-config-resource'); c['candidates'][0]['dependencies'].append('resource:storage@1'); c['candidates'][0]['config']['store_ref']='resource:storage@1'; evaluation.append(c)
    c=base('E-no-compatible'); c['candidates'][0]['outputs']['response']='Number'; c['oracle']={'outcome':'blocked-within-horizon','gap':'no-compatible-candidate'}; evaluation.append(c)
    for c in dev: c['collection']='development'
    for c in evaluation: c['collection']='designated-evaluation-exposed'
    return dev+evaluation

# The procedure never receives the case's oracle record.
def generate(inp, method):
    c=deepcopy(inp); trace=[]; attempts=0
    def finish(outcome,gap,**extra):
        return dict(case=c['id'],method=method,outcome=outcome,gap=gap,attempts=attempts,
                    trace=trace,**extra)
    if c['profile']!='components-to-composite-dag@1':
        return finish('blocked-within-horizon','unsupported-profile')
    if c['required_capability'] is None:
        return finish('awaiting-clarification','ambiguous-capability')
    if c['forced_cycle']:
        return finish('blocked-within-horizon','unsupported-cycle')
    domain=[n for n in c['candidates'] if n.get('capability')==c['required_capability']]
    if not domain: return finish('blocked-within-horizon','missing-capability')
    chosen=None
    for candidate in domain:
        if attempts>=c['budget']: return finish('partial','budget-exhausted')
        attempts+=1
        guards={
            'input_type': candidate['inputs'].get('message',{}).get('type')==c['source']['outputs']['message'],
            'output_type': candidate['outputs'].get('response')==c['sink']['inputs']['message']['type'],
            'locality': c['required_locality'] is None or candidate.get('locality')==c['required_locality'],
            'layer': candidate['layer']=='components',
        }
        accepted= method=='ungated-first' or all(guards.values())
        trace.append({'candidate':candidate['id'],'guards':guards,'accepted':accepted,'charged':1})
        if accepted: chosen=candidate; break
    if chosen is None: return finish('blocked-within-horizon','no-compatible-candidate')
    members=[c['source'],chosen,c['sink']]+c['additional_members']
    ids={n['id'] for n in members}
    edges=[[c['source']['id'],'message',chosen['id'],'message'],[chosen['id'],'response',c['sink']['id'],'message']]
    crossing=[e for e in c['ambient_edges'] if (e[0] in ids)!=(e[2] in ids)]
    # v0 deliberately models crossings only; v1 repairs required-unbound exposure.
    exposed=[]
    if method!='boundary-v0':
        occupied={(e[2],e[3]) for e in edges+crossing}
        exposed=[[n['id'],port] for n in members for port,spec in n['inputs'].items()
                 if spec.get('required') and (n['id'],port) not in occupied]
    composite=dict(id='composite:'+c['id'],layer='composite',members=[n['id'] for n in members],
                   member_records=members,edges=edges,crossings=crossing,exposed_required_inputs=exposed,
                   output_map=[c['sink']['id'],'result'])
    if True:
        composite['configuration']={n['id']:n.get('config',{}) for n in members}
        composite['dependency_refs']=sorted({d for n in members for d in n.get('dependencies',[])})
    residuals=[{'requirement':'behavior:faithful-summary','phase':'behavior','judgment':'unknown',
                'reason':'No generated application was executed'},
               {'requirement':'activation:resources','phase':'activation','judgment':'unknown',
                'reason':'References are described, not authenticated'}]
    return finish('design-closed',None,composite=composite,residuals=residuals,
                  requirement_accounting={'design:typed-assembly':'met','design:complete-boundary':'met',
                                          'behavior:faithful-summary':'unknown','activation:resources':'unknown'})

# Independent reference assessment: no invocation of selection/packaging helpers.
def assess(case,result):
    errors=[]; expected=case['oracle']
    if result['outcome']!=expected['outcome']: errors.append('outcome-mismatch')
    if expected.get('gap')!=result.get('gap'): errors.append('gap-mismatch')
    comp=result.get('composite')
    if comp:
        records={n['id']:n for n in comp['member_records']}
        if len(records)!=len(comp['member_records']): errors.append('identity-collision')
        if sorted(comp['members'])!=sorted(expected.get('members',[])): errors.append('membership-mismatch')
        for src,op,dst,ip in comp['edges']:
            if src not in records or dst not in records: errors.append('dangling-endpoint'); continue
            if records[src]['outputs'].get(op)!=records[dst]['inputs'].get(ip,{}).get('type'): errors.append('type-mismatch')
        if case['required_locality']:
            workers=[n for n in comp['member_records'] if n['role']=='transform' and n.get('capability')]
            if any(n.get('locality')!=case['required_locality'] for n in workers): errors.append('constraint-mismatch')
        if sorted(comp['exposed_required_inputs'])!=sorted(expected.get('boundary',[])): errors.append('unbound-input-loss')
        if sorted(comp['crossings'])!=sorted(expected.get('crossings',[])): errors.append('crossing-loss')
        original={n['id']:n for n in [case['source'],case['sink']]+case['candidates']+case['additional_members']}
        for oid,n in records.items():
            if n!=original.get(oid): errors.append('member-record-mutation')
        for oid,n in records.items():
            if comp.get('configuration',{}).get(oid)!=n.get('config',{}): errors.append('configuration-loss')
            if not set(n.get('dependencies',[])).issubset(comp.get('dependency_refs',[])): errors.append('dependency-loss')
        if result.get('requirement_accounting',{}).get('behavior:faithful-summary')!='unknown': errors.append('unsupported-behavior-claim')
    if result['attempts']>case['budget']: errors.append('budget-overrun')
    return dict(passed=not errors,errors=sorted(set(errors)),accepted_artifact=comp is not None)

def main(output_dir=None):
    out=Path(output_dir) if output_dir else ROOT/'observations'
    out.mkdir(parents=True,exist_ok=True)
    suite=cases()
    # Persist inputs/criteria before executing any procedure.
    (out/'cases.json').write_text(json.dumps(suite,indent=2)+'\n')
    manifest={'protocol_sha256':sha256((ROOT/'protocol.json').read_bytes()).hexdigest(),
              'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
              'cases_sha256':sha256((out/'cases.json').read_bytes()).hexdigest(),
              'scope':'synthetic finite structural candidate selection; not full Paper 2',
              'evaluation_exposure':'same-author exposed; no independently held-out claim'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    results=[]
    for case in suite:
        for method in ['ungated-first','boundary-v0','boundary-v1']:
            inp={k:deepcopy(v) for k,v in case.items() if k!='oracle'}
            r=generate(inp,method); r['assessment']=assess(case,r); r['collection']=case['collection']; results.append(r)
    summary=[]
    for collection in ['development','designated-evaluation-exposed']:
        for method in ['ungated-first','boundary-v0','boundary-v1']:
            rows=[r for r in results if r['collection']==collection and r['method']==method]
            summary.append(dict(collection=collection,method=method,cases=len(rows),
                                passes=sum(r['assessment']['passed'] for r in rows),
                                accepted_artifacts=sum(r['assessment']['accepted_artifact'] for r in rows),
                                invalid_accepted=sum(r['assessment']['accepted_artifact'] and not r['assessment']['passed'] for r in rows),
                                candidate_attempts=sum(r['attempts'] for r in rows)))
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # Assertions are study acceptance checks, not claims about arbitrary inputs.
    final=[r for r in results if r['method']=='boundary-v1']
    assert all(r['assessment']['passed'] for r in final),[(r['case'],r['assessment']) for r in final if not r['assessment']['passed']]
    assert any(not r['assessment']['passed'] for r in results if r['method']=='boundary-v0')
    assert any(not r['assessment']['passed'] for r in results if r['method']=='ungated-first')
    return dict(manifest=manifest,summary=summary,results=results)

if __name__=='__main__':
    print(json.dumps(main()['summary'],indent=2))
