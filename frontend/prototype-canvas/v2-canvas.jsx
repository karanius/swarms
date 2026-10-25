import React, {useEffect,useRef,useState} from 'react';
import V2Library from './v2-library.jsx';
import MachineSequence from './machine-sequence.jsx';
import './v2-canvas.css';

export default function VersionTwo(){
 const surface=useRef(null),native=useRef(null);
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
 return <main className="v2-canvas"><div className="v2-native-surface" ref={surface}/>{error&&<div role="alert" className="v2-native-error">{error}</div>}<V2Library onAddComponent={ready?type=>native.current.add(type):undefined}/><MachineSequence/></main>;
}
