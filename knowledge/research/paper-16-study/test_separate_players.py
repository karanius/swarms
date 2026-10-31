"""Previewing must never clear the last generated take or invoke generation."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('controls',Path(__file__).with_name('controls.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=m.PerformanceControls()
assert p.output is not p.reference_output
p.output.append_stdout('saved generated recording')
before=p.output.outputs
clears=[]
p.output.clear_output=lambda **kwargs: clears.append(kwargs)
m.display=lambda item: None
for emotion in ('neutral','anger','neutral'):
    p.emotion.value=emotion
    p._preview(None)
assert not clears, 'Reference preview cleared the generated recording'
assert p.output.outputs==before
print('PASS: repeated reference switching preserves generated player')
