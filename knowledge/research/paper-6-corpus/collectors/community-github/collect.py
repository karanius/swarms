import subprocess,json,pathlib,concurrent.futures,urllib.request,hashlib,datetime,time,threading
BASE=pathlib.Path(__file__).parent
QUERIES=['langflow templates','langflow workflows','langflow flows','langflow json','langflow tutorial','langflow rag','langflow agents','langflow examples']
def api(path):
 p=subprocess.run(['gh','api',path],capture_output=True)
 if p.returncode: raise RuntimeError(p.stderr.decode()[:250])
 return json.loads(p.stdout)
def raw(repo,rev,path):
 url='https://raw.githubusercontent.com/'+repo+'/'+rev+'/'+urllib.parse.quote(path)
 with urllib.request.urlopen(url,timeout=30) as r:return r.read(),url
repos={}; failures=[]
for q in QUERIES:
 try:
  d=json.loads((BASE/('search-'+q.replace(' ','-')+'.json')).read_text())
  (BASE/('search-'+q.replace(' ','-')+'.json')).write_text(json.dumps(d,indent=2))
  for r in d['items']:
   if r['owner']['login'].lower()!='langflow-ai': repos[r['full_name']]=r
 except Exception as e: failures.append({'query':q,'error':str(e)})
print('Discovered',len(repos),'repositories',flush=True)
lock=threading.Lock(); sources=[]; artifacts=[]
if (BASE/'manifest.json').exists():
 previous=json.loads((BASE/'manifest.json').read_text());sources=previous['sources'];artifacts=previous['artifacts'];failures=previous['failures']
 completed={s['repository'] for s in sources};repos={k:v for k,v in repos.items() if k not in completed}
 print('Resuming',len(repos),'remaining; completed',len(sources),flush=True)
def graphs(x):
 if isinstance(x,dict):
  if isinstance(x.get('nodes'),list) and isinstance(x.get('edges'),list) and any(isinstance(n,dict) and ('data' in n or 'type' in n) for n in x['nodes']):return True
  return any(graphs(v) for v in x.values() if isinstance(v,(dict,list)))
 if isinstance(x,list):return any(graphs(v) for v in x)
 return False
def collect(item):
 repo,r=item; fs=[]; arts=[]
 try:
  rev=api('repos/'+repo+'/commits/'+r['default_branch'])['sha']
  tr=api('repos/'+repo+'/git/trees/'+rev+'?recursive=1')
  tree=tr['tree']; license_status={'status':'unknown','spdx':None,'files':[]}
  if r.get('license'):license_status['spdx']=r['license'].get('spdx_id')
  licenses=[f for f in tree if f['type']=='blob' and f['path'].split('/')[-1].lower() in ['license','license.md','license.txt','copying','copying.md','notice','notice.txt'] and f.get('size',0)<200000]
  for f in licenses[:10]:
   try:
    b,url=raw(repo,rev,f['path']); out=BASE/'licenses'/repo/f['path'];out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);license_status['files'].append(str(out.relative_to(BASE)))
   except Exception as e:fs.append({'repository':repo,'path':f['path'],'error':str(e)})
  if license_status['files']:license_status['status']='license-text-collected; review-required'
  candidates=[f for f in tree if f['type']=='blob' and f['path'].lower().endswith('.json') and 20<f.get('size',0)<8000000 and not any(p in f['path'].split('/') for p in ['node_modules','.venv','venv','package-lock.json','pnpm-lock.json'])]
  for f in candidates[:500]:
   try:
    b,url=raw(repo,rev,f['path']); j=json.loads(b)
    if not graphs(j):continue
    out=BASE/'artifacts'/repo/f['path'];out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
    arts.append({'file':str(out.relative_to(BASE)),'sha256':hashlib.sha256(b).hexdigest(),'sourceUrl':url,'repository':repo,'revision':rev,'sourcePath':f['path'],'license':license_status,'collectionKind':'community-github-json-graph','collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(b),'fork':r.get('fork',False)})
   except (json.JSONDecodeError,UnicodeDecodeError):pass
   except Exception as e:fs.append({'repository':repo,'path':f['path'],'error':str(e)})
  s={'repository':repo,'url':r['html_url'],'revision':rev,'defaultBranch':r['default_branch'],'fork':r.get('fork',False),'license':license_status,'treeTruncated':tr.get('truncated',False),'jsonCandidates':len(candidates),'jsonCandidatesExamined':min(500,len(candidates)),'artifactCount':len(arts)}
 except Exception as e:
  s={'repository':repo,'artifactCount':0};fs.append({'repository':repo,'error':str(e)})
 with lock:
  sources.append(s);artifacts.extend(arts);failures.extend(fs)
  (BASE/'manifest.json').write_text(json.dumps({'collector':'community-github','queries':QUERIES,'sources':sources,'artifacts':artifacts,'failures':failures},indent=2))
  if arts or len(sources)%10==0:print('Progress',len(sources),'/',len(repos),repo,'graphs',len(arts),'total',len(artifacts),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:list(ex.map(collect,repos.items()))
print('DONE',len(sources),len(artifacts),len(failures),flush=True)
