import copy,csv,importlib.util,io,json,unittest
from pathlib import Path
S=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('crema_audit',S/'audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AuditTests(unittest.TestCase):
 def setUp(self):self.row=next(csv.DictReader(io.StringIO((S/'processedResults--tabulatedVotes.csv').read_text())))
 def test_modality_key_is_not_a_movie_or_actor_id(self):
  r=m.decode(self.row);self.assertEqual((r['modality'],r['clip_number']),(1,1));self.assertEqual(r['actor'],'1001')
 def test_no_votes_is_missing_not_zero_intensity(self):self.assertIsNone(m.decode(self.row)['perceived_intensity_given_emotion']['A'])
 def test_vote_sum_corruption_is_rejected(self):
  self.row['numResponses']='500'
  with self.assertRaisesRegex(ValueError,'count'):m.decode(self.row)
 def test_wrong_majority_is_rejected(self):
  self.row['emoVote']='A'
  with self.assertRaisesRegex(ValueError,'majority'):m.decode(self.row)
 def test_label_is_not_perception(self):
  r=json.loads((S/'audit-results.json').read_text())['example'];self.assertEqual(r['intended'],'H');self.assertEqual(r['majority'],['N']);self.assertFalse(r['eligible_candidate'])
 def test_uncertainty_is_not_discarded(self):self.assertLess(m.wilson(9,10),.9);self.assertGreater(m.wilson(9,10),0)
 def test_candidate_not_promoted(self):
  p=json.loads((S/'actor-candidate.json').read_text());self.assertEqual(p['state'],'candidate_not_approved');self.assertIsNone(p['identity_anchor']);self.assertEqual(p['generation_transfer_results'],[])
if __name__=='__main__':unittest.main()
