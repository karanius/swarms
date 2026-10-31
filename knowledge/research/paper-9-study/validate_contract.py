"""Contract verification utilities. Does not run research or enforce a deployed system."""
from pathlib import Path
import json
from jsonschema import Draft202012Validator,FormatChecker
D=Path(__file__).resolve().parent

def load_spec():return json.loads((D/'market-intelligence.instance.json').read_text())
def load_schema():return json.loads((D/'artifacts.schema.json').read_text())

def validate_spec(s):
 errors=[]
 required=['schema_version','business_id','instance_id','processes','flows','composites','components','observers','configuration','guards','guard_context_contract','lifecycle','policies','handoffs','persistence_contract']
 for k in required:
  if k not in s:errors.append('Missing instance section: '+k)
 if errors:return errors
 for binding in s.get('schema_bindings',[])+([s['validator_binding']] if s.get('validator_binding') else []):
  import hashlib
  path=(D/binding['path']).resolve()
  if not path.is_relative_to(D.resolve()) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=binding['sha256']:errors.append('Schema/validator binding changed: '+binding['path'])
 if s['business_id']!='local-content-business' or s['instance_id']!='market-intelligence':errors.append('Business/instance identity mismatch')
 types=set(load_schema()['$defs']);composites={c['id']:c for c in s['composites']};flow_ids={f['id'] for f in s['flows']};observers={o['id']:o for o in s['observers']}
 if len(composites)!=len(s['composites']):errors.append('Duplicate composite identity')
 if len(flow_ids)!=len(s['flows']):errors.append('Duplicate flow identity')
 for occurrence in s['components'].get('native_occurrences',[]):
  import hashlib
  native_path=Path(occurrence['source_path'])
  if not native_path.is_file() or hashlib.sha256(native_path.read_bytes()).hexdigest()!=occurrence['source_sha256']:errors.append('Native definition changed: '+occurrence['id'])
 for resource in s['components'].get('resource_adapters',[]):
  import hashlib
  path=(D/resource['path']).resolve()
  if not path.is_relative_to(D.resolve()) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=resource['sha256']:errors.append('Resource changed: '+resource['id'])
 for c in s['composites']:
  if c['acceptance_policy'] not in s['policies']:errors.append('Unknown acceptance policy')
  if c.get('status')=='implementation-bound':
   import hashlib
   graph=c['internal_graph'];path=(D/graph['path']).resolve()
   if not path.is_relative_to(D.resolve()) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=graph['sha256']:errors.append('Native graph binding missing or changed')
   resource=c.get('resource_binding',{});rp=(D/resource.get('path','missing')).resolve()
   if not rp.is_relative_to(D.resolve()) or not rp.is_file() or hashlib.sha256(rp.read_bytes()).hexdigest()!=resource.get('source_sha256'):errors.append('Capability resource missing or changed')
  elif c['internal_graph'] is not None or c['native_occurrence_refs']:errors.append('Contract-only composite unexpectedly bound')
  for t in [*c['input_ports'].values(),*c['output_ports'].values()]:
   if t not in types:errors.append('Unknown composite artifact type: '+t)
 all_nodes=set()
 for f in s['flows']:
  available={'input.'+p:t for p,t in f['external_inputs'].items()}
  available.update({'observer.'+p:t for o in s['observers'] for p,t in o['output_bindings'].items()})
  seen=set()
  for node in f['nodes']:
   ident=node['id'];all_nodes.add(ident)
   if ident in seen:errors.append('Duplicate node: '+ident)
   seen.add(ident)
   c=composites.get(node['composite_ref'])
   if not c:errors.append('Unknown composite: '+ident);continue
   if set(node['bindings'])!=set(c['input_ports']):errors.append('Incomplete or extra bindings: '+ident)
   for port,expected in c['input_ports'].items():
    binding=node['bindings'].get(port)
    if binding not in available:errors.append('Unavailable input: '+ident+'.'+port)
    elif available[binding]!=expected:errors.append('Type mismatch: '+ident+'.'+port)
   if node['observer_ref'] not in observers:errors.append('Attempt has no observer: '+ident)
   for gate in [node['entry_gate'],node.get('additional_gate')]:
    if gate and gate not in s['guards']:errors.append('Unknown gate: '+str(gate))
   available.update({ident+'.'+port:t for port,t in c['output_ports'].items()})
  for port,binding in f['result_bindings'].items():
   if binding not in available:errors.append('Unavailable flow output: '+f['id']+'.'+port)
 for p in s['processes']:
  if not set(p['flow_refs'])<=flow_ids:errors.append('Unknown process flow')
  if not set(p['owns_nodes'])<=all_nodes:errors.append('Unknown owned node')
  if p['owner_role'] not in s['configuration']['role_bindings']:errors.append('Unknown owner role')
 owned=[n for p in s['processes'] for n in p['owns_nodes']]
 if set(owned)!=all_nodes or len(owned)!=len(set(owned)):errors.append('Every node needs exactly one process owner')
 producers=s['guard_context_contract']['producers']
 for name,g in s['guards'].items():
  if set(g)!= {'all'} or not g['all']:errors.append('Unsupported or empty guard: '+name)
  if not set(g['all'])<=set(producers):errors.append('Guard context has no producer: '+name)
 states=set(s['lifecycle']['states'])
 for t in s['lifecycle']['transitions']:
  if t['from'] not in states or t['to'] not in states:errors.append('Unknown lifecycle state')
  if t['guard'] and t['guard'] not in s['guards']:errors.append('Unknown lifecycle guard')
  if t['actor_role'] not in s['configuration']['role_bindings']:errors.append('Unknown transition actor')
 for t in s['lifecycle']['cross_cutting_transitions']:
  origins=t['from'] if isinstance(t['from'],list) else ([t['from']] if t['from']!='active' else s['lifecycle']['active_states'])
  if not set(origins)<=states or t['to'] not in states:errors.append('Unknown exception state')
  if t.get('guard') and t['guard'] not in s['guards']:errors.append('Unknown exception guard')
 for h in s['handoffs']:
  if h['artifact'] not in types:errors.append('Unknown handoff artifact')
 if any(v is not False for v in s['configuration']['side_effects'].values()):errors.append('Forbidden business side effect enabled')
 return errors

def guard_allows(spec,name,context):
 # Boolean evidence context only. No string "true", missing values or model prose treated as authority.
 return all(context.get(k) is True for k in spec['guards'][name]['all'])

def validate_activation(configuration):
 schema=json.loads((D/'activation.schema.json').read_text())
 return [e.message for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(configuration)]

def activation_blockers(s,request=None):
 if s.get('status')=='implementation-bound-parameterized':
  binding_errors=validate_spec(s)
  if binding_errors:return binding_errors
  if request is None:return ['A validated per-investigation research brief and operating profile must be supplied']
  try:
   import sys
   sys.path.insert(0,str(D/'implementation'))
   from configuration import resolve
   resolved=resolve(s,request)
   return validate_activation(resolved)
  except (KeyError,TypeError,ValueError) as exc:return ['Invalid activation request: '+str(exc)]
 missing=['configuration.'+k for k,v in s['configuration']['required_before_activation'].items() if v is None]
 missing+=['role.'+k for k,v in s['configuration']['role_bindings'].items() if v is None]
 if s['components']['grounding_status']!='verified':missing.append('native components/resources not grounded')
 for k in ['model_revision','runtime']:
  if not s['configuration']['runtime_bindings'][k]:missing.append('runtime.'+k)
 if validate_activation(s['configuration']):missing.append('activation configuration schema not satisfied')
 return missing

def validate_artifact(a):
 typ=a.get('artifact_type');schema=load_schema()
 if typ not in schema['$defs']:return ['Unknown artifact type']
 schema={**schema,'$ref':'#/$defs/'+typ}
 return [e.message for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(a)]

def validate_review_acceptance(review,required):
 p=review['payload'];errors=[]
 if p['decision']=='accepted':
  checks={c['criterion_ref']:c for c in p['checks']}
  if len(checks)!=len(p['checks']):errors.append('Duplicate review criterion')
  if not set(required)<=checks.keys():errors.append('Missing critical review criteria')
  if any(checks.get(c,{}).get('status')!='pass' for c in required):errors.append('Critical review not passed')
  if p['critical_unresolved']!=0:errors.append('Critical findings unresolved')
 return errors

if __name__=='__main__':
 s=load_spec();schema=load_schema();Draft202012Validator.check_schema(schema)
 request=json.loads((D/'implementation/request.example.json').read_text()) if (D/'implementation/request.example.json').exists() else None
 report={'design_errors':validate_spec(s),'template_requires_inputs':activation_blockers(s),'example_request_activation_blockers':activation_blockers(s,request),'scope':'Contract completeness and declared gates, not factual truth or runtime enforcement'}
 print(json.dumps(report,indent=2))
