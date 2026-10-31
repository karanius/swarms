"""Designer contracts with isolated fixtures; native runs are separate evidence."""
import importlib.util,json,sys,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import voice_designer as m

class DesignerTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.a=self.root/'auditions';self.p=self.root/'profiles';self.a.mkdir();self.p.mkdir()
  self.patches=[patch.object(m,'AUDITIONS',self.a),patch.object(m,'PROFILES',self.p),patch.object(m.scene,'STUDY',self.root)]
  for p in self.patches:p.start()
 def tearDown(self):
  for p in reversed(self.patches):p.stop()
  self.temp.cleanup()
 def request(self):return {'text':'This is a test sentence.','description':'A raspy, low voice with a calm delivery.'}
 def fixture(self,state='saved'):
  value=str(uuid.uuid4());folder=self.a/value;folder.mkdir();raw=folder/'voice.wav';raw.write_bytes(b'isolated fixture bytes, not native speech')
  r={'id':value,'created':1,'state':state,'request':m.validate(self.request()),'audio':{'path':str(raw),'listening_path':str(raw)}};m.scene.dump(folder/'audition.json',r);return r
 def test_validate_native_limits_and_model(self):
  for extra in [{'seed':-1},{'steps':65},{'guidance':0},{'description':''},{'text':''},{'model':'imaginary'}]:
   with self.subTest(extra=extra),self.assertRaises(ValueError):m.validate({**self.request(),**extra})
 def test_profile_is_pinned_and_idempotent(self):
  r=self.fixture();a=m.save_profile({'audition_id':r['id'],'name':'Fixture voice'});b=m.save_profile({'audition_id':r['id'],'name':'Fixture voice'});self.assertEqual(a,b);self.assertEqual(a['reference']['transcript'],r['request']['text']);self.assertEqual(len(list(self.p.glob('*.json'))),1)
 def test_failed_audition_cannot_become_profile(self):
  r=self.fixture('failed')
  with self.assertRaisesRegex(ValueError,'Generate'):m.save_profile({'audition_id':r['id'],'name':'Fixture'})
 def test_reuse_checks_original_bytes_and_ignores_new_description(self):
  r=self.fixture();p=m.save_profile({'audition_id':r['id'],'name':'Fixture'});q=m.validate({**self.request(),'profile_id':p['id'],'description':'different voice'});self.assertEqual(q['description'],'');self.assertEqual(q['mode'],'profile_reuse');Path(p['reference']['path']).write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'changed'):m.validate({**self.request(),'profile_id':p['id']})
 def test_native_design_forwards_freeform_without_reference_and_preserves_failure(self):
  value=str(uuid.uuid4());(self.a/value).mkdir();r={'id':value,'created':1,'state':'queued','request':m.validate(self.request())};captured={}
  def post(*args,**kw):
   captured.update(kw['files']);return type('Response',(),{'status_code':503,'text':'controlled unavailable service'})()
  m.scene.QUEUE.acquire()
  with patch.object(m.requests,'post',post):m.run(r)
  self.assertEqual(captured['instruct'][1],self.request()['description']);self.assertNotIn('ref_audio',captured);self.assertFalse(m.scene.QUEUE.locked());self.assertEqual(m.get(value)['state'],'failed')
 def test_media_requires_registered_completed_audition(self):
  with self.assertRaises(ValueError):m.media('../escape')
  r=self.fixture('running')
  with self.assertRaisesRegex(ValueError,'not ready'):m.media(r['id'])

if __name__=='__main__':unittest.main()
