# 10 — Risk, Assumption, and Dependency (RAID) Log

## Risks
- **R-01 (Confounding Misinterpretation):** Stakeholders might interpret unadjusted Kaplan-Meier curves as proof that SLA breaches directly cause client exits. *Mitigation:* Mandatory Cox PH adjusted comparison and "What this analysis can — and cannot — establish" panel.
- **R-02 (Pilot Contamination):** Advisors in control regions may adopt informal pre-submission checks during the KYC pilot. *Mitigation:* Cluster randomization at regional/team level.

## Assumptions
- **A-01 (Business Calendar):** SLA deadlines assume `Mon–Fri 09:00–17:00 America/New_York` (8 business hours/day).
- **A-02 (Capacity Baseline):** Active advisor capacity is modeled at 35 concurrent open cases per active advisor.
- **A-03 (Inactivity Threshold):** 90 days without a qualifying engagement flags a client as `Inactive`, distinct from formal account exit.

## Dependencies
- **D-01:** Compliance Representative sign-off on KYC v2.4 pre-submission validation rules (`REC-001`).
- **D-02:** CRM webhook for <90d SLA breach alerts (`REC-002`).
