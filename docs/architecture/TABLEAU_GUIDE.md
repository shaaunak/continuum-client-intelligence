# Tableau Integration Guide

CONTINUUM provides five Tableau-ready CSV extracts via `GET /api/v1/exports/{report_type}` and the top-bar **Export** menu:

1. `executive_monthly_metrics.csv` (`month`, `active_start`, `exited_month`)
2. `journey_stage_metrics.csv` (`stage`, `entered_month`, `total_episodes`, `completed_count`, `reopened_count`, `median_days`, `p90_days`)
3. `service_sla_metrics.csv` (`month`, `assigned_team_id`, `request_category`, `total_cases`, `first_response_breaches`, `resolution_breaches`)
4. `advisor_workload_metrics.csv` (`advisor_id`, `display_name`, `team_id`, `active`, `max_active_cases`, `open_cases`, `total_fr_breaches`)
5. `complaint_category_metrics.csv` (`month`, `category`, `severity`, `complaint_count`, `reopened_count`)

## Recommended Tableau Calculated Fields
- **Monthly Retention Rate:** `1 - (SUM([Exited Month]) / SUM([Active Start]))`
- **KYC Rework Rate:** `SUM([Reopened Count]) / SUM([Total Episodes])`
- **SLA Breach Rate:** `SUM([First Response Breaches]) / SUM([Total Cases])`
- **Advisor Utilization:** `SUM([Open Cases]) / SUM(IF [Active] THEN [Max Active Cases] ELSE 0 END)`

*Note: Tableau Desktop is not bundled in this repository; all extracts are validated directly against PostgreSQL.*
