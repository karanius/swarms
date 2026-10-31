"""Coordinator CLI for recorded turns through the same service used by Jupyter."""
import argparse,json,time,urllib.request
from pathlib import Path
BASE=Path(__file__).resolve().parent
# Calls go through the browser-facing local boundary; no credentials enter prompts.
def request(path,data=None):
 req=urllib.request.Request('http://127.0.0.1:5188/paper6-agent-api'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)
def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',default='interview');p.add_argument('--message-file',type=Path);p.add_argument('--wait',action='store_true');args=p.parse_args()
 if args.message_file:request('/turn',{'text':args.message_file.read_text(),'mode':args.mode})
 if args.wait:
  deadline=time.monotonic()+600
  while True:
   state=request('/state')
   if not state['running']:
    print(json.dumps({'run':state['run'],'error':state['error'],'lastMessage':state['conversation'][-1] if state['conversation'] else None},indent=2));return
   if time.monotonic()>deadline:raise TimeoutError('Assistant turn remains active; inspect Jupyter activity')
   time.sleep(2)
 else:print(json.dumps(request('/state'),indent=2))
if __name__=='__main__':main()
