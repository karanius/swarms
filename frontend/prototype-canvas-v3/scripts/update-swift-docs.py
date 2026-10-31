from pathlib import Path
import json,html,hashlib
base=Path(__file__).resolve().parents[3]
docs=base/'knowledge/instance-machine'
files=['domain-model.md','contracts.md','canonical-specification.md','compiler-lifecycle.md','proof-milestone.md','strategy.md']
record={
 'schemaVersion':1,'id':'swift-agent','version':'0.3.0','name':'Swift','kind':'agent-template','layer':'Components','status':'draft',
 'resources':{'executor':{'repository':'https://github.com/openai/codex','configurationRef':None,'status':'planned'},'model':{'providerRef':'api-proxy','provider':'OpenAI Compatible','name':'gpt-6.1-sol','configurationRef':'langflow:model-provider/OpenAI Compatible'},'skills':[]},
 'assembly':{'scriptRef':'frontend/prototype-canvas-v3/scripts/assemble-swift.mjs','status':'implemented'},'deployment':{'launcherRef':'frontend/prototype-canvas-v3/scripts/deploy-swift.mjs','status':'implemented'},
 'architecture':[
 {'piece':'Instance generator','type':'Agent','github':'https://github.com/openai/codex','status':'planned','role':'Propose Instance JSON'},
 {'piece':'Library tools','type':'Tool interface','status':'planned','role':'Find items and resolve definitions','tools':['List layers','Search items','Inspect definitions','Inspect contracts','Resolve dependencies','Find compatible items','Retrieve assembly recipes','Check available versions']},
 {'piece':'Ajv','type':'JSON Schema validator','github':'https://github.com/ajv-validator/ajv','status':'planned','role':'Validate structure against our schemas'},
 {'piece':'Harness²','type':'Optimization framework','github':'https://github.com/google-research/harness2','status':'planned','role':'Improve the generator harness'}],
 'documents':[{'path':'knowledge/instance-machine/'+f,'title':f.removesuffix('.md').replace('-',' ').title(),'href':'/swift-agent/documents/'+hashlib.sha256((docs/f).read_bytes()).hexdigest()[:16]+'-'+f,'sha256':hashlib.sha256((docs/f).read_bytes()).hexdigest()} for f in files]
}
(base/'frontend/prototype-canvas-v3/components/swift-definition.json').write_text(json.dumps(record,indent=2)+'\n')
public=base/'frontend/public/swift-agent'
(public/'documents').mkdir(parents=True,exist_ok=True)
for document in record['documents']:
 (public/'documents'/Path(document['href']).name).write_bytes((base/document['path']).read_bytes())
(public/'definition.json').write_text(json.dumps(record,indent=2)+'\n')
rows=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [r['piece'],r['type'],r['role'],r.get('github','Our integration'),r['status'],', '.join(r.get('tools',[]))])+'</tr>' for r in record['architecture'])
sections=''.join('<details><summary>'+html.escape(d['title'])+'</summary><pre>'+html.escape((base/d['path']).read_text())+'</pre></details>' for d in record['documents'])
(public/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Swift · Template Documentation</title><style>body{margin:0;background:#111419;color:#e0e5ed;font:16px/1.6 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:40px 24px}h1{font-size:36px;margin-bottom:8px}a{color:#9fc9d5}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #414b5b;vertical-align:top}.table{overflow:auto}details{border-bottom:1px solid #414b5b;padding:16px 0}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.7 system-ui,sans-serif}a:focus-visible,summary:focus-visible{outline:2px solid #8edbce;outline-offset:4px}</style><main><a href="/prototype-canvas-v3/">Back to V3</a><h1>Swift</h1><p>Template version 0.3.0 · JSON references only</p><p>Swift is a JSON template that references its resources and versioned design documents. The canvas displays that template. A separate assembly script must resolve the references into an instance, and deployment must start it. The separate assembly script resolves native Langflow components; deployment creates an independent backend flow. Chat uses Langflow’s original chat controller. The generator, library tools, Ajv and Harness² integrations remain planned.</p><div class="table"><table><thead><tr><th>Piece</th><th>Type</th><th>Job</th><th>GitHub</th><th>Status</th><th>Tools</th></tr></thead><tbody>'''+rows+'''</tbody></table></div><p><a href="definition.json">Download the Swift JSON template</a></p><h2>Design documents</h2>'''+sections+'</main></html>')
