"""Isolated feedback-policy contracts, never real listener approvals."""
import copy,unittest,uuid,types
from unittest.mock import patch
import character_workflow as w
import guided_loop as g
import performance_bridge as b
import test_character_workflow as fixture_module
class GuidedTests(unittest.TestCase):
 setUp=fixture_module.WorkflowTests.setUp
 tearDown=fixture_module.WorkflowTests.tearDown
 fixture=fixture_module.WorkflowTests.fixture
 fix=fixture_module.WorkflowTests.fix
 populate=fixture_module.WorkflowTests.populate
 def candidate(self):
  p=self.populate();s=p['styles']['anger'];r=w.designer.get(s['selected']);guide=copy.deepcopy(p['identity']['reference']);guide.update(id='fixture:anger',emotion='anger',label='Fixture acting',terms='Fixture only');r['request'].update(mode='reference_performance',profile=p['identity'],emotion_reference=guide,strength=1,duration_scale=1);w.scene.dump(self.paths['AUDITIONS']/r['id']/'audition.json',r);return p,s,r
 def control(self,p,s):
  a=self.fixture();s['loop']={'controls':[{'audition_id':a['id'],'candidate_id':s['selected'],'state':'saved'}],'events':[]};w.save(p);return a
 def command(self,p,action,**kw):return g.command({'id':p['id'],'style':'anger','action':action,'binding':g.view(w.load(p['id']),'anger')['binding'],**kw})
 def test_control_is_required_before_comparison(self):
  p,s,r=self.candidate();self.assertEqual(g.view(p,'anger')['phase'],'needs_control');self.control(p,s);self.assertEqual(g.view(p,'anger')['phase'],'comparison')
 def test_stale_feedback_rejected(self):
  p,s,r=self.candidate();self.control(p,s)
  with self.assertRaisesRegex(ValueError,'changed'):g.command({'id':p['id'],'style':'anger','action':'improve','binding':{},'issue':'words'})
 def test_keep_requires_explicit_confirmation_and_never_approves_initial_take(self):
  p,s,r=self.candidate();self.control(p,s)
  with self.assertRaisesRegex(ValueError,'explicit'):self.command(p,'keep')
  result=self.command(p,'keep',confirm_words_voice_emotion=True);self.assertEqual(result['guided']['anger']['phase'],'validation');self.assertFalse(result['styles']['anger']['evidence']['qualified']);self.assertEqual(result['styles']['anger']['reviews'],[])
 def test_uncertainty_never_generates(self):
  p,s,r=self.candidate();self.control(p,s);result=self.command(p,'improve',issue='uncertain');self.assertEqual(result['guided']['anger']['recommendation']['kind'],'relisten')
  with self.assertRaisesRegex(ValueError,'no supported'):self.command(p,'try')
 def test_identical_state_has_identical_rule_and_bounded_seed_changes(self):
  p,s,r=self.candidate();self.assertEqual(g.plan_for(p,'anger','words','comparison'),g.plan_for(p,'anger','words','comparison'));s['loop']={'events':[{'action':'try','issue':'words'},{'action':'try','issue':'words'}]};self.assertEqual(g.plan_for(p,'anger','words','comparison')['kind'],'stop')
 def test_vector_changes_character_control_stays_acted_audio(self):
  p,s,r=self.candidate();recommendation=g.plan_for(p,'anger','emotion_character','comparison');self.assertEqual(recommendation['rule'],'native_vector')
  with patch.object(b,'resolve',return_value=r['request']['emotion_reference']):plans=g.performance_plan(p,'anger',recommendation)
  self.assertEqual(plans[0]['request']['emotion_vector'],[0,1,0,0,0,0,0,0]);self.assertNotIn('emotion_vector',plans[1]['request']);self.assertEqual(plans[1]['request']['emotion_mode'],'audio');self.assertEqual(plans[0]['request']['profile']['reference'],p['identity']['reference'])
 def test_native_vector_reaches_worker_and_disables_emotion_audio(self):
  p,s,r=self.candidate();r['request']['emotion_vector']=[0,1,0,0,0,0,0,0];r['request']['emotion_mode']='vector';captured={}
  def native(**kw):captured.update(kw);raise RuntimeError('Fixture ends before inference')
  with patch.object(b.scene,'STUDY',self.root),patch.object(b.scene,'module',return_value=types.SimpleNamespace(run=native)):b.run(r,release_queue=False)
  self.assertEqual(captured['conditions'][0]['emo_vector'],[0,1,0,0,0,0,0,0]);native_fields=__import__('json').loads((self.paths['AUDITIONS']/r['id']/'native-fields.json').read_text());self.assertFalse(native_fields['emotion_reference_applied'])
 def test_validation_failure_stays_unqualified_and_stops_unsupported_engine_handoff(self):
  p,s,r=self.candidate();self.control(p,s);self.command(p,'keep',confirm_words_voice_emotion=True);result=self.command(p,'improve',issue='emotion_character');self.assertEqual(result['guided']['anger']['recommendation']['kind'],'stop');self.assertFalse(result['styles']['anger']['evidence']['qualified'])
 def test_control_failure_preserves_selected_candidate_and_releases_queue(self):
  p,s,r=self.candidate();job={'id':str(uuid.uuid4()),'kind':'guided','state':'queued','done':0,'results':[]};p['jobs'].append(job);w.save(p)
  def fail(a,release_queue):a['state']='failed';a['error']='Controlled failure';w.scene.dump(self.paths['AUDITIONS']/a['id']/'audition.json',a)
  w.scene.QUEUE.acquire()
  with patch.object(b,'run',fail):w.run(p['id'],job['id'],[{'style':'anger','purpose':'control','candidate_id':s['selected'],'request':g.make_control(s['candidates'][0])}])
  saved=w.load(p['id']);self.assertEqual(saved['styles']['anger']['selected'],s['selected']);self.assertEqual(g.view(saved,'anger')['phase'],'needs_control');self.assertFalse(w.scene.QUEUE.locked())
 def test_try_is_serial_and_control_never_replaces_character(self):
  p,s,r=self.candidate();self.control(p,s);self.command(p,'improve',issue='words');captured={}
  def launch(project,kind,plans):captured.update(project=project,kind=kind,plans=plans);return w.public(project)
  with patch.object(w,'launch',launch),patch.object(b,'resolve',return_value=r['request']['emotion_reference']):self.command(p,'try')
  plans=captured['plans'];self.assertEqual([p['purpose'] for p in plans],['performance','control']);self.assertEqual(plans[0]['request']['seed'],24)
  project=captured['project'];job={'id':str(uuid.uuid4()),'kind':'guided','state':'queued','done':0,'results':[]};project['jobs'].append(job);w.save(project);order=[]
  def save(a,release_queue):
   order.append(a['id']);a['state']='saved';a['audio']=self.fixture()['audio'];a['word_check']={'exact_words':True};w.scene.dump(self.paths['AUDITIONS']/a['id']/'audition.json',a)
  w.scene.QUEUE.acquire()
  with patch.object(b,'run',save):w.run(p['id'],job['id'],plans)
  final=w.load(p['id']);self.assertEqual(final['styles']['anger']['selected'],order[0]);self.assertEqual(g.view(final,'anger')['control']['audition_id'],order[1]);self.assertFalse(w.scene.QUEUE.locked())
 def test_keep_validation_qualifies_only_exact_pair_and_persists(self):
  p,s,r=self.candidate();self.control(p,s);self.command(p,'keep',confirm_words_voice_emotion=True);result=self.command(p,'keep',confirm_words_voice_emotion=True);self.assertTrue(result['styles']['anger']['evidence']['qualified']);self.assertEqual(g.view(w.load(p['id']),'anger')['phase'],'qualified');self.assertFalse(result['ready_to_publish'])
 def test_draft_contains_control_recording_and_feedback_history(self):
  import zipfile,io,json
  p,s,r=self.candidate();control=self.control(p,s);self.command(p,'improve',issue='uncertain');archive=zipfile.ZipFile(io.BytesIO(w.export(p['id'])));self.assertIn(control['id']+'.wav',archive.namelist());saved=json.loads(archive.read('draft-project.json'));self.assertEqual(saved['guided']['anger']['feedback']['issue'],'uncertain')
if __name__=='__main__':unittest.main()
