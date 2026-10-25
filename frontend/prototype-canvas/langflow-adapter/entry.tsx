import React, {useEffect} from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter} from 'react-router-dom';
import {QueryClientProvider} from '@tanstack/react-query';
import {ReactFlow, ReactFlowProvider, Background} from '@xyflow/react';
import CanvasControls from '@/components/core/canvasControlsComponent/CanvasControls';
import {AssistantPanel} from '@/components/core/assistantPanel';
import {SidebarProvider} from '@/components/ui/sidebar';
import useAssistantManagerStore from '@/stores/assistantManagerStore';
import {MIN_ZOOM,MAX_ZOOM} from '@/components/core/canvasControlsComponent/fit-view-options';
import {nodeTypes,edgeTypes} from '@/pages/FlowPage/consts';
import {NOTE_NODE_MIN_HEIGHT,NOTE_NODE_MIN_WIDTH} from '@/constants/constants';
import {computeNoteScreenPosition} from '@/pages/FlowPage/components/PageComponent/utils/compute-note-position';
import useFlowStore from '@/stores/flowStore';
import useFlowsManagerStore from '@/stores/flowsManagerStore';
import {useDarkStore} from '@/stores/darkStore';
import {useTypesStore} from '@/stores/typesStore';
import {queryClient} from '@/contexts';
import {TooltipProvider} from '@/components/ui/tooltip';
import '@/i18n';
import classes from '@/style/classes.css?inline';
import theme from '@/style/index.css?inline';
import app from '@/App.css?inline';
import applies from '@/style/applies.css?inline';
import flowCss from '@xyflow/react/dist/style.css?inline';

export async function mount(element:HTMLElement){
 const shadow=element;
 shadow.replaceChildren();
 const extraCss=await fetch('/langflow-native/langflow.css').then(r=>r.text());
 const style=document.createElement('style');
 style.textContent='@scope (.v2-native-surface) {'+[classes,theme,app,applies,flowCss,extraCss,'.native-root{height:100%;width:100%;background:hsl(var(--background));color:hsl(var(--foreground))}'].join('\n')+'}';
 shadow.append(style);
 // Original Radix controls portal into document.body. Supply their unchanged
 // styles only inside those portal roots, leaving our library and V1 alone.
 const portalStyle=document.createElement('style');
 portalStyle.textContent='@scope (body:has(> .native-langflow-portal)) to (#root) {'+[classes,theme,app,applies,flowCss,extraCss].join('\n')+' .native-langflow-portal{font-family:Inter,system-ui,sans-serif;--font-sans:Inter,sans-serif;--font-mono:"JetBrains Mono",monospace}}';
 document.head.append(portalStyle);
 const stylePortal=(child:Element)=>{
  if(child instanceof HTMLElement && (child.classList.contains('noflow') || child.hasAttribute('data-radix-popper-content-wrapper'))){child.classList.add('native-langflow-portal','dark');}
 };
 const portalObserver=new MutationObserver(records=>{for(const record of records)for(const child of record.addedNodes)if(child instanceof Element)stylePortal(child);});
 portalObserver.observe(document.body,{childList:true});
 for(const child of document.body.children)stylePortal(child);
 const host=document.createElement('body');host.className='native-root dark';host.id='body';shadow.append(host);
 const root=createRoot(host);
 let response=await fetch('/api/v1/all',{credentials:'include'});
 if(response.status===401||response.status===403){
  const refreshed=await fetch('/api/v1/refresh',{method:'POST',credentials:'include'});
  if(refreshed.ok)response=await fetch('/api/v1/all',{credentials:'include'});
 }
 if(!response.ok)throw new Error('Langflow component catalog unavailable ('+response.status+').');
 const catalog=await response.json();
 delete catalog.component_display_names;
 useTypesStore.getState().setTypes(catalog);
 const definitions=Object.fromEntries(Object.values(catalog).flatMap((group:any)=>Object.entries(group).filter(([,definition]:any)=>definition?.template)));
 const supportedTypes=Object.keys(definitions);
 const saved=await fetch('/api/v1/flows/42232ff0-2ef7-46f2-bd61-6151e88cd5e5',{credentials:'include'});
 if(!saved.ok)throw new Error('Langflow flow unavailable ('+saved.status+').');
 const flow=await saved.json();
 useFlowStore.getState().setCurrentFlow(flow);
 useFlowsManagerStore.setState({currentFlowId:flow.id,currentFlow:flow});
 useDarkStore.setState({dark:true});
 useFlowStore.setState({nodes:flow.data?.nodes??[],edges:flow.data?.edges??[]});
 function Canvas(){
  const assistantOpen=useAssistantManagerStore(s=>s.assistantSidebarOpen);
  const setAssistantOpen=useAssistantManagerStore(s=>s.setAssistantSidebarOpen);
  useEffect(()=>{
   const addNote=()=>{
    const toolbar=shadow.querySelector('[data-testid="main_canvas_controls"]');
    const screen=computeNoteScreenPosition(toolbar?.getBoundingClientRect());
    const id='note-'+crypto.randomUUID();
    useFlowStore.getState().setNodes(nodes=>[...nodes,{id,type:'noteNode',position:controller.instance?.screenToFlowPosition(screen)??{x:300,y:300},width:NOTE_NODE_MIN_WIDTH,height:NOTE_NODE_MIN_HEIGHT,selected:false,data:{id,type:'note',node:{description:'',display_name:'',documentation:'',template:{}}}}]);
    window.dispatchEvent(new Event('lf:end-add-note'));
   };
   window.addEventListener('lf:start-add-note',addNote);
   return ()=>window.removeEventListener('lf:start-add-note',addNote);
  },[]);
  const nodes=useFlowStore(s=>s.nodes),edges=useFlowStore(s=>s.edges);
  const onNodesChange=useFlowStore(s=>s.onNodesChange),onEdgesChange=useFlowStore(s=>s.onEdgesChange),onConnect=useFlowStore(s=>s.onConnect);
  return <><AssistantPanel isOpen={assistantOpen} onClose={()=>setAssistantOpen(false)}/><ReactFlow minZoom={MIN_ZOOM} maxZoom={MAX_ZOOM} nodes={nodes} edges={edges} defaultViewport={flow.data?.viewport} nodeTypes={nodeTypes} edgeTypes={edgeTypes} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} colorMode="dark" onInit={instance=>{controller.instance=instance;useFlowStore.getState().setReactFlowInstance(instance);}} onDragOver={e=>{if(e.dataTransfer.types.includes('application/x-langflow-component')){e.preventDefault();e.dataTransfer.dropEffect='copy';}}} onDrop={e=>{e.preventDefault();const type=e.dataTransfer.getData('application/x-langflow-component');if(supportedTypes.includes(type))controller.add(type,{x:e.clientX,y:e.clientY});}}><Background/><CanvasControls selectedNode={nodes.find(node=>node.selected)??null}/></ReactFlow></>;
 }
 const controller:any={instance:null,clear(){useAssistantManagerStore.getState().setAssistantSidebarOpen(false);useFlowStore.setState({nodes:[],edges:[]});},restore(graph:any){useFlowStore.setState({nodes:structuredClone(graph.nodes),edges:structuredClone(graph.edges)});controller.instance?.setViewport(graph.viewport);},snapshot(){const state=useFlowStore.getState();return structuredClone({nodes:state.nodes,edges:state.edges,viewport:controller.instance?.getViewport()??{x:0,y:0,zoom:1}});},add(type:string,point?:{x:number,y:number}){
  if(!definitions[type])throw new Error('This component is unavailable in the connected Langflow catalog: '+type);
  const bounds=element.getBoundingClientRect();
  const position=controller.instance?.screenToFlowPosition(point??{x:bounds.x+bounds.width/2,y:bounds.y+bounds.height/2})??{x:300,y:200};
  const id=type+'-'+crypto.randomUUID();
  useFlowStore.getState().setNodes(nodes=>[...nodes,{id,type:'genericNode',position,data:{id,type,node:structuredClone(definitions[type])}}]);
 },unmount(){root.unmount();portalObserver.disconnect();portalStyle.remove();shadow.replaceChildren();}};
 root.render(<BrowserRouter><QueryClientProvider client={queryClient}><TooltipProvider><ReactFlowProvider><SidebarProvider defaultOpen={false} className="h-full min-h-0" style={{height:"100%",minHeight:0}}><Canvas/></SidebarProvider></ReactFlowProvider></TooltipProvider></QueryClientProvider></BrowserRouter>);
 return controller;
}
