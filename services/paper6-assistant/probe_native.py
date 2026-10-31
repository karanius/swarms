"""Bounded native-runtime probe; no paper or canvas writes."""
import asyncio,json
from urllib.request import urlopen
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage
from lfx.components.models_and_agents import AgentComponent
async def main():
 model=json.load(urlopen('http://127.0.0.1:8787/v1/models'))['data'][0]['id']
 async def describe_research_scope(topic:str)->str:
  """Return the exact isolated research scope; call this before answering about scope."""
  return 'Paper6 only. No canvas access. Tool invocation observed.'
 tool=StructuredTool.from_function(coroutine=describe_research_scope)
 llm=ChatOpenAI(model=model,base_url='http://127.0.0.1:8787/v1',api_key='local-proxy',use_responses_api=False,timeout=90,max_retries=0)
 component=AgentComponent(_user_id="paper6-research");component.set(model=llm,tools=[tool],system_prompt='You are a dedicated research assistant. Call describe_research_scope, then state its returned scope in one sentence.',max_iterations=4,handle_parsing_errors=True)
 agent=component.create_agent_runnable(allow_interrupts=False)
 result=await asyncio.wait_for(agent.ainvoke({'messages':[HumanMessage(content='What is your research scope?')]},{'recursion_limit':30}),120)
 print(json.dumps([{'role':m.type,'text':m.content,'tool_calls':getattr(m,'tool_calls',[])} for m in result['messages']],default=str))
if __name__=='__main__':asyncio.run(main())
