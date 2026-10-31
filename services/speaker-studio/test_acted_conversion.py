"""Reference selection must fail closed, with no alternate emotion or text fallback."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import acted_conversion as c

class GuideTests(unittest.TestCase):
 def test_joy_uses_happiness_while_anger_and_sadness_keep_their_labels(self):
  for target,expected in [('joy','happiness'),('anger','anger'),('sadness','sadness')]:
   with self.subTest(target=target),tempfile.TemporaryDirectory() as d:
    p=Path(d)/'reference.wav';p.write_bytes(b'isolated fixture')
    ref={'id':'fixture:'+expected,'emotion':expected,'path':str(p),'sha256':c.scene.digest(p)}
    with patch.object(c.bridge,'default_reference',return_value=ref['id']) as select,patch.object(c.bridge,'catalog',return_value={ref['id']:ref}):
     self.assertEqual(c.guide_for(target)['id'],ref['id']);select.assert_called_once_with(expected)
 def test_unsupported_reference_never_substitutes_another_emotion(self):
  with self.assertRaisesRegex(ValueError,'No qualified'):c.guide_for('reassurance')
 def test_selected_wrong_emotion_is_rejected(self):
  with patch.object(c.bridge,'catalog',return_value={'sad':{'emotion':'sadness'}}),self.assertRaisesRegex(ValueError,'does not match'):
   c.guide_for('anger','sad')
 def test_tampered_reference_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'reference.wav';p.write_bytes(b'changed')
   ref={'id':'fixture','emotion':'anger','path':str(p),'sha256':'wrong'}
   with patch.object(c.bridge,'default_reference',return_value='fixture'),patch.object(c.bridge,'catalog',return_value={'fixture':ref}),self.assertRaisesRegex(ValueError,'changed'):
    c.guide_for('anger')
if __name__=='__main__':unittest.main()
