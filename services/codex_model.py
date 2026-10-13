"""Swarms LLM adapter using the supported Codex CLI and its existing sign-in."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

MODEL='gpt-6-luna'
EFFORT='low'
class CodexModel:
    model_name=MODEL
    def run(self,task=None,*args,**kwargs):
        prompt=str(task if task is not None else kwargs.get('prompt',''))
        executable=shutil.which('codex') or '/opt/homebrew/bin/codex'
        root=Path(__file__).parent/'langfuse'/'pipeline-runtime'/'codex-turns'
        root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            output=Path(directory)/'response.txt'
            command=[executable,'exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--cd',directory,'--model',MODEL,'-c',f'model_reasoning_effort="{EFFORT}"','--color','never','--output-last-message',str(output),'-']
            text='You are the text-generation backend for a Swarms workflow agent. Answer only from the supplied conversation. Do not use tools, inspect files, or execute commands. Follow the requested response schema.\n\n'+prompt
            result=subprocess.run(command,input=text,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
            if result.returncode!=0:
                raise RuntimeError(f'Codex {MODEL} invocation failed (exit {result.returncode}). Check Codex login status and model availability.')
            if not output.exists() or not output.read_text().strip():raise RuntimeError('Codex returned no final response.')
            return output.read_text().strip()

def studio_model_args():
    return {'llm':CodexModel(),'model_name':MODEL}
