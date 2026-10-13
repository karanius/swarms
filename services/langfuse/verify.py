"""Verify local Langfuse ingestion and retrieval using a labeled infrastructure test."""
from pathlib import Path
import base64,json,uuid,time,urllib.request,urllib.error,urllib.parse
from datetime import datetime,timezone,timedelta
config=dict(line.split('=',1) for line in (Path(__file__).parent/'.env').read_text().splitlines() if '=' in line)
root='http://127.0.0.1:'+config['LANGFUSE_PORT']
auth=base64.b64encode((config['LANGFUSE_PUBLIC_KEY']+':'+config['LANGFUSE_SECRET_KEY']).encode()).decode()
def request(path,data=None):
    req=urllib.request.Request(root+path,data=None if data is None else json.dumps(data).encode(),headers={'Authorization':'Basic '+auth,'Content-Type':'application/json','x-langfuse-ingestion-version':'4'})
    with urllib.request.urlopen(req,timeout=15) as response:return json.load(response)
trace=uuid.uuid4().hex
stamp=datetime.now(timezone.utc).isoformat()
span=uuid.uuid4().hex[:16]
start=time.time_ns()
result=request('/api/public/otel/v1/traces',{'resourceSpans':[{'resource':{'attributes':[{'key':'service.name','value':{'stringValue':'swarms-canvas'}}]},'scopeSpans':[{'scope':{'name':'swarms-infrastructure-test'},'spans':[{'traceId':trace,'spanId':span,'name':'swarms-infrastructure-smoke-test','kind':1,'startTimeUnixNano':str(start),'endTimeUnixNano':str(start+1000000),'attributes':[{'key':'langfuse.trace.name','value':{'stringValue':'swarms-infrastructure-smoke-test'}},{'key':'langfuse.trace.metadata.synthetic','value':{'stringValue':'true'}}],'status':{'code':1}}]}]}]})
for attempt in range(30):
    try:
        query=urllib.parse.urlencode({'traceId':trace,'fromStartTime':(datetime.now(timezone.utc)-timedelta(minutes=5)).isoformat(),'toStartTime':(datetime.now(timezone.utc)+timedelta(minutes=1)).isoformat()})
        records=request('/api/public/v2/observations?'+query)
        found=next((r for r in records.get('data',[]) if r.get('traceId')==trace),{})
        if found:
            print(json.dumps({'health':request('/api/public/health'),'ingested':True,'retrieved':True,'traceId':trace,'traceName':found['name']}));break
    except urllib.error.HTTPError as error:
        if error.code!=404:raise
    time.sleep(1)
else:raise RuntimeError('Trace not retrievable after 30 seconds')
