import hashlib,json,unittest
from pathlib import Path
import nbformat
from migrate_papers import ROOT,TITLES,text
class MigrationContent(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.original=json.loads((ROOT/'knowledge/research/notebook-migration/original-papers.json').read_text())['papers']
 def test_all_three_papers_valid_and_all_prose_preserved(self):
  for p in self.original:
   n=nbformat.read(ROOT/'knowledge/research/notebooks'/(TITLES[p['id']]+'.ipynb'),as_version=4);nbformat.validate(n)
   markdown='\n\n'.join(c.source for c in n.cells if c.cell_type=='markdown')
   for b in p['content']:
    if b['type'] in ['paragraph','heading'] and text(b.get('content')):self.assertIn(text(b.get('content')),markdown,p['title'])
    if b['type']=='table':
     for row in b['content']['rows']:
      for cell in row['cells']:
       value=text(cell.get('content',[]) if isinstance(cell,dict) else cell).replace('|','\\|').replace('\n','<br>');self.assertIn(value,markdown)
 def test_paper_two_figures_are_portable_attachments(self):
  n=nbformat.read(ROOT/'knowledge/research/notebooks/Paper 2 - Boundary Resolution.ipynb',as_version=4)
  attachments=[a for c in n.cells for a in c.get('attachments',{})];self.assertEqual(len(attachments),4)
  for c in n.cells:
   for bundle in c.get('attachments',{}).values():self.assertTrue(bundle['image/png'].startswith('iVBOR'))
  self.assertFalse(any('http://127.0.0.1' in c.source for c in n.cells))
 def test_paper_three_embedded_code_imported(self):
  p=next(p for p in self.original if p['id'].startswith('8b72'))
  n=nbformat.read(ROOT/'knowledge/research/notebooks'/(TITLES[p['id']]+'.ipynb'),as_version=4)
  code=[c for c in n.cells if c.cell_type=='code'];self.assertGreaterEqual(len(code),1)
  self.assertTrue(any('functionality demonstration' in c.source for c in n.cells))
 def test_original_source_collection_unchanged(self):
  self.assertEqual((ROOT/'knowledge/research/papers.json').read_bytes(),(ROOT/'knowledge/research/notebook-migration/original-papers.json').read_bytes())
if __name__=='__main__':unittest.main()
