"""Scenario mathematics, not observed revenue/CPM/RPM or production forecasts."""
from dataclasses import dataclass,asdict
import math
@dataclass(frozen=True)
class Scenario:
    name:str
    eligible:bool
    views_per_month:float
    ad_receipts_per_1000_total_views_assumption:float
    attempted_videos_per_month:float
    acceptance_fraction:float
    generation_hours_per_attempt:float
    average_system_power_kw:float
    energy_price_per_kwh:float
    review_minutes_per_attempt:float
    other_operator_hours_month:float
    owner_hour_value:float
    fixed_cash_cost_month:float
    economic_hardware_charge_month:float

def evaluate(s):
    values=asdict(s)
    for k,v in values.items():
        if isinstance(v,(int,float)) and (not math.isfinite(v) or v<0):raise ValueError('Nonnegative finite scenario values required: '+k)
    if not 0<=s.acceptance_fraction<=1:raise ValueError('Acceptance fraction must be in [0,1]')
    accepted=s.attempted_videos_per_month*s.acceptance_fraction
    compute_hours=s.attempted_videos_per_month*s.generation_hours_per_attempt
    energy=compute_hours*s.average_system_power_kw*s.energy_price_per_kwh
    operator=s.attempted_videos_per_month*s.review_minutes_per_attempt/60+s.other_operator_hours_month
    cash_cost=s.fixed_cash_cost_month+energy
    economic_cost=cash_cost+operator*s.owner_hour_value+s.economic_hardware_charge_month
    effective_rate=s.ad_receipts_per_1000_total_views_assumption if s.eligible else 0
    receipts=s.views_per_month/1000*effective_rate
    threshold=lambda cost:cost*1000/effective_rate if effective_rate>0 else None
    return {**values,'accepted_videos_expected':accepted,'generation_hours_month':compute_hours,'operator_hours_month':operator,'energy_cost_month':energy,'cash_cost_month':cash_cost,'economic_cost_month':economic_cost,'ad_receipts_month':receipts,'cash_surplus_month':receipts-cash_cost,'economic_profit_month':receipts-economic_cost,'cash_break_even_views_month':threshold(cash_cost),'economic_break_even_views_month':threshold(economic_cost),'cash_cost_per_accepted_video':cash_cost/accepted if accepted else None,'economic_cost_per_accepted_video':economic_cost/accepted if accepted else None,'interpretation':'Authored scenario; no observed audience, ad yield, accepted videos or production throughput implied'}

def illustrative_scenarios():
    base=dict(views_per_month=100000,ad_receipts_per_1000_total_views_assumption=2,attempted_videos_per_month=12,acceptance_fraction=.75,generation_hours_per_attempt=2,average_system_power_kw=.12,energy_price_per_kwh=.25,review_minutes_per_attempt=25,other_operator_hours_month=4,owner_hour_value=20,fixed_cash_cost_month=15,economic_hardware_charge_month=25)
    # Deliberately hypothetical USD inputs. These are not market rates or a forecast.
    return [Scenario('Pre-eligibility: zero ad receipts',False,**base),Scenario('Eligible illustrative arithmetic only',True,**base),Scenario('Lower hypothetical yield',True,**{**base,'ad_receipts_per_1000_total_views_assumption':.5}),Scenario('More review/rejection work',True,**{**base,'acceptance_fraction':.5,'review_minutes_per_attempt':60}),Scenario('Higher hypothetical yield',True,**{**base,'ad_receipts_per_1000_total_views_assumption':5})]

if __name__=='__main__':
 import json
 print(json.dumps([evaluate(s) for s in illustrative_scenarios()],indent=2))
