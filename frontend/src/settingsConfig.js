import {researchDefaults} from './ResearchPanel';
import {defaults as compare} from './ComparePanel';
import {defaults as write} from './WritePanel';
import {defaults as review} from './ReviewPanel';
import {defaults as repeat} from './RepeatPanel';
import {defaults as parallel} from './ParallelPanel';
export const kinds=['research','read','compare','write','parallel','review','repeat'];
export const labels={research:'Research',read:'Read documents',compare:'Compare',write:'Write',parallel:'Parallel team',review:'Review',repeat:'Repeat'};
export const initialDefaults={research:researchDefaults,read:{file_path:''},compare,write,parallel,review,repeat};
export const categories=['Models','Instructions and presets','Inputs and objectives','Tools and access','Execution and coordination','Outputs','Evaluation and failures','Storage and files','Plugin'];
export const fields={
 retry_attempts:['Execution and coordination','Model retries','number'],tool_retry_attempts:['Execution and coordination','Tool retries','number'],context_length:['Models','Context length','number'],context_compression:['Execution and coordination','Compress context','boolean'],persistent_memory:['Storage and files','Persistent agent memory','boolean'],
 reasoning_effort:['Models','Reasoning effort','effort'],
 model_name:['Models','Model','text'],temperature:['Models','Temperature','number'],max_tokens:['Models','Maximum output tokens','number'],
 system_prompt:['Instructions and presets','System instructions','textarea'],instructions:['Instructions and presets','Instructions','textarea'],criteria:['Instructions and presets','Comparison criteria','textarea'],
 task:['Inputs and objectives','Default task','textarea'],question:['Inputs and objectives','Default question','textarea'],material:['Inputs and objectives','Default source material','textarea'],file_path:['Storage and files','File path','text'],
 mcp_urls:['Tools and access','MCP server URLs','textarea'],max_loops:['Execution and coordination','Iterations / rounds','loops'],plan_enabled:['Execution and coordination','Plan before execution','boolean'],name:['Execution and coordination','Team name','text'],description:['Execution and coordination','Team description','textarea'],max_workers:['Execution and coordination','Concurrent workers','number'],members:['Execution and coordination','Members','members'],
 output_type:['Outputs','Returned data','output'],layout:['Outputs','Comparison layout','layout'],format:['Outputs','Writing format','format'],destination:['Storage and files','Output destination','destination'],on_error:['Evaluation and failures','Member failure policy','failure'],return_score:['Evaluation and failures','Return keyword reward','boolean'],autosave:['Storage and files','Save Python workflow conversation','boolean'],
};
export function categoryFor(node,key){return node==='review'&&key==='criteria'?'Evaluation and failures':node==='read'&&key==='file_path'?'Inputs and objectives':fields[key]?.[0];}
