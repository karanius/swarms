import copy,json,unittest,tempfile
from pathlib import Path
from relational_experiment import parse_rule,token,canonical,exact_rules,make_cases,apply_direct,metrics,proposal,native_answers,run_engine
A=canonical(['Agent','in','ChatInput','message','input_value'])
B=canonical(['Agent','out','ChatOutput','response','input_value'])
C=canonical(['Agent','in','Prompt','prompt','system_prompt'])
def tx(i,items,graph=None):return {'id':str(i),'graph':graph or 'g'+str(i),'center':'Agent-'+str(i),'centerType':'Agent','items':items}
class ContractTests(unittest.TestCase):
 def test_allowlist_rejects_bridges_memorization_tautology(self):
  v={token(x):x for x in [A,B,C]};good=f'has_feature(X,{token(B)}) <= has_feature(X,{token(A)})';self.assertEqual(parse_rule(good,v),(A,B))
  for bad in [good.replace('<= has_feature(X,','<= has_feature(Y,'),good.replace('X,','o123,',1),good+', has_feature(Y,'+token(C)+')',f'has_feature(X,{token(A)}) <= has_feature(X,{token(A)})',good.replace(token(B),'f'+'0'*24)]:self.assertIsNone(parse_rule(bad,v))
 def test_center_type_confound_is_not_a_rule(self):
  D=canonical(['Other','out','ChatOutput','response','input_value']);v={token(x):x for x in [A,D]};self.assertIsNone(parse_rule(f'has_feature(X,{token(D)}) <= has_feature(X,{token(A)})',v))
 def test_counts_and_center_conditioned_lift(self):
  ts=[tx(i,([A,B] if i<6 else [A] if i<8 else [C])) for i in range(10)];families={t['graph']:'family'+str(i%2) for i,t in enumerate(ts)};rr,_=exact_rules(ts,families);r=next(r for r in rr if r['body']==A and r['head']==B);self.assertEqual((r['bodyCount'],r['jointCount']), (8,6));self.assertAlmostEqual(r['confidence'],.75);self.assertAlmostEqual(r['centerLift'],1.25)
 def test_separate_centers_never_form_joint_rule(self):
  ts=[tx(i,[A] if i%2 else [B]) for i in range(20)];rr,_=exact_rules(ts,{t['graph']:t['graph'] for t in ts});self.assertEqual(rr,[])
 def test_mask_removes_every_target_copy_and_is_deterministic(self):
  t=tx('mask',[A,A,B,B]);families={t['graph']:'family'};c=make_cases([t],families)[0];self.assertNotIn(c['target'],c['visible']);self.assertEqual(make_cases([t],families),make_cases([t],families));self.assertEqual(t['items'],[A,A,B,B])
 def test_apply_filters_known_heads_and_ranks_canonically(self):
  rr=[{'id':'rule','body':A,'head':B,'confidence':.8}];self.assertEqual(apply_direct(rr,[A],'Agent')[0],[B]);self.assertEqual(apply_direct(rr,[A,B],'Agent')[0],[]);self.assertEqual(apply_direct(rr,[C],'Agent')[0],[])
 def test_metrics_keep_abstention_and_mismatch_distinct(self):
  cases=[{'id':'a','family':'f','target':B},{'id':'b','family':'g','target':B},{'id':'c','family':'g','target':B}];m,r=metrics(cases,[[{'feature':B,'score':.8}],[],[{'feature':C,'score':.9}]]);self.assertEqual((m['answered'],m['recovered']),(2,1));self.assertEqual(m['recoveryPerAnswer'],.5);self.assertEqual(m['familyMacroRecovery'],.5)
 def test_unknown_catalog_abstains_instead_of_inventing_ports(self):
  case={'id':'a','visible':[A]};r={'prediction':B,'ruleIds':['rule']};rules={'rule':{'body':A,'head':B}};self.assertEqual(proposal(case,r,rules,{})['status'],'unresolved-catalog')
 def test_proposal_preserves_required_fields_resources_and_sources(self):
  def descriptor(kind,ins,outs):return {'descriptor':{'type':kind,'version':'fixture','inputs':[{'name':n,'types':ty,'required':True} for n,ty in ins],'outputs':[{'name':n,'types':ty} for n,ty in outs],'resourceRequirements':[{'field':'api_key','required':True}]},'graph':'training-only','node':kind,'sources':[{'sourceUrl':'https://example.org/training'}]}
  catalog={'Agent':[descriptor('Agent',[('input_value',['Message']),('model',[])],[('response',['Message'])])],'ChatInput':[descriptor('ChatInput',[],[('message',['Message'])])],'ChatOutput':[descriptor('ChatOutput',[('input_value',['Message'])],[])]}
  r={'prediction':B,'ruleIds':['rule']};p=proposal({'id':'c','visible':[A]},r,{'rule':{'body':A,'head':B}},catalog);self.assertEqual(len(p['edges']),2);self.assertTrue(p['structuralChecks']['allKnownTypesOverlap']);self.assertTrue(any(e['field']=='model' for e in p['requiredExposures']));self.assertEqual(len(p['resources']),3);self.assertTrue(all(n['graph']=='training-only' for n in p['nodes']));self.assertEqual(p['status'],'proposal-only')
 def test_stale_engine_artifact_is_rejected_before_launch(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'rules.txt';p.write_text('stale')
   with self.assertRaisesRegex(RuntimeError,'stale'):run_engine(p,p)
 def test_native_does_not_truncate_more_than_ten_answers(self):
  heads=[canonical(['Agent','out','Neighbor'+str(i),'response','input']) for i in range(16)];ts=[tx('train',[A,*heads])];cases=[{'id':'case','entity':'ocase','visible':[A],'centerType':'Agent'}];rr=[{'id':str(i),'body':A,'head':f,'bodyCount':10,'jointCount':8,'confidence':.8} for i,f in enumerate(heads)];ans=native_answers(rr,ts,cases,{token(f):f for f in [A,*heads]});self.assertEqual(len(ans[0]),16)
 def test_native_predictions_match_direct_rule(self):
  ts=[tx('train',[A,B])];cases=[{'id':'case','entity':'ocase','visible':[A],'centerType':'Agent'}];r={'id':'r','body':A,'head':B,'bodyCount':10,'jointCount':8,'confidence':.8};ans=native_answers([r],ts,cases,{token(A):A,token(B):B});self.assertEqual(ans[0][0]['feature'],B);self.assertAlmostEqual(ans[0][0]['score'],.8)
if __name__=='__main__':unittest.main()
