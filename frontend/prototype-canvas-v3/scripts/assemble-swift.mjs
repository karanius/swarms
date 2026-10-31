// Deterministic assembly: definitions and resource bindings are supplied by the host.
export function assembleSwift(template,definitions,createId=()=>crypto.randomUUID()){
 if(template.kind!=='agent-template')throw Error('Expected a Swift agent template.');
 const nodes=['ChatInput','Agent','ChatOutput'].map((type,index)=>{
  if(!definitions[type]?.template)throw Error('Missing Langflow component: '+type);
  const id=type+'-'+createId();
  return {id,type:'genericNode',position:{x:360+index*420,y:140},data:{id,type,node:structuredClone(definitions[type])}};
 });
 const fields=nodes[1].data.node.template;
 fields.model.value=[{provider:template.resources.model.provider,name:template.resources.model.name}];
 fields.system_prompt.value='You are Swift, an agent instance created from the Swift template. Help with the task the user describes. Use only tools actually connected to this instance. Explain missing capabilities honestly.';
 fields.n_messages.value=20;
 for(const key of ['add_current_date_tool','add_calculator_tool'])if(fields[key])fields[key].value=false;
 const edge=(source,target,output,input)=>{
  const sourceHandle={dataType:source.data.type,id:source.id,name:output,output_types:['Message']};
  const field=target.data.node.template[input];
  const targetHandle={fieldName:input,id:target.id,inputTypes:field?.input_types??['Message'],type:field?.type??'str'};
  return {id:createId(),source:source.id,target:target.id,type:'default',sourceHandle:JSON.stringify(sourceHandle).replaceAll('"','œ'),targetHandle:JSON.stringify(targetHandle).replaceAll('"','œ'),data:{sourceHandle,targetHandle}};
 };
 return {schemaVersion:1,kind:'agent-instance',id:'swift-'+createId(),name:'Swift instance',templateRef:{id:template.id,version:template.version},state:'assembled',data:{nodes,edges:[edge(nodes[0],nodes[1],'message','input_value'),edge(nodes[1],nodes[2],'response','input_value')],viewport:{x:0,y:0,zoom:1}}};
}
