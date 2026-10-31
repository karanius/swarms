"""Validate custom-file conditioning without spending native inference."""
from pathlib import Path
import copy,importlib.util,unittest
S=Path(__file__).resolve().parents[2]/'knowledge/research/paper-16-study'
s=importlib.util.spec_from_file_location('custom_b',S/'take_backends.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class CustomReferenceTests(unittest.TestCase):
 def test_custom_reference_preserves_id_and_hash(self):
  ref=copy.deepcopy(m.refs()['esd:0012:anger']);ref['id']='candidate:actor:anger'
  self.assertEqual(m.validate('f5','A fresh line.','candidate:actor','anger',m.default_settings('f5'),ref),ref)
 def test_corrupted_reference_rejected(self):
  ref=copy.deepcopy(m.refs()['esd:0012:anger']);ref['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'changed'):m.validate('vox','A fresh line.','candidate:actor','anger',m.default_settings('vox'),ref)
 def test_model_specific_settings_remain_enforced(self):
  ref=m.refs()['esd:0012:anger']
  with self.assertRaisesRegex(ValueError,'Unsupported'):m.validate('dia','A fresh line.','candidate:actor','anger',{'strength':.5},ref)
if __name__=='__main__':unittest.main()
