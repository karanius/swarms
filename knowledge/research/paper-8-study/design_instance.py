"""Author and render a design specification; no agents, collection or business execution."""
from pathlib import Path
import json,base64,hashlib
import nbformat as nb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
NOTEBOOK=ROOT/'knowledge/research/notebooks/Paper 8 - Market Intelligence Instance.ipynb'
processes=[
 {'id':'P1','name':'Investigation governance','trigger':'new or changed brief','flow_refs':['F1'],'owner_role':'intelligence_owner','exit':'accepted scoped plan or explicit clarification'},
 {'id':'P2','name':'Opportunity investigation','trigger':'accepted plan','flow_refs':['F2','F3','F4'],'owner_role':'intelligence_owner','exit':'evidence and challenged claims or bounded insufficient result'},
 {'id':'P3','name':'Review and dossier handoff','trigger':'candidate dossier','flow_refs':['F5'],'owner_role':'evidence_reviewer','exit':'accepted handoff or recorded rejection'},
 {'id':'P4','name':'Freshness and revision','trigger':'expiry, correction or new evidence','flow_refs':['F6'],'owner_role':'intelligence_owner','exit':'superseding revision and affected-consumer notice'},
 {'id':'P5','name':'Cost and privacy stewardship','trigger':'each attempt and access event','flow_refs':[],'cross_cutting':True,'owner_role':'operations_owner','exit':'cost/access record or escalated exception'}]
composites=[
 ('C1','Brief-to-plan',['research_brief'],['research_plan','open_obligations'],'No invented scope or authority'),
 ('C2','Source-to-observations',['research_plan','source_locator'],['source_record','observation','retrieval_event'],'Actual source and access status; preserve failure'),
 ('C3','Evidence normalization',['source_record','observation'],['normalized_evidence','source_family'],'Preserve raw context and uncertain duplicate links'),
 ('C4','Problem and solution comparison',['research_brief','normalized_evidence'],['alternative'],'Include strong existing solutions and contrary evidence'),
 ('C5','Claim assessment',['normalized_evidence','alternative'],['claim'],'Support status and source entailment; no invented probability'),
 ('C6','Dossier assembly',['research_brief','claim','alternative','cost_event','open_obligations'],['opportunity_dossier'],'Expose missing evidence; no profitable-niche claim'),
 ('C7','Change impact',['change_notice','opportunity_dossier'],['impact_report','revision_request'],'Trace affected claims and preserve unrelated revisions')]
flows=[
 ('F1','Brief intake',['C1'],['research_brief'],['research_plan','open_obligations']),
 ('F2','Evidence acquisition',['C2'],['research_plan'],['source_record','observation','retrieval_event']),
 ('F3','Normalize and assess',['C3'],['source_record','observation'],['normalized_evidence','source_family']),
 ('F4','Synthesize and challenge',['C4','C5'],['normalized_evidence','research_brief'],['claim','alternative']),
 ('F5','Review and handoff',['C6'],['claim','alternative','research_brief','cost_event','open_obligations'],['opportunity_dossier','handoff_record']),
 ('F6','Refresh and revise',['C7'],['change_notice','opportunity_dossier'],['impact_report','revision_request'])]
fields={
 'source_locator':['url_or_authorized_path','source_type','access_authority','retrieval_policy_ref'],
 'research_brief':['decision_question','audience_job','language','geography','time_window','permitted_sources','time_cap','cash_cap','acceptance_owner'],
 'research_plan':['brief_ref','queries','inclusion_rules','exclusion_rules','counterevidence_strategy','stop_rules'],
 'open_obligations':['question','owner','blocked_transition','resolution_status'],
 'source_record':['locator','publisher','retrieval_status','content_hash','access_context','family_ref'],
 'observation':['source_ref','location','raw_statement_or_metric','unit','period','limits'],
 'retrieval_event':['attempt_ref','start','end','status','error_or_reason'],
 'normalized_evidence':['observation_ref','normalized_value','transform_ref','relevance','freshness'],
 'source_family':['member_refs','duplicate_basis','independence_status'],
 'alternative':['description','support_refs','opposing_refs','comparison_limits'],
 'claim':['statement','evidence_refs','opposing_refs','judgment','inference_limits','reviewer'],
 'cost_event':['attempt_ref','owner_minutes','resource_usage','cost_basis','allocation_key'],
 'opportunity_dossier':['brief_ref','audience_problem','claim_refs','alternative_refs','differentiation_hypothesis','uncertainty','open_obligation_refs','cost_refs','recommendation'],
 'handoff_record':['artifact_revision','recipient','decision','reason','acknowledgment'],
 'change_notice':['source_or_artifact_ref','change_reason','evidence_refs'],
 'impact_report':['affected_claim_refs','affected_consumers','unaffected_invariants'],
 'revision_request':['parent_revision','proposed_change','reason','review_status']}
spec={
 'schema_version':'0.1-design','id':'market-intelligence','revision':1,'status':'proposed-not-implemented',
 'operations_plane':{'business_ref':'paper7-local-content-business','role':'enclosing shared coordination plane','instance_ref':'market-intelligence'},
 'instance_contract':{'purpose':'Investigate audience problems and existing solutions; deliver traceable opportunity dossiers',
 'inputs':['research_brief','change_notice'],'outputs':['opportunity_dossier','handoff_record','cost_event','open_obligations'],
 'decisions_owned':['evidence judgments','research scope within accepted brief','bounded continue/narrow/ask/stop recommendations'],
 'decisions_not_owned':['business adoption','public release','spending','account changes'],
 'invariants':['Trace every factual claim to evidence or label assumption','Preserve contrary evidence and missingness','No duplicate source families counted as independent by default','New evidence creates a new revision','No public or financial side effects'],
 'completion':'Consumer accepts a versioned dossier or receives a reasoned blocked/insufficient outcome'},
 'processes':processes,
 'flows':[{'id':i,'name':name,'composite_refs':cs,'input_types':ins,'output_types':outs,'implementation':'deferred'} for i,name,cs,ins,outs in flows],
 'flow_dependencies':[{'from':'F1','to':'F2','condition':'accepted plan and access/limit gates pass'},
 {'from':'F2','to':'F3','condition':'available observations; failures remain recorded'},
 {'from':'F3','to':'F4','condition':'reviewable normalized evidence with independence/freshness limits'},
 {'from':'F4','to':'F5','condition':'challenged claims or explicit insufficient-evidence result'},
 {'from':'F5','to':'F6','condition':'accepted dossier later needs refresh','revision_boundary':True},
 {'from':'F6','to':'F1','condition':'targeted revised brief; preserve parent history','revision_boundary':True}],
 'composite_contracts':[{'id':i,'name':name,'input_types':ins,'output_types':outs,'acceptance':gate,'native_component_refs':[],'internal_wiring':None,'grounding_status':'unbound'} for i,name,ins,outs,gate in composites],
 'components':{'native_occurrences':[],'resource_adapters':[],'status':'selection-and-wiring-deferred','rule':'Only populate after actual pinned catalog and adapter verification'},
 'configuration':{'required_before_collection':{'audience_job':None,'language':None,'geography':None,'time_window':None,'permitted_sources':None,'time_cap':None,'cash_cap':None,'acceptance_owner':None},
 'runtime_bindings':{'model_revision':None,'model_license':None,'runtime':None,'secret_refs':[]},
 'policies':{'local_analysis_preferred':True,'calls_or_meetings_required':False,'personal_data_minimization':True,'unauthorized_access':'stop-and-record','publication_enabled':False,'spending_enabled':False,'account_changes_enabled':False,'retry_limit':None,'retention_policy':None},
 'unknown_rule':'Unresolved required fields block the relevant transition; do not silently choose defaults'},
 'artifact_contracts':{'common_envelope':['artifact_id','schema_version','revision','owner','created_at','access_classification','source_lineage'],
 'types':[{'id':k,'required_fields':v,'unknown_handling':'explicit unknown or validation failure according to accepted schema; never fabricated'} for k,v in fields.items()],
 'status':'proposed field contracts, not production JSON Schema validation'},
 'state_model':{'states':['draft','needs_clarification','planned','collecting','assessing','in_review','accepted','rejected','insufficient','blocked','cancelled','superseded'],
 'transitions':[['draft','needs_clarification'],['draft','planned'],['needs_clarification','planned'],['planned','collecting'],['collecting','assessing'],['assessing','in_review'],['in_review','accepted'],['in_review','rejected'],['assessing','insufficient'],['accepted','superseded']],
 'exception_rule':'Any active nonterminal state may become blocked or cancelled with a recorded reason; retry/rework creates a new attempt or revision',
 'missing_evidence_rule':'insufficient is an honest outcome, not proof of no demand'},
 'handoffs':[{'from':'Operations','to':'market-intelligence','artifact_types':['research_brief'],'authority':'scope and limit authorization'},
 {'from':'Audience Care','to':'market-intelligence','artifact_types':['change_notice'],'authority':'deidentified feedback evidence only'},
 {'from':'Finance and Performance','to':'market-intelligence','artifact_types':['change_notice'],'authority':'versioned metrics and resource context; no unsupported causal conclusion'},
 {'from':'market-intelligence','to':'Content Strategy','artifact_types':['opportunity_dossier','handoff_record'],'authority':'recommendation; not automatic strategy adoption'},
 {'from':'market-intelligence','to':'Finance and Performance','artifact_types':['cost_event'],'authority':'actual research costs including failed attempts'},
 {'from':'market-intelligence','to':'Operations','artifact_types':['open_obligations'],'authority':'scope, budget and access exceptions'}],
 'implementation_sequence':['Freeze one concrete research brief','Verify native catalog and resource options','Ground one composite contract at a time','Verify composite outputs before complete flow','Review a full dossier against original evidence','Validate handoff and revision behavior'],
 'evidence_status':{'market_collection_run':False,'native_graph_built':False,'local_inference_tested':False,'business_validated':False}}

def validate(s):
 errors=[]
 ids=lambda items:{i['id'] for i in items}
 fs=ids(s['flows']);cs=ids(s['composite_contracts']);ats=ids(s['artifact_contracts']['types'])
 for group in ['processes','flows','composite_contracts']:
  if len(ids(s[group]))!=len(s[group]):errors.append('Duplicate identity: '+group)
 for p in s['processes']:
  if not set(p['flow_refs'])<=fs:errors.append('Unknown process flow')
 for f in s['flows']:
  if not set(f['composite_refs'])<=cs:errors.append('Unknown composite')
  if not set(f['input_types']+f['output_types'])<=ats:errors.append('Unknown flow artifact type')
 for c in s['composite_contracts']:
  if not set(c['input_types']+c['output_types'])<=ats:errors.append('Unknown composite artifact type')
  if c['internal_wiring'] is not None or c['native_component_refs']:errors.append('Deferred internals unexpectedly bound')
 for e in s['flow_dependencies']:
  if e['from'] not in fs or e['to'] not in fs:errors.append('Unknown dependency endpoint')
 for h in s['handoffs']:
  if not set(h['artifact_types'])<=ats:errors.append('Unknown handoff artifact')
 if any(s['configuration']['policies'][k] for k in ['publication_enabled','spending_enabled','account_changes_enabled']):errors.append('Design-only side effect boundary violated')
 # Same-revision dependency graph must be acyclic. Refresh edges are across revisions.
 adjacency={x:[] for x in fs}
 for e in s['flow_dependencies']:
  if not e.get('revision_boundary') and e['from'] in fs and e['to'] in fs:adjacency[e['from']].append(e['to'])
 active=set();done=set()
 def visit(v):
  if v in active:return True
  if v in done:return False
  active.add(v)
  if any(visit(n) for n in adjacency[v]):return True
  active.remove(v);done.add(v);return False
 if any(visit(v) for v in fs):errors.append('Same-revision dependency cycle')
 return errors

if __name__=='__main__':
 errors=validate(spec);assert not errors,errors
 (D/'market-intelligence-instance.design.json').write_text(json.dumps(spec,indent=2))
 # All diagrams are projections of this same specification.
 fig,axes=plt.subplots(1,2,figsize=(17,10),facecolor='#111b26',gridspec_kw={'width_ratios':[.9,1.4]})
 for ax in axes:ax.set_facecolor('#111b26');ax.axis('off')
 ax=axes[0]
 levels=[('Operations plane','Shared authority, budgets and inter-instance handoffs'),('Market Intelligence','One specialized, revisionable instance'),('Processes',f"{len(spec['processes'])} accountable processes"),('Flows',f"{len(spec['flows'])} research and revision flows"),('Composite contracts',f"{len(spec['composite_contracts'])} capabilities; internals deferred"),('Components','Selection and wiring deferred'),('Configuration','Required settings and policies; values unresolved')]
 for j,(name,detail) in enumerate(levels):
  y=7-j
  ax.add_patch(FancyBboxPatch((.1,y),5.5,.78,boxstyle='round,pad=.025',facecolor='#234a50' if j<2 else '#273e55',edgecolor='#79aaa9'))
  ax.text(2.85,y+.52,name,ha='center',color='white',fontsize=12,weight='bold');ax.text(2.85,y+.20,detail,ha='center',color='#cbdee7',fontsize=8.8)
 ax.set_xlim(0,5.8);ax.set_ylim(.4,8.4);ax.set_title('INSTANCE CONTRACT VIEW',color='white',weight='bold',pad=20)
 ax=axes[1]
 for j,f in enumerate(spec['flows']):
  y=7-j
  ax.add_patch(FancyBboxPatch((.4,y),6.7,.7,boxstyle='round,pad=.025',facecolor='#273e55',edgecolor='#79aaa9'))
  ax.text(3.75,y+.45,f["name"],ha='center',color='white',fontsize=12,weight='bold')
  ax.text(3.75,y+.16,'Capabilities: '+', '.join(f['composite_refs']),ha='center',color='#c4d9e5',fontsize=9)
  if j<5:ax.annotate('',xy=(3.75,y-.27),xytext=(3.75,y-.04),arrowprops={'arrowstyle':'->','color':'#86bcb3','lw':1.5,'linestyle':'--' if j==4 else '-'})
 ax.text(3.75,1.1,'Refresh returns to a new brief/revision.\nClarification, rejection, cancellation and limits have explicit outcomes.',ha='center',color='#b8d7d8',fontsize=10)
 ax.set_xlim(0,7.6);ax.set_ylim(.4,8.4);ax.set_title('FLOW DEPENDENCIES',color='white',weight='bold',pad=20)
 fig.suptitle('Market Intelligence • one JSON specification, two visual projections',color='#e2f5f6',fontsize=18,weight='bold',y=.98)
 fig.text(.5,.025,'Design only • native components unbound • no research, agents or market experiments executed',ha='center',color='#b9d5df',fontsize=11)
 fig.tight_layout(rect=[0,.05,1,.95]);image=D/'instance-design-views.png';fig.savefig(image,dpi=150,facecolor=fig.get_facecolor(),bbox_inches='tight');plt.close(fig)
 notebook=nb.read(NOTEBOOK,as_version=4);before=[json.dumps(c,sort_keys=True) for c in notebook.cells]
 # Idempotence: do not duplicate an already appended design section.
 marker='paper8-json-design-v1'
 if any(c.get('metadata',{}).get('design_section')==marker for c in notebook.cells):raise SystemExit('Design section already exists; review rather than duplicate')
 intro=nb.v4.new_markdown_cell('''## 15. Inspectable instance specification — JSON and visual views
This addition specifies the Market Intelligence instance before component selection and composite internal wiring. The diagram and JSON are generated from the same authored specification. Native occurrences and adapters remain empty; unresolved configuration stays null. These are design artifacts, not a deployed instance.

The left view shows the five internal planes beneath the instance and Operations. The right view shows dependencies between research flows. The dashed step represents later refresh across revisions; it does not imply a same-version dependency loop.

**Design contents:** five processes, six flows, seven composite interface contracts, artifact field contracts, state/exception rules, inter-instance handoffs and implementation gates. Component implementations are deliberately deferred. A structural reference check is not a test of research quality or business value.''')
 intro.metadata['design_section']=marker
 picture=nb.v4.new_markdown_cell('![Market Intelligence JSON design: instance layers and flow dependencies](attachment:instance-design-views.png)');picture.attachments={'instance-design-views.png':{'image/png':base64.b64encode(image.read_bytes()).decode()}}
 jsoncell=nb.v4.new_markdown_cell('### JSON design specification\n\nThe full editable design is shown below. Null values mean unresolved, not a default or successful binding.\n\n```json\n'+json.dumps(spec,indent=2)+'\n```')
 notebook.cells.extend([intro,picture,jsoncell]);nb.validate(notebook);nb.write(notebook,NOTEBOOK)
 after=nb.read(NOTEBOOK,as_version=4);assert [json.dumps(c,sort_keys=True) for c in after.cells[:len(before)]]==before
 (D/'JSON-DESIGN-VERIFICATION.json').write_text(json.dumps({'existing_cells_preserved':len(before),'appended_cells':3,'reference_check_errors':errors,'specification':str(D/'market-intelligence-instance.design.json'),'diagram':str(image),'notebook_sha256':hashlib.sha256(NOTEBOOK.read_bytes()).hexdigest(),'status':'design-only'},indent=2))
 print('Appended JSON specification and two-view diagram; prior cells unchanged')
