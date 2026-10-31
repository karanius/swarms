import json,copy,unittest
from pathlib import Path
from verify_interpretation import verify,BASE,ART
class InterpretationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.flow=json.loads((BASE/json.loads((BASE/'latest.json').read_text())['run']/'flow.json').read_text());cls.proposal=json.loads((ART/'stock-first-analysis-v2.json').read_text())
 def test_positive_and_preserved_first_failure(self):
  self.assertTrue(verify(self.proposal,self.flow)['passed']);original=json.loads((ART/'stock-first-analysis.json').read_text());self.assertIn('flow retains all composite obligations',verify(original,self.flow)['issues'])
 def test_corruption_sensitivity(self):
  variants={
   'drop-coverage':lambda d:d.update(requirementCoverage=[]),
   'drop-node':lambda d:d['componentRoles'].pop(),
   'invent-type':lambda d:d['componentRoles'][0].update(type='Invented'),
   'drop-wire':lambda d:d['nativeWires'].pop(),
   'wrong-wire-port':lambda d:d['nativeWires'][0].update(sourcePort='invented'),
   'lost-cut':lambda d:d['proposedComposites'][0]['crossingEdgeIds'].clear(),
   'wrong-export':lambda d:d['proposedComposites'][0]['exports'][0].update(direction='input'),
   'drop-parent-obligations':lambda d:d['proposedFlow']['unknownObligations'].clear(),
   'false-human-binding':lambda d:d['proposedProcess']['accountability'].update(binding='invented-approved-user'),
   'false-behavior':lambda d:d['requirementCoverage'][0].update(behaviorVerified=True),
  }
  for label,change in variants.items():
   with self.subTest(label=label):
    d=copy.deepcopy(self.proposal);change(d)
    try:self.assertFalse(verify(d,self.flow)['passed'])
    except (KeyError,ValueError):pass
if __name__=='__main__':unittest.main(verbosity=2)
