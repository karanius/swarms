import json, unittest
from search_engine import CorpusSearch, node_record, edge_record, resolve_pointer, clean, CORPUS

class ExtractionTests(unittest.TestCase):
    def test_saved_credentials_and_code_are_not_indexed(self):
        node={'id':'x','data':{'type':'APIRequest','node':{'template':{'api_key':{'value':'SENTINEL_PRIVATE_KEY','password':True,'required':True},'code':{'value':'ARBITRARY_EXECUTABLE_SENTINEL'},'input_value':{'value':'SAVED_PRIVATE_INPUT'}},'outputs':[{'name':'response','types':['Data']} ]}}}
        record=node_record(node);encoded=json.dumps(record)
        for text in ['SENTINEL_PRIVATE_KEY','ARBITRARY_EXECUTABLE_SENTINEL','SAVED_PRIVATE_INPUT']:self.assertNotIn(text,encoded)
        self.assertTrue(record['requirements'][0]['kind']=='credential')
    def test_source_ports_preserved(self):
        r=edge_record({'source':'a','target':'b','data':{'sourceHandle':{'name':'message','output_types':['Message']},'targetHandle':{'fieldName':'input_value','inputTypes':['Message']}}})
        self.assertTrue(r['port_details_resolved']);self.assertEqual(r['source_port'],'message');self.assertEqual(r['target_port'],'input_value')
    def test_unknown_ports_stay_unknown(self):self.assertFalse(edge_record({'source':'a','target':'b'})['port_details_resolved'])
    def test_pointer_and_redaction(self):
        self.assertEqual(resolve_pointer({'data':[{'nodes':[]}]},'$/data/0'),{'nodes':[]})
        self.assertNotIn('sk-'+'A'*30,clean('credential sk-'+'A'*30))

class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.engine=CorpusSearch()
    def test_complete_index(self):
        self.assertEqual(self.engine.stats['unique_eligible_contents'],1148)
        self.assertFalse(self.engine.stats['failures'])
        for kind in ['template','component','connected_group']:self.assertGreater(self.engine.stats['kinds'][kind],0)
    def test_unknown_capability_does_not_get_invented(self):
        self.assertFalse(self.engine.search('zxqvplmn9876 zzzquux5432')['results'])
    def test_bad_inputs_and_kind(self):
        for value in ['',None,'a'*1300]:
            with self.assertRaises(ValueError):self.engine.search(value)
        with self.assertRaises(ValueError):self.engine.search('market research',kind='validated_composite')
    def test_query_cannot_modify_sql(self):
        self.engine.search("market OR 1=1; DROP TABLE docs --",semantic=False)
        self.assertEqual(len(self.engine.docs),self.engine.db.execute('SELECT count(*) FROM docs').fetchone()[0])
    def test_kind_filters(self):
        for kind in ['template','component','connected_group']:
            hits=self.engine.search('YouTube comments audience feedback',kind=kind)['results'];self.assertTrue(hits);self.assertTrue(all(h['kind']==kind for h in hits))
    def test_matched_source_is_hash_verified(self):
        hits=self.engine.search('company pricing market research',k=5)['results']
        self.assertTrue(hits)
        self.assertTrue(all(self.engine.verify_source(h['id']) for h in hits))
    def test_results_explain_limits_and_money_gap(self):
        answer=self.engine.search('Find monetization pieces using my actual private channel earnings')
        self.assertTrue(any('not proof of creator revenue' in g for g in answer['gaps']))
        self.assertTrue(any('no access to your accounts' in g for g in answer['gaps']))
        for hit in answer['results']:self.assertIn('require validation',hit['fit'])
    def test_multi_capability_question_is_separated(self):
        answer=self.engine.answer('Find audience feedback, competitor pricing and monetization pieces')
        self.assertTrue({'audience','competitors','monetization'}<=set(answer['sections']))
    def test_connected_group_is_from_actual_edges(self):
        hit=self.engine.search('YouTube comments',kind='connected_group',k=1)['results'][0]
        source=hit['sources'];obj=json.loads((CORPUS/source['file']).read_text());graph=resolve_pointer(obj,source['graph_pointer'])
        original=[edge_record(e) for e in graph['edges']];selected={n['node_id'] for n in hit['nodes']}
        self.assertTrue(hit['edges']);self.assertTrue(all(e in original for e in hit['edges']))
        self.assertTrue(all(e['source'] in selected and e['target'] in selected for e in hit['edges']))
        for e in hit['boundary']['inputs']:self.assertTrue(e['source'] not in selected and e['target'] in selected and e in original)
        for e in hit['boundary']['outputs']:self.assertTrue(e['source'] in selected and e['target'] not in selected and e in original)
    def test_inspection_returns_a_copy(self):
        ident=self.engine.docs[0]['id'];copy=self.engine.inspect(ident);copy['title']='MODIFIED';self.assertNotEqual(self.engine.inspect(ident)['title'],'MODIFIED')
    def test_missing_embedding_binding_reports_lexical_fallback(self):
        original=self.engine.embedding_current
        try:
            self.engine.embedding_current=False
            answer=self.engine.search('company pricing market research')
            self.assertTrue(answer['results']);self.assertIn('fallback',answer['semantic_status'])
        finally:self.engine.embedding_current=original
    def test_changed_source_results_are_withheld(self):
        original=self.engine.verify_source
        try:
            self.engine.verify_source=lambda _:False
            answer=self.engine.search('company pricing market research',semantic=False)
            self.assertFalse(answer['results']);self.assertTrue(any('withheld' in g for g in answer['gaps']))
        finally:self.engine.verify_source=original
    def test_changed_corpus_snapshot_is_reported(self):
        original=self.engine.corpus_current
        try:
            self.engine.corpus_current=False
            answer=self.engine.search('company pricing market research',semantic=False)
            self.assertTrue(any('snapshot' in g for g in answer['gaps']))
        finally:self.engine.corpus_current=original
    def test_parent_description_does_not_invent_comment_collector(self):
        answer=self.engine.search('Which pieces collect viewer comments to understand audience feedback?',k=10)
        self.assertTrue(answer['results'])
        for result in answer['results']:
            types=' '.join(result['component_types']).lower()
            self.assertTrue('comment' in types or 'youtubeapi' in types)

if __name__=='__main__':unittest.main(verbosity=2)
