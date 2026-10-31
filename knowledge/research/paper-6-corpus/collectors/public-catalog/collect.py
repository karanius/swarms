import urllib.request,urllib.parse,json,re,hashlib,pathlib,datetime,concurrent.futures,threading
ROOT=pathlib.Path(__file__).parent; (ROOT/'artifacts').mkdir(exist_ok=True);(ROOT/'evidence').mkdir(exist_ok=True)
M={'collector':'public-catalog','sources':[],'artifacts':[],'failures':[]};lock=threading.Lock();seen=set()
def get(u):
 req=urllib.request.Request(u,headers={'User-Agent':'Public-Langflow-Template-Research/1.0'})
 with urllib.request.urlopen(req,timeout=25) as r:
  b=r.read(12000000)
  if len(b)>=12000000: raise ValueError('size cap')
  return b

def graph(j):
 if isinstance(j,dict):
  if isinstance(j.get('nodes'),list) and isinstance(j.get('edges'),list) and j['nodes']:return True
  return any(graph(v) for v in j.values())
 if isinstance(j,list):return any(graph(v) for v in j)
 return False

def save(u,source,repo=None,revision=None,path=None,license='No explicit license found; publicly accessible does not imply reuse permission',kind='website-download'):
 with lock:
  if u in seen:return
  seen.add(u)
 try:
  b=get(u);j=json.loads(b)
  if not graph(j):return
  sha=hashlib.sha256(b).hexdigest();name=re.sub('[^a-zA-Z0-9._-]','_',path or urllib.parse.unquote(urllib.parse.urlparse(u).path.split('/')[-1]))[-120:]
  f='artifacts/'+sha[:12]+'-'+name
  (ROOT/f).write_bytes(b)
  with lock:M['artifacts'].append({'file':f,'sha256':sha,'sourceUrl':u,'discoveryUrl':source,'repository':repo,'revision':revision,'sourcePath':path or urllib.parse.urlparse(u).path,'license':license,'collectionKind':kind,'collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(b)})
 except Exception as e:
  with lock:M['failures'].append({'url':u,'error':str(e),'discoveryUrl':source})
def scanpage(u):
 try:
  s=get(u).decode(); links=re.findall(r'(?:href|src)=["\']([^"\']+)',s)
  useful=[]
  for x in links:
   x=urllib.parse.urljoin(u,x.replace('&amp;','&'))
   if '.json' in x.lower() or 'gist.github' in x:useful.append(x)
  with lock:M['sources'].append({'url':u,'kind':'official-blog','downloadLinks':useful})
  for x in useful:
   if '.json' in x.lower():save(x,u)
   elif 'gist.github.com' in x:
    gid=x.split('/')[-1].split('#')[0].split('?')[0]
    try:
     gj=json.loads(get('https://api.github.com/gists/'+gid));revision=gj.get('history',[{}])[0].get('version')
     for fn,d in gj.get('files',{}).items():
      if fn.endswith('.json'):save(d['raw_url'],u,'gist:'+gid,revision,fn,kind='official-blog-gist')
    except Exception as e:
     with lock:M['failures'].append({'url':x,'error':str(e)})
 except Exception as e:
  with lock:M['failures'].append({'url':u,'error':str(e)})
def hf(repo):
 u='https://huggingface.co/api/spaces/'+repo
 try:
  info=json.loads(get(u));rev=info['sha']; files=info.get('siblings',[]);license=info.get('cardData',{}).get('license','No explicit license declared in Space card')
  js=[x['rfilename'] for x in files if x['rfilename'].lower().endswith('.json')]
  with lock:M['sources'].append({'url':'https://huggingface.co/spaces/'+repo,'kind':'huggingface-space','revision':rev,'jsonCandidates':js,'license':license})
  for p in js:save('https://huggingface.co/spaces/'+repo+'/resolve/'+rev+'/'+urllib.parse.quote(p),'https://huggingface.co/spaces/'+repo,repo,rev,p,license,'huggingface-space')
 except Exception as e:
  with lock:M['failures'].append({'url':u,'error':str(e)})
if __name__=='__main__':
 sitemap=get('https://www.langflow.org/sitemap.xml');(ROOT/'evidence/sitemap.xml').write_bytes(sitemap)
 pages=[x for x in re.findall(r'<loc>(.*?)</loc>',sitemap.decode()) if '/blog/' in x]
 print('Blog pages',len(pages),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(scanpage,pages))
 (ROOT/'manifest.json').write_text(json.dumps(M,indent=2));print('Blog artifacts',len(M['artifacts']),flush=True)
 spaces=get('https://huggingface.co/api/spaces?search=langflow&limit=1000');(ROOT/'evidence/huggingface-search.json').write_bytes(spaces)
 repos=[r['id'] for r in json.loads(spaces)];print('HF spaces',len(repos),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(hf,repos))
 (ROOT/'manifest.json').write_text(json.dumps(M,indent=2));print('Done',len(M['artifacts']),'artifacts',len(M['failures']),'failures',flush=True)
