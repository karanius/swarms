"""Isolated state tests; stubbed inference is not reported as native model proof."""
from pathlib import Path
import copy,importlib.util,json,tempfile,unittest
S=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('test_comparison',S/'comparison_controls.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA=json.loads((S/'take-library.json').read_text())
def walk(w):
 yield w
 for c in getattr(w,'children',[]):yield from walk(c)
def card(panel,root):return next(w for w in walk(panel.grid) if 'p16-take-'+root in getattr(w,'_dom_classes',()))
class TakeControlsTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.oldS,self.oldL=m.S,m.LIBRARY
  m.S=Path(self.temp.name);m.LIBRARY=m.S/'library.json';m.LIBRARY.write_text(json.dumps(copy.deepcopy(DATA)))
  self.original_generate=m.backends.generate
 def tearDown(self):
  m.S,m.LIBRARY=self.oldS,self.oldL;m.backends.generate=self.original_generate;self.temp.cleanup()
 def test_draft_survives_column_changes_without_changing_applied_take(self):
  p=m.ComparisonControls();p.history.value=True;root='initial-index-1';before=copy.deepcopy(m.library())
  take=card(p,root);slider=next(w for w in walk(take) if isinstance(w,m.w.FloatSlider))
  slider.value=.6
  p.render()
  replacement=card(p,root)
  self.assertEqual(next(w for w in walk(replacement) if isinstance(w,m.w.FloatSlider)).value,.6)
  self.assertEqual(m.library(),before)
  self.assertTrue(any('Edits pending' in w.value for w in walk(replacement) if isinstance(w,m.w.HTML)))
 def test_failure_preserves_library_draft_and_reenables_controls(self):
  p=m.ComparisonControls();before=copy.deepcopy(m.library());p.new_text.value='Keep this draft.'
  def failed(*a,**k):raise RuntimeError('controlled unit failure')
  m.backends.generate=failed
  p.execute('vox','Keep this draft.','0012','neutral',m.backends.default_settings('vox'))
  self.assertEqual(m.library(),before);self.assertEqual(p.new_text.value,'Keep this draft.')
  self.assertFalse(p.busy);self.assertFalse(p.add.disabled);self.assertIn('Previous audio and edits are preserved',p.status.value)
 def test_success_appends_version_without_replacing_original(self):
  p=m.ComparisonControls();before=copy.deepcopy(m.library())
  original=next(r for r in before['records'] if r['id']=='initial-index-1')
  fake={**original,'id':'unit-fixture-new','parent_id':original['id'],'settings':{'strength':.7,'seed':7},'applied_settings':{'strength':.7,'seed':7}}
  m.backends.generate=lambda *a,**k:fake
  p.execute('index',original['text'],'0012','anger',fake['settings'],root_id=original['id'],parent_id=original['id'])
  after=m.library();self.assertEqual(after['records'][:-1],before['records'])
  self.assertEqual(after['records'][-1]['root_id'],original['id'])
  self.assertEqual(next(r for r in p.heads() if r['root_id']==original['id'])['id'],'unit-fixture-new')
 def test_missing_one_recording_does_not_block_other_players(self):
  data=copy.deepcopy(DATA);active=next(r for r in reversed(data['records']) if r['model']=='index');active['listening_path']=str(m.S/'missing.wav');m.LIBRARY.write_text(json.dumps(data))
  p=m.ComparisonControls();p.history.value=True
  self.assertTrue(any('Saved audio is unavailable' in w.value for w in walk(p.grid) if isinstance(w,m.w.HTML)))
  self.assertTrue(any('waveform and analysis' in w.value for w in walk(p.grid) if isinstance(w,m.w.HTML)))
 def test_all_queue_is_ordered_and_continues_after_failure(self):
  p=m.ComparisonControls();self.assertEqual(p.new_model.value,'all');calls=[]
  original=copy.deepcopy(DATA['records'][0])
  def generate(model,text,speaker,emotion,settings,**kwargs):
   calls.append(model)
   if model=='vox':raise RuntimeError('controlled queue failure')
   return {**original,'id':'queue-'+model,'model':model,'text':text,'speaker':speaker,'emotion':emotion,'settings':settings,'applied_settings':settings}
  m.backends.generate=generate
  before=len(m.library()['records']);p.create(None)
  self.assertEqual(calls,['index','vox','f5','dia'])
  self.assertEqual(len(m.library()['records']),before+3)
  self.assertIn('VoxCPM2</th>',p.queue_status.value);self.assertIn('failed. Generation',p.queue_status.value)
  self.assertIn('Queue finished',p.queue_status.value)
  self.assertFalse(p.queue_running);self.assertFalse(p.add.disabled)
 def test_inline_controls_persist_and_drive_individual_generation(self):
  p=m.ComparisonControls();p.model_fields['index']['strength'].value=.3
  p.preview_references()
  self.assertEqual(p.model_fields['index']['strength'].value,.3)
  calls=[]
  def fail(model,text,speaker,emotion,settings,**kwargs):
   calls.append((model,settings));raise RuntimeError('controlled stop')
  m.backends.generate=fail
  buttons=[x for x in walk(p.preview) if isinstance(x,m.w.Button)]
  buttons[0].click()
  self.assertEqual(calls[0][0],'index');self.assertEqual(calls[0][1]['strength'],.3)
  self.assertEqual(len(calls),1)
  self.assertFalse(p.model_checks)
 def test_unsupported_native_control_is_rejected(self):
  with self.assertRaisesRegex(ValueError,'Unsupported native controls'):
   m.backends.validate('dia','A test.','0012','neutral',{'strength':.5})
if __name__=='__main__':unittest.main()
