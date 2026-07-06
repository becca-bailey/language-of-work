# Well-Being Locus Validation (Phase 1.3)

2026-07-06 — hand vs frozen-codebook model, 91 items. GATES PASS (alpha 0.903 after learning/amenity exclusions).

```
==================================================================
LOCUS — hand vs frozen-codebook model
  raw agreement: 86/91 = 94.5%
  Krippendorff alpha (nominal): 0.903   [gate >= 0.80]  PASS
  hard-case subset (69 items): agreement 92.8%, alpha 0.870   [gate >= 0.667]  PASS

  confusion (hand → model):
    individual  -> individual:52, ambiguous:2
    structural  -> structural:24, ambiguous:1
    ambiguous   -> ambiguous:3, individual:2
    exclude     -> exclude:7

  per-category agreement:
    parental_leave         5/6 = 83%
    pto_accrued            5/6 = 83%
    other                  8/9 = 89%
    remote_flexibility     28/30 = 93%
    pto_unlimited          17/17 = 100%
    caregiver_support      8/8 = 100%
    wellness_perk          10/10 = 100%
    mental_health_eap      2/2 = 100%
    pto_minimum_enforced   2/2 = 100%
    sabbatical             1/1 = 100%

  DISAGREEMENTS (adjudicate):
    #56 hubspot    remote_flexibility hand=individual model=ambiguous  | work remotely when necessary
    #58 hubspot    remote_flexibility hand=individual model=ambiguous  | The ability to work from home
    #73 salesforce other              hand=ambiguous  model=individual | Foundation Paid time-off for community servi
    #74 salesforce parental_leave     hand=structural model=ambiguous  | Paid Maternity/Paternity Programs
    #79 salesforce pto_accrued        hand=ambiguous  model=individual | 6 paid days a year to volunteer

==================================================================
SPECIFICITY — secondary check
  raw agreement: 87/89 = 97.8%
```
