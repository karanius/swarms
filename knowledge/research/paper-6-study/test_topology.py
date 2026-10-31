import unittest
from build_topology import extract,handle,digest
class Extraction(unittest.TestCase):
 def graph(self):return {'nodes':[{'id':'a','data':{'type':'Agent','node':{'outputs':[{'name':'response','types':['Message']}],'template':{'key':{'password':True,'required':True,'value':'DO_NOT_EXPORT'},'code':{'value':'DO_NOT_EXECUTE'}},'lf_version':'1'}}},{'id':'b','data':{'type':'ChatOutput','node':{}}}], 'edges':[{'source':'a','target':'b','sourceHandle':'{œnameœ:œresponseœ}','data':{'targetHandle':{'fieldName':'input_value','inputTypes':['Message']}}}]}
 def test_scope_identity(self):
  a=extract(self.graph(),'one');b=extract(self.graph(),'two');self.assertNotEqual(a['id'],b['id']);self.assertEqual(a['nodes'][0]['id'],'a')
 def test_ports(self):
  e=extract(self.graph(),'g')['edges'][0];self.assertEqual(e['sourcePort'],'response');self.assertEqual(e['targetPort'],'input_value');self.assertTrue(e['resolved'])
 def test_no_values_or_code(self):
  import json
  value=json.dumps(extract(self.graph(),'g'));self.assertNotIn('DO_NOT_EXPORT',value);self.assertNotIn('DO_NOT_EXECUTE',value)
 def test_unresolved_retained(self):
  g=self.graph();g['edges'][0]['target']='missing';x=extract(g,'g');self.assertEqual(len(x['edges']),1);self.assertFalse(x['edges'][0]['resolved']);self.assertIn('edge-with-unresolved-or-note-endpoint',x['warnings'])
 def test_parallel_edges_retained(self):
  g=self.graph();g['edges'].append(dict(g['edges'][0]));self.assertEqual(len(extract(g,'g')['edges']),2)
 def test_unknown_handle(self):self.assertTrue(handle({'sourceHandle':'broken'},'source')['unparsed'])
 def test_unknown_type(self):
  g=self.graph();del g['nodes'][0]['data']['type'];self.assertEqual(extract(g,'g')['nodes'][0]['type'],'Unknown')
 def test_graph_key(self):self.assertNotEqual(digest(['a','$/one']),digest(['a','$/two']))
if __name__=='__main__':unittest.main()
