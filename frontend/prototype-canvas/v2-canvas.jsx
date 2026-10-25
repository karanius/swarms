import React, {useEffect,useRef,useState} from 'react';
import {ReactFlow,Background,Controls,addEdge,applyNodeChanges,applyEdgeChanges} from '@xyflow/react';
import V2Library from './v2-library.jsx';
import MachineSequence from './machine-sequence.jsx';
import './v2-canvas.css';

const planes=['Confederations','Federation','Alliances','Ecosystems','Enterprises','Operations','Programs','Processes','Flows','Composite Components','Components'];
const storageKey='swarms.v2.custom-library.v1';
const emptyGraph=()=>({nodes:[],edges:[],viewport:{x:0,y:0,zoom:1}});
function readLibrary(){
 try{const raw=localStorage.getItem(storageKey);if(!raw)return {items:[]};const saved=JSON.parse(raw);if(saved.schemaVersion!==1||!Array.isArray(saved.items)||saved.items.some(item=>!item.id||!item.name||!planes.includes(item.plane)||!Array.isArray(item.assembly?.nodes)||!Array.isArray(item.assembly?.edges)))throw Error();return saved;}
 catch{return {items:[],error:'Saved custom library could not be read. Existing storage has been preserved; saving is disabled.'};}
}
function PlaneSurface({plane,graph,onChange,onDropItem}){
 const instance=useRef(null);
 return <ReactFlow nodes={graph.nodes} edges={graph.edges} defaultViewport={graph.viewport} onInit={flow=>{instance.current=flow;}} onMoveEnd={(_,viewport)=>onChange(old=>({...old,viewport}))} onNodesChange={changes=>onChange(old=>({...old,nodes:applyNodeChanges(changes,old.nodes)}))} onEdgesChange={changes=>onChange(old=>({...old,edges:applyEdgeChanges(changes,old.edges)}))} onConnect={connection=>onChange(old=>({...old,edges:addEdge(connection,old.edges)}))} onDragOver={event=>{if(event.dataTransfer.types.includes('application/x-canvas-custom')){event.preventDefault();event.dataTransfer.dropEffect='copy';}}} onDrop={event=>{event.preventDefault();onDropItem(event.dataTransfer.getData('application/x-canvas-custom'),plane,instance.current?.screenToFlowPosition({x:event.clientX,y:event.clientY}));}} colorMode="dark"><Background/><Controls/></ReactFlow>;
}
export default function VersionTwo(){
 const surface=useRef(null),native=useRef(null);
 const [activePlane,setActivePlane]=useState('Components');
 const [initialLibrary]=useState(readLibrary);
 const [customItems,setCustomItems]=useState(initialLibrary.items);
 const [graphs,setGraphs]=useState({});
 const [cleared,setCleared]=useState({});
 const [name,setName]=useState(''),[saveMessage,setSaveMessage]=useState('');
 const [error,setError]=useState(''),[ready,setReady]=useState(false);
 const higherPlane=planes[planes.indexOf(activePlane)-1];
 useEffect(()=>{
  let cancelled=false;
  import(/* @vite-ignore */ window.location.origin+'/langflow-native/adapter.js').then(async module=>{
   if(cancelled)return;
   const controller=await module.mount(surface.current);
   if(cancelled)controller.unmount();else{native.current=controller;setReady(true);}
  }).catch(e=>{if(!cancelled)setError(e.message);});
  return ()=>{cancelled=true;native.current?.unmount();native.current=null;};
 },[]);
 const changePlane=plane=>{setActivePlane(plane);setSaveMessage('');};
 const updateGraph=(plane,change)=>setGraphs(old=>({...old,[plane]:change(old[plane]??emptyGraph())}));
 function addCustom(item,position){
  changePlane(item.plane);
  updateGraph(item.plane,old=>({...old,nodes:[...old.nodes,{id:crypto.randomUUID(),type:'default',position:position??{x:350+old.nodes.length*35,y:220+old.nodes.length*35},data:{label:item.name,customItemId:item.id}}]}));
 }
 function clearCanvas(){
  const graph=activePlane==='Components'?native.current?.snapshot():graphs[activePlane];
  if(!graph?.nodes?.length&&!graph?.edges?.length){setSaveMessage('This canvas is already empty.');return;}
  setCleared(old=>({...old,[activePlane]:structuredClone(graph)}));
  if(activePlane==='Components')native.current.clear();else updateGraph(activePlane,()=>emptyGraph());
  setSaveMessage('Canvas cleared. Saved library items are unchanged.');
 }
 function undoClear(){
  const graph=cleared[activePlane];if(!graph)return;
  if(activePlane==='Components')native.current.restore(graph);else updateGraph(activePlane,()=>structuredClone(graph));
  setCleared(old=>({...old,[activePlane]:null}));setSaveMessage('Canvas restored.');
 }
 function saveAssembly(event){
  event.preventDefault();
  if(!higherPlane||initialLibrary.error)return;
  const title=name.trim();
  if(!title){setSaveMessage('Give this assembly a name.');return;}
  if(customItems.some(item=>item.plane===higherPlane&&item.name.toLowerCase()===title.toLowerCase())){setSaveMessage('That name already exists in '+higherPlane+'. Choose another name.');return;}
  try{
   const graph=activePlane==='Components'?native.current?.snapshot():graphs[activePlane];
   if(!graph?.nodes?.length){setSaveMessage('Add items to this plane before saving an assembly.');return;}
   const usedIds=new Set(graph.nodes.map(node=>node.data?.customItemId).filter(Boolean));
   const item={id:crypto.randomUUID(),name:title,plane:higherPlane,sourcePlane:activePlane,createdAt:new Date().toISOString(),status:'design-saved',assembly:structuredClone(graph),dependencies:customItems.filter(entry=>usedIds.has(entry.id))};
   const next=[...customItems,item];
   localStorage.setItem(storageKey,JSON.stringify({schemaVersion:1,items:next}));
   setCustomItems(next);setName('');setSaveMessage('Saved “'+title+'” in '+higherPlane+' → Custom.');
  }catch{setSaveMessage('Could not save locally. Browser storage may be full or unavailable. Your canvas is unchanged.');}
 }
 return <main className="v2-canvas"><div className="v2-native-surface" ref={surface} style={{display:activePlane==='Components'?'block':'none'}}/>{planes.filter(plane=>plane!=='Components').map(plane=><section key={plane} className="v2-plane-surface" hidden={activePlane!==plane} aria-label={plane+' plane'}><PlaneSurface plane={plane} graph={graphs[plane]??emptyGraph()} onChange={change=>updateGraph(plane,change)} onDropItem={(id,target,position)=>{const item=customItems.find(entry=>entry.id===id&&entry.plane===target);if(item)addCustom(item,position);}}/></section>)}{error&&activePlane==='Components'&&<div role="alert" className="v2-native-error">{error}</div>}<V2Library activePlane={activePlane} onSelectPlane={changePlane} customItems={customItems} onAddCustom={addCustom} onAddComponent={ready?type=>{changePlane('Components');try{native.current.add(type);setError('');}catch(cause){setError(cause.message);}}:undefined}/><div className="assembly-save"><div className="canvas-clear-controls"><button type="button" onClick={clearCanvas} disabled={activePlane==='Components'&&!ready}>🧹 Clear canvas</button>{cleared[activePlane]&&<button type="button" onClick={undoClear}>Undo clear</button>}</div><form onSubmit={saveAssembly}><label htmlFor="assembly-name">Assembly name</label><div className="assembly-save-fields"><input id="assembly-name" value={name} onChange={event=>setName(event.target.value)} placeholder="Name your assembly" maxLength={120} disabled={!higherPlane}/><button type="submit" disabled={!higherPlane||Boolean(initialLibrary.error)||(activePlane==='Components'&&!ready)}>Save to {higherPlane??'higher plane'}</button></div></form><p className="assembly-save-hint">{higherPlane?'Saved locally under Custom · design only':'This is the highest plane.'}</p>{(saveMessage||initialLibrary.error)&&<p className="assembly-save-message" role="status">{saveMessage||initialLibrary.error}</p>}</div><MachineSequence/></main>;
}
