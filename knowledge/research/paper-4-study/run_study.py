from pathlib import Path
from copy import deepcopy
import hashlib,json,sys,platform

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from controller import run,reassess_evidence,VERSION
from cases import build
from assessor import check,mutation_checks


def main():
    out=ROOT/'observations';out.mkdir(exist_ok=True)
    suite=build();(out/'cases.json').write_text(json.dumps(suite,indent=2)+'\n')
    files=['protocol.json','controller.py','cases.py','assessor.py','run_study.py']
    manifest={'version':VERSION,'python':platform.python_version(),'implementation_files':{},
              'case_count':len(suite),'exposure':'same-author exposed; not independent held-out evaluation'}
    for f in files:manifest['implementation_files'][f]=hashlib.sha256((ROOT/f).read_bytes()).hexdigest()
    manifest['cases_sha256']=hashlib.sha256((out/'cases.json').read_bytes()).hexdigest()
    # Save exact snapshots before any generator invocation; never overwrite earlier freeze.
    freeze_id=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()[:12]
    freeze=ROOT/'freezes'/freeze_id;freeze.mkdir(parents=True,exist_ok=True)
    for f in files:
        target=freeze/f
        if not target.exists():target.write_bytes((ROOT/f).read_bytes())
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    results=[]
    for c in suite:
        for method in ['boundary','fifo','greedy']:
            r=run({k:deepcopy(v) for k,v in c.items() if k!='oracle'},method)
            r['collection']=c['collection'];r['assessment']=check(c,r);results.append(r)
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    summary=[]
    for coll in sorted({c['collection'] for c in suite}):
        for method in ['boundary','fifo','greedy']:
            rows=[r for r in results if r['collection']==coll and r['method']==method]
            summary.append({'collection':coll,'method':method,'cases':len(rows),
                            'passes':sum(r['assessment']['passed'] for r in rows),
                            'closed':sum(r['outcome']=='design-closed' for r in rows),
                            'invalid_accepted':sum(r['assessment']['invalid_accepted'] for r in rows),
                            'operations':sum(r['attempts'] for r in rows),'backtracks':sum(r['backtracks'] for r in rows)})
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    reference_case=next(c for c in suite if c['id']=='D-decompose')
    good=next(r for r in results if r['case']=='D-decompose' and r['method']=='boundary')
    negatives=mutation_checks(reference_case,good)
    (out/'negative-checks.json').write_text(json.dumps(negatives,indent=2)+'\n')
    evidence={'versions':{'model':'1','tool':'1'},'support':['analysis:1'],'contradiction':[]}
    records=[]
    for label,rec,versions in [('current',evidence,{'model':'1','tool':'1'}),
                              ('changed-model',evidence,{'model':'2','tool':'1'}),
                              ('changed-transitive-tool',evidence,{'model':'1','tool':'2'}),
                              ('conflicted',dict(evidence,contradiction=['counterexample:1']),{'model':'1','tool':'1'})]:
        records.append({'condition':label,'result':reassess_evidence(rec,versions)})
    (out/'evidence-reassessment.json').write_text(json.dumps(records,indent=2)+'\n')
    # Exploratory budget sweep on exposed cases, not confirmatory independent trials.
    sweeps=[]
    for cid in ['E-backtrack','E-three-step','E-conflict-priority']:
        c=next(c for c in suite if c['id']==cid)
        for budget in [4,12,24,48,96,160]:
            for method in ['boundary','fifo','greedy']:
                cc=deepcopy(c);cc['limits']['attempts']=budget
                r=run({k:v for k,v in cc.items() if k!='oracle'},method)
                sweeps.append({'case':cid,'budget':budget,'method':method,'outcome':r['outcome'],
                               'gap':r['gap'],'operations':r['attempts'],'backtracks':r['backtracks']})
    (out/'budget-sweep.json').write_text(json.dumps(sweeps,indent=2)+'\n')
    checks={'no_invalid_acceptance':all(not r['assessment']['invalid_accepted'] for r in results),
            'boundary_suite':all(r['assessment']['passed'] for r in results if r['method']=='boundary'),
            'negative_checks_detected':all(not x['passed'] for x in negatives.values()),
            'evidence_expected':[x['result']['judgment'] for x in records]==['met','unknown','unknown','unknown']}
    (out/'acceptance.json').write_text(json.dumps(checks,indent=2)+'\n')
    return {'summary':summary,'results':results,'checks':checks,'sweeps':sweeps,'negatives':negatives,'evidence':records,'manifest':manifest}

if __name__=='__main__':
    result=main();print(json.dumps({'summary':result['summary'],'checks':result['checks'],
       'failures':[(r['case'],r['method'],r['outcome'],r['gap'],r['assessment']['errors']) for r in result['results'] if not r['assessment']['passed']]},indent=2))
