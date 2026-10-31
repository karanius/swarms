"""Independent identity/emotion inputs; isolated fixtures are not listener approvals."""
import json,sys,tempfile,types,unittest,uuid
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import performance_bridge as b
import character_workflow as w
class ReferencePerformanceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.a=self.root/'auditions';self.a.mkdir();self.projects=self.root/'projects';self.projects.mkdir();self.profiles=self.root/'profiles';self.profiles.mkdir()
  raw=self.root/'identity.wav';raw.write_bytes(b'Isolated synthetic fixture; no real speech');self.identity={'audition_id':str(uuid.uuid4()),'path':str(raw),'sha256':b.scene.digest(raw),'transcript':'The fixture identity words.'}
  guide=self.root/'actor.wav';guide.write_bytes(b'Different isolated fixture bytes');self.guide={'id':'actor:anger','speaker':'crema:1006','label':'Fixture actor anger','emotion':'anger','path':str(guide),'sha256':b.scene.digest(guide),'transcript':'The fixture guide words.','terms':'Fixture only'}
  self.patches=[patch.object(b.designer,'AUDITIONS',self.a),patch.object(b.designer,'PROFILES',self.profiles),patch.object(w,'PROJECTS',self.projects),patch.object(b,'catalog',lambda:{self.guide['id']:self.guide})]
  for p in self.patches:p.start()
 def tearDown(self):
  for p in reversed(self.patches):p.stop()
  self.temp.cleanup()
 def request(self,style='anger',ref='actor:anger'):return b.request(self.identity,'Fixture character',w.DEVELOPMENT_TEXT,style,ref,1,23)
 def test_separate_input_hashes_and_no_emotion_text(self):
  q=self.request();self.assertEqual(q['profile']['reference'],self.identity);self.assertEqual(q['emotion_reference'],self.guide);self.assertNotEqual(q['profile']['reference']['sha256'],q['emotion_reference']['sha256']);self.assertEqual(q['performance_direction'],'');self.assertEqual(q['mode'],'reference_performance')
 def test_missing_reference_cannot_fall_back_to_text(self):
  self.assertEqual(b.default_reference('curiosity'),'')
  with self.assertRaisesRegex(ValueError,'Choose'):self.request(ref='')
 def test_ranges_and_source_tampering_fail_closed(self):
  for strength,scale in [(-1,1),(2,1),(1,0),(1,3)]:
   with self.subTest(strength=strength,scale=scale),self.assertRaises(ValueError):b.request(self.identity,'Fixture',w.DEVELOPMENT_TEXT,'anger','actor:anger',strength,23,scale)
  Path(self.guide['path']).write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'changed'):self.request()
 def test_neutral_guide_never_replaces_fixed_identity(self):
  q=self.request(style='neutral');r=b.designer.create_record(q);captured={}
  def native(**kwargs):captured.update(kwargs);raise RuntimeError('Controlled fixture end before inference')
  with patch.object(b.scene,'STUDY',self.root),patch.object(b.scene,'module',return_value=types.SimpleNamespace(run=native)):b.run(r,release_queue=False)
  self.assertEqual(captured['reference_overrides']['neutral']['sha256'],self.identity['sha256']);self.assertEqual(captured['reference_overrides']['guide']['sha256'],self.guide['sha256']);self.assertEqual(captured['conditions'],[{'emotion':'guide','strength':1}]);self.assertEqual(r['state'],'failed');self.assertEqual(r['engine'],'IndexTTS 2.5')
 def test_workflow_queues_reference_request_and_index_engine(self):
  p=w.create({'name':'Fixture'});p=w.load(p['id']);p['identity']={'reference':self.identity};w.save(p)
  try:
   with patch.object(w.scene.B,'inventory',return_value=[{'id':'index','ready':True}]),patch.object(w.threading.Thread,'start'):
    result=w.generate({'id':p['id'],'styles':['anger'],'references':{'anger':'actor:anger'}})
   self.assertEqual(result['jobs'][-1]['total'],1);self.assertTrue(w.scene.QUEUE.locked())
  finally:
   if w.scene.QUEUE.locked():w.scene.QUEUE.release()
 def test_feedback_preserves_unknown_words_and_identity(self):
  p=w.create({'name':'Fixture'});p=w.load(p['id']);p['styles']['anger']['selected']='old-candidate';p['styles']['anger']['candidates']=[{'audition_id':'old-candidate','text':'A fixture voice.'}];w.save(p);w.mutate({'id':p['id'],'action':'feedback','style':'anger','candidate_id':'old-candidate','note':'Listener did not hear anger.'});s=w.load(p['id'])['styles']['anger'];self.assertEqual(s['reviews'],[]);self.assertNotIn('identity',s['feedback'][0]);self.assertNotIn('words',s['feedback'][0]);self.assertFalse(w.evidence(s)['qualified'])
if __name__=='__main__':unittest.main()
