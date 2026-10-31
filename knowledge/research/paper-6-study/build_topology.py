"""Extract source graphs as data only. Never import or execute corpus node code."""
import collections, hashlib, importlib.util, json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'paper-6-corpus'

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def handle(edge,side):
 value=edge.get('data',{}).get(side+'Handle') or edge.get(side+'Handle')
 if isinstance(value,dict):return value
 if isinstance(value,str):
  try:return json.loads(value.replace('œ','"'))
  except ValueError:return {'unparsed':True}
 return {}
def extract(g,gid):
 nodes=[];warnings=[];ids=set()
 for raw in g['nodes']:
  data=raw.get('data',{});native=data.get('node',{});nid=str(raw.get('id',''))
  if not nid or nid in ids:warnings.append('missing-or-duplicate-node-id');continue
  ids.add(nid)
  typ=data.get('type')
  if typ=='note' or raw.get('type')=='note':continue
  if not typ:typ='Unknown';warnings.append('unknown-component-type')
  outputs=[]
  for o in native.get('outputs',[]) or []:
   if isinstance(o,dict):outputs.append({'name':o.get('name'),'types':o.get('types',[]),'selected':o.get('selected')})
  template=native.get('template',{});inputs=[];resources=[]
  if isinstance(template,dict):
   for k,v in template.items():
    if not isinstance(v,dict) or k=='code':continue
    inputs.append({'name':k,'types':v.get('input_types',[]),'required':v.get('required'),'dynamic':v.get('dynamic',False)})
    if v.get('password') or v.get('load_from_db'):resources.append({'field':k,'kind':'credential-or-external-binding','required':v.get('required')})
  pos=raw.get('position',{})
  nodes.append({'id':nid,'type':typ,'label':native.get('display_name') or data.get('display_name') or typ,'version':native.get('lf_version') or 'unknown','inputs':inputs,'outputs':outputs,'resourceRequirements':resources,'position':{'x':pos.get('x',0),'y':pos.get('y',0)}})
 lookup={n['id']:n for n in nodes};edges=[]
 for i,raw in enumerate(g['edges']):
  s=str(raw.get('source',''));t=str(raw.get('target',''));sh=handle(raw,'source');th=handle(raw,'target')
  if s not in lookup or t not in lookup:warnings.append('edge-with-unresolved-or-note-endpoint')
  if sh.get('unparsed') or th.get('unparsed'):warnings.append('unparsed-handle')
  edges.append({'id':str(i),'source':s,'target':t,'sourcePort':sh.get('name'),'targetPort':th.get('fieldName') or th.get('name'),'outputTypes':sh.get('output_types',[]),'inputTypes':th.get('inputTypes',[]),'resolved':s in lookup and t in lookup,'sourceType':lookup.get(s,{}).get('type'),'targetType':lookup.get(t,{}).get('type')})
 return {'id':gid,'nodes':nodes,'edges':edges,'warnings':dict(collections.Counter(warnings))}
def main():
 index_bytes=(BASE/'index.json').read_bytes();index=json.loads(index_bytes)
 spec=importlib.util.spec_from_file_location('corpus_index',BASE/'index_corpus.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 out=BASE/'topology';(out/'graphs').mkdir(parents=True,exist_ok=True)
 byhash=collections.defaultdict(list)
 for a in index['artifacts']:
  if a.get('graphFormat')=='langflow':byhash[a['sha256']].append(a)
 summaries=[];failures=[];totals=collections.Counter()
 for sha,origins in sorted(byhash.items()):
  a=origins[0]
  try:
   content=(BASE/a['file']).read_bytes()
   if hashlib.sha256(content).hexdigest()!=sha:raise ValueError('source hash mismatch')
   document=json.loads(content);descriptions={d['pointer']:d for d in a['graphs']}
   for pointer,g in mod.walk(document):
    desc=descriptions.get(pointer)
    if not desc or desc.get('format')!='langflow':continue
    gid=digest([sha,pointer]);graph=extract(g,gid)
    provenance=[{k:x.get(k) for k in ['sourceUrl','sourcePath','repository','revision','collector','file','licenseAssessment']} for x in origins]
    graph.update({'name':document.get('name') if isinstance(document,dict) else None,'pointer':pointer,'sha256':sha,'sources':provenance,'fixture':all(x.get('fixture',False) for x in origins),'mixedFixtureOrigins':len({x.get('fixture',False) for x in origins})>1})
    graph['name']=graph['name'] or Path(a['sourcePath']).stem
    (out/'graphs'/f'{gid}.json').write_text(json.dumps(graph,separators=(',',':')))
    pairs=sorted({(e['sourceType'],e['targetType']) for e in graph['edges'] if e['resolved']})
    types=sorted({n['type'] for n in graph['nodes']})
    summaries.append({k:graph[k] for k in ['id','name','fixture','mixedFixtureOrigins','warnings','pointer','sha256']}|{'types':types,'pairs':pairs,'nodeCount':len(graph['nodes']),'edgeCount':len(graph['edges']),'repositories':sorted({x.get('repository') or x.get('sourceUrl') for x in origins}),'sourceCount':len(origins),'source':provenance[0]})
    totals.update(nodes=len(graph['nodes']),edges=len(graph['edges']),graphs=1)
  except Exception as exc:failures.append({'file':a['file'],'error':str(exc)})
 result={'schemaVersion':1,'indexSha256':hashlib.sha256(index_bytes).hexdigest(),'counts':dict(totals),'corpusCounts':index['counts'],'graphs':summaries,'failures':failures,'semantics':{'overview':'Directed type-pair projection; edge weight is number of distinct byte-content graph occurrences containing that pair. Not semantic independence.','clusters':'Louvain communities on the undirected weighted type projection; structural groups only, not composite definitions.','detail':'Each graph preserves scoped occurrence IDs and all recorded edges. No workflow execution. Credential values and node code are never exported.'}}
 (out/'index.json').write_text(json.dumps(result,separators=(',',':')))
 print(json.dumps({'counts':dict(totals),'distinctArtifacts':len(byhash),'failures':len(failures),'indexBytes':(out/'index.json').stat().st_size}))
if __name__=='__main__':main()
