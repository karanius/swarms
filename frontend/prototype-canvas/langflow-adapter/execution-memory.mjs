// V2 policy uses Langflow's existing session and agent-history fields.
export const executionMemoryPolicy=Object.freeze({version:1,scope:'run',agentHistory:'disabled',retention:'langflow-managed'});
export function configureExecutionMemory(nodes,sessionId=''){
 const configured=structuredClone(nodes);
 for(const node of configured){
  const template=node.data?.node?.template;
  if(!template)continue;
  if(['ChatInput','ChatOutput'].includes(node.data?.type)&&template.session_id){
   template.session_id={...template.session_id,value:sessionId,load_from_db:false};
  }
  if(node.data?.type==='Agent'){
   if(!template.n_messages)throw new Error('Agent has no Langflow history control: '+node.id);
   template.n_messages={...template.n_messages,value:0,load_from_db:false};
   if(template.context_id)template.context_id={...template.context_id,value:sessionId?sessionId+':'+node.id:'',load_from_db:false};
  }
 }
 return configured;
}
export function prepareIsolatedRun(nodes,createId=()=>crypto.randomUUID()){
 const session='v2-run-'+createId();
 const inputValue=nodes.find(node=>node.data?.type==='ChatInput')?.data?.node?.template?.input_value?.value;
 return {session,nodes:configureExecutionMemory(nodes,session),inputValue:typeof inputValue==='string'?inputValue:undefined};
}
