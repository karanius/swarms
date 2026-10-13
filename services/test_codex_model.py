import unittest
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
from services.codex_model import CodexModel
class CodexAdapterTests(unittest.TestCase):
    def test_auth_and_model_flags_and_exact_output(self):
        def fake(command,**options):
            self.assertIn('--ignore-user-config',command)
            self.assertIn('--ephemeral',command)
            self.assertEqual(command[command.index('--model')+1],'gpt-6-luna')
            self.assertIn('model_reasoning_effort="low"',command)
            self.assertEqual(command[command.index('--sandbox')+1],'read-only')
            self.assertIn('test prompt',options['input'])
            Path(command[command.index('--output-last-message')+1]).write_text('exact response')
            return SimpleNamespace(returncode=0)
        with patch('services.codex_model.subprocess.run',side_effect=fake):
            self.assertEqual(CodexModel().run('test prompt'),'exact response')
    def test_failure_does_not_expose_cli_stderr(self):
        with patch('services.codex_model.subprocess.run',return_value=SimpleNamespace(returncode=1,stderr='sensitive')):
            with self.assertRaises(RuntimeError) as error:CodexModel().run('test')
            self.assertNotIn('sensitive',str(error.exception))
if __name__=='__main__':unittest.main()
