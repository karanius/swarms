"""Deliberately corrupt saved artifacts; the separate verifier must reject them."""
import contextlib,io,json,shutil,tempfile,unittest
from pathlib import Path
import verify_relational as verifier
class ArtifactCorruptionTests(unittest.TestCase):
 def setUp(self):
  self.original=verifier.OUT;self.temp=tempfile.TemporaryDirectory();self.folder=Path(self.temp.name)
  for name in ['summary.json','rules.json','exact-rules.json','vocabulary.json','guidance.json','cases.json','predictions.json','proposals.json','train-features.tsv']:shutil.copy2(self.original/name,self.folder/name)
  verifier.OUT=self.folder
 def tearDown(self):verifier.OUT=self.original;self.temp.cleanup()
 def mutate(self,file,fn):
  p=self.folder/file;v=json.loads(p.read_text());fn(v);p.write_text(json.dumps(v))
 def rejected(self):
  with self.assertRaises((AssertionError,StopIteration,KeyError)),contextlib.redirect_stdout(io.StringIO()):verifier.main()
 def test_rule_support_corruption(self):self.mutate('rules.json',lambda v:v[0].update(jointCount=v[0]['jointCount']+1));self.rejected()
 def test_masked_target_leak(self):self.mutate('cases.json',lambda v:v[0]['visible'].append(v[0]['target']));self.rejected()
 def test_case_family_forgery(self):self.mutate('cases.json',lambda v:v[0].update(family='invented-independent-family'));self.rejected()
 def test_proposal_wrong_port(self):self.mutate('proposals.json',lambda v:v[0]['edges'][1].update(targetPort='invented_port'));self.rejected()
 def test_type_judgment_corruption(self):self.mutate('proposals.json',lambda v:v[0]['typeChecks'][0].update(judgment='invented-validated-type'));self.rejected()
 def test_reported_rate_corruption(self):self.mutate('summary.json',lambda v:v['metrics']['anyburl'].update(recoveryPerAnswer=-1));self.rejected()
 def test_center_frequency_result_corruption(self):self.mutate('predictions.json',lambda v:v['center_frequency'][0].update(prediction='invented-feature'));self.rejected()
 def test_required_exposure_omission(self):
  def drop(v):
   p=next(p for p in v if p.get('requiredExposures'));p['requiredExposures'].pop()
  self.mutate('proposals.json',drop);self.rejected()
if __name__=='__main__':unittest.main()
