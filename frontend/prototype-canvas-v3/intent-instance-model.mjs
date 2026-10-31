export function projectInstance(document,plane='all',library=null){
 const layers=[...document.layers].sort((a,b)=>b.order-a.order);
 const included=document.entities.filter(e=>plane==='all'||e.layer===plane),ids=new Set(included.map(e=>e.id)),positions=new Map();
 for(const [row,l] of layers.entries())document.entities.filter(e=>e.layer===l.id).forEach((e,index)=>positions.set(e.id,{x:index*240,y:plane==='all'?row*200:0}));
 const nodes=included.map(e=>({id:e.id,type:'instanceEntity',position:positions.get(e.id),data:{entity:e,nativeName:e.itemRef?(library?.items.find(item=>item.id===e.itemRef.id&&item.revision===e.itemRef.revision)?.name??e.itemRef.id):null,gapCount:document.gaps.filter(g=>g.status==='open'&&g.entityIds.includes(e.id)).length},draggable:false}));
 if(plane==='all')for(const [row,l] of layers.entries())nodes.push({id:'label:'+l.id,type:'instancePlaneLabel',position:{x:-135,y:row*200+26},data:{label:l.name},selectable:false,draggable:false});
 const edges=document.links.filter(l=>ids.has(l.from)&&ids.has(l.to)).map(l=>({id:l.id,source:l.from,target:l.to,sourceHandle:'out',targetHandle:'in',label:l.kind==='data'?l.type:l.kind,animated:false,style:{stroke:l.kind==='data'?'#8dd3c3':'#9daac0',strokeDasharray:l.kind==='data'?undefined:'5 5'},data:{relationship:l}}));
 if(plane==='all')for(const e of included)for(const member of e.members)if(ids.has(member))edges.push({id:'member:'+e.id+':'+member,source:e.id,target:member,sourceHandle:'members',targetHandle:'parent',label:'represents',style:{stroke:'#687e9c',strokeDasharray:'4 6'},data:{relationship:{kind:'membership',from:e.id,to:member}}});
 return {nodes,edges};
}
export const openQuestions=doc=>doc.questions.filter(q=>!q.answer||doc.gaps.find(g=>g.id===q.gapId)?.status==='open');
export function requirementCoverage(doc){return doc.requirements.map(r=>({...r,entities:r.realizationIds.map(id=>doc.entities.find(e=>e.id===id)).filter(Boolean),openGaps:doc.gaps.filter(g=>g.status==='open'&&g.requirementIds.includes(r.id))}));}
