import {proposePolicyRevision,applyPolicyPlan,validatePolicyPreservation} from '../prototype-canvas-v3/instance-revision.mjs';
import {readFile,writeFile,mkdir,rename,readdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import Ajv from 'ajv';
const ajv=new Ajv({allErrors:true,strict:true});
const schema={type:'object',additionalProperties:false,required:['schemaVersion','kind','id','name','revision','parentRevision','change','intent','libraryRef','layers','requirements','entities','links','questions','gaps','decisions','validation','unusedLayers'],properties:{
 schemaVersion:{const:1},kind:{const:'intent-instance'},id:{const:'ticket-triage'},name:{type:'string'},revision:{type:'integer',minimum:1},parentRevision:{anyOf:[{type:'integer',minimum:1},{type:'null'}]},change:{type:'object'},intent:{type:'object'},libraryRef:{type:'object'},layers:{type:'array',items:{type:'object'}},requirements:{type:'array',items:{type:'object'}},entities:{type:'array',items:{type:'object'}},links:{type:'array',items:{type:'object'}},questions:{type:'array',items:{type:'object'}},gaps:{type:'array',items:{type:'object'}},decisions:{type:'array',items:{type:'object'}},validation:{type:'object'},unusedLayers:{type:'object'}}};
const shape=ajv.compile(schema);
export function validateInstance(doc,library){
 if(!shape(doc))throw Error('Instance format is invalid: '+ajv.errorsText(shape.errors));
 const unique=(items,name)=>{const ids=items.map(x=>x.id);if(ids.some(x=>typeof x!=='string')||new Set(ids).size!==ids.length)throw Error(name+' must have unique identities.');return new Map(items.map(x=>[x.id,x]));};
 const layers=unique(doc.layers,'Layers'),entities=unique(doc.entities,'Entities'),requirements=unique(doc.requirements,'Requirements'),gaps=unique(doc.gaps,'Gaps');unique(doc.questions,'Questions');
 const items=new Map(library.items.map(x=>[x.id,x]));
 if(doc.libraryRef.id!==library.id||doc.libraryRef.revision!==library.revision)throw Error('Pinned library reference does not resolve.');
 const requireRef=(map,id,label)=>{if(!map.has(id))throw Error('Unresolved '+label+': '+id);};
 for(const r of doc.requirements){for(const id of r.parentIds)requireRef(requirements,id,'parent requirement');for(const id of r.realizationIds)requireRef(entities,id,'realization');if(!['confirmed','proposed'].includes(r.status))throw Error('Unknown requirement status.');}
 for(const e of doc.entities){
  requireRef(layers,e.layer,'layer');for(const id of e.requirementIds)requireRef(requirements,id,'entity requirement');for(const id of e.policyRefs??[])requireRef(requirements,id,'entity policy');
  for(const id of e.members){requireRef(entities,id,'member');if(layers.get(entities.get(id).layer).order>=layers.get(e.layer).order)throw Error('Membership must refer to a lower plane.');}
  if(e.itemRef){const item=items.get(e.itemRef.id);if(!item||item.revision!==e.itemRef.revision||e.layer!=='components')throw Error('Native definition revision or layer does not resolve.');
   for(const k of Object.keys(e.configuration??{}))if(!item.native.template[k])throw Error('Unknown native configuration field: '+k);
  }
  for(const mapping of Object.values(e.interface??{})){requireRef(entities,mapping.entityId,'interface entity');if(!e.members.includes(mapping.entityId))throw Error('Interface mapping must retain a member endpoint.');const member=entities.get(mapping.entityId),native=items.get(member.itemRef?.id)?.native;
   if(mapping.kind==='output'){if(!native?.outputs.some(p=>p.name===mapping.port&&p.types.includes(mapping.type)))throw Error('Native output mapping is incompatible.');}
   else {const field=native?.template[mapping.port];if(!field||!(field.input_types?.includes(mapping.type)||field.type===mapping.type))throw Error('Native input/field mapping is incompatible.');}
  }
 }
 unique(doc.links,'Links');
 for(const l of doc.links){requireRef(entities,l.from,'link source');requireRef(entities,l.to,'link target');
  if(l.kind==='data'&&entities.get(l.from).itemRef&&entities.get(l.to).itemRef){const source=items.get(entities.get(l.from).itemRef.id).native,target=items.get(entities.get(l.to).itemRef.id).native;const types=source.outputs.find(p=>p.name===l.fromPort)?.types??[],accepted=target.template[l.toPort]?.input_types??[];if(!types.includes(l.type)||!accepted.includes(l.type))throw Error('Native connection has incompatible named endpoints.');}
  if(l.realizesLinkId){const underlying=doc.links.find(x=>x.id===l.realizesLinkId);if(!underlying)throw Error('Projection must identify its underlying connection.');const from=entities.get(l.from).interface?.output,to=entities.get(l.to).interface?.input;if(!from||!to||from.entityId!==underlying.from||from.port!==underlying.fromPort||to.entityId!==underlying.to||to.port!==underlying.toPort)throw Error('Projected connection must retain the same underlying endpoints.');}
 }
 for(const g of doc.gaps){for(const id of g.requirementIds)requireRef(requirements,id,'gap requirement');for(const id of g.entityIds)requireRef(entities,id,'gap entity');if(!['open','resolved'].includes(g.status))throw Error('Unknown gap disposition.');}
 for(const q of doc.questions)requireRef(gaps,q.gapId,'question gap');
 if(doc.validation.behavior!=='not-tested'||doc.validation.deployment!=='not-requested')throw Error('Design edits cannot manufacture behavior or deployment evidence.');
 return {schema:'Ajv JSON shape',references:'checked',nativeInterfaces:'checked where represented',behavior:'not-tested',readiness:doc.gaps.some(g=>g.status==='open')?'open-boundaries':'design-review-needed'};
}
export function answerQuestion(current,questionId,value,note=''){
 const doc=structuredClone(current),q=doc.questions.find(x=>x.id===questionId);
 if(!q||!q.options.some(x=>x.value===value))throw Object.assign(Error('Choose a supported answer.'),{status:400});
 q.answer={value,label:q.options.find(x=>x.value===value).label,note,source:'requester'};
 const gap=doc.gaps.find(g=>g.id===q.gapId);gap.status='resolved';
 const addGap=(g)=>{const old=doc.gaps.find(x=>x.id===g.id);if(!old)doc.gaps.push(g);else old.status='open';};
 if(questionId==='Q-channel'){
  const e=doc.entities.find(x=>x.id==='input');if(e)e.description=value==='manual'?'Requester selected pasted ticket text as the first intake channel.':'The requester wants a ticket-system integration; Chat Input remains a design entry point until an adapter is specified.';
  if(value==='integration')addGap({id:'G-intake-adapter',kind:'missing-capability',status:'open',description:'A ticket-system connector, authentication scope and ticket-to-Message mapping are not selected. Chat Input alone is not that integration.',requirementIds:['R-intake'],entityIds:['input'],blocks:['claim-intake-integrated'],nextAction:'Identify the ticket system and a permitted native connector.'});
  else {const old=doc.gaps.find(g=>g.id==='G-intake-adapter');if(old)old.status='resolved';}
 }
 if(questionId==='Q-policy'){
  addGap({id:'G-policy-rules',kind:'clarification',status:'open',description:'Category preference is recorded; exact urgency thresholds, examples and exception rules still need definition.',requirementIds:['R-assess'],entityIds:['classifier'],blocks:['claim-behavior-correct'],nextAction:'Define policy examples and counterexamples in a later revision.'});
  if(value==='custom')gap.status='open';
 }
 if(questionId==='Q-review'){
  const e=doc.entities.find(x=>x.id==='review-policy');if(e){e.status='confirmed';e.description=value==='human-review'?'Requester chose human review before external action; reviewer identity and escalation rules remain open.':'Requester chose to stop at the draft. No external action is described.';}
  if(value==='human-review')addGap({id:'G-escalation',kind:'clarification',status:'open',description:'Who reviews drafts, and when does escalation occur?',requirementIds:['R-review'],entityIds:['review-policy'],blocks:['finalize-process'],nextAction:'Agree on owner and escalation conditions.'});
  else {const g=doc.gaps.find(g=>g.id==='G-escalation');if(g)g.status='resolved';}
 }
 if(questionId==='Q-model'){
  const e=doc.entities.find(x=>x.id==='model-config');if(e){e.bindingRef=value==='api-proxy'?'langflow-existing-config:api-proxy':null;e.status=value==='api-proxy'?'reference-selected':'unresolved';}
  if(value==='unresolved')gap.status='open';
  else addGap({id:'G-binding-resolution',kind:'binding',status:'open',description:'API Proxy reference selected; resolve it to an approved native LanguageModel binding before export. Availability and authentication are not checked.',requirementIds:['R-assess','R-draft'],entityIds:['model-config'],blocks:['assemble-native-export'],nextAction:'Resolve through existing Langflow configuration without copying credentials.'});
 }
 doc.decisions.push({id:'decision-'+(doc.decisions.length+1),kind:'answer',questionId,value,note,source:'requester'});
 return doc;
}
export function createInstanceStore(root){
 const dir=resolve(root,'knowledge/instance-machine/instances/ticket-triage');let queue=Promise.resolve();
 const loadJSON=async f=>JSON.parse(await readFile(resolve(dir,f),'utf8'));
 const loadRevision=rev=>loadJSON('revisions/'+String(rev).padStart(4,'0')+'.json');
 async function read(){const head=await loadJSON('head.json'),document=await loadRevision(head.revision),library=await loadJSON('library.json');const history=[];const seen=new Set();let cursor=document;
  while(cursor){if(seen.has(cursor.revision))throw Error('Revision history contains a cycle.');seen.add(cursor.revision);history.unshift({revision:cursor.revision,parentRevision:cursor.parentRevision,...cursor.change});cursor=cursor.parentRevision?await loadRevision(cursor.parentRevision):null;}
  return {document,library,history,checks:validateInstance(document,library)};
 }
 function makePlan(current,body){
  if(body.baseRevision!==current.document.revision)throw Object.assign(Error('The instance changed. Generate a new proposal from the latest revision.'),{status:409});
  const plan=proposePolicyRevision(current.document,body.rule);let checks=null;
  if(plan.outcome==='proposed'){const candidate=applyPolicyPlan(current.document,plan);checks=validatePolicyPreservation(current.document,candidate,plan);if(!checks.passed)throw Error('Revision preservation failed.');validateInstance(candidate,current.library);}
  return {plan,planDigest:createHash('sha256').update(JSON.stringify(plan)).digest('hex'),checks};
 }
 async function plan(body){if(!body||typeof body!=='object'||!Number.isSafeInteger(body.baseRevision))throw Object.assign(Error('A base revision is required.'),{status:400});return makePlan(await read(),body);}
 function mutate(body){const op=queue.then(async()=>{if(!body||typeof body!=='object'||Array.isArray(body)||!Number.isSafeInteger(body.baseRevision))throw Object.assign(Error('A revision action and integer base revision are required.'),{status:400});const current=await read();if(body.baseRevision!==current.document.revision)throw Object.assign(Error('The instance changed. Reload the latest revision before saving.'),{status:409});let doc;
  if(body.action==='answer-question')doc=answerQuestion(current.document,body.questionId,body.value,typeof body.note==='string'?body.note.slice(0,1000):'');
  else if(body.action==='apply-policy-proposal'){const prepared=makePlan(current,body);if(prepared.plan.outcome!=='proposed')throw Object.assign(Error('The proposal is blocked: '+prepared.plan.gap),{status:400});if(body.planDigest!==prepared.planDigest)throw Object.assign(Error('The proposal changed. Review a new proposal before applying it.'),{status:409});doc=applyPolicyPlan(current.document,prepared.plan);}
  else if(body.action==='checkpoint'){doc=structuredClone(current.document);doc.decisions.push({id:'decision-'+(doc.decisions.length+1),kind:'checkpoint',source:'workbench',description:'Save the current draft without changing requirements or answering questions.'});}
  else if(body.action==='confirm-requirement'){doc=structuredClone(current.document);const r=doc.requirements.find(x=>x.id===body.requirementId);if(!r)throw Object.assign(Error('Requirement not found.'),{status:400});r.status='confirmed';for(const gap of doc.gaps)if(gap.confirmationRequirementId===r.id)gap.status='resolved';doc.decisions.push({id:'decision-'+(doc.decisions.length+1),kind:'confirm-requirement',requirementId:r.id,source:'requester'});}
  else throw Object.assign(Error('Unknown revision action.'),{status:400});
  const ids=(await readdir(resolve(dir,'revisions'))).filter(x=>/^\d+\.json$/.test(x)).map(x=>Number(x.split('.')[0]));doc.parentRevision=current.document.revision;doc.revision=Math.max(...ids)+1;doc.change={action:body.action,summary:body.action==='apply-policy-proposal'?'Apply an algorithm-generated policy proposal; business approval and behavior remain open.':body.action==='answer-question'?'Record requester answer: '+body.questionId:body.action==='checkpoint'?'Save the current design draft; all open questions remain unchanged.':'Confirm requirement: '+body.requirementId,source:body.action==='apply-policy-proposal'?'revision-algorithm':body.action==='checkpoint'?'workbench-checkpoint':'requester',recordedAt:new Date().toISOString()};
  validateInstance(doc,current.library);await mkdir(resolve(dir,'revisions'),{recursive:true});await writeFile(resolve(dir,'revisions',String(doc.revision).padStart(4,'0')+'.json'),JSON.stringify(doc,null,2)+'\n',{flag:'wx'});const temporary=resolve(dir,'head.json.tmp');await writeFile(temporary,JSON.stringify({revision:doc.revision},null,2)+'\n');await rename(temporary,resolve(dir,'head.json'));return read();
 });queue=op.catch(()=>{});return op;}
 return {read,mutate,plan,async revision(rev){const library=await loadJSON('library.json'),document=await loadRevision(rev);return {document,library,checks:validateInstance(document,library)};}};
}
export function instanceStorePlugin(root){const store=createInstanceStore(root);return {name:'intent-instance-store',configureServer(server){server.middlewares.use('/instance-api',async(req,res)=>{
  const reply=(code,data)=>{res.statusCode=code;res.setHeader('Content-Type','application/json');res.setHeader('Cache-Control','no-store');res.end(JSON.stringify(data));};
  try{const host=req.headers.host??'';if(!/^(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$/.test(host)||req.headers['sec-fetch-site']==='cross-site'||(req.headers.origin&&req.headers.origin!=='http://'+host))return reply(403,{error:'Local same-origin requests only.'});
   const url=new URL(req.url,'http://'+host);
   if(req.method==='GET'){if(url.pathname!=='/'&&url.pathname!=='')return reply(404,{error:'Unknown instance route.'});const rev=url.searchParams.get('revision');if(rev&&(!/^[1-9]\d*$/.test(rev)||!Number.isSafeInteger(Number(rev))))return reply(400,{error:'Invalid revision.'});return reply(200,rev?await store.revision(Number(rev)):await store.read());}
   if(req.method!=='POST')return reply(405,{error:'Method not allowed.'});
   if(req.headers['content-type']?.split(';')[0]!=='application/json')return reply(415,{error:'JSON required.'});
   let text='';for await(const chunk of req){text+=chunk;if(Buffer.byteLength(text)>16000)return reply(413,{error:'Revision request is too large.'});}
   let body;try{body=JSON.parse(text);}catch{return reply(400,{error:'Revision request must be valid JSON.'});}if(url.pathname==='/plan')return reply(200,await store.plan(body));if(url.pathname!=='/'&&url.pathname!=='')return reply(404,{error:'Unknown instance route.'});return reply(200,await store.mutate(body));
  }catch(e){reply(e.status??500,{error:e.status?e.message:'Instance storage could not be read or validated. Existing revisions remain preserved.'});}
 });}};}
