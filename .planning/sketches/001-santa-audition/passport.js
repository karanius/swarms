// Shared, lazy-loaded asset lineage for every stage. No current form values are used.
let passportInstance=0;
function passportNode(tag,text){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;return el}
function makePassport(recordingId,showRelated=true){
 const details=passportNode('details');details.className='asset-passport';details.dataset.recordingId=recordingId;
 const summary=passportNode('summary','Passport');summary.setAttribute('aria-label','Passport for recording '+recordingId.slice(0,8));
 const body=passportNode('div');body.className='passport-body';details.append(summary,body);let loading=false,loaded=false;
 const prefix='passport-'+(++passportInstance)+'-';
 async function load(){
  if(loading||loaded||!details.open)return;loading=true;body.replaceChildren(passportNode('p','Loading saved lineage…'));
  try{
   const response=await fetch('/api/designer/passport?id='+encodeURIComponent(recordingId));const result=await response.json();
   if(!response.ok)throw new Error(result.error||'Passport unavailable');
   const p=result.passport,checks=result.integrity.assets,bad=checks.filter(a=>a.status!=='match');
   body.replaceChildren();body.append(passportNode('p','Recording '+recordingId+' · sealed '+p.passport_id.slice(0,23)+'…'));
   const status=passportNode('p',bad.length?bad.length+' linked file(s) missing, changed or unverified. Inspect the downloaded passport.':checks.length+' linked files match their fingerprints.');status.className='passport-integrity';body.append(status);
   const download=passportNode('a','Download passport JSON');download.href='/api/designer/passport?id='+encodeURIComponent(recordingId);download.download='voice-passport-'+recordingId+'.json';body.append(download);
   const byId=new Map(p.nodes.map(n=>[n.id,n])),ordered=[],seen=new Set();
   function visit(id){if(seen.has(id))return;seen.add(id);for(const e of p.edges.filter(e=>e.to===id))visit(e.from);if(byId.has(id))ordered.push(byId.get(id))}visit(p.root);
   const anchors=new Map(ordered.map((n,i)=>[n.id,prefix+i]));
   const roles={selected_as_identity:'identity selected from',reference_recording:'voice sample',voice_identity:'voice identity',target_voice:'target character voice',emotion_guidance:'emotion guide',upstream_acting_recipe:'upstream acting sample',performed_audio_to_convert:'actor audio converted'};
   for(const n of ordered){
    const item=passportNode('section');item.className='passport-node';item.id=anchors.get(n.id);
    const title=passportNode('h4',(n.stage?'Stage '+n.stage+' · ':'')+n.label);item.append(title);
    if(n.kind==='recording'){
     const q=n.request||{},cv=n.model_provenance?.conversion;
     let settings=n.engine||'Engine not recorded';
     if(q.seed!==undefined)settings+=' · seed '+q.seed;
     if(cv)settings+=' · conversion '+cv.steps+' steps · CFG '+cv.cfg+' · length '+cv.length_adjust;
     else if(q.mode==='reference_performance')settings+=' · emotion strength '+q.strength+' · duration scale '+q.duration_scale;
     else{if(q.steps!==undefined)settings+=' · '+q.steps+' steps';if(q.guidance!==undefined)settings+=' · guidance '+q.guidance}
     item.append(passportNode('p',settings),passportNode('p','Words: '+(q.text||'Not recorded')));
     if(q.description)item.append(passportNode('p','Saved voice brief: '+q.description));
     if(q.performance_direction)item.append(passportNode('p','Saved direction: '+q.performance_direction));
     if(n.state==='saved'){const play=passportNode('audio');play.controls=true;play.preload='none';play.src=n.play_url;play.setAttribute('aria-label','Play '+n.label+' '+n.recording_id.slice(0,8));play.onplay=()=>document.querySelectorAll('audio').forEach(a=>{if(a!==play)a.pause()});item.append(play)}
     if(n.playback_processing?.gain!==undefined)item.append(passportNode('p','Playback copy: gain ×'+Number(n.playback_processing.gain).toFixed(3)+'; original recording retained.'));
    }else if(n.kind==='reference'){
     for(const ref of n.snapshots){item.append(passportNode('p','Sample: '+(ref.id||'ID not recorded')),passportNode('p','Words: '+(ref.transcript||'Not recorded')));if(ref.terms)item.append(passportNode('p',ref.terms))}
     const play=passportNode('audio');play.controls=true;play.preload='none';play.src='/api/designer/passport-media?id='+encodeURIComponent(recordingId)+'&node='+encodeURIComponent(n.id);play.setAttribute('aria-label','Play saved reference '+n.label);play.onplay=()=>document.querySelectorAll('audio').forEach(a=>{if(a!==play)a.pause()});item.append(play);
    }else if(n.kind==='profile')item.append(passportNode('p','Saved identity profile · '+(n.snapshot.id||'snapshot without profile ID')));
    else item.append(passportNode('p','This parent is missing; its lineage cannot be reconstructed.'));
    const parents=p.edges.filter(e=>e.to===n.id);
    if(parents.length){const links=passportNode('p');links.className='passport-links';for(const e of parents){const link=passportNode('a',(roles[e.role]||e.role)+': '+(byId.get(e.from)?.label||e.from));link.href='#'+anchors.get(e.from);links.append(link,document.createTextNode(' · '))}item.append(links)}
    const advanced=passportNode('details');advanced.append(passportNode('summary','Exact saved metadata'));const raw=passportNode('pre',JSON.stringify(n,null,2));advanced.append(raw);item.append(advanced);body.append(item);
   }
   if(result.checkpoint_history?.length)body.append(passportNode('p','Checkpoint decisions and retry history are included in the export as review context, separate from the sealed generation inputs.'));
   if(result.comparisons.length)body.append(passportNode('p','Used in '+result.comparisons.length+' saved batch/comparison(s). Other comparison takes are controls, not parent inputs; their IDs and reuse status are in the export.'));
   if(showRelated&&result.related_identity_tests?.length){
    const related=passportNode('details');related.append(passportNode('summary','Stage 2 identity tests · related checks, not inputs'));
    for(const test of result.related_identity_tests){const row=passportNode('section');row.className='passport-node';row.append(passportNode('p',test.text||'Words not recorded'),passportNode('p',test.word_check?.exact_words?'Words checked; listener approval not recorded here.':'Word check or listener approval unavailable.'),makePassport(test.id,false));related.append(row)}body.append(related);
   }
   for(const warning of p.warnings)body.append(passportNode('p','Unknown: '+warning));
   body.append(passportNode('p','Word checks do not approve emotion or voice identity. Listening-copy fingerprints measured at passport creation are labelled separately in the export.'));
   loaded=true;
  }catch(error){body.replaceChildren(passportNode('p',error.message));const retry=passportNode('button','Retry passport');retry.onclick=load;body.append(retry)}finally{loading=false}
 }
 details.addEventListener('toggle',load);return details;
}
