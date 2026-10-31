import asyncio,json,os,signal,tempfile,unittest
from pathlib import Path
from runtime import ResearchRuntime
from workspace import Workspace
from sandbox_runner import execute
class LifecycleTests(unittest.TestCase):
 def test_cancel_before_task_start_does_not_latch_busy(self):
  async def check():
   with tempfile.TemporaryDirectory() as t:
    r=ResearchRuntime(Workspace(Path(t)/'workspace'));await r.turn('fixture cancel before model','interview');s=await r.cancel();self.assertFalse(s['running']);self.assertEqual(s['run']['status'],'canceled')
  asyncio.run(check())
 def test_sandbox_denies_fork_and_signaling_parent(self):
  with tempfile.TemporaryDirectory() as t:
   w=Workspace(Path(t)/'workspace');source=f'''import os,signal\nchecks=[]\ntry:\n pid=os.fork()\n if pid==0:os._exit(0)\n os.waitpid(pid,0);checks.append(False)\nexcept PermissionError:checks.append(True)\ntry:os.kill({os.getpid()},signal.SIGCONT);checks.append(False)\nexcept PermissionError:checks.append(True)\nassert all(checks),checks\nprint('Fork and outside-process signal denied')'''
   n={'nbformat':4,'nbformat_minor':5,'metadata':{},'cells':[{'cell_type':'code','metadata':{},'source':source,'execution_count':None,'outputs':[]}]};w.write_artifact('scope.ipynb',json.dumps(n));result=execute(w.root,w.safe('scope.ipynb'),w.safe('scope.output.ipynb'),20);self.assertEqual(result['status'],'passed',result)
 def test_tool_executes_in_scratch_and_imports_only_artifacts(self):
  async def check():
   with tempfile.TemporaryDirectory() as t:
    w=Workspace(Path(t)/'workspace');r=ResearchRuntime(w)
    n={'nbformat':4,'nbformat_minor':5,'metadata':{},'cells':[{'cell_type':'code','metadata':{},'source':"from pathlib import Path\nPath('artifacts/result.json').write_text('{\"answer\":42}')\ntry: Path('../escape.txt').write_text('bad'); raise AssertionError('escaped')\nexcept PermissionError: pass\nprint(42)",'execution_count':None,'outputs':[]}]}
    w.write_artifact('fixture.ipynb',json.dumps(n));tool=next(x for x in r.tools() if x.name=='execute_notebook');result=json.loads(await tool.ainvoke({'path':'fixture.ipynb','timeout_seconds':20}));self.assertEqual(result['status'],'passed',result);self.assertIn('result.json',result['importedArtifacts']);self.assertEqual(json.loads(w.read_artifact('result.json')['content'])['answer'],42);self.assertFalse((w.root/'escape.txt').exists())
  asyncio.run(check())
 def test_notebook_timeout_terminates_busy_code(self):
  with tempfile.TemporaryDirectory() as t:
   w=Workspace(Path(t)/'workspace');n={'nbformat':4,'nbformat_minor':5,'metadata':{},'cells':[{'cell_type':'code','metadata':{},'source':'while True: pass','execution_count':None,'outputs':[]}]};w.write_artifact('loop.ipynb',json.dumps(n));result=execute(w.root,w.safe('loop.ipynb'),w.safe('loop.output.ipynb'),1);self.assertEqual(result['status'],'timeout')
if __name__=='__main__':unittest.main()
