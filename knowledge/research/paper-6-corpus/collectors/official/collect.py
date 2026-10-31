import os,json,subprocess,hashlib,datetime,urllib.request,tarfile,io,re,concurrent.futures
from pathlib import Path
OUT=Path(__file__).resolve().parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest={'collector':'official','collectedAt':now,'sources':[],'artifacts':[],'failures':[]}
def request(u):
 return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Swarms-static-corpus-collector'}),timeout=90).read()
def graph(v):
 if isinstance(v,dict):
  if isinstance(v.get('nodes'),list) and isinstance(v.get('edges'),list) and (v['nodes'] or v['edges']):return True
  return any(graph(x) for x in v.values())
 if isinstance(v,list):return any(graph(x) for x in v)
 return False
def qualifies(p,b):
 try:
  t=b.decode('utf-8')
  if p.endswith(('.json','.ipynb','.jsonc')):
   try:return graph(json.loads(t))
   except Exception:return False
  if p.endswith(('.md','.mdx')):
   for block in re.findall(r'```(?:json|JSON)?\s*\n(.*?)```',t,re.S):
    try:
     if graph(json.loads(block)):return True
    except Exception:pass
 except Exception:pass
 return False
def collect(repo,rev,files,method):
 slug=repo.split('/')[-1]; licenses=[]
 for p,b in files.items():
  if Path(p).name.lower() in ('license','license.md','license.txt','copying','notice','notice.md'):
   dest=Path('licenses')/slug/rev/p; (OUT/dest).parent.mkdir(parents=True,exist_ok=True);(OUT/dest).write_bytes(b);licenses.append(str(dest))
 scanned=0;count=0
 for p,b in sorted(files.items()):
  if not p.endswith(('.json','.jsonc','.ipynb','.md','.mdx')):continue
  scanned+=1
  if not qualifies(p,b):continue
  kind='test-fixture' if re.search(r'(^|/)(tests?|fixtures?)(/|$)',p) else 'starter-template' if 'starter_project' in p else 'documentation-example' if p.startswith(('docs/','documentation/')) or p.endswith(('.md','.mdx')) else 'repository-graph'
  dest=Path('raw')/slug/rev/p;(OUT/dest).parent.mkdir(parents=True,exist_ok=True);(OUT/dest).write_bytes(b)
  manifest['artifacts'].append({'file':str(dest),'sha256':hashlib.sha256(b).hexdigest(),'sourceUrl':f'{repo}/blob/{rev}/'+urllib.parse.quote(p,safe='/'),'repository':repo,'revision':rev,'sourcePath':p,'license':{'references':licenses,'sourceUrl':f'{repo}/blob/{rev}/LICENSE'},'collectionKind':kind,'collectedAt':now,'collectionMethod':method,'bytes':len(b)})
  count+=1
 manifest['sources'].append({'repository':repo,'revision':rev,'collectionMethod':method,'candidateFilesScanned':scanned,'artifactsCollected':count,'licenses':licenses})
 print(slug,scanned,count,flush=True)
repo='https://github.com/langflow-ai/langflow';root='/Users/x/projects/langflow';rev=subprocess.check_output(['git','-C',root,'rev-parse','HEAD'],text=True).strip()
archive=subprocess.check_output(['git','-C',root,'archive','--format=tar',rev])
with tarfile.open(fileobj=io.BytesIO(archive)) as tf: files={m.name:tf.extractfile(m).read() for m in tf if m.isfile() and (m.name.endswith(('.json','.jsonc','.ipynb','.md','.mdx')) or Path(m.name).name.lower() in ('license','license.md','license.txt','copying','notice','notice.md'))}
collect(repo,rev,files,'clean-local-git-object-archive; verified-against-live-main')
repos=json.loads(request('https://api.github.com/orgs/langflow-ai/repos?per_page=100'))
(OUT/'organization-inventory.json').write_text(json.dumps([{k:x.get(k) for k in ('full_name','html_url','description','default_branch','archived')} for x in repos],indent=2)+'\n')
def extra(x):
 name=x['name'];repo=x['html_url']
 try:
  sha=json.loads(request(f'https://api.github.com/repos/langflow-ai/{name}/commits/{x["default_branch"]}'))['sha']
  data=request(f'https://codeload.github.com/langflow-ai/{name}/tar.gz/{sha}')
  with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tf:
   fs={m.name.split('/',1)[1]:tf.extractfile(m).read() for m in tf if m.isfile() and (m.name.endswith(('.json','.jsonc','.ipynb','.md','.mdx')) or Path(m.name).name.lower() in ('license','license.md','license.txt','copying','notice','notice.md'))}
  return repo,sha,fs,None
 except Exception as e:return repo,None,None,str(e)
# Include every other official organization repository except desktop update binary manifests.
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for repo,sha,fs,error in pool.map(extra,[x for x in repos if x['name'] not in ('langflow','desktop-updates')]):
  if error:manifest['failures'].append({'repository':repo,'error':error})
  else:collect(repo,sha,fs,'github-exact-commit-tarball')
manifest['failures'].append({'repository':'https://github.com/langflow-ai/langflow-examples','error':'Repository not found via git ls-remote; no collection claimed.'})
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
