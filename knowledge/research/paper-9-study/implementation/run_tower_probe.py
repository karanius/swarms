"""Exercise canonical stage bindings through unchanged native components; isolated private run."""
import sys,json
from pathlib import Path
D=Path(__file__).resolve().parents[1];sys.path.insert(0,str(D));sys.path.insert(0,str(D/'implementation'))
from controller import Tower,ReviewRequired
from lfx.components.prototypes.python_function import PythonFunctionComponent
profile={'max_attempts_per_stage':4,'allowed_hosts':['support.google.com'],'request_timeout':20,'max_source_bytes':8000000,'max_text_chars':24000,'max_sources':2,'model':'llama3.2:3b','model_timeout':60,'time_cap_seconds':240,'reviewer':'coordinator-reviewer','web_search_enabled':False}
brief={'question':'Which source-policy constraints should a hypothetical original AI-assisted educational channel investigate?','audience_job':'Implementation verification probe; not validated audience demand','language':'English','geography':'No target market selected','time_window':'Public document retrieval snapshot','decision_owner':'coordinator-probe-owner','allowed_source_classes':['official-public-document']}
sources=[{'url':'https://support.google.com/youtube/answer/1311392?hl=en','reason':'Official monetization policy'}, {'url':'https://support.google.com/youtube/answer/14328491?hl=en','reason':'Official synthetic-media disclosure policy'}]
e=Tower(D/'.runtime'/'tower',profile);run=e.create(brief,sources);bindings=json.loads((D/'native-composite-bindings.json').read_text());results=[]
for row in bindings:
 if row['node']=='impact':continue
 code=row['code_template'].replace('{run_id!r}',repr(run));component=PythonFunctionComponent(function_code=code,_user_id='isolated-paper9-runtime-probe')
 result=component.execute_function_data();payload=[r.data for r in result]
 if row['node']=='review':
  # Native wrapper may represent the required review interruption as an error message.
  state=e.store.run(run)['state']
  if state!='in_review':raise RuntimeError('Native review did not stop for required independent review')
  results.append({'node':row['node'],'status':'expected_review_gate','native_output':payload});break
 if not payload or 'artifacts' not in payload[0]:raise RuntimeError('Native stage failed: '+str(payload)[:500])
 results.append({'node':row['node'],'status':'executed','artifact_refs':payload[0]['artifacts']})
 print(row['node']+' executed through native PythonFunction',flush=True)
state=e.store.run(run);report={'run_id':run,'store':str(e.store.root),'state':state['state'],'stages':results,'profile':'bounded-public-document/local-model probe; no business validation','native_type':'PythonFunction','no_active_canvas_changes':True,'limitations':['Independent review pending','No real consumer instance connected; outbox contract has controlled tests','No market demand or profitability evidence']}
(D/'tower-native-probe.json').write_text(json.dumps(report,indent=2));print(json.dumps({'state':state['state'],'native_stages_executed':len(results),'report':str(D/'tower-native-probe.json')},indent=2))
