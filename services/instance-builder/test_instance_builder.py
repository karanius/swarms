import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from rich.console import Console
import instance_builder as app

class NavigationTests(unittest.TestCase):
    def play(self, root, inputs):
        with patch('builtins.input', side_effect=inputs), patch.object(app, 'console', Console(file=io.StringIO())):
            return app.run(root)

    def test_create_resume_and_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = self.play(root, ['1', 'Referral program', 'q'])
            resumed = self.play(root, ['2', '1', 'e', 'Profitable referral program', 'q'])
            self.assertEqual(first['id'], resumed['id'])
            self.assertEqual(app.load_instances(root)[0]['outcome'], 'Profitable referral program')
            self.assertEqual(len(list(root.glob('*.json'))), 1)

    def test_back_before_capture_leaves_no_empty_instance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.play(root, ['1', '/back', 'q'])
            self.assertEqual(app.load_instances(root), [])

    def test_back_from_picker_and_cancel_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.play(root, ['1', 'Original', 'q'])
            self.play(root, ['2', 'b', '2', '1', 'e', '/back', 'b', 'q'])
            self.assertEqual(app.load_instances(root)[0]['outcome'], 'Original')

    def test_interrupted_edit_preserves_saved_description(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.play(root, ['1', 'Original', 'q'])
            with self.assertRaises(EOFError):
                self.play(root, ['2', '1', 'e', EOFError()])
            self.assertEqual(app.load_instances(root)[0]['outcome'], 'Original')

if __name__ == '__main__':
    unittest.main()
