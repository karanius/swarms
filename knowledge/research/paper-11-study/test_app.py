"""Live local HTTP acceptance checks. Start app_server.py first."""
import unittest, requests
import architecture
from test_upgrade import VIDEO_QUERY
BASE='http://127.0.0.1:5193'
class AppTests(unittest.TestCase):
 def setUp(self):
  self.s=requests.Session();self.assertEqual(self.s.get(BASE+'/api/session').status_code,200)
 def post(self,payload):return self.s.post(BASE+'/api/propose',json=payload,headers={'Origin':BASE})
 def test_propose_revise_and_isolate(self):
  r=self.post({'question':VIDEO_QUERY});self.assertEqual(r.status_code,200,r.text);a=r.json()['proposal'];self.assertEqual(a['coverage']['logical_requirement_groups'],5)
  chosen=next(x['primary']['id'] for x in a['slots'] if x['primary'])
  r=self.post({'question':VIDEO_QUERY,'parent':a['revision'],'excluded':[chosen],'reason':'Acceptance test alternative'});self.assertEqual(r.status_code,200,r.text);b=r.json();self.assertEqual(b['history'][0],a);self.assertEqual(b['proposal']['parent_revision'],1);self.assertFalse(any(x['primary'] and x['primary']['id']==chosen for x in b['proposal']['slots']))
  other=requests.Session();other.get(BASE+'/api/session');r=other.post(BASE+'/api/propose',json={'question':VIDEO_QUERY,'parent':1,'reason':'Invalid cross-session parent'},headers={'Origin':BASE});self.assertEqual(r.status_code,400)
 def test_clarify_then_context_changes_proposal(self):
  q='Local video generation on my Mac'
  r=self.s.post(BASE+'/api/clarify',json={'question':q},headers={'Origin':BASE});self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['questions']),3)
  r=self.post({'question':q,'context':{'memory_gb':64,'output_goal':'narrated_video','duration_seconds':30,'visual_path':'video_generation'}});self.assertEqual(r.status_code,200,r.text);p=r.json()['proposal'];self.assertFalse(p['decision_support']['questions']);self.assertIn('video_assembly',{s['capability'] for s in p['slots']});self.assertEqual(p['coverage']['validated_implementations'],0)
  self.assertEqual(self.post({'question':q,'context':{'memory_gb':-2}}).status_code,400)
 def test_validation_and_origin(self):
  self.assertEqual(self.post({'question':'x'}).status_code,400)
  self.assertEqual(self.s.post(BASE+'/api/propose',json={'question':VIDEO_QUERY}).status_code,403)
  self.assertEqual(self.s.get(BASE+'/',headers={'Host':'untrusted.example'}).status_code,403)
  self.assertEqual(self.s.get(BASE+'/../../architecture.py').status_code,404)
  self.assertEqual(requests.post(BASE+'/api/propose',json={'question':VIDEO_QUERY},headers={'Origin':BASE}).status_code,401)
if __name__=='__main__':unittest.main()
