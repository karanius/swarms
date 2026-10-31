import unittest,math,tempfile,json
from pathlib import Path
from PIL import Image
from pipeline import validate_plan,draw_scene,captions,stamp,audio_duration,build
class Contracts(unittest.TestCase):
 def plan(self):return {'title':'A bounded test','scenes':[{'headline':'Read the request','narration':'A request becomes requirements before a design is proposed.','steps':['Request','Requirements','Design']},{'headline':'Check the implementation','narration':'Testing produces evidence and reveals what still needs work.','steps':['Build','Test','Evidence']}]}
 def test_valid_plan(self):self.assertEqual(len(validate_plan(self.plan())['scenes']),2)
 def test_rejects_missing_scene(self):
  p=self.plan();p['scenes'].pop()
  with self.assertRaises(ValueError):validate_plan(p)
 def test_rejects_code_as_scene(self):
  p=self.plan();p['scenes'][0]['code']='print(1)'
  with self.assertRaises(ValueError):validate_plan(p)
 def test_rejects_overlong_narration(self):
  p=self.plan();p['scenes'][0]['narration']='word '*40
  with self.assertRaises(ValueError):validate_plan(p)
 def test_real_image_contract(self):
  with tempfile.TemporaryDirectory() as td:
   target=Path(td)/'scene.png';r=draw_scene(self.plan()['scenes'][0],0,target)
   with Image.open(target) as im:
    self.assertEqual(im.size,(1280,720));self.assertEqual(len(r['sha256']),64);self.assertGreater(len(im.getcolors(1280*720)),10)
 def test_audio_timeline_caption_boundaries(self):
  result=captions(self.plan()['scenes'],[4.25,3.5]);self.assertIn('00:00:00,000 --> 00:00:04,250',result);self.assertIn('00:00:04,250 --> 00:00:07,750',result)
 def test_invalid_timing_fails(self):
  for d in [[-1,2],[math.nan,2],[1]]:
   with self.assertRaises(ValueError):captions(self.plan()['scenes'],d)
 def test_unsafe_run_name_fails(self):
  with self.assertRaises(ValueError):build('A legitimate example request','../escape')
 def test_text_never_shell_executes(self):
  with tempfile.TemporaryDirectory() as td:
   p=self.plan();p['scenes'][0]['headline']='$(touch /tmp/paper12-should-not-exist)';draw_scene(p['scenes'][0],0,Path(td)/'a.png');self.assertFalse(Path('/tmp/paper12-should-not-exist').exists())
if __name__=='__main__':unittest.main(verbosity=2)
