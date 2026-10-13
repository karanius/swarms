import {WorkspaceModes} from './WorkflowStudio';
import ImageDiscovery from './ImageDiscovery';
import {inputShape,includedSources,composeTask,taskPosition} from './inputComposition';
import InputShapePanel,{inputFields} from './InputShapePanel';
import {LogsProviderNode,LogsInputPanel} from './LogsProvider';
import PipelineWorkspace from './PipelineWorkspace';
import NodeConnections from './NodeConnections';
import BlockNode,{blocks} from './ui/BlockNode';
import LiveLoop from './LiveLoop';
import PatternLibrary from './PatternLibrary';
import {normalizeModelConfig,ModelProfileContext} from './ModelSelect';
import {libraryPresets} from './libraryPresets';
import React, { useCallback, useRef, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { ReactFlow, ReactFlowProvider, Background, Controls, Handle, Position, Panel, MarkerType, useNodesState, useEdgesState, addEdge, useReactFlow } from '@xyflow/react';
import { MagnifyingGlass, Files, ArrowsLeftRight, PencilLine, Stack, ShieldCheck, ArrowClockwise, SquaresFour, GearSix, Cpu, TextAlignLeft, Target, Plug, FlowArrow, Export, Folder, PuzzlePiece } from './ui/icons';
import '@xyflow/react/dist/style.css';
import '@fontsource/geist/400.css';
import '@fontsource/geist/500.css';
import '@fontsource/geist/600.css';
import './style.css';
import ResearchPanel from './ResearchPanel';
import ReadPanel from './ReadPanel';
import ComparePanel from './ComparePanel';
import WritePanel from './WritePanel';
import ParallelPanel from './ParallelPanel';
import SettingsPage from './SettingsPage';
import {initialDefaults,kinds,categories} from './settingsConfig';
import ReviewPanel from './ReviewPanel';
import RepeatPanel from './RepeatPanel';

const exampleNodes = [
  {id:'example-read',kind:1,x:0,y:180},
  {id:'example-parallel',kind:4,x:300,y:180},
  {id:'example-performance',kind:0,x:600,y:60,label:'Research performance'},
  {id:'example-compatibility',kind:0,x:600,y:300,label:'Research compatibility'},
  {id:'example-compare',kind:2,x:900,y:180},
  {id:'example-write',kind:3,x:1200,y:180},
  {id:'example-review',kind:5,x:1500,y:180},
  {id:'example-repeat',kind:6,x:1200,y:460},
].map(({id,kind,x,y,label})=>({id,type:'block',position:{x,y},data:{kind,label}}));
const exampleEdges = [
 ['example-read','example-parallel'],['example-parallel','example-performance'],
 ['example-parallel','example-compatibility'],['example-performance','example-compare'],
 ['example-compatibility','example-compare'],['example-compare','example-write'],
 ['example-write','example-review'],['example-review','example-repeat','Needs evidence'],
 ['example-repeat','example-parallel','Research again'],
].map(([source,target,label],i)=>({id:`example-edge-${i}`,source,target,label,type:'smoothstep',markerEnd:{type:MarkerType.ArrowClosed}}));
const layers=[{name:'Actions',indices:[0,1,2,3]},{name:'Coordination',indices:[4,6]},{name:'Evaluation',indices:[5]}];
const initialNodes = [];
const nodeTypes = { block: BlockNode, logsProvider:LogsProviderNode };
function normalizeNodeModels(n){if(n.type==='logsProvider')return n;const kind=kinds[n.data.kind];return {...n,data:{...n.data,[kind]:normalizeModelConfig(kind,{...initialDefaults[kind],...n.data[kind]})}};}
function loadStored(key,fallback){try{return JSON.parse(localStorage.getItem(key)) || fallback;}catch{return fallback;}}
const failureExperiment={title:'Why did this fail?',nodes:[{id:'failure-logs',type:'logsProvider',position:{x:0,y:120},data:{minutes:1440,errors:true}},{id:'failure-analyst',type:'block',position:{x:420,y:120},data:{kind:0,label:'Why did this fail?',description:'Explain the recorded failure and suggest one next check.',research:{...initialDefaults.research,model_profile:'exo',model_name:'mlx-community/Llama-3.2-3B-Instruct-4bit',reasoning_effort:'',task:'Using only the supplied logs, give three short sections: What failed; What the records show (cite record IDs); One suggested next check. Do not invent a root cause.'}}}],edges:[{id:'failure-context',source:'failure-logs',sourceHandle:'logs',target:'failure-analyst',targetHandle:'logs-context',label:'Logs → Input',type:'smoothstep',data:{logsProvider:true},markerEnd:{type:MarkerType.ArrowClosed}}],inputs:{},outputs:{}};
function uniqueEntries(items){return [...new Map((items||[]).map(item=>[item.id,item])).values()];}
function Canvas({pipeline,pipelineStatus,onSelectPipeline}) {
  const savedCanvas=useRef(loadStored('swarm-canvas-'+pipeline,pipeline==='failure'?failureExperiment:null)).current;
  const removedNodes=useRef(new Set(savedCanvas?.deleted||[]));
  const [defaults,setDefaults]=useState(()=>Object.fromEntries(Object.entries(loadStored('swarm-defaults-v1',initialDefaults)).map(([k,v])=>[k,normalizeModelConfig(k,v)])));
  const [workflows,setWorkflows]=useState(()=>loadStored('swarm-workflows-v1',[]).map(w=>({...w,nodes:w.nodes.map(normalizeNodeModels)})));
  const [profile,setProfile]=useState(()=>localStorage.getItem('swarm-model-profile')||'codex');
  const [exoModels,setExoModels]=useState([]);
  const [exoStatus,setExoStatus]=useState('Loading EXO catalog');
  useEffect(()=>{fetch('/exo-api/v1/models').then(r=>{if(!r.ok)throw Error();return r.json();}).then(d=>{setExoModels(d.data||[]);setExoStatus('');}).catch(()=>setExoStatus('EXO unavailable'));},[]);
  const [templateName,setTemplateName]=useState(()=>savedCanvas?.title||(pipeline==='logs'?'Live log processing pipeline':'Draft canvas'));
  const [settingsOpen,setSettingsOpen]=useState(false);
  const [libraryOpen,setLibraryOpen]=useState(false);
  const [layerIndex,setLayerIndex]=useState(0);
  const swipeStart=useRef(null);
  const trayDrag=useRef(null);
  const suppressTrayClick=useRef(false);
  const libraryTimer=useRef(null);
  const holdLibrary=()=>clearTimeout(libraryTimer.current);
  const closeLibrary=()=>{libraryTimer.current=setTimeout(()=>setLibraryOpen(false),220);};
  useEffect(()=>()=>{clearTimeout(libraryTimer.current);clearTimeout(hoverTimer.current);},[]);
  const [storageError,setStorageError]=useState('');
  useEffect(()=>{try{localStorage.setItem('swarm-defaults-v1',JSON.stringify(defaults));localStorage.setItem('swarm-workflows-v1',JSON.stringify(workflows));setStorageError('');}catch{setStorageError('Browser storage is unavailable. Export your node configurations before closing.');}},[defaults,workflows]);
  const [nodes,setNodes,onNodesChange] = useNodesState((savedCanvas?.nodes||initialNodes).map(normalizeNodeModels));
  const [edges,setEdges,onEdgesChange] = useEdgesState(savedCanvas?.edges||[]);
  const { screenToFlowPosition, fitView } = useReactFlow();
  useEffect(()=>{
    const key='swarm-role-models-v1';
    if(localStorage.getItem(key))return;
    const choices={research:{model_name:'gpt-6.1-sol',reasoning_effort:'high'},compare:{model_name:'gpt-6.1-sol',reasoning_effort:'high'},write:{model_name:'gpt-6-luna',reasoning_effort:'high'},review:{model_name:'gpt-6-astra',reasoning_effort:'medium'}};
    const update=n=>{const kind=kinds[n.data.kind];return choices[kind]?{...n,data:{...n.data,[kind]:{...n.data[kind],...choices[kind]}}}:n;};
    setDefaults(prev=>Object.fromEntries(Object.entries(prev).map(([k,v])=>[k,{...v,...choices[k]}])));
    setNodes(prev=>prev.map(update));
    setWorkflows(prev=>prev.map(w=>({...w,nodes:w.nodes.map(update)})));
    localStorage.setItem(key,'applied');
  },[]);
  useEffect(()=>{
    const key='swarm-library-instructions-v1';
    if(localStorage.getItem(key))return;
    const apply=(kind,config)=>libraryPresets[kind]?{...config,[libraryPresets[kind].field]:libraryPresets[kind].text}:config;
    const update=n=>{const kind=kinds[n.data.kind];return libraryPresets[kind]?{...n,data:{...n.data,[kind]:apply(kind,n.data[kind])}}:n;};
    setDefaults(prev=>Object.fromEntries(Object.entries(prev).map(([kind,config])=>[kind,apply(kind,config)])));
    setNodes(prev=>prev.map(update));
    setWorkflows(prev=>prev.map(w=>({...w,nodes:w.nodes.map(update)})));
    localStorage.setItem(key,'applied');
  },[]);
  useEffect(()=>{
    const key='swarm-library-shape-v1';if(localStorage.getItem(key))return;
    const align=(kind,config)=>{
      const merged={...initialDefaults[kind],...config};
      if(kind==='repeat')merged.max_loops=1;
      if(['compare','write'].includes(kind))merged.output_type='str-all-except-first';
      return merged;
    };
    const update=n=>{const kind=kinds[n.data.kind];return {...n,data:{...n.data,[kind]:align(kind,n.data[kind])}};};
    setDefaults(prev=>Object.fromEntries(kinds.map(k=>[k,align(k,prev[k])])));
    setNodes(prev=>prev.map(update));setWorkflows(prev=>prev.map(w=>({...w,nodes:w.nodes.map(update)})));
    localStorage.setItem(key,'applied');
  },[]);
  const [activity,setActivity]=useState({phase:'stopped'});
  const [nodeOutputs,setNodeOutputs]=useState(Object.fromEntries(Object.entries(savedCanvas?.outputs||{}).map(([id,items])=>[id,uniqueEntries(items)])));
  const [nodeInputs,setNodeInputs]=useState(Object.fromEntries(Object.entries(savedCanvas?.inputs||{}).map(([id,items])=>[id,uniqueEntries(items)])));
  const outputCounter=useRef(0);
  useEffect(()=>{try{localStorage.setItem('swarm-canvas-'+pipeline,JSON.stringify({nodes,edges,inputs:nodeInputs,outputs:nodeOutputs,title:templateName,deleted:[...removedNodes.current]}));}catch{}},[pipeline,nodes,edges,nodeInputs,nodeOutputs,templateName]);
  const onActivity=useCallback(value=>{setActivity(value);if(value.phase==='deleted'){setNodeOutputs({});setNodeInputs({});setNodes([]);setEdges([]);setTemplateName('Untitled canvas');return;}if(value.phase==='objective'){setTemplateName(value.title||'Local inference deployment review');const demo=(value.nodes||[{kind:0,label:'Assess supplied evidence'},{kind:2,label:'Compare deployments'},{kind:3,label:'Write recommendation'},{kind:5,label:'Review and improve'}]).map((item,i)=>({id:`live-agent-${i}`,type:'block',position:{x:i*300,y:100},data:{...item,runtimeProfile:value.runtimeProfile||'demo',[kinds[item.kind]]:{...initialDefaults[kinds[item.kind]],task:value.objective}}}));setNodes(previous=>demo.filter(n=>!removedNodes.current.has(n.id)).map(n=>{const old=previous.find(v=>v.id===n.id);return old?{...n,position:old.position}:n;}).concat(previous.filter(n=>n.type==='logsProvider')));setEdges(previous=>demo.filter((n,i)=>(value.cycle!==false||i<demo.length-1)&&!removedNodes.current.has(n.id)&&!removedNodes.current.has(demo[(i+1)%demo.length].id)).map((n,i)=>({id:`live-link-${i}`,source:n.id,target:demo[(demo.findIndex(v=>v.id===n.id)+1)%demo.length].id,type:'smoothstep',label:value.cycle!==false&&i===3?'Next round with feedback':undefined,markerEnd:{type:MarkerType.ArrowClosed}})).concat(previous.filter(e=>e.data?.logsProvider)));setTimeout(()=>fitView({padding:.2,maxZoom:1}),100);}if(value.input&&value.phase==='running'){const id=`live-agent-${value.stage}`;setNodeInputs(prev=>({...prev,[id]:[{id:value.inputId,text:value.input,time:value.time,round:value.round},...(prev[id]||[]).filter(v=>v.id!==value.inputId)].slice(0,3)}));}if(value.output&&value.phase==='complete'){const id=`live-agent-${value.stage}`;setNodeOutputs(prev=>({...prev,[id]:[{id:value.outputId,text:value.output,time:value.time},...(prev[id]||[]).filter(v=>v.id!==value.outputId)].slice(0,5)}));}},[]);

  const activeKinds=activity.kind!==undefined?[activity.kind]:[];
  const liveIds=new Set(activity.phase==='stopped'?[]:nodes.filter(n=>activeKinds.includes(n.data.kind)).slice(0,1).map(n=>n.id));
  const [connectionView,setConnectionView]=useState(null);
  function deleteCanvasNodes(deleted){const ids=new Set(deleted.map(n=>n.id));ids.forEach(id=>removedNodes.current.add(id));setNodes(prev=>prev.filter(n=>!ids.has(n.id)));setEdges(prev=>prev.filter(e=>!ids.has(e.source)&&!ids.has(e.target)));setNodeInputs(prev=>Object.fromEntries(Object.entries(prev).filter(([id])=>!ids.has(id))));setNodeOutputs(prev=>Object.fromEntries(Object.entries(prev).filter(([id])=>!ids.has(id))));setResearchId(null);setConnectionView(null);setLogsView(null);}
  const [inputShapeNode,setInputShapeNode]=useState(null);
  const [logsView,setLogsView]=useState(null);
  const [providerBusy,setProviderBusy]=useState(null);
  const providerState=useRef({nodes,edges});providerState.current={nodes,edges};
  const providerRequests=useRef(new Set());
  const readProviderRef=useRef(null);
  async function readProvider(id,inspect=true){
    if(providerRequests.current.has(id))return;
    const provider=providerState.current.nodes.find(n=>n.id===id);if(!provider)return;
    providerRequests.current.add(id);if(inspect)setProviderBusy(id);
    try{setNodes(prev=>prev.map(n=>n.id===id?{...n,data:{...n.data,request:{id:crypto.randomUUID(),time:new Date().toLocaleTimeString(),body:{minutes:provider.data.minutes||60,errors_only:!!provider.data.errors,limit:10}}}}:n));const r=await fetch('/log-api/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({minutes:provider.data.minutes||60,errors_only:!!provider.data.errors,limit:10})});const snapshot=await r.json();if(!r.ok)throw Error(snapshot.detail||'Could not read logs');
      const current=providerState.current.nodes.find(n=>n.id===id);if(!current||current.data.minutes!==provider.data.minutes||current.data.errors!==provider.data.errors)return;
      setNodes(prev=>prev.map(n=>n.id===id?{...n,data:{...n.data,snapshot,error:'',lastRead:new Date().toLocaleTimeString()}}:n));
      const targets=providerState.current.edges.filter(e=>e.source===id&&e.data?.logsProvider).map(e=>e.target);
      setNodeInputs(prev=>{let updated=prev;for(const target of targets){const existing=prev[target]||[];const unseen=snapshot.records.filter(record=>!existing.some(item=>item.id===id+':'+record.id));if(unseen.length){updated={...updated,[target]:[...unseen.map(record=>({id:id+':'+record.id,providerId:id,text:record.name+' · '+record.level+'\nRecord '+record.id+'\n'+(record.statusMessage||'')+'\n\n'+JSON.stringify(record,null,2),time:new Date().toLocaleTimeString()})),...existing].slice(0,30)};}}return updated;});
      if(inspect)setLogsView({source:id,target:targets[0]});
    }catch(e){setNodes(prev=>prev.map(n=>n.id===id?{...n,data:{...n.data,error:e.message}}:n));}finally{providerRequests.current.delete(id);if(inspect)setProviderBusy(null);}
  }
  readProviderRef.current=readProvider;
  useEffect(()=>{const poll=()=>{for(const provider of providerState.current.nodes.filter(n=>n.type==='logsProvider'))readProviderRef.current(provider.id,false);};poll();const timer=setInterval(poll,5000);return()=>clearInterval(timer);},[pipeline]);
  const visibleNodes=nodes.map(n=>({...n,data:{...n.data,onInputConfigure:id=>{setInputShapeNode(id);setResearchId(null);setConnectionView(null);setLogsView(null);},remove:()=>deleteCanvasNodes([n]),read:()=>readProvider(n.id),loading:providerBusy===n.id,configure:change=>setNodes(prev=>prev.map(v=>v.id===n.id?{...v,data:{...v.data,...change,snapshot:null}}:v)),onConfigure:(id,section)=>{setResearchId(id);setConnectionView(section==='settings'?null:section);},inputs:(nodeInputs[n.id]||[]).filter(item=>!item.providerId||(inputShape(n).enabled!==false&&edges.some(e=>e.source===item.providerId&&e.target===n.id&&e.data?.logsProvider))),outputs:nodeOutputs[n.id]||[],liveState:liveIds.has(n.id)?activity.phase:null}}));
  const visibleEdges=edges.map(e=>({...e,animated:activity.phase==='running'&&(liveIds.has(e.source)||liveIds.has(e.target)),style:{...e.style,stroke:activity.phase==='running'&&(liveIds.has(e.source)||liveIds.has(e.target))?'var(--accent)':undefined},className:activity.phase==='running'&&(liveIds.has(e.source)||liveIds.has(e.target))?'live-edge':''}));
  const [hoverBlock,setHoverBlock]=useState(null);
  const [hoverCategory,setHoverCategory]=useState(null);
  const hoverTimer=useRef(null);
  const closeHover=()=>{hoverTimer.current=setTimeout(()=>{setHoverBlock(null);setHoverCategory(null);},180);};
  const holdHover=()=>clearTimeout(hoverTimer.current);
  const nextId = useRef(7);
  const [researchId,setResearchId] = useState(null);
  const researchNode = nodes.find(n=>n.id===researchId);
  const updateResearch = research => setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,research}} : n));
  const onConnect=connection=>{const source=nodes.find(n=>n.id===connection.source),target=nodes.find(n=>n.id===connection.target);if(source?.type==='logsProvider'){if(![0,2,3,5].includes(target?.data.kind)||target?.data.runtimeRole==='Code')return;setEdges(current=>addEdge({...connection,targetHandle:'logs-context',label:'Logs → Input',data:{logsProvider:true},type:'smoothstep'},current));readProvider(source.id,false);setLogsView({source:source.id,target:target.id});}else if(pipeline==='draft')setEdges(current=>addEdge(connection,current));};
  const addLogsProvider=point=>setNodes(current=>[...current,{id:'logs-'+crypto.randomUUID(),type:'logsProvider',draggable:true,position:point||screenToFlowPosition({x:window.innerWidth/2,y:window.innerHeight/2}),data:{minutes:60,errors:false}}]);
  const addBlock = (kind,point) => {
    const position = point || screenToFlowPosition({x:window.innerWidth/2,y:window.innerHeight/2});
    setNodes(current => [...current,{id:`block-${nextId.current++}`,type:'block',position,data:{kind,[kinds[kind]]:structuredClone(defaults[kinds[kind]])}}]);
  };
  const onDrop = event => {
    event.preventDefault();
    if(event.dataTransfer.getData('application/swarm-logs')){addLogsProvider(screenToFlowPosition({x:event.clientX,y:event.clientY}));return;}
    const raw = event.dataTransfer.getData('application/swarm-block');
    if (!/^\d$/.test(raw) || Number(raw) >= blocks.length) return;
    addBlock(Number(raw),screenToFlowPosition({x:event.clientX,y:event.clientY}));
  };
  const usePattern=p=>{
    if(p.pipeline){setLibraryOpen(false);onSelectPipeline(p.pipeline);return;}
    setTemplateName(p.name);
    let freshNodes, freshEdges;
    if(p.saved){freshNodes=structuredClone(p.nodes).map(normalizeNodeModels);freshEdges=structuredClone(p.edges);}
    else {
      const columns=p.id==='research'?[0,1,2,2,3,4,5,4]:p.id==='perspectives'?[0,1,1,1,2,3,4]:p.sequence.map((_,i)=>i);
      freshNodes=p.sequence.map((kind,i)=>{
        const key=kinds[kind];const config=structuredClone(defaults[key]);
        if(['research','write','review','repeat'].includes(key))config.task=`${p.labels[i]}. ${p.objective}`;
        if(key==='compare'){config.question=p.objective;config.criteria='Evidence quality, benefits, risks, and meaningful differences';config.layout='table';}
        if(key==='write')config.format='markdown';
        if(key==='repeat')config.max_loops=p.id==='refine'?2:1;
        return {id:`pattern-${p.id}-${i}`,type:'block',position:{x:columns[i]*300,y:p.id==='research'?(i===2?40:i===3?300:i===7?460:180):p.id==='perspectives'?(i>=1&&i<=3?(i-1)*220:220):p.id==='documents'&&i<2?i*220:110},data:{kind,label:p.labels[i],[key]:config}};
      });
      freshNodes=freshNodes.map(n=>{const key=kinds[n.data.kind];if(key==='parallel')return {...n,data:{...n.data,parallel:{...n.data.parallel,members:p.links.filter(([a])=>freshNodes[a].id===n.id).map(([,b])=>freshNodes[b].id)}}};if(key==='repeat')return {...n,data:{...n.data,repeat:{...n.data.repeat,members:freshNodes.filter(m=>[0,3,5].includes(m.data.kind)).map(m=>m.id)}}};return n;});
      freshEdges=p.links.map(([a,b],i)=>({id:`pattern-${p.id}-edge-${i}`,source:freshNodes[a].id,target:freshNodes[b].id,type:'smoothstep',markerEnd:{type:MarkerType.ArrowClosed}}));
    }
    if(pipeline!=='draft'){localStorage.setItem('swarm-canvas-draft',JSON.stringify({nodes:freshNodes,edges:freshEdges,title:p.name||'Draft canvas',inputs:{},outputs:{}}));onSelectPipeline('draft');return;}
    setNodes(freshNodes);setEdges(freshEdges);setResearchId(null);setLibraryOpen(false);setHoverBlock(null);
    setTimeout(()=>fitView({padding:.2,maxZoom:1}),100);
  };
  const switchProfile=value=>{
    const update=(kind,c)=>{if(!['research','compare','write','review'].includes(kind))return c;const old=c.model_profile||'codex';const saved={...c.profile_models,[old]:{model_name:c.model_name,reasoning_effort:c.reasoning_effort}};const selected=saved[value]||(value==='exo'?{model_name:exoModels[0]?.id||'',reasoning_effort:''}:{model_name:initialDefaults[kind].model_name,reasoning_effort:initialDefaults[kind].reasoning_effort});return {...c,...selected,model_profile:value,profile_models:saved};};
    setDefaults(prev=>Object.fromEntries(Object.entries(prev).map(([k,c])=>[k,update(k,c)])));
    setNodes(prev=>prev.map(n=>{const k=kinds[n.data.kind];return {...n,data:{...n.data,[k]:update(k,{...initialDefaults[k],...n.data[k]})}};}));
    setProfile(value);localStorage.setItem('swarm-model-profile',value);
  };
  return <ModelProfileContext.Provider value={{profile,models:exoModels,status:exoStatus}}><main className="workspace">
    <aside className="tray" aria-label="Building blocks">
      <div className="pattern-library-anchor" onMouseEnter={()=>{holdLibrary();setHoverBlock(null);setLibraryOpen(true);}} onMouseLeave={closeLibrary}><button className="tray-mark" aria-label="Open pattern library" aria-expanded={libraryOpen} onFocus={()=>{holdLibrary();setLibraryOpen(true);}} onClick={()=>setLibraryOpen(true)}><SquaresFour size={25} weight="duotone" /></button>{libraryOpen&&!settingsOpen&&<PatternLibrary workflows={workflows} blocks={blocks} onUse={usePattern} onClose={()=>setLibraryOpen(false)}/>}</div>
      <button className="tray-block logs-provider-tray" aria-label="Add logs provider" draggable onDragStart={e=>e.dataTransfer.setData('application/swarm-logs','logs')} onClick={()=>addLogsProvider()}><Files size={23}/><span>Logs</span></button>
      <div className="layer-switcher" aria-label="Node layers"><div className="layer-dots">{layers.map((layer,i)=><button key={layer.name} aria-label={`Show ${layer.name} layer`} aria-pressed={layerIndex===i} className={layerIndex===i?'active':''} onMouseEnter={()=>{setLayerIndex(i);setHoverBlock(null);}} onFocus={()=>{setLayerIndex(i);setHoverBlock(null);}} onClick={()=>setLayerIndex(i)}><span/></button>)}</div><span className="layer-name">{layers[layerIndex].name}</span></div>
      <div className="layer-viewport" onTouchStart={e=>{swipeStart.current=e.touches[0].clientX;}} onTouchEnd={e=>{if(swipeStart.current===null)return;const delta=e.changedTouches[0].clientX-swipeStart.current;if(Math.abs(delta)>35){setLayerIndex(i=>Math.max(0,Math.min(layers.length-1,i+(delta<0?1:-1))));setHoverBlock(null);}swipeStart.current=null;}}><div className="layer-track" style={{transform:`translateX(-${layerIndex*100}%)`}}>{layers.map((layer,li)=><div key={layer.name} className="tray-items layer-page" inert={li!==layerIndex?true:undefined} aria-label={`${layer.name} nodes`}>{layer.indices.map(index => {
        const block=blocks[index];
        const Icon = block.icon;
        return <button key={block.name} className="tray-block" onMouseEnter={e=>{holdHover();setHoverCategory(null);setHoverBlock({kind:index,top:Math.min(e.currentTarget.getBoundingClientRect().top,window.innerHeight-230)});}} onMouseLeave={closeHover} draggable={false} onPointerDown={event=>{if(event.button!==0)return;trayDrag.current={kind:index,x:event.clientX,y:event.clientY,moved:false};event.currentTarget.setPointerCapture(event.pointerId);holdHover();setHoverBlock(null);setHoverCategory(null);}} onPointerMove={event=>{const drag=trayDrag.current;if(drag&&Math.hypot(event.clientX-drag.x,event.clientY-drag.y)>5){drag.moved=true;event.currentTarget.style.cursor='grabbing';}}} onPointerUp={event=>{const drag=trayDrag.current;trayDrag.current=null;event.currentTarget.style.cursor='';if(!drag?.moved)return;suppressTrayClick.current=true;const rect=document.querySelector('.canvas').getBoundingClientRect();if(event.clientX>=rect.left&&event.clientX<=rect.right&&event.clientY>=rect.top&&event.clientY<=rect.bottom)addBlock(drag.kind,screenToFlowPosition({x:event.clientX,y:event.clientY}));}} onPointerCancel={()=>{trayDrag.current=null;}} title={`Add ${block.name}: ${block.description}`} aria-label={`Add ${block.name}`} onClick={() => {if(suppressTrayClick.current){suppressTrayClick.current=false;return;}addBlock(index);}} onDragStart={event => {event.dataTransfer.setData('application/swarm-block',String(index));event.dataTransfer.effectAllowed='copy';}}><span className="tray-node-preview"><span className="preview-port preview-port-in" /><span className="preview-top"><span className="preview-icon"><Icon size={14} /></span><span className="preview-kind">{index===5?'Evaluation':index>=4?'Coordination':'Action'}</span></span><span className="preview-name">{block.name}</span><span className="preview-description">{block.description}</span><span className="preview-port preview-port-out" /></span></button>;
      })}</div>)}</div></div>
      <div className="tray-bottom"><span className="tray-foot">7 blocks</span><button className="settings-gear" aria-label="Open settings" title="Settings" onClick={()=>{setResearchId(null);if(!workflows.length)setWorkflows([{id:crypto.randomUUID(),name:'Research and decision assistant',nodes:structuredClone(nodes),edges:structuredClone(edges)}]);setSettingsOpen(true);}}><GearSix size={23}/></button></div>
    </aside>
    <section className="canvas" aria-label="Swarm canvas" onDrop={onDrop} onDragOver={event => {event.preventDefault();event.dataTransfer.dropEffect='copy';}}>
      <ReactFlow nodes={visibleNodes} edges={visibleEdges} nodeTypes={nodeTypes} onNodesChange={onNodesChange} onNodesDelete={deleteCanvasNodes} onEdgesChange={onEdgesChange} onConnect={onConnect} onNodeClick={(_,node)=>{setResearchId(node.id);setConnectionView(null);}} onEdgeClick={(_,edge)=>{if(edge.data?.logsProvider)setLogsView({source:edge.source,target:edge.target});}} onPaneClick={()=>{setResearchId(null);setConnectionView(null);}} fitView fitViewOptions={{padding:0.2,maxZoom:1}} minZoom={0.25} maxZoom={2} nodesDraggable={pipeline!=='logs'} nodesConnectable={true} colorMode="system" deleteKeyCode={['Backspace','Delete']} defaultEdgeOptions={{type:'smoothstep',style:{strokeWidth:1.5},markerEnd:{type:MarkerType.ArrowClosed}}}>
        <Background gap={24} size={1} />
        <Panel position="top-left" className="canvas-heading"><h1>{templateName}</h1><span>{pipeline==='logs'?'Live runtime · pinned canvas':'Design mode · not executing'}</span></Panel>
        <Panel position="top-right" className="io-legend"><span className="input-key">Input</span><span className="output-key">Output</span></Panel>
        <Controls position="bottom-left" showInteractive={false} />
        <Panel position="bottom-center" className="canvas-hint">Drag blocks to arrange. Connect the handles.</Panel>
        {nodes.length === 0 && <Panel position="top-center" className="empty-state">Your canvas is clear. Add a block from the tray.</Panel>}
      </ReactFlow>
    </section>
    {pipeline==='logs'&&<LiveLoop key={pipeline} pipeline={pipeline} onActivity={onActivity}/>}
    {!settingsOpen && !connectionView && researchNode?.data.kind===0 && <ResearchPanel node={researchNode} onChange={updateResearch} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && !connectionView && researchNode?.data.kind===1 && <ReadPanel node={researchNode} onChange={read=>setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,read}} : n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && !connectionView && researchNode?.data.kind===2 && <ComparePanel node={researchNode} incoming={edges.filter(e=>e.target===researchNode.id).map(e=>{const source=nodes.find(n=>n.id===e.source);return source ? source.data.label || blocks[source.data.kind].name : e.source;})} onChange={compare=>setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,compare}} : n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && !connectionView && researchNode?.data.kind===3 && <WritePanel node={researchNode} onChange={write=>setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,write}} : n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && !connectionView && researchNode?.data.kind===4 && <ParallelPanel node={researchNode} members={nodes.filter(n=>edges.some(e=>e.source===researchNode.id && e.target===n.id))} onChange={parallel=>setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,parallel}} : n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && !connectionView && researchNode?.data.kind===5 && <ReviewPanel node={researchNode} onChange={review=>setNodes(current=>current.map(n=>n.id===researchId?{...n,data:{...n.data,review}}:n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && !connectionView && researchNode?.data.kind===6 && <RepeatPanel node={researchNode} nodes={nodes} onChange={repeat=>setNodes(current=>current.map(n=>n.id===researchId?{...n,data:{...n.data,repeat}}:n))} onClose={()=>setResearchId(null)}/>}
    {settingsOpen && <SettingsPage profile={profile} onProfileChange={switchProfile} defaults={defaults} setDefaults={setDefaults} workflows={workflows} setWorkflows={setWorkflows} nodes={nodes} edges={edges} error={storageError} onClose={()=>setSettingsOpen(false)} onApply={()=>setNodes(current=>current.map(n=>({...n,data:{...n.data,[kinds[n.data.kind]]:structuredClone(defaults[kinds[n.data.kind]])}})))} onLoad={w=>{setTemplateName(w.name);setNodes(structuredClone(w.nodes).map(normalizeNodeModels));setEdges(structuredClone(w.edges));setResearchId(null);setSettingsOpen(false);nextId.current=Math.max(7,...w.nodes.map(n=>Number(n.id.replace('block-',''))||0))+1;setTimeout(()=>fitView({padding:.2,maxZoom:1}),100);}}/>}
    {inputShapeNode&&nodes.find(n=>n.id===inputShapeNode)&&<InputShapePanel node={nodes.find(n=>n.id===inputShapeNode)} sources={nodes.filter(n=>n.type==='logsProvider'&&edges.some(e=>e.source===n.id&&e.target===inputShapeNode&&e.data?.logsProvider))} onClose={()=>setInputShapeNode(null)} onChange={inputShape=>setNodes(prev=>prev.map(n=>n.id===inputShapeNode?{...n,data:{...n.data,inputShape}}:n))}/> }
    {logsView&&nodes.find(n=>n.id===logsView.source)&&<LogsInputPanel source={nodes.find(n=>n.id===logsView.source)} target={nodes.find(n=>n.id===logsView.target)} onTaskChange={task=>setNodes(prev=>prev.map(n=>n.id===logsView.target?{...n,data:{...n.data,inputShape:{...inputShape(n),task}}}:n))} onClose={()=>setLogsView(null)} onDisconnect={()=>{setEdges(prev=>prev.filter(e=>!(e.source===logsView.source&&e.target===logsView.target&&e.data?.logsProvider)));setLogsView(null);}} onRun={async task=>{if(!edges.some(e=>e.source===logsView.source&&e.target===logsView.target&&e.data?.logsProvider))throw Error('Connect the logs provider to this agent first.');const source=nodes.find(n=>n.id===logsView.source),target=nodes.find(n=>n.id===logsView.target);const shape=inputShape(target);const attached=nodes.filter(n=>n.type==='logsProvider'&&edges.some(e=>e.source===n.id&&e.target===target.id&&e.data?.logsProvider));const selected=includedSources(attached,shape);if(selected.some(n=>!n.data.snapshot))throw Error('Wait for all included sources to load.');const r=await fetch('/log-api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({snapshot_id:source.data.snapshot.snapshotId,snapshot_ids:selected.map(n=>n.data.snapshot.snapshotId),task:composeTask(task,shape),task_position:taskPosition(attached,shape),context_fields:target.data.inputShape?.fields||inputFields,include_context:selected.length>0,node_id:pipeline+':'+target.id,agent_name:target.data.label||blocks[target.data.kind].name})});const result=await r.json();if(!r.ok)throw Error(result.detail||'Agent execution failed');const time=new Date().toLocaleTimeString();setNodeInputs(prev=>({...prev,[target.id]:[{id:crypto.randomUUID(),text:result.agentInput,time},...(prev[target.id]||[])].slice(0,3)}));setNodeOutputs(prev=>({...prev,[target.id]:[{id:crypto.randomUUID(),text:result.output,time},...(prev[target.id]||[])].slice(0,5)}));}}/>}
    {connectionView&&researchNode&&!settingsOpen&&<NodeConnections nodeKey={pipeline+':'+researchNode.id} recordsConnected={edges.some(e=>e.target===researchNode.id&&e.data?.logsProvider)} node={researchNode} section={connectionView} onClose={()=>setConnectionView(null)}/>}
    {hoverBlock && !settingsOpen && <div className="node-hover-menu" style={{top:Math.max(12,hoverBlock.top)}} onMouseEnter={holdHover} onMouseLeave={closeHover}>
      <div className="block-node"><div className="node-top"><span className="node-icon">{React.createElement(blocks[hoverBlock.kind].icon,{size:23})}</span><span className="node-kind">{['Agent','File tool','Agent','Agent','Concurrent','Judge','Round robin'][hoverBlock.kind]}</span></div><h2>{blocks[hoverBlock.kind].name}</h2><p>{blocks[hoverBlock.kind].description}</p></div>
      <div className="hover-category-row">{[...categories,'Saved workflows'].map((category,i)=><button key={category} aria-label={`${blocks[hoverBlock.kind].name}: ${category}`} title={category} className={hoverCategory===category?'active':''} onMouseEnter={()=>setHoverCategory(category)} onFocus={()=>setHoverCategory(category)} onClick={()=>setHoverCategory(category)}>{React.createElement([Cpu,TextAlignLeft,Target,Plug,FlowArrow,Export,ShieldCheck,Folder,PuzzlePiece,Stack][i],{size:17})}</button>)}</div>
      {hoverCategory && <div className="hover-config" style={{top:Math.min(0,window.innerHeight-20-Math.min(680,window.innerHeight-40)-Math.max(12,hoverBlock.top))}}><SettingsPage profile={profile} onProfileChange={switchProfile} targetKind={kinds[hoverBlock.kind]} activeCategory={hoverCategory} defaults={defaults} setDefaults={setDefaults} workflows={workflows} setWorkflows={setWorkflows} nodes={nodes} edges={edges} error={storageError} onClose={()=>setHoverCategory(null)} onApply={()=>{}} onLoad={w=>{setTemplateName(w.name);setNodes(structuredClone(w.nodes).map(normalizeNodeModels));setEdges(structuredClone(w.edges));setHoverBlock(null);setHoverCategory(null);}}/></div>}
    </div>}
  </main></ModelProfileContext.Provider>;
}
createRoot(document.getElementById('root')).render(<React.StrictMode><WorkspaceModes><ReactFlowProvider><PipelineWorkspace>{(pipeline,status,change)=>pipeline==='images'?<ImageDiscovery/>:<Canvas key={pipeline} pipeline={pipeline} pipelineStatus={status} onSelectPipeline={change}/>}</PipelineWorkspace></ReactFlowProvider></WorkspaceModes></React.StrictMode>);
