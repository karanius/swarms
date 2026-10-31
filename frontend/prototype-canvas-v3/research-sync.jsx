import {useEffect,useRef,useState} from 'react';
const REVISION_KEY='swarms.v3.research.repository-revision';
export function useResearchSync(state,onLoad){
 const latest=useRef(state);latest.current=state;
 const load=useRef(onLoad);load.current=onLoad;
 const revision=useRef(null),queue=useRef(Promise.resolve()),blocked=useRef(false);
 const [ready,setReady]=useState(false),[status,setStatus]=useState('Connecting repository storage…');
 const request=async(path='',options)=>{const response=await fetch('/research-api'+path,options);const result=await response.json();if(!response.ok)throw Error(result.error||'Repository request failed.');return result;};
 useEffect(()=>{let active=true;request().then(remote=>{if(!active)return;const local=latest.current;const same=JSON.stringify(local.papers)===JSON.stringify(remote.document.papers);const remembered=localStorage.getItem(REVISION_KEY);
  if(remote.exists&&!same){if(!local.papers.length&&!local.clearedPapers?.length)load.current(remote.document.papers);else if(remembered!==remote.revision){blocked.current=true;setStatus('Repository and browser drafts differ. Browser edits are preserved; resolve the difference before syncing.');return;}}
  revision.current=remote.revision;setReady(true);setStatus(remote.status.message);
 }).catch(()=>{if(active)setStatus('Browser autosave only. Repository storage is unavailable.');});return ()=>{active=false;};},[]);
 useEffect(()=>{if(!ready||blocked.current||state.error)return;let active=true;
 const timer=setTimeout(()=>{queue.current=queue.current.then(async()=>{if(blocked.current)return;try{const result=await request('',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({document:{schemaVersion:1,papers:state.papers},baseRevision:revision.current})});revision.current=result.revision;localStorage.setItem(REVISION_KEY,result.revision);if(active)setStatus(result.status.message);}catch(error){blocked.current=true;if(active)setStatus(error.message);}});},700);
 return ()=>{active=false;clearTimeout(timer);};},[ready,state.papers]);
 useEffect(()=>{if(!ready)return;let active=true;const timer=setInterval(()=>{if(blocked.current)return;request().then(result=>{if(active)setStatus(result.status.message);}).catch(()=>{if(active)setStatus('Saved in browser; repository connection unavailable.');});},3000);return ()=>{active=false;clearInterval(timer);};},[ready]);
 const retry=async()=>{setStatus('Retrying GitHub push…');try{const result=await request('/push',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});setStatus(result.status.message);}catch(error){setStatus(error.message);}};
 return {ready,status,retry};
}
