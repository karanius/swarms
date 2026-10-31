"""Execute workspace notebook cells under a separate deny-default macOS policy."""
from pathlib import Path
import json,os,signal,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[2]
PYTHON=ROOT/'services/research-notebook/.venv/bin/python'
def profile(workspace,temp):
 # Python may read its standard library and installed dependencies, not user stores.
 uv=PYTHON.resolve().parents[1]
 paths=[Path(workspace).resolve(),Path(temp).resolve(),ROOT/'services/research-notebook/.venv',uv,Path('/System'),Path('/usr'),Path('/bin'),Path('/sbin'),Path('/Library/Apple'),Path('/Library/Frameworks'),Path('/opt/homebrew/Cellar'),Path('/opt/homebrew/lib'),Path('/private/etc'),Path('/private/var/db/dyld')]
 quote=lambda p:json.dumps(str(p))
 return '\n'.join(['(version 1)','(deny default)','(allow process-exec)','(allow process-info-setcontrol (target self))','(allow sysctl-read)','(allow mach-lookup)','(allow file-read-metadata)','(allow file-read* (literal "/") (subpath "/dev"))','(allow file-write* (literal "/dev/dtracehelper"))',*[f'(allow file-read* (subpath {quote(p)}))' for p in paths],f'(allow file-read* (literal "/dev/null") (literal "/dev/urandom") (literal "/dev/random"))',f'(allow file-write* (subpath {quote(Path(workspace).resolve()/'artifacts')}) (subpath {quote(Path(temp).resolve())}) (literal "/dev/null"))'])
def execute(workspace,source,destination,timeout=60,cancel_event=None):
 workspace=Path(workspace).resolve();source=Path(source).resolve();destination=Path(destination).resolve()
 if not source.is_relative_to(workspace/'artifacts') or not destination.is_relative_to(workspace/'artifacts'):raise ValueError('Notebook source/output must stay within artifact workspace')
 if source==destination:raise ValueError('Use a separate executed output file')
 notebook=json.loads(source.read_text())
 if notebook.get('nbformat')!=4 or len(notebook.get('cells',[]))>60:raise ValueError('Use a v4 notebook with at most60 cells')
 if any(len(''.join(c.get('source',[])))>100000 for c in notebook['cells']):raise ValueError('Notebook cell exceeds code budget')
 if not Path('/usr/bin/sandbox-exec').exists():raise RuntimeError('Enforced execution isolation unavailable; execution is disabled')
 with tempfile.TemporaryDirectory(prefix='paper6-experiment-') as temp:
  script=Path(temp)/'execute.py';script.write_text('''import json,sys,os,resource
resource.setrlimit(resource.RLIMIT_CPU,(60,65))
resource.setrlimit(resource.RLIMIT_FSIZE,(20*1024*1024,20*1024*1024))

os.chdir(sys.argv[3])
class LimitedText:
 def __init__(self,target):self.target=target;self.count=0
 def write(self,text):
  self.count+=len(text)
  if self.count>1000000:raise RuntimeError("Cell text output exceeds1MB budget")
  return self.target.write(text)
 def flush(self):return self.target.flush()
 def __getattr__(self,key):return getattr(self.target,key)
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
import nbformat
n=nbformat.read(sys.argv[1],4);shell=InteractiveShell.instance();counter=0
for c in n.cells:
 if c.cell_type!='code':continue
 counter+=1
 with capture_output() as cap:
  saved_out,saved_err=sys.stdout,sys.stderr;sys.stdout=LimitedText(saved_out);sys.stderr=LimitedText(saved_err)
  try:result=shell.run_cell(c.source,store_history=False)
  finally:sys.stdout,sys.stderr=saved_out,saved_err
 c.execution_count=counter;c.outputs=[]
 if cap.stdout:c.outputs.append(nbformat.v4.new_output('stream',name='stdout',text=cap.stdout))
 if cap.stderr:c.outputs.append(nbformat.v4.new_output('stream',name='stderr',text=cap.stderr))
 for output in cap.outputs:
  if len(json.dumps(output.data))>8000000:raise RuntimeError('Rich output exceeds8MB budget')
  c.outputs.append(nbformat.v4.new_output('display_data',data=output.data,metadata=output.metadata))
 if result.error_before_exec or result.error_in_exec:
  err=result.error_before_exec or result.error_in_exec;c.outputs.append(nbformat.v4.new_output('error',ename=type(err).__name__,evalue=str(err),traceback=[]));nbformat.write(n,sys.argv[2]);raise SystemExit(2)
nbformat.write(n,sys.argv[2])
''')
  policy=Path(temp)/'policy.sb';policy.write_text(profile(workspace,temp));env={'PATH':'/usr/bin:/bin:/opt/homebrew/bin','HOME':temp,'TMPDIR':temp,'MPLCONFIGDIR':temp,'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1'}
  started=time.monotonic()
  with (Path(temp)/'worker.stdout').open('w+b') as stdout_file,(Path(temp)/'worker.stderr').open('w+b') as stderr_file:
   p=subprocess.Popen(['/usr/bin/sandbox-exec','-f',str(policy),str(PYTHON),str(script),str(source),str(destination),str(workspace)],cwd=workspace,env=env,stdout=stdout_file,stderr=stderr_file,start_new_session=True)
   deadline=time.monotonic()+min(120,max(1,timeout));reason=None
   while p.poll() is None:
    rss=0
    try:rss=int(subprocess.check_output(['/bin/ps','-o','rss=','-p',str(p.pid)],text=True).strip() or 0)
    except (ValueError,subprocess.CalledProcessError):pass
    reason='memory-budget' if rss>512*1024 else 'canceled' if cancel_event is not None and cancel_event.is_set() else 'timeout' if time.monotonic()>=deadline else None
    if reason:
     os.killpg(p.pid,signal.SIGKILL);p.wait();break
    try:p.wait(timeout=min(.2,max(.01,deadline-time.monotonic())))
    except subprocess.TimeoutExpired:continue
   def tail(f,limit):
    f.flush();f.seek(0,os.SEEK_END);length=f.tell();f.seek(max(0,length-limit));return f.read(limit).decode('utf-8',errors='replace')
   return {'status':reason or ('passed' if p.returncode==0 else 'failed'),'returncode':p.returncode,'elapsedSeconds':round(time.monotonic()-started,3),'stdout':tail(stdout_file,16000),'stderr':tail(stderr_file,8000),'outputWritten':destination.exists(),'network':'denied by process policy','filesystem':'writes restricted to this scratch artifact area and private temporary directory','processes':'child creation and signaling other processes denied','resources':'60 CPU seconds;20MB per file/log;512MB monitored RSS (not a hard allocation bound)'}
