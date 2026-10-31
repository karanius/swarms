"""Casting contract tests. Native mixed-cast evidence is recorded separately."""
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('casting_scene',Path(__file__).with_name('scene.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class CastingTests(unittest.TestCase):
 def setUp(self):
  self.lib=copy.deepcopy(m.libraries()['esd'])
  self.lib['voices']={v['speaker_id']:copy.deepcopy(v) for v in self.lib['roles'].values()}
  self.a=self.lib['roles']['A']['speaker_id'];self.b=self.lib['roles']['B']['speaker_id']
  self.catalog=patch.object(m,'libraries',lambda:{'esd':copy.deepcopy(self.lib)});self.catalog.start()
 def tearDown(self):self.catalog.stop()
 def test_swap_changes_all_actor_references_together(self):
  lib,_,_=m.validate({'library':'esd','model':'index','casting':{'A':self.b,'B':self.a}})
  self.assertEqual(lib['roles']['A'],self.lib['voices'][self.b])
  self.assertEqual(lib['roles']['B'],self.lib['voices'][self.a])
  self.assertEqual(self.lib['roles']['A']['speaker_id'],self.a)
 def test_invalid_casts_fail_closed(self):
  for cast in [{'A':self.a},{'A':self.a,'B':self.a},{'A':'missing','B':self.b},{'A':[],'B':self.b}]:
   with self.subTest(cast=cast),self.assertRaises(ValueError):m.cast_library(self.lib,cast)
 def test_role_restriction_is_enforced(self):
  self.lib['voices'][self.b]['allowed_roles']=['B']
  with self.assertRaisesRegex(ValueError,'unavailable'):m.cast_library(self.lib,{'A':self.b,'B':self.a})
 def test_missing_emotion_does_not_use_another_actor(self):
  self.lib['voices'][self.b]['performances'].pop('anger')
  with self.assertRaisesRegex(ValueError,'Missing supported'):m.validate({'library':'esd','model':'index','casting':{'A':self.b,'B':self.a}})
 def test_unconditioned_dia_cannot_claim_selected_cast(self):
  with self.assertRaisesRegex(ValueError,'reference continuation'):m.validate({'library':'esd','model':'dia','casting':{'A':self.a,'B':self.b},'settings':{'use_reference':False}})
 def test_preview_uses_selected_speaker(self):
  p=m.reference_preview('esd','A',identity='1',speaker=self.b)
  self.assertEqual(str(p),self.lib['roles']['B']['identity']['path'])
 def test_retake_cannot_change_cast(self):
  with tempfile.TemporaryDirectory() as directory,patch.object(m,'DATA',Path(directory)):
   parent=Path(directory)/'abc';parent.mkdir();m.dump(parent/'experiment.json',{'id':'abc','model':'index','library':'esd','scene':m.SCRIPT,'library_snapshot':self.lib})
   with self.assertRaisesRegex(ValueError,'new complete scene'):m.start({'library':'esd','model':'index','parent_id':'abc','line_ids':['01'],'casting':{'A':self.b,'B':self.a}})
   self.assertFalse(m.QUEUE.locked())

if __name__=='__main__':unittest.main()
