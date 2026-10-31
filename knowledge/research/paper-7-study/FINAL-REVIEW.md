# Paper 7 independent final review

Reviewed 2026-10-30 by the business-research collaborator, independently of the coordinator's notebook synthesis. Read-only review of the notebook and economics implementation; this report is the only review edit. This is internal AI review, not external academic peer review.

## Verdict

**No blocking findings for delivery as a provisional research/business blueprint.** The notebook does not establish a working production business and correctly says so. It does not justify publication, production installation, spending, account creation, or a revenue claim.

Reviewed `knowledge/research/notebooks/Paper 7 - Local AI Social Media Business.ipynb`, `knowledge/research/paper-7-study/economics.py`, and its five focused tests. Saved notebook code outputs have execution counts and no stored error outputs. Independently ran `python3 -B -m unittest test_economics.py -v`: all five checks passed. This rerun verifies those arithmetic properties, not production, demand, licensing clearance, or user-visible rendering.

## Findings by requested concern

| Concern | Assessment | Evidence / limit |
|---|---|---|
| Unsupported success claims | No blocker | Abstract, Sections 4/10 and source dossiers explicitly distinguish authored design, arithmetic, unmeasured demand, and no commercial receipts. Conditional niche preference is not called a measured winner. |
| Economics denominator | No blocker | Section 7 and implementation use an explicitly assumed ad receipt per thousand total views, not advertiser CPM. The dossier warns that platform RPM includes other revenue and uses different Shorts/video denominators. Actual calibration must preserve that distinction. |
| Arithmetic | No blocker | Eligibility zeroes ad revenue; failed attempts retain costs; owner labor and hardware allowance enter economic cost; break-even identity is correct when eligible and the assumed rate is positive. Views are independent of output count. |
| Scope | No blocker | No production/publishing execution implied. Pseudo-instance is an authored document and native component array remains empty pending catalog verification. |
| Local readiness | No blocker | Hardware observation is separated from throughput; named candidates are unbenchmarked; FFmpeg absence on current PATH is disclosed; online research and distribution are separate from intended local production. |
| Owner constraints | No blocker | Jurisdiction/payment eligibility, language/audience, expertise, time/cash ceilings and written support tolerance remain open. Income target is explicitly unknown in the business dossier. No residency inferred from timezone. |
| Demand | No blocker | No search volumes, earning rates, conversion rates or niche demand invented. Private quality tests are not presented as audience/buyer evidence. |

## Nonblocking limitations to retain before operational use

1. **Zero accepted output is excluded by the current scenario schema.** `evaluate()` requires `acceptance_fraction > 0`. That is acceptable for the displayed unit-cost sensitivity, but an all-failed production period is a real future case. Before using this as a pilot accounting tool, permit zero acceptance, retain full costs, and report unit cost as undefined rather than exclude that period. No present scenario is incorrectly computed because of this restriction.
2. **Scenario input validation is not a production API contract.** Python type annotations do not enforce boolean eligibility or numeric field types at runtime. Current authored inputs are valid; do not expose the function to arbitrary external input without schema validation.
3. **The compact economics model is deliberately incomplete.** It models ad-rate arithmetic only; actual payment delay, cash reserves/runway, taxes, variable selling fees, affiliate attribution, refunds and product support need separate models when chosen. Fixed cash and operator hours must be populated from a complete ledger; an omitted cost is not zero. The notebook discloses these limits sufficiently for this deliverable.
4. **Finalize a single demand protocol before collection.** Notebook Section 4 proposes three audience/problem candidates, while the business dossier's example protocol proposes two. Both are proposals, not results; choose one budgeted protocol and record it before collecting data. Similarly fix the owner's income target and acceptable loss/time envelope before interpreting profitability gates.
5. **Source documentation is mutable.** This review checked consistency with the research dossiers, not every primary source again. The platform's future-terms announcement is correctly treated as a future checkpoint. Exact account eligibility, checkpoint licenses, asset rights and platform terms require refresh before operational decisions.

## Delivery boundary

The paper is suitable to explain **what should be investigated and how to decide**, with reproducible illustrative arithmetic. It is not evidence that the proposed models are installed, the content pipeline runs, viewers want the niche, the channel will monetize, or the business is profitable. Preserve this boundary in the user-facing handoff.

## Coordinator response
Addressed items 1 and 4: zero acceptance now retains costs with undefined unit cost; a sixth regression check covers this. The summary and dossier now both propose two demand candidates. Production input-schema enforcement and complete operating accounting remain explicitly deferred limitations.
