# Well-Being Locus Validation (Phase 1.3)

2026-07-06 — hand vs frozen-codebook model, 91 items. GATES PASS.

```
==================================================================
LOCUS — hand vs frozen-codebook model
  raw agreement: 82/91 = 90.1%
  Krippendorff alpha (nominal): 0.818   [gate >= 0.80]  PASS
  hard-case subset (69 items): agreement 91.3%, alpha 0.837   [gate >= 0.667]  PASS

  confusion (hand → model):
    individual  -> individual:52, structural:2, exclude:1, ambiguous:1
    structural  -> structural:23, ambiguous:1, individual:1
    ambiguous   -> individual:3, ambiguous:2
    exclude     -> exclude:5

  per-category agreement:
    other                  7/9 = 78%
    wellness_perk          8/10 = 80%
    parental_leave         5/6 = 83%
    pto_accrued            5/6 = 83%
    caregiver_support      7/8 = 88%
    remote_flexibility     28/30 = 93%
    pto_unlimited          17/17 = 100%
    mental_health_eap      2/2 = 100%
    pto_minimum_enforced   2/2 = 100%
    sabbatical             1/1 = 100%

  DISAGREEMENTS (adjudicate):
    #33 gitlab     other              hand=individual model=exclude    | Learn in-demand skills with access to platfo
    #52 hubspot    remote_flexibility hand=ambiguous  model=individual | work remotely when necessary
    #58 hubspot    remote_flexibility hand=individual model=ambiguous  | The ability to work from home
    #73 salesforce other              hand=ambiguous  model=individual | Foundation Paid time-off for community servi
    #74 salesforce parental_leave     hand=structural model=ambiguous  | Paid Maternity/Paternity Programs
    #79 salesforce pto_accrued        hand=ambiguous  model=individual | 6 paid days a year to volunteer
    #82 salesforce wellness_perk      hand=individual model=structural | on-site free yoga
    #83 starbucks  caregiver_support  hand=structural model=individual | Referral and support resources for child and
    #85 starbucks  wellness_perk      hand=individual model=structural | all the handcrafted beverages you can drink

==================================================================
SPECIFICITY — secondary check
  raw agreement: 70/89 = 78.7%
```
