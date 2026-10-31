import unittest
from dia_input import format_input
class DiaInputTests(unittest.TestCase):
 def test_single_speaker(self):self.assertEqual(format_input('Hello there.'),('[S1] Hello there. [S2]',None))
 def test_continuation_merges_same_speaker(self):self.assertEqual(format_input('[S1] Stay here.','A reference sentence.'),('Stay here. [S2]','[S1] A reference sentence.'))
 def test_dialogue_closes_with_opposite_tag(self):self.assertEqual(format_input('[S1] Hello. [S2] Hi.'),('[S1] Hello. [S2] Hi. [S1]',None))
 def test_repeated_turns_rejected(self):
  with self.assertRaises(ValueError):format_input('[S1] Hello. [S1] Again.')
 def test_closing_tag_not_duplicated(self):self.assertEqual(format_input('[S1] Hello. [S2]'),('[S1] Hello. [S2]',None))
if __name__=='__main__':unittest.main()
