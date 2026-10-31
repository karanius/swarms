// Focus this workspace on one anger pipeline without rewriting saved experiments.
const angerStage=dom('emotionStage');angerStage.classList.add('anger-pipeline');
dom('emotionHeading').textContent='Develop Santa’s anger pipeline.';
dom('emotionHeading').nextElementSibling.textContent='Keep one Santa voice. Develop an angry performance, check the result, then reuse the kept reference on new words.';
dom('emotionTab').textContent='3 · Anger pipeline';
const stageBadge=angerStage.querySelector('.test-heading > .badge');if(stageBadge)stageBadge.textContent='Anger · text to performance';
const pipelineNav=node('nav');pipelineNav.className='pipeline-navigation';pipelineNav.setAttribute('aria-label','Anger pipeline steps');
for(const [id,label] of [['pipelineIdentity','1 · Santa identity'],['pipelineActing','2 · Anger example'],['pipelineDevelop','3 · Develop & review'],['pipelineReuse','4 · Reuse on new words']]){const link=node('a',label);link.href='#'+id;pipelineNav.append(link)}angerStage.querySelector('.test-heading').after(pipelineNav);
function pipelineHeading(id,title,instruction,before){const block=node('div');block.className='pipeline-step-heading';block.id=id;block.append(node('h3',title),node('p',instruction));before.before(block);return block}
const identityControls=angerStage.querySelector('.emotion-voice');pipelineHeading('pipelineIdentity','1 · Keep Santa’s identity','Play the original voice. Keep this identity steady while you develop the anger; change the acting example in the next step.',identityControls);
pipelineHeading('pipelineActing','2 · Choose an anger performance','Play an example and choose the kind of anger you want. This actor supplies the performance; it is not Santa’s voice.',actingControls);
actingControls.classList.add('pipeline-acting-controls');emotionField.hidden=true;dom('emotionTarget').value='anger';dom('emotionTarget').disabled=true;syncActingGuide();
const directionBox=dom('emotionDirection').parentElement;directionBox.classList.add('pipeline-example-words');actingControls.after(directionBox);
const setup=angerStage.querySelector('.emotion-setup');setup.classList.add('pipeline-sentence');pipelineHeading('pipelineDevelop','3 · Develop and review a take','Write one sentence, create a test, then work through its saved checkpoints below. Acting approval and Santa approval are separate decisions.',setup);
document.querySelector('label[for="emotionSentence"]').textContent='Sentence to develop · one sentence, up to 35 words';
const developmentOrder=node('ol');developmentOrder.className='pipeline-decision-order';for(const text of ['Generate and review the actor','Approve acting, then convert to Santa','Listen to Santa and keep or improve'])developmentOrder.append(node('li',text));dom('pipelineDevelop').append(developmentOrder);
const historyHeading=node('div');historyHeading.className='pipeline-history-heading';historyHeading.append(node('h3','Saved development tests'),node('p','Each card is a separate attempt. Its development sentence, inputs, checkpoints and recordings stay together.'));comparisonLibrary.before(historyHeading);
const reuse=node('section');reuse.id='pipelineReuse';reuse.className='pipeline-reuse';reuse.append(node('h3','4 · Reuse a kept angry Santa'),node('p','Use this emotion starts from a kept emotional Santa recording. Write new words inside that card; each new recording is saved there. This direct path skips the intermediate actor and conversion, but still needs listening checks.'));
const referenceLabel=node('label','Kept anger reference');const referenceChoice=node('select');referenceChoice.setAttribute('aria-label','Kept anger pipeline reference');referenceLabel.append(referenceChoice);const reuseStatus=node('p');reuseStatus.className='hint';const reuseButton=checkpointButton('Write a new angry line',()=>{const card=[...checkpointCards.values()].find(card=>card.dataset.directReference===referenceChoice.value&&!card.hidden);if(!card)return;const mode=card.querySelector(':scope > .result-mode-switch button:last-child');mode.click();card.scrollIntoView({behavior:'smooth',block:'start'});const sentence=card.querySelector('.result-direct-body textarea');if(sentence)sentence.focus({preventScroll:true})});reuse.append(referenceLabel,reuseStatus,reuseButton);comparisonTrash.after(reuse);
const otherEmotionNotice=node('p','Other emotion records remain in the archive. This workspace is dedicated to anger.');otherEmotionNotice.className='hint pipeline-archive-note';reuse.after(otherEmotionNotice);
let pipelineIdentityRestored=false;
function applyAngerPipelineCopy(){
 const candidate=dom('emotionCandidate');if(candidate.value)pipelineIdentityRestored=true;
 const keptIdentities=[...new Set(checkpointSessions.filter(s=>!s.deleted&&s.style==='anger'&&s.attempts.some(a=>a.final_decision==='keep')).map(s=>s.source))];
 const restoreSource=candidate.dataset.wanted||(keptIdentities.length===1?keptIdentities[0]:'');
 if(!candidate.value&&!pipelineIdentityRestored&&restoreSource&&lastRecords.some(r=>r.id===restoreSource&&r.state==='saved'&&!trashedIds.has(r.id))){candidate.dataset.wanted=restoreSource;syncEmotionCandidate();pipelineIdentityRestored=!!candidate.value;}
 else if(!candidate.value&&candidate.options.length<=1&&lastRecords.length)syncEmotionCandidate();
 for(const run of emotionRuns){const card=comparisonRows.get(run.id);if(!card||card.hidden)continue;const title=card.querySelector(':scope > .comparison-script h3');if(title)title.textContent=(run.target||'Emotion')+' · earlier comparison';const words=card.querySelector(':scope > .comparison-script > p');if(words)words.textContent='Development sentence: “'+run.text+'”';}
 for(const s of checkpointSessions){const card=checkpointCards.get(s.id);if(!card||card.hidden)continue;const a=s.attempts.find(a=>a.token===s.active_attempt&&!a.deleted)||s.attempts.filter(a=>!a.deleted).at(-1);const title=card.querySelector(':scope > .comparison-script h3');const phase=checkpointProcess(a);
  if(title)title.textContent=s.style.charAt(0).toUpperCase()+s.style.slice(1)+' · '+(a?.final_decision==='keep'?'kept Santa reference':phase.santa?'Santa ready to review':phase.actor?'actor review in progress':'development in progress');
  const words=card.querySelector(':scope > .comparison-script > p');if(words)words.textContent='Development sentence: “'+s.text+'”';
  const summary=card.querySelector('.checkpoint-pipeline > summary');if(summary)summary.textContent='Development checkpoints · inputs, actor, Santa';
  const hints=card.querySelectorAll('.checkpoint-pipeline h3');for(const h of hints){if(h.textContent==='2 · Get the acting right')h.textContent='Actor checkpoint · get the acting right';if(h.textContent==='3 · Check the voice swap')h.textContent='Santa checkpoint · check the voice and emotion';}
  const inputs=card.querySelector('.checkpoint-summary > strong');if(inputs)inputs.textContent='Inputs preserved for this test';
  const panel=card.querySelector(':scope > .result-direct-body');if(panel){const title=panel.querySelector('h4');if(title&&a?.conversion_state==='saved')title.textContent='Reuse this angry Santa on new words';const label=panel.querySelector(':scope > label');if(label?.firstChild?.nodeType===Node.TEXT_NODE)label.firstChild.textContent='New words · saved separately from the development sentence';const source=panel.querySelector(':scope > details > summary');if(source)source.textContent=a?.final_decision==='keep'?'Reference recording · the kept angry Santa':'Reference recording · experimental Santa take';}
 }
 const kept=checkpointSessions.filter(s=>!s.deleted&&s.style==='anger').flatMap(s=>s.attempts.filter(a=>!a.deleted&&a.final_decision==='keep'&&a.conversion_state==='saved').map(a=>({s,a})));const signature=kept.map(k=>k.a.conversion_id).join(',');const wanted=referenceChoice.value;
 if(referenceChoice.dataset.options!==signature){referenceChoice.replaceChildren(...kept.map((k,i)=>new Option('Kept reference '+(i+1)+' · '+k.s.text.slice(0,55),k.a.conversion_id)));referenceChoice.dataset.options=signature;if(kept.some(k=>k.a.conversion_id===wanted))referenceChoice.value=wanted;}
 referenceLabel.hidden=kept.length<2;reuseButton.disabled=!kept.length;const selected=kept.find(k=>k.a.conversion_id===referenceChoice.value)||kept[0];
 if(!selected)reuseStatus.textContent='Keep a converted Santa result in development before using the direct path.';
 else {const profile=directEmotionProfiles.find(p=>p.source_id===selected.a.conversion_id&&!p.deleted),runs=profile?.runs.filter(r=>!r.deleted&&!r.workspace_removed)||[],fresh=profile?.qualifying_by_engine?.VoxCPM2||0;reuseStatus.textContent='Kept development reference · '+runs.length+' direct recording'+(runs.length===1?'':'s')+' saved · '+fresh+' different new sentence'+(fresh===1?'':'s')+' kept for the direct route.';}
 dom('generateEmotion').textContent='Create anger development test';
 dom('generateEmotion').parentElement.querySelector('p:last-child').textContent='Creates a saved test below. Generate the actor inside it; conversion waits for your approval.';
 if(!angerStage.hidden)dom('stageHint').textContent='Anger pipeline · follow the four steps. Every attempt and its source recordings remain saved.';
}
referenceChoice.onchange=applyAngerPipelineCopy;
const renderBeforeAngerPipeline=renderCheckpoints;renderCheckpoints=function(...args){renderBeforeAngerPipeline(...args);applyAngerPipelineCopy()};
const comparisonsBeforeAngerPipeline=renderComparisonLibrary;renderComparisonLibrary=function(...args){comparisonsBeforeAngerPipeline(...args);applyAngerPipelineCopy()};
const emotionPairBeforeAngerPipeline=renderEmotionPair;renderEmotionPair=function(...args){emotionPairBeforeAngerPipeline(...args);applyAngerPipelineCopy()};
const actingSelectionBeforePipeline=applyActingSelection;applyActingSelection=function(...args){actingSelectionBeforePipeline(...args);document.querySelector('label[for="emotionDirection"]').textContent='Words spoken in the acting example';};actingSelect.onchange=applyActingSelection;
const openBeforeAngerPipeline=openEmotionStage;openEmotionStage=function(){openBeforeAngerPipeline();applyAngerPipelineCopy()};dom('emotionTab').onclick=openEmotionStage;
applyAngerPipelineCopy();applyActingSelection();
if(['#anger-pipeline','#pipelineIdentity','#pipelineActing','#pipelineDevelop','#pipelineReuse'].includes(location.hash))openEmotionStage();
