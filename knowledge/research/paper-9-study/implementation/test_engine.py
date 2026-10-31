import tempfile,unittest,json
from engine import Engine
CFG={'max_attempts_per_stage':4,'allowed_hosts':['example.com'],'request_timeout':5,'max_source_bytes':100000,'max_text_chars':12000,'max_sources':2,'model':'llama3.2:3b','model_timeout':20,'time_cap_seconds':60,'reviewer':'test-reviewer'}
BRIEF={'question':'Controlled reference question','audience_job':'Controlled software-research fixture','language':'English','geography':'unspecified fixture','time_window':'test snapshot','decision_owner':'test-owner','allowed_source_classes':['approved-source-catalog']}
def source(url,remaining):return b'<html><p>Original source text for a controlled implementation fixture, not a market finding.</p></html>','text/html'
def synth(brief,evidence,remaining):return [{'observation_id':evidence['observations'][0]['observation_id'],'quote':'Original source text for a controlled implementation fixture'}] if evidence['observations'] else []
class EngineTests(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory()
 def tearDown(self):self.t.cleanup()
 def engine(self,fetch=source,model=synth):return Engine(self.t.name,CFG,fetcher=fetch,synthesizer=model)
 def test_fixture_complete_path_reaches_review_without_fake_acceptance(self):
  e=self.engine();r=e.investigate(BRIEF,[{'url':'https://example.com/evidence'}]);self.assertEqual(r['retrieved'],1);self.assertEqual(r['candidate_count'],1);self.assertEqual(r['state'],'in_review')
  dossier=e.payload(r['dossier_ref']);self.assertEqual(dossier['recommendation'],'insufficient');self.assertFalse(dossier['business_profitability_proven'])
  self.assertTrue(e.payload(r['final_cost_ledger'])['events'])
 def test_unavailable_sources_produce_insufficient_not_no_demand(self):
  def fail(*args):raise OSError('fixture transport failure')
  e=self.engine(fetch=fail);r=e.investigate(BRIEF,[{'url':'https://example.com/evidence'}]);self.assertEqual(r['retrieved'],0);self.assertEqual(e.payload(r['dossier_ref'])['recommendation'],'insufficient')
  self.assertTrue(any(v['status']=='failed' for v in e.store.events(r['run_id'])))
 def test_hallucinated_model_quotation_is_not_retained(self):
  e=self.engine(model=lambda *a:[{'observation_id':'os0','quote':'An invented statement with no matching source evidence'}]);r=e.investigate(BRIEF,[{'url':'https://example.com/evidence'}]);self.assertEqual(r['candidate_count'],0)
 def test_model_failure_is_visible_and_does_not_become_success_claim(self):
  def fail(*args):raise TimeoutError('fixture model unavailable')
  e=self.engine(model=fail);r=e.investigate(BRIEF,[{'url':'https://example.com/evidence'}]);self.assertIsNotNone(r['model_failure']);self.assertEqual(r['state'],'in_review');self.assertEqual(r['candidate_count'],0)
 def test_forbidden_host_not_fetched(self):
  def never(*a):self.fail('Forbidden locator reached fetcher')
  e=self.engine(fetch=never);r=e.investigate(BRIEF,[{'url':'https://forbidden.invalid'}]);self.assertEqual(r['source_count'],0)
if __name__=='__main__':unittest.main(verbosity=2)
