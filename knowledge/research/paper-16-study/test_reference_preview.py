"""Regression: a Listen click must request playback and replace stale status."""
from pathlib import Path
import importlib.util
from IPython.display import Audio
spec=importlib.util.spec_from_file_location('controls',Path(__file__).with_name('controls.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
panel=module.PerformanceControls();panel.status.value='<p>Audio generated.</p>'
shown=[];module.display=shown.append
panel._preview(None)
audio=next(item for item in shown if isinstance(item,Audio))
assert audio.autoplay is True, 'Listen created a paused player instead of requesting playback'
assert 'Audio generated' not in panel.status.value, 'Reference preview left a misleading generated-audio status'
assert 'reference' in panel.status.value.lower(), 'Reference preview needs a visible reference-specific status'
print('PASS: reference preview requests playback and shows reference-specific status')
