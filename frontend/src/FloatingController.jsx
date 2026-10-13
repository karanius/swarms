import React,{useEffect,useRef,useState} from 'react';
import {Minus,ArrowsOutSimple} from './ui/icons';
const minimum={w:310,h:290};
export default function FloatingController({children,header}){
 const [minimized,setMinimized]=useState(true);
 const minimizedRef=useRef(true);
 const element=useRef(null),gesture=useRef(null);
 const bounds=useRef(null);
 const paint=rect=>{
  const maxW=Math.max(240,window.innerWidth-24),maxH=Math.max(220,window.innerHeight-24);
  rect.w=Math.min(maxW,Math.max(Math.min(minimum.w,maxW),rect.w));rect.h=Math.min(maxH,Math.max(Math.min(minimum.h,maxH),rect.h));
  rect.x=Math.min(Math.max(12,rect.x),window.innerWidth-rect.w-12);rect.y=Math.min(Math.max(12,rect.y),window.innerHeight-rect.h-12);
  bounds.current=rect;Object.assign(element.current.style,{left:`${rect.x}px`,top:`${rect.y}px`,width:`${rect.w}px`,height:`${minimizedRef.current?54:rect.h}px`});
 };
 useEffect(()=>{
  let saved;try{saved=JSON.parse(localStorage.getItem('swarm-controller-window'));}catch{}
  paint(saved&&['x','y','w','h'].every(k=>Number.isFinite(saved[k]))?saved:{x:window.innerWidth-408,y:window.innerHeight-402,w:390,h:384});
  const resize=()=>paint({...bounds.current});window.addEventListener('resize',resize);return()=>window.removeEventListener('resize',resize);
 },[]);
 const begin=(event,edge)=>{
  if(event.button!==0||event.target.closest('button,a,input'))return;
  event.preventDefault();event.stopPropagation();gesture.current={edge,x:event.clientX,y:event.clientY,rect:{...bounds.current}};event.currentTarget.setPointerCapture(event.pointerId);
 };
 const move=event=>{
  const g=gesture.current;if(!g)return;const dx=event.clientX-g.x,dy=event.clientY-g.y,r={...g.rect};
  if(g.edge==='move'){r.x+=dx;r.y+=dy;}
  else{if(g.edge.includes('e'))r.w+=dx;if(g.edge.includes('s'))r.h+=dy;if(g.edge.includes('w')){r.w-=dx;r.x+=dx;if(r.w<minimum.w){r.x=g.rect.x+g.rect.w-minimum.w;r.w=minimum.w;}}if(g.edge.includes('n')){r.h-=dy;r.y+=dy;if(r.h<minimum.h){r.y=g.rect.y+g.rect.h-minimum.h;r.h=minimum.h;}}}
  paint(r);
 };
 const end=()=>{gesture.current=null;try{localStorage.setItem('swarm-controller-window',JSON.stringify(bounds.current));}catch{}};
 const keyboard=(event,edge)=>{
  const arrows={ArrowLeft:[-12,0],ArrowRight:[12,0],ArrowUp:[0,-12],ArrowDown:[0,12]};const delta=arrows[event.key];if(!delta)return;event.preventDefault();gesture.current={edge,x:0,y:0,rect:{...bounds.current}};move({clientX:delta[0],clientY:delta[1]});end();
 };
 const toggle=()=>{const next=!minimizedRef.current;minimizedRef.current=next;setMinimized(next);paint({...bounds.current});};
 return <aside ref={element} className={`floating-controller ${minimized?'is-minimized':''}`} aria-label="Swarms runtime controller"><header className="controller-drag" onPointerDown={e=>begin(e,'move')} onPointerMove={move} onPointerUp={end} onPointerCancel={end} tabIndex={0} aria-label="Move controller window" onKeyDown={e=>keyboard(e,'move')}>{header}<button className="controller-minimize" aria-label={minimized?'Restore controller':'Minimize controller'} title={minimized?'Restore':'Minimize'} onClick={toggle}>{minimized?<ArrowsOutSimple size={16}/>:<Minus size={16}/>}</button></header><div className="controller-content" hidden={minimized}>{children}</div>{!minimized&&['n','e','s','w','ne','se','sw','nw'].map(edge=><div key={edge} className={`controller-resize resize-${edge}`} role="separator" tabIndex={0} aria-label={`Resize controller ${edge}`} onPointerDown={e=>begin(e,edge)} onPointerMove={move} onPointerUp={end} onPointerCancel={end} onKeyDown={e=>keyboard(e,edge)}/>)}</aside>;
}
