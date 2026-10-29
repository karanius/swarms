// Exploratory multiscale grouping model added after the user's objective clarification.
// It generates structural candidates under explicit responsibility profiles, not semantics from nothing.
import {createHash} from 'node:crypto';
export const formationVersion='layer-formation-1';
const hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex').slice(0,12);
function connected(ids,links){const selected=new Set(ids),reached=new Set([ids[0]]);let changed=true;while(changed){changed=false;for(const l of links)if(selected.has(l.from)&&selected.has(l.to)&&(reached.has(l.from)||reached.has(l.to))){if(!reached.has(l.from)||!reached.has(l.to)){reached.add(l.from);reached.add(l.to);changed=true;}}}return reached.size===ids.length;}
function dag(ids,links){const degree=Object.fromEntries(ids.map(i=>[i,0]));const graph=Object.fromEntries(ids.map(i=>[i,[]]));for(const l of links)if(l.from in degree&&l.to in degree){degree[l.to]++;graph[l.from].push(l.to);}const q=ids.filter(i=>degree[i]===0);let n=0;while(q.length){const id=q.pop();n++;for(const to of graph[id])if(--degree[to]===0)q.push(to);}return n===ids.length;}
export function formLayer(items,links,profile,{maxCandidates=100,minMembers=2,maxMembers=3}={}){
 if(!profile)return {items:[],links:[],attempts:0,omitted:true,gaps:[{kind:'missing-profile'}]};
 const ordered=[...items].sort((a,b)=>a.id.localeCompare(b.id));const output=[],gaps=[],trace=[];let attempts=0,truncated=false;
 const inspect=group=>{
  if(attempts>=maxCandidates){truncated=true;return false;}attempts++;
  const ids=group.map(x=>x.id),requirements=[...new Set(group.flatMap(x=>x.requirements))].sort();
  const criterion=profile.responsibilities.find(r=>JSON.stringify([...r.requirements].sort())===JSON.stringify(requirements));
  if(!criterion||group.some(i=>i.layer!==profile.from)||!connected(ids,links)||!dag(ids,links)){trace.push({ids,accepted:false,reason:'profile-responsibility-or-graph'});return true;}
  const inner=links.filter(l=>ids.includes(l.from)&&ids.includes(l.to));
  if(inner.some(l=>!group.find(x=>x.id===l.from).outputs.includes(l.type)||!group.find(x=>x.id===l.to).inputs.includes(l.type))){trace.push({ids,accepted:false,reason:'type'});return true;}
  const crossing=links.filter(l=>ids.includes(l.from)!==ids.includes(l.to));
  const incoming=new Set(inner.map(l=>l.to)),outgoing=new Set(inner.map(l=>l.from));
  const entries=group.filter(x=>!incoming.has(x.id)),exits=group.filter(x=>!outgoing.has(x.id));
  const item={id:profile.to+':'+hash({profile:profile.id,ids}),layer:profile.to,name:criterion.name,requirements,
    members:ids,leafIds:[...new Set(group.flatMap(x=>x.leafIds??[x.id]))].sort(),
    inputs:[...new Set(entries.flatMap(x=>x.inputs))],outputs:[...new Set(exits.flatMap(x=>x.outputs))],
    boundary:{entries:entries.map(x=>x.id),exits:exits.map(x=>x.id),crossing,fieldBindings:group.flatMap(x=>x.boundary?.fieldBindings??(x.fieldBindings?[{member:x.id,bindings:x.fieldBindings}]:[]))},
    unresolvedBindings:group.flatMap(x=>x.unresolvedBindings??[]),
    profile:profile.id,structuralStatus:'candidate',behavior:'unknown',provenance:'explicit-profile grouping; not learned emergence'};
  output.push(item);trace.push({ids,accepted:true,item:item.id});return true;
 };
 function choose(start,chosen,size){if(chosen.length===size)return inspect(chosen);for(let i=start;i<ordered.length;i++){if(!choose(i+1,[...chosen,ordered[i]],size))return false;}return true;}
 for(let n=minMembers;n<=Math.min(maxMembers,ordered.length);n++)if(!choose(0,[],n))break;
 const projected=[];
 for(const l of links)for(const a of output.filter(x=>x.members.includes(l.from)))for(const b of output.filter(x=>x.members.includes(l.to)))if(a.id!==b.id&&!a.leafIds.some(x=>b.leafIds.includes(x))){const key=a.id+'>'+b.id+':'+l.type;if(!projected.some(e=>e.id===key))projected.push({id:key,from:a.id,to:b.id,type:l.type,underlyingLink:l.id,underlyingIncidence:l});}
 if(!output.length)gaps.push({kind:truncated?'search-horizon':'no-supported-group',profile:profile.id});
 return {items:output,links:projected,attempts,omitted:truncated,gaps,trace};
}
export function growFromComponents(document,library,{flowProfile=true,reviewContract=null,maxCandidates=100}={}){
 const definitions=new Map(library.items.map(i=>[i.id,i]));
 const items=document.entities.filter(e=>e.layer==='components').map(e=>{const d=definitions.get(e.itemRef.id);if(!d||d.revision!==e.itemRef.revision)throw Error('Unpinned native reference.');return {id:e.id,layer:'components',name:d.name,requirements:e.requirementIds,
  inputs:[...new Set(Object.values(d.native.template).filter(f=>f&&typeof f==='object').flatMap(f=>f.input_types??[]))],
  outputs:[...new Set(d.native.outputs.flatMap(p=>p.types))],leafIds:[e.id],definition:e.itemRef,ports:{inputs:Object.entries(d.native.template).filter(([k,f])=>f&&typeof f==='object'&&k!=='code').map(([name,f])=>({name,type:f.type,accepted:f.input_types??[],required:f.required??false})),outputs:d.native.outputs.map(p=>({name:p.name,types:p.types}))},unresolvedBindings:(e.resourceRefs??[]).map(ref=>({member:e.id,field:'model',resourceRef:ref,status:'unresolved/native binding not established'}))};});
 // Chat Input's source-text field is distinct from its Message output and is retained explicitly.
 for(const i of items)if(i.name==='Chat Input'){i.inputs=['str'];i.fieldBinding=document.entities.find(e=>e.id===i.id).fieldBindings;}
 const links=document.links.filter(l=>l.kind==='data'&&items.some(i=>i.id===l.from)&&items.some(i=>i.id===l.to));
 const compositeProfile={id:'components-to-composite-responsibility@1',from:'components',to:'composite',responsibilities:[{name:'Assessment capability',requirements:['R-intake','R-assess']},{name:'Drafting capability',requirements:['R-draft']}]};
 const composites=formLayer(items,links,compositeProfile,{maxCandidates});
 const flowProfileRecord=flowProfile?{id:'composite-to-flow-order@1',from:'composite',to:'flows',responsibilities:[{name:'Triage sequence',requirements:['R-intake','R-assess','R-draft']}]}:null;
 const flows=formLayer(composites.items,composites.links,flowProfileRecord,{maxCandidates});
 const process={items:[],gaps:[]};
 if(flows.items.length){if(!reviewContract)process.gaps.push({kind:'missing-lifecycle-contract',requirement:'R-review',description:'A flow does not define accountable review, escalation and completion on its own.'});
  else if(!reviewContract.owner||!reviewContract.completion)process.gaps.push({kind:'incomplete-lifecycle-contract'});
  else for(const f of flows.items)process.items.push({id:'processes:'+hash({flow:f.id,reviewContract}),layer:'processes',name:'Proposed triage lifecycle',members:[f.id],leafIds:f.leafIds,requirements:[...f.requirements,'R-review'],reviewContract,structuralStatus:'candidate',behavior:'unknown',provenance:'supplied synthetic lifecycle contract; not runtime evidence'});
 }
 return {version:formationVersion,components:items,composite:composites,flows,process,
  claimBoundary:'Layer-specific responsibilities and lifecycle semantics are supplied. Typed metadata bounds candidates but does not uniquely derive higher-layer meaning.'};
}
