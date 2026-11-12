# 09 — User Acceptance Testing (UAT) Test Cases

| UAT ID | Scenario / Edge Case | Expected Behavior | Verification Status |
| --- | --- | --- | --- |
| `UAT-01` | Open cases not yet due for first response (`first_response_due_at > as_of_date`) | Excluded from SLA breach failures; `first_response_breached = FALSE`. | Verified (`test_chronology_and_timestamp_validity`) |
| `UAT-02` | Recently activated immature cohort (`2026-10`) | Future cohort months are blank/null (`observed_months = 0`), never `0%`. | Verified (`test_retention_cohorts_maturity_and_survival_landmark`) |
| `UAT-03` | Client exiting before day 90 post-activation | Excluded from Day-90 landmark survival cohort to prevent immortal-time bias. | Verified (`_build_landmark_dataframe`) |
| `UAT-04` | Multiple KYC rework loops on same client | Stored as separate `journey_stage_episodes` rows linked via `previous_episode_id`. | Verified (`test_planted_story_a_kyc_rework`) |
| `UAT-05` | Client with no qualifying interactions (>90d) | Flagged `Inactive` (engagement status), distinct from `Exited`. | Verified (`client_engine.py`) |
| `UAT-06` | Impact Simulator web vs. Excel workbook | Base, Conservative, and Optimistic formulas match 1:1. | Verified (`test_impact_simulator_and_excel_parity`) |
| `UAT-07` | SQL injection attempt in Client Explorer search | Parameterized query returns 0 rows safely with HTTP 200. | Verified (`test_client_explorer_and_sql_injection_resistance`) |
