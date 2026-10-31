import json,subprocess,tempfile,unittest
from pathlib import Path
from git_sync import NotebookGitSync
class NotebookSync(unittest.TestCase):
 def test_commits_only_saved_notebook_and_preserves_unrelated_staging(self):
  with tempfile.TemporaryDirectory() as directory:
   base=Path(directory);repo=base/'repo';repo.mkdir();remote=base/'remote.git'
   def git(*args):return subprocess.run(['git',*args],cwd=repo,check=True,capture_output=True,text=True).stdout.strip()
   git('init','-b','master');git('config','user.email','test@example.invalid');git('config','user.name','Notebook test');git('init','--bare',str(remote));git('remote','add','origin',str(remote))
   (repo/'unrelated.txt').write_text('original');git('add','unrelated.txt');git('commit','-m','Initial')
   (repo/'unrelated.txt').write_text('unrelated staged edit');git('add','unrelated.txt')
   note=repo/'knowledge/research/notebooks/Example.ipynb';note.parent.mkdir(parents=True);note.write_text('{}')
   sync=NotebookGitSync(repo,base/'status.json',delay=60);sync.saved({'type':'notebook'},str(note));sync.timer.cancel();sync.publish()
   self.assertEqual(json.loads((base/'status.json').read_text())['state'],'synced')
   self.assertEqual(git('show','HEAD:unrelated.txt'),'original');self.assertEqual(git('diff','--cached','--name-only'),'unrelated.txt')
   self.assertEqual(git('--git-dir',str(remote),'show','master:knowledge/research/notebooks/Example.ipynb'),'{}')
 def test_ignores_nonnotebook_and_outside_paths(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);sync=NotebookGitSync(root,root/'status.json');sync.saved({'type':'file'},root/'file.txt');sync.saved({'type':'notebook'},root/'outside.ipynb');self.assertEqual(sync.pending,set())
if __name__=='__main__':unittest.main()
