function updateEmotionCardActions(){
 for(const card of document.querySelectorAll('article.comparison-row,article.checkpoint-session-card')){
  const button=card.querySelector(':scope > .comparison-script > .comparison-delete');if(!button)continue;
  if(button.dataset.baseDisabled===undefined)button.dataset.baseDisabled=String(button.disabled);
  const active=directEmotionProfiles.some(p=>p.source_id===card.dataset.directReference&&p.runs.some(r=>['queued','running'].includes(r.state)));
  button.disabled=button.dataset.baseDisabled==='true'||active||directEmotionBusy||checkpointPending;
 }
}
async function consistentCheckpointAction(data){const result=await checkpointAction(data);if(!result)throw Error(checkpointNotice.textContent||'Could not update this item');return result}
// One deletion surface for legacy comparisons, checkpoint cards and direct recordings.
function showEmotionUndo(message,restore){comparisonNotice.replaceChildren(node('span',message+' '));const undo=checkpointButton('Undo',async()=>{await restore();comparisonNotice.replaceChildren(node('span','Restored.'));renderUnifiedEmotionTrash()});comparisonNotice.append(undo)}
function emotionTrashEntries(){
 const entries=[];
 for(const run of emotionRuns.filter(r=>r.deleted))entries.push({kind:'Comparison',label:run.target+' · '+run.text,restore:async()=>{run.deleted=false;saveEmotionRuns();renderComparisonLibrary()},purge:async()=>{emotionRuns=emotionRuns.filter(r=>r.id!==run.id);comparisonRows.get(run.id)?.remove();comparisonRows.delete(run.id);saveEmotionRuns();renderComparisonLibrary()}});
 for(const s of checkpointSessions){
  if(s.deleted)entries.push({kind:'Emotion test',label:s.style+' · '+s.text,restore:()=>consistentCheckpointAction({id:s.id,action:'trash',deleted:false}),purge:()=>consistentCheckpointAction({id:s.id,action:'purge'})});
  else for(const a of s.attempts.filter(a=>a.deleted&&!a.workspace_removed))entries.push({kind:'Actor attempt',label:s.style+' · seed '+a.seed+' · '+s.text,restore:()=>consistentCheckpointAction({id:s.id,action:'trash',actor_id:a.actor_id,deleted:false}),purge:()=>consistentCheckpointAction({id:s.id,action:'purge',actor_id:a.actor_id})});
 }
 for(const p of directEmotionProfiles)for(const r of p.runs.filter(r=>r.deleted&&!r.workspace_removed))entries.push({kind:'Direct recording',label:p.name+' · '+r.text,restore:async()=>{await api('/api/designer/direct-emotion-action',{id:p.id,action:'trash',recording_id:r.id,deleted:false});await pollDirectEmotionProfiles()},purge:async()=>{await api('/api/designer/direct-emotion-action',{id:p.id,action:'purge',recording_id:r.id});await pollDirectEmotionProfiles()}});
 return entries;
}
function renderUnifiedEmotionTrash(){
 updateEmotionCardActions();
 const entries=emotionTrashEntries();comparisonTrash.hidden=!entries.length;comparisonTrash.replaceChildren(node('summary','Trash ('+entries.length+')'));if(!entries.length)return;
 const empty=checkpointButton('Empty trash',async()=>{if(!confirm('Remove '+entries.length+' trashed items from this workspace permanently? Archived audio and passports will remain.'))return;empty.disabled=true;try{for(const e of entries)await e.purge();comparisonNotice.replaceChildren(node('span','Trash emptied. Archived audio and passports retained.'));renderUnifiedEmotionTrash()}catch(error){comparisonNotice.textContent=error.message}});comparisonTrash.append(empty);
 for(const entry of entries){const row=node('div');row.className='comparison-restore';row.append(node('span',entry.kind+' · '+entry.label));const restore=checkpointButton('Restore',async()=>{restore.disabled=true;try{await entry.restore();renderUnifiedEmotionTrash()}catch(error){comparisonNotice.textContent=error.message;restore.disabled=false}});row.append(restore);comparisonTrash.append(row)}
}
showComparisonUndo=function(run){showEmotionUndo('Comparison moved to Trash.',async()=>{run.deleted=false;saveEmotionRuns();renderComparisonLibrary()})};
renderComparisonTrash=renderUnifiedEmotionTrash;
const checkpointsBeforeConsistentTrash=renderCheckpoints;renderCheckpoints=function(...args){checkpointsBeforeConsistentTrash(...args);renderUnifiedEmotionTrash()};
// The global notice and trash stay in one predictable position around the saved-card library.
comparisonLibrary.before(comparisonNotice);checkpointArea.after(comparisonTrash);
renderUnifiedEmotionTrash();

checkpointNotice.style.display='none';
new MutationObserver(()=>{if(checkpointNotice.textContent)comparisonNotice.replaceChildren(node('span',checkpointNotice.textContent))}).observe(checkpointNotice,{childList:true,characterData:true,subtree:true});
