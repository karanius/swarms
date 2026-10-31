"""Contract tests use stubbed synthesis; runtime scene evidence is separate."""
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('scene_test',Path(__file__).with_name('scene.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SceneTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.old=(m.DATA,m.B.generate,m.assemble,m.STUDY,m.COMPARISONS);m.DATA=Path(self.temp.name);m.STUDY=Path(self.temp.name);m.COMPARISONS=m.DATA/'comparisons';m.COMPARISONS.mkdir()
 def tearDown(self):m.DATA,m.B.generate,m.assemble,m.STUDY,m.COMPARISONS=self.old;self.temp.cleanup()
 def test_unknown_library_and_control_fail_before_generation(self):
  with self.assertRaises(ValueError):m.validate({'library':'imaginary','model':'index'})
  with self.assertRaisesRegex(ValueError,'Unsupported'):m.validate({'library':'esd','model':'dia','settings':{'strength':1}})
 def test_duplicate_line_rejected(self):
  with self.assertRaisesRegex(ValueError,'duplicate'):m.validate({'library':'esd','model':'index','line_ids':['01','01']})
 def test_exact_reference_mapping_and_esd_baseline(self):
  lib,settings,ids=m.validate({'library':'esd','model':'index'})
  self.assertEqual(lib['roles']['A']['identity']['id'],'esd:0012:neutral');self.assertEqual(lib['roles']['B']['performances']['sadness']['id'],'esd:0015:sadness');self.assertEqual(len(ids),6)
 def test_sequential_success_and_no_ratings_fabrication(self):
  calls=[]
  def gen(model,text,speaker,emotion,settings,**kw):
   calls.append(text);return {'id':'stub','path':'stub.wav','word_check':{'exact_words':True},'reference':kw['reference_override']}
  m.B.generate=gen;m.assemble=lambda r,p:r.update(mix={'path':'stubbed assembly'})
  r=self.record();m.QUEUE.acquire();m.run(r);saved=m.get('abc');self.assertEqual(saved['state'],'complete');self.assertEqual(calls,[l['text'] for l in m.SCRIPT['lines']]);self.assertEqual(saved['ratings'],{})
 def test_failure_is_partial_and_preserves_other_lines(self):
  def gen(model,text,*a,**kw):
   if text==m.SCRIPT['lines'][1]['text']:raise RuntimeError('controlled synthesis failure')
   return {'id':'stub','path':'stub.wav','word_check':{'exact_words':True}}
  m.B.generate=gen;m.assemble=lambda *a: self.fail('Incomplete run must not assemble')
  r=self.record();m.QUEUE.acquire();m.run(r);saved=m.get('abc');self.assertEqual(saved['state'],'partial');self.assertEqual(saved['lines']['02']['state'],'failed');self.assertEqual(len([v for v in saved['lines'].values() if v['state']=='saved']),5);self.assertNotIn('mix',saved)
 def test_heldout_scene_is_distinct_and_validated(self):
  lib,settings,ids=m.validate({'library':'esd','model':'index','scene_id':'the-empty-seat-v1'})
  self.assertEqual(len(ids),4)
  with self.assertRaisesRegex(ValueError,'Unknown scene'):m.validate({'library':'esd','model':'index','scene_id':'missing'})
 def test_missing_reference_cannot_silently_fallback(self):
  original=m.libraries
  lib=copy.deepcopy(original()['esd']);lib['roles']['A']['performances'].pop('anger')
  m.libraries=lambda:{'esd':lib}
  try:
   with self.assertRaisesRegex(ValueError,'Missing supported'):m.validate({'library':'esd','model':'index'})
  finally:m.libraries=original
 def test_comparison_hides_conditions_until_assessment(self):
  for ident in ['abc','def']:
   (m.DATA/ident).mkdir();m.dump(m.DATA/ident/'experiment.json',{'id':ident,'scene':m.SCRIPT,'state':'complete','mix':{'path':'stub.wav'},'library':ident,'model':'index'})
  public=m.compare({'experiments':['abc','def']})
  self.assertNotIn('mapping',public)
  result=m.assess_compare({'id':public['id'],'preference':'no_clear_difference','notes':'Unit fixture'})
  self.assertEqual(set(result['mapping']),{'A','B'});self.assertTrue(result['assessment']['condition_labels_hidden'])
 def test_comparison_rejects_different_scripts(self):
  for ident,script in [('abc',m.SCRIPT),('def',m.HELDOUT)]:
   (m.DATA/ident).mkdir();m.dump(m.DATA/ident/'experiment.json',{'id':ident,'scene':script,'state':'complete','mix':{'path':'stub.wav'}})
  with self.assertRaisesRegex(ValueError,'same script'):m.compare({'experiments':['abc','def']})
 def record(self):
  lib,settings,ids=m.validate({'library':'esd','model':'index'});r={'id':'abc','library':'esd','library_snapshot':copy.deepcopy(lib),'model':'index','settings':settings,'requested_lines':ids,'scene':m.SCRIPT,'lines':{},'events':[],'ratings':{}};(m.DATA/'abc').mkdir();return r
if __name__=='__main__':unittest.main()
