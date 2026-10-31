export const CONTEXT_STORAGE_KEY='swarms.v3.system-context-checkpoints.v1';

// Consumers receive independent snapshots, never a mutable handle to the source.
export function createContextChannel(){
 let snapshot=null;
 const listeners=new Set();
 const getSnapshot=()=>snapshot===null?null:structuredClone(snapshot);
 const reader=Object.freeze({getSnapshot,subscribe(listener){listeners.add(listener);return ()=>listeners.delete(listener);}});
 return {reader,publish(value){snapshot=sanitizeContextValue(value);for(const listener of listeners){try{listener(getSnapshot());}catch{ /* A consumer cannot interrupt context publication. */ }}},clear(){snapshot=null;listeners.clear();}};
}
const label=plane=>plane==='Composite Components'?'Composite':plane;
const secretKey=key=>{
 const normalized=String(key).replace(/[^a-z0-9]/gi,'').toLowerCase();
 if(/refs?$/.test(normalized))return false;
 return /^(authorization|proxyauthorization|cookie|setcookie|apikey|openaiapikey|accesstoken|refreshtoken|idtoken|bearertoken|password|passwd|clientsecret|privatekey|credential|credentials|secret|token)$/.test(normalized)||/(apikey|password|clientsecret|accesstoken|refreshtoken|privatekey)$/.test(normalized);
};
const credentialRef=path=>({ref:'credential:'+path,status:'not-exported'});
function safeString(value){
 return value.replace(/\b(Bearer|Basic)\s+[^\s"'<>]+/gi,'$1 [redacted]').replace(/([?&](?:api[_-]?key|access[_-]?token|refresh[_-]?token|token|secret|password)=)[^&#\s]*/gi,'$1[redacted]').replace(/(https?:\/\/)[^/@\s]+:[^/@\s]+@/gi,'$1[redacted]@');
}
export function sanitizeContextValue(value,path='context',seen=new WeakSet()){
 if(value===null||typeof value==='boolean'||typeof value==='number')return value;
 if(typeof value==='string')return safeString(value);
 if(value===undefined)return undefined;
 if(typeof value!=='object')throw new Error('System context contains a value that cannot be represented as JSON.');
 if(seen.has(value))throw new Error('System context contains a circular reference.');
 seen.add(value);
 const result=Array.isArray(value)?value.map((entry,index)=>sanitizeContextValue(entry,path+'/'+index,seen)):Object.fromEntries(Object.entries(value).map(([key,entry])=>[key,secretKey(key)?credentialRef(path+'/'+key):sanitizeContextValue(entry,path+'/'+key,seen)]));
 seen.delete(value);return result;
}
function configuration(node){
 const template=node.data?.node?.template??{};
 return Object.fromEntries(Object.entries(template).filter(([key,field])=>key!=='code'&&key!=='_type'&&field&&typeof field==='object'&&'value' in field).map(([key,field])=>{
  const path='langflow/'+node.id+'/'+key;
  const secret=secretKey(key)||field.password===true||/secret|password/i.test(String(field._input_type??field.type??''));
  return [key,secret?credentialRef(path):typeof field.value==='string'&&field.value.length>16000?{ref:'configuration:'+path,status:'large-value-not-inlined',characters:field.value.length}:sanitizeContextValue(field.value,path)];
 }));
}
export function projectCanvasGraph(graph={nodes:[],edges:[]}){
 if(!Array.isArray(graph.nodes)||!Array.isArray(graph.edges))throw new Error('A canvas graph has invalid nodes or connections.');
 return {
  nodes:graph.nodes.map(node=>{
   const type=node.data?.type??node.type;
   const template=node.data?.swiftTemplate;
   const reference=template?{kind:'template',id:template.id,version:template.version}:node.data?.customItemId?{kind:'custom-library-item',id:node.data.customItemId,storageRef:'browser-local:swarms.v3.custom-library.v1'}:{kind:'native-component',catalogRef:'langflow-connected',type,revisionStatus:'live-unpinned'};
   return {id:node.id,type,label:template?.name??node.data?.label??node.data?.node?.display_name??type,definitionRef:reference,position:node.position,configuration:template||node.data?.customItemId?{}:configuration(node)};
  }),
  connections:graph.edges.map(edge=>({id:edge.id,source:edge.source,target:edge.target,sourceHandle:edge.sourceHandle,targetHandle:edge.targetHandle})),
  viewport:graph.viewport??{x:0,y:0,zoom:1},
 };
}
const refForDocument=(template,suffix)=>template.documents?.find(doc=>doc.path?.endsWith(suffix))?.path??'knowledge/instance-machine/'+suffix;
export function buildSystemContext({planes,catalog,officialTemplates,swiftTemplate,customItems=[],nativeGraph={nodes:[],edges:[]},planeGraphs={},instancePositions={},activePlane='Components',nativeContext={},checkpointMetadata=[],assemblyName=''}){
 const connected=new Set(nativeContext.catalog?.componentTypes??[]);
 const componentItems=catalog.flatMap(group=>group.items.map(item=>({id:item.id,name:item.name,layerId:'Components',category:group.name,legacy:Boolean(item.legacy),definitionRef:{endpoint:'/api/v1/all',componentType:item.id},availability:connected.size?(connected.has(item.id)?'available-in-connected-catalog':'not-in-connected-catalog'):'connection-not-observed',validation:'not-established-by-catalog'})));
 const canvases=Object.fromEntries(planes.map(plane=>[plane,{label:label(plane),layout:{instancePosition:instancePositions[plane]??{x:32,y:96}},...projectCanvasGraph(plane==='Components'?nativeGraph:planeGraphs[plane]??{nodes:[],edges:[]})}]));
 const instances=(nativeContext.knownInstances??[]).map(instance=>sanitizeContextValue(instance,'instances/'+instance.id));
 const unstructured={status:'documented-not-normalized',records:[],documentRefs:[refForDocument(swiftTemplate,'domain-model.md'),refForDocument(swiftTemplate,'canonical-specification.md')]};
 const context={
  schemaVersion:1,kind:'system-context',id:'swarms-instance-machine-v3',status:'working-draft',
  scope:{coverage:'V3 workbench, referenced library resources, and instances observed in this session',limitations:['This manifest is an inspectable projection, not a completed canonical registry or compiler.','Backend-wide instance discovery and structured discovery records are not connected.']},
  library:{id:'v3-library',layers:planes.map((plane,index)=>({id:plane,label:label(plane),order:index,representation:plane==='Components'?'native-component-catalog':plane==='Composite Components'?'imported-candidates-and-design-snapshots':'proposed-label-catalog',proposedCatalogRef:plane==='Components'?null:'frontend/prototype-canvas-v3/v3-library.jsx#'+encodeURIComponent(plane)})),components:componentItems,officialTemplates:officialTemplates.items.map(item=>({id:item.id,name:item.name,category:item.category,layerId:item.candidatePlane,classificationStatus:item.classificationStatus,validationStatus:item.validationStatus,definitionRef:{href:item.file,sha256:item.source.sha256},sourceRef:{repository:item.source.repository,revision:item.source.revision,path:item.source.path,license:item.source.license}})),customItems:customItems.map(item=>({id:item.id,name:item.name,layerId:item.plane,sourcePlane:item.sourcePlane,status:item.status,createdAt:item.createdAt,definitionRef:{storage:'browser-local',key:'swarms.v3.custom-library.v1',itemId:item.id},nodeCount:item.assembly?.nodes?.length??0,connectionCount:item.assembly?.edges?.length??0,dependencyRefs:(item.dependencies??[]).map(dependency=>({id:dependency.id,layerId:dependency.plane}))}))},
  templates:[sanitizeContextValue(swiftTemplate,'templates/'+swiftTemplate.id)],
  instances:{activeInstanceRef:nativeContext.activeInstance?.id??null,records:instances,coverage:'observed-workbench-session-only',workspaceFlow:nativeContext.flow??null},
  discovery:{intent:{status:'not-captured-as-a-structured-record',record:null},requirements:unstructured,decisions:unstructured,assumptions:{status:'not-normalized',records:[]},constraints:{status:'not-normalized',records:[]}},
  assemblies:{scripts:[{ref:swiftTemplate.assembly?.scriptRef,status:swiftTemplate.assembly?.status,scope:'Swift native chat assembly only'}],contracts:{status:'draft-documentation',documentRef:refForDocument(swiftTemplate,'contracts.md')}},
  deployments:{launcherRefs:[{ref:swiftTemplate.deployment?.launcherRef,status:swiftTemplate.deployment?.status}],records:instances.filter(instance=>instance.deployment).map(instance=>({instanceRef:instance.id,...instance.deployment})),registryCoverage:'observed-session-only'},
  resources:{modelBindings:[swiftTemplate.resources?.model].filter(Boolean),executor:{activeAdapter:'langflow-native',planned:swiftTemplate.resources?.executor??null},skills:swiftTemplate.resources?.skills??[],tools:{status:'planned-interface',definitions:swiftTemplate.architecture?.find(piece=>piece.piece==='Library tools')?.tools??[]},credentialPolicy:{policy:'references-only',storage:'existing-provider-stores',valuesIncluded:false},optimizer:{ref:'https://github.com/google-research/harness2',integrationStatus:'not-integrated'}},
  documents:swiftTemplate.documents??[],
  validation:{serialization:{method:'JSON.stringify',scope:'this projection only'},schema:{status:'not-integrated',plannedValidatorRef:'https://github.com/ajv-validator/ajv'},behavior:{status:'not-established-by-this-view'}},
  evidence:{records:nativeContext.lastBuildObservation?[nativeContext.lastBuildObservation]:[],scope:'native controller observations only; no private chat history is loaded'},
  gaps:[{id:'native-revisions',status:'open',description:'Connected component definitions are live references, not pinned executable revisions.'},{id:'discovery-records',status:'open',description:'Intent, requirements and decisions still need structured instance records.'},{id:'higher-layer-catalogs',status:'open',description:'Proposed higher-layer names are not executable library definitions.'},{id:'canonical-registry',status:'open',description:'The full canonical instance registry and general compiler are not implemented.'},{id:'schema-validation',status:'open',description:'Ajv schemas and semantic contract validation are not integrated.'}],
  workspace:{activePlane,assemblyDraftName:assemblyName,canvases},
  runtime:{connection:nativeContext.catalog?'catalog-connected':'not-observed',activity:nativeContext.isBuilding?'building':'idle',memoryPolicy:nativeContext.memoryPolicy??null},
  checkpoints:{persistence:'browser-local',storageKey:CONTEXT_STORAGE_KEY,records:checkpointMetadata},
 };
 return sanitizeContextValue(context);
}
export function readContextCheckpoints(storage){
 const raw=storage.getItem(CONTEXT_STORAGE_KEY);
 if(!raw)return {schemaVersion:1,checkpoints:[]};
 let value;try{value=JSON.parse(raw);}catch{throw new Error('Saved context checkpoints could not be read. Existing storage has been preserved.');}
 if(value?.schemaVersion!==1||!Array.isArray(value.checkpoints)||value.checkpoints.some(checkpoint=>!checkpoint.id||!Number.isSafeInteger(checkpoint.version)||checkpoint.version<1||checkpoint.context?.kind!=='system-context'))throw new Error('Saved context checkpoints have an unsupported format. Existing storage has been preserved.');
 return value;
}
export function checkpointSummaries(store){return store.checkpoints.map(({id,version,createdAt})=>({id,version,createdAt}));}
export function saveContextCheckpoint(storage,context,{id=crypto.randomUUID(),createdAt=new Date().toISOString()}={}){
 if(context?.kind!=='system-context')throw new Error('A system context is required before saving a checkpoint.');
 const store=readContextCheckpoints(storage);
 const version=Math.max(0,...store.checkpoints.map(checkpoint=>checkpoint.version))+1;
 const checkpoint={id,version,createdAt,context:sanitizeContextValue(context)};
 const next={schemaVersion:1,checkpoints:[...store.checkpoints,checkpoint]};
 // setItem is the commit point; failures leave both the prior store and caller state intact.
 storage.setItem(CONTEXT_STORAGE_KEY,JSON.stringify(next));
 return {store:next,checkpoint};
}
