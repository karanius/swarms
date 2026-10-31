import copy,sys,unittest
from architecture import ArchitectureDesigner,port_inventory,possible_port_pairs,observed_witnesses,validate_proposal,sha,summarize_candidate
from test_upgrade import VIDEO_QUERY

def reseal(p):p.pop('digest',None);p['digest']=sha(p);return p

class ProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.designer=ArchitectureDesigner();cls.proposal=cls.designer.propose(VIDEO_QUERY,k=6)
    def test_original_requirements_preserved(self):self.assertEqual({s['capability'] for s in self.proposal['slots']},{'script_input','image_generation','video_generation','narration','subtitles','video_assembly'})
    def test_or_alternative_not_double_requirement(self):
        groups=self.proposal['requirement_groups'];self.assertEqual(len(groups),5);self.assertTrue(any(g['kind']=='OR' and set(g['members'])=={'image_generation','video_generation'} for g in groups))
    def test_conflicting_cloud_candidates_never_selected(self):
        for s in self.proposal['slots']:
            if s['primary']:self.assertFalse(s['primary']['assessment']['constraint_conflict'])
        self.assertFalse(next(s for s in self.proposal['slots'] if s['capability']=='video_generation')['primary'])
    def test_unknown_hardware_does_not_become_ready(self):
        self.assertEqual(self.proposal['coverage']['validated_implementations'],0);self.assertFalse(self.proposal['architecture_accepted']);self.assertIn('not executable',self.proposal['readiness'])
    def test_assembly_gap_kept(self):self.assertTrue(any(g.get('capability')=='video_assembly' for g in self.proposal['gaps']))
    def test_missing_endpoint_never_claimed_connected(self):
        slots={s['capability']:s for s in self.proposal['slots']}
        for r in self.proposal['relations']:
            if not slots[r['source_capability']]['primary'] or not slots[r['target_capability']]['primary']:self.assertEqual(r['status'],'unresolved')
    def test_archived_sources_and_ports_validate(self):self.assertEqual(validate_proposal(self.proposal,self.designer.engine),[])
    def test_no_semantic_or_adapter_proof_invented(self):
        for r in self.proposal['relations']:self.assertFalse(r['semantic_mapping_verified']);self.assertFalse(r['automatic_adapter_selected'])
    def test_revision_uses_alternative_and_preserves_parent(self):
        d=ArchitectureDesigner(self.designer.engine);first=d.propose('Find script input and narration');before=copy.deepcopy(first);chosen=next(s['primary']['id'] for s in first['slots'] if s['capability']=='script_input')
        second=d.propose('Find script input and narration',parent=1,excluded_ids=[chosen],revision_reason='Controlled candidate exclusion, not an observed defect')
        self.assertEqual(d.revision(1),before);self.assertEqual(second['parent_digest'],first['digest']);self.assertNotEqual(next(s['primary']['id'] for s in second['slots'] if s['capability']=='script_input'),chosen)
    def test_revision_reason_required(self):
        with self.assertRaises(ValueError):self.designer.propose(VIDEO_QUERY,parent=1)
    def test_returned_copy_is_not_history(self):
        d=ArchitectureDesigner(self.designer.engine);p=d.propose('Find script input');p['question']='tampered';self.assertNotEqual(d.revision(1)['question'],'tampered')
    def test_unknown_domain_no_wiring_invented(self):
        p=ArchitectureDesigner(self.designer.engine).propose('Find SQL queries and vector retrieval');self.assertFalse(p['relations']);self.assertTrue(any(g.get('capability')=='cross-capability relationships' for g in p['gaps']))
    def test_unmapped_request_stays_unmapped(self):
        p=ArchitectureDesigner(self.designer.engine).propose('Find zzzquantum987 zzzbathymetry654');self.assertEqual(p['slots'][0]['state'],'unmapped');self.assertFalse(p['slots'][0]['primary'])
    def test_no_local_constraint_can_admit_declared_cloud_option(self):
        p=ArchitectureDesigner(self.designer.engine).propose('Find script input and video generation');s=next(s for s in p['slots'] if s['capability']=='video_generation');self.assertIsNotNone(s['primary']);self.assertFalse(p['architecture_accepted'])
    def test_forged_ready_flag_rejected_even_with_new_digest(self):
        p=copy.deepcopy(self.proposal);p['architecture_accepted']=True;reseal(p);self.assertIn('Unverified architecture promoted',validate_proposal(p,self.designer.engine))
    def test_forged_ports_rejected(self):
        p=copy.deepcopy(self.proposal);s=next(s for s in p['slots'] if s['primary']);s['primary']['ports']['outputs'].append({'port':'invented'});reseal(p);self.assertIn('Candidate contract/source differs from archive',validate_proposal(p,self.designer.engine))
    def test_forged_semantic_mapping_rejected(self):
        p=copy.deepcopy(self.proposal);p['relations'][0]['semantic_mapping_verified']=True;reseal(p);self.assertIn('Unverified connection promoted',validate_proposal(p,self.designer.engine))
    def test_dangling_relation_rejected(self):
        p=copy.deepcopy(self.proposal);p['relations'][0]['target_capability']='invented';reseal(p);self.assertIn('Unknown relation endpoint',validate_proposal(p,self.designer.engine))
    def test_real_archived_wire_is_traceable(self):
        template=next(d for d in self.designer.engine.docs if d['kind']=='template' and d['edges'] and not d['unresolved_edges'])
        edge=template['edges'][0];left=copy.deepcopy(template);right=copy.deepcopy(template)
        left['kind']=right['kind']='connected_group';left['nodes']=[n for n in template['nodes'] if n['node_id']==edge['source']];right['nodes']=[n for n in template['nodes'] if n['node_id']==edge['target']]
        proof=observed_witnesses(left,right);self.assertTrue(any(w['edge']==edge for w in proof['witnesses']))
    def test_type_overlap_is_never_called_behavior_proof(self):
        out={'outputs':[{'declared_types':['Message'],'port':'x'}]};inp={'inputs':[{'declared_types':['Message'],'port':'y','credential':False}]};pairs=possible_port_pairs(out,inp);self.assertTrue(pairs);self.assertIn('unverified',pairs[0]['status'])
    def test_forged_source_wire_rejected(self):
        p=copy.deepcopy(self.proposal);primary=next(s['primary'] for s in p['slots'] if s['primary']);src=primary['sources']
        p['relations'][0]['source_wiring_evidence']['witnesses']=[{'file':src['file'],'sha256':src['sha256'],'graph_pointer':src['graph_pointer'],'edge':{'source':'invented','target':'invented'}}];reseal(p)
        self.assertIn('Invalid archived wiring witness',validate_proposal(p,self.designer.engine))
    def test_saved_history_restores_and_corruption_does_not(self):
        d=ArchitectureDesigner.restore([self.proposal],self.designer.engine);self.assertEqual(d.revision(1),self.proposal)
        broken=copy.deepcopy(self.proposal);broken['question']='tampered'
        with self.assertRaises(ValueError):ArchitectureDesigner.restore([broken],self.designer.engine)

if __name__=='__main__':unittest.main(verbosity=2)
