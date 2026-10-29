// Explicit impact/revision algorithm. Domain predicates are data, never executable strings.
export const revisionAlgorithmVersion='instance-revision-1';
const clone=value=>structuredClone(value);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
export const exampleTriageRule={id:'policy-outage',targetRequirementId:'R-assess',when:{field:'ticket.explicitAllUsersOutage',operator:'equals',value:true},then:'urgent',otherwise:'uncertain'};
export function normalizePolicy(input){
 if(!input||typeof input!=='object'||!/^policy-[a-z0-9-]{1,60}$/.test(input.id??''))throw Error('A stable policy identity is required.');
 if(typeof input.targetRequirementId!=='string')throw Error('A target requirement is required.');
 if(!['ticket.explicitAllUsersOutage','ticket.explicitDataLoss'].includes(input.when?.field)||input.when?.operator!=='equals'||input.when?.value!==true||!['urgent','routine'].includes(input.then)||input.otherwise!=='uncertain')throw Error('Unsupported structured predicate. Record a grammar gap rather than invent a rule.');
 return {id:input.id,targetRequirementId:input.targetRequirementId,when:clone(input.when),then:input.then,otherwise:'uncertain'};
}
export function impactClosure(doc,seeds,{propagate=true}={}){
 const ids=new Set(doc.entities.map(e=>e.id)),affected=new Set(seeds),reasons=Object.fromEntries(seeds.map(id=>[id,{kind:'direct-realization',from:null}])),queue=[...seeds];let visits=0;
 if(seeds.some(id=>!ids.has(id)))throw Error('Impact seed does not resolve.');
 while(queue.length){const id=queue.shift();visits++;if(!propagate)continue;
  const neighbors=[...doc.entities.filter(e=>e.members.includes(id)).map(e=>({id:e.id,kind:'membership-parent'})),...doc.links.filter(l=>l.from===id&&['data','lifecycle'].includes(l.kind)).map(l=>({id:l.to,kind:l.kind+'-downstream'}))];
  for(const n of neighbors){if(!ids.has(n.id))throw Error('Impact relationship does not resolve.');if(!affected.has(n.id)){affected.add(n.id);reasons[n.id]={kind:n.kind,from:id};queue.push(n.id);}}
 }
 return {seeds:[...seeds].sort(),affectedIds:[...affected].sort(),unchangedIds:[...ids].filter(id=>!affected.has(id)).sort(),reasons,visits};
}
export function proposePolicyRevision(document,input,{method='impact',maxAffected=100,maxOperations=100}={}){
 const baseRevision=document.revision;
 const blocked=(gap,details)=>({schemaVersion:1,kind:'instance-revision-plan',algorithm:revisionAlgorithmVersion,baseRevision,outcome:'blocked',gap,details,operations:[]});
 if(!['impact','direct-only','rewrite-all'].includes(method))return blocked('unsupported-method','Unknown revision method.');
 let rule;try{rule=normalizePolicy(input);}catch(e){return blocked('unsupported-rule',e.message);}
 const target=document.requirements.find(r=>r.id===rule.targetRequirementId);
 if(!target)return blocked('missing-requirement','The target requirement is absent.');
 if(document.requirements.some(r=>r.id==='R-'+rule.id))return blocked('duplicate-policy','This policy already exists; replacement needs a separate versioned operation.');
 const conflict=document.requirements.find(r=>r.rule&&same(r.rule.when,rule.when)&&r.rule.then!==rule.then);
 if(conflict)return blocked('policy-conflict','Existing '+conflict.id+' assigns a different result to this predicate.');
 const seeds=target.realizationIds.filter(id=>{const e=document.entities.find(e=>e.id===id);return e?.kind==='native-reference'&&typeof e.configuration?.system_prompt==='string';});
 if(!seeds.length)return blocked('missing-policy-adapter','No explicitly mapped prompt-bearing realization is available.');
 if(seeds.length!==1)return blocked('ambiguous-policy-adapter','Several prompt-bearing realizations require an explicit target choice.');
 const impact=impactClosure(document,seeds,{propagate:method!=='direct-only'});
 if(method==='rewrite-all'){impact.affectedIds=document.entities.map(e=>e.id).sort();impact.unchangedIds=[];for(const e of document.entities)impact.reasons[e.id]??={kind:'unselective-rewrite',from:null};}
 if(impact.affectedIds.length>maxAffected)return blocked('impact-budget','The affected set exceeds the declared limit.');
 const requirementId='R-'+rule.id;
 const requirement={id:requirementId,description:`Proposed rule: when ${rule.when.field} is explicitly true, label ${rule.then}; otherwise retain uncertainty.`,status:'proposed',parentIds:[target.id],phase:'behavior',realizationIds:impact.affectedIds,rule,acceptanceCriteria:['Structured predicate is recorded without changing unrelated entities.','No claim that a model follows this instruction without behavioral evidence.']};
 const operations=[{collection:'requirements',action:'append',value:requirement}];
 for(const e of document.entities.filter(e=>impact.affectedIds.includes(e.id))){const next=clone(e);next.policyRefs=[...new Set([...(next.policyRefs??[]),requirementId])];next.revisionImpact={policy:requirementId,status:seeds.includes(e.id)?'configuration-proposed':'reassessment-required',reason:impact.reasons[e.id]};
  // Only the direct mapped configuration is edited. Downstream/upper nodes receive review marks.
  if(seeds.includes(e.id))next.configuration.system_prompt+='\n\nProposed policy '+rule.id+': if '+rule.when.field+' is explicitly true, label '+rule.then+'; otherwise retain uncertainty. This is a proposed policy, not evidence of compliance.';
  operations.push({collection:'entities',action:'replace',id:e.id,before:clone(e),value:next});
 }
 operations.push({collection:'gaps',action:'append',value:{id:'G-approve-'+rule.id,kind:'policy-approval',status:'open',description:'The example policy is proposed, not requester-approved.',requirementIds:[requirementId],entityIds:impact.affectedIds,confirmationRequirementId:requirementId,blocks:['claim-policy-approved'],nextAction:'Review and explicitly confirm the intended rule.'}});
 operations.push({collection:'gaps',action:'append',value:{id:'G-evidence-'+rule.id,kind:'evidence',status:'open',description:'Instruction change and impact markings do not demonstrate correct classification or downstream behavior.',requirementIds:[requirementId],entityIds:impact.affectedIds,blocks:['claim-behavior-correct'],nextAction:'Define independent behavioral evidence before claiming compliance.'}});
 operations.push({collection:'gaps',action:'append',value:{id:'G-predicate-'+rule.id,kind:'missing-contract',status:'open',description:'The structured ticket predicate has no confirmed raw-ticket extractor or input binding. Recording it does not establish that a model detects it correctly.',requirementIds:[requirementId],entityIds:impact.seeds,blocks:['claim-policy-executable'],nextAction:'Define the predicate input contract and its independent evidence.'}});
 operations.push({collection:'decisions',action:'append',value:{id:'decision-'+rule.id,kind:'algorithm-proposal',source:'revision-algorithm',algorithm:revisionAlgorithmVersion,rule,impact,description:'Deterministic graph closure and narrow patch; example business rule remains proposed.'}});
 if(operations.length>maxOperations)return blocked('patch-budget','The patch exceeds the declared operation limit.');
 return {schemaVersion:1,kind:'instance-revision-plan',algorithm:revisionAlgorithmVersion,baseRevision,outcome:'proposed',rule,impact,operations,
         claimBoundary:'Graph reachability is a conservative review scope, not proof of semantic impact. No behavioral or policy approval evidence is created.'};
}
export function applyPolicyPlan(document,plan){
 if(plan.outcome!=='proposed')throw Error('A blocked proposal cannot be applied.');
 if(document.revision!==plan.baseRevision)throw Error('Stale proposal base.');
 const doc=clone(document);
 for(const op of plan.operations){if(!['entities','requirements','gaps','decisions'].includes(op.collection))throw Error('Unsupported patch collection.');const collection=doc[op.collection];
  if(op.action==='append'){if(collection.some(x=>x.id===op.value.id))throw Error('Duplicate patch identity.');collection.push(clone(op.value));}
  else if(op.action==='replace'){const index=collection.findIndex(x=>x.id===op.id);if(index<0||!same(collection[index],op.before))throw Error('Patch precondition failed.');collection[index]=clone(op.value);}
  else throw Error('Unsupported patch operation.');
 }
 return doc;
}
export function validatePolicyPreservation(before,after,plan){
 const failures=[];
 for(const key of ['id','schemaVersion','kind','name','intent','libraryRef','layers','links','questions','validation','unusedLayers'])if(!same(before[key],after[key]))failures.push('changed-'+key);
 for(const old of before.requirements)if(!same(old,after.requirements.find(r=>r.id===old.id)))failures.push('changed-requirement:'+old.id);
 for(const old of before.gaps)if(!same(old,after.gaps.find(g=>g.id===old.id)))failures.push('lost-or-changed-gap:'+old.id);
 for(const e of before.entities){const next=after.entities.find(x=>x.id===e.id);if(!next){failures.push('lost-entity:'+e.id);continue;}
  if(!plan.impact.affectedIds.includes(e.id)&&!same(e,next))failures.push('unrelated-entity-changed:'+e.id);
  for(const k of ['id','layer','kind','members','itemRef','interface','resourceRefs','fieldBindings'])if(!same(e[k],next[k]))failures.push('identity-or-interface-changed:'+e.id+':'+k);
  if(!plan.impact.seeds.includes(e.id)&&!same(e.configuration,next.configuration))failures.push('downstream-config-rewritten:'+e.id);
 }
 const required=after.requirements.find(r=>r.id==='R-'+plan.rule.id);
 if(!required||required.status!=='proposed')failures.push('policy-approval-invented');
 if(after.validation.behavior!=='not-tested'||after.validation.deployment!=='not-requested')failures.push('evidence-invented');
 const independentImpact=impactClosure(before,plan.impact.seeds);
 for(const id of independentImpact.unchangedIds)if(!same(before.entities.find(e=>e.id===id),after.entities.find(e=>e.id===id)))failures.push('unrelated-entity-changed:'+id);
 for(const id of independentImpact.affectedIds){if(!after.entities.find(e=>e.id===id)?.policyRefs?.includes(required?.id))failures.push('missing-impact:'+id);}
 return {passed:failures.length===0,failures};
}
