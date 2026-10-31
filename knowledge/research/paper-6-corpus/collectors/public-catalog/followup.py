import importlib.util,json,pathlib,urllib.parse,datetime,hashlib
p=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location('collector',p/'collect.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
m=json.loads((p/'manifest.json').read_text());c.M=m;c.seen={a['sourceUrl'] for a in m['artifacts']}
start=len(m['artifacts'])
for s in list(m['sources']):
 for url in set(s.get('downloadLinks',[])):
  if not url.startswith('https://github.com/') or '/blob/' not in url or not url.endswith('.json'):continue
  parts=urllib.parse.urlparse(url).path.strip('/').split('/');repo='/'.join(parts[:2]);branch=parts[3];path=urllib.parse.unquote('/'.join(parts[4:]))
  try:
   info=json.loads(c.get('https://api.github.com/repos/'+repo+'/commits/'+branch));rev=info['sha'];license='No explicit license returned by GitHub API';licensefile=None
   try:
    li=json.loads(c.get('https://api.github.com/repos/'+repo+'/license?ref='+rev));license=li.get('license',{}).get('spdx_id','NOASSERTION');raw=c.get(li['download_url']);licensefile='evidence/license-'+repo.replace('/','--')+'-'+rev[:12]+'.txt';(p/licensefile).write_bytes(raw)
   except Exception as e:m['failures'].append({'url':'https://api.github.com/repos/'+repo+'/license?ref='+rev,'error':str(e),'phase':'followup-license'})
   rawurl='https://raw.githubusercontent.com/'+repo+'/'+rev+'/'+urllib.parse.quote(path)
   c.save(rawurl,s['url'],repo,rev,path,license,'official-blog-github')
   if len(m['artifacts'])>start:
    a=m['artifacts'][-1]
    if a['sourceUrl']==rawurl:a['originalLinkedUrl']=url;a['licenseFile']=licensefile
   m['sources'].append({'url':url,'discoveryUrl':s['url'],'kind':'official-blog-github','repository':repo,'revision':rev,'license':license,'licenseFile':licensefile,'collectedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
  except Exception as e:m['failures'].append({'url':url,'error':str(e),'phase':'followup'})
m['followup']={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'addedArtifacts':len(m['artifacts'])-start,'hf429GapCount':sum('429' in f.get('error','') for f in m['failures']),'hfRetryEligibility':'Unknown: original HTTPError records did not preserve Retry-After or rate-limit reset headers. No retries performed; no evidence establishes stated cooldown elapsed.'}
for a in m['artifacts']:assert hashlib.sha256((p/a['file']).read_bytes()).hexdigest()==a['sha256']
(p/'manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps(m['followup'],indent=2));print('Final',len(m['artifacts']),'unique',len(set(a['sha256'] for a in m['artifacts'])))
