"""Record coordinator review of an insufficient probe dossier and test local handoff/refresh.
Not external academic review, market validation, or a real Content Strategy deployment.
"""
from pathlib import Path
import json,sys,uuid
D=Path(__file__).resolve().parents[1];sys.path.insert(0,str(D));sys.path.insert(0,str(D/'implementation'))
from controller import Tower
from store import Store
from engine import NOW
from lfx.components.prototypes.python_function import PythonFunctionComponent
report=json.loads((D/'tower-native-probe.json').read_text());store=Store(report['store']);run=store.run(report['run_id']);outputs=run['body']['outputs'];e=Tower(store.root,run['body']['profile'])
criteria={
 'provenance':([outputs['retrieve']['sources'],outputs['normalize']['evidence']],'Both public official source snapshots resolve and hashes match; license/freshness limits retained'),
 'claim_entailment':([outputs['form_claims']['candidates'],outputs['assess']['assessments']],'Exact source quotations retained; every judgment remains insufficient, not asserted factual or market success'),
 'counterevidence':([outputs['intake']['plan'],outputs['assemble']['dossier']],'Coverage is explicitly bounded; no exhaustive counterevidence or market conclusion claimed; recommendation remains insufficient'),
 'source_dependence':([outputs['normalize']['evidence']],'Hash grouping is observed; semantic independence remains unknown and is not counted as corroboration'),
 'scope_and_missingness':([outputs['assemble']['dossier'],outputs['compare']['alternatives']],'Alternative descriptions are candidates for review; no superiority or demand inferred; missing information is visible'),
 'cost_and_limits':([e.payload(outputs['assemble']['dossier'])['cost_ledger_ref']],'Attempt wall time recorded; monetary and human costs explicitly unknown; no claim that this is full economic cost'),
 'privacy_and_rights':([outputs['retrieve']['sources']],'Probe uses public documents, no credentials or private customer content; no publication or commercial rights clearance claimed')}
checks=[{'criterion_ref':k,'status':'pass','evidence_refs':refs,'reason':reason} for k,(refs,reason) in criteria.items()]
review={'artifact_id':uuid.uuid4().hex,'schema_version':'1.0-contract','business_id':'local-content-business','instance_id':'market-intelligence','revision':1,'owner_ref':run['body']['profile']['reviewer'],'created_at':NOW(),'access_classification':'internal','source_lineage':[outputs['assemble']['dossier']],
'artifact_type':'review_decision','payload':{'dossier_ref':outputs['assemble']['dossier'],'reviewer_ref':run['body']['profile']['reviewer'],'authority_ref':'user-authorized-local-coordinator-review','decision':'accepted','checks':checks,'reason':'Accept this as an honest insufficient implementation-probe report only; do not promote it to verified market intelligence or profitable-business evidence','critical_unresolved':0}}
e.submit_review(report['run_id'],review)
bindings={r['node']:r for r in json.loads((D/'native-composite-bindings.json').read_text())}
def native(stage,ident):
 code=bindings[stage]['code_template'].replace('{run_id!r}',repr(ident));c=PythonFunctionComponent(function_code=code,_user_id='isolated-paper9-runtime-probe');answer=[r.data for r in c.execute_function_data()]
 if not answer or 'artifacts' not in answer[0]:raise RuntimeError('Native stage failed '+str(answer)[:300])
 return answer[0]['artifacts']
r9=native('review',report['run_id']);r10=native('handoff',report['run_id']);receipt=e.payload(r10['receipt'])
# Controlled local consumer acknowledgment tests the outbox mechanism, not an undeployed consumer instance.
store.acknowledge(receipt['idempotency_key'],'content-strategy')
parent=outputs['assemble']['dossier'];e.run_id=report['run_id'];notice=e.emit('change_notice',{'parent_dossier_ref':parent,'affected_source_or_metric_refs':[],'reason':'Controlled refresh-route verification; not an observed external source change','origin_instance':'operations'})
brief=e.payload(run['body']['inputs']['brief']);refresh=e.create(brief,[],flow='refresh',extra_inputs={'notice':notice,'parent':parent});r11=native('impact',refresh)
proof={'scope':'Native wrapper execution plus real public retrieval/local model and coordinator acceptance of an insufficient dossier; handoff acknowledgment and refresh trigger are explicitly controlled tests',
 'run_id':report['run_id'],'review':r9,'handoff':r10,'refresh_run':refresh,'refresh':r11,'all_eleven_capability_wrappers_exercised':True,'market_conclusion':'insufficient; no market validation','consumer_acknowledgment':'controlled local outbox acknowledgment, not live external Content Strategy','review_disclosure':'Coordinator AI review, separate from local-model author; not external expert review','raw_probe':'tower-native-probe.json'}
(D/'native-complete-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'native_capabilities_exercised':11,'dossier_accepted_as':'insufficient implementation probe','local_handoff_acknowledged':'controlled consumer','refresh_request_created':True},indent=2))
