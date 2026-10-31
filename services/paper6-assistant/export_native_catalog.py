"""Pin a minimal trusted local native component alphabet, excluding field values."""
import hashlib,inspect,json,subprocess,typing
from pathlib import Path
from lfx.components.input_output import ChatInput,ChatOutput
from lfx.components.models_and_agents import AgentComponent
ROOT=Path(__file__).resolve().parents[2];rows=[]
for cls in [ChatInput,AgentComponent,ChatOutput]:
 instance=cls(_user_id='paper6-catalog');source=Path(inspect.getfile(cls));ports=[]
 for output in cls.outputs:
  annotation=typing.get_type_hints(getattr(cls,output.method)).get('return');ports.append({'name':output.name,'declaredTypes':output.types,'returnAnnotation':getattr(annotation,'__name__',str(annotation)),'activation':'unverified'})
 rows.append({'type':'Agent' if cls is AgentComponent else cls.__name__,'displayName':cls.display_name,'class':cls.__module__+'.'+cls.__name__,'sourceFile':str(source),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'inputs':[{'name':p.name,'required':bool(p.required),'types':getattr(p,'input_types',None) or [],'dynamic':bool(getattr(p,'dynamic',False)),'fieldClass':type(p).__name__} for p in instance._inputs.values()],'outputs':ports})
result={'scope':'Minimal three-type native alphabet, not the complete catalog','source':'local Langflow checkout; no component run','langflowCommit':subprocess.check_output(['git','-C','/Users/x/projects/langflow','rev-parse','HEAD'],text=True).strip(),'components':rows,'limits':['Metadata and return annotations do not establish active ports or behavior','No configuration values or credentials included','The local checkout may include changes beyond its HEAD; class source hashes are pinned']}
p=ROOT/'knowledge/research/paper-6-study/native-starter-catalog.json';p.write_text(json.dumps(result,indent=2));print('Pinned',len(rows),'native component types without field values')
