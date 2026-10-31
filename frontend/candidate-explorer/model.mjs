// Pure, static boundary analysis. Saved graphs are data; no component code runs.
export function seedMembers(graph, witness) {
 const ids=new Set(witness.previewEdgeIds);
 return [...new Set(graph.edges.filter(e=>ids.has(e.id)).flatMap(e=>[e.source,e.target]))].filter(id=>graph.nodes.some(n=>n.id===id));
}
export function expandMembers(graph,members){
 const selected=new Set(members), known=new Set(graph.nodes.map(n=>n.id));
 return [...new Set([...members,...graph.edges.filter(e=>selected.has(e.source)||selected.has(e.target)).flatMap(e=>[e.source,e.target])])].filter(id=>known.has(id));
}
export function analyzeCandidate(graph,members,purpose=''){
 const known=new Set(graph.nodes.map(n=>n.id)), selected=new Set(members.filter(id=>known.has(id)));
 const nodes=graph.nodes.filter(n=>selected.has(n.id)), internal=[], incoming=[], outgoing=[], unresolved=[];
 for(const e of graph.edges){
  const s=selected.has(e.source),t=selected.has(e.target);
  if(!s&&!t)continue;
  if(!known.has(e.source)||!known.has(e.target)||!e.resolved||!e.sourcePort||!e.targetPort)unresolved.push(e);
  if(s&&t)internal.push(e);else if(t)incoming.push(e);else outgoing.push(e);
 }
 const unconnectedInputs=[],terminalOutputs=[],resources=[];
 for(const n of nodes){
  for(const p of n.inputs??[])if(!graph.edges.some(e=>e.target===n.id&&e.targetPort===p.name))unconnectedInputs.push({node:n.id,type:n.type,...p,status:'No saved incoming edge; configured/default value not inspected'});
  for(const p of n.outputs??[])if(!graph.edges.some(e=>e.source===n.id&&e.sourcePort===p.name))terminalOutputs.push({node:n.id,type:n.type,...p,status:'Declared output without saved consumer; exposure is a proposal, activation unverified'});
  for(const r of n.resourceRequirements??[])resources.push({node:n.id,...r,status:'Binding value and availability not inspected'});
 }
 const seen=new Set(),queue=nodes.length?[nodes[0].id]:[];
 while(queue.length){const id=queue.pop();if(seen.has(id))continue;seen.add(id);for(const e of internal){if(e.source===id&&!seen.has(e.target))queue.push(e.target);if(e.target===id&&!seen.has(e.source))queue.push(e.source)}}
 const indegree=new Map(nodes.map(n=>[n.id,0]));for(const e of internal)indegree.set(e.target,indegree.get(e.target)+1);
 const ready=nodes.filter(n=>!indegree.get(n.id)).map(n=>n.id);let visited=0;
 while(ready.length){const id=ready.pop();visited++;for(const e of internal.filter(e=>e.source===id)){indegree.set(e.target,indegree.get(e.target)-1);if(!indegree.get(e.target))ready.push(e.target)}}
 const checks=[
  {name:'Nonempty group',status:nodes.length?'observed':'blocked',detail:`${nodes.length} actual component occurrences selected`},
  {name:'Connected group',status:nodes.length&&seen.size===nodes.length?'observed':'blocked',detail:'Weak connectivity of the induced saved-edge subgraph'},
  {name:'Acyclic internal graph',status:visited===nodes.length&&nodes.length?'observed':'blocked',detail:'Directed cycle check on recorded internal edges'},
  {name:'Readable incident edges',status:unresolved.length?'unknown':'observed',detail:`${unresolved.length} unresolved endpoint or port records`},
  {name:'Purpose',status:purpose.trim()?'proposed':'unknown',detail:purpose.trim()||'Specify one bounded job; topology does not establish purpose'},
  {name:'Configuration and resources',status:'unknown',detail:`${unconnectedInputs.filter(p=>p.required).length} required fields without a saved incoming edge; values/defaults not inspected`},
  {name:'Port activation and compatibility',status:'unknown',detail:'Saved port names and labels alone do not establish runtime compatibility'},
  {name:'Task usefulness',status:'unknown',detail:'No task execution, behavioral evaluation or approved composite'}
 ];
 return {schemaVersion:1,status:'candidate-only',graph:graph.id,sourceFileSha256:graph.sha256,sourcePointer:graph.pointer,purpose:{text:purpose,judgment:'proposed, not inferred or validated'},members:nodes.map(n=>({id:n.id,type:n.type,version:n.version})),internal,incoming,outgoing,unresolved,unconnectedInputs,terminalOutputs,resources,checks,sources:graph.sources};
}
