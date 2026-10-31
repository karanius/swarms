import copy,json,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
import scene,voice_designer as d,emotion_checkpoints as c,direct_emotions as direct
class NoThread:
 def __init__(self,*args,**kwargs):pass
 def start(self):pass
class DirectEmotionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.patches=[]
  for obj,key,value in [(d,'DATA',self.root),(d,'AUDITIONS',self.root/'auditions'),(d,'PROFILES',self.root/'profiles'),(c,'ROOT',self.root/'checkpoints'),(direct,'ROOT',self.root/'direct')]:
   value.mkdir(exist_ok=True);p=patch.object(obj,key,value);p.start();self.patches.append(p)
  p=patch.object(direct.threading,'Thread',NoThread);p.start();self.patches.append(p)
  raw=self.root/'reference.wav';raw.write_bytes(b'kept angry Santa');self.raw=raw
  self.source=d.create_record({'mode':'acted_conversion','text':'Stay right here.','profile':None,'seed':65,'steps':10,'guidance':2})
  self.source.update(state='saved',word_check={'exact_words':True},audio={'path':str(raw),'sha256':scene.digest(raw)},elapsed_seconds=15);scene.dump(d.AUDITIONS/self.source['id']/'audition.json',self.source)
  self.s={'id':str(uuid.uuid4()),'created':1,'style':'anger','attempts':[{'actor_id':str(uuid.uuid4()),'conversion_id':self.source['id'],'final_decision':'keep','actor_approval':{'emotion':True},'reviews':[]} ]};c.save(self.s)
 def tearDown(self):
  if scene.QUEUE.locked():scene.QUEUE.release()
  for p in reversed(self.patches):p.stop()
  self.temp.cleanup()
 def promote(self):return direct.promote({'checkpoint_id':self.s['id'],'source_id':self.source['id']})
 def generate(self,p,text='Leave those presents alone.',engine='vox'):
  q={'id':p['id'],'action':'generate','token':str(uuid.uuid4()),'text':text,'seed':65,'engine':engine};out=direct.command(q);r=d.get(out['runs'][-1]['id']);scene.QUEUE.release();return out,r,q
 def complete(self,r):
  r.update(state='saved',word_check={'exact_words':True},audio=self.source['audio'],elapsed_seconds=5);scene.dump(d.AUDITIONS/r['id']/'audition.json',r)
 def test_promote_requires_kept_source_and_is_idempotent(self):
  self.s['attempts'][0]['final_decision']='emotion';c.save(self.s)
  with self.assertRaises(ValueError):self.promote()
  self.s['attempts'][0]['final_decision']='keep';c.save(self.s)
  p=self.promote();self.assertEqual(p['source_id'],self.source['id']);self.assertEqual(self.promote()['id'],p['id']);self.assertEqual(p['status'],'experimental')
 def test_direct_routes_and_snapshot_no_conversion(self):
  p=self.promote();p,r,q=self.generate(p);self.assertEqual(r['request']['mode'],'profile_reuse');self.assertEqual(r['request']['profile']['audition_id'],self.source['id']);self.assertEqual(r['request']['emotion_route'],'direct');self.assertNotIn('actor_audition_id',r)
  self.complete(r);p,index,q2=self.generate(p,engine='index');iq=index['request'];self.assertEqual(iq['mode'],'reference_performance');self.assertEqual(iq['profile']['reference']['sha256'],iq['emotion_reference']['sha256']);self.assertEqual(iq['target_style'],'anger');self.assertEqual(iq['strength'],1)
  # Replaying the same token never creates another generation.
  self.assertEqual(len(direct.command(q2)['runs']),2)
 def test_qualification_needs_three_fresh_sentences_for_same_engine(self):
  p=self.promote()
  for text,engine in [('Leave them alone.','vox'),('LEAVE THEM ALONE!','vox'),('I warned you.','index')]:
   p,r,_=self.generate(p,text,engine);self.complete(r);p=direct.command({'id':p['id'],'action':'review','recording_id':r['id'],'choice':'keep'})
  self.assertEqual(p['status'],'experimental');self.assertEqual(p['qualifying_by_engine']['VoxCPM2'],1)
  p,r,_=self.generate(p,'You must listen to me.');self.complete(r);p=direct.command({'id':p['id'],'action':'review','recording_id':r['id'],'choice':'keep'})
  self.assertEqual(p['qualifying_by_engine']['VoxCPM2'],2);self.assertEqual(p['status'],'experimental')
  p,r,_=self.generate(p,'Those gifts belong to everyone.');self.complete(r);p=direct.command({'id':p['id'],'action':'review','recording_id':r['id'],'choice':'keep'})
  self.assertEqual(p['qualifying_by_engine']['VoxCPM2'],3);self.assertEqual(p['status'],'qualified')
 def test_trash_restore_keeps_audio_and_blocks_generation(self):
  p=self.promote();p,r,_=self.generate(p);self.complete(r)
  p=direct.command({'id':p['id'],'action':'trash','recording_id':r['id'],'deleted':True});self.assertTrue(p['runs'][0]['deleted']);self.assertTrue(self.raw.exists())
  p=direct.command({'id':p['id'],'action':'trash','deleted':True})
  with self.assertRaises(ValueError):self.generate(p)
  p=direct.command({'id':p['id'],'action':'trash','deleted':False});self.assertFalse(p['deleted'])
 def test_empty_direct_trash_keeps_ancestry(self):
  p=self.promote();p,r,_=self.generate(p);self.complete(r)
  with self.assertRaises(ValueError):direct.command({'id':p['id'],'action':'purge','recording_id':r['id']})
  direct.command({'id':p['id'],'action':'trash','recording_id':r['id'],'deleted':True})
  p=direct.command({'id':p['id'],'action':'purge','recording_id':r['id']});self.assertTrue(p['runs'][0]['workspace_removed']);self.assertTrue(self.raw.exists());self.assertEqual(d.get(r['id'])['id'],r['id'])
 def test_invalid_words_and_changed_reference_rejected(self):
  p=self.promote()
  with self.assertRaises(ValueError):self.generate(p,' '.join(['word']*36)+'.')
  self.raw.write_bytes(b'changed')
  with self.assertRaises(ValueError):self.generate(p)
if __name__=='__main__':unittest.main()
