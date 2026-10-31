"""Isolated HTTP test with synthetic PCM; does not claim microphone proof."""
import base64,importlib.util,io,json,math,os,struct,tempfile,threading,unittest,urllib.request,urllib.error,wave,zipfile
from pathlib import Path
class StudioTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();os.environ['SPEAKER_STUDIO_DATA']=cls.temp.name
  spec=importlib.util.spec_from_file_location('studio_test',Path(__file__).with_name('server.py'));cls.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.m)
  cls.server=cls.m.ThreadingHTTPServer(('127.0.0.1',0),cls.m.Handler);threading.Thread(target=cls.server.serve_forever,daemon=True).start();cls.url='http://127.0.0.1:'+str(cls.server.server_port)
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.temp.cleanup()
 def req(self,path,data=None,origin='http://127.0.0.1:5197'):
  req=urllib.request.Request(self.url+path,data=json.dumps(data).encode() if data else None,headers={'Host':'127.0.0.1:5197','Origin':origin,'Content-Type':'application/json'})
  with urllib.request.urlopen(req) as r:return r.read()
 def test_record_review_resume_and_export(self):
  p=json.loads(self.req('/api/profile',{'name':'Synthetic test fixture'}));ident=p['id']
  with self.assertRaises(urllib.error.HTTPError):self.req('/api/finish',{'profile_id':ident})
  b=io.BytesIO()
  with wave.open(b,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b''.join(struct.pack('<h',int(4000*math.sin(i*2*math.pi*220/24000))) for i in range(30000)))
  for lesson in self.m.LESSONS:
   p=json.loads(self.req('/api/clip',{'profile_id':ident,'emotion':lesson['id'],'transcript':lesson['text'],'audio':base64.b64encode(b.getvalue()).decode(),'intensity':.6,'mime':'audio/wav','notes':'Synthetic fixture, not speech'}));take=p['clips'][-1]
   with self.assertRaises(urllib.error.HTTPError):self.req('/api/keep',{'profile_id':ident,'clip_id':take['id']})
   p=json.loads(self.req('/api/keep',{'profile_id':ident,'clip_id':take['id'],'words_checked':True,'performance_checked':True}))
   self.assertGreater(len(self.req(take['url'])),100)
  p=json.loads(self.req('/api/finish',{'profile_id':ident}));self.assertEqual(p['status'],'self_reviewed_library')
  restored=json.loads(self.req('/api/library'))['profiles'][0];self.assertEqual(len(restored['clips']),8)
  z=zipfile.ZipFile(io.BytesIO(self.req('/export/'+ident)));self.assertEqual(len(z.namelist()),18)
 def test_cross_origin_write_rejected(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.req('/api/profile',{'name':'No'},origin='https://example.com')
  self.assertEqual(e.exception.code,403)
if __name__=='__main__':unittest.main()
