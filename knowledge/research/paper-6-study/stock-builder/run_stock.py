"""Use the existing unmodified native headless assistant API in a private backend.

No prompt/toolkit substitutions; caller instruction contains no graph recipe.
"""
import json,urllib.request,hashlib,time,os
from pathlib import Path
BASE=Path(__file__).resolve().parent
SOURCE=Path('/Users/x/projects/langflow/src/backend/base/langflow/agentic/flows/flow_builder_assistant.py')
API='http://127.0.0.1:7861/api/v1'
def call(path,data=None,token=None,timeout=30):
 headers={'Content-Type':'application/json'}
 if token:headers['Authorization']='Bearer '+token
 req=urllib.request.Request(API+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
 return urllib.request.urlopen(req,timeout=timeout)
def main():
 stamp=str(time.time_ns());run=BASE/'runs'/stamp;run.mkdir(parents=True)
 with call('/auto_login') as r:auth=json.load(r)
 token=auth.get('access_token');assert token,'Private stock backend did not issue local auth'
 instruction=(BASE/'request.txt').read_text();sourcehash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
 payload={'instruction':instruction,'provider':'OpenAI','model_name':'gpt-6.1-sol'}
 (run/'request.json').write_text(json.dumps(payload,indent=2));(run/'source-before.json').write_text(json.dumps({'path':str(SOURCE),'sha256':sourcehash,'prompt':'Unmodified FLOW_BUILDER_PROMPT from stock factory','toolkit':'Unmodified build_toolkit from stock factory','configuration':'Private localhost backend/database; normal model provider configuration via existing local API Proxy','entrypoint':'POST /api/v1/agentic/assist/run native headless pipeline'},indent=2))
 events=[]
 try:
  with call('/agentic/assist/run',payload,token,timeout=600) as response:
   with (run/'events.jsonl').open('w') as out:
    for raw in response:
     text=raw.decode().strip()
     if text.startswith('data: '):
      event=json.loads(text[6:]);events.append(event);out.write(json.dumps(event)+'\n');out.flush()
  complete=next((e for e in reversed(events) if e.get('event',e.get('type')) in ('complete','error')),None)
  (run/'terminal.json').write_text(json.dumps(complete,indent=2))
  if complete:
   flowid=complete.get('data',{}).get('flow_id') or complete.get('flow_id') or complete.get('result',{}).get('flow_id')
   if flowid:
    with call('/flows/'+flowid,token=token) as r:flow=json.load(r)
    (run/'flow.json').write_text(json.dumps(flow,indent=2))
  after=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert after==sourcehash,'Stock factory source changed'
  record={'run':str(run.relative_to(BASE)),'events':len(events),'terminal':complete,'stockSourceUnchanged':True,'sourceSha256':sourcehash}
  (run/'summary.json').write_text(json.dumps(record,indent=2));(BASE/'latest.json').write_text(json.dumps({'run':str(run.relative_to(BASE))},indent=2));print(json.dumps(record,indent=2))
 except Exception as e:
  (run/'failure.json').write_text(json.dumps({'error':str(e),'stockSourceUnchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==sourcehash},indent=2));raise
if __name__=='__main__':main()
