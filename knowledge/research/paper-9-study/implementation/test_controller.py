import unittest,tempfile,copy
from controller import Tower
from test_engine import CFG,BRIEF,source,synth
from test_contract import artifact
class ControllerTests(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.e=Tower(self.t.name,CFG,fetcher=source,synthesizer=synth,alternative_finder=lambda *a:[])
 def tearDown(self):self.t.cleanup()
 def test_json_driven_path_and_checkpoint_replay(self):
  ident=self.e.create(BRIEF,[{'url':'https://example.com/evidence'}]);r=self.e.execute(ident);self.assertEqual(r['state'],'in_review')
  count=len(self.e.store.events(ident));self.e.step(ident,'retrieve');self.assertEqual(count,len(self.e.store.events(ident)))
 def test_successful_review_and_durable_local_handoff(self):
  ident=self.e.create(BRIEF,[{'url':'https://example.com/evidence'}]);r=self.e.execute(ident)
  checks=[{'criterion_ref':k,'status':'pass','evidence_refs':[r['dossier_ref']],'reason':'Controlled fixture reference, not market review'} for k in self.e.spec['policies']['review_acceptance']['required_criteria']]
  review=artifact('review_decision',{'dossier_ref':r['dossier_ref'],'reviewer_ref':CFG['reviewer'],'authority_ref':'test-local-caller','decision':'accepted','checks':checks,'reason':'Controlled fixture','critical_unresolved':0})
  review['owner_ref']=CFG['reviewer']
  self.e.submit_review(ident,review);r=self.e.execute(ident);self.assertEqual(r['state'],'delivery_pending');self.assertIn('handoff',r['results']);self.assertIn('final_cost_ledger',self.e.store.run(ident)['body']);self.assertIn('finance_outbox_key',self.e.store.run(ident)['body'])
 def test_refresh_has_immutable_parent_and_revision_request(self):
  ident=self.e.create(BRIEF,[{'url':'https://example.com/evidence'}]);r=self.e.execute(ident);parent=r['dossier_ref'];before=self.e.store.get(parent)
  notice=self.e.emit('change_notice',{'parent_dossier_ref':parent,'affected_source_or_metric_refs':[],'reason':'Controlled fixture update','origin_instance':'operations'})
  revision=self.e.create(BRIEF,[],flow='refresh',extra_inputs={'notice':notice,'parent':parent});r2=self.e.execute(revision)
  self.assertEqual(r2['state'],'revision_requested');self.assertEqual(self.e.store.get(parent),before)
 def test_review_wait_does_not_spend_saved_execution_budget(self):
  ident=self.e.create(BRIEF,[]);r=self.e.execute(ident);state=self.e.store.run(ident);self.assertGreater(state['body']['paused_budget_seconds'],0)
  with self.e.store.connect() as db:db.execute('UPDATE runs SET deadline=0 WHERE id=?',(ident,))
  self.assertEqual(self.e.execute(ident)['state'],'in_review')
 def test_rejected_review_stops_before_handoff(self):
  ident=self.e.create(BRIEF,[]);r=self.e.execute(ident)
  review=artifact('review_decision',{'dossier_ref':r['dossier_ref'],'reviewer_ref':CFG['reviewer'],'authority_ref':'test-local-caller','decision':'rejected','checks':[],'reason':'Controlled rejection','critical_unresolved':1});review['owner_ref']=CFG['reviewer']
  self.e.submit_review(ident,review);result=self.e.execute(ident);self.assertEqual(result['state'],'rejected');self.assertNotIn('handoff',self.e.store.run(ident)['body']['outputs'])
 def test_reviewed_feedback_can_produce_continue_without_overwriting_parent(self):
  ident=self.e.create(BRIEF,[{'url':'https://example.com/evidence'}]);r=self.e.execute(ident);before=self.e.store.get(r['dossier_ref']);outs=self.e.store.run(ident)['body']['outputs']
  assessments=copy.deepcopy(self.e.payload(outs['assess']['assessments']))
  for j in assessments['judgments']:j.update(status='supported',entailment_review='passed',reviewer_ref=CFG['reviewer'],reason='Controlled exact-quotation fixture review, not a real market judgment')
  child=self.e.revise_from_feedback(ident,assessments,'continue','Controlled decision to continue a bounded research fixture')
  result=self.e.execute(child);self.assertEqual(result['state'],'in_review');self.assertEqual(self.e.payload(result['dossier_ref'])['recommendation'],'continue');self.assertEqual(self.e.store.get(r['dossier_ref']),before);self.assertIn(r['dossier_ref'],self.e.store.get(result['dossier_ref'])['source_lineage'])
 def test_feedback_must_match_exact_candidate_revision(self):
  ident=self.e.create(BRIEF,[]);self.e.execute(ident)
  with self.assertRaises(ValueError):self.e.revise_from_feedback(ident,{'candidate_ref':'wrong','judgments':[],'policy_ref':'p'},'continue','invalid fixture')
 def test_continue_without_supported_review_is_blocked(self):
  ident=self.e.create(BRIEF,[]);self.e.execute(ident);outs=self.e.store.run(ident)['body']['outputs'];a=self.e.payload(outs['assess']['assessments'])
  child=self.e.revise_from_feedback(ident,a,'continue','Controlled unsupported recommendation')
  with self.assertRaises(ValueError):self.e.execute(child)
 def test_out_of_order_stage_rejected(self):
  ident=self.e.create(BRIEF,[])
  with self.assertRaises(KeyError):self.e.step(ident,'assess')
if __name__=='__main__':unittest.main(verbosity=2)
