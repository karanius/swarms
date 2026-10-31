import unittest
from copy import deepcopy
from business_system import make_system,validate_system
class BusinessDesignChecks(unittest.TestCase):
 def test_proposed_system_is_consistent_without_native_graph_claims(self):
  self.assertEqual(validate_system(make_system()),[])
 def test_missing_shared_plane_is_rejected(self):
  s=make_system();del s['instances'][0]['planes']['configuration'];self.assertTrue(validate_system(s))
 def test_unknown_handoff_endpoint_is_rejected(self):
  s=make_system();s['handoff_contracts'][0]['to']='invented-domain';self.assertTrue(validate_system(s))
 def test_duplicate_artifact_contract_identity_is_rejected(self):
  s=make_system();s['handoff_contracts'].append(deepcopy(s['handoff_contracts'][0]));self.assertTrue(validate_system(s))
 def test_unauthorized_release_or_spend_is_rejected(self):
  for flag in ['publication_enabled','spending_enabled','account_changes_enabled']:
   s=make_system();s['operations']['controls'][flag]=True;self.assertTrue(validate_system(s))
 def test_fake_native_occurrence_is_rejected(self):
  s=make_system();s['instances'][0]['planes']['components']['native_occurrences']=[{'id':'invented-block'}];self.assertTrue(validate_system(s))
 def test_unreviewable_handoff_is_rejected(self):
  s=make_system();s['handoff_contracts'][0]['acceptance']='';self.assertTrue(validate_system(s))
 def test_disconnected_domain_is_rejected(self):
  s=make_system();s['handoff_contracts']=[h for h in s['handoff_contracts'] if h['to']!='audience-care'];self.assertTrue(validate_system(s))
if __name__=='__main__':unittest.main(verbosity=2)
