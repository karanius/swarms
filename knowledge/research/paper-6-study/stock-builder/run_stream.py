"""Unchanged stock UI streaming endpoint for full native event observability."""
import sys,json,time,hashlib
from pathlib import Path
from run_stock import call,BASE
LROOT=Path('/Users/x/projects/langflow/src')
FILES=[*LROOT.glob('backend/base/langflow/agentic/flows/*.py'),*LROOT.glob('lfx/src/lfx/mcp/flow_builder_tools/*.py'),LROOT/'backend/base/langflow/agentic/services/assistant_service.py',LROOT/'backend/base/langflow/agentic/api/router.py']
def hashes():return {str(p.relative_to(LROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}
def main():
 run=BASE/'runs'/('stream-'+str(time.time_ns()));run.mkdir(parents=True);before=hashes()
 with call('/auto_login') as r:token=json.load(r)['access_token']
 with call('/flows/',{'name':'Paper6 stock observable generation','data':{'nodes':[],'edges':[]}},token) as r:flow=json.load(r)
 payload={'flow_id':flow['id'],'input_value':(BASE/'request.txt').read_text(),'provider':'OpenAI','model_name':'gpt-6.1-sol','history_limit':0}
 (run/'request.json').write_text(json.dumps(payload,indent=2));(run/'source-before.json').write_text(json.dumps(before,indent=2))
 events=[]
 with call('/agentic/assist/stream',payload,token,timeout=600) as response:
  with (run/'events.jsonl').open('w') as out:
   for raw in response:
    line=raw.decode().strip()
    if line.startswith('data: '):
     event=json.loads(line[6:]);events.append(event);out.write(json.dumps(event)+'\n');out.flush()
     if event.get('event')=='flow_update' and isinstance(event.get('flow'),dict):(run/'proposed-flow.json').write_text(json.dumps(event['flow'],indent=2))
 after=hashes();(run/'source-after.json').write_text(json.dumps(after,indent=2))
 summary={'run':str(run.relative_to(BASE)),'events':len(events),'sourceFilesUnchanged':before==after,'terminal':next((e for e in reversed(events) if e.get('event') in ('complete','error')),None),'mode':'Normal stock UI stream, proposals preserved, no active canvas'}
 (run/'summary.json').write_text(json.dumps(summary,indent=2));(BASE/'latest-stream.json').write_text(json.dumps({'run':str(run.relative_to(BASE))},indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
