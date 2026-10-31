let directEmotionProfiles=[],directEmotionPolling=false,directEmotionBusy=false;
const directEmotionPanels=new Set();
function makeDirectEmotionPanel(sourceId,title,seed,script){
 const panel=node('div');panel.className='result-direct-body';
 if(!sourceId){panel.append(node('h4','Finish this emotion test first'),node('p','This test has not produced a Santa recording yet. Review the actor, then convert the approved take. That Santa recording becomes the reference for direct generation.'));panel.append(checkpointButton('Continue developing this emotion',()=>openEmotionCheckpoint(panel.closest('article'),0)));return panel}

 panel.append(node('h4','Generate directly from this '+title.toLowerCase()+' voice'));
 const qualification=node('p','Experimental direct route · judge emotion and identity on new sentences.');panel.append(qualification);
 if(sourceId){const reference=node('details');reference.append(node('summary','Hear this emotional Santa reference'),checkpointAudio(sourceId,'Emotional Santa reference for direct mode'),makePassport(sourceId));panel.append(reference)}else panel.append(node('p','Finish and keep a Santa recording in Develop emotion first.'));
 const label=node('label','What should Santa say next?');const sentence=node('textarea');sentence.rows=2;sentence.value='I told you to leave those presents alone, and I expect you to listen.';sentence.setAttribute('aria-label','New sentence for '+title);label.append(sentence);const count=node('p');count.className='hint';panel.append(label,count);
 const advanced=node('details');advanced.append(node('summary','Generation settings'));const settingsSeed=checkpointNumber('Seed',seed??65),steps=checkpointNumber('Steps',10,1,64),guidance=checkpointNumber('Guidance',2,.1,8,.1);advanced.append(settingsSeed.label,steps.label,guidance.label,node('p','VoxCPM2 · one pass using this emotional Santa recording. No intermediate actor or conversion.'));panel.append(advanced);
 const draftKey='santa.direct-emotion.draft.'+sourceId;
 try{const draft=JSON.parse(localStorage.getItem(draftKey)||'{}');if(draft.text)sentence.value=draft.text;for(const [key,field] of [['seed',settingsSeed.input],['steps',steps.input],['guidance',guidance.input]])if(draft[key]!==undefined)field.value=draft[key]}catch{}
 function persistDraft(){try{localStorage.setItem(draftKey,JSON.stringify({text:sentence.value,seed:settingsSeed.input.value,steps:steps.input.value,guidance:guidance.input.value}))}catch{}}
 const status=node('p');status.setAttribute('role','status');status.setAttribute('aria-live','polite');
 const generate=node('button','Generate direct line');generate.type='button';generate.className='primary';panel.append(generate,status);
 const resultList=node('div');resultList.className='direct-saved-results';panel.append(resultList);const trash=node('details');trash.className='direct-sample-trash';panel.append(trash);let signature='';
 function profile(){return directEmotionProfiles.find(p=>p.source_id===sourceId&&!p.deleted)}
 async function action(data){if(directEmotionBusy)return;directEmotionBusy=true;updateAllDirectPanels();try{const result=await api('/api/designer/direct-emotion-action',data);directEmotionProfiles=directEmotionProfiles.map(p=>p.id===result.id?result:p);status.textContent='Saved.';render(true);if(window.renderUnifiedEmotionTrash)renderUnifiedEmotionTrash();if(data.action==='trash'&&data.deleted)showEmotionUndo('Recording moved to Trash.',()=>action({...data,deleted:false}))}catch(error){status.textContent=error.message}finally{directEmotionBusy=false;updateAllDirectPanels()}}
 function update(){const n=voiceWordCount(sentence.value);count.textContent=n+' / 35 words';sentence.setAttribute('aria-invalid',String(n>35));const running=directEmotionProfiles.some(p=>p.runs.some(r=>['queued','running'].includes(r.state)));generate.disabled=!sourceId||!sentence.value.trim()||n>35||directEmotionBusy||running;generate.textContent=profile()?.runs.some(r=>['queued','running'].includes(r.state))?'Generating direct line…':'Generate direct line';}
 function render(force=false){
  const p=profile();update();const sig=JSON.stringify(p);if(!force&&sig===signature)return;signature=sig;
  const n=p?.qualifying_by_engine?.VoxCPM2||0;qualification.textContent=n>=3?'Direct emotion kept on '+n+' different new sentences.':'Experimental direct route · '+n+' of 3 different new sentences kept. Listen for both emotion and Santa’s identity.';
  resultList.replaceChildren();trash.replaceChildren();const removed=p?.runs.filter(r=>r.deleted)||[];trash.hidden=!removed.length;trash.append(node('summary','Trash ('+removed.length+')'));
  if(!p||!p.runs.length){resultList.append(node('p','Your generated lines will be saved here.'));return}
  for(const r of p.runs.slice().reverse()){
   if(r.deleted){const row=node('p',r.text);row.append(checkpointButton('Restore',()=>action({id:p.id,action:'trash',recording_id:r.id,deleted:false})));trash.append(row);continue}
   const row=node('section');row.className='direct-generated-row';if(r.qualification)row.append(node('strong','Qualification line '+r.qualification.case+' of 3'));row.append(node('p',r.text));
   if(r.state==='saved'){
    row.append(checkpointAudio(r.id,'Direct Santa result'),node('p',r.engine+' · seed '+r.seed+' · '+Math.round(r.elapsed_seconds||0)+' seconds · '+(r.word_check?.exact_words?'Words checked':'Word check needs review')),makePassport(r.id));
    const review=node('div');review.className='direct-preview-actions';const rating=node('select');rating.setAttribute('aria-label','Rate direct recording '+r.id.slice(0,8));for(const [choice,text] of [['','Not rated'],['keep','Good'],['emotion','Emotion too weak'],['identity','Voice changed'],['words','Words wrong'],['quality','Unnatural delivery']])rating.append(new Option(text,choice));rating.value=r.verdict||'';rating.onchange=()=>{if(rating.value)action({id:p.id,action:'review',recording_id:r.id,choice:rating.value})};review.append(rating);const remove=checkpointButton('Delete',()=>action({id:p.id,action:'trash',recording_id:r.id,deleted:true}));review.append(remove);row.append(review);
   }else row.append(node('p',r.state==='failed'?'Failed: '+r.error:'Generating Santa directly. The recording will appear here when ready.'));
   resultList.append(row);
  }
 }
 generate.onclick=async()=>{
  if(generate.disabled)return;directEmotionBusy=true;persistDraft();updateAllDirectPanels();status.textContent='Starting direct generation…';
  try{let p=profile();if(!p){p=await api('/api/designer/direct-emotions',{source_id:sourceId,accept_reference:true});directEmotionProfiles.push(p)}const result=await api('/api/designer/direct-emotion-action',{id:p.id,action:'generate',token:crypto.randomUUID(),text:sentence.value,seed:Number(settingsSeed.input.value),steps:Number(steps.input.value),guidance:Number(guidance.input.value),engine:'vox'});directEmotionProfiles=directEmotionProfiles.map(p=>p.id===result.id?result:p);status.textContent='Generating and saving a new line from this reference.';render(true)}catch(error){status.textContent=error.message}finally{directEmotionBusy=false;updateAllDirectPanels()}
 };
 for(const el of [sentence,settingsSeed.input,steps.input,guidance.input])el.addEventListener('input',()=>{persistDraft();update()});
 const controller={panel,update,render};directEmotionPanels.add(controller);render(true);return panel;
}
function updateAllDirectPanels(){for(const c of directEmotionPanels)c.update();if(window.updateEmotionCardActions)updateEmotionCardActions()}
async function pollDirectEmotionProfiles(){if(directEmotionPolling)return;directEmotionPolling=true;try{directEmotionProfiles=(await api('/api/designer/direct-emotions')).profiles;for(const c of directEmotionPanels){if(!c.panel.isConnected){directEmotionPanels.delete(c);continue}c.render()}if(window.renderUnifiedEmotionTrash)renderUnifiedEmotionTrash()}catch(error){for(const c of directEmotionPanels){const status=c.panel.querySelector('[role=status]');if(status)status.textContent=error.message}}finally{directEmotionPolling=false}}
// Real direct generation stays inside each saved emotion card.
function mountEmotionModes(host,sourceId,title,seed,script,legacy=false){
 if(host.querySelector(':scope > .result-mode-switch'))return;host.dataset.directReference=sourceId||'';
 const header=legacy?host.querySelector(':scope > .comparison-script'):null;
 const body=node('div');body.className='result-development-body';
 const existing=[...host.children].filter(child=>child!==header);for(const child of existing)body.append(child);
 const nav=node('nav');nav.className='result-mode-switch';nav.setAttribute('aria-label',title+' workflow modes');
 const develop=node('button','Develop emotion'),direct=node('button','Use this emotion');develop.type=direct.type='button';nav.append(develop,direct);
 const preview=makeDirectEmotionPanel(sourceId,title,seed,script);preview.hidden=true;
 function select(mode){try{localStorage.setItem('santa.emotion-card-mode.'+(sourceId||script),mode)}catch{}body.hidden=mode!=='develop';preview.hidden=mode!=='direct';develop.setAttribute('aria-pressed',String(mode==='develop'));direct.setAttribute('aria-pressed',String(mode==='direct'));host.querySelectorAll('audio').forEach(a=>a.pause())}
 develop.onclick=()=>select('develop');direct.onclick=()=>select('direct');host.append(nav,body,preview);let mode='develop';try{mode=localStorage.getItem('santa.emotion-card-mode.'+(sourceId||script))||mode}catch{}select(mode);host.classList.add('has-result-modes');
}
const comparisonsBeforeModes=renderComparisonLibrary;
renderComparisonLibrary=function(){comparisonsBeforeModes();for(const run of emotionRuns){const row=comparisonRows.get(run.id);if(!row||row.hidden)continue;const item=run.batch?.items?.[1],record=allTestRecords.find(r=>r.id===item?.id);mountEmotionModes(row,record?.state==='saved'?record.id:null,run.target,record?.request?.seed,run.text,true)}};
function mountCurrentCheckpointModes(){
 for(const s of checkpointSessions){const card=checkpointCards.get(s.id);if(!card||card.hidden)continue;
  const a=s.attempts.find(a=>a.token===s.active_attempt&&!a.deleted)||s.attempts.filter(a=>!a.deleted).at(-1);
  mountEmotionModes(card,a?.conversion_state==='saved'?a.conversion_id:null,s.style,a?.conversion_seed??s.default_seed,s.text,true);
  if(card.dataset.wantedMode==='direct'){card.querySelector(':scope > .result-mode-switch button:last-child').click();card.dataset.wantedMode='develop'}
  const promote=[...(card.querySelector('.checkpoint-pipeline')?.querySelectorAll('button')||[])].find(b=>b.textContent==='Use this emotion');if(promote)promote.onclick=()=>card.querySelector(':scope > .result-mode-switch button:last-child').click();
 }
}
const checkpointsBeforeModes=renderCheckpoints;
renderCheckpoints=function(...args){checkpointsBeforeModes(...args);mountCurrentCheckpointModes()};
renderComparisonLibrary();mountCurrentCheckpointModes();

pollDirectEmotionProfiles();setInterval(pollDirectEmotionProfiles,3000);
