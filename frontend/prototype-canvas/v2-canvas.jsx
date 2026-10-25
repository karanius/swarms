import React, {useEffect,useRef,useState} from 'react';
import {ReactFlow,Background,Controls,useNodesState,useEdgesState,addEdge} from '@xyflow/react';
import V2Library from './v2-library.jsx';
import MachineSequence from './machine-sequence.jsx';
import './v2-canvas.css';

const planes=['Confederations','Federation','Alliances','Ecosystems','Enterprises','Operations','Programs','Processes','Flows','Composite Components'];
function PlaneSurface(){
 const [nodes,,onNodesChange]=useNodesState([]),[edges,setEdges,onEdgesChange]=useEdgesState([]);
 return <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={connection=>setEdges(old=>addEdge(connection,old))} colorMode="dark"><Background/><Controls/></ReactFlow>;
}
export default function VersionTwo(){
 const surface=useRef(null),native=useRef(null);
 const [activePlane,setActivePlane]=useState('Components');
 const [error,setError]=useState(''),[ready,setReady]=useState(false);
 useEffect(()=>{
  let cancelled=false;
  import(/* @vite-ignore */ window.location.origin+'/langflow-native/adapter.js').then(async module=>{
   if(cancelled)return;
   const controller=await module.mount(surface.current);
   if(cancelled)controller.unmount();else{native.current=controller;setReady(true);}
  }).catch(e=>{if(!cancelled)setError(e.message);});
  return ()=>{cancelled=true;native.current?.unmount();native.current=null;};
 },[]);
 return <main className="v2-canvas"><div className="v2-native-surface" ref={surface} style={{display:activePlane==='Components'?'block':'none'}}/>{planes.map(plane=><section key={plane} className="v2-plane-surface" hidden={activePlane!==plane} aria-label={plane+' plane'}><PlaneSurface/></section>)}{error&&activePlane==='Components'&&<div role="alert" className="v2-native-error">{error}</div>}<V2Library activePlane={activePlane} onSelectPlane={plane=>setActivePlane(plane)} onAddComponent={ready?type=>{setActivePlane('Components');native.current.add(type);}:undefined}/><div className="plane-location" role="status">{activePlane}</div><MachineSequence/></main>;
}
