"""Project-local Langfuse credentials, MCP connection, and Swarms skill configuration."""
from pathlib import Path
import base64
ROOT=Path(__file__).resolve().parent

def config():
    """Read local credentials without placing them in frontend configuration."""
    values=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if '=' in line)
    return values

def connection_options():
    """Return native Swarms Agent constructor options for Langfuse tools and skills."""
    values=config()
    token=base64.b64encode((values['LANGFUSE_PUBLIC_KEY']+':'+values['LANGFUSE_SECRET_KEY']).encode()).decode()
    return {'mcp_configs':[{'name':'Langfuse local','url':'http://127.0.0.1:'+values['LANGFUSE_PORT']+'/api/public/mcp','transport':'streamable_http','headers':{'Authorization':'Basic '+token},'timeout':30}]}

def agent_options(node_id=None):
    """Expose only explicitly granted MCP capabilities; deny by default."""
    if not node_id:return {}
    from services.langfuse.grants import get_grant,require
    grant=get_grant(node_id)
    if not grant['enabled']:return {}
    def call(name,args):
        require(node_id,name)
        from swarms.tools.mcp_manager import MCPManager
        manager=MCPManager(**connection_options())
        manager.get_tools()
        require(node_id,name)
        return manager.call_tool(name,args)
    def read_execution_records(from_start_time:str,to_start_time:str,limit:int=10)->str:
        """Read execution records within an explicit time range, if permitted."""
        return str(call('listObservations',{'limit':min(max(limit,1),30),'fromStartTime':from_start_time,'toStartTime':to_start_time}))
    def read_evaluation_scores(limit:int=10)->str:
        """Read evaluation scores from the connected project, if permitted."""
        return str(call('listScores',{'limit':min(max(limit,1),30)}))
    def record_evaluation_score(trace_id:str,name:str,value:float,comment:str='')->str:
        """Write an explicitly permitted numeric evaluation score."""
        return str(call('createScore',{'traceId':trace_id,'name':name,'value':value,'comment':comment,'dataType':'NUMERIC'}))
    available={'listObservations':read_execution_records,'listScores':read_evaluation_scores,'createScore':record_evaluation_score}
    tools=[available[name] for name in grant['tools'] if name in available]
    return {'tools':tools} if tools else {}

_tracer=None
_provider=None

def tracer():
    """Create a separate local-only exporter without enabling Swarms' remote telemetry."""
    global _tracer,_provider
    if _tracer is None:
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        values=config()
        token=base64.b64encode((values['LANGFUSE_PUBLIC_KEY']+':'+values['LANGFUSE_SECRET_KEY']).encode()).decode()
        _provider=TracerProvider(resource=Resource.create({'service.name':'swarms-canvas'}))
        _provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint='http://127.0.0.1:'+values['LANGFUSE_PORT']+'/api/public/otel/v1/traces',headers={'Authorization':'Basic '+token,'x-langfuse-ingestion-version':'4'},timeout=5)))
        _tracer=_provider.get_tracer('swarms-canvas')
    return _tracer

def run_agent(agent,task,*args,**kwargs):
    """Record one real agent invocation, returning its ordinary result unchanged."""
    with tracer().start_as_current_span(agent.agent_name,attributes={'langfuse.observation.type':'agent','langfuse.observation.input':task,'gen_ai.request.model':agent.model_name}) as span:
        output=agent.run(task,*args,**kwargs)
        span.set_attribute('langfuse.observation.output',str(output))
        return output

def flush():
    """Wait for pending local trace export before verification or run completion."""
    if _provider is not None:_provider.force_flush(timeout_millis=10000)
