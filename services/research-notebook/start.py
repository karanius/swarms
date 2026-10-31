"""Authenticated local Jupyter runtime for embedded Research notebooks."""
from pathlib import Path
import os,secrets,sys
from traitlets.config import Config
from jupyter_server.serverapp import ServerApp
base=Path(__file__).resolve().parent
runtime=base/'.runtime';runtime.mkdir(exist_ok=True,mode=0o700)
token_file=runtime/'token'
if not token_file.exists():
 fd=os.open(token_file,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:f.write(secrets.token_hex(32))
os.chmod(token_file,0o600)
root=base.parents[1]/'knowledge/research/notebooks';root.mkdir(parents=True,exist_ok=True)
c=Config()
c.ServerApp.ip='127.0.0.1';c.ServerApp.port=5191;c.ServerApp.port_retries=0
c.ServerApp.open_browser=False;c.ServerApp.root_dir=str(root)
c.ServerApp.base_url='/research-jupyter/'
c.ServerApp.allow_origin='http://127.0.0.1:5188'
c.ServerApp.allow_remote_access=False;c.ServerApp.terminals_enabled=False
c.ServerApp.disable_check_xsrf=False
c.IdentityProvider.token=token_file.read_text().strip()
c.ServerApp.log_level='WARN'
c.MappingKernelManager.cull_idle_timeout=3600
c.MappingKernelManager.cull_interval=300
# A dedicated venv kernel, rather than the host's default Python.
c.KernelSpecManager.ensure_native_kernel=False
spec=runtime/'kernels/research-python';spec.mkdir(parents=True,exist_ok=True)
import json
(spec/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Research Python','language':'python'}))
os.environ['JUPYTER_PATH']=str(runtime)
c.ServerApp.kernel_spec_manager_class='jupyter_client.kernelspec.KernelSpecManager'
c.KernelSpecManager.allowed_kernelspecs={'research-python'}
c.ServerApp.jpserver_extensions={'notebook':True,'jupyterlab':True}
c.ServerApp.default_url='/tree'
from git_sync import NotebookGitSync
sync=NotebookGitSync(base.parents[1],runtime/'git-sync.json')
def save_notebook(model,os_path,contents_manager=None,**kwargs):
 sync.saved(model,os_path,contents_manager,**kwargs)
c.FileContentsManager.post_save_hook=save_notebook
ServerApp.launch_instance(config=c)
