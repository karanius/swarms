import ast,json,pathlib,subprocess,urllib.request,urllib.parse,hashlib,datetime,concurrent.futures
BASE=pathlib.Path(__file__).parent
source=ast.parse((BASE/'collect.py').read_text())
for n in source.body:
 if isinstance(n,ast.FunctionDef) and n.name in ['api','raw','graphs']:exec(compile(ast.Module(body=[n],type_ignores=[]),'collector-helpers','exec'))
d=json.loads((BASE/'manifest.json').read_text()); caps=[s for s in d['sources'] if s.get('jsonCandidates',0)>s.get('jsonCandidatesExamined',0)];pending=[]
for s in caps:
 tree=api('repos/'+s['repository']+'/git/trees/'+s['revision']+'?recursive=1')['tree']
 cand=[f for f in tree if f['type']=='blob' and f['path'].lower().endswith('.json') and 20<f.get('size',0)<8000000 and not any(p in f['path'].split('/') for p in ['node_modules','.venv','venv','package-lock.json','pnpm-lock.json'])]
 for f in cand[s['jsonCandidatesExamined']:]:pending.append((s,f['path']))
for fail in d['failures']:
 if 'path' in fail:
  s=next(s for s in d['sources'] if s['repository']==fail['repository']);pending.append((s,fail['path']))
results=[]
def inspect(item):
 s,path=item
 try:
  b,url=raw(s['repository'],s['revision'],path);j=json.loads(b)
  if graphs(j):
   out=BASE/'artifacts'/s['repository']/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
   a={'file':str(out.relative_to(BASE)),'sha256':hashlib.sha256(b).hexdigest(),'sourceUrl':url,'repository':s['repository'],'revision':s['revision'],'sourcePath':path,'license':s['license'],'collectionKind':'community-github-json-graph','collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(b),'fork':s.get('fork',False)}
  else:a=None
  return {'repository':s['repository'],'path':path,'status':'collected-graph' if a else 'no-graph','artifact':a}
 except Exception as e:return {'repository':s['repository'],'path':path,'status':'failed','error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:results=list(ex.map(inspect,pending))
for r in results:
 if r.get('artifact') and not any(a['file']==r['artifact']['file'] for a in d['artifacts']):d['artifacts'].append(r['artifact'])
for s in caps:
 failed=[r for r in results if r['repository']==s['repository'] and r['status']=='failed'];s['initialJsonCandidatesExamined']=s['jsonCandidatesExamined'];s['jsonCandidatesExamined']=s['jsonCandidates']-len(failed);s['remainingPaths']=[r['path'] for r in failed]
for s in d['sources']:s['artifactCount']=sum(a['repository']==s['repository'] for a in d['artifacts'])
d['followupSweep']=[{k:v for k,v in r.items() if k!='artifact'} for r in results]
(BASE/'manifest.json').write_text(json.dumps(d,indent=2));print('Swept',len(results),'remaining failures',sum(r['status']=='failed' for r in results),'artifacts',len(d['artifacts']))
