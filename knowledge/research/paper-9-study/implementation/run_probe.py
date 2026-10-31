"""Explicitly bounded public-document/local-model implementation probe, not market research."""
from pathlib import Path
import json,uuid,datetime
from engine import Engine
D=Path(__file__).resolve().parents[1]
config={'max_attempts_per_stage':4,'allowed_hosts':['support.google.com'],'request_timeout':20,'max_source_bytes':8000000,'max_text_chars':24000,'max_sources':2,'model':'llama3.2:3b','model_timeout':60,'time_cap_seconds':150,'reviewer':'coordinator-reviewer'}
brief={'question':'What restrictions do the official YouTube documents describe for original versus repetitive educational content and synthetic-media disclosure?','audience_job':'Implementation probe: inspect source-policy evidence for a hypothetical educational channel; not a validated audience need','language':'English','geography':'No market geography chosen; official policy pages only','time_window':'Current public-document retrieval snapshot','decision_owner':'coordinator-probe-owner','allowed_source_classes':['official-public-document']}
sources=[{'url':'https://support.google.com/youtube/answer/1311392?hl=en','reason':'Official channel monetization policy; may challenge mass-production assumptions'}, {'url':'https://support.google.com/youtube/answer/14328491?hl=en','reason':'Official synthetic-media disclosure guidance; complementary policy scope'}]
root=D/'.runtime'/('probe-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
e=Engine(root,config)
print('Running bounded probe: two public official pages and one existing local model; no publishing or account changes',flush=True)
r=e.investigate(brief,sources);r['store']=str(root);r['probe_not_market_validation']=True
out=D/'implementation-probe.json';out.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2),flush=True)
