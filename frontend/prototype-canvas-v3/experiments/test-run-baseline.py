import importlib.util
import pathlib
import unittest
spec = importlib.util.spec_from_file_location('runner', pathlib.Path(__file__).with_name('run-baseline.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
class EvaluatorChecks(unittest.TestCase):
    def test_format_rejects_heading_empty_or_extra_bullets(self):
        for text in ['Heading\n- a\n- b\n- c', '- a\n- \n- c', '- a\n- b', '- a\n- b\n- c\n- d']:
            self.assertFalse(runner.format_check(text))
        self.assertTrue(runner.format_check('- a\n- b\n- c'))
    def test_invalid_preconditions_are_local(self):
        self.assertEqual(runner.guard('  ', {'provider': 'x', 'name': 'y'}), 'empty source')
        self.assertEqual(runner.guard('source', None), 'missing model binding')
    def test_extract_uses_final_component(self):
        raw = {'outputs': [{'outputs': [{'component_id': 'agent', 'results': {'message': {'text': 'wrong'}}}, {'component_id': 'out', 'results': {'message': {'text': 'right'}}}]}]}
        self.assertEqual(runner.extract_text(raw, 'out'), 'right')
if __name__ == '__main__': unittest.main()
