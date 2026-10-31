"""Exposed development scenarios, not independent user-comprehension evidence."""
import json
from pathlib import Path
from architecture import ArchitectureDesigner,validate_proposal
from test_upgrade import VIDEO_QUERY
SCENARIOS=[('local_video',VIDEO_QUERY,{}),('clarified_narrated_video','Local video generation on my Mac',{'memory_gb':64,'duration_seconds':30,'output_goal':'narrated_video','visual_path':'image_generation'}),('non_media','Find SQL queries and vector retrieval',{}),('unknown','Find zzzquantum987',{})]
def evaluate():
 d=ArchitectureDesigner();cases=[]
 for name,q,ctx in SCENARIOS:
  p=d.propose(q,k=30,context=ctx);ds=p['decision_support']
  cases.append({'case':name,'question':q,'context':ctx,'summary':ds['summary'],'recommendation_reason':ds['recommendation_reason'],'approaches':[{'name':a['name'],'members':a['members'],'unfilled':a['unfilled'],'evidence_ids':a['source_evidence_ids']} for a in ds['approaches']],'next_action':ds['next_technical_action'],'diagnoses':ds['diagnoses'],'checks':{'valid_source_contracts':not validate_proposal(p,d.engine),'concrete_next_action':bool(ds['next_technical_action']['title']),'requirements_retained':all(any(c in a['members'] for a in ds['approaches']) for g in p['requirement_groups'] for c in g['members']),'no_runtime_promotion':not p['architecture_accepted'] and p['coverage']['validated_implementations']==0,'relation_profile_limit_visible':bool(p['relations']) or any(a['priority']=='design' for a in ds['next_actions'])}})
 result={'scope':'Exposed development scenarios plus contract checks; no independent user-comprehension study, system runtime or optimality proof.','cases':cases,'all_contract_checks_pass':all(all(c['checks'].values()) for c in cases)}
 Path(__file__).with_name('DECISION-EVALUATION.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 r=evaluate();print(json.dumps({c['case']:{'summary':c['summary'],'next_action':c['next_action']['title'],'checks':c['checks']} for c in r['cases']},indent=2))
