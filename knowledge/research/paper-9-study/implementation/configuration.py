"""Resolve per-investigation parameters into the typed activation configuration."""
from pathlib import Path
from validate_contract import validate_activation
D=Path(__file__).resolve().parents[1]
def resolve(spec,request):
 brief=request['brief'];profile=request['profile']
 required={'audience_job':brief['audience_job'],'language':brief['language'],'geography':brief['geography'],'time_window':brief['time_window'],
 'source_connectors':['approved-source-catalog']+(['public-search'] if profile.get('web_search_enabled') else []),'allowed_sources':profile['allowed_hosts'],
 'freshness_window':profile.get('freshness_window_seconds',604800),'time_cap_seconds':profile['time_cap_seconds'],'cash_cap_amount':0,'currency':profile.get('currency','USD'),
 'max_attempts_per_node':profile['max_attempts_per_stage'],'max_concurrent_retrievals':1,'retention_policy':'retain run store until explicit owner cleanup; no automatic deletion',
 'storage_binding':str(D/'.runtime'/'tower'/'state.sqlite3'),'review_acceptance_owner':profile['reviewer']}
 cfg={'design_mode':False,'required_before_activation':required,'role_bindings':{'intelligence_owner':'local-research-engine','evidence_reviewer':profile['reviewer'],'operations_owner':brief['decision_owner']},
 'runtime_bindings':{'model_revision':profile['model'],'runtime':'/Users/x/projects/langflow/.venv/bin/python','secret_refs':[]},'side_effects':{'publication':False,'spending':False,'account_changes':False},
 'local_generation':'Existing local Ollama only; no paid inference endpoint','unknown_gate':'Invalid or missing request fields are rejected before any collection'}
 errors=validate_activation(cfg)
 if errors:raise ValueError('Activation configuration invalid: '+'; '.join(errors)[:500])
 return cfg
