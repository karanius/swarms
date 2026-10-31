"""Isolated contract fixtures never become listener-approved production characters."""
import copy,json,sys,tempfile,unittest,uuid,zipfile,io
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import character_workflow as m
class WorkflowTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.paths={key:self.root/key for key in ['PROJECTS','PACKAGES','AUDITIONS','PROFILES']}
  for p in self.paths.values():p.mkdir()
  self.patches=[patch.object(m,key,self.paths[key]) for key in ['PROJECTS','PACKAGES']]+[patch.object(m.designer,key,self.paths[key]) for key in ['AUDITIONS','PROFILES']]
  for p in self.patches:p.start()
  self.project=m.create({'name':'Isolated fixture'})
 def tearDown(self):
  for p in reversed(self.patches):p.stop()
  self.temp.cleanup()
 def fixture(self,mode='voice_design',text='A fixture sentence, not real speech.'):
  r=m.designer.create_record({'mode':mode,'text':text,'description':'Fixture voice','profile':None,'seed':23,'steps':20,'guidance':2.5});folder=self.paths['AUDITIONS']/r['id'];wav=folder/'voice.wav';wav.write_bytes(b'NOT REAL SPEECH '+r['id'].encode());r.update(state='saved',audio={'path':str(wav),'listening_path':str(wav)},word_check={'exact_words':True});m.scene.dump(folder/'audition.json',r);return r
 def fix(self):
  r=self.fixture();m.mutate({'id':self.project['id'],'action':'choose_design','audition_id':r['id']});self.project=m.mutate({'id':self.project['id'],'action':'fix_identity'});return r
 def populate(self):
  self.fix();p=m.load(self.project['id'])
  for style,s in p['styles'].items():
   a=self.fixture('performance',m.DEVELOPMENT_TEXT);ref=m.snapshot(a);c={'audition_id':a['id'],'reference':ref,'direction':s['direction'],'identity_sha256':p['identity']['reference']['sha256']};s['candidates'].append(c);s['selected']=a['id'];batch=str(uuid.uuid4())
   for text in m.TRIAL_TEXTS:
    t=self.fixture('profile_reuse',text);s['trials'].append({'audition_id':t['id'],'state':'saved','batch_id':batch,'candidate_id':a['id'],'text':text,'reference':m.snapshot(t)})
  m.save(p);return p
 def review_all(self):
  p=m.load(self.project['id'])
  for style,s in p['styles'].items():m.mutate({'id':p['id'],'action':'review','style':style,'binding':m.evidence(s)['binding'],'words':True,'identity':True,'delivery':True,'note':'Isolated simulated listener fixture only'})
 def test_stage_gates_are_server_enforced(self):
  with self.assertRaisesRegex(ValueError,'Choose'):m.mutate({'id':self.project['id'],'action':'fix_identity'})
  with self.assertRaisesRegex(ValueError,'Fix'):m.generate({'id':self.project['id']})
  with self.assertRaisesRegex(ValueError,'Complete'):m.package({'id':self.project['id']})
 def test_pinned_identity_and_stage_survive_reload(self):
  r=self.fix();m.mutate({'id':self.project['id'],'action':'stage','stage':4});p=m.load(self.project['id']);self.assertEqual(p['stage'],4);self.assertEqual(p['identity']['reference']['sha256'],m.scene.digest(r['audio']['path']))
  with self.assertRaisesRegex(ValueError,'fixed'):m.mutate({'id':p['id'],'action':'choose_design','audition_id':r['id']})
  Path(r['audio']['path']).write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'changed'):m.generate({'id':p['id']})
 def test_selection_invalidates_review_without_deleting_history(self):
  p=self.populate();self.review_all();self.assertTrue(m.public(m.load(p['id']))['ready_to_publish']);p=m.load(p['id']);s=p['styles']['anger'];new=self.fixture('performance');s['candidates'].append({'audition_id':new['id'],'reference':m.snapshot(new)});m.save(p);m.mutate({'id':p['id'],'action':'select','style':'anger','audition_id':new['id']});p=m.load(p['id']);self.assertFalse(m.evidence(p['styles']['anger'])['qualified']);self.assertEqual(len(p['styles']['anger']['reviews']),1)
 def test_stale_review_and_non_boolean_checks_rejected(self):
  p=self.populate();e=m.evidence(p['styles']['neutral']);q={'id':p['id'],'action':'review','style':'neutral','binding':e['binding'],'words':True,'identity':True,'delivery':True}
  with self.assertRaisesRegex(ValueError,'changed'):m.mutate({**q,'binding':{}})
  with self.assertRaisesRegex(ValueError,'Explicit'):m.mutate({**q,'words':'true'})
 def test_word_disagreement_requires_listener_note(self):
  p=self.populate();e=m.evidence(p['styles']['neutral']);r=m.designer.get(e['trials'][0]['audition_id']);r['word_check']['exact_words']=False;m.scene.dump(self.paths['AUDITIONS']/r['id']/'audition.json',r)
  q={'id':p['id'],'action':'review','style':'neutral','binding':e['binding'],'words':True,'identity':True,'delivery':True}
  with self.assertRaisesRegex(ValueError,'Explain'):m.mutate(q)
  m.mutate({**q,'note':'In this fixture, listener explicitly overrode the diagnostic.'})
 def test_publish_is_self_contained_and_immutable(self):
  p=self.populate();self.review_all();result=m.package({'id':p['id']});self.assertTrue(result['package_id']);archive=zipfile.ZipFile(io.BytesIO(m.export(p['id'])));self.assertIn('manifest.json',archive.namelist());self.assertEqual(len([n for n in archive.namelist() if n.endswith('.wav')]),22)
  manifest=json.loads(archive.read('manifest.json'));self.assertEqual(manifest['qualified_engines'],['vox']);self.assertEqual(len(m.casting_voices()),1)
  for style in manifest['performances'].values():self.assertTrue(Path(style['reference']['path']).is_file())
  with self.assertRaisesRegex(ValueError,'published'):m.mutate({'id':p['id'],'action':'select','style':'neutral','audition_id':p['styles']['neutral']['selected']})
  revised=m.mutate({'id':p['id'],'action':'revision'});self.assertEqual(revised['version'],2);self.assertEqual(revised['identity'],result['identity']);self.assertIsNone(revised['package_id'])
 def test_published_profile_resolves_in_real_scene_contract(self):
  p=self.populate();self.review_all();result=m.package({'id':p['id']});lib=m.scene.libraries()['characters'];voice='character:'+result['package_id'];other=lib['roles']['B']['speaker_id']
  resolved,settings,ids=m.scene.validate({'library':'characters','model':'vox','casting':{'A':voice,'B':other}})
  self.assertEqual(resolved['roles']['A']['package_id'],result['package_id'])
  self.assertTrue(resolved['roles']['A']['performances']['anger']['id'])
  with self.assertRaisesRegex(ValueError,'VoxCPM2 only'):m.scene.validate({'library':'characters','model':'index','casting':{'A':voice,'B':other}})
 def test_emotion_guide_is_in_portable_draft_and_published_profile(self):
  p=self.populate();r=m.designer.get(p['styles']['anger']['selected']);guide=self.root/'acted-guide.wav';guide.write_bytes(b'Isolated acted-guide fixture');r['request']['emotion_reference']={'id':'fixture:anger','path':str(guide),'sha256':m.scene.digest(guide),'transcript':'Fixture words.','terms':'Fixture only','emotion':'anger'};m.scene.dump(self.paths['AUDITIONS']/r['id']/'audition.json',r)
  draft=zipfile.ZipFile(io.BytesIO(m.export(p['id'])));self.assertIn('emotion-references.json',draft.namelist());self.assertEqual(len(json.loads(draft.read('emotion-references.json'))),1)
  self.review_all();result=m.package({'id':p['id']});archive=zipfile.ZipFile(io.BytesIO(m.export(p['id'])));self.assertIn('emotion-anger.wav',archive.namelist());manifest=json.loads(archive.read('manifest.json'));ref=manifest['performances']['anger']['emotion_reference'];self.assertEqual(ref['archive_path'],'emotion-anger.wav');self.assertEqual(m.scene.digest(ref['path']),ref['sha256']);voice=next(iter(m.casting_voices().values()));self.assertEqual(voice['source_terms'],['Fixture only']);self.assertEqual(voice['performance_guides']['anger']['sha256'],ref['sha256'])
 def test_tampered_trial_blocks_publish(self):
  p=self.populate();self.review_all();Path(p['styles']['anger']['trials'][0]['reference']['path']).write_bytes(b'modified')
  with self.assertRaisesRegex(ValueError,'changed'):m.package({'id':p['id']})
  self.assertEqual(m.casting_voices(),{})
 def test_draft_export_and_casting_exclusion(self):
  self.populate();archive=zipfile.ZipFile(io.BytesIO(m.export(self.project['id'])));self.assertIn('STATUS.txt',archive.namelist());self.assertNotIn('manifest.json',archive.namelist());self.assertEqual(m.casting_voices(),{})
 def test_native_direction_uses_fixed_reference(self):
  self.fix();p=m.load(self.project['id']);q=m.designer.validate({'text':m.DEVELOPMENT_TEXT,'performance_direction':'Tender reassurance'},reference_profile={'name':p['name'],'reference':p['identity']['reference']});r=m.designer.create_record(q);captured={}
  def post(*args,**kwargs):captured.update(kwargs['files']);return type('Response',(),{'status_code':503,'text':'controlled fixture failure'})()
  lockpath=self.root/'take-generation.lock'
  with patch.object(m.scene,'STUDY',self.root),patch.object(m.designer.requests,'post',post):m.designer.run(r,release_queue=False)
  self.assertEqual(captured['instruct'][1],'Tender reassurance');self.assertIn('ref_audio',captured);self.assertEqual(captured['ref_text'][1],p['identity']['reference']['transcript'])
 def test_worker_preserves_success_after_failure_and_releases_queue(self):
  self.fix();p=m.load(self.project['id']);plans=[{'style':k,'direction':v,'request':{'text':m.DEVELOPMENT_TEXT,'profile':p['identity'],'mode':'performance'}} for k,v in list(m.STYLES.items())[:2]];job={'id':str(uuid.uuid4()),'state':'queued','kind':'performance','done':0,'results':[]};p['jobs'].append(job);m.save(p);count=[0]
  def fake_run(r,release_queue):
   count[0]+=1;r['state']='failed' if count[0]==1 else 'saved';r['error']='Controlled fixture failure'
   if r['state']=='saved':r['audio']=self.fixture()['audio']
   m.scene.dump(self.paths['AUDITIONS']/r['id']/'audition.json',r)
  m.scene.QUEUE.acquire()
  with patch.object(m.designer,'run',fake_run):m.run(p['id'],job['id'],plans)
  p=m.load(p['id']);self.assertEqual(p['jobs'][0]['state'],'finished_with_failures');self.assertEqual(p['jobs'][0]['done'],2);self.assertEqual(len(p['styles']['reassurance']['candidates']),1);self.assertFalse(m.scene.QUEUE.locked())
 def test_restart_marks_interrupted_jobs_without_losing_results(self):
  p=m.load(self.project['id']);p['jobs']=[{'state':'running','results':[{'state':'saved'}]}];m.save(p);m.recover();p=m.load(p['id']);self.assertEqual(p['jobs'][0]['state'],'interrupted');self.assertEqual(len(p['jobs'][0]['results']),1)
if __name__=='__main__':unittest.main()
