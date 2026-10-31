import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from workspace import Workspace,sha
from sandbox_runner import execute
class ScopeTests(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.ws=Workspace(Path(self.temp.name)/'workspace')
 def tearDown(self):self.temp.cleanup()
 def test_paths_and_symlinks(self):
  for p in ['../escape','/tmp/escape','.hidden','notes/../../escape']:
   with self.assertRaises(ValueError):self.ws.safe(p)
  (self.ws.root/'artifacts/link').symlink_to('/tmp')
  with self.assertRaises(ValueError):self.ws.safe('link/escape')
 def test_artifact_compare_and_swap(self):
  r=self.ws.write_artifact('notes/a.md','a')
  with self.assertRaises(ValueError):self.ws.write_artifact('notes/a.md','b')
  n=self.ws.write_artifact('notes/a.md','b',r['revision']);self.assertEqual(self.ws.read_artifact('notes/a.md')['revision'],n['revision']);self.assertEqual(len(list((self.ws.root/'history').glob('*'))),1)
 def test_context_progression_and_unknown_resource(self):
  self.assertIn('error',self.ws.read_context('study_results'));self.ws.grant_context('study_results');self.assertIn('205',self.ws.read_context('study_results')['content'])
  with self.assertRaises(ValueError):self.ws.grant_context('/etc/passwd')
 def test_paper_edits_stay_in_draft_and_preserve_abstract(self):
  from workspace import PAPER
  original=sha(PAPER.read_bytes());section=self.ws.section(1);self.ws.write_section(1,section['markdown']+'\n\nProposed fixture note.',section['revision']);self.assertEqual(sha(PAPER.read_bytes()),original)
  with self.assertRaises(ValueError):self.ws.write_section(1,'## 1. Stale','old')
  with self.assertRaises(ValueError):self.ws.section(0)
 def test_real_execution_and_scope_denials(self):
  outside=Path(self.temp.name)/'outside-sensitive-fixture.txt';outside.write_text('fixture-only-private-data')
  cells=[{'cell_type':'code','metadata':{},'source':['print(6*7)\n',"from pathlib import Path\n","import socket\n","checks=[]\n",f"for name in [{str(outside)!r}]:\n"," try: Path(name).read_text();checks.append(False)\n"," except PermissionError: checks.append(True)\n","try: Path('../forbidden.txt').write_text('bad');checks.append(False)\n","except PermissionError: checks.append(True)\n","try: socket.create_connection(('127.0.0.1',8787),timeout=1);checks.append(False)\n","except OSError: checks.append(True)\n","assert all(checks),checks\n","print('Isolation denials verified',checks)"],'execution_count':None,'outputs':[]}]
  self.ws.write_artifact('check.ipynb',json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{},'cells':cells}));result=execute(self.ws.root,self.ws.safe('check.ipynb'),self.ws.safe('check.executed.ipynb'),20);self.assertEqual(result['status'],'passed',result);out=json.loads(self.ws.safe('check.executed.ipynb').read_text());self.assertIn('42',''.join(''.join(x.get('text',[])) if isinstance(x.get('text'),list) else x.get('text','') for x in out['cells'][0]['outputs']))
if __name__=='__main__':unittest.main()
