"""Execute the canonical JSON's stage bindings with checkpointed capability resources."""
import json,hashlib,uuid,time,copy
from pathlib import Path
from engine import Engine
from tasks import HANDLERS
from validate_contract import validate_artifact,validate_spec
class ReviewRequired(RuntimeError):
 def __init__(self,dossier):self.dossier=dossier;super().__init__('Independent review required for '+dossier)
class Tower(Engine):
 ReviewRequired=ReviewRequired
 def create(self,brief,sources,flow='investigate',extra_inputs=None):
  from configuration import resolve
  activation=resolve(self.spec,{'brief':brief,'profile':self.cfg})
  errors=validate_spec(self.spec)
  if errors:raise ValueError('Instance binding validation failed: '+str(errors))
  self.run_id=self.store.create_run({'profile':self.cfg,'flow':flow,'source_catalog':sources,'activation_configuration':activation,'outputs':{},'binding_hashes':{},'spec_hash':hashlib.sha256(json.dumps(self.spec,sort_keys=True).encode()).hexdigest()},self.cfg['time_cap_seconds'])
  bref=self.emit('brief',brief)
  feedback=self.emit('review_feedback',{'status':'pending','parent_dossier_ref':None,'assessments_ref':None,'reviewer_ref':self.cfg['reviewer'],'recommendation':None,'reason':'No independent feedback submitted yet'})
  run=self.store.run(self.run_id);body=run['body'];body['inputs']={'brief':bref,'feedback':feedback,**(extra_inputs or {})};self.store.update(self.run_id,run['revision'],'planned',body);return self.run_id
 def obligations(self):
  return self.emit('obligation_set',{'items':[{'obligation_id':'evidence-review','question':'Independent reviewer must inspect exact source context, contrary evidence, freshness, alternatives and costs','owner_ref':self.cfg['reviewer'],'blocks':['handoff'],'status':'open','resolution':None}]})
 def step(self,run_id,node_id):
  self.run_id=run_id;run=self.store.run(run_id);self.cfg=run['body']['profile']
  if run['state']=='in_review' and not run['body'].get('review_submission') and node_id=='review':raise ReviewRequired(run['body']['outputs']['assemble']['dossier'])
  self.store.check_bound(run_id)
  expected=hashlib.sha256(json.dumps(self.spec,sort_keys=True).encode()).hexdigest()
  if expected!=run['body']['spec_hash']:raise ValueError('Specification changed; create a new run revision')
  flow=next(f for f in self.spec['flows'] if f['id']==run['body']['flow']);node=next(n for n in flow['nodes'] if n['id']==node_id)
  comp=next(c for c in self.spec['composites'] if c['id']==node['composite_ref']);available={'input.'+k:v for k,v in run['body']['inputs'].items()}
  for stage,ports in run['body']['outputs'].items():available.update({stage+'.'+p:ref for p,ref in ports.items()})
  # Observer snapshots are concrete artifacts, never phantom flow inputs.
  if any(v=='observer.costs' for v in node['bindings'].values()):available['observer.costs']=self.costs()
  if any(v=='observer.obligations' for v in node['bindings'].values()):available['observer.obligations']=self.obligations()
  inputs={p:available[src] for p,src in node['bindings'].items()}
  for p,ref in inputs.items():
   a=self.store.get(ref)
   if a['artifact_type']!=comp['input_ports'][p]:raise ValueError('Input type mismatch')
   if validate_artifact(a):raise ValueError('Stored input fails schema')
  # Hash stable supplied inputs. Observer snapshots are excluded from resume keys but preserved in output lineage.
  key=hashlib.sha256(json.dumps({p:r for p,r in inputs.items() if not node['bindings'][p].startswith('observer.')},sort_keys=True).encode()).hexdigest()
  if node_id in run['body']['outputs']:
   if run['body']['binding_hashes'][node_id]!=key:raise ValueError('Checkpoint input mismatch')
   for ref in run['body']['outputs'][node_id].values():self.store.get(ref)
   return run['body']['outputs'][node_id]
  lease_owner=uuid.uuid4().hex
  self.store.claim_stage(run_id,node_id,lease_owner,self.store.check_bound(run_id))
  try:
   with self.attempt(node_id) as (attempt,remaining):
    self.current_attempt=attempt
    result=HANDLERS[node['composite_ref']](self,inputs)
    if set(result)!=set(comp['output_ports']):raise ValueError('Output ports incomplete')
    for p,ref in result.items():
     a=self.store.get(ref)
     if a['artifact_type']!=comp['output_ports'][p] or validate_artifact(a):raise ValueError('Output contract violated')
   run=self.store.run(run_id);body=run['body'];body['outputs'][node_id]=result;body['binding_hashes'][node_id]=key
   phase={'intake':'planned','discover':'collecting','retrieve':'collecting','normalize':'assessing','compare':'assessing','form_claims':'assessing','assess':'assessing','assemble':'assessing','review':'accepted','handoff':'delivery_pending','impact':'revision_requested'}[node_id]
   if node_id=='review':phase={'accepted':'accepted','rework':'rework_requested','rejected':'rejected'}[self.payload(result['review'])['decision']]
   self.store.update(run_id,run['revision'],phase,body);return result
  except ReviewRequired:
   run=self.store.run(run_id);body=run['body'];body['paused_budget_seconds']=max(0,run['deadline']-time.time());self.store.update(run_id,run['revision'],'in_review',body);raise
  except Exception as exc:
   run=self.store.run(run_id);self.store.update(run_id,run['revision'],'blocked',{**run['body'],'last_error':type(exc).__name__+': '+str(exc)[:300]});raise
  finally:self.store.release_stage(run_id,node_id,lease_owner)
 def execute(self,run_id):
  run=self.store.run(run_id)
  if run['state']=='in_review' and not run['body'].get('review_submission'):return {'state':'in_review','run_id':run_id,'dossier_ref':run['body']['outputs']['assemble']['dossier']}
  flow=next(f for f in self.spec['flows'] if f['id']==run['body']['flow'])
  for n in flow['nodes']:
   try:
    result=self.step(run_id,n['id'])
    if n['id']=='review' and self.payload(result['review'])['decision']!='accepted':
     self.finalize_outputs(run_id)
     return {'state':self.store.run(run_id)['state'],'run_id':run_id,'review_ref':result['review']}
   except ReviewRequired as r:return {'state':'in_review','run_id':run_id,'dossier_ref':r.dossier,'implementation_scope':'Bounded source-catalog investigation; no automatic factual approval'}
  self.finalize_outputs(run_id,'delivery_pending' if flow['id']=='investigate' else 'revision_requested')
  return {'state':self.store.run(run_id)['state'],'run_id':run_id,'results':self.store.run(run_id)['body']['outputs']}
 def finalize_outputs(self,run_id,state=None):
  self.run_id=run_id;run=self.store.run(run_id);event_count=len(self.store.events(run_id))
  if run['body'].get('closure_event_count')==event_count and run['body'].get('final_cost_ledger'):
   self.store.get(run['body']['final_cost_ledger']);return run['body']['final_cost_ledger']
  ledger=self.costs();finance=self.store.deliver(run_id,ledger,'finance-performance','local-research-engine')
  run=self.store.run(run_id);body=run['body'];body['final_cost_ledger']=ledger;body['finance_outbox_key']=finance['key'];body['closure_event_count']=event_count
  self.store.update(run_id,run['revision'],state or run['state'],body);return ledger
 def submit_review(self,run_id,artifact):
  self.run_id=run_id;run=self.store.run(run_id);self.cfg=run['body']['profile']
  if run['state']!='in_review':raise ValueError('Run is not awaiting review')
  if artifact['payload']['reviewer_ref']!=self.cfg['reviewer']:raise PermissionError('Reviewer identity differs from configured local caller role')
  if validate_artifact(artifact):raise ValueError('Invalid review schema')
  body=run['body'];body['review_submission']=artifact
  remaining=body.pop('paused_budget_seconds',max(0,run['deadline']-time.time()))
  if remaining<=0:raise TimeoutError('No active execution budget remains')
  with self.store.connect() as db:
   cur=db.execute('UPDATE runs SET deadline=?,body=?,revision=revision+1 WHERE id=? AND revision=?',(time.time()+remaining,json.dumps(body),run_id,run['revision']))
   if cur.rowcount!=1:raise ValueError('Stale review submission')

 def revise_from_feedback(self,parent_run,assessment_payload,recommendation,reason):
  parent=self.store.run(parent_run);self.run_id=parent_run;self.cfg=parent['body']['profile'];outputs=parent['body']['outputs']
  if 'assemble' not in outputs:raise ValueError('No parent dossier to revise')
  candidate_ref=outputs['form_claims']['candidates']
  if assessment_payload['candidate_ref']!=candidate_ref:raise ValueError('Feedback references another candidate revision')
  if any(j.get('reviewer_ref')!=self.cfg['reviewer'] for j in assessment_payload['judgments']):raise PermissionError('Feedback reviewer mismatch')
  assessments=self.emit('assessment_set',assessment_payload,owner=self.cfg['reviewer'],lineage=[candidate_ref])
  feedback=self.emit('review_feedback',{'status':'submitted','parent_dossier_ref':outputs['assemble']['dossier'],'assessments_ref':assessments,'reviewer_ref':self.cfg['reviewer'],'recommendation':recommendation,'reason':reason},owner=self.cfg['reviewer'],lineage=[outputs['assemble']['dossier'],assessments])
  body=copy.deepcopy(parent['body']);body.pop('review_submission',None);body.pop('paused_budget_seconds',None);body.pop('last_error',None)
  body['parent_run']=parent_run;body['inputs']['feedback']=feedback
  keep={'intake','discover','retrieve','normalize','compare','form_claims'}
  body['outputs']={k:v for k,v in body['outputs'].items() if k in keep};body['binding_hashes']={k:v for k,v in body['binding_hashes'].items() if k in keep}
  body['spec_hash']=hashlib.sha256(json.dumps(self.spec,sort_keys=True).encode()).hexdigest()
  ident=self.store.create_run(body,self.cfg['time_cap_seconds']);return ident
