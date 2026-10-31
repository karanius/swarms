"""Research-only adapter to native Langflow's flow-builder; no canvas/backend authority."""
import json,hashlib,inspect,copy
from lfx.graph.flow_builder.builder import load_local_registry,build_flow_from_spec
from lfx.graph.flow_builder.spec import parse_flow_spec
ALLOWED=('ChatInput','Agent','ChatOutput')
def catalog():
 registry=load_local_registry()
 return {key:copy.deepcopy(registry[key]) for key in ALLOWED}
def describe(name):
 if name not in ALLOWED:raise ValueError('Type outside this pinned research alphabet')
 entry=catalog()[name]
 return {'type':name,'template':{k:{p:v for p,v in val.items() if p in ('type','required','input_types','options','info','display_name','advanced','list')} for k,val in entry['template'].items() if isinstance(val,dict) and k!='code'},'outputs':entry.get('outputs',[]),'scope':'Bundled static builder catalog, not live-port evidence'}
def build(spec):
 if len(spec)>15000:raise ValueError('Research spec too large')
 parsed=parse_flow_spec(spec)
 if not 1<=len(parsed['nodes'])<=20 or len(parsed['edges'])>35:raise ValueError('Research graph budget exceeded')
 if any(n['type'] not in ALLOWED for n in parsed['nodes']):raise ValueError('Only pinned native research types allowed')
 if len({n['id'] for n in parsed['nodes']})!=len(parsed['nodes']):raise ValueError('Duplicate spec aliases')
 # No supplied source code, keys, provider selection or external side effects.
 for alias,fields in parsed.get('config',{}).items():
  for field,value in fields.items():
   if field not in ('system_prompt','input_value','should_store_message'):raise ValueError('Configuration field not authorized for this research build: '+field)
   if not isinstance(value,(str,bool)) or len(str(value))>5000:raise ValueError('Invalid bounded configuration')
 result=build_flow_from_spec(spec,registry=catalog())
 if 'error' in result:return result
 flow=result['flow'];nodes=flow['data']['nodes'];edges=flow['data']['edges']
 # Retain native graph unmodified separately. A compact identity map is a projection.
 return {'nativeFlow':flow,'aliasToNativeId':result.get('node_id_map',{}),'summary':{'name':result.get('name'),'nodeCount':len(nodes),'edgeCount':len(edges),'nodes':[{'id':n['id'],'type':n['data'].get('type'),'displayName':n['data'].get('node',{}).get('display_name')} for n in nodes]},'provenance':{'engine':'lfx.graph.flow_builder.builder.build_flow_from_spec','engineSha256':hashlib.sha256(inspect.getsource(build_flow_from_spec).encode()).hexdigest(),'registrySha256':hashlib.sha256(json.dumps(catalog(),sort_keys=True).encode()).hexdigest(),'scope':'Actual native graph assembly, static only; no component or provider execution; no active canvas mutation'}}
