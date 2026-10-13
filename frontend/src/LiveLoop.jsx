import {Button} from './ui/components';
import React,{useEffect,useRef,useState} from 'react';
import {Cpu,Stop,Play,ArrowClockwise,ArrowsOutCardinal,Trash} from './ui/icons';
import FloatingController from './FloatingController';
export default function LiveLoop({onActivity,pipeline}){
 const cleared=localStorage.getItem('swarm-run-cleared')==='true';
 const logMode=pipeline==='logs';
 const api=logMode?'/log-api':'/swarm-api';
 const [listening,setListening]=useState(logMode||!cleared),[version,setVersion]=useState(0),[state,setState]=useState(cleared?'ready':'connecting'),[detail,setDetail]=useState(cleared?'Ready for a new run.':'Connecting to local runtime'),[count,setCount]=useState(0),[round,setRound]=useState(0),[events,setEvents]=useState([]),[error,setError]=useState(''),[busy,setBusy]=useState(false),[watchInfo,setWatchInfo]=useState('');
 const lastEvent=useRef(Date.now());
 const terminal=useRef(false),sourceRef=useRef(null);
 useEffect(()=>{
  if(!listening)return;
  setState('connecting');setError('');let received=false;
  const watchdog=setTimeout(()=>{if(!received){setError('No runtime events received. Reconnect to try again.');setState('disconnected');}},10000);
  const source=new EventSource(api+'/run');sourceRef.current=source;
  source.onmessage=event=>{
   lastEvent.current=Date.now();received=true;clearTimeout(watchdog);const value=JSON.parse(event.data);
   if(value.phase==='objective'){localStorage.setItem('swarm-run-cleared','true');terminal.current=false;setCount(0);setRound(0);setEvents([]);onActivity(value);}
   if(value.phase==='running'){setState('running');setDetail(value.agent);setRound(value.round);onActivity(value);}
   if(value.phase==='complete'){onActivity(value);setCount(value.turn);setRound(value.round);setEvents(prev=>[{id:value.outputId,text:value.output,time:value.time,task:value.agent,round:value.round},...prev.filter(e=>e.id!==value.outputId)].slice(0,12));}
   if(['watching','polling','retrying'].includes(value.phase)){setWatchInfo(value.agent);setState(value.phase==='retrying'?'retrying':'watching');setDetail(value.agent);setError(value.phase==='retrying'?value.error:'');onActivity({phase:'stopped'});}
   if(value.phase==='finished'){terminal.current=true;setState(value.reason?.startsWith('No further')?'stalled':'finished');setDetail(value.reason||'Three rounds completed');onActivity({phase:'stopped'});source.close();}
   if(value.phase==='error'){terminal.current=true;setError(value.error);setState('failed');setDetail('Run failed');onActivity({phase:'stopped'});source.close();}
  };
  source.onerror=()=>{if(logMode&&!terminal.current){setState('retrying');setDetail('Reconnecting to log watcher…');return;}clearTimeout(watchdog);setError('Connection to Swarms runtime closed.');setState('disconnected');onActivity({phase:'stopped'});source.close();};
  return()=>{clearTimeout(watchdog);source.close();};
 },[listening,version,onActivity]);
 useEffect(()=>{if(!logMode||!listening)return;const timer=setInterval(async()=>{try{const r=await fetch(api+'/status');if(!r.ok)return;const health=await r.json();if(health.running){setWatchInfo('Check '+health.pollCount+' · last checked '+new Date(health.lastPoll).toLocaleTimeString());if(Date.now()-lastEvent.current>25000){lastEvent.current=Date.now();setVersion(v=>v+1);}}}catch{setWatchInfo('Service reconnecting…');}},5000);return()=>clearInterval(timer);},[logMode,listening]);
 async function control(action){
  setBusy(true);setError('');
  try{
   if(action==='stop'){const r=await fetch(api+'/stop',{method:'POST'});if(!r.ok)throw Error('Could not stop run');setListening(false);setState('stopped');setDetail('Stopped by you. Current inference may finish.');onActivity({phase:'stopped'});}
   if(action==='start'){const r=await fetch(api+'/reset',{method:'POST'});if(!r.ok)throw Error('Previous inference is finishing. Try again shortly.');localStorage.removeItem('swarm-run-cleared');terminal.current=false;setListening(true);setVersion(v=>v+1);}
   if(action==='delete'){
    sourceRef.current?.close();setListening(false);
    const stop=await fetch(api+'/stop',{method:'POST'});if(!stop.ok)throw Error('Could not stop run for deletion.');
    let reset;
    for(let attempt=0;attempt<30;attempt++){
     reset=await fetch(api+'/reset',{method:'POST'});
     if(reset.ok||reset.status!==409)break;
     await new Promise(resolve=>setTimeout(resolve,1000));
    }
    if(!reset?.ok)throw Error('Inference is still finishing. Try Delete run again shortly.');
    localStorage.setItem('swarm-run-cleared','true');terminal.current=false;setCount(0);setRound(0);setEvents([]);setState('ready');setDetail('Ready for a new run.');onActivity({phase:'deleted'});
   }
   if(action==='reconnect'){setListening(true);setVersion(v=>v+1);}
  }catch(e){setError(e.message);}finally{setBusy(false);}
 }
 const active=['running','connecting','watching','retrying'].includes(state);
 const labels={watching:'Watching logs',retrying:'Retrying',ready:'Ready',connecting:'Connecting',running:'Running',finished:'Completed',stalled:'No further progress',failed:'Failed',stopped:'Stopped',disconnected:'Disconnected'};
 return <FloatingController header={<><Cpu size={20}/><strong>{logMode?'Log pipeline':'Swarms + EXO'}</strong><span className={`controller-status status-${state}`}><i/>{labels[state]}{logMode&&watchInfo&&<small className="watcher-heartbeat">{watchInfo}</small>}</span><ArrowsOutCardinal size={15} className="controller-grip"/></>}>
  <div className="controller-summary"><div><small>Local model</small><strong>Llama 3.2 3B</strong></div><div><small>Completed turns</small><strong>{count}</strong></div><div><small>Round</small><strong>{round} <span>/ 3</span></strong></div></div>
  <div className="controller-current"><small>{active?'Current activity':'Run outcome'}</small><p>{detail}</p></div>
  <div className="controller-controls"><Button className="primary" disabled={busy} onClick={()=>control(active?'stop':'start')}>{active?<Stop size={16}/>:<Play size={16}/>} {active?'Stop':'Start run'}</Button><Button disabled={busy||state==='ready'} onClick={()=>control('reconnect')}><ArrowClockwise size={16}/> Reconnect</Button><Button disabled={busy} onClick={()=>control('delete')}><Trash size={16}/> Delete run</Button></div>
  {error&&<p className="controller-error" role="status">{error}</p>}
  <div className="controller-feed-heading"><h3>Latest outputs</h3><span>{events.length} shown</span></div>
  <div className="controller-feed">{events.length?events.map(e=><article key={e.id}><div><strong>{e.task}</strong><time>{e.time}</time></div><small>Round {e.round}</small><p>{e.text}</p></article>):<p className="controller-empty">Outputs appear here as agents finish their turns.</p>}</div>
  <footer className="controller-footer">{logMode?'Continuous Langfuse observation processing':'Task: local inference deployment review'}</footer>
 </FloatingController>;
}
