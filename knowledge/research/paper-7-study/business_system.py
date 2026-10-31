"""Authored multi-instance design, never an operational business or native graph."""
from copy import deepcopy
PLANES=('configuration','components','composites','flows','processes')
SPECS=[
('market-intelligence','Market Intelligence','Identify audience problems and evidence, not select the editorial slate',
 'Dated public observations, audience feedback and research questions','Opportunity dossiers, counterevidence and confidence limits',
 'Queries, audience/language, inclusion and deduplication policies',
 'Evidence collection / provenance normalization / problem comparison',
 'Observation collection → deduplication → opportunity assessment',
 'Accountable research cycle; source freshness and uncertainty review'),
('content-strategy','Content Strategy','Choose differentiated viewer outcomes and allocate content priorities',
 'Opportunity dossiers, performance reports, capacity and revenue constraints','Versioned content briefs, acceptance rubrics and portfolio decisions',
 'Audience promise, editorial standards, experiment allocation and topic exclusions',
 'Opportunity-to-brief / portfolio prioritization / acceptance rubric',
 'Compare alternatives → select brief → reserve capacity → revise or cancel',
 'Editorial planning and hypothesis review, with explicit owner approval gates'),
('production','Production','Produce reproducible original media against an accepted brief',
 'Approved content brief, rights constraints and resource bindings','Private release package, provenance, QA and actual effort record',
 'Pinned model/voice/tool revisions, scene schema and render profile',
 'Evidence-to-script / script-to-scenes / narration / media QA',
 'Script → original demo/diagrams → audio → render → QA → package',
 'Local production, maintenance and quality ownership; failed attempts retained'),
('distribution','Distribution','Manage channels, release state and audience measurement delivery',
 'Accepted package, publication authorization, channel policy and account binding','Release receipts or blocked status, analytics snapshots and corrections',
 'Channel/account references, metadata, timezone, disclosure and release policy',
 'Package-to-channel metadata / release-state tracking / analytics collection',
 'Validate package → approval → private staging → authorized release → reconcile',
 'Channel operations and takedown/correction lifecycle; publishing currently disabled'),
('monetization','Monetization','Define and maintain appropriate eligible revenue mechanisms',
 'Viewer value, audience signals, verified eligibility and product/offer evidence','Versioned monetization plan, approved offers and attributed receipt claims',
 'Allowed programs, offer terms, disclosures, product versions and support envelope',
 'Eligibility assessment / relevant-offer selection / product delivery contract',
 'Evaluate route → accept or reject → configure offer → monitor/refund/update',
 'Revenue-route governance; no guaranteed earnings or hidden custom service'),
('audience-care','Audience Care','Own feedback, corrections and asynchronous service exceptions',
 'Comments, questions, privacy/rights reports and optional customer issues','Categorized signals, correction requests, resolutions and unresolved cases',
 'Channels, response standards, consent/retention and escalation policy',
 'Feedback triage / correction dossier / written response proposal',
 'Receive → classify → resolve within authority or escalate → close with record',
 'Audience trust and optional product support; no calls or meetings required'),
('finance-performance','Finance and Performance','Reconcile money, total effort and business performance',
 'Cost events, release/cohort measures, attributable revenue and payout evidence','Cost ledger, receipt reconciliation, budget envelope and decision reports',
 'Currency, cost allocation, owner hour value, budget/time cap and income target',
 'Cost reconciliation / revenue attribution / cohort comparison / budget forecast',
 'Ingest → reconcile → distinguish estimates/cash → assess → advise Operations',
 'Financial control and performance learning; no tax advice or automatic spend')]

def make_system():
 instances=[]
 for row in SPECS:
  ident,name,mandate,inputs,outputs,config,comps,flow,proc=row
  instances.append({'id':ident,'name':name,'mandate':mandate,'inputs':inputs,'outputs':outputs,
   'planes':{'configuration':{'proposed':config,'bindings':[]},
    'components':{'native_occurrences':[],'status':'unresolved: requires pinned native catalog and real adapters'},
    'composites':{'proposed_capabilities':comps,'status':'authored candidate contracts'},
    'flows':{'proposed':flow,'status':'not executable'},
    'processes':{'proposed':proc,'status':'accountability design'}},
   'state':'design','revision':1})
 # Feedback is across revisions; these are handoff contracts, not claimed native wires.
 routes=[
 ('market-intelligence','content-strategy','opportunity-dossier','Source IDs, audience/job, alternatives, counterevidence, freshness; not demand proof'),
 ('content-strategy','production','content-brief','Viewer outcome, evidence, originality, acceptance rubric, budget reservation; no unsupported claims'),
 ('production','distribution','release-package','Asset hashes, rights/QA, captions, disclosure proposal, version; no public release authority'),
 ('distribution','audience-care','release-context','Release ID/status and version for feedback routing, no excessive personal data'),
 ('distribution','finance-performance','analytics-snapshot','Platform, cohort, metric denominator, period, availability and source receipt'),
 ('audience-care','market-intelligence','audience-problem-signal','Deidentified problem evidence with uncertainty and source authority'),
 ('audience-care','production','correction-request','Affected version, claim and evidence, severity; proposal cannot rewrite history'),
 ('audience-care','monetization','customer-exception','Optional product/offer reference, issue and permitted resolution; refund requires authority'),
 ('monetization','content-strategy','revenue-constraints','Eligible routes, relevant offer, evidence and conflicts; editorial value preserved'),
 ('monetization','distribution','offer-metadata','Versioned approved links/disclosures or explicit no-offer; no fabricated endorsement'),
 ('monetization','finance-performance','revenue-claim','External transaction/payout ID, status, currency, gross/fees/refunds; reconcile before counting'),
 ('production','finance-performance','production-cost-event','Attempt ID, real resource/time, reject cost and owner effort; never successful-only'),
 ('finance-performance','content-strategy','performance-decision-report','Cost/value evidence, uncertainty and alternatives; no views-to-profit shortcut')]
 for domain in ['market-intelligence','content-strategy','distribution','monetization','audience-care']:
  routes.append((domain,'finance-performance','domain-cost-event','Actual research, operator, maintenance, fees or service effort; unique event identity and shared-cost allocation; no internal transfer counted as revenue'))
 contracts=[{'id':f'h{i+1:02d}','from':a,'to':b,'artifact_type':k,'acceptance':v,
  'required_envelope':['business_id','instance_id','artifact_id','revision','schema_version','status','source_refs','created_at','idempotency_key','owner','acceptance_record','access_classification'],
  'rejection':'reject/quarantine with reason; preserve submitted version; return obligation to sender',
  'implementation':'proposed contract, no transport implemented'} for i,(a,b,k,v) in enumerate(routes)]
 return {'schema_version':1,'business_id':'local-content-business','revision':2,'status':'provisional-design',
  'goal':'Useful original content with sustainable economic profit, local production and no meetings',
  'shared_planes':list(PLANES),'instances':instances,'handoff_contracts':contracts,
  'operations':{'role':'coordination over instances, not a sixth plane or an eighth specialized instance',
   'responsibilities':['intent and priority arbitration','budget/time envelopes','approval and exception routing','versioned change coordination','stop/revise/continue decisions'],
   'controls':{'publication_enabled':False,'spending_enabled':False,'account_changes_enabled':False,
               'monthly_cash_cap':None,'owner_hours_cap':None,'income_target':None},
   'unknown_gate':'No production commitment until relevant owner decisions and measured feasibility are recorded'},
  'shared_library':{'native_definitions':'unchanged, pinned when verified','resource_bindings':'separate from native definitions',
    'occurrences':'unique per instance, may reference the same definition; no silent collapse'},
  'business_evidence':'research only: no production, demand, sales or profitability validation'}

def validate_system(s):
 errors=[]
 ids=[i['id'] for i in s.get('instances',[])]
 if len(ids)!=7 or len(ids)!=len(set(ids)):errors.append('Seven distinct specialized instances required')
 for i in s.get('instances',[]):
  if set(i.get('planes',{}))!=set(PLANES):errors.append('Shared plane contract violated: '+i['id'])
  if i.get('planes',{}).get('components',{}).get('native_occurrences'):errors.append('Ungrounded native occurrences in research-only design')
 seen=set()
 for h in s.get('handoff_contracts',[]):
  if h['from'] not in ids or h['to'] not in ids:errors.append('Unknown handoff endpoint')
  if h['id'] in seen:errors.append('Duplicate handoff identity')
  seen.add(h['id'])
  if not h.get('acceptance') or not h.get('rejection'):errors.append('Handoff requires acceptance and rejection')
 incoming={h['to'] for h in s.get('handoff_contracts',[])};outgoing={h['from'] for h in s.get('handoff_contracts',[])}
 if set(ids)-incoming or set(ids)-outgoing:errors.append('Business domain disconnected from inputs or outputs')
 controls=s.get('operations',{}).get('controls',{})
 if any(controls.get(k) is not False for k in ['publication_enabled','spending_enabled','account_changes_enabled']):errors.append('Research authorization boundary violated')
 return errors
