import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from services.image_discovery import scan_image_files, verify_image_inventory

class InventoryTests(unittest.TestCase):
    def test_overlapping_roots_and_symlink_cycle(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); child=root/'nested'; child.mkdir()
            (root/'photo.JPG').touch(); (child/'picture.png').touch(); (root/'note.txt').touch()
            (root/'loop').symlink_to(root,target_is_directory=True)
            result=scan_image_files([str(root),str(child)])
            self.assertEqual(result['imageFiles'],2)
            self.assertEqual(result['formats'],{'.png':1,'.jpg':1})
            self.assertEqual(result['symlinksSkipped'],1)
            self.assertTrue(verify_image_inventory(result)['consistent'])
            self.assertEqual((root/'photo.JPG').read_bytes(),b'')

    def test_read_errors_are_disclosed(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('services.image_discovery.os.scandir',side_effect=PermissionError('Denied')):
                result=scan_image_files([directory])
            self.assertEqual(result['imageFiles'],0)
            self.assertEqual(len(result['unreadable']),1)
            self.assertEqual(verify_image_inventory(result)['coverage'],'partial')

    def test_inconsistent_aggregation_is_rejected(self):
        self.assertFalse(verify_image_inventory({'imageFiles':2,'formats':{'.png':1},'folders':{'/x':2},'unreadable':[]})['consistent'])

if __name__=='__main__':unittest.main()
