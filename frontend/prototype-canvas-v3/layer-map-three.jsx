import React,{useEffect,useMemo,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {CSS2DRenderer,CSS2DObject} from 'three/addons/renderers/CSS2DRenderer.js';
import LayerMap from './layer-map.jsx';
import {layerSceneModel} from './layer-scene-model.mjs';
import './layer-map.css';
export default function LayerMapThree(props){
 const {graph,upperGraph,items,selectedIds,onSelect,onPackage,onOpen,onReady}=props;
 const mount=useRef(null),sceneApi=useRef(null),callbacks=useRef(props);callbacks.current=props;
 const [fallback,setFallback]=useState(''),[inspected,setInspected]=useState(null);
 const signature=JSON.stringify({nodes:graph.nodes.map(node=>({id:node.id,type:node.type,label:node.data.node?.display_name})),edges:graph.edges.map(edge=>({id:edge.id,source:edge.source,target:edge.target})),upper:upperGraph.nodes.map(node=>node.data),items:items.map(item=>({id:item.id,children:item.realization?.childNodeIds??item.assembly.nodes.map(node=>node.id)}))});
 const model=useMemo(()=>layerSceneModel(graph,upperGraph,items),[signature]);
 useEffect(()=>{
  if(!mount.current)return;
  let renderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'low-power'});}catch{setFallback('WebGL is unavailable in this browser. Showing the same graph in 2D.');return;}
  setFallback('');
  const host=mount.current,scene=new THREE.Scene();scene.background=new THREE.Color('#10151d');
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.domElement.setAttribute('aria-label','Three.js layered DAG');renderer.domElement.dataset.renderer='three-webgl';host.append(renderer.domElement);
  const labels=new CSS2DRenderer();labels.domElement.className='three-layer-labels';Object.assign(labels.domElement.style,{position:'absolute',inset:'0',pointerEvents:'none'});host.append(labels.domElement);
  const camera=new THREE.PerspectiveCamera(42,1,.1,200);camera.position.set(11,10,16);
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,2.1,0);controls.enableDamping=true;controls.minDistance=7;controls.maxDistance=60;controls.maxPolarAngle=Math.PI*.88;
  scene.add(new THREE.HemisphereLight(0xcfe8ff,0x202733,2));const light=new THREE.DirectionalLight(0xffffff,2.2);light.position.set(4,12,7);scene.add(light);
  const dropPlanes=[];
  const width=Math.max(15,model.components.length*4.2+4,model.composites.length*4.5+4);
  const addLabel=(text,position,className)=>{const element=document.createElement('div');element.className=className;element.textContent=text;const object=new CSS2DObject(element);object.position.copy(position);scene.add(object);return object;};
  for(const [y,title] of [[0,'COMPONENTS'],[4.3,'COMPOSITE']]){
   const plane=new THREE.Mesh(new THREE.PlaneGeometry(width,6),new THREE.MeshBasicMaterial({color:y?'#37594e':'#294059',transparent:true,opacity:.17,side:THREE.DoubleSide,depthWrite:false}));plane.rotation.x=-Math.PI/2;plane.position.y=y;plane.userData.plane=y?'Composite Components':'Components';scene.add(plane);dropPlanes.push(plane);
   const points=[[-width/2,y,-3],[width/2,y,-3],[width/2,y,3],[-width/2,y,3]].map(p=>new THREE.Vector3(...p));const outline=new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:y?0x668c7b:0x526e8c,transparent:true,opacity:.7}));scene.add(outline);
   addLabel(title,new THREE.Vector3(-width/2+1,y+.22,2.7),'three-plane-label');
  }
  const grid=new THREE.GridHelper(width,Math.ceil(width),0x344757,0x263442);grid.position.y=-.02;scene.add(grid);
  const positions=new Map([...model.components,...model.composites].map(node=>[node.id,new THREE.Vector3(...node.position)])),meshes=new Map();
  for(const node of [...model.components,...model.composites]){
   const isUpper=Boolean(node.itemId);const mesh=new THREE.Mesh(new THREE.BoxGeometry(3.25,.18,1.25),new THREE.MeshStandardMaterial({color:isUpper?0x355c54:0x2c4056,roughness:.8,metalness:.1}));mesh.position.copy(positions.get(node.id));scene.add(mesh);
   const button=document.createElement('button');button.className='three-layer-node '+(isUpper?'is-composite':'');button.setAttribute('aria-label',isUpper?'Inspect composite '+node.label:'Select component '+node.label);button.innerHTML='';const title=document.createElement('strong');title.textContent=node.label;const detail=document.createElement('small');detail.textContent=isUpper?node.children.length+' components · double-click to open':node.type;button.append(title,detail);button.style.pointerEvents='auto';
   button.onclick=event=>{const current=callbacks.current;if(isUpper)setInspected(node.itemId);else current.onSelect(event.shiftKey?(current.selectedIds.includes(node.id)?current.selectedIds.filter(id=>id!==node.id):[...current.selectedIds,node.id]):[node.id]);};
   button.ondblclick=()=>{if(isUpper)callbacks.current.onOpen(callbacks.current.items.find(item=>item.id===node.itemId));};
   const label=new CSS2DObject(button);label.position.copy(mesh.position).add(new THREE.Vector3(0,.45,0));scene.add(label);mesh.userData.label=button;meshes.set(node.id,mesh);
  }
  for(const edge of model.edges){
   const source=positions.get(edge.source).clone(),target=positions.get(edge.target).clone();
   if(edge.kind==='membership'){
    const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([source,target]),new THREE.LineDashedMaterial({color:0x8fd0b5,dashSize:.15,gapSize:.1}));line.computeLineDistances();scene.add(line);
   }else{
    const direction=target.clone().sub(source);const length=direction.length();direction.normalize();source.addScaledVector(direction,1.7);scene.add(new THREE.ArrowHelper(direction,source,Math.max(.1,length-3.4),0xb0c4da,.28,.17));
   }
  }
  let dirty=true,frame;const render=()=>{frame=requestAnimationFrame(render);if(controls.update()||dirty){renderer.render(scene,camera);labels.render(scene,camera);dirty=false;}};
  controls.addEventListener('change',()=>{dirty=true;});
  const resize=()=>{const rect=host.getBoundingClientRect();if(!rect.width||!rect.height)return;camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();renderer.setSize(rect.width,rect.height);labels.setSize(rect.width,rect.height);dirty=true;};
  const observer=new ResizeObserver(resize);observer.observe(host);resize();render();
  const reset=()=>{camera.position.set(11,10,16);controls.target.set(0,2.1,0);dirty=true;};
  sceneApi.current={dropPlane(x,y){const rect=renderer.domElement.getBoundingClientRect();const ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2((x-rect.left)/rect.width*2-1,-(y-rect.top)/rect.height*2+1),camera);return ray.intersectObjects(dropPlanes)[0]?.object.userData.plane;},meshes,render:()=>{dirty=true;},reset};onReady?.({fitView:reset});
  for(const id of callbacks.current.selectedIds){const mesh=meshes.get(id);if(mesh){mesh.material.color.set(0x416f68);mesh.userData.label.setAttribute('aria-pressed','true');}}
  return ()=>{cancelAnimationFrame(frame);observer.disconnect();controls.dispose();scene.traverse(object=>{object.geometry?.dispose();if(object.material){for(const material of Array.isArray(object.material)?object.material:[object.material])material.dispose();}if(object instanceof CSS2DObject)object.element.remove();});renderer.dispose();host.replaceChildren();sceneApi.current=null;};
 },[model]);
 useEffect(()=>{const api=sceneApi.current;if(!api)return;for(const node of model.components){const mesh=api.meshes.get(node.id);if(mesh){const selected=selectedIds.includes(node.id);mesh.material.color.set(selected?0x416f68:0x2c4056);mesh.userData.label.classList.toggle('is-selected',selected);mesh.userData.label.setAttribute('aria-pressed',String(selected));}}api.render();},[selectedIds,model]);
 const item=items.find(item=>item.id===inspected);
 if(fallback)return <div className="three-layer-fallback"><p role="status">{fallback}</p><LayerMap {...props}/></div>;
 return <div className="layer-map three-layer-map"><div className="layer-map-controls"><div><strong>Same system · two planes</strong><span>Drag to orbit · right-drag to pan · scroll to zoom</span></div><button onClick={()=>onSelect(model.components.map(node=>node.id))}>Select all components</button><button disabled={!selectedIds.length} onClick={onPackage}>Package {selectedIds.length||''} selected</button><button onClick={()=>sceneApi.current?.reset()}>Reset camera</button></div><div className="three-layer-scene" ref={mount} onDragOver={event=>{event.preventDefault();event.dataTransfer.dropEffect='copy';}} onDrop={event=>{event.preventDefault();const plane=sceneApi.current?.dropPlane(event.clientX,event.clientY);if(!plane){props.onError?.('Drop onto a visible plane.');return;}const id=event.dataTransfer.getData('application/x-canvas-custom');if(id)props.onDropItem?.(id,plane);else props.onError?.('Components belong on Components. Add them in Nodes view.');}}/><div className="three-layer-legend">{model.components.length} components · {model.composites.length} composites · {model.edges.filter(edge=>edge.kind==='membership').length} membership links</div>{item&&<aside className="layer-map-inspector"><header><strong>{item.name}</strong><button onClick={()=>setInspected(null)}>Close</button></header><p>Same component identities: {item.realization?.childNodeIds.length??item.assembly.nodes.length}</p><h3>Inputs</h3>{item.contract?.inputs.map(port=><p key={port.id}>{port.name}<small>{port.dataTypes.join(', ')}</small></p>)}<h3>Outputs</h3>{item.contract?.outputs.map(port=><p key={port.id}>{port.name}<small>{port.dataTypes.join(', ')}</small></p>)}<p>Solid arrows carry data. Dashed links identify the components represented by this composite.</p><button onClick={()=>onOpen(item)}>Open component DAG</button></aside>}</div>;
}
