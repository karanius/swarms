import {normalizeModelConfig,ModelProfileContext} from './ModelSelect';
import {libraryPresets} from './libraryPresets';
import React, { useCallback, useRef, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { ReactFlow, ReactFlowProvider, Background, Controls, Handle, Position, Panel, MarkerType, useNodesState, useEdgesState, addEdge, useReactFlow } from '@xyflow/react';
import { MagnifyingGlass, Files, ArrowsLeftRight, PencilLine, Stack, ShieldCheck, ArrowClockwise, SquaresFour, GearSix, Cpu, TextAlignLeft, Target, Plug, FlowArrow, Export, Folder, PuzzlePiece } from '@phosphor-icons/react';
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

const blocks = [
  { name: 'Research', short: 'Research', description: 'Find sources and gather evidence', icon: MagnifyingGlass },
  { name: 'Read documents', short: 'Read', description: 'Extract information from files', icon: Files },
  { name: 'Compare', short: 'Compare', description: 'Find patterns and differences', icon: ArrowsLeftRight },
  { name: 'Write', short: 'Write', description: 'Turn findings into an output', icon: PencilLine },
  { name: 'Parallel team', short: 'Parallel', description: 'Work on multiple tasks together', icon: Stack },
  { name: 'Review', short: 'Review', description: 'Check the result before continuing', icon: ShieldCheck },
  { name: 'Repeat', short: 'Repeat', description: 'Return to a step and try again', icon: ArrowClockwise },
];
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
const initialNodes = [];
const nodeTypes = { block: BlockNode };
function BlockNode({ data, selected }) {
  const block = blocks[data.kind];
  const Icon = block.icon;
  return <div className={`block-node ${selected ? 'is-selected' : ''}`}>
    <Handle type="target" position={Position.Left} aria-label={`${block.name} input`} />
    <div className="node-top"><span className="node-icon"><Icon size={23} weight="regular" /></span><span className="node-kind">{['Agent','File tool','Agent','Agent','Concurrent','Judge','Round robin'][data.kind]}</span></div>
    <h2>{data.label || block.name}</h2><p>{block.description}</p>
    <Handle type="source" position={Position.Right} aria-label={`${block.name} output`} />
  </div>;
}
function normalizeNodeModels(n){const kind=kinds[n.data.kind];return {...n,data:{...n.data,[kind]:normalizeModelConfig(kind,{...initialDefaults[kind],...n.data[kind]})}};}
function loadStored(key,fallback){try{return JSON.parse(localStorage.getItem(key)) || fallback;}catch{return fallback;}}
function Canvas() {
  const [defaults,setDefaults]=useState(()=>Object.fromEntries(Object.entries(loadStored('swarm-defaults-v1',initialDefaults)).map(([k,v])=>[k,normalizeModelConfig(k,v)])));
  const [workflows,setWorkflows]=useState(()=>loadStored('swarm-workflows-v1',[]).map(w=>({...w,nodes:w.nodes.map(normalizeNodeModels)})));
  const [profile,setProfile]=useState(()=>localStorage.getItem('swarm-model-profile')||'codex');
  const [exoModels,setExoModels]=useState([]);
  const [exoStatus,setExoStatus]=useState('Loading EXO catalog');
  useEffect(()=>{fetch('/exo-api/v1/models').then(r=>{if(!r.ok)throw Error();return r.json();}).then(d=>{setExoModels(d.data||[]);setExoStatus('');}).catch(()=>setExoStatus('EXO unavailable'));},[]);
  const [settingsOpen,setSettingsOpen]=useState(false);
  const [storageError,setStorageError]=useState('');
  useEffect(()=>{try{localStorage.setItem('swarm-defaults-v1',JSON.stringify(defaults));localStorage.setItem('swarm-workflows-v1',JSON.stringify(workflows));setStorageError('');}catch{setStorageError('Browser storage is unavailable. Export your node configurations before closing.');}},[defaults,workflows]);
  const [nodes,setNodes,onNodesChange] = useNodesState((new URLSearchParams(location.search).has('example') ? exampleNodes : initialNodes).map(normalizeNodeModels));
  const [edges,setEdges,onEdgesChange] = useEdgesState(new URLSearchParams(location.search).has('example') ? exampleEdges : []);
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
  const [hoverBlock,setHoverBlock]=useState(null);
  const [hoverCategory,setHoverCategory]=useState(null);
  const hoverTimer=useRef(null);
  const closeHover=()=>{hoverTimer.current=setTimeout(()=>{setHoverBlock(null);setHoverCategory(null);},180);};
  const holdHover=()=>clearTimeout(hoverTimer.current);
  const nextId = useRef(7);
  const [researchId,setResearchId] = useState(null);
  const researchNode = nodes.find(n=>n.id===researchId);
  const updateResearch = research => setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,research}} : n));
  const onConnect = useCallback(connection => setEdges(current => addEdge(connection,current)),[setEdges]);
  const addBlock = (kind,point) => {
    const position = point || screenToFlowPosition({x:window.innerWidth/2,y:window.innerHeight/2});
    setNodes(current => [...current,{id:`block-${nextId.current++}`,type:'block',position,data:{kind,[kinds[kind]]:structuredClone(defaults[kinds[kind]])}}]);
  };
  const onDrop = event => {
    event.preventDefault();
    const raw = event.dataTransfer.getData('application/swarm-block');
    if (!/^\d$/.test(raw) || Number(raw) >= blocks.length) return;
    addBlock(Number(raw),screenToFlowPosition({x:event.clientX,y:event.clientY}));
  };
  const switchProfile=value=>{
    const update=(kind,c)=>{if(!['research','compare','write','review'].includes(kind))return c;const old=c.model_profile||'codex';const saved={...c.profile_models,[old]:{model_name:c.model_name,reasoning_effort:c.reasoning_effort}};const selected=saved[value]||(value==='exo'?{model_name:exoModels[0]?.id||'',reasoning_effort:''}:{model_name:initialDefaults[kind].model_name,reasoning_effort:initialDefaults[kind].reasoning_effort});return {...c,...selected,model_profile:value,profile_models:saved};};
    setDefaults(prev=>Object.fromEntries(Object.entries(prev).map(([k,c])=>[k,update(k,c)])));
    setNodes(prev=>prev.map(n=>{const k=kinds[n.data.kind];return {...n,data:{...n.data,[k]:update(k,{...initialDefaults[k],...n.data[k]})}};}));
    setProfile(value);localStorage.setItem('swarm-model-profile',value);
  };
  return <ModelProfileContext.Provider value={{profile,models:exoModels,status:exoStatus}}><main className="workspace">
    <aside className="tray" aria-label="Building blocks">
      <div className="tray-mark" title="Swarm Canvas"><SquaresFour size={25} weight="duotone" /></div>
      <div className="tray-items">{blocks.map((block,index) => {
        const Icon = block.icon;
        return <button key={block.name} className="tray-block" onMouseEnter={e=>{holdHover();setHoverCategory(null);setHoverBlock({kind:index,top:Math.min(e.currentTarget.getBoundingClientRect().top,window.innerHeight-230)});}} onMouseLeave={closeHover} draggable title={`Add ${block.name}: ${block.description}`} aria-label={`Add ${block.name}`} onClick={() => addBlock(index)} onDragStart={event => {event.dataTransfer.setData('application/swarm-block',String(index));event.dataTransfer.effectAllowed='copy';}}><span className="tray-node-preview"><span className="preview-port preview-port-in" /><span className="preview-top"><span className="preview-icon"><Icon size={14} /></span><span className="preview-kind">{index >= 4 ? 'Control' : 'Action'}</span></span><span className="preview-name">{block.name}</span><span className="preview-description">{block.description}</span><span className="preview-port preview-port-out" /></span></button>;
      })}</div>
      <div className="tray-bottom"><span className="tray-foot">7 blocks</span><button className="settings-gear" aria-label="Open settings" title="Settings" onClick={()=>{setResearchId(null);if(!workflows.length)setWorkflows([{id:crypto.randomUUID(),name:'Research and decision assistant',nodes:structuredClone(nodes),edges:structuredClone(edges)}]);setSettingsOpen(true);}}><GearSix size={23}/></button></div>
    </aside>
    <section className="canvas" aria-label="Swarm canvas" onDrop={onDrop} onDragOver={event => {event.preventDefault();event.dataTransfer.dropEffect='copy';}}>
      <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} onNodeClick={(_,node)=>setResearchId(node.id)} onPaneClick={()=>setResearchId(null)} fitView fitViewOptions={{padding:0.2,maxZoom:1}} minZoom={0.25} maxZoom={2} colorMode="system" deleteKeyCode={['Backspace','Delete']} defaultEdgeOptions={{type:'smoothstep',style:{strokeWidth:1.5},markerEnd:{type:MarkerType.ArrowClosed}}}>
        <Background gap={24} size={1} />
        <Panel position="top-left" className="canvas-heading"><h1>Swarm canvas</h1><span>Arrange your building blocks.</span></Panel>
        <Controls position="bottom-left" showInteractive={false} />
        <Panel position="bottom-center" className="canvas-hint">Drag blocks to arrange. Connect the handles.</Panel>
        {nodes.length === 0 && <Panel position="top-center" className="empty-state">Your canvas is clear. Add a block from the tray.</Panel>}
      </ReactFlow>
    </section>
    {!settingsOpen && researchNode?.data.kind===0 && <ResearchPanel node={researchNode} onChange={updateResearch} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && researchNode?.data.kind===1 && <ReadPanel node={researchNode} onChange={read=>setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,read}} : n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && researchNode?.data.kind===2 && <ComparePanel node={researchNode} incoming={edges.filter(e=>e.target===researchNode.id).map(e=>{const source=nodes.find(n=>n.id===e.source);return source ? source.data.label || blocks[source.data.kind].name : e.source;})} onChange={compare=>setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,compare}} : n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && researchNode?.data.kind===3 && <WritePanel node={researchNode} onChange={write=>setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,write}} : n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && researchNode?.data.kind===4 && <ParallelPanel node={researchNode} members={nodes.filter(n=>edges.some(e=>e.source===researchNode.id && e.target===n.id))} onChange={parallel=>setNodes(current=>current.map(n=>n.id===researchId ? {...n,data:{...n.data,parallel}} : n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && researchNode?.data.kind===5 && <ReviewPanel node={researchNode} onChange={review=>setNodes(current=>current.map(n=>n.id===researchId?{...n,data:{...n.data,review}}:n))} onClose={()=>setResearchId(null)}/>}
    {!settingsOpen && researchNode?.data.kind===6 && <RepeatPanel node={researchNode} nodes={nodes} onChange={repeat=>setNodes(current=>current.map(n=>n.id===researchId?{...n,data:{...n.data,repeat}}:n))} onClose={()=>setResearchId(null)}/>}
    {settingsOpen && <SettingsPage profile={profile} onProfileChange={switchProfile} defaults={defaults} setDefaults={setDefaults} workflows={workflows} setWorkflows={setWorkflows} nodes={nodes} edges={edges} error={storageError} onClose={()=>setSettingsOpen(false)} onApply={()=>setNodes(current=>current.map(n=>({...n,data:{...n.data,[kinds[n.data.kind]]:structuredClone(defaults[kinds[n.data.kind]])}})))} onLoad={w=>{setNodes(structuredClone(w.nodes).map(normalizeNodeModels));setEdges(structuredClone(w.edges));setResearchId(null);setSettingsOpen(false);nextId.current=Math.max(7,...w.nodes.map(n=>Number(n.id.replace('block-',''))||0))+1;setTimeout(()=>fitView({padding:.2,maxZoom:1}),100);}}/>}
    {hoverBlock && !settingsOpen && <div className="node-hover-menu" style={{top:Math.max(12,hoverBlock.top)}} onMouseEnter={holdHover} onMouseLeave={closeHover}>
      <div className="block-node"><div className="node-top"><span className="node-icon">{React.createElement(blocks[hoverBlock.kind].icon,{size:23})}</span><span className="node-kind">{['Agent','File tool','Agent','Agent','Concurrent','Judge','Round robin'][hoverBlock.kind]}</span></div><h2>{blocks[hoverBlock.kind].name}</h2><p>{blocks[hoverBlock.kind].description}</p></div>
      <div className="hover-category-row">{[...categories,'Saved workflows'].map((category,i)=><button key={category} aria-label={`${blocks[hoverBlock.kind].name}: ${category}`} title={category} className={hoverCategory===category?'active':''} onMouseEnter={()=>setHoverCategory(category)} onFocus={()=>setHoverCategory(category)} onClick={()=>setHoverCategory(category)}>{React.createElement([Cpu,TextAlignLeft,Target,Plug,FlowArrow,Export,ShieldCheck,Folder,PuzzlePiece,Stack][i],{size:17})}</button>)}</div>
      {hoverCategory && <div className="hover-config" style={{top:Math.min(0,window.innerHeight-20-Math.min(680,window.innerHeight-40)-Math.max(12,hoverBlock.top))}}><SettingsPage profile={profile} onProfileChange={switchProfile} targetKind={kinds[hoverBlock.kind]} activeCategory={hoverCategory} defaults={defaults} setDefaults={setDefaults} workflows={workflows} setWorkflows={setWorkflows} nodes={nodes} edges={edges} error={storageError} onClose={()=>setHoverCategory(null)} onApply={()=>{}} onLoad={w=>{setNodes(structuredClone(w.nodes).map(normalizeNodeModels));setEdges(structuredClone(w.edges));setHoverBlock(null);setHoverCategory(null);}}/></div>}
    </div>}
  </main></ModelProfileContext.Provider>;
}
createRoot(document.getElementById('root')).render(<React.StrictMode><ReactFlowProvider><Canvas /></ReactFlowProvider></React.StrictMode>);
