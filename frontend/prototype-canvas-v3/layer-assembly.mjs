const clone=value=>structuredClone(value);
const key=(node,port)=>node+'::'+port;
function handle(edge,side){
 if(edge.data?.[side+'Handle'])return edge.data[side+'Handle'];
 try{return JSON.parse((edge[side+'Handle']??'').replaceAll('œ','"'));}catch{return {};}
}
export function assertDAG(nodes,edges){
 const ids=new Set(nodes.map(node=>node.id));
 if(ids.size!==nodes.length)throw Error('The graph has duplicate node identities.');
 const degree=new Map(nodes.map(node=>[node.id,0])),next=new Map(nodes.map(node=>[node.id,[]]));
 for(const edge of edges){
  if(!ids.has(edge.source)||!ids.has(edge.target))throw Error('A connection refers to a missing component.');
  degree.set(edge.target,degree.get(edge.target)+1);next.get(edge.source).push(edge.target);
 }
 const ready=[...ids].filter(id=>degree.get(id)===0).sort(),order=[];
 while(ready.length){const id=ready.shift();order.push(id);for(const target of next.get(id)){degree.set(target,degree.get(target)-1);if(degree.get(target)===0){ready.push(target);ready.sort();}}}
 if(order.length!==nodes.length)throw Error('This selection contains a cycle. A composite DAG must be acyclic.');
 return order;
}
export function packageAssembly(graph,selectedIds,name,{id=crypto.randomUUID(),createdAt=new Date().toISOString()}={}){
 const selected=new Set(selectedIds);
 if(!name?.trim())throw Error('Name the composite.');
 if(!selected.size)throw Error('Select components to package.');
 const nodes=graph.nodes.filter(node=>selected.has(node.id));
 if(nodes.length!==selected.size)throw Error('A selected component is no longer on this canvas.');
 if(nodes.some(node=>node.type!=='genericNode'||!node.data?.node?.template))throw Error('Only executable Langflow components can be packaged; templates and notes remain separate.');
 const edges=graph.edges.filter(edge=>selected.has(edge.source)&&selected.has(edge.target));
 const order=assertDAG(nodes,edges);
 if(nodes.length>1){
  const visited=new Set([nodes[0].id]);let changed=true;
  while(changed){changed=false;for(const edge of edges)if(visited.has(edge.source)||visited.has(edge.target))for(const n of [edge.source,edge.target])if(!visited.has(n)){visited.add(n);changed=true;}}
  if(visited.size!==nodes.length)throw Error('Select a connected group of components.');
 }
 const inputs=new Map(),outputs=new Map();
 const expose=(direction,node,port,types,required=false)=>{
  const map=direction==='input'?inputs:outputs;const k=key(node.id,port);
  if(!map.has(k))map.set(k,{id:direction+'-'+map.size,name:(node.data.node.display_name??node.data.type)+' · '+(node.data.node.template[port]?.display_name??port),dataTypes:types?.length?types:['Any'],required,internal:{nodeId:node.id,port}});
 };
 const byId=new Map(nodes.map(node=>[node.id,node]));
 for(const edge of graph.edges){
  if(!selected.has(edge.source)&&selected.has(edge.target)){const h=handle(edge,'target');const n=byId.get(edge.target);const port=h.fieldName??'input_value';const f=n.data.node.template[port];expose('input',n,port,h.inputTypes??f?.input_types,Boolean(f?.required));}
  if(selected.has(edge.source)&&!selected.has(edge.target)){const h=handle(edge,'source');const n=byId.get(edge.source);const port=h.name??n.data.node.outputs?.[0]?.name??'output';expose('output',n,port,h.output_types??n.data.node.outputs?.find(output=>output.name===port)?.types);}
 }
 for(const node of nodes){
  const fields=node.data.node.template;
  if(node.data.type==='ChatInput'&&fields.input_value)expose('input',node,'input_value',fields.input_value.input_types?.length?fields.input_value.input_types:[fields.input_value.type??'str'],Boolean(fields.input_value.required));
  if(!edges.some(edge=>edge.target===node.id)&&node.data.type!=='ChatInput'){
   const field=fields.input_value;
   if(field&&(field.value==null||field.value===''))expose('input',node,'input_value',field.input_types??['Message'],Boolean(field.required));
  }
  if(!edges.some(edge=>edge.source===node.id)){
   const output=node.data.node.outputs?.find(output=>!output.hidden);
   if(output)expose('output',node,output.name,output.types);
  }
 }
 const assembly=clone({nodes,edges,viewport:graph.viewport??{x:0,y:0,zoom:1}});
 for(const node of assembly.nodes)node.selected=false;
 return {schemaVersion:1,id,name:name.trim(),version:1,kind:'composite-definition',plane:'Composite Components',sourcePlane:'Components',createdAt,status:'design-saved',assembly,contract:{inputs:[...inputs.values()],outputs:[...outputs.values()]},realization:{childNodeIds:nodes.map(node=>node.id),order},validation:{structure:'passed',behavior:'not-tested'},dependencies:[]};
}
export function compositeNode(item,{id=crypto.randomUUID(),position={x:360,y:160}}={}){
 return {id,type:'compositeNode',position,data:{label:item.name,customItemId:item.id,definitionVersion:item.version??1,contract:clone(item.contract??{inputs:[],outputs:[]}),childNodeIds:item.realization?.childNodeIds??item.assembly.nodes.map(node=>node.id),childCount:item.assembly.nodes.length}};
}
export function canConnectComposite(nodes,edges,connection){
 const source=nodes.find(node=>node.id===connection.source),target=nodes.find(node=>node.id===connection.target);
 if(!source||!target)throw Error('A connection endpoint is missing.');
 const out=source.data.contract?.outputs.find(port=>port.id===connection.sourceHandle),input=target.data.contract?.inputs.find(port=>port.id===connection.targetHandle);
 if(out&&input&&!out.dataTypes.some(type=>type==='Any'||input.dataTypes.includes(type)||input.dataTypes.includes('Any')))throw Error('These composite port types are incompatible.');
 assertDAG(nodes,[...edges,{...connection,id:'proposed'}]);
 return true;
}
