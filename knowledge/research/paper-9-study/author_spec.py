"""Author Paper 9's machine-readable instance contract. No market or agent execution."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
existing=D/'market-intelligence.instance.json'
if existing.exists() and json.loads(existing.read_text()).get('status')=='implementation-bound-parameterized':
 raise SystemExit('Preserving implemented revision: this historical contract author cannot overwrite it. Use explicit revision tooling.')
S=lambda **kw:{'type':'string',**kw}
NONEMPTY=S(minLength=1)
ARR=lambda item:{'type':'array','items':item}
REF=NONEMPTY
ENUM=lambda *v:{'type':'string','enum':list(v)}
NUM={'type':'number','minimum':0}
BOOL={'type':'boolean'}
NULLSTR={'type':['string','null']}
OBJ=lambda props,req=None:{'type':'object','properties':props,'required':list(props) if req is None else req,'additionalProperties':False}
# Typed artifact payloads; arrays explicitly allow empty evidence and honest insufficient outcomes.
payloads={
'brief':OBJ({'question':NONEMPTY,'audience_job':NONEMPTY,'language':NONEMPTY,'geography':NONEMPTY,'time_window':NONEMPTY,'decision_owner':REF,'allowed_source_classes':ARR(NONEMPTY)}),
'plan':OBJ({'brief_ref':REF,'queries':ARR(OBJ({'query_id':REF,'query':NONEMPTY,'purpose':ENUM('support','counterevidence','existing_solution'),'source_class':NONEMPTY})),
'inclusion_rules':ARR(NONEMPTY),'exclusion_rules':ARR(NONEMPTY),'stop_policy_ref':REF,'amendment_reason':NULLSTR}),
'discovery_batch':OBJ({'plan_ref':REF,'candidates':ARR(OBJ({'locator':NONEMPTY,'query_ref':REF,'source_class':NONEMPTY,'screening':ENUM('eligible','excluded','needs_review'),'reason':NONEMPTY})),'coverage_limits':ARR(NONEMPTY)}),
'source_batch':OBJ({'discovery_ref':REF,'sources':ARR(OBJ({'source_id':REF,'locator':NONEMPTY,'publisher':NULLSTR,'retrieved_at':S(format='date-time'),'status':ENUM('retrieved','inaccessible','excluded','failed'),
'snapshot_ref':NULLSTR,'content_hash':NULLSTR,'published_at':NULLSTR,'access_basis':NONEMPTY,'license_status':ENUM('verified','unknown','restricted'),'failure_reason':NULLSTR})), 'attempt_refs':ARR(REF)}),
'evidence_set':OBJ({'sources_ref':REF,'observations':ARR(OBJ({'observation_id':REF,'source_id':REF,'location':NONEMPTY,'raw_observation':NONEMPTY,'normalized_value':{'type':['string','number','null']},'unit':NULLSTR,'period':NULLSTR,
'family_id':REF,'independence':ENUM('independent','dependent','unknown'),'freshness':ENUM('current','stale','unknown'),'relevance':ENUM('in_scope','out_of_scope','uncertain'),'transform_ref':NULLSTR})),
'family_decisions':ARR(OBJ({'family_id':REF,'source_ids':ARR(REF),'basis':NONEMPTY,'review_status':ENUM('reviewed','unreviewed','uncertain')}))}),
'alternative_set':OBJ({'brief_ref':REF,'alternatives':ARR(OBJ({'alternative_id':REF,'description':NONEMPTY,'strengths':ARR(NONEMPTY),'limits':ARR(NONEMPTY),'observation_refs':ARR(REF)})),'search_limits':ARR(NONEMPTY)}),
'candidate_claims':OBJ({'claims':ARR(OBJ({'claim_id':REF,'statement':NONEMPTY,'claim_kind':ENUM('observation','inference','hypothesis'),'support_refs':ARR(REF),'opposing_refs':ARR(REF),'scope_limits':ARR(NONEMPTY)}))}),
'assessment_set':OBJ({'candidate_ref':REF,'judgments':ARR(OBJ({'claim_id':REF,'status':ENUM('supported','contradicted','mixed','insufficient','stale','inaccessible'),'support_refs':ARR(REF),'opposing_refs':ARR(REF),'reason':NONEMPTY,
'entailment_review':ENUM('passed','failed','pending'),'reviewer_ref':NULLSTR,'inference_limits':ARR(NONEMPTY)})),'policy_ref':REF}),
'obligation_set':OBJ({'items':ARR(OBJ({'obligation_id':REF,'question':NONEMPTY,'owner_ref':REF,'blocks':ARR(REF),'status':ENUM('open','resolved','waived_with_reason'),'resolution':NULLSTR}))}),
'cost_ledger':OBJ({'events':ARR(OBJ({'event_id':REF,'attempt_id':REF,'stage_ref':REF,'status':ENUM('started','completed','failed','cancelled'),
'owner_minutes':NUM,'resource_usage':ARR(OBJ({'resource_ref':REF,'quantity':NUM,'unit':NONEMPTY})),
'amount':{'type':['number','null'],'minimum':0},'currency':NULLSTR,'cost_basis':ENUM('measured','assumed','unknown'),'allocation_key':REF})), 'accounting_limits':ARR(NONEMPTY)}),
'dossier':OBJ({'brief_ref':REF,'plan_ref':REF,'evidence_ref':REF,'alternatives_ref':REF,'assessments_ref':REF,'obligations_ref':REF,'cost_ledger_ref':REF,
'audience_problem':NONEMPTY,'differentiation_hypothesis':NULLSTR,'recommendation':ENUM('continue','narrow','ask','stop','insufficient'), 'reason':NONEMPTY,'uncertainty':ARR(NONEMPTY),'next_action':NONEMPTY,'business_profitability_proven':{'const':False}}),
'review_decision':OBJ({'dossier_ref':REF,'reviewer_ref':REF,'authority_ref':REF,'decision':ENUM('accepted','rework','rejected'),'checks':ARR(OBJ({'criterion_ref':REF,'status':ENUM('pass','fail','unknown'),'evidence_refs':ARR(REF),'reason':NONEMPTY})), 'reason':NONEMPTY,'critical_unresolved':{'type':'integer','minimum':0}}),
'handoff_receipt':OBJ({'dossier_ref':REF,'review_ref':REF,'recipient_id':{'const':'content-strategy'},'idempotency_key':REF,'delivery_status':ENUM('pending','acknowledged','rejected','failed'), 'acknowledgment_ref':NULLSTR,'reason':NONEMPTY}),
'change_notice':OBJ({'parent_dossier_ref':REF,'affected_source_or_metric_refs':ARR(REF),'reason':NONEMPTY,'origin_instance':ENUM('operations','audience-care','finance-performance','market-intelligence')}),
'impact_report':OBJ({'parent_dossier_ref':REF,'affected_claim_refs':ARR(REF),'consumer_refs':ARR(REF),'unaffected_invariants':ARR(NONEMPTY),'recommended_reentry':ENUM('intake','discover','retrieve','assess'),'reason':NONEMPTY}),
'revision_request':OBJ({'parent_dossier_ref':REF,'impact_ref':REF,'new_revision':{'type':'integer','minimum':2},'amendment_reason':NONEMPTY,'approval_status':ENUM('pending','approved','rejected')})}
envelope={'artifact_id':REF,'schema_version':{'const':'1.0-contract'},'business_id':{'const':'local-content-business'},'instance_id':{'const':'market-intelligence'},'revision':{'type':'integer','minimum':1},'owner_ref':REF,
'created_at':S(format='date-time'),'access_classification':ENUM('public','internal','restricted'),'source_lineage':ARR(REF)}
defs={}
for name,payload in payloads.items():
 defs[name]=OBJ({**envelope,'artifact_type':{'const':name},'payload':payload})
# Conditional requirements encode record shape, not whether source content is true.
source_item=defs['source_batch']['properties']['payload']['properties']['sources']['items']
source_item['allOf']=[{'if':{'properties':{'status':{'const':'retrieved'}}},'then':{'properties':{'snapshot_ref':NONEMPTY,'content_hash':S(pattern='^[a-f0-9]{64}$'),'failure_reason':{'type':'null'}}},'else':{'properties':{'failure_reason':NONEMPTY}}}]
judgment=defs['assessment_set']['properties']['payload']['properties']['judgments']['items']
judgment['allOf']=[{'if':{'properties':{'status':{'const':'contradicted'}}},'then':{'properties':{'opposing_refs':{**ARR(REF),'minItems':1},'entailment_review':{'const':'passed'},'reviewer_ref':REF}}},{'if':{'properties':{'status':{'const':'supported'}}},'then':{'properties':{'support_refs':{**ARR(REF),'minItems':1},'entailment_review':{'const':'passed'},'reviewer_ref':REF}}},
 {'if':{'properties':{'status':{'const':'mixed'}}},'then':{'properties':{'support_refs':{**ARR(REF),'minItems':1},'opposing_refs':{**ARR(REF),'minItems':1}}}}]
review=defs['review_decision']['properties']['payload']
review['allOf']=[{'if':{'properties':{'decision':{'const':'accepted'}}},'then':{'properties':{'critical_unresolved':{'const':0},'checks':{**ARR(review['properties']['checks']['items']),'minItems':1}}}}]
receipt=defs['handoff_receipt']['properties']['payload'];receipt['allOf']=[{'if':{'properties':{'delivery_status':{'const':'acknowledged'}}},'then':{'properties':{'acknowledgment_ref':REF}}}]
schemas={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://local.invalid/paper9/artifacts.schema.json','$defs':defs}

composite_data=[
 ('K01','Brief-to-plan',{'brief':'brief'},{'plan':'plan','obligations':'obligation_set'},'Frame a research plan without inventing limits','brief_schema_and_authority'),
 ('K02','Source discovery',{'plan':'plan'},{'candidates':'discovery_batch'},'Translate declared queries into screened candidate source locations','discovery_scope_and_coverage'),
 ('K03','Evidence retrieval',{'plan':'plan','candidates':'discovery_batch'},{'sources':'source_batch'},'Retrieve permitted original evidence and preserve failures','retrieval_provenance'),
 ('K04','Normalize and group evidence',{'sources':'source_batch'},{'evidence':'evidence_set'},'Preserve observations, transformations and uncertain source-family dependence','normalization_and_independence'),
 ('K05','Existing-solution comparison',{'brief':'brief','evidence':'evidence_set'},{'alternatives':'alternative_set'},'Find strong competing solutions and explanations','alternative_fairness'),
 ('K06','Candidate claim formation',{'brief':'brief','evidence':'evidence_set','alternatives':'alternative_set'},{'candidates':'candidate_claims'},'Explicitly separate observation, inference and hypothesis','candidate_scope'),
 ('K07','Evidence judgment',{'candidates':'candidate_claims','evidence':'evidence_set','alternatives':'alternative_set'},{'assessments':'assessment_set'},'Judge support, contradiction, scope and missing evidence','evidence_judgment'),
 ('K08','Dossier assembly',{'brief':'brief','plan':'plan','evidence':'evidence_set','alternatives':'alternative_set','assessments':'assessment_set','obligations':'obligation_set','costs':'cost_ledger'},{'dossier':'dossier'},'Assemble a traceable recommendation without replacing evidence','dossier_completeness'),
 ('K09','Independent review',{'brief':'brief','plan':'plan','candidates':'discovery_batch','sources':'source_batch','alternatives':'alternative_set','dossier':'dossier','evidence':'evidence_set','assessments':'assessment_set'},{'review':'review_decision'},'Accept, reject or request rework against declared criteria','review_acceptance'),
 ('K10','Versioned handoff',{'dossier':'dossier','review':'review_decision'},{'receipt':'handoff_receipt'},'Deliver accepted exact revision and record acknowledgment or failure','handoff_authority'),
 ('K11','Change-impact analysis',{'notice':'change_notice','parent':'dossier'},{'impact':'impact_report','revision':'revision_request'},'Trace changed evidence and request a new revision','revision_fidelity')]
composites=[{'id':i,'name':name,'input_ports':ins,'output_ports':outs,'responsibility':purpose,'acceptance_policy':policy,'internal_graph':None,'native_occurrence_refs':[],'status':'contract-only'} for i,name,ins,outs,purpose,policy in composite_data]
nodes=[
 ('intake','K01',{'brief':'input.brief'}),
 ('discover','K02',{'plan':'intake.plan'}),
 ('retrieve','K03',{'plan':'intake.plan','candidates':'discover.candidates'}),
 ('normalize','K04',{'sources':'retrieve.sources'}),
 ('compare','K05',{'brief':'input.brief','evidence':'normalize.evidence'}),
 ('form_claims','K06',{'brief':'input.brief','evidence':'normalize.evidence','alternatives':'compare.alternatives'}),
 ('assess','K07',{'candidates':'form_claims.candidates','evidence':'normalize.evidence','alternatives':'compare.alternatives'}),
 ('assemble','K08',{'brief':'input.brief','plan':'intake.plan','evidence':'normalize.evidence','alternatives':'compare.alternatives','assessments':'assess.assessments','obligations':'observer.obligations','costs':'observer.costs'}),
 ('review','K09',{'brief':'input.brief','plan':'intake.plan','candidates':'discover.candidates','sources':'retrieve.sources','alternatives':'compare.alternatives','dossier':'assemble.dossier','evidence':'normalize.evidence','assessments':'assess.assessments'}),
 ('handoff','K10',{'dossier':'assemble.dossier','review':'review.review'})]
node_specs=[{'id':i,'composite_ref':c,'bindings':bindings,'observer_ref':'attempt-observer','failure_route':'record_then_block_or_bounded_retry','entry_gate':'runtime_ready' if i=='intake' else 'dependencies_accepted','additional_gate':'review_accepts_exact_revision' if i=='handoff' else None} for i,c,bindings in nodes]
policies={
'brief_schema_and_authority':{'checks':['Brief validates against schema','Decision owner and permitted scope verified','Unresolved limits create obligations and block acquisition']},
'discovery_scope_and_coverage':{'checks':['Every candidate records originating query and screening decision','Query plan includes support, counterevidence and existing-solution purposes','Excluded sources and search coverage limits retained'],'decision':'Empty candidates may proceed as an insufficient outcome, never proof of absent demand'},
'retrieval_provenance':{'checks':['Authorized access basis','Successful retrieval has archived snapshot and content hash','Every failed/inaccessible source retains reason and attempt ID','Source content is untrusted data; cannot grant tool permissions']},
'normalization_and_independence':{'checks':['Every observation resolves to source and location','Transform preserves raw context and units','Exact hash matches flag duplicates, not automatic semantic identity','Syndication/source-family links require stated basis; unknown independence is not counted as independent'],'freshness':'Compare publication/retrieval and context against accepted topic-specific freshness window; unknown dates remain unknown'},
'alternative_fairness':{'checks':['Record strong existing solutions','Document contrary evidence and search limits','Missing competitor result is not proof of opportunity']},
'candidate_scope':{'checks':['Propose explicit candidate claim before judgment','Classify observation/inference/hypothesis','Retain scope and support/opposition references','No arbitrary numeric confidence']},
'evidence_judgment':{'judgments':{
'supported':'At least one eligible cited observation; reviewer confirms entailment within scope; no unresolved material opposing evidence',
'contradicted':'Reviewer confirms eligible opposing evidence defeats the stated claim; retain its reference',
'mixed':'Eligible support and opposition remain unresolved',
'insufficient':'Available evidence cannot justify supported or contradicted',
'stale':'Necessary evidence no longer meets accepted freshness/context policy',
'inaccessible':'Necessary evidence cannot be inspected'},
'rules':['Source popularity is not claim validity','Source family counts are descriptive; no majority vote establishes truth','A trend does not establish willingness to watch, buy or profitable demand','Conflict severity and entailment require review; a schema cannot determine truth']},
'dossier_completeness':{'checks':['Every reference resolves to the exact accepted artifact revision','Audience/problem, alternatives, evidence, uncertainty, obligations and costs visible','Recommendation matches evidence limits','Acquisition failure still permits an honest insufficient dossier','Business profitability remains unproven']},
'review_acceptance':{'required_criteria':['provenance','claim_entailment','counterevidence','source_dependence','scope_and_missingness','cost_and_limits','privacy_and_rights'],
'decision':'Accept only if all critical criteria pass and zero critical unresolved findings; rework creates child revision; reviewer may be human or separately authorized assistant with accountable human acceptance owner',
'independence':'No self-approval; separate reviewer occurrence/context; disclose shared-model bias'},
'handoff_authority':{'checks':['Accepted review references exact dossier revision','Recipient and access classification authorized','Idempotency key is business+instance+artifact+revision+recipient','Acknowledgment distinguishes delivered from accepted','Failed delivery does not erase accepted dossier']},
'revision_fidelity':{'checks':['Parent revision immutable','Impact lists affected claims and consumers','New brief/attempt references parent and amendment reason','Consumer notifications have acknowledgment records','Unrelated artifacts do not change']}}

spec={
 'schema_version':'1.0-contract','business_id':'local-content-business','instance_id':'market-intelligence','revision':1,
 'status':'specified-not-implemented','operations_plane':{'ref':'local-content-business/operations','role':'enclosing coordination plane'},
 'instance_contract':{'purpose':'Source-grounded audience problem and existing-solution intelligence for Content Strategy','external_inputs':{'brief':'brief'},'external_outputs':{'dossier':'assemble.dossier','review':'review.review','handoff':'handoff.receipt','obligations':'observer.obligations','costs':'observer.costs'},
 'completion_outcomes':['accepted_and_acknowledged','accepted_delivery_pending','rejected_with_reason','insufficient_with_evidence_limits','blocked_with_obligations','cancelled_with_costs'],
 'forbidden_decisions':['choose the entire business without owner decision','publish content','spend money','open/change accounts','claim demand or profitability from source counts']},
 'processes':[{'id':'P1','name':'Govern investigation','flow_refs':['investigate'],'owns_nodes':['intake'],'owner_role':'intelligence_owner'},
 {'id':'P2','name':'Investigate opportunity','flow_refs':['investigate'],'owns_nodes':['discover','retrieve','normalize','compare','form_claims','assess'],'owner_role':'intelligence_owner'},
 {'id':'P3','name':'Review and handoff','flow_refs':['investigate'],'owns_nodes':['assemble','review','handoff'],'owner_role':'evidence_reviewer'},
 {'id':'P4','name':'Refresh and revise','flow_refs':['refresh'],'owns_nodes':['impact'],'owner_role':'intelligence_owner'},
 {'id':'P5','name':'Cost, access and privacy stewardship','flow_refs':['investigate','refresh'],'owns_nodes':[],'observer_refs':['attempt-observer'],'owner_role':'operations_owner'}],
 'flows':[{'id':'investigate','external_inputs':{'brief':'brief'},'nodes':node_specs,'result_bindings':{'dossier':'assemble.dossier','review':'review.review','receipt':'handoff.receipt'}},
 {'id':'refresh','external_inputs':{'notice':'change_notice','parent':'dossier'},'nodes':[{'id':'impact','composite_ref':'K11','bindings':{'notice':'input.notice','parent':'input.parent'},'observer_ref':'attempt-observer','entry_gate':'runtime_ready','failure_route':'record_then_block_or_bounded_retry','additional_gate':None}],
 'result_bindings':{'impact':'impact.impact','revision':'impact.revision'},'next_flow':{'ref':'investigate','condition':'owner approves revised brief based on impact','revision_boundary':True,'input_construction':'New brief explicitly records parent dossier and amendment; never reuse a stale accepted plan implicitly'}}],
 'composites':composites,
 'components':{'native_occurrences':[],'resource_adapters':[],'grounding_status':'deferred','required_resource_roles':['permitted-source discovery','retrieval and snapshot store','deterministic parsing','evidence family review','local synthesis model','schema and cross-artifact validator','artifact registry','scoped review and delivery'],
 'grounding_gate':['actual pinned native catalog','actual adapter contracts','model/checkpoint rights','typed port validation','bounded runtime behavior proof'], 'note':'These roles are not claimed native Langflow component names'},
 'observers':[{'id':'attempt-observer','output_bindings':{'costs':'cost_ledger','obligations':'obligation_set'},'coverage':'Every node attempt in every flow, including failure, rejection, retry and cancellation','event_schema_ref':'cost_ledger',
 'obligation_rule':'Merge intake obligations and all later stage exceptions into a versioned obligation set; resolved items retain resolution history',
 'persistence':'append to immutable event log with unique attempt/event identities','cost_rule':'No missing cost treated as zero; distinguish measured, assumed and unknown; allocate shared cost once; internal transfers are not revenue',
 'snapshot_rule':'Dossier receives a ledger snapshot through assembly. Final ledger includes later review/handoff costs; final ledger checkpoint is linked at closure without mutating the reviewed dossier',
 'implementation':'required middleware contract; not implemented'}],
 'artifact_schema_file':'artifacts.schema.json','policies':policies,
 'configuration':{'design_mode':True,'required_before_activation':{'audience_job':None,'language':None,'geography':None,'time_window':None,'source_connectors':None,'allowed_sources':None,'freshness_window':None,'time_cap_seconds':None,'cash_cap_amount':None,'currency':None,'max_attempts_per_node':None,'max_concurrent_retrievals':None,'retention_policy':None,'storage_binding':None,'review_acceptance_owner':None},
 'role_bindings':{'intelligence_owner':None,'evidence_reviewer':None,'operations_owner':None},'runtime_bindings':{'model_revision':None,'runtime':None,'secret_refs':[]},
 'side_effects':{'publication':False,'spending':False,'account_changes':False},'local_generation':'Local synthesis requirement must be verified at runtime; source retrieval and other services may be online',
 'unknown_gate':'Required unresolved activation values block acquisition; dry contract validation remains permitted'},
 'persistence_contract':{'artifacts':'Immutable artifact ID+revision; content hash plus schema version','events':'Append-only attempt log; causal run/attempt IDs and real timestamps','checkpoints':'Persist accepted node outputs; resume only when input hashes, configuration revision and permissions match',
 'concurrency':'Per-run revision compare-and-swap and idempotency keys; bounded worker leases; rejected stale writes recorded','reference_resolution':'Artifact ID+revision+type resolves to stored record; no source URL substitutes for immutable content','retention':'Owner-set policy by classification; legitimate deletion leaves tombstone/access status rather than dangling invented evidence','implementation':'not implemented'},
 'handoffs':[{'sender':'operations','recipient':'market-intelligence','artifact':'brief','rule':'Authenticated scope/limits and acceptance authority'},
 {'sender':'audience-care','recipient':'market-intelligence','artifact':'change_notice','rule':'Deidentified evidence with authority and source limits'},
 {'sender':'finance-performance','recipient':'market-intelligence','artifact':'change_notice','rule':'Metrics retain cohort, period, denominator and uncertainty; invalid evidence is rejected'},
 {'sender':'market-intelligence','recipient':'content-strategy','artifact':'dossier','rule':'Exact revision plus review; recipient acknowledgment required'},
 {'sender':'market-intelligence','recipient':'finance-performance','artifact':'cost_ledger','rule':'Final costs including review/handoff; snapshot vs final distinguished'},
 {'sender':'market-intelligence','recipient':'operations','artifact':'obligation_set','rule':'Blocked scope/access/budget or policy decisions escalated'}],
 'readiness':{'json_contract':'subject to validation','native_graph':'unbound','source_access':'unverified','model_inference':'unverified','market_evidence':'none collected','business_value':'untested'}}
# Guards are an explicit Boolean context contract, evaluated by the validator utility without eval.
guards={
 'runtime_ready':{'all':['configuration_resolved','roles_authorized','components_grounded','access_authorized','budget_reserved']},
 'dependencies_accepted':{'all':['inputs_schema_valid','references_resolved','upstream_accepted','budget_remaining']},
 'review_accepts_exact_revision':{'all':['review_accepted','review_matches_dossier_revision','recipient_authorized','critical_checks_passed']},
 'may_review':{'all':['dossier_schema_valid','references_resolved','reviewer_authorized','reviewer_separate_from_author']},
 'may_accept':{'all':['critical_checks_passed','zero_critical_findings','reviewer_authorized']},
 'may_revise':{'all':['parent_record_preserved','new_revision_assigned','amendment_recorded','owner_approved']},
 'may_acknowledge':{'all':['recipient_authorized','ack_matches_revision','idempotency_checked']}}
spec['guards']=guards
spec['guard_context_contract']={'default':'Missing or unknown inputs evaluate false; no truth inferred from model text','producers':{'configuration_resolved':'validated activation configuration','roles_authorized':'authority registry','components_grounded':'pinned catalog and runtime qualification','access_authorized':'allowed source/account policy','budget_reserved':'time/cash reservation ledger','inputs_schema_valid':'JSON Schema validator','references_resolved':'artifact registry','upstream_accepted':'checkpoint registry','budget_remaining':'live time/cash ledger','review_accepted':'review_decision','review_matches_dossier_revision':'artifact reference comparison','recipient_authorized':'authority registry','critical_checks_passed':'complete review rubric','dossier_schema_valid':'JSON Schema validator','reviewer_authorized':'authority registry','reviewer_separate_from_author':'actor and context separation record','zero_critical_findings':'review_decision','parent_record_preserved':'artifact registry','new_revision_assigned':'revision allocator','amendment_recorded':'revision record','owner_approved':'approval record','ack_matches_revision':'handoff_receipt','idempotency_checked':'delivery registry'}}
transitions=[('draft','plan','planned','runtime_ready'),('planned','collect','collecting','dependencies_accepted'),('collecting','assess','assessing','dependencies_accepted'),('assessing','submit','in_review','may_review'),('in_review','accept','accepted','may_accept'),('in_review','rework','rework_requested',None),('in_review','reject','rejected',None),('assessing','insufficient','insufficient',None),('accepted','deliver','delivery_pending','review_accepts_exact_revision'),('delivery_pending','acknowledge','acknowledged','may_acknowledge'),('delivery_pending','delivery_failed','delivery_failed',None),('delivery_failed','retry_delivery','delivery_pending','review_accepts_exact_revision')]
spec['lifecycle']={'states':['draft','needs_clarification','planned','collecting','assessing','in_review','accepted','rework_requested','rejected','insufficient','blocked','cancelled','delivery_pending','delivery_failed','acknowledged','superseded'],
 'transitions':[{'from':a,'event':e,'to':b,'guard':g,'actor_role':'evidence_reviewer' if a=='in_review' else 'intelligence_owner','record_required':True} for a,e,b,g in transitions],
 'cross_cutting_transitions':[{'from':['draft','planned'],'event':'missing_scope','to':'needs_clarification','record':'obligation_set'},
 {'from':'active','event':'cap_or_access_failure','to':'blocked','record':'obligation_set'}, {'from':'active','event':'cancel','to':'cancelled','record':'cost_ledger'},
 {'from':['blocked','needs_clarification','rework_requested','insufficient'],'event':'revise','to':'draft','guard':'may_revise','new_revision':True},
 {'from':['accepted','acknowledged'],'event':'refresh_approved','to':'superseded','guard':'may_revise','new_revision':True,'next':'draft'}],
 'terminal_states':['rejected','cancelled','superseded'],'active_states':['draft','needs_clarification','planned','collecting','assessing','in_review','rework_requested','blocked','delivery_pending','delivery_failed'],
 'retry_policy':'Each retry creates unique attempt; maximum/time cap from configuration; no retry of denied authority; cancellation propagates to leased work and records costs',
 'implementation':'state transition contract; not deployed orchestration'}
activation_fields={k:NONEMPTY for k in spec['configuration']['required_before_activation']}
for k in ['source_connectors','allowed_sources']:activation_fields[k]={**ARR(NONEMPTY),'minItems':1}
for k in ['time_cap_seconds','freshness_window']:activation_fields[k]={'type':'number','exclusiveMinimum':0}
activation_fields['cash_cap_amount']=NUM
for k in ['max_attempts_per_node','max_concurrent_retrievals']:activation_fields[k]={'type':'integer','minimum':1}
activation={'$schema':'https://json-schema.org/draft/2020-12/schema',**OBJ({'design_mode':{'const':False},'required_before_activation':OBJ(activation_fields),'role_bindings':OBJ({k:NONEMPTY for k in spec['configuration']['role_bindings']}),'runtime_bindings':OBJ({'model_revision':NONEMPTY,'runtime':NONEMPTY,'secret_refs':ARR(REF)}),'side_effects':OBJ({k:{'const':False} for k in spec['configuration']['side_effects']}),'local_generation':NONEMPTY,'unknown_gate':NONEMPTY})}
(D/'activation.schema.json').write_text(json.dumps(activation,indent=2))
(D/'artifacts.schema.json').write_text(json.dumps(schemas,indent=2))
(D/'market-intelligence.instance.json').write_text(json.dumps(spec,indent=2))
print('Authored JSON instance and typed artifact schemas')
