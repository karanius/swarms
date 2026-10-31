"""Concrete capability resources used by the JSON-driven controller and native adapter."""
import json,hashlib,uuid,urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
from engine import NOW

def brief_to_plan(e,inputs):
 brief=inputs['brief'];b=e.payload(brief)
 queries=[{'query_id':f'q{i}','query':b['question'],'purpose':p,'source_class':'approved-source-catalog'} for i,p in enumerate(['support','counterevidence','existing_solution'])]
 return {'plan':e.emit('plan',{'brief_ref':brief,'queries':queries,'inclusion_rules':['Allowed host and public original document'],'exclusion_rules':['Private or unauthorized source','Unpermitted host','Duplicate content'],'stop_policy_ref':'bounded-profile','amendment_reason':None}), 'obligations':e.emit('obligation_set',{'items':[]})}

def discover(e,inputs):
 catalog=list(e.store.run(e.run_id)['body']['source_catalog']);items=[];limits=[]
 if e.cfg.get('web_search_enabled',False):
  if e.cfg.get('external_query_authorized') is not True:raise PermissionError('External query transmission requires explicit per-request authorization')
  for query in e.payload(inputs['plan'])['queries'][:e.cfg.get('max_search_queries',3)]:
   address='https://html.duckduckgo.com/html/?'+urllib.parse.urlencode({'q':query['query']+' '+query['purpose'],'kl':'us-en'})
   original=list(e.cfg['allowed_hosts'])
   try:
    e.cfg['allowed_hosts']=original+['html.duckduckgo.com']
    raw,_=e.fetcher(address,e.store.check_bound(e.run_id));soup=BeautifulSoup(raw,'html.parser')
    results=soup.select('a.result__a')
    if not results:limits.append('Search produced no parseable results; absent results may be blocking or page change, not absent demand')
    for link in results[:e.cfg['max_sources']]:
     url=link.get('href','');parsed=urllib.parse.urlsplit(url);target=urllib.parse.parse_qs(parsed.query).get('uddg',[url])[0]
     target=urllib.parse.unquote(target)
     catalog.append({'url':target,'reason':'Search candidate: '+link.get_text(' ',strip=True),'query_ref':query['query_id']})
   except (InterruptedError,TimeoutError):raise
   except Exception as exc:limits.append('Search failure: '+type(exc).__name__+': '+str(exc)[:150])
   finally:e.cfg['allowed_hosts']=original
 else:limits.append('Source-catalog mode: no open-web search requested')
 seen=set()
 for src in catalog:
  if src['url'] in seen:continue
  seen.add(src['url']);parsed=urllib.parse.urlsplit(src['url']);ok=parsed.scheme=='https' and parsed.hostname in e.cfg['allowed_hosts'] and not parsed.username and not parsed.password
  items.append({'locator':src['url'],'query_ref':src.get('query_ref','q0'),'source_class':'approved-source-catalog' if not src.get('query_ref') else 'public-search-candidate','screening':'eligible' if ok else 'excluded','reason':src.get('reason','Source-catalog candidate') if ok else 'Locator not permitted'})
  if len(items)>=e.cfg['max_sources']:break
 limits.append('Bounded discovery; source coverage does not establish market prevalence or demand')
 return {'candidates':e.emit('discovery_batch',{'plan_ref':inputs['plan'],'candidates':items,'coverage_limits':limits})}

def retrieve(e,inputs):
 records=[];attempt=e.current_attempt
 for i,c in enumerate(e.payload(inputs['candidates'])['candidates']):
  if c['screening']!='eligible':continue
  s={'source_id':'s'+str(i),'locator':c['locator'],'publisher':urllib.parse.urlsplit(c['locator']).hostname,'retrieved_at':NOW(),'status':'failed','snapshot_ref':None,'content_hash':None,'published_at':None,'access_basis':'Authorized public HTTPS under exact allowlist','license_status':'unknown','failure_reason':None}
  try:
   raw,_=e.fetcher(c['locator'],e.store.check_bound(e.run_id));h=hashlib.sha256(raw).hexdigest();path=e.store.root/'snapshots'/h;path.parent.mkdir(exist_ok=True)
   if path.exists() and path.read_bytes()!=raw:raise ValueError('Immutable snapshot hash mismatch')
   if not path.exists():
    with path.open('xb') as f:f.write(raw)
   s.update(status='retrieved',snapshot_ref=str(path),content_hash=h)
  except (TimeoutError,InterruptedError):raise
  except Exception as exc:s['failure_reason']=type(exc).__name__+': '+str(exc)[:300]
  records.append(s)
 return {'sources':e.emit('source_batch',{'discovery_ref':inputs['candidates'],'sources':records,'attempt_refs':[attempt]})}

def normalize(e,inputs):
 observations=[];families={}
 for s in e.payload(inputs['sources'])['sources']:
  if s['status']!='retrieved':continue
  path=Path(s['snapshot_ref']).resolve()
  if not path.is_relative_to((e.store.root/'snapshots').resolve()):raise PermissionError('Snapshot outside run store')
  raw=path.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=s['content_hash']:raise ValueError('Source content changed')
  soup=BeautifulSoup(raw,'html.parser')
  for el in soup(['script','style','nav','footer','header']):el.decompose()
  content=soup.select_one('article') or soup.select_one('.article-content-body') or soup
  text=' '.join(content.get_text(' ',strip=True).split())[:e.cfg['max_text_chars']]
  family='sha256:'+s['content_hash'];families.setdefault(family,[]).append(s['source_id'])
  observations.append({'observation_id':'o'+s['source_id'],'source_id':s['source_id'],'location':'Bounded normalized HTML article text','raw_observation':text,'normalized_value':None,'unit':None,'period':None,'family_id':family,'independence':'unknown','freshness':'unknown','relevance':'uncertain','transform_ref':'BeautifulSoup article text and whitespace normalization'})
 return {'evidence':e.emit('evidence_set',{'sources_ref':inputs['sources'],'observations':observations,'family_decisions':[{'family_id':k,'source_ids':v,'basis':'Exact content hash; semantic dependence needs review','review_status':'uncertain'} for k,v in families.items()]})}

def compare(e,inputs):
 evidence=e.payload(inputs['evidence']);observations={o['observation_id']:o for o in evidence['observations']};records=[];limits=['Only source-described alternatives; no superiority, coverage or market prevalence inferred']
 try:
  candidates=e.alternative_finder(e.payload(inputs['brief']),evidence,e.store.check_bound(e.run_id))
  for row in candidates[:3]:
   oid=row.get('observation_id');quote=row.get('quote');description=row.get('description')
   if oid in observations and isinstance(quote,str) and 15<=len(quote)<=250 and quote in observations[oid]['raw_observation'] and isinstance(description,str) and description.strip():
    records.append({'alternative_id':'a'+str(len(records)+1),'description':'Candidate for review: '+description[:500],'strengths':['Source excerpt: '+quote],'limits':['Description and relevance require independent review; no comparative superiority established'],'observation_refs':[oid]})
 except (InterruptedError,TimeoutError):raise
 except Exception as exc:limits.append('Alternative extraction failed: '+type(exc).__name__+': '+str(exc)[:150])
 if not records:limits.append('No verified candidate alternatives extracted; this is not evidence of no competitors')
 return {'alternatives':e.emit('alternative_set',{'brief_ref':inputs['brief'],'alternatives':records,'search_limits':limits})}

def form_claims(e,inputs):
 ev=e.payload(inputs['evidence']);rows=e.synthesizer(e.payload(inputs['brief']),ev,e.store.check_bound(e.run_id));obs={o['observation_id']:o for o in ev['observations']};claims=[]
 for row in rows[:3]:
  ref=row.get('observation_id');quote=row.get('quote')
  if ref in obs and isinstance(quote,str) and 15<=len(quote)<=250 and quote in obs[ref]['raw_observation']:
   claims.append({'claim_id':'c'+str(len(claims)+1),'statement':quote,'claim_kind':'observation','support_refs':[ref],'opposing_refs':[],'scope_limits':['Exact captured quotation only; truth, entailment, counterevidence and market relevance unreviewed']})
 return {'candidates':e.emit('candidate_claims',{'claims':claims})}

def assess(e,inputs):
 candidates=e.payload(inputs['candidates'])['claims'];evidence=e.payload(inputs['evidence']);obs={o['observation_id']:o for o in evidence['observations']}
 for c in candidates:
  if any(r not in obs for r in c['support_refs']+c['opposing_refs']):raise ValueError('Claim points to missing observation')
 feedback=e.payload(inputs['feedback'])
 if feedback['status']=='submitted':
  record=e.store.get(feedback['assessments_ref'])
  if record['artifact_type']!='assessment_set' or record['owner_ref']!=e.cfg['reviewer']:raise PermissionError('Assessment authority or type mismatch')
  if record['payload']['candidate_ref']!=inputs['candidates']:raise ValueError('Assessment candidate revision mismatch')
  ids={c['claim_id'] for c in candidates};judgments=record['payload']['judgments']
  if {j['claim_id'] for j in judgments}!=ids or len(judgments)!=len(ids):raise ValueError('Review must assess each candidate exactly once')
  for j in judgments:
   if j['reviewer_ref']!=e.cfg['reviewer']:raise PermissionError('Judgment reviewer mismatch')
   if any(r not in obs for r in j['support_refs']+j['opposing_refs']):raise ValueError('Judgment evidence reference missing')
  return {'assessments':feedback['assessments_ref']}
 return {'assessments':e.emit('assessment_set',{'candidate_ref':inputs['candidates'],'judgments':[{'claim_id':c['claim_id'],'status':'insufficient','support_refs':c['support_refs'],'opposing_refs':c['opposing_refs'],'reason':'Captured evidence exists; independent semantic and context review pending','entailment_review':'pending','reviewer_ref':None,'inference_limits':c['scope_limits']} for c in candidates],'policy_ref':'evidence_judgment'})}

def assemble(e,inputs):
 b=e.payload(inputs['brief']);feedback=e.payload(inputs['feedback'])
 recommendation='insufficient';reason='Evidence captured but independent review and adequate market/alternative evidence are required'
 if feedback['status']=='submitted':
  recommendation=feedback['recommendation'];reason=feedback['reason']
  if recommendation=='continue' and not any(j['status']=='supported' for j in e.payload(inputs['assessments'])['judgments']):raise ValueError('Continue recommendation requires at least one reviewed supported claim')
 for ref in inputs.values():e.store.get(ref)
 return {'dossier':e.emit('dossier',{'brief_ref':inputs['brief'],'plan_ref':inputs['plan'],'evidence_ref':inputs['evidence'],'alternatives_ref':inputs['alternatives'],'assessments_ref':inputs['assessments'],'obligations_ref':inputs['obligations'],'cost_ledger_ref':inputs['costs'],'audience_problem':b['audience_job'],'differentiation_hypothesis':None,'recommendation':recommendation,'reason':reason,'uncertainty':['Source-catalog coverage limited','Semantic independence/freshness unverified','No audience demand or revenue observed'],'next_action':'Independent review and targeted evidence gathering','business_profitability_proven':False},lineage=[feedback['parent_dossier_ref']] if feedback['status']=='submitted' else [])}

def review(e,inputs):
 from validate_contract import validate_review_acceptance,validate_artifact
 run=e.store.run(e.run_id);decision=run['body'].get('review_submission')
 if not decision:raise e.ReviewRequired(inputs['dossier'])
 if decision['payload']['dossier_ref']!=inputs['dossier']:raise PermissionError('Review references another dossier revision')
 if decision['owner_ref']!=decision['payload']['reviewer_ref']:raise PermissionError('Review envelope actor mismatch')
 for check in decision['payload']['checks']:
  for ref in check['evidence_refs']:e.store.get(ref)
 if decision['payload']['reviewer_ref']==e.store.get(inputs['dossier'])['owner_ref']:raise PermissionError('No self approval')
 if decision['payload']['reviewer_ref']!=e.cfg['reviewer']:raise PermissionError('Reviewer role mismatch')
 errs=validate_artifact(decision)+validate_review_acceptance(decision,e.spec['policies']['review_acceptance']['required_criteria'])
 if errs:raise ValueError('; '.join(errs))
 e.store.approve(e.run_id,inputs['dossier'],e.cfg['reviewer'],decision['payload']['decision'],decision['payload'])
 return {'review':e.store.put(decision)}

def handoff(e,inputs):
 r=e.payload(inputs['review'])
 if r['decision']!='accepted':raise PermissionError('Dossier review not accepted')
 d=e.store.deliver(e.run_id,inputs['dossier'],'content-strategy',e.cfg['reviewer'])
 return {'receipt':e.emit('handoff_receipt',{'dossier_ref':inputs['dossier'],'review_ref':inputs['review'],'recipient_id':'content-strategy','idempotency_key':d['key'],'delivery_status':'pending','acknowledgment_ref':None,'reason':'Durable local outbox delivery; separate consumer acknowledgment required'})}

def impact(e,inputs):
 notice=e.payload(inputs['notice']);parent=e.store.get(inputs['parent'])
 if notice['parent_dossier_ref']!=inputs['parent']:raise ValueError('Change notice parent mismatch')
 assessments=e.payload(parent['payload']['assessments_ref']);affected=[c['claim_id'] for c in assessments['judgments']]
 # Conservative whole-dossier invalidation is explicit; do not pretend exact semantic impact inference.
 ir=e.emit('impact_report',{'parent_dossier_ref':inputs['parent'],'affected_claim_refs':affected,'consumer_refs':['content-strategy'],'unaffected_invariants':['Parent artifacts remain immutable','Other runs unchanged'],'recommended_reentry':'intake','reason':'Conservative invalidation: all parent claims require reconsideration for this change'})
 return {'impact':ir,'revision':e.emit('revision_request',{'parent_dossier_ref':inputs['parent'],'impact_ref':ir,'new_revision':parent['revision']+1,'amendment_reason':notice['reason'],'approval_status':'pending'})}

HANDLERS={'K01':brief_to_plan,'K02':discover,'K03':retrieve,'K04':normalize,'K05':compare,'K06':form_claims,'K07':assess,'K08':assemble,'K09':review,'K10':handoff,'K11':impact}
