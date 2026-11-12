# 05 — Authoritative KPI Dictionary

All KPIs in CONTINUUM are calculated in PostgreSQL and exposed via `/api/v1/metrics/dictionary` and the **View Calculation (SQL)** drawer.

| KPI Key | KPI Name | Formula | Exclusions & Caveats |
| --- | --- | --- | --- |
| `active_clients` | Active Clients | `COUNT(*) WHERE activated_at <= end_dt AND (exited_at IS NULL OR exited_at > end_dt)` | Excludes prospects, in-progress onboarding, and onboarding abandonments. |
| `client_retention_rate` | Client Retention Rate | `1 - (Exited in window / Active at window start)` | Mixes cohort tenures; pair with Retention Studio cohort heatmap. |
| `client_attrition_rate` | Client Attrition Rate | `Exited in window / Active at window start` | Formal exits only; inactivity is tracked separately. |
| `inactivity_rate` | Client Inactivity Rate | `Active (>90d tenure) with >90d since last qualifying contact / Active (>90d tenure)` | Inactivity is not automatic churn. |
| `funnel_conversion` | Funnel Conversion | `Completed / (Completed + Cancelled)` | In-progress episodes are separated from failures. |
| `stage_completion_time` | Median Stage Duration | `PERCENTILE_CONT(0.5)` of `(exited_at - entered_at)` in days | Completed episodes only. |
| `p90_stage_duration` | p90 Stage Duration | `PERCENTILE_CONT(0.9)` of `(exited_at - entered_at)` in days | Captures tail delays. |
| `stage_stall_rate` | Stage Stall Rate | `In Progress >14d / Total In Progress` | As of reporting end date. |
| `kyc_rework_rate` | KYC Rework Rate | `Reopened KYC episodes / Initial KYC episodes` | Initial episodes (`previous_episode_id IS NULL`) form denominator. |
| `first_response_sla_attainment` | First-Response SLA | `Responded on time / Due cases (due <= as_of)` | Mon–Fri 09:00–17:00 `America/New_York`; open cases not yet due excluded. |
| `resolution_sla_attainment` | Resolution SLA | `Resolved on time / Due cases (due <= as_of)` | Mon–Fri 09:00–17:00 `America/New_York`. |
| `reopen_rate` | Case Reopen Rate | `Cases with reopen_count > 0 / Resolved or Closed cases` | Excludes still-open cases. |
| `repeat_contact_rate` | Repeat-Contact Rate | `Cases with repeat_contact_count > 0 / Total cases` | Intra-case repeat inquiries. |
| `backlog_aging` | Open Backlog Aging | `Open/In Progress cases grouped by 0-2d, 3-7d, 8-14d, 15+d` | Calendar-day aging as of end date. |
| `advisor_utilization` | Advisor Utilization | `Open cases / (Active advisors * 35)` | Departed/inactive advisors excluded from capacity denominator. |
