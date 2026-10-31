import unittest,copy
from layer_builder import build,describe
SPEC='''name: isolated research probe
nodes:
  start: ChatInput
  reason: Agent
  finish: ChatOutput
edges:
  start.message -> reason.input_value
  reason.response -> finish.input_value
config:
  reason.system_prompt: Draft only; preserve uncertainty.
'''
class BuilderAdapterTests(unittest.TestCase):
 def test_actual_native_graph_and_provenance(self):
  result=build(SPEC);self.assertNotIn('error',result)
  self.assertEqual(result['summary']['nodeCount'],3);self.assertEqual(result['summary']['edgeCount'],2)
  self.assertEqual({n['data']['type'] for n in result['nativeFlow']['data']['nodes']},{'ChatInput','Agent','ChatOutput'})
  self.assertIn('build_flow_from_spec',result['provenance']['engine'])
 def test_rejects_unapproved_type_code_keys_and_duplicate_aliases(self):
  for text in [SPEC.replace('Agent','FileSystem'),SPEC+'  reason.code: dangerous\n',SPEC+'  reason.api_key: dummy\n',SPEC.replace('finish: ChatOutput','start: ChatOutput')]:
   with self.subTest(text=text):
    with self.assertRaises(ValueError):build(text)
 def test_invalid_port_does_not_claim_success(self):
  self.assertIn('error',build(SPEC.replace('reason.response','reason.nonexistent')))
 def test_describe_no_source_or_values(self):
  data=describe('Agent');self.assertNotIn('code',data['template']);self.assertTrue(all('value' not in v for v in data['template'].values()))
if __name__=='__main__':unittest.main(verbosity=2)
