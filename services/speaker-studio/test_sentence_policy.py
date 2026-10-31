"""Single-sentence generation contracts and legacy evidence preservation."""
import sys,unittest,copy,tempfile,json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import sentence_policy as policy
import voice_designer as designer
import character_workflow as workflow
class SentencePolicyTests(unittest.TestCase):
 def test_abbreviations_decimals_and_quotes_are_not_extra_sentences(self):
  for text in ['I need you to stay right here.','Dr. Smith lives in the U.S. and works here.','The price is $3.50 today.','Jonas E. Smith is here.','Wait... stay here.','He said, "Stay right here."']:
   with self.subTest(text=text):self.assertTrue(policy.inspect(text)['valid']);self.assertEqual(policy.inspect(text)['sentence_count'],1)
 def test_multiple_sentences_are_rejected_with_the_count(self):
  for text,count in [('I waited. You returned.',2),('What happened? Tell me.',2),('Stop! Stay here!',2),('I waited.\nYou returned.',2),('I arrived. I waited. I left.',3)]:
   with self.subTest(text=text),self.assertRaisesRegex(ValueError,'found '+str(count)):policy.require(text)
 def test_empty_and_long_targets_fail(self):
  for text in ['', 'Hi.', 'a'*501]:
   with self.subTest(text=text),self.assertRaises(ValueError):policy.require(text)
 def test_designer_api_cannot_bypass_policy(self):
  with self.assertRaisesRegex(ValueError,'one sentence'):designer.validate({'text':'First sentence. Second sentence.','description':'A fixture voice.'})
 def test_invalid_target_never_enters_generation_queue(self):
  with tempfile.TemporaryDirectory() as d,patch.object(workflow,'PROJECTS',Path(d)):
   raw=Path(d)/'identity.wav';raw.write_bytes(b'isolated fixture');p=workflow.create({'name':'Fixture'});p=workflow.load(p['id']);p['identity']={'reference':{'path':str(raw),'sha256':workflow.scene.digest(raw)}};workflow.save(p)
   with patch.object(workflow.scene.B,'inventory') as inventory,patch.object(workflow.threading.Thread,'start') as start:
    with self.assertRaisesRegex(ValueError,'one sentence'):workflow.generate({'id':p['id'],'styles':['anger'],'text':'I arrived. I waited.'})
    inventory.assert_not_called();start.assert_not_called()
   self.assertEqual(workflow.load(p['id'])['jobs'],[])
 def test_legacy_pair_remains_visible_but_cannot_qualify(self):
  s={'selected':'candidate','candidates':[{'audition_id':'candidate','text':'I arrived. I waited.'}],'trials':[{'audition_id':str(i),'candidate_id':'candidate','batch_id':'legacy','text':text,'state':'saved'} for i,text in enumerate(workflow.LEGACY_TRIAL_TEXTS)],'reviews':[]}
  before=copy.deepcopy(s);e=workflow.evidence(s);self.assertEqual(len(e['trials']),2);self.assertFalse(e['single_sentence']);self.assertFalse(e['qualified']);self.assertEqual(s,before)
 def test_new_protocol_pair_is_bound_to_exact_single_sentences(self):
  s={'selected':'candidate','candidates':[{'audition_id':'candidate','text':'I need you to stay right here.'}],'trials':[{'audition_id':str(i),'candidate_id':'candidate','batch_id':'single','text':text,'expected_texts':workflow.TRIAL_TEXTS,'state':'saved'} for i,text in enumerate(workflow.TRIAL_TEXTS)],'reviews':[]}
  e=workflow.evidence(s);self.assertEqual(len(e['trials']),2);self.assertTrue(e['single_sentence']);self.assertFalse(e['qualified'])
if __name__=='__main__':unittest.main()
