from pathlib import Path
import copy,importlib.util,unittest
S=Path(__file__).resolve().parent
def mod(name):
 s=importlib.util.spec_from_file_location(name,S/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
lib=mod('reference_library')
class LibraryTests(unittest.TestCase):
 def test_source_original_and_enhanced_integrity(self):self.assertTrue(lib.validate(lib.load()))
 def test_models_share_performance_but_index_keeps_identity(self):
  for speaker in ['0012','0017']:
   for emotion in ['neutral','anger','sadness','surprise','happiness']:
    refs={m:lib.bindings(m,speaker,emotion,{'use_reference':True}) for m in ['index','vox','f5','dia']}
    self.assertEqual(refs['index'][0]['reference_id'],f'esd:{speaker}:neutral')
    self.assertEqual(len({refs[m][-1]['sha256'] for m in refs}),1)
 def test_no_reference_means_no_binding(self):self.assertEqual(lib.bindings('dia','0012','anger',{'use_reference':False}),[])
 def test_unknowns_are_explicit_not_inferred(self):
  for r in lib.load()['references']:
   self.assertIsNone(r['performance']['intensity']);self.assertEqual(r['review']['status'],'candidate_unrated')
 def test_invalid_intensity_is_rejected(self):
  data=copy.deepcopy(lib.load());data['references'][0]['performance']['intensity']=8
  with self.assertRaises(Exception):lib.validate(data,False)
 def test_duplicate_is_rejected(self):
  data=copy.deepcopy(lib.load());data['references'].append(data['references'][0])
  with self.assertRaisesRegex(ValueError,'Duplicate'):lib.validate(data,False)
if __name__=='__main__':unittest.main()
