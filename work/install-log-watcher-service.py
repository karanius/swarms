from pathlib import Path
import plistlib
repo=Path('/Users/x/projects/swarms')
plist=Path.home()/'Library/LaunchAgents/local.swarms.log-pipeline.plist'
plist.parent.mkdir(parents=True,exist_ok=True)
data={'Label':'local.swarms.log-pipeline','ProgramArguments':[str(repo/'services/swarm-runtime-venv/bin/python'),'-m','uvicorn','services.log_pipeline:app','--host','127.0.0.1','--port','52418'],'WorkingDirectory':str(repo),'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':5,'StandardOutPath':str(repo/'services/langfuse/pipeline-runtime/service.log'),'StandardErrorPath':str(repo/'services/langfuse/pipeline-runtime/service-error.log')}
plist.write_bytes(plistlib.dumps(data))
