import copy,json,unittest
from pathlib import Path
from layer_contract_engine import check,apply_revision,construction_trace
BASE=Path(__file__).resolve().parent
class LayerChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.native=json.loads((BASE/'assistant-workspace/artifacts/tower-native-v1-compact.json').read_text());cls.doc=json.loads((BASE/'layers/instance-v1.json').read_text())
 def test_baseline_structural_contract_with_open_obligations(self):
  r=check(self.doc,self.native);self.assertTrue(r['passed']);self.assertEqual(r['openObligations'],10);self.assertIn('blocked',r['readiness'])
 def test_corruptions_detected(self):
  mutations={
   'lost-own-control':lambda d:d['layers']['flows'][0]['openObligations'].remove('O-control'),
   'wrong-config-owner':lambda d:next(c for c in d['layers']['components'] if c['role']=='draft').update(configurationRefs=['cfg-review-model']),
   'reversed-order':lambda d:d['layers']['flows'][0]['coordination']['order'].reverse(),
   'unknown-requirement-predicate':lambda d:d['requirements'][0].update(mandatory_unknown_predicate=True),
   'unknown-plane':lambda d:d['layers'].update(unknown=[]),
   'missing-public-api':lambda d:d['layers']['composites'][0]['publicInterfaces'].clear(),
   'wrong-public-port':lambda d:d['layers']['composites'][0]['publicInterfaces'][0].update(port='not_a_field'),
   'native-type':lambda d:d['layers']['components'][0].update(nativeType='Invented'),
   'dropped-component':lambda d:d['layers']['components'].pop(),
   'lost-cut':lambda d:d['layers']['composites'][0]['exposures'].clear(),
   'wrong-boundary-port':lambda d:d['layers']['composites'][0]['exposures'][0].update(port='invented'),
   'lost-internal-wire':lambda d:d['layers']['composites'][0]['internalEdges'].clear(),
   'lost-model-obligation':lambda d:next(c for c in d['layers']['components'] if c['nativeType']=='Agent')['openObligations'].clear(),
   'lost-flow-obligation':lambda d:d['layers']['flows'][0]['openObligations'].clear(),
   'missing-control':lambda d:d['layers']['flows'][0]['coordination'].update(termination=''),
   'false-flow-grounded':lambda d:d['layers']['flows'][0].update(status='verified'),
   'wrong-handoff':lambda d:d['layers']['flows'][0]['handoffs'][0].update(to='composite-draft'),
   'human-approval-lost':lambda d:d['layers']['processes'][0]['openObligations'].remove('O-human'),
   'invented-runtime':lambda d:d.update(runtimeExecuted=True),
  }
  for name,fn in mutations.items():
   with self.subTest(name=name):
    d=copy.deepcopy(self.doc);fn(d)
    try:r=check(d,self.native);self.assertFalse(r['passed'],name)
    except (ValueError,KeyError):pass # malformed finite schema rejected rather than accepted
 def test_finite_stage_gates(self):
  r=construction_trace(self.doc,self.native);self.assertEqual(r['stop'],'ask_for_missing_evidence');self.assertEqual(len(r['trace']),9);self.assertEqual(len(r['questions']),10)
  self.assertEqual(construction_trace(self.doc,self.native,budget=2)['stop'],'budget_exhausted')
 def test_revision_scope(self):
  p={'op':'propose_configuration','configurationId':'cfg-draft-system_prompt','proposedValue':'Proposed only','requirementId':'R-draft'}
  changed=apply_revision(self.doc,p);self.assertTrue(check(changed,self.native)['passed'])
  self.assertEqual(changed['obligations'],self.doc['obligations']);self.assertEqual(changed['requirements'],self.doc['requirements']);self.assertEqual(changed['parentRevision'],1)
  expected=copy.deepcopy(self.doc);expected['revision']=2;expected['parentRevision']=1;expected['revisionTrace']=changed['revisionTrace'];next(c for c in expected['layers']['configuration'] if c['id']==p['configurationId'])['proposedValue']='Proposed only';self.assertEqual(changed,expected)
  with self.assertRaises(ValueError):apply_revision(self.doc,{**p,'op':'run_and_approve'})
if __name__=='__main__':unittest.main(verbosity=2)
