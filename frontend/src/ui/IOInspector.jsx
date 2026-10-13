import React,{useState,useEffect,useRef} from 'react';
import {GearSix} from './icons';
import {Handle,Position} from '@xyflow/react';
import {MessageBubble} from './MessageBubble';
export default function IOInspector({direction,items=[],acceptsLogs=false,onConfigure}){
 const seen=useRef(new Set(items.map(item=>item.id))),numericHigh=useRef(items.reduce((high,item)=>/^\d+$/.test(String(item.id))&&BigInt(item.id)>high?BigInt(item.id):high,BigInt(Date.now())*1000000n));
 const [pulse,setPulse]=useState(0);const timer=useRef(null);
 useEffect(()=>{let arrived=false;for(const item of items){if(seen.current.has(item.id))continue;seen.current.add(item.id);if(/^\d+$/.test(String(item.id))){const id=BigInt(item.id);if(id>numericHigh.current){numericHigh.current=id;arrived=true;}}else arrived=true;}if(arrived){clearTimeout(timer.current);setPulse(v=>v+1||1);timer.current=setTimeout(()=>setPulse(0),1000);}},[items]);
 useEffect(()=>()=>clearTimeout(timer.current),[]);
 const [hovered,setHovered]=useState(false),[locked,setLocked]=useState(true);const open=hovered||locked;const label=direction==='input'?'Input':'Output';
 return <div className={`io-inspector io-${direction} nodrag nopan ${open?'is-open':''}`} onClick={e=>e.stopPropagation()} onDoubleClick={e=>e.stopPropagation()} onPointerDown={e=>e.stopPropagation()} onMouseEnter={()=>setHovered(true)} onMouseLeave={()=>setHovered(false)} onFocus={e=>{if(e.target.matches(':focus-visible'))setHovered(true);}} onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget))setHovered(false);}}>
  {direction==='input'&&acceptsLogs&&<Handle type="target" position={Position.Left} id="logs-context" style={{top:10,background:'var(--input-color)'}} aria-label="Logs input tray connection"/>}
  <button className="io-inspector-bar" aria-label={`Inspect ${label.toLowerCase()}`} aria-expanded={open} aria-pressed={locked} title={locked?`Unlock ${label.toLowerCase()} history`:`Lock ${label.toLowerCase()} history open`} onClick={e=>{e.stopPropagation();setLocked(v=>!v);}}><span>{label}{locked?' · Locked':''}</span><span>{items.length}</span>{pulse>0&&<span key={pulse} className="io-event-flash" aria-hidden="true"/>}</button>
  {direction==='input'&&onConfigure&&<button className="input-shape-gear" aria-label="Configure input shape" title="Configure input" onClick={e=>{e.stopPropagation();onConfigure?.();}}><GearSix size={13}/></button>}
  {open&&<div className={`io-inspector-popover node-${direction}-chain`} role="region" aria-label={`${label} history`} tabIndex={0}>{items.length?items.map((item,i)=><MessageBubble key={item.id} direction={direction} item={item} newest={i===0}/>):<p className="io-inspector-empty">No {direction} recorded yet.</p>}</div>}
 </div>;
}
