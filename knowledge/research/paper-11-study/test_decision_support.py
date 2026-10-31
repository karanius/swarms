import unittest,copy
from architecture import ArchitectureDesigner,validate_proposal,sha
from design_adviser import diagnose,clarification_questions,normalize_context
from test_upgrade import VIDEO_QUERY
class DecisionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=ArchitectureDesigner();cls.p=cls.d.propose(VIDEO_QUERY,k=30)
 def test_complete_paths_keep_or_exclusive(self):
  a=self.p['decision_support']['approaches'];self.assertEqual(len(a),2)
  for path in a:
   self.assertEqual(len(set(path['members'])&{'image_generation','video_generation'}),1)
   self.assertIn('video_assembly',path['members']);self.assertEqual(path['required_count'],5)
 def test_no_evidence_winner_when_tied(self):
  a=self.p['decision_support']['approaches']
  if a[0]['provisional_count']==a[1]['provisional_count']:self.assertIn('no evidence-backed winner',self.p['decision_support']['recommendation_reason'])
 def test_source_references_are_real(self):
  for a in self.p['decision_support']['approaches']:
   for key in a['source_evidence_ids']:self.assertIn(key,self.d.engine.by_id)
   self.assertEqual(a['verified_implementations'],0)
 def test_clarification_changes_requirements_only_explicitly(self):
  qs=clarification_questions('Local video generation on my Mac',{});self.assertEqual({q['field'] for q in qs},{'memory_gb','output_goal','duration_seconds'})
  p=ArchitectureDesigner(self.d.engine).propose('Local video generation on my Mac',context={'memory_gb':64,'duration_seconds':30,'output_goal':'narrated_video'},k=30)
  self.assertFalse(p['decision_support']['questions']);self.assertIn('video_assembly',{s['capability'] for s in p['slots']});self.assertEqual(p['coverage']['validated_implementations'],0)
 def test_context_never_proves_hardware(self):
  p=ArchitectureDesigner(self.d.engine).propose(VIDEO_QUERY,context={'memory_gb':128,'visual_path':'video_generation'})
  ds=p['decision_support'];a=next(a for a in ds['approaches'] if a['id']==ds['recommended_approach']);self.assertIn('video_generation',a['members']);self.assertIn('preference',ds['recommendation_reason']);self.assertFalse(p['architecture_accepted'])
 def test_gap_taxonomy(self):
  slot={'capability':'video_generation','label':'Video','primary':None,'alternatives':[]};self.assertEqual(diagnose(slot)['category'],'retrieval_gap')
  c={'id':'fixture','assessment':{'constraint_conflict':True}};slot['alternatives']=[c];self.assertEqual(diagnose(slot)['category'],'constraint_conflict')
  slot['alternatives'].append({'id':'fixture2','assessment':{'constraint_conflict':False}});self.assertEqual(diagnose(slot)['category'],'mixed_evidence_gap')
  slot['alternatives']=[slot['alternatives'][1]];self.assertEqual(diagnose(slot)['category'],'qualification_gap')
  slot['primary']=slot['alternatives'][0];self.assertEqual(diagnose(slot)['category'],'unverified')
  slot['capability']='unmapped';self.assertEqual(diagnose(slot)['category'],'interpretation_gap')
 def test_first_action_addresses_core_gap(self):
  a=self.p['decision_support']['next_technical_action'];self.assertEqual(a['priority'],'resolve_gap');self.assertNotIn('Script input',a['title'])
 def test_unknown_domain_no_fabricated_handoffs(self):
  p=ArchitectureDesigner(self.d.engine).propose('Find SQL queries and vector retrieval');self.assertFalse(p['relations']);self.assertTrue(any(a['priority']=='design' for a in p['decision_support']['next_actions']))
 def test_unknown_request_gets_interpretation_action(self):
  p=ArchitectureDesigner(self.d.engine).propose('Find zzzquantum987');self.assertEqual(p['decision_support']['diagnoses'][0]['category'],'interpretation_gap')
 def test_altered_support_rejected(self):
  p=copy.deepcopy(self.p);p['decision_support']['summary']='Everything works';p.pop('digest');p['digest']=sha(p);self.assertIn('Decision support differs from grounded proposal',validate_proposal(p,self.d.engine))
 def test_exclusions_and_context_survive_second_revision(self):
  d=ArchitectureDesigner(self.d.engine);a=d.propose('Find script input',context={'memory_gb':64});key=a['slots'][0]['primary']['id'];b=d.propose('Find script input',parent=1,excluded_ids=[key],revision_reason='Explore');c=d.propose('Find script input',parent=2,revision_reason='Recheck');self.assertIn(key,c['excluded_ids']);self.assertEqual(c['design_context'],{'memory_gb':64.0});self.assertNotEqual(c['slots'][0]['primary']['id'],key)
 def test_box_identity_search_and_source_obligations(self):
  for slot in self.p['slots']:
   self.assertTrue(slot['search_query']);self.assertEqual(slot['search_limit'],30)
   if slot['primary']:
    self.assertIn(slot['primary']['kind'],('component','connected_group','template'));self.assertTrue(slot['primary']['sources']['origins'])
   else:self.assertTrue(next(d for d in self.p['decision_support']['diagnoses'] if d['capability']==slot['capability'])['next_action'])
 def test_invalid_context_rejected(self):
  for c in [{'memory_gb':-1},{'visual_path':'cloud'},{'invented':True},{'output_goal':'anything'}]:
   with self.assertRaises(ValueError):normalize_context(c)
if __name__=='__main__':unittest.main(verbosity=2)
