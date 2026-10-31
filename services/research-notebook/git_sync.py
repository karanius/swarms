"""Debounced, path-scoped Git persistence for native notebook saves."""
from pathlib import Path
import json,subprocess,threading,datetime
class NotebookGitSync:
 def __init__(self,repo,status_file,delay=5):
  self.repo=Path(repo).resolve();self.status_file=Path(status_file);self.delay=delay
  self.pending=set();self.timer=None;self.lock=threading.RLock();self.publish_lock=threading.Lock()
 def status(self,state,message):
  self.status_file.parent.mkdir(parents=True,exist_ok=True)
  value={'state':state,'message':message,'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  temporary=self.status_file.with_suffix('.tmp');temporary.write_text(json.dumps(value)+'\n');temporary.replace(self.status_file)
 def saved(self,model,os_path,contents_manager=None,**kwargs):
  if model.get('type')!='notebook':return
  file=Path(os_path).resolve();root=(self.repo/'knowledge/research/notebooks').resolve()
  if not file.is_relative_to(root) or file.suffix!='.ipynb' or '.ipynb_checkpoints' in file.parts:return
  with self.lock:
   self.pending.add(file.relative_to(self.repo).as_posix())
   if self.timer:self.timer.cancel()
   self.status('queued','Notebook saved to disk; GitHub sync queued.')
   self.timer=threading.Timer(self.delay,self.publish);self.timer.daemon=True;self.timer.start()
 def git(self,*args):return subprocess.run(['git',*args],cwd=self.repo,check=True,timeout=60,capture_output=True,text=True).stdout
 def publish(self):
  with self.publish_lock:
   with self.lock:
    paths=sorted(self.pending);self.pending.clear()
   if not paths:return
   try:
    self.status('pushing','Pushing saved notebooks.')
    self.git('add','--',*paths)
    if self.git('diff','--cached','--numstat','--',*paths).strip():self.git('commit','--only','-m','Save research notebooks','--',*paths)
    self.git('push','origin','HEAD')
    self.status('synced','Saved notebooks pushed to GitHub.')
   except (subprocess.SubprocessError,OSError):
    with self.lock:self.pending.update(paths)
    self.status('error','Notebook is on disk. GitHub sync failed; a later save retries it.')
