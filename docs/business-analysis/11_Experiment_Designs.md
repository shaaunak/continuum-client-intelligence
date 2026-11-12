# 11 — Experiment Designs (Proposed)

All experiments are **Proposed**; no treatment effects are claimed prior to execution.

| Exp ID | Linked Rec | Design Type | Primary Metric | Guardrail Metrics | Window |
| --- | --- | --- | --- | --- | --- |
| `EXP-001` | `REC-001` | Controlled Team Pilot (DiD: East vs. West) | KYC Rework Rate | Median KYC Duration, Onboarding Abandonment | 56 days |
| `EXP-002` | `REC-002` | Randomized Stratified Holdout (50/50 by Tier) | 180d Post-Breach Retention & Engagement | Complaint Rate, Advisor Follow-Up Workload | 90 days |
| `EXP-003` | `REC-003` | Phased Operational Pilot (`T-03` overflow to `T-04`) | p90 First-Response Business Hours | Case Reopen Rate, Complexity Mix Balance | 42 days |
| `EXP-004` | `REC-004` | Stepped-Wedge Staged Rollout | Follow-Up On-Time Completion Rate | Repeat-Contact Rate, Alert Dismissals | 42 days |
