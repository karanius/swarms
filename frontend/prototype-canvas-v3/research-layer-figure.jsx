import React,{useEffect,useMemo,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {CSS2DRenderer,CSS2DObject} from 'three/addons/renderers/CSS2DRenderer.js';
import './research-layer-figure.css';

export default function ResearchLayerFigure({artifact}){
 const mount=useRef(null),api=useRef(null);
 const [fallback,setFallback]=useState('');
 const layers=useMemo(()=>[...(artifact?.layers??[])].sort((a,b)=>(Number(a.order)||0)-(Number(b.order)||0)),[artifact]);
 const nodes=artifact?.nodes??[],edges=artifact?.edges??[];
 useEffect(()=>{
  const host=mount.current;if(!host)return;
  let renderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'low-power'});}catch{setFallback('3D view unavailable. The complete layer and connection list is below.');return;}
  setFallback('');
  const scene=new THREE.Scene();scene.background=new THREE.Color('#111820');
  const camera=new THREE.PerspectiveCamera(40,1,.1,2000);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  renderer.domElement.setAttribute('aria-hidden','true');host.append(renderer.domElement);
  const labels=new CSS2DRenderer();labels.domElement.className='research-layer-labels';host.append(labels.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minDistance=3;controls.maxDistance=1000;
  const finite=value=>Number.isFinite(Number(value))?Number(value):0;
  const positions=new Map(),heightByLayer=new Map(layers.map((layer,index)=>[layer.id,index*3.1]));
  const xs=nodes.map(node=>finite(node.position?.x)),ys=nodes.map(node=>finite(node.position?.y));
  const minX=Math.min(0,...xs),maxX=Math.max(1,...xs),minY=Math.min(0,...ys),maxY=Math.max(1,...ys);
  // Keep authored relative positions while fitting pixel-style and world-style coordinates.
  const scale=Math.max(maxX-minX,maxY-minY)>40?0.018:1;
  const cx=(minX+maxX)/2,cz=(minY+maxY)/2;
  const width=Math.max(10,(maxX-minX)*scale+5),depth=Math.max(6,(maxY-minY)*scale+4);
  const addLabel=(text,position,className)=>{const element=document.createElement('div');element.className=className;element.textContent=text;const label=new CSS2DObject(element);label.position.copy(position);scene.add(label);};
  for(const [index,layer] of layers.entries()){
   const y=index*3.1;
   const plane=new THREE.Mesh(new THREE.PlaneGeometry(width,depth),new THREE.MeshBasicMaterial({color:index%2?0x41645b:0x354d67,transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false}));plane.rotation.x=-Math.PI/2;plane.position.y=y;scene.add(plane);
   const outline=new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints([[-width/2,y,-depth/2],[width/2,y,-depth/2],[width/2,y,depth/2],[-width/2,y,depth/2]].map(point=>new THREE.Vector3(...point))),new THREE.LineBasicMaterial({color:0x547185,transparent:true,opacity:.7}));scene.add(outline);
   addLabel(layer.label,new THREE.Vector3(-width/2+1,y+.22,depth/2-.35),'research-layer-plane-label');
  }
  for(const node of nodes){
   const position=new THREE.Vector3((finite(node.position?.x)-cx)*scale,(heightByLayer.get(node.layer)??0)+.2,(finite(node.position?.y)-cz)*scale);positions.set(node.id,position);
   const mesh=new THREE.Mesh(new THREE.BoxGeometry(1.8,.24,.8),new THREE.MeshBasicMaterial({color:0x416376}));mesh.position.copy(position);scene.add(mesh);
   addLabel(node.label,position.clone().add(new THREE.Vector3(0,.4,0)),'research-layer-node-label');
  }
  for(const edge of edges){
   const source=positions.get(edge.source),target=positions.get(edge.target);if(!source||!target)continue;
   const color=edge.kind==='membership'?0x95cab5:edge.kind==='feedback'?0xe2b777:0xbacddd;
   let points=[source,target];
   if(edge.kind==='feedback'){
    const middle=source.clone().lerp(target,.5).add(new THREE.Vector3(0,1.5,1));points=new THREE.QuadraticBezierCurve3(source,middle,target).getPoints(24);
   }
   const material=edge.kind==='data'?new THREE.LineBasicMaterial({color}):new THREE.LineDashedMaterial({color,dashSize:.18,gapSize:.12});
   const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),material);if(edge.kind!=='data')line.computeLineDistances();scene.add(line);
   if(edge.kind!=='membership'){
    const end=points.at(-1),previous=points.at(-2),direction=end.clone().sub(previous);if(direction.length()>.001){direction.normalize();scene.add(new THREE.ArrowHelper(direction,end.clone().addScaledVector(direction,-.55),.4,color,.22,.13));}
   }
  }
  const target=new THREE.Vector3(0,Math.max(0,layers.length-1)*1.55,0),span=Math.max(width,depth,layers.length*3.1,8);
  const render=()=>{renderer.render(scene,camera);labels.render(scene,camera);};
  const reset=()=>{camera.position.copy(target).add(new THREE.Vector3(span*.9,span*.7,span*1.1));controls.target.copy(target);controls.update();render();};
  const resize=()=>{const {width:w,height:h}=host.getBoundingClientRect();if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h);labels.setSize(w,h);render();};
  const onContextLost=event=>{event.preventDefault();setFallback('The 3D view lost graphics access. The complete layer and connection list remains below.');};
  renderer.domElement.addEventListener('webglcontextlost',onContextLost);
  controls.addEventListener('change',render);
  const observer=new ResizeObserver(resize);observer.observe(host);api.current={reset};reset();resize();
  return()=>{api.current=null;observer.disconnect();controls.removeEventListener('change',render);controls.dispose();renderer.domElement.removeEventListener('webglcontextlost',onContextLost);scene.traverse(object=>{object.geometry?.dispose();if(object.material)for(const material of Array.isArray(object.material)?object.material:[object.material])material.dispose();if(object instanceof CSS2DObject)object.element.remove();});renderer.dispose();host.replaceChildren();};
 },[artifact,layers]);
 const nodeLabel=id=>nodes.find(node=>node.id===id)?.label??id;
 const stop=event=>event.stopPropagation();
 return <figure className="research-layer-figure" contentEditable={false} onPointerDown={stop} onPointerMove={stop} onPointerUp={stop} onClick={stop} onDoubleClick={stop} onWheel={stop} onKeyDown={stop} onContextMenu={event=>{event.preventDefault();stop(event);}}>
  <figcaption><strong>{artifact?.title||'Layer design'}</strong><button type="button" disabled={Boolean(fallback)} onClick={()=>api.current?.reset()}>Reset view</button></figcaption>
  <div className="research-artifact-stage research-layer-stage" ref={mount}/>
  {fallback&&<p className="research-layer-fallback" role="status">{fallback}</p>}
  <p className="research-layer-legend">Drag to orbit · right-drag to pan · scroll to zoom. Solid arrows: data. Mint dashes: membership. Amber dashes: feedback.</p>
  <details className="research-layer-equivalent" open={Boolean(fallback)}><summary>Layers and connections as text</summary>
   {layers.map(layer=><section key={layer.id}><strong>{layer.label}</strong><ul>{nodes.filter(node=>node.layer===layer.id).map(node=><li key={node.id}>{node.label}{node.description?` — ${node.description}`:''}</li>)}</ul></section>)}
   <ul>{edges.map(edge=><li key={edge.id}>{nodeLabel(edge.source)} → {nodeLabel(edge.target)} ({edge.kind})</li>)}</ul>
   {!nodes.length&&<p>No nodes in this design.</p>}
  </details>
 </figure>;
}
