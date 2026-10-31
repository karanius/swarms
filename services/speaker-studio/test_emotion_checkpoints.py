import copy,json,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
import scene,voice_designer as d,emotion_checkpoints as c,acted_conversion as cv
class NoThread:
 def __init__(self,*args,**kwargs):pass
 def start(self):pass
class Checkpoints(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.patches=[]
  for obj,key,value in [(d,'DATA',self.root),(d,'AUDITIONS',self.root/'auditions'),(d,'PROFILES',self.root/'profiles'),(c,'ROOT',self.root/'checkpoints')]:
   value.mkdir(exist_ok=True);p=patch.object(obj,key,value);p.start();self.patches.append(p)
  raw=self.root/'voice.wav';raw.write_bytes(b'fixed identity audio');self.guide={'id':'test:anger','path':str(raw),'sha256':scene.digest(raw),'transcript':'Listen to me.','label':'Test actor','emotion':'anger'}
  self.source=d.create_record({'mode':'voice_design','text':'Hello there.','description':'A warm voice','seed':42,'steps':10,'guidance':2,'profile':None})
  self.source.update(state='saved',audio={'path':str(raw),'sha256':scene.digest(raw)});scene.dump(d.AUDITIONS/self.source['id']/'audition.json',self.source)
  self.p=patch.object(cv,'guide_for',return_value=self.guide);self.p.start();self.patches.append(self.p)
  self.resolve=patch.object(c.bridge,'resolve',return_value=self.guide);self.resolve.start();self.patches.append(self.resolve)
  self.thread=patch.object(c.threading,'Thread',NoThread);self.thread.start();self.patches.append(self.thread)
 def tearDown(self):
  if scene.QUEUE.locked():scene.QUEUE.release()
  for p in reversed(self.patches):p.stop()
  self.tmp.cleanup()
 def new(self):return c.create({'token':str(uuid.uuid4()),'source':self.source['id'],'text':'Stay right here.','style':'anger','reference_id':'test:anger'})
 def actor(self,s):
  q={'id':s['id'],'action':'actor','token':str(uuid.uuid4()),'seed':65,'duration_scale':1.2};s=c.command(q);r=d.get(s['attempts'][-1]['actor_id']);r.update(state='saved',audio=self.source['audio'],word_check={'exact_words':True});scene.dump(d.AUDITIONS/r['id']/'audition.json',r);scene.QUEUE.release();return c.refresh(s),q
 def test_gate_retry_preservation_and_reload(self):
  s=self.new();self.assertEqual(s['attempts'],[])
  with self.assertRaises(ValueError):c.command({'id':s['id'],'action':'convert','actor_id':'missing','token':str(uuid.uuid4()),'approve':True})
  s,q=self.actor(s);self.assertEqual(len(c.command(q)['attempts']),1)
  a=s['attempts'][0];convert={'id':s['id'],'action':'convert','actor_id':a['actor_id'],'token':str(uuid.uuid4()),'approve':False,'seed':99}
  with self.assertRaises(ValueError):c.command(convert)
  convert['approve']=True
  out=d.create_record({'mode':'acted_conversion','profile':s['profile'],'text':s['text'],'seed':99});out['state']='saved';scene.dump(d.AUDITIONS/out['id']/'audition.json',out)
  with patch.object(cv,'start',return_value=out) as start:
   s=c.command(convert);payload=start.call_args.args[0];self.assertEqual(payload['approved_actor_id'],a['actor_id']);self.assertEqual(payload['actor_approval']['actor_sha256'],self.guide['sha256'])
   c.command(convert);self.assertEqual(start.call_count,1)
   convert.update(token=str(uuid.uuid4()),retry=True,seed=100);s=c.command(convert)
   self.assertEqual(len(s['attempts'][0]['conversion_history']),1)
   self.assertEqual(s['attempts'][0]['actor_id'],a['actor_id'])
  loaded=c.listing()['sessions'][0];self.assertEqual(loaded['profile'],s['profile']);self.assertEqual(loaded['text'],'Stay right here.')
 def test_new_actor_is_a_separate_attempt_and_bad_review_rejected(self):
  s=self.new();s,_=self.actor(s);first=s['attempts'][0]['actor_id'];s,_=self.actor(s)
  self.assertEqual(len(s['attempts']),2);self.assertNotEqual(first,s['attempts'][1]['actor_id'])
  selected=c.command({'id':s['id'],'action':'select_actor','actor_id':first});self.assertEqual(selected['active_attempt'],s['attempts'][0]['token'])
  c.command({'id':s['id'],'action':'select_actor','actor_id':s['attempts'][1]['actor_id']})
  with self.assertRaises(ValueError):c.command({'id':s['id'],'action':'review','subject':'actor','choice':'keep','recording_id':first})
 def test_conversion_consumes_approved_audio_without_regenerating_actor(self):
  s=self.new();s,_=self.actor(s);actor=d.get(s['attempts'][0]['actor_id'])
  runtime=self.root/'runtime';(runtime/'venv/bin').mkdir(parents=True);(runtime/'venv/bin/python').touch()
  q={'profile_id':s['profile']['id'],'text':s['text'],'seed':99,'target_style':'anger','reference_id':self.guide['id'],'approved_actor_id':actor['id'],'actor_approval':{'actor_id':actor['id'],'actor_sha256':actor['audio']['sha256'],'emotion':True,'pace_quality':True},'conversion_settings':{'steps':40,'cfg':.8,'length_adjust':1.1}}
  class Result:
   returncode=0
   stdout=json.dumps({'path':str(self.root/'voice.wav'),'listening_path':str(self.root/'voice.wav'),'sha256':self.guide['sha256'],'exact_words':True})
  with patch.object(cv.seedvc_runner,'RUNTIME',runtime),patch.object(scene,'STUDY',self.root),patch.object(cv.bridge,'run') as generated,patch.object(cv.seedvc_runner,'convert',return_value=(self.root/'voice.wav',q['conversion_settings'])) as convert,patch.object(cv.subprocess,'run',return_value=Result()):
   r=cv.start(q);cv.run(r)
   generated.assert_not_called();self.assertEqual(convert.call_args.args[0],actor['audio']['path']);self.assertEqual(convert.call_args.args[4],q['conversion_settings'])
   self.assertEqual(r['actor_audition_id'],actor['id']);self.assertEqual(r['state'],'saved')
 def test_trash_restore_and_empty_preserve_archive(self):
  s=self.new();s,_=self.actor(s);actor=s['attempts'][0]['actor_id']
  with self.assertRaises(ValueError):c.command({'id':s['id'],'action':'purge'})
  s=c.command({'id':s['id'],'action':'trash','deleted':True});self.assertTrue(s['deleted']);self.assertTrue((d.AUDITIONS/actor/'audition.json').exists())
  s=c.command({'id':s['id'],'action':'trash','deleted':False});self.assertFalse(s['deleted'])
  c.command({'id':s['id'],'action':'trash','deleted':True});c.command({'id':s['id'],'action':'purge'})
  self.assertEqual(c.listing()['sessions'],[]);self.assertEqual(d.get(actor)['id'],actor);self.assertTrue(self.raw.exists() if hasattr(self,'raw') else Path(self.guide['path']).exists())
 def test_restart_marks_interrupted_step_without_resubmission(self):
  s=self.new();s=c.command({'id':s['id'],'action':'actor','token':str(uuid.uuid4()),'seed':42})
  actor=s['attempts'][0]['actor_id'];c.recover()
  self.assertEqual(d.get(actor)['state'],'failed');self.assertEqual(len(c.listing()['sessions'][0]['attempts']),1)
 def test_35_word_gate_and_changed_sample(self):
  with self.assertRaises(ValueError):c.create({'token':str(uuid.uuid4()),'source':self.source['id'],'text':' '.join(['word']*36)+'.','style':'anger','reference_id':'test:anger'})
  s=self.new();Path(self.guide['path']).write_bytes(b'changed')
  with self.assertRaises(ValueError):c.command({'id':s['id'],'action':'actor','token':str(uuid.uuid4()),'seed':65})
 def test_conversion_rejects_wrong_or_modified_actor(self):
  s=self.new();s,_=self.actor(s);a=d.get(s['attempts'][0]['actor_id'])
  q={'profile_id':s['profile']['id'],'text':'Different words.','seed':65,'target_style':'anger','reference_id':self.guide['id'],'approved_actor_id':a['id'],'actor_approval':{'actor_id':a['id'],'actor_sha256':a['audio']['sha256'],'emotion':True,'pace_quality':True}}
  with self.assertRaises(ValueError):cv.start(q)
  q['text']=s['text'];Path(a['audio']['path']).write_bytes(b'changed')
  with self.assertRaises(ValueError):cv.start(q)
if __name__=='__main__':unittest.main()
