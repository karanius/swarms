"""Coordinator-authored conformance fixtures and withheld acceptance manifest.
No generator or experimental outputs are read while constructing this suite.
"""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];STUDY=ROOT/'knowledge/research/paper-6-study';WORK=STUDY/'assistant-workspace'
def base():return {'nodes':[{'id':'i','type':'ChatInput'},{'id':'a','type':'Agent'},{'id':'o','type':'ChatOutput'}],'edges':[{'id':'e1','source':'i','output':'message','target':'a','input':'input_value'},{'id':'e2','source':'a','output':'response','target':'o','input':'input_value'}],'bindings':[{'id':'model-a','node':'a','field':'model','kind':'LanguageModel','state':'attested','tier':'synthetic-assumption'}],'node_type_assertions':[],'intent':{'id':'intent','route':'through_agent','required_agent':'a','route_assertions':[],'capabilities':[],'certify_active_ports':False,'selected_provider':None},'revision':None}
cases=[];expected={}
def add(family,label,c,action,blockers=(),patch=()):
 cid=f'C{len(cases)+1:02d}';cases.append({'case_id':cid,'family':family,'description':label,**c});expected[cid]={'action':action,'requiredBlockerKinds':sorted(blockers),'allowedPatchKinds':list(patch),'runtimeMustRemainUnknown':True}
c=base();c['bindings']=[];add('F1','Required model declaration absent',c,'ASK',['required_model'])
add('F1','Model interface attested as an authored assumption',base(),'SPEC_GROUNDED')
c=base();c['revision']={'op':'revoke_model','node':'a','authorized':True};add('F1','Model evidence revoked by authorized revision',c,'ASK',['required_model'],['revoke_model'])
c=base();c['edges']=[];c['nodes']=[{'id':'o','type':'ChatOutput'}];c['bindings']=[];c['intent'].update(route='any',required_agent=None);add('F2','Required output input has no incoming witness',c,'ASK',['required_input'])
c=base();c['nodes']=[n for n in c['nodes'] if n['id']!='a'];c['edges']=[{'id':'direct','source':'i','output':'message','target':'o','input':'input_value'}];c['bindings']=[];c['intent'].update(route='direct',required_agent=None);add('F2','Annotation-compatible direct route',c,'SPEC_GROUNDED')
c=base();c['edges'].append({'id':'bad','source':'i','output':'message','target':'a','input':'model'});add('F2','Message output conflicts with LanguageModel input',c,'ASK',['edge_type_conflict'])
for cap in ['vector_retrieval','database_write','email_transmission']:
 c=base();c['intent']['capabilities']=[cap];add('F3','Capability absent from the scoped alphabet: '+cap,c,'REJECT_SCOPE',['unsupported_capability'])
c=base();c['node_type_assertions']=[{'node':'a','type':'Agent'},{'node':'a','type':'ChatInput'}];add('F4','Conflicting type assertions for one identity',c,'ASK',['node_type_conflict'])
c=base();c['bindings'].append({**c['bindings'][0],'state':'revoked'});add('F4','Model evidence both attested and revoked',c,'ASK',['model_conflict'])
c=base();c['intent']['route_assertions']=['through_agent','forbid_agent'];add('F4','Intent both requires and forbids Agent route',c,'ASK',['intent_conflict'])
c=base();c['bindings'][0]['node']='ghost';add('F5','Model evidence references an absent node',c,'ASK',['orphan_binding','required_model'])
c=base();c['revision']={'op':'rename_node','old':'a','new':'renamed','authorized':True};add('F5','Authorized identity-preserving rename',c,'REVISE',patch=['rename_node'])
c=base();c['nodes'].append({'id':'a2','type':'Agent'});c['bindings'].append({**c['bindings'][0],'id':'model-a2','node':'a2'});c['intent']['required_agent']=None;add('F5','Through-Agent identity not selected among alternatives',c,'ASK',['ambiguous_identity'])
add('F6','Output compatibility supported by return annotation only',base(),'SPEC_GROUNDED')
c=base();c['intent']['certify_active_ports']=True;add('F6','Request active-port certification from static metadata',c,'REJECT_SCOPE',['runtime_certification'])
c=base();c['intent']['selected_provider']={'node':'a','name':'synthetic-provider'};add('F6','Provider-specific requirements have no supporting metadata',c,'ASK',['provider_requirements_unknown'])
c=base();c['edges']=[{'id':'direct','source':'i','output':'message','target':'o','input':'input_value'}];add('F7','Direct route violates explicit through-Agent intent',c,'ASK',['intent_route'])
c=base();c['edges']=[{'id':'direct','source':'i','output':'message','target':'o','input':'input_value'}];c['revision']={'op':'route_through_agent','node':'a','authorized':True};add('F7','Explicit unique authorization to insert existing Agent in route',c,'REVISE',patch=['route_through_agent'])
c=base();c['revision']={'op':'remove_node','node':'a','authorized':True};add('F7','Removal request conflicts with retained mandatory intent',c,'ASK',['revision_intent_conflict'])
add('F8','Statically grounded control under assumption-tier model witness',base(),'SPEC_GROUNDED')
c=base();c['bindings']=[];c['intent']['capabilities']=['vector_retrieval'];add('F8','Unsupported capability and missing model both retained',c,'REJECT_SCOPE',['unsupported_capability','required_model'])
c=base();c['bindings'][0]['node']='wrong';add('F8','Changed evidence target invalidates previous model grounding',c,'ASK',['orphan_binding','required_model'])
assert len(cases)==24
input_data={'schemaVersion':1,'authorship':'Coordinator-authored conformance cases following jointly debated blueprint; not held-out real tasks','catalogSha256':hashlib.sha256((STUDY/'native-starter-catalog.json').read_bytes()).hexdigest(),'cases':cases}
(STUDY/'assistant-reference-oracle.json').write_text(json.dumps({'scope':'Internal authored acceptance manifest, withheld from implementation agent until source freeze','expected':expected},indent=2))
(WORK/'artifacts/inputs').mkdir(exist_ok=True);(WORK/'artifacts/inputs/cases-v1.json').write_text(json.dumps(input_data,indent=2));print('Frozen24 coordinator-authored states; expected decisions remain outside agent workspace.')
