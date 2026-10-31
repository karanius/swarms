import unittest,sys
from request_analysis import interpret,qualification
from search_engine import CorpusSearch,requested_facets

VIDEO_QUERY='Find reusable pieces for a video-generation pipeline that runs locally on an Apple Silicon Mac. I need script input, image or video generation, narration, subtitles, and final video assembly. Show each piece’s hardware requirements, dependencies, inputs and outputs. Identify anything requiring cloud services, paid APIs, or custom development, and report capabilities with no matching evidence.'
VIDEO_CAPS={'script_input','image_generation','video_generation','narration','subtitles','video_assembly'}

class IntentTests(unittest.TestCase):
    def test_full_video_request_not_research(self):
        i=interpret(VIDEO_QUERY);self.assertEqual({c['id'] for c in i['capabilities']},VIDEO_CAPS)
        self.assertTrue(i['constraints']['local_required']);self.assertTrue(i['constraints']['apple_silicon'])
        self.assertEqual(i['alternatives'],[['image_generation','video_generation']])
    def test_presentation_instruction_does_not_add_research(self):
        self.assertEqual([c['id'] for c in interpret('Find image generation with evidence')['capabilities']],['image_generation'])
        self.assertFalse(requested_facets('machine learning with evidence'))
    def test_paid_api_identification_is_not_prohibition(self):self.assertFalse(interpret(VIDEO_QUERY)['constraints']['no_paid_apis'])
    def test_explicit_paid_api_exclusion(self):self.assertTrue(interpret('Find narration without paid APIs')['constraints']['no_paid_apis'])
    def test_negated_action_not_requested(self):self.assertEqual([c['id'] for c in interpret('Do not generate video. Find transcription only')['capabilities']],['transcription'])
    def test_not_offline_is_not_offline(self):self.assertFalse(interpret('Find narration, not offline')['constraints']['offline_required'])
    def test_broader_requests(self):
        examples={'Find competitor pricing and audience feedback':{'competitors','audience'},'Find document chunking and typed JSON':{'document_chunks','structured_output'},'Find SQL queries and vector retrieval':{'sql','vector_retrieval'},'Find web search and read web pages':{'web_search','page_fetch'}}
        for question,expected in examples.items():self.assertEqual({c['id'] for c in interpret(question)['capabilities']},expected)
    def test_unknown_stays_unmapped(self):self.assertEqual(interpret('Find quantum bathymetric teleportation')['capabilities'][0]['id'],'unmapped')
    def test_unknown_part_of_compound_request_is_retained(self):self.assertEqual({c['id'] for c in interpret('Find script input and quantum teleportation')['capabilities']},{'script_input','unmapped'})

class QualificationTests(unittest.TestCase):
    def doc(self,types,description=''):
        return {'kind':'connected_group','component_types':types,'description':'Parent says generate videos on Mac','purpose_text':'','nodes':[{'description':description,'node_id':'a'}],'sources':{'file':'missing-fixture','graph_pointer':'$'}}
    def test_parent_cannot_create_generation_capability(self):
        cap=interpret('Find video generation')['capabilities'][0]
        self.assertIsNone(qualification(self.doc(['Agent','Prompt']),cap,interpret(VIDEO_QUERY)['constraints']))
    def test_cloud_is_conflict_not_paid_proof(self):
        cap=interpret('Find video generation')['capabilities'][0];q=qualification(self.doc(['GoogleVeo2VideoGenerator']),cap,interpret(VIDEO_QUERY)['constraints'])
        self.assertEqual(q['status'],'partial');self.assertEqual(q['constraint_checks']['local_execution']['status'],'conflict');self.assertEqual(q['constraint_checks']['mac_hardware']['status'],'unknown')
    def test_ollama_is_not_apple_silicon_runtime_proof(self):
        cap=interpret('Find script input')['capabilities'][0];q=qualification(self.doc(['TextInput','OllamaModel']),cap,interpret(VIDEO_QUERY)['constraints'])
        self.assertEqual(q['constraint_checks']['local_execution']['status'],'unknown');self.assertEqual(q['constraint_checks']['mac_hardware']['status'],'unknown')
    def test_explicit_provider_in_selected_description_flagged(self):
        cap=interpret('Find image generation')['capabilities'][0];doc=self.doc(['APIRequest'],'Image generation using fal.ai')
        q=qualification(doc,cap,interpret(VIDEO_QUERY)['constraints']);self.assertTrue(q['constraint_conflict'])

class EndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.engine=CorpusSearch();cls.answer=cls.engine.answer(VIDEO_QUERY,k=3)
    def test_six_sections(self):self.assertEqual(set(self.answer['sections']),VIDEO_CAPS)
    def test_hardware_never_silently_passes(self):
        for section in self.answer['sections'].values():
            self.assertNotEqual(section['status'],'supported')
            for hit in section['results']:self.assertEqual(hit['assessment']['constraint_checks']['mac_hardware']['status'],'unknown')
    def test_no_research_noise(self):
        for section in self.answer['sections'].values():
            for hit in section['results']:self.assertNotIn('Sequential Tasks Agents',hit['title'])
    def test_subtitles_cloud_binding(self):
        section=self.answer['sections']['subtitles'];self.assertTrue(section['results']);self.assertTrue(any(h['assessment']['constraint_conflict'] for h in section['results']))
    def test_source_checked_cards(self):
        for section in self.answer['sections'].values():
            for hit in section['results']:self.assertTrue(self.engine.verify_source(hit['id']))
    def test_primitive_text_input_not_lost_behind_workflows(self):
        self.assertTrue(any(r['kind']=='component' and 'TextInput' in r['component_types'] for r in self.answer['sections']['script_input']['results']))
    def test_unknown_not_impossibility(self):
        s=self.engine.answer('Find zzzquantum987 zzzbathymetry654')['sections']['unmapped'];self.assertEqual(s['status'],'unknown')
    def test_empty_question_rejected(self):
        with self.assertRaises(ValueError):self.engine.answer('')

if __name__=='__main__':unittest.main(verbosity=2)
