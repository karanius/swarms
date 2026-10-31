import unittest
from dataclasses import replace
from economics import evaluate,illustrative_scenarios
class EconomicsTests(unittest.TestCase):
 def test_before_eligibility_zero_ads_and_no_ad_break_even(self):
  r=evaluate(illustrative_scenarios()[0]);self.assertEqual(r['ad_receipts_month'],0);self.assertIsNone(r['economic_break_even_views_month']);self.assertLess(r['economic_profit_month'],0)
 def test_owner_time_can_reverse_positive_cash(self):
  r=evaluate(illustrative_scenarios()[1]);self.assertGreater(r['cash_surplus_month'],0);self.assertLess(r['economic_profit_month'],0)
 def test_break_even_identity(self):
  s=illustrative_scenarios()[1];r=evaluate(s);at=evaluate(replace(s,views_per_month=r['economic_break_even_views_month']));self.assertAlmostEqual(at['economic_profit_month'],0)
 def test_rejections_raise_unit_cost_without_creating_views(self):
  s=illustrative_scenarios()[1];a=evaluate(s);b=evaluate(replace(s,acceptance_fraction=.25));self.assertGreater(b['economic_cost_per_accepted_video'],a['economic_cost_per_accepted_video']);self.assertEqual(a['ad_receipts_month'],b['ad_receipts_month'])
 def test_all_failed_period_retains_cost_and_undefined_unit_cost(self):
  s=illustrative_scenarios()[1];a=evaluate(s);b=evaluate(replace(s,acceptance_fraction=0,views_per_month=0));self.assertEqual(b['economic_cost_month'],a['economic_cost_month']);self.assertEqual(b['accepted_videos_expected'],0);self.assertIsNone(b['economic_cost_per_accepted_video'])
 def test_invalid_inputs_rejected(self):
  s=illustrative_scenarios()[1]
  for kwargs in [{'acceptance_fraction':1.1},{'average_system_power_kw':-1},{'views_per_month':float('nan')}]:
   with self.assertRaises(ValueError):evaluate(replace(s,**kwargs))
if __name__=='__main__':unittest.main(verbosity=2)
