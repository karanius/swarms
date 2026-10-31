import unittest,copy
from validate_contract import load_spec,load_schema,validate_spec,guard_allows,activation_blockers,validate_artifact,validate_review_acceptance,validate_activation
from jsonschema import Draft202012Validator

def artifact(kind,payload):
 return {'artifact_id':'fixture-only','schema_version':'1.0-contract','business_id':'local-content-business','instance_id':'market-intelligence','revision':1,'owner_ref':'fixture-reviewer','created_at':'2026-10-30T00:00:00Z','access_classification':'internal','source_lineage':[],'artifact_type':kind,'payload':payload}
class ContractTests(unittest.TestCase):
 def setUp(self):self.s=load_spec()
 def test_spec_and_schema_valid(self):
  Draft202012Validator.check_schema(load_schema());self.assertEqual(validate_spec(self.s),[])
 def test_source_discovery_cannot_be_removed(self):
  self.s['flows'][0]['nodes']=[n for n in self.s['flows'][0]['nodes'] if n['id']!='discover'];self.assertTrue(validate_spec(self.s))
 def test_input_type_mismatch(self):
  self.s['flows'][0]['nodes'][1]['bindings']['plan']='input.brief';self.assertTrue(validate_spec(self.s))
 def test_future_dependency_not_available(self):
  self.s['flows'][0]['nodes'][0]['bindings']['brief']='assemble.dossier';self.assertTrue(validate_spec(self.s))
 def test_cost_producer_required(self):
  self.s['observers'][0]['output_bindings']={};self.assertTrue(validate_spec(self.s))
 def test_attempt_observation_required(self):
  self.s['flows'][0]['nodes'][0]['observer_ref']='missing';self.assertTrue(validate_spec(self.s))
 def test_review_producer_required(self):
  self.s['flows'][0]['nodes']=[n for n in self.s['flows'][0]['nodes'] if n['id']!='review'];self.assertTrue(validate_spec(self.s))
 def test_identity_mismatch_rejected(self):
  self.s['business_id']='paper7-local-content-business';self.assertTrue(validate_spec(self.s))
 def test_process_owner_coverage(self):
  self.s['processes'][1]['owns_nodes'].remove('form_claims');self.assertTrue(validate_spec(self.s))
 def test_guard_requires_actual_boolean_and_all_inputs(self):
  keys=self.s['guards']['runtime_ready']['all'];ctx={k:True for k in keys};self.assertTrue(guard_allows(self.s,'runtime_ready',ctx))
  ctx[keys[0]]='true';self.assertFalse(guard_allows(self.s,'runtime_ready',ctx));del ctx[keys[0]];self.assertFalse(guard_allows(self.s,'runtime_ready',ctx))
 def test_parameterized_template_requires_a_request(self):self.assertTrue(activation_blockers(self.s))
 def test_required_payload_and_types(self):
  a=artifact('cost_ledger',{'events':[],'accounting_limits':[]});self.assertEqual(validate_artifact(a),[])
  a['payload']['events']='none';self.assertTrue(validate_artifact(a))
 def test_successful_source_requires_snapshot(self):
  source={'source_id':'s','locator':'https://example.invalid','publisher':None,'retrieved_at':'2026-10-30T00:00:00Z','status':'retrieved','snapshot_ref':None,'content_hash':None,'published_at':None,'access_basis':'fixture','license_status':'unknown','failure_reason':None}
  self.assertTrue(validate_artifact(artifact('source_batch',{'discovery_ref':'d','sources':[source],'attempt_refs':[]})))
 def test_supported_claim_cannot_have_no_evidence(self):
  j={'claim_id':'c','status':'supported','support_refs':[],'opposing_refs':[],'reason':'fixture','entailment_review':'pending','reviewer_ref':None,'inference_limits':[]}
  self.assertTrue(validate_artifact(artifact('assessment_set',{'candidate_ref':'x','judgments':[j],'policy_ref':'p'})))
 def test_mixed_claim_requires_both_sides(self):
  j={'claim_id':'c','status':'mixed','support_refs':['e'],'opposing_refs':[],'reason':'fixture','entailment_review':'pending','reviewer_ref':None,'inference_limits':[]}
  self.assertTrue(validate_artifact(artifact('assessment_set',{'candidate_ref':'x','judgments':[j],'policy_ref':'p'})))
 def test_review_rejects_incomplete_rubric(self):
  r=artifact('review_decision',{'dossier_ref':'d','reviewer_ref':'r','authority_ref':'a','decision':'accepted','checks':[],'reason':'fixture','critical_unresolved':0})
  required=self.s['policies']['review_acceptance']['required_criteria'];self.assertTrue(validate_review_acceptance(r,required));self.assertTrue(validate_artifact(r))
 def test_ack_requires_receipt(self):
  r=artifact('handoff_receipt',{'dossier_ref':'d','review_ref':'r','recipient_id':'content-strategy','idempotency_key':'x','delivery_status':'acknowledged','acknowledgment_ref':None,'reason':'fixture'})
  self.assertTrue(validate_artifact(r))
 def test_activation_schema_rejects_invalid_limits(self):
  self.assertTrue(validate_activation(self.s['configuration']))
  cfg=copy.deepcopy(self.s['configuration']);cfg['design_mode']=False
  for k in cfg['required_before_activation']:cfg['required_before_activation'][k]='fixture'
  for k in ['source_connectors','allowed_sources']:cfg['required_before_activation'][k]=['fixture']
  for k in ['time_cap_seconds','freshness_window']:cfg['required_before_activation'][k]=60
  for k in ['max_attempts_per_node','max_concurrent_retrievals']:cfg['required_before_activation'][k]=1
  cfg['required_before_activation']['cash_cap_amount']=0
  cfg['role_bindings']={k:'fixture-actor' for k in cfg['role_bindings']}
  cfg['runtime_bindings']['model_revision']='fixture-model';cfg['runtime_bindings']['runtime']='fixture-runtime'
  self.assertEqual(validate_activation(cfg),[])
  cfg['required_before_activation']['max_attempts_per_node']=-1;self.assertTrue(validate_activation(cfg))
 def test_review_requires_failing_critical_check_to_block_acceptance(self):
  criteria=self.s['policies']['review_acceptance']['required_criteria']
  checks=[{'criterion_ref':k,'status':'pass','evidence_refs':['fixture'],'reason':'fixture'} for k in criteria]
  r=artifact('review_decision',{'dossier_ref':'d','reviewer_ref':'r','authority_ref':'a','decision':'accepted','checks':checks,'reason':'fixture','critical_unresolved':0})
  self.assertEqual(validate_review_acceptance(r,criteria),[])
  checks[0]['status']='unknown';self.assertTrue(validate_review_acceptance(r,criteria))
 def test_unknown_payload_field_rejected(self):
  a=artifact('cost_ledger',{'events':[],'accounting_limits':[],'invented':1});self.assertTrue(validate_artifact(a))
 def test_no_public_side_effects(self):
  self.s['configuration']['side_effects']['publication']=True;self.assertTrue(validate_spec(self.s))
if __name__=='__main__':unittest.main(verbosity=2)
