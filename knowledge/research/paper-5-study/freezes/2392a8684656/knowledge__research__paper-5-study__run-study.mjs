import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {proposePolicyRevision,applyPolicyPlan,validatePolicyPreservation,impactClosure,exampleTriageRule,revisionAlgorithmVersion} from './implementation/frontend/prototype-canvas-v3/instance-revision.mjs';
import {validateInstance} from './implementation/frontend/server/instance-store.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../..');
const clone=x=>structuredClone(x),same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const expectedBase=['assess','classifier','draft','output','process-triage','review-policy','triage-flow','writer'];
const baseline=JSON.parse(await readFile(resolve(here,'baseline.instance.json'))),library=JSON.parse(await readFile(resolve(here,'baseline.library.json')));
const cases=[];
const add=(id,edit=()=>{},expected={outcome:'proposed',affected:expectedBase},options={})=>{const doc=clone(baseline),rule=clone(exampleTriageRule);edit(doc,rule);cases.push({id,document:doc,rule,expected,options});};
add('base-outage');
add('data-loss',(_,r)=>{r.id='policy-data-loss';r.when.field='ticket.explicitDataLoss';});
add('unrelated-extra',d=>{const e=clone(d.entities.find(x=>x.id==='output'));e.id='unrelated-output';e.name='Unrelated output';e.requirementIds=[];d.entities.push(e);});
add('disconnected-downstream',d=>{d.links=d.links.filter(l=>!['L-assess-draft','L-composites'].includes(l.id));},{outcome:'proposed',affected:['assess','classifier','process-triage','review-policy','triage-flow']});
add('additional-consumer',d=>{const e=clone(d.entities.find(x=>x.id==='output'));e.id='audit-output';e.name='Audit output';e.requirementIds=[];d.entities.push(e);d.links.push({id:'audit-link',from:'writer',to:'audit-output',kind:'data',fromPort:'response',toPort:'input_value',type:'Message',status:'interface-compatible'});},{outcome:'proposed',affected:[...expectedBase,'audit-output'].sort()});
add('missing-requirement',(_,r)=>r.targetRequirementId='R-absent',{outcome:'blocked',gap:'missing-requirement'});
add('missing-adapter',d=>{delete d.entities.find(e=>e.id==='classifier').configuration.system_prompt;},{outcome:'blocked',gap:'missing-policy-adapter'});
add('ambiguous-adapter',d=>{d.requirements.find(r=>r.id==='R-assess').realizationIds.push('writer');d.entities.find(e=>e.id==='writer').requirementIds.push('R-assess');},{outcome:'blocked',gap:'ambiguous-policy-adapter'});
add('conflicting-policy',d=>{d.requirements.push({id:'R-existing',description:'Existing opposite result',status:'proposed',parentIds:['R-assess'],phase:'behavior',realizationIds:['classifier'],rule:{...clone(exampleTriageRule),id:'policy-existing',then:'routine'}});},{outcome:'blocked',gap:'policy-conflict'});
add('duplicate-policy',d=>{const p=proposePolicyRevision(d,exampleTriageRule);const changed=applyPolicyPlan(d,p);Object.assign(d,changed);},{outcome:'blocked',gap:'duplicate-policy'});
add('unsupported-operator',(_,r)=>r.when.operator='contains',{outcome:'blocked',gap:'unsupported-rule'});
add('unsupported-field',(_,r)=>r.when.field='ticket.invented',{outcome:'blocked',gap:'unsupported-rule'});
add('impact-limit',()=>{},{outcome:'blocked',gap:'impact-budget'},{maxAffected:1});
add('patch-limit',()=>{},{outcome:'blocked',gap:'patch-budget'},{maxOperations:1});
// Explicit expected sets above are authored separately from the reachability function.
function assess(c,plan,after){const errors=[];if(plan.outcome!==c.expected.outcome)errors.push('outcome');
 if(c.expected.outcome==='blocked'){if(plan.gap!==c.expected.gap)errors.push('gap');return {passed:!errors.length,errors};}
 if(!after)return {passed:false,errors:[...errors,'missing-candidate']};
 if(!same([...plan.impact.affectedIds].sort(),[...c.expected.affected].sort()))errors.push('impact-set');
 for(const old of c.document.entities){const now=after.entities.find(e=>e.id===old.id);if(!c.expected.affected.includes(old.id)&&!same(old,now))errors.push('unrelated-change:'+old.id);
  if(!now||!same(old.members,now.members)||!same(old.itemRef,now.itemRef))errors.push('identity:'+old.id);
  if(old.id!=='classifier'&&!same(old.configuration,now.configuration))errors.push('nonseed-configuration:'+old.id);
  if(c.expected.affected.includes(old.id)&&!now?.policyRefs?.includes('R-'+plan.rule.id))errors.push('missing-review-mark:'+old.id);
 }
 for(const r of c.document.requirements)if(!same(r,after.requirements.find(x=>x.id===r.id)))errors.push('old-requirement');
 for(const g of c.document.gaps)if(!same(g,after.gaps.find(x=>x.id===g.id)))errors.push('old-gap');
 for(const field of ['links','questions','intent','libraryRef','layers','validation'])if(!same(c.document[field],after[field]))errors.push('changed-'+field);
 if(after.requirements.find(x=>x.id==='R-'+plan.rule.id)?.status!=='proposed')errors.push('approval');
 if(!after.gaps.some(x=>x.id==='G-predicate-'+plan.rule.id&&x.status==='open'))errors.push('predicate-gap');
 try{validateInstance(after,library);}catch(e){errors.push('schema-or-reference:'+e.message);}
 return {passed:!errors.length,errors};}
await mkdir(resolve(here,'observations'),{recursive:true});
await writeFile(resolve(here,'observations/cases.json'),JSON.stringify(cases,null,2)+'\n');
const sourceFiles=['knowledge/research/paper-5-study/implementation/frontend/prototype-canvas-v3/instance-revision.mjs','knowledge/research/paper-5-study/implementation/frontend/server/instance-store.mjs','knowledge/research/paper-5-study/run-study.mjs','knowledge/research/paper-5-study/protocol.json','knowledge/research/paper-5-study/baseline.instance.json','knowledge/research/paper-5-study/baseline.library.json'];
const hashes={};for(const p of sourceFiles)hashes[p]=createHash('sha256').update(await readFile(resolve(root,p))).digest('hex');
const freezeId=createHash('sha256').update(JSON.stringify(hashes)).digest('hex').slice(0,12);await mkdir(resolve(here,'freezes',freezeId),{recursive:true});
for(const p of sourceFiles){const target=resolve(here,'freezes',freezeId,p.replaceAll('/','__'));try{await copyFile(resolve(root,p),target,1);}catch(e){if(e.code!=='EEXIST')throw e;}}
const records=[];
for(const c of cases)for(const method of ['impact','direct-only','rewrite-all']){const plan=proposePolicyRevision(c.document,c.rule,{method,...c.options});let candidate=null,guard=null;if(plan.outcome==='proposed'){candidate=applyPolicyPlan(c.document,plan);guard=validatePolicyPreservation(c.document,candidate,plan);}records.push({case:c.id,method,plan,candidate,guard,assessment:assess(c,plan,candidate)});}
const summary=['impact','direct-only','rewrite-all'].map(method=>{const rows=records.filter(r=>r.method===method);return {method,cases:rows.length,passes:rows.filter(r=>r.assessment.passed).length,proposed:rows.filter(r=>r.plan.outcome==='proposed').length,preservationRejected:rows.filter(r=>r.guard&&!r.guard.passed).length};});
const good=records.find(r=>r.case==='base-outage'&&r.method==='impact');const negatives=[];
for(const [name,corrupt] of [['erase-old-gap',x=>x.gaps.shift()],['invent-approval',x=>x.requirements.find(r=>r.id==='R-policy-outage').status='confirmed'],['rewrite-unrelated-input',x=>x.entities.find(e=>e.id==='input').name='Changed'],['rewrite-downstream-prompt',x=>x.entities.find(e=>e.id==='writer').configuration.system_prompt='Changed'],['alter-native-definition',x=>x.entities.find(e=>e.id==='classifier').itemRef.revision='other'],['erase-impact-mark',x=>delete x.entities.find(e=>e.id==='draft').policyRefs]]){const doc=clone(good.candidate);corrupt(doc);const check=validatePolicyPreservation(baseline,doc,good.plan);negatives.push({name,...check});}
const cycleDoc=clone(baseline);cycleDoc.links.push({id:'cycle-helper',from:'output',to:'classifier',kind:'data'});const cycle=impactClosure(cycleDoc,['classifier']);
const checks={impactReferences:records.filter(r=>r.method==='impact').every(r=>r.assessment.passed),impactPreserved:records.filter(r=>r.method==='impact'&&r.guard).every(r=>r.guard.passed),faultsDetected:negatives.every(n=>!n.passed),closureCycleBounded:cycle.visits<=cycleDoc.entities.length};
const output={algorithm:revisionAlgorithmVersion,hashes,exposure:'same-author exposed; structured grammar only',summary,records,negatives,helper:{cycleClosureVisits:cycle.visits,entities:cycleDoc.entities.length,scope:'reachability helper only; does not certify cyclic execution semantics'},checks};
await writeFile(resolve(here,'observations/results.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({summary,checks,failures:records.filter(r=>!r.assessment.passed).map(r=>({case:r.case,method:r.method,errors:r.assessment.errors}))},null,2));
if(!Object.values(checks).every(Boolean))process.exitCode=1;
