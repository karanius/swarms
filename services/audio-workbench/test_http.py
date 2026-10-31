import unittest,requests,time
import test_contracts
BASE='http://127.0.0.1:5194/engine';ORIGIN='http://127.0.0.1:5194'
class HttpContracts(unittest.TestCase):
 def setUp(self):self.s=requests.Session();self.assertEqual(self.s.get(BASE+'/session').status_code,200)
 def test_invalid_graph_and_origin(self):
  g=test_contracts.GraphContracts().graph();g['edges'].pop()
  self.assertEqual(self.s.post(BASE+'/run',json=g,headers={'Origin':ORIGIN}).status_code,400)
  self.assertEqual(self.s.post(BASE+'/run',json=g,headers={'Origin':'https://untrusted.example'}).status_code,403)
 def test_session_isolation_and_file_boundary(self):
  self.assertEqual(self.s.get(BASE+'/state/'+'a'*24).status_code,404)
  self.assertEqual(self.s.get(BASE+'/media/'+'a'*24+'/voice/audio').status_code,404)
  self.assertEqual(self.s.get('http://127.0.0.1:5195/worker.py').status_code,404)
 def test_saved_graph_validation_and_reference(self):
  r=self.s.post(BASE+'/validate',json=test_contracts.GraphContracts().graph(),headers={'Origin':ORIGIN});self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['valid'])
  r=self.s.get(BASE+'/reference/esd%3A0015%3Aneutral');self.assertEqual(r.status_code,200);self.assertEqual(r.content[:4],b'RIFF')
  self.assertEqual(self.s.get('http://127.0.0.1:5195/reference/%2E%2E%2Fconfig.toml').status_code,404)
 def test_cancel_own_worker(self):
  r=self.s.post(BASE+'/run',json=test_contracts.GraphContracts().graph(),headers={'Origin':ORIGIN});self.assertEqual(r.status_code,202,r.text);ident=r.json()['id']
  other=requests.Session();other.get(BASE+'/session');self.assertEqual(other.get(BASE+'/state/'+ident).status_code,404)
  r=self.s.post(BASE+'/cancel',json={'id':ident},headers={'Origin':ORIGIN});self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['status'],'cancelled')
  for _ in range(30):
   r=self.s.get(BASE+'/state/'+ident)
   if r.json()['status']=='cancelled':break
   time.sleep(.1)
  self.assertEqual(r.json()['status'],'cancelled')
if __name__=='__main__':unittest.main(verbosity=2)

class FullControlHttp(unittest.TestCase):
 def setUp(self):self.s=requests.Session();self.s.get(BASE+'/session')
 def test_original_catalog_and_defaults(self):
  d=self.s.get(BASE+'/session').json();self.assertEqual(len(d['catalog']['presets']),100);self.assertTrue(any(p['id'].startswith('esd-original:') and p['transcript'] for p in d['catalog']['presets']))
  g=test_contracts.GraphContracts().graph();g['nodes'][1]['config']['steps']=17
  r=self.s.post(BASE+'/defaults',json=g,headers={'Origin':ORIGIN});self.assertEqual(r.status_code,200);self.assertEqual(self.s.get(BASE+'/session').json()['defaults'],g)
 def test_invalid_upload_and_foreign_reference(self):
  r=self.s.post(BASE+'/upload',json={'audio':'not base64'},headers={'Origin':ORIGIN});self.assertEqual(r.status_code,400)
  g=test_contracts.GraphContracts().graph();g['nodes'][1]['config'].update(reference='upload:foreign',reference_text='A reference.')
  self.assertEqual(self.s.post(BASE+'/validate',json=g,headers={'Origin':ORIGIN}).status_code,400)
