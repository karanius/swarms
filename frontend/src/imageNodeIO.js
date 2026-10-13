import {inventoryReport} from './imageInventoryReport';
// These entries describe actual execution data, not the current editable folder selection.
export function imageNodeIO(job){
 const history=Object.fromEntries(['scope','scan','verify','agent','report','markdown'].map(kind=>[kind,{inputs:[],outputs:[]} ]));
 if(!job?.id)return history;
 const inventory=job.inventory,verification=job.verification;
 const roots=job.request?.roots||inventory?.roots;
 const time=inventory?.completedAt?new Date(inventory.completedAt).toLocaleTimeString():'';
 function record(kind,direction,value,suffix=''){
  if(value===undefined||value===null)return;
  const recordedTime=kind==='scan'&&direction==='outputs'&&inventory?time:'';
  history[kind][direction].push({id:`${job.id}:${kind}:${direction}${suffix}`,time:recordedTime,text:typeof value==='string'?value:JSON.stringify(value,null,2)});
 }
 if(roots){record('scope','inputs',job.request||{roots});record('scope','outputs',{roots,readOnly:true});record('scan','inputs',{roots});}
 if(inventory){record('scan','outputs',inventory);record('verify','inputs',inventory);}else if(job.progress?.entries){record('scan','outputs',{progress:job.progress},':progress:'+job.progress.entries);}
 if(verification)record('verify','outputs',verification);
 record('agent','inputs',job.agentInput);
 record('agent','outputs',job.explanation);
 if(inventory){
  const report={inventory,verification,explanation:job.explanation};
  record('markdown','inputs',report,job.explanation?':explained':':inventory');
  record('markdown','outputs',inventoryReport(job).markdown);
  record('report','inputs',report,job.explanation?':explained':':inventory');
  record('report','outputs',{imageFiles:inventory.imageFiles,coverage:verification?.coverage,formats:inventory.formats,unreadablePaths:inventory.unreadable,explanation:job.explanation},job.explanation?':explained':':inventory');
 }
 return history;
}
export function mergeImageIO(previous,current){
 const next={...previous};
 for(const [kind,streams] of Object.entries(current)){
  next[kind]={};
  for(const direction of ['inputs','outputs']){
   const old=previous[kind]?.[direction]||[],arrivals=streams[direction].filter(item=>!old.some(existing=>existing.id===item.id));
   next[kind][direction]=[...arrivals,...old.map(item=>streams[direction].find(latest=>latest.id===item.id)||item)].slice(0,5);
  }
 }
 return next;
}
