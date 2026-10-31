"""Pin real native catalog definitions and compile private per-stage composite graphs."""
from pathlib import Path
import json,hashlib,sys,inspect
D=Path(__file__).resolve().parents[1];sys.path.insert(0,str(D));sys.path.insert(0,str(D/'implementation'))
from lfx.graph.flow_builder.builder import load_local_registry,build_flow_from_spec
from lfx.components.prototypes.python_function import PythonFunctionComponent
from controller import Tower
from test_engine import CFG,BRIEF
from native_bridge import dispatch
registry=load_local_registry();entry=registry['PythonFunction']
source=Path(inspect.getfile(PythonFunctionComponent))
catalog={'type':'PythonFunction','class':PythonFunctionComponent.__module__+'.PythonFunctionComponent','source_path':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'catalog_sha256':hashlib.sha256(json.dumps(entry,sort_keys=True).encode()).hexdigest(),'native_definition_unchanged':True,'resource_boundary':'Native PythonFunction invokes pinned trusted local resource code. It is not an operating-system sandbox.'}
(D/'native-component-binding.json').write_text(json.dumps(catalog,indent=2))
profile={**CFG,'allowed_hosts':['support.google.com'],'time_cap_seconds':300,'max_source_bytes':8000000,'max_attempts_per_stage':5}
engine=Tower(D/'.runtime'/'tower',profile)
run_id=engine.create({**BRIEF,'question':'Native adapter compilation fixture; no market research','audience_job':'Controlled native-adapter fixture'},[])
results=[];out=D/'native-composites';out.mkdir(exist_ok=True)
for f in engine.spec['flows']:
 for node in f['nodes']:
  # Exported defaults refuse execution until their per-run binding is supplied by this factory.
  template="def capability():\n    import sys\n    sys.path.insert(0, "+repr(str(D/'implementation'))+")\n    from native_bridge import dispatch\n    return dispatch({run_id!r}, "+repr(node['id'])+")"
  # Public exported graph defaults are inert: use the factory to supply a real run identifier.
  code=template.replace('{run_id!r}',repr('RUN_ID_REQUIRED'))
  text='name: Market Intelligence '+node['id']+'\nnodes:\n  capability: PythonFunction\nedges:\nconfig:\n  capability.function_code: |\n'+''.join('    '+line+'\n' for line in code.splitlines())
  result=build_flow_from_spec(text,registry=registry)
  if 'error' in result:raise RuntimeError(result['error'])
  path=out/(node['composite_ref']+'.json');path.write_text(json.dumps(result['flow'],indent=2))
  results.append({'composite':node['composite_ref'],'node':node['id'],'native_type':'PythonFunction','graph_path':str(path.relative_to(D)),'graph_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'input_binding':'Controller resolves typed artifact ports from run state; factory supplies validated run_id','code_template':template,'native_graph_compiled':True})
# Execute one real native component through its unchanged implementation and bridge.
code=next(r['code_template'] for r in results if r['node']=='intake').replace('{run_id!r}',repr(run_id))
component=PythonFunctionComponent(function_code=code,_user_id='isolated-paper9-probe')
answer=component.execute_function_data()
if not answer or 'artifacts' not in answer[0].data:raise RuntimeError('Native component did not return artifact references')
(D/'native-composite-bindings.json').write_text(json.dumps(results,indent=2))
report={'scope':'Private compiled composite graphs; unchanged native PythonFunction executed intake through concrete resource bridge','compiled_graphs':len(results),'native_execution_output':answer[0].data,'run_id':run_id,'catalog':catalog,'not_claimed':['All native graphs executed','Full Langflow GUI run','Independent market reasoning validation']}
(D/'native-execution-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps({'compiled_graphs':len(results),'native_intake_executed':True},indent=2))
