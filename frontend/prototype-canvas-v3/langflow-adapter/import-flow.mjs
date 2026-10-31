export function parseFlowImport(text){
 const value=JSON.parse(text);
 const flow=Array.isArray(value?.flows)?value.flows[0]:value;
 const data=flow?.data??flow;
 if(!Array.isArray(data?.nodes)||!Array.isArray(data?.edges))throw new Error('Choose a Langflow JSON file containing nodes and edges.');
 const ids=new Set();
 for(const node of data.nodes){
  if(typeof node?.id!=='string'||!node.id||ids.has(node.id))throw new Error('Every imported node needs a unique ID.');
  if(!node.position||!Number.isFinite(node.position.x)||!Number.isFinite(node.position.y)||!node.data)throw new Error('An imported node has an invalid position or definition.');
  ids.add(node.id);
 }
 for(const edge of data.edges)if(!ids.has(edge.source)||!ids.has(edge.target))throw new Error('An imported connection refers to a missing node.');
 return {name:typeof flow?.name==='string'?flow.name:'Imported assembly',data:structuredClone(data)};
}
