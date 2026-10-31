// Topology-only research artifacts. These describe designs, never executable flows.
const list = (value, max, name) => {
 if (!Array.isArray(value) || value.length > max) throw Error(`Invalid ${name}`);
 return value;
};
const text = (value, max, name) => {
 if (typeof value !== 'string' || !value.trim() || value.length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(value)) throw Error(`Invalid ${name}`);
 return value;
};
const id = value => {
 text(value, 120, 'id');
 if (!/^[a-zA-Z0-9_.:-]+$/.test(value)) throw Error('Invalid id');
 return value;
};
const finite = value => {
 if (typeof value !== 'number' || !Number.isFinite(value) || Math.abs(value) > 1000000) throw Error('Invalid position/order');
 return value;
};
function unique(items, name) {
 if (new Set(items.map(item => item.id)).size !== items.length) throw Error(`Duplicate ${name} id`);
}

export function validateArtifact(value) {
 if (!value || value.schemaVersion !== 1 || !['graph','layers'].includes(value.kind)) throw Error('Invalid artifact schema');
 if (!['synthetic-design','canvas-snapshot'].includes(value.provenance?.kind)) throw Error('Invalid provenance');
 const layers = list(value.layers, 20, 'layers').map(layer => ({id:id(layer.id),label:text(layer.label,160,'layer label'),order:finite(layer.order)}));
 if (!layers.length) throw Error('At least one layer is required');
 unique(layers,'layer');
 const layerIds = new Set(layers.map(layer=>layer.id));
 const nodes = list(value.nodes,100,'nodes').map(node => {
  if (!layerIds.has(node.layer)) throw Error('Invalid node layer');
  const result = {id:id(node.id),label:text(node.label,160,'node label'),layer:node.layer,position:{x:finite(node.position?.x),y:finite(node.position?.y)}};
  if (node.description !== undefined) result.description=text(node.description,1200,'description');
  return result;
 });
 unique(nodes,'node');
 const nodeIds = new Set(nodes.map(node=>node.id));
 const edges = list(value.edges,500,'edges').map(edge => {
  if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target) || !['data','membership','feedback'].includes(edge.kind)) throw Error('Invalid edge');
  return {id:id(edge.id),source:edge.source,target:edge.target,kind:edge.kind};
 });
 unique(edges,'edge');
 return {schemaVersion:1,kind:value.kind,title:text(value.title,200,'title'),provenance:{kind:value.provenance.kind,label:text(value.provenance.label,300,'provenance label')},layers,nodes,edges};
}

export function createDesignArtifact() {
 const steps = [
  ['intent','Intent','Describe the desired outcome.'],
  ['requirements','Requirements','Make constraints and acceptance criteria explicit.'],
  ['resolve','Resolve','Resolve terms and available definition identities.'],
  ['select','Select','Propose components against requirements.'],
  ['compose','Compose','Propose compatible connections and boundaries.'],
  ['check','Check','Inspect proposed structure and outstanding uncertainty.'],
  ['promote','Promote','Propose a reusable composite after evidence review.'],
  ['reassess','Reassess','Reconsider the design against new evidence.'],
 ];
 return validateArtifact({schemaVersion:1,kind:'graph',title:'Proposed composition design',provenance:{kind:'synthetic-design',label:'Conceptual proposal only; not an implemented or proven algorithm.'},layers:[{id:'design',label:'Proposed reasoning stages',order:0}],nodes:steps.map(([id,label,description],index)=>({id,label,description,layer:'design',position:{x:(index%4)*240,y:Math.floor(index/4)*190}})),edges:[...steps.slice(1).map(([target],index)=>({id:`data-${index}`,source:steps[index][0],target,kind:'data'})),{id:'feedback-requirements',source:'reassess',target:'requirements',kind:'feedback'},{id:'feedback-select',source:'check',target:'select',kind:'feedback'}]});
}

export function createLayerArtifact() {
 return validateArtifact({schemaVersion:1,kind:'layers',title:'Shared components within a composite',provenance:{kind:'synthetic-design',label:'Synthetic structural example; no live agent or execution.'},layers:[{id:'components',label:'Components',order:0},{id:'composite',label:'Composite',order:1}],nodes:[{id:'receive',label:'Receive',layer:'components',position:{x:0,y:0}},{id:'process',label:'Process',layer:'components',position:{x:240,y:0}},{id:'respond',label:'Respond',layer:'components',position:{x:480,y:0}},{id:'summary-composite',label:'Summary composite',layer:'composite',position:{x:240,y:220}}],edges:[{id:'receive-process',source:'receive',target:'process',kind:'data'},{id:'process-respond',source:'process',target:'respond',kind:'data'},...['receive','process','respond'].map(source=>({id:`member-${source}`,source,target:'summary-composite',kind:'membership'}))]});
}

export function captureCanvasArtifact(graph) {
 // Only exact public component type names may become labels. Never copy native
 // definitions, arbitrary labels, handles or settings into a snapshot.
 const sourceNodes=list(graph?.nodes,100,'nodes');
 const sourceEdges=list(graph?.edges,500,'edges');
 const ids=new Map();
 const nodes=sourceNodes.map((node,index)=>{
  if (typeof node.id !== 'string' || ids.has(node.id)) throw Error('Invalid canvas node identity');
  const safeId=`canvas-node-${index+1}`; ids.set(node.id,safeId);
  const publicLabels={ChatInput:'Chat Input',Agent:'Agent',ChatOutput:'Chat Output'};
  const nativeType=node.data?.type;
  const label=Object.hasOwn(publicLabels,nativeType)?publicLabels[nativeType]:`Node ${index+1}`;
  return {id:safeId,label,layer:'canvas',position:{x:node.position?.x,y:node.position?.y}};
 });
 const edgeIds=new Set();
 const edges=sourceEdges.map((edge,index)=>{
  if (typeof edge.id!=='string' || edgeIds.has(edge.id)) throw Error('Invalid canvas edge identity');
  edgeIds.add(edge.id);
  return {id:`canvas-edge-${index+1}`,source:ids.get(edge.source),target:ids.get(edge.target),kind:'data'};
 });
 return validateArtifact({schemaVersion:1,kind:'graph',title:'Canvas topology snapshot',provenance:{kind:'canvas-snapshot',label:'Topology only; neutral identifiers and labels; no execution evidence.'},layers:[{id:'canvas',label:'Canvas',order:0}],nodes,edges});
}
