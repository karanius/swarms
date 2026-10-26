import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location('lite_search', Path(__file__).with_name('lite_web_search.py'))
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class SearchTests(unittest.TestCase):
    def component(self):
        return module.LiteWebSearchComponent(query='hybrid work productivity', timeout=10, max_results=2)

    def response(self, html, status=200):
        response = Mock(status_code=status, text=html)
        if status >= 400:
            response.raise_for_status.side_effect = module.requests.HTTPError(str(status))
        return response

    @patch.object(module.requests, 'get')
    def test_real_lite_structure_and_single_url_decode(self, get):
        get.return_value = self.response('<table><tr><td><a class="result-link" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpaper%3Fq%3Da%2520b">Study</a></td></tr><tr><td class="result-snippet">Measured outcomes</td></tr></table>')
        rows = self.component().perform_web_search().to_dict(orient='records')
        self.assertEqual(rows[0]['link'], 'https://example.com/paper?q=a%20b')
        self.assertEqual(rows[0]['snippet'], 'Measured outcomes')
        self.assertEqual(rows[0]['source_type'], 'search_snippet')
        self.assertEqual(get.call_args.kwargs['params'], {'q': 'hybrid work productivity'})

    @patch.object(module.requests, 'get')
    def test_tool_message_keeps_urls_and_snippets(self, get):
        get.return_value = self.response('<table><tr><td><a class="result-link" href="https://example.com/study">Study</a></td></tr><tr><td class="result-snippet">Measured outcomes</td></tr></table>')
        import json
        payload = json.loads(self.component().perform_search().get_text())
        self.assertEqual(payload['results'][0]['link'], 'https://example.com/study')
        self.assertEqual(payload['results'][0]['snippet'], 'Measured outcomes')
        self.assertEqual(payload['evidence_scope'], 'search_snippets_only')

    @patch.object(module.requests, 'get')
    def test_403_is_failure_not_evidence(self, get):
        get.return_value = self.response('Forbidden', 403)
        with self.assertRaises(module.requests.HTTPError):
            self.component().perform_web_search()

    @patch.object(module.requests, 'get')
    def test_challenge_and_empty_page_are_failures(self, get):
        for body in ['<form id="challenge-form"></form>', '<html>No results</html>']:
            get.return_value = self.response(body)
            with self.assertRaises(ValueError):
                self.component().perform_web_search()


if __name__ == '__main__':
    unittest.main()
