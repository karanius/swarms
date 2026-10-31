import hashlib,json,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch
import asset_passport as p

class PassportTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.data=self.root/'voice-designer';self.a=self.data/'auditions';self.a.mkdir(parents=True)
  self.patches=[patch.object(p.designer,'AUDITIONS',self.a),patch.object(p.designer,'DATA',self.data)]
  for q in self.patches:q.start()
 def tearDown(self):
  for q in reversed(self.patches):q.stop()
  self.temp.cleanup()
 def record(self,mode,profile=None,guide=None,actor=None):
  ident=str(uuid.uuid4());folder=self.a/ident;folder.mkdir();raw=folder/'voice.wav';raw.write_bytes(('fixture '+ident).encode());listen=folder/'listening.wav';listen.write_bytes(b'playback fixture')
  r={'id':ident,'state':'saved','engine':'Fixture','created':1,'request':{'mode':mode,'text':'Saved words.','description':'Saved voice brief.','seed':65,'profile':profile},'audio':{'path':str(raw),'listening_path':str(listen),'sha256':p.file_hash(raw),'gain':1.2},'model_provenance':{'revision':'fixture'}}
  if guide:r['request']['emotion_reference']=guide
  if actor:r['actor_audition_id']=actor['id']
  (folder/'audition.json').write_text(json.dumps(r));return r
 def profile(self,r):return {'id':str(uuid.uuid4()),'name':'Frozen identity','audition_id':r['id'],'reference':{'path':r['audio']['path'],'sha256':r['audio']['sha256'],'transcript':r['request']['text']}}
 def test_three_stage_lineage_and_actor_inputs(self):
  original=self.record('voice_design');test=self.record('profile_reuse',self.profile(original));ref_file=self.root/'actor.wav';ref_file.write_bytes(b'acted sample');ref={'id':'actor:anger','path':str(ref_file),'sha256':p.file_hash(ref_file),'transcript':'Actor words.','emotion':'anger'}
  actor=self.record('reference_performance',{'name':'Actor','reference':ref},ref);final=self.record('acted_conversion',self.profile(test),ref,actor)
  result=p.get(final['id']);m=result['passport'];ids={n.get('recording_id') for n in m['nodes']}
  self.assertTrue({r['id'] for r in (original,test,actor,final)}<=ids)
  self.assertIn({'from':'recording:'+actor['id'],'to':'recording:'+final['id'],'role':'performed_audio_to_convert'},m['edges'])
  self.assertTrue(all(x['status']=='match' for x in result['integrity']['assets']))
 def test_seal_does_not_follow_changed_source_metadata_and_reports_changed_audio(self):
  r=self.record('voice_design');first=p.seal(r['id']);path=self.a/r['id']/'audition.json';changed=json.loads(path.read_text());changed['request']['description']='Different current description';path.write_text(json.dumps(changed));Path(r['audio']['path']).write_bytes(b'tampered')
  result=p.get(r['id']);self.assertEqual(first,result['passport']);self.assertIn('changed',[x['status'] for x in result['integrity']['assets']])
 def test_related_stage_two_test_is_not_a_parent(self):
  original=self.record('voice_design');test=self.record('profile_reuse',self.profile(original));final=self.record('acted_conversion',self.profile(original))
  result=p.get(final['id']);self.assertEqual(result['related_identity_tests'][0]['id'],test['id']);self.assertNotIn('recording:'+test['id'],[n['id'] for n in result['passport']['nodes']]);self.assertTrue(result['passport']['warnings'])
 def test_missing_parent_and_cycle_are_explicit(self):
  r=self.record('profile_reuse',{'audition_id':str(uuid.uuid4()),'reference':{}});self.assertTrue(p.get(r['id'])['passport']['warnings'])
  a=self.record('voice_design');path=self.a/a['id']/'audition.json';a['request']['profile']={'audition_id':a['id'],'reference':{}};path.write_text(json.dumps(a));self.assertTrue(any('Cycle' in w for w in p.get(a['id'])['passport']['warnings']))
if __name__=='__main__':unittest.main()
