import IntentInstance from './intent-instance.jsx';
import Research from './research-native.jsx';
import LayerMapThree from './layer-map-three.jsx';
import {CompositeCard} from './layer-map.jsx';
import {packageAssembly,compositeNode,canConnectComposite} from './layer-assembly.mjs';
import ContextExplorer from './context-explorer.jsx';
import React, {useEffect,useRef,useState} from 'react';
import {ReactFlow,Background,Controls,addEdge,applyNodeChanges,applyEdgeChanges} from '@xyflow/react';
import V3Library from './v3-library.jsx';
import {parseFlowImport} from './langflow-adapter/import-flow.mjs';
import MachineSequence from './machine-sequence.jsx';
import catalog from './v3-catalog.json';
import officialTemplates from './official-templates.json';
import swiftTemplate from './components/swift-definition.json';
import {buildSystemContext,readContextCheckpoints,checkpointSummaries,saveContextCheckpoint,createContextChannel} from './system-context.mjs';
import './system-context.css';
import './v3-canvas.css';

const planes=['Confederations','Federation','Alliances','Ecosystems','Enterprises','Operations','Programs','Processes','Flows','Composite Components','Components'];
const planeLabel=plane=>plane==='Composite Components'?'Composite':plane;
const storageKey='swarms.v3.custom-library.v1';
const emptyGraph=()=>({nodes:[],edges:[],viewport:{x:0,y:0,zoom:1}});
function readLibrary(){
 try{const raw=localStorage.getItem(storageKey);if(!raw)return {items:[]};const saved=JSON.parse(raw);if(saved.schemaVersion!==1||!Array.isArray(saved.items)||saved.items.some(item=>!item.id||!item.name||!planes.includes(item.plane)||!Array.isArray(item.assembly?.nodes)||!Array.isArray(item.assembly?.edges)))throw Error();return saved;}
 catch{return {items:[],error:'Saved custom library could not be read. Existing storage has been preserved; saving is disabled.'};}
}
const planeNodeTypes={compositeNode:CompositeCard};
function PlaneSurface({plane,graph,onChange,onDropItem,onReady,onOpenComposite,onError}){
 const instance=useRef(null);
 return <ReactFlow nodes={graph.nodes} edges={graph.edges} nodeTypes={planeNodeTypes} onNodeDoubleClick={(_,node)=>{if(node.type==='compositeNode')onOpenComposite?.(node.data.customItemId);}} defaultViewport={graph.viewport} onInit={flow=>{instance.current=flow;onReady?.(flow);}} onMoveEnd={(_,viewport)=>onChange(old=>({...old,viewport}))} onNodesChange={changes=>onChange(old=>({...old,nodes:applyNodeChanges(changes,old.nodes)}))} onEdgesChange={changes=>onChange(old=>({...old,edges:applyEdgeChanges(changes,old.edges)}))} onConnect={connection=>{try{if(plane==='Composite Components')canConnectComposite(graph.nodes,graph.edges,connection);onChange(old=>({...old,edges:addEdge(connection,old.edges)}));}catch(cause){onError?.(cause.message);}}} onDragOver={event=>{if((event.dataTransfer.types.includes('application/x-canvas-custom')||event.dataTransfer.types.includes('application/x-langflow-component'))){event.preventDefault();event.dataTransfer.dropEffect='copy';}}} onDrop={event=>{event.preventDefault();if(event.dataTransfer.getData('application/x-langflow-component')){onError?.('Components can only be placed on Components. Swift belongs on Composite; its placement and expansion are not available yet.');return;}onDropItem(event.dataTransfer.getData('application/x-canvas-custom'),plane,instance.current?.screenToFlowPosition({x:event.clientX,y:event.clientY}));}} colorMode="dark"><Background/><Controls/></ReactFlow>;
}
export default function VersionThree(){
 const surface=useRef(null),native=useRef(null),importInput=useRef(null),layerSurface=useRef(null);
 const [importBackup,setImportBackup]=useState(null);
 const [view,setView]=useState(()=>new URLSearchParams(window.location.search).get('view')==='instance'?'instance':'nodes');
 const [purposefulInstance,setPurposefulInstance]=useState(null);
 useEffect(()=>{const url=new URL(window.location.href);if(view==='instance')url.searchParams.set('view','instance');else url.searchParams.delete('view');window.history.replaceState(window.history.state,'',url);},[view]);
 const [layerSelection,setLayerSelection]=useState([]),[openedComposite,setOpenedComposite]=useState(null);
 const [instanceTarget,setInstanceTarget]=useState(null);
 const [libraryOpen,setLibraryOpen]=useState(true),[saveOpen,setSaveOpen]=useState(false);
 const [chatState,setChatState]=useState({open:false,available:false});
 const [instancePositions,setInstancePositions]=useState({});
 const planeControllers=useRef({}),savePanel=useRef(null);
 const [jsonView,setJsonView]=useState('');
 const [nativeRevision,setNativeRevision]=useState(0);
 const [contextState,setContextState]=useState(null),[contextError,setContextError]=useState('');
 const contextCache=useRef({signature:null,revision:0,manifest:null});
 const [contextChannel]=useState(createContextChannel);
 useEffect(()=>{
  window.v3SystemContext=contextChannel.reader;
  return ()=>{if(window.v3SystemContext===contextChannel.reader)delete window.v3SystemContext;contextChannel.clear();};
 },[contextChannel]);
 const [checkpointStore,setCheckpointStore]=useState(()=>{try{return readContextCheckpoints(localStorage);}catch(cause){return {schemaVersion:1,checkpoints:[],error:cause.message};}});

 const [openingTemplate,setOpeningTemplate]=useState(false);
 const [activePlane,setActivePlane]=useState('Components');
 const [initialLibrary]=useState(readLibrary);
 const [customItems,setCustomItems]=useState(initialLibrary.items);
 const [graphs,setGraphs]=useState({});
 const [cleared,setCleared]=useState({});
 const [name,setName]=useState(''),[saveMessage,setSaveMessage]=useState('');
 const [error,setError]=useState(''),[ready,setReady]=useState(false);
 const higherPlane=planes[planes.indexOf(activePlane)-1];
 useEffect(()=>{
  let cancelled=false;let unsubscribeContext=()=>{};
  import(/* @vite-ignore */ window.location.origin+'/langflow-native-v3/adapter.js').then(async module=>{
   if(cancelled)return;
   const controller=await module.mount(surface.current);
   if(cancelled)controller.unmount();else{native.current=controller;unsubscribeContext=controller.subscribeContext?.(()=>{if(!cancelled)setNativeRevision(value=>value+1);})??(()=>{});setReady(true);}
  }).catch(e=>{if(!cancelled)setError(e.message);});
  return ()=>{cancelled=true;unsubscribeContext();native.current?.unmount();native.current=null;};
 },[]);
 useEffect(()=>{
  const deployed=()=>setSaveMessage('Swift instance created. Chat is ready.');
  const failed=event=>setSaveMessage('Swift assembly failed: '+event.detail);
  const chat=event=>setChatState(event.detail);
  const placement=event=>setSaveMessage(event.detail);
  window.addEventListener('v3:placement-error',placement);
  window.addEventListener('v3:chat-state',chat);
  window.addEventListener('swift:deployed',deployed);window.addEventListener('swift:error',failed);
  return ()=>{window.removeEventListener('v3:placement-error',placement);window.removeEventListener('v3:chat-state',chat);window.removeEventListener('swift:deployed',deployed);window.removeEventListener('swift:error',failed);};
 },[]);
 function captureSystemContext(){
  const graph=native.current?.inspect?.()??{nodes:[],edges:[],viewport:{x:0,y:0,zoom:1}};
  const baseContext=buildSystemContext({planes,catalog,officialTemplates,swiftTemplate,customItems,nativeGraph:graph,planeGraphs:graphs,instancePositions,activePlane,nativeContext:native.current?.inspectContext?.()??{},checkpointMetadata:checkpointSummaries(checkpointStore),assemblyName:name});
  const next={...baseContext,purposefulInstance};
  const signature=JSON.stringify(next);
  if(contextCache.current.signature!==signature){
   const revision=contextCache.current.revision+1;
   const manifest={...next,workingRevision:revision,updatedAt:new Date().toISOString()};
   const serialized=JSON.stringify(manifest,null,2);
   contextCache.current={signature,revision,manifest};contextChannel.publish(manifest);setContextState(manifest);setJsonView(serialized);
  }
  setContextError('');return contextCache.current.manifest;
 }
 useEffect(()=>{
  const timer=setTimeout(()=>{try{captureSystemContext();}catch{setContextError('Live system context could not be refreshed. The previous view has been retained.');}},80);
  return ()=>clearTimeout(timer);
 },[ready,nativeRevision,activePlane,graphs,instancePositions,customItems,checkpointStore,name,purposefulInstance]);
 function saveContext(){
  try{
   const manifest=captureSystemContext();
   const saved=saveContextCheckpoint(localStorage,manifest);
   setCheckpointStore(saved.store);setSaveMessage('Saved context checkpoint v'+saved.checkpoint.version+' in this browser.');
  }catch{setContextError('Context checkpoint could not be saved. Previous checkpoints remain intact.');}
 }
 useEffect(()=>{
  const frame=requestAnimationFrame(()=>{
   const root=view==='layers'?layerSurface.current:(activePlane==='Components'?surface.current:document.querySelector('[aria-label="'+activePlane+' plane"]'));
   setInstanceTarget(root?.querySelector('.react-flow__viewport')??null);
  });
  return ()=>cancelAnimationFrame(frame);
 },[activePlane,ready,view]);
 useEffect(()=>{
  if(!saveOpen)return;
  const outside=event=>{if(!savePanel.current?.contains(event.target)&&!event.target.closest('[data-save-toggle]'))setSaveOpen(false);};
  const escape=event=>{if(event.key==='Escape')setSaveOpen(false);};
  document.addEventListener('pointerdown',outside);document.addEventListener('keydown',escape);
  return ()=>{document.removeEventListener('pointerdown',outside);document.removeEventListener('keydown',escape);};
 },[saveOpen]);
 const instancePosition=instancePositions[activePlane]??{x:32,y:96};
 const moveInstance=position=>setInstancePositions(old=>({...old,[activePlane]:position}));
 useEffect(()=>{window.dispatchEvent(new CustomEvent('v3:instance-layout',{detail:instancePosition}));},[instancePosition.x,instancePosition.y,ready]);
 const fitCanvas=()=>{if(view==='layers')planeControllers.current.layers?.fitView({padding:.15,duration:200});else if(activePlane==='Components')native.current?.fit?.();else planeControllers.current[activePlane]?.fitView({padding:.2,duration:200});};
 const changePlane=plane=>{setActivePlane(plane);setSaveMessage('');};
 const updateGraph=(plane,change)=>setGraphs(old=>({...old,[plane]:change(old[plane]??emptyGraph())}));
 function placeSwift(target='Composite Components',position){
  if(target!=='Composite Components'){setSaveMessage('Swift belongs on Composite, not '+planeLabel(target)+'.');return;}
  try{
   const instance=native.current.planSwift();
   const children=instance.data.nodes.map(node=>node.id);
   const item=packageAssembly(instance.data,children,'Swift',{id:instance.id});
   item.templateRef=instance.templateRef;
   native.current.appendAssembly(instance.data);
   setCustomItems(old=>[...old,item]);
   updateGraph('Composite Components',old=>({...old,nodes:[...old.nodes,compositeNode(item,{position:position??{x:360+old.nodes.length*280,y:160}})]}));
   setLayerSelection([]);changePlane('Composite Components');setView('layers');
   setSaveMessage('Swift placed on Composite · 3 real components and 2 connections expanded below. Design assembled; not deployed.');
  }catch(cause){setSaveMessage('Could not assemble Swift: '+cause.message);}
 }
 function addCustom(item,position){
  if(item.id==='swift-template'){placeSwift('Composite Components',position);return;}
  changePlane(item.plane);
  updateGraph(item.plane,old=>({...old,nodes:[...old.nodes,item.kind==='composite-definition'?compositeNode(item,{position:position??{x:360+old.nodes.length*280,y:180}}):{id:crypto.randomUUID(),type:'default',position:position??{x:350+old.nodes.length*35,y:220+old.nodes.length*35},data:{label:item.name,customItemId:item.id}}]}));
 }
 function openComposite(item){
  if(!item)return;
  const graph=native.current?.inspect();
  const memberIds=item.realization?.childNodeIds??item.assembly.nodes.map(node=>node.id);
  if(!memberIds.every(id=>graph?.nodes.some(node=>node.id===id))){setSaveMessage('These saved internals are not on the current Components plane. Import the saved assembly before opening it here.');return;}
  setOpenedComposite(item);changePlane('Components');setView('nodes');
  requestAnimationFrame(()=>native.current?.focus(memberIds));
  setSaveMessage('Viewing the same components used by “'+item.name+'”.');
 }
 async function openOfficialTemplate(item){
  if(!ready||openingTemplate)return;
  setOpeningTemplate(true);setSaveMessage('Opening “'+item.name+'”…');
  try{
   const response=await fetch(item.file);if(!response.ok)throw Error('Template download failed ('+response.status+').');
   const bytes=await response.arrayBuffer();
   const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
   if(digest!==item.source.sha256)throw Error('Template integrity check failed.');
   const flow=parseFlowImport(new TextDecoder().decode(bytes));
   const backup=native.current.snapshot();native.current.importFlow(flow.data);
   setImportBackup({graph:backup,name});changePlane('Components');setName(item.name);
   setSaveMessage('Opened official template “'+item.name+'” · unverified. Configure its resources before running. Undo import restores the previous graph.');
  }catch(cause){setSaveMessage('Could not open template: '+cause.message);}
  finally{setOpeningTemplate(false);}
 }
 async function importFlow(event){
  const file=event.target.files?.[0];if(!file)return;
  try{
   const flow=parseFlowImport(await file.text());
   const backup=native.current.snapshot();
   native.current.importFlow(flow.data);
   setImportBackup({graph:backup,name});changePlane('Components');setName(flow.name);
   setSaveMessage('Loaded “'+flow.name+'”: '+flow.data.nodes.length+' items, '+flow.data.edges.length+' connections.');
  }catch(cause){setSaveMessage('Import failed: '+cause.message);}
  finally{event.target.value='';}
 }
 function undoImport(){
  if(!importBackup)return;
  native.current.importFlow(importBackup.graph);setName(importBackup.name);setImportBackup(null);changePlane('Components');setSaveMessage('Previous canvas restored.');
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
   const ids=layerSelection.length?layerSelection:graph.nodes.filter(node=>node.selected&&node.type==='genericNode').map(node=>node.id);
   const members=ids.length?ids:graph.nodes.filter(node=>node.type==='genericNode').map(node=>node.id);
   const item=activePlane==='Components'?packageAssembly(graph,members,title):{id:crypto.randomUUID(),name:title,plane:higherPlane,sourcePlane:activePlane,createdAt:new Date().toISOString(),status:'design-saved',assembly:structuredClone(graph),dependencies:customItems.filter(entry=>usedIds.has(entry.id))};
   const next=[...customItems,item];
   localStorage.setItem(storageKey,JSON.stringify({schemaVersion:1,items:next}));
   setCustomItems(next);if(item.kind==='composite-definition'){updateGraph('Composite Components',old=>({...old,nodes:[...old.nodes,compositeNode(item,{position:{x:360+old.nodes.length*280,y:160}})]}));setView('layers');setLayerSelection(members);}setName('');setSaveOpen(false);setSaveMessage('Saved “'+title+'” in '+higherPlane+' → Custom.');
  }catch(cause){setSaveMessage(cause.message??'Could not save locally. Your canvas is unchanged.');}
 }
 const componentGraph=native.current?.inspect?.()??emptyGraph();
 const upperGraph=graphs['Composite Components']??emptyGraph();
 return <main className="v3-canvas" style={{'--library-width':(view==='research'||view==='instance')?'0px':libraryOpen?'248px':'0px'}}>
  <header className="workbench-toolbar" aria-label="Workbench toolbar">
   <button type="button" className="toolbar-library-toggle" aria-expanded={libraryOpen} onClick={()=>setLibraryOpen(value=>!value)}>Library</button>
   <div className="canvas-view-switch" role="group" aria-label="Canvas view"><button type="button" aria-pressed={view==='nodes'} onClick={()=>setView('nodes')}>Nodes</button><button type="button" aria-pressed={view==='layers'} onClick={()=>{changePlane('Components');setView('layers');}}>Layers</button><button type="button" aria-pressed={view==='instance'} onClick={()=>setView('instance')}>Instance</button><button type="button" aria-pressed={view==='json'} onClick={()=>setView('json')}>JSON</button><button type="button" aria-pressed={view==='research'} onClick={()=>setView('research')}>Research</button></div>
   <div className="toolbar-actions" style={{display:(view==='research'||view==='instance')?'none':undefined}}>
    <button type="button" disabled={!ready||view==='json'} onClick={fitCanvas}>Fit view</button>
    <button type="button" disabled={!ready} onClick={()=>importInput.current.click()}>Import</button>
    <button type="button" onClick={clearCanvas} disabled={activePlane==='Components'&&!ready}>Clear</button>
    {cleared[activePlane]&&<button type="button" onClick={undoClear}>Undo clear</button>}
    {importBackup&&<button type="button" onClick={undoImport}>Undo import</button>}
    <button type="button" data-save-toggle aria-expanded={saveOpen} disabled={!higherPlane||!ready} onClick={()=>setSaveOpen(value=>!value)}>Save assembly</button>
    <button type="button" disabled={!chatState.available||view!=='nodes'} aria-pressed={chatState.open} onClick={()=>native.current?.toggleChat?.()}>Chat</button>
    <MachineSequence/>
   </div>
  </header>
  <div className="canvas-workspace">
   <div className="v3-native-surface" ref={surface} style={{display:activePlane==='Components'&&view==='nodes'?'block':'none'}}/>
   {planes.filter(plane=>plane!=='Components').map(plane=><section key={plane} className="v3-plane-surface" hidden={activePlane!==plane||view!=='nodes'} aria-label={plane+' plane'}><PlaneSurface plane={plane} graph={graphs[plane]??emptyGraph()} onChange={change=>updateGraph(plane,change)} onReady={controller=>{planeControllers.current[plane]=controller;}} onOpenComposite={id=>openComposite(customItems.find(item=>item.id===id))} onError={setSaveMessage} onDropItem={(id,target,position)=>{if(id==='swift-template'){placeSwift(target,position);return;}const item=customItems.find(entry=>entry.id===id);if(!item)return;if(item.plane!==target){setSaveMessage('“'+item.name+'” belongs on '+(item.plane==='Composite Components'?'Composite':item.plane)+', not '+(target==='Composite Components'?'Composite':target)+'.');return;}addCustom(item,position);}}/></section>)}
   {view==='research'&&<Research/>}
   {view==='instance'&&<IntentInstance onDocumentChange={setPurposefulInstance}/>}
   {view==='layers'&&<section className="v3-layer-surface" ref={layerSurface} aria-label="Two-layer DAG"><LayerMapThree onDropItem={(id,target)=>{if(id==='swift-template'){placeSwift(target);return;}const item=customItems.find(entry=>entry.id===id);if(item&&item.plane===target)addCustom(item);else setSaveMessage('This item belongs on '+planeLabel(item?.plane??'Components')+', not '+planeLabel(target)+'.');}} onError={setSaveMessage} graph={componentGraph} upperGraph={upperGraph} items={customItems} selectedIds={layerSelection} onSelect={setLayerSelection} onPackage={()=>{changePlane('Components');setSaveOpen(true);}} onOpen={openComposite} onReady={controller=>{planeControllers.current.layers=controller;setInstanceTarget(layerSurface.current?.querySelector('.react-flow__viewport')??null);}}/></section>}
   {openedComposite&&view==='nodes'&&activePlane==='Components'&&<div className="drilldown-banner"><button onClick={()=>{setOpenedComposite(null);setView('layers');}}>Back to layers</button><span>{openedComposite.name} · same component identities</span></div>}
   {error&&view!=='research'&&view!=='instance'&&activePlane==='Components' &&<div role="alert" className="v3-native-error">{error}</div>}
   {view==='json'&&<section className="canvas-json-view" aria-label="System context JSON view"><header className="system-context-header"><div><strong>System context · live draft</strong><small>Revision {contextState?.workingRevision??0} · read only · references keep shared resources lightweight</small></div><div><span>{checkpointStore.checkpoints.length?'Saved v'+Math.max(...checkpointStore.checkpoints.map(checkpoint=>checkpoint.version))+' · this browser':'No saved checkpoints'}</span><button type="button" disabled={!contextState||Boolean(checkpointStore.error)} onClick={saveContext}>Save context checkpoint</button></div></header>{(contextError||checkpointStore.error)&&<p className="system-context-error" role="alert">{contextError||checkpointStore.error}</p>}<ContextExplorer value={contextState}/></section>}
  </div>
  <V3Library libraryOpen={libraryOpen&&view!=='research'&&view!=='instance'} onClose={()=>setLibraryOpen(false)} instancePosition={instancePosition} onMoveInstance={moveInstance} instanceTarget={instanceTarget} activePlane={activePlane} onSelectPlane={changePlane} customItems={customItems} onAddCustom={addCustom} onOpenTemplate={openOfficialTemplate} templatesReady={ready&&!openingTemplate} onAddComponent={ready?type=>{changePlane('Components');try{native.current.add(type);setError('');}catch(cause){setError(cause.message);}}:undefined}/>
  <input ref={importInput} type="file" accept=".json,application/json" aria-label="Import Langflow JSON file" hidden onChange={importFlow}/>
  {saveOpen&&<section className="assembly-save" role="dialog" aria-label="Save assembly" ref={savePanel}><header><strong>Save assembly</strong><button type="button" aria-label="Close save panel" onClick={()=>setSaveOpen(false)}>Close</button></header><p>Package this design into {planeLabel(higherPlane)} → Custom.</p><form onSubmit={saveAssembly}><label htmlFor="assembly-name">Assembly name</label><input id="assembly-name" autoFocus value={name} onChange={event=>setName(event.target.value)} placeholder="Name your assembly" maxLength={120}/><button type="submit" disabled={Boolean(initialLibrary.error)}>Save to {planeLabel(higherPlane)}</button></form></section>}
  <footer className="workbench-status" role="status">{view==='instance'?'Instance design · revisioned JSON · no deployment':saveMessage||initialLibrary.error||(ready?'Ready · '+planeLabel(activePlane):'Connecting to Langflow…')}</footer>
 </main>;
}
