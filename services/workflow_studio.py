from services.codex_model import studio_model_args,MODEL,EFFORT
import json,re,threading,uuid,time
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from swarms import Agent
from swarms.structs.sequential_workflow import SequentialWorkflow
from swarms.structs.context_utils import agent_answer
router=APIRouter(prefix='/studio')
jobs={}
class Request(BaseModel):
    objective:str=Field(min_length=1,max_length=4000)
    instructions:list[str]=Field(default_factory=list,max_length=3)
    max_attempts:int=Field(default=4,ge=1,le=8)
def parse_graph(text):
    text=re.sub(r'<think>.*?</think>','',text,flags=re.S)
    decoder=json.JSONDecoder();spec=None
    for match in re.finditer(r'\{',text):
        try:
            value,_=decoder.raw_decode(text[match.start():])
            if isinstance(value,dict) and 'steps' in value:spec=value;break
        except ValueError:pass
    if not spec:raise ValueError('The agents did not produce a workflow JSON object.')
    steps=spec.get('steps');links=spec.get('links')
    if not isinstance(steps,list) or not 1<=len(steps)<=15:raise ValueError('Expected 1–15 workflow steps.')
    for step in steps:
        if not isinstance(step,dict) or type(step.get('kind')) is not int or not 0<=step['kind']<=6 or not isinstance(step.get('label'),str) or not isinstance(step.get('instructions'),str):raise ValueError('Invalid node configuration.')
    if not isinstance(links,list):raise ValueError('links must be an array of [sourceIndex,targetIndex] pairs.')
    invalid=[link for link in links if not isinstance(link,list) or len(link)!=2 or any(type(i) is not int or not 0<=i<len(steps) for i in link) or link[0]==link[1]]
    if invalid:raise ValueError('Invalid links: '+json.dumps(invalid)+'. There are '+str(len(steps))+' steps: valid connection indexes are 0 through '+str(len(steps)-1)+'. These indexes are array positions, NOT kind values. Step index map: '+json.dumps({i:s['label'] for i,s in enumerate(steps)}))
    return {'title':str(spec.get('title','Generated workflow'))[:180],'nodes':[{'id':f'generated-{i}','type':'block','position':{'x':i*300,'y':180},'data':{'kind':s['kind'],'label':s['label'],'task':s['instructions'],'inputs':[],'outputs':[]}} for i,s in enumerate(steps)],'edges':[{'id':f'generated-edge-{i}','source':f'generated-{a}','target':f'generated-{b}','type':'smoothstep'} for i,(a,b) in enumerate(links)]}
def phase1_checks(graph):
    nodes=graph['nodes'];edges=graph['edges'];issues=[]
    if any(not n['data']['label'].strip() or not n['data']['task'].strip() for n in nodes):issues.append('Every step needs a nonempty name and task instructions.')
    if len(nodes)>1:
        adjacent={n['id']:set() for n in nodes}
        for e in edges:adjacent[e['source']].add(e['target']);adjacent[e['target']].add(e['source'])
        visited=set();pending=[nodes[0]['id']]
        while pending:
            node=pending.pop()
            if node in visited:continue
            visited.add(node);pending.extend(adjacent[node]-visited)
        if len(visited)!=len(nodes):issues.append('All nodes must be connected to the workflow.')
    return issues

def parse_review(text):
    decoder=json.JSONDecoder()
    for match in re.finditer(r'\{',text):
        try:
            value,_=decoder.raw_decode(text[match.start():])
            if type(value.get('approved')) is bool and isinstance(value.get('issues'),list) and all(isinstance(i,str) for i in value['issues']):return value
        except (ValueError,AttributeError):pass
    raise ValueError('Objective review must return approved:boolean and issues:string[].')

@router.post('/run')
def run(request:Request):
    if any(job['phase']=='running' for job in jobs.values()):raise HTTPException(409,'A workflow generation is already running.')
    key=str(uuid.uuid4());jobs[key]={'id':key,'phase':'running','events':[],'workflow':None,'error':None,'provider':'codex','model':MODEL,'reasoningEffort':EFFORT,'attempt':0,'maxAttempts':request.max_attempts,'checks':[],'completionCriteria':['Valid supported node types and connections','Nonempty instructions for every node','All nodes connected','Reviewer approves coverage of the objective']}
    def worker():
        started=time.monotonic()
        try:
            prompts=['Plan a workflow for the objective. Give concise steps and dependencies. Do not perform the task.', 'Build a workflow from the plan. Return JSON only.', 'Review the proposed workflow against the original objective. Correct it if necessary. Return the complete workflow JSON only.']
            schema='Allowed kinds: 0 Research agent, 1 Read documents tool, 2 Compare agent, 3 Write agent, 4 Parallel team, 5 Review agent, 6 Repeat. Schema: {"title":"name","steps":[{"kind":0,"label":"name","instructions":"task"}],"links":[[0,1]]}. Links refer to zero-based positions in steps, NEVER kind values. For N steps valid indexes are 0 through N-1. Example with 3 steps: links [[0,1],[1,2]]. Use only these real block types; do not claim the workflow has executed. Preserve the original objective.'
            agents=[]
            for stage,name in enumerate(['Planner','Builder','Reviewer']):
                class ObservedAgent(Agent):
                    def run(self,task=None,*args,**kwargs):
                        jobs[key]['events'].append({'id':str(uuid.uuid4()),'stage':self.stage,'round':jobs[key].get('attempt',1),'direction':'inputs','text':str(task)})
                        result=super().run(task,*args,**kwargs)
                        answer=agent_answer(self,fallback=result)
                        jobs[key]['events'].append({'id':str(uuid.uuid4()),'stage':self.stage,'round':jobs[key].get('attempt',1),'direction':'outputs','text':str(answer)})
                        return result
                agent=ObservedAgent(agent_name=name,system_prompt=prompts[stage]+'\n'+schema+'\nOriginal objective: '+request.objective+'\nUser instructions: '+(request.instructions[stage] if len(request.instructions)>stage else ''),**studio_model_args(),max_loops=1,max_tokens=1000,temperature=.1,output_type='final',verbose=False,telemetry=False,retry_attempts=1,llm_args={'timeout':120})
                agent.stage=stage;agents.append(agent)
            feedback='';last='';previous_failure=None;repeated=0
            for attempt in range(1,request.max_attempts+1):
                if time.monotonic()-started>480:
                    jobs[key].update(phase='blocked',error='Phase 1 time budget reached. No completed output was published.');return
                jobs[key]['attempt']=attempt
                if attempt==1:
                    SequentialWorkflow(name='Workflow producer',agents=agents,max_loops=1,output_type='dict').run(request.objective)
                    last=next(event['text'] for event in reversed(jobs[key]['events']) if event['stage']==2 and event['direction']=='outputs')
                else:
                    task='Repair the workflow using the exact failed completion checks. Original objective: '+request.objective+'\nChecks: '+feedback+'\nPrevious candidate: '+last
                    result=agents[1].run(task);candidate=str(agent_answer(agents[1],fallback=result))
                    result=agents[2].run('Review and correct this candidate. Return complete workflow JSON only.\n'+candidate)
                    last=str(agent_answer(agents[2],fallback=result))
                jobs[key]['events'].append({'id':str(uuid.uuid4()),'stage':3,'round':attempt,'direction':'inputs','text':last})
                try:
                    graph=parse_graph(last);issues=phase1_checks(graph)
                    if not issues:
                        result=agents[2].run('Completion audit only. Does this DESIGN cover every part of the original objective? Identify missing operations or capabilities; do not pretend the task executed. Return JSON only: {"approved":true,"issues":[]}. Set approved false if anything is missing. Original objective: '+request.objective+'\nWorkflow: '+json.dumps(graph))
                        review=parse_review(str(agent_answer(agents[2],fallback=result)))
                        if not review['approved'] or review['issues']:issues=review['issues'] or ['Reviewer did not approve objective coverage.']
                except ValueError as error:issues=[str(error)]
                check={'attempt':attempt,'passed':not issues,'issues':issues}
                jobs[key]['checks'].append(check)
                jobs[key]['events'].append({'id':str(uuid.uuid4()),'stage':3,'round':attempt,'direction':'outputs','text':json.dumps(check,indent=2)})
                if not issues:
                    graph['phase1Completion']={'passed':True,'attempts':attempt,'criteria':jobs[key]['completionCriteria']}
                    jobs[key].update(workflow=graph,phase='complete');return
                feedback=json.dumps(issues);repeated=repeated+1 if feedback==previous_failure else 1;previous_failure=feedback
                if repeated>=3:
                    jobs[key].update(phase='blocked',error='The same completion failure repeated three times. '+feedback);return
            jobs[key].update(phase='blocked',error='Attempt budget reached. Unresolved checks: '+feedback)
        except Exception as error:jobs[key].update(phase='error',error=str(error))
    threading.Thread(target=worker,daemon=True).start()
    return {'id':key}
@router.get('/jobs/{key}')
def status(key:str):
    if key not in jobs:raise HTTPException(404,'Generation unavailable. Generate again.')
    return jobs[key]

class ConfigureRequest(BaseModel):
    workflow:dict
    defaults:dict

@router.post('/configure')
def configure(request:ConfigureRequest):
    graph=request.workflow
    nodes=graph.get('nodes',[]);edges=graph.get('edges',[])
    if not nodes or len(nodes)>15 or any(type(n.get('data',{}).get('kind')) is not int or not 0<=n['data']['kind']<=6 for n in nodes):raise HTTPException(400,'Invalid Phase 1 graph')
    ids={n['id'] for n in nodes}
    if len(ids)!=len(nodes) or any(e.get('source') not in ids or e.get('target') not in ids for e in edges):raise HTTPException(400,'Invalid Phase 1 connections')
    key=str(uuid.uuid4());jobs[key]={'id':key,'phase':'running','events':[],'workflow':None,'error':None,'provider':'codex','model':MODEL,'reasoningEffort':EFFORT}
    def worker():
        try:
            from copy import deepcopy
            names=['research','read','compare','write','parallel','review','repeat']
            configured=deepcopy(graph);issues=[]
            jobs[key]['events'].append({'id':str(uuid.uuid4()),'stage':0,'direction':'inputs','text':json.dumps(graph,indent=2)})
            for node in configured['nodes']:
                data=node['data'];kind=data['kind'];name=names[kind]
                config=deepcopy(request.defaults.get(name,{}));config['task']=data.get('task','')
                if kind in (0,2,3,5):config.update(model_profile='codex',model_name=MODEL,reasoning_effort=EFFORT,max_tokens=1000)
                data[name]=config
                data['inputBindings']=[{'sourceNode':e['source'],'source':'output'} for e in edges if e['target']==node['id']]
                data['outputContract']={'type':'text' if kind in (0,2,3,5) else 'library-result','nodeType':name}
                data['permissions']={'mcp':False,'filesystem':False,'tools':[]}
                missing=[]
                if not data.get('task','').strip():missing.append('Task instructions are missing.')
                if kind==1 and not config.get('file_path'):missing.append('Select a file or bind a supported file provider.')
                if kind==4 and not config.get('members'):missing.append('Assign member agents to the parallel team.')
                if kind==6:missing.append('Choose and validate the repeat destination and stopping condition.')
                data['readiness']={'configured':True,'issues':missing}
                issues.extend({'nodeId':node['id'],'message':message} for message in missing)
            checks={'configuredNodes':len(nodes),'executionReady':False,'issues':issues,'blockers':['Generated graphs do not yet have an executable graph runtime.']}
            configured['readiness']=checks
            payload=json.dumps(configured,indent=2)
            jobs[key]['events'].append({'id':str(uuid.uuid4()),'stage':0,'direction':'outputs','text':payload})
            task='Review these configured nodes. Explain remaining missing settings and capability bindings. Do not claim execution readiness. Keep the review concise.\n'+payload
            jobs[key]['events'].append({'id':str(uuid.uuid4()),'stage':1,'direction':'inputs','text':task})
            agent=Agent(agent_name='Phase 2 readiness reviewer',system_prompt='Audit workflow configuration using the provided evidence. Never invent tools, grants, or execution results.',**studio_model_args(),max_loops=1,max_tokens=500,temperature=.1,output_type='final',verbose=False,telemetry=False,retry_attempts=1,llm_args={'timeout':120})
            result=agent.run(task);answer=str(agent_answer(agent,fallback=result))
            jobs[key]['events'].append({'id':str(uuid.uuid4()),'stage':1,'direction':'outputs','text':answer})
            configured['configurationReview']=answer
            jobs[key].update(workflow=configured,phase='complete')
        except Exception as error:jobs[key].update(phase='error',error=str(error))
    threading.Thread(target=worker,daemon=True).start()
    return {'id':key}

class BindRequest(BaseModel):
    workflow:dict
    file_path:str=''
    grant_file_read:bool=False

@router.post('/bind')
def bind(request:BindRequest):
    if not request.workflow.get('readiness'):raise HTTPException(400,'Apply Phase 2 first.')
    key=str(uuid.uuid4());jobs[key]={'id':key,'phase':'running','events':[],'workflow':None,'error':None,'provider':'codex','model':MODEL,'reasoningEffort':EFFORT}
    def worker():
        from copy import deepcopy
        from pathlib import Path
        try:
            graph=deepcopy(request.workflow);issues=[];checks=[]
            def event(stage,direction,value):jobs[key]['events'].append({'id':str(uuid.uuid4()),'stage':stage,'direction':direction,'text':json.dumps(value,indent=2) if not isinstance(value,str) else value})
            event(0,'inputs',graph)
            agent_kinds=(0,2,3,5)
            for node in graph['nodes']:
                data=node['data'];kind=data['kind'];missing=[]
                if kind in agent_kinds:data['capabilityBinding']={'implementation':'swarms.Agent','access':'Codex sign-in inference','model':MODEL,'reasoningEffort':EFFORT,'adapter':'services.codex_model.CodexModel','tools':[]}
                elif kind==1:
                    data['capabilityBinding']={'implementation':'app.read_only_text_file','path':request.file_path or data.get('read',{}).get('file_path',''),'readLimitBytes':4096,'granted':request.grant_file_read}
                    if not data['capabilityBinding']['path']:missing.append('Select an exact file for the file-reader tool.')
                    if not request.grant_file_read:missing.append('File read permission has not been granted.')
                elif kind==4:
                    members=[e['target'] for e in graph['edges'] if e['source']==node['id'] and any(n['id']==e['target'] and n['data']['kind'] in agent_kinds for n in graph['nodes'])]
                    data['parallel']['members']=members;data['capabilityBinding']={'implementation':'swarms.ConcurrentWorkflow','members':members}
                    if not members:missing.append('Parallel team has no connected agent members.')
                else:
                    data['capabilityBinding']={'implementation':'swarms.RoundRobinSwarm','resolved':False}
                    missing.append('Repeat destination and stopping condition need an explicit configuration.')
                if not data.get('task','').strip():missing.append('Task instructions are missing.')
                issues.extend({'nodeId':node['id'],'message':m} for m in missing)
            event(0,'outputs',graph);event(1,'inputs',{'bindings':[n['data'].get('capabilityBinding') for n in graph['nodes']]})
            if any(n['data']['kind'] in agent_kinds for n in graph['nodes']):
                try:
                    probe=Agent(agent_name='Phase 3 Codex capability check',system_prompt='Reply briefly.',**studio_model_args(),max_loops=1,max_tokens=8,temperature=0,output_type='final',verbose=False,telemetry=False,retry_attempts=1,llm_args={'timeout':30})
                    result=probe.run('Reply with OK.');reply=str(agent_answer(probe,fallback=result))
                    checks.append({'capability':'swarms.Agent → Codex','passed':bool(reply.strip()),'observedReply':reply,'scope':'One bounded inference probe; generated node tasks were not executed.'})
                except Exception as error:checks.append({'capability':'swarms.Agent → Codex','passed':False,'error':str(error)})
            for node in graph['nodes']:
                binding=node['data'].get('capabilityBinding',{})
                if node['data']['kind']!=1 or not binding.get('granted') or not binding.get('path'):continue
                try:
                    path=Path(binding['path']).expanduser()
                    if path.is_symlink() or path.suffix.lower() not in ('.txt','.md','.csv','.json'):raise ValueError('Only exact non-symlink text, Markdown, CSV or JSON files are supported by this binding.')
                    with path.open('rb') as file:sample=file.read(4096)
                    sample.decode('utf-8')
                    node['data']['read']['file_path']=str(path);node['data']['permissions']['filesystem']=True
                    checks.append({'nodeId':node['id'],'capability':'read-only file','passed':True,'bytesRead':len(sample),'path':str(path)})
                except Exception as error:
                    checks.append({'nodeId':node['id'],'capability':'read-only file','passed':False,'error':str(error)})
            event(1,'outputs',checks);event(2,'inputs',{'issues':issues,'checks':checks})
            graph['readiness']={'bindingChecked':True,'executionReady':False,'issues':issues,'checks':checks,'blockers':['The executable graph runtime is not implemented. Full workflow execution is Phase 4.']}
            event(2,'outputs',graph['readiness']);jobs[key].update(workflow=graph,phase='complete')
        except Exception as error:jobs[key].update(phase='error',error=str(error))
    threading.Thread(target=worker,daemon=True).start();return {'id':key}
