"""Local, bounded Swarms demo with real agent events streamed to the canvas."""
import os
os.environ["SWARMS_TELEMETRY_ON"]="false"
import json
import re
from difflib import SequenceMatcher
import asyncio
import threading
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from swarms import Agent, RoundRobinSwarm
from services.langfuse.swarms_integration import agent_options, run_agent, tracer, flush

app = FastAPI()
job_lock = threading.Lock()
current_job = None

async def stream_job(job):
    cursor=0
    while True:
        with job_lock:
            pending=job['events'][cursor:]
            done=job['done']
        for event in pending:
            cursor+=1
            yield 'data: '+json.dumps(event)+'\n\n'
        if done: break
        if not pending: yield ': heartbeat\n\n'
        await asyncio.sleep(.15)

@app.post('/stop')
def stop():
    if current_job: current_job['stopped'].set()
    return {'stopped':True}

@app.post('/reset')
def reset():
    global current_job
    with job_lock:
        if current_job and not current_job['done']:
            raise HTTPException(409,'Stop the current run before restarting')
        current_job=None
    return {'ready':True}
MODEL = 'openai/mlx-community/Llama-3.2-3B-Instruct-4bit'
OBJECTIVE = '''Recommend a local inference deployment for our Swarm Canvas. Supplied facts: one Mac has 64GB RAM; EXO serves Llama 3.2 3B 4bit locally; a verified sample finished in 2.25 seconds with 289 generated tokens; its existing model cache is reused read-only. Option A uses this one Mac; Option B adds a second Mac, whose hardware, network performance and inference speed are unknown. Compare latency, complexity and evidence. Produce a recommendation, explain unknowns, and give three measurable validation checks. Do not invent benchmarks or browse. Each round must incorporate earlier feedback and improve the recommendation, not repeat it.'''
def is_repetition(previous, current):
    def normalize(text):
        return ' '.join(re.findall(r'[a-z0-9]+', text.lower()))
    before, after = normalize(previous), normalize(current)
    if not before or not after:
        return False
    a, b = set(before.split()), set(after.split())
    return SequenceMatcher(None, before, after).ratio() >= .60 or len(a & b) / max(1, len(a | b)) >= .60

class NoProgress(Exception):
    pass

ROLES = [
 ('Evidence analyst',0,'Extract relevant supplied facts and uncertainties. In later rounds address reviewer feedback and identify evidence gaps. Do not claim external research.'),
 ('Comparison analyst',2,'Compare options A and B using the shared evidence. Give tradeoffs and explicitly label unknowns. Improve prior comparison using feedback.'),
 ('Recommendation writer',3,'Write a concise recommendation from the shared analysis with exactly three measurable validation checks. Revise your prior draft based on review feedback.'),
 ('Quality reviewer',5,'Review the latest recommendation against the objective. Identify unsupported claims and missing measurable checks. Give concrete revision instructions. If satisfied say ACCEPTED and explain why. Never invent new evidence.'),
]

@app.get('/run')
def run():
    global current_job
    with job_lock:
        if current_job is not None:
            return StreamingResponse(stream_job(current_job),media_type='text/event-stream')
        job={'events':[],'stopped':threading.Event(),'done':False}
        current_job=job
    stopped=job['stopped']
    def emit(event):
        with job_lock: job['events'].append(event)
    class ObservedSwarm(RoundRobinSwarm):
        turn=0
        prior_outputs=None
        def __init__(self,**kwargs):
            super().__init__(**kwargs)
            self.prior_outputs={}
            self.last_review=""
        def _execute_agent(self,agent,task,*args,**kwargs):
            if stopped.is_set():
                raise RuntimeError('Run stopped')
            stage=self.turn%4
            round_number=self.turn//4+1
            task += '\n\nYOUR REQUIRED ACTION: '+ROLES[stage][2]+'\nSOURCE OF TRUTH: '+OBJECTIVE+'\nRespond in at most 100 words. No greetings, speaker announcements or claims of having run tests. Treat numbers invented by other agents as unsupported. Reviewer: explicitly reject unsupported numerical claims.'
            previous=self.prior_outputs.get(stage)
            if previous:
                task += '\nYOUR PREVIOUS ANSWER: '+previous+'\nLATEST REVIEW: '+self.last_review+'\nOnly describe concrete changes needed to address the review. Do not restate existing facts or the previous recommendation. If no change is justified, reply exactly NO_CHANGE.'
            incoming=kwargs.get('messages',[])
            input_text='ROLE INSTRUCTIONS\n'+ROLES[stage][2]+'\n\nSHARED HISTORY\n'+'\n\n'.join(str(m.get('role',''))+': '+str(m.get('content','')) for m in incoming)+'\n\nCURRENT TASK\n'+task
            emit({'phase':'running','stage':stage,'kind':ROLES[stage][1],'round':round_number,'agent':agent.agent_name,'input':input_text,'inputId':str(time.time_ns()),'time':time.strftime('%H:%M:%S')})
            from swarms.structs.context_utils import agent_answer
            result=agent_answer(agent,fallback=run_agent(agent,task,*args,**kwargs))
            if previous and is_repetition(previous,result):
                retry_task='Your answer repeated existing work. Give only a new correction responding to this review: '+self.last_review+'. Do not repeat: '+previous+'. If nothing new can be justified from supplied facts, reply exactly NO_CHANGE.'
                result=agent_answer(agent,fallback=run_agent(agent,retry_task,*args,**kwargs))
            if re.match(r'^\W*no[\s_]*change\b',result,re.IGNORECASE) or (previous and is_repetition(previous,result)):
                raise NoProgress('No further progress: '+agent.agent_name+' has no supported new contribution.')
            self.prior_outputs[stage]=result
            self.conversation.add(role=agent.agent_name,content=result)
            if stage==3:
                self.last_review=result
            if stopped.is_set():
                raise RuntimeError('Run stopped')
            self.turn+=1
            emit({'phase':'complete','stage':stage,'kind':ROLES[stage][1],'round':round_number,'agent':agent.agent_name,'output':result,'outputId':f'{time.time_ns()}','time':time.strftime('%H:%M:%S'),'turn':self.turn})
            if stage==3 and result.strip().upper().startswith("ACCEPTED"):
                raise NoProgress("Review accepted the recommendation.")
            return result
    def work():
        try:
            agents=[Agent(agent_name=name,system_prompt=instruction,model_name=MODEL,llm_base_url='http://127.0.0.1:52416/v1',llm_api_key='local-exo',max_loops=1,max_tokens=240,temperature=.25,llm_args={'timeout':30},output_type='final',verbose=False,telemetry=False,**agent_options('logs-demo:live-agent-'+str(index))) for index,(name,kind,instruction) in enumerate(ROLES)]
            swarm=ObservedSwarm(agents=agents,max_loops=3,verbose=False,output_type='final')
            emit({'phase':'objective','objective':OBJECTIVE})
            with tracer().start_as_current_span("Swarm Canvas workflow",attributes={"langfuse.trace.name":"Swarm Canvas workflow","langfuse.observation.type":"chain"}):
                result=swarm.run(OBJECTIVE)
            flush()
            emit({'phase':'finished','output':str(result),'rounds':3})
        except NoProgress as outcome:
            emit({'phase':'finished','reason':str(outcome),'rounds':swarm.turn//4,'turn':swarm.turn})
        except Exception as error:
            emit({'phase':'error','error':str(error)})
        finally:
            with job_lock: job['done']=True
    threading.Thread(target=work,daemon=True).start()
    return StreamingResponse(stream_job(job),media_type='text/event-stream')
