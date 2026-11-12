# 13 — Requirements Traceability Matrix

| Objective | Functional Req | User Story | API Endpoint / SQL Logic | Automated Test | UI Screen |
| --- | --- | --- | --- | --- | --- |
| `OBJ-1` | `FR-EXEC-001` | `US-EXEC-001` | `GET /api/v1/overview` | `test_overview_and_trends` | Executive Overview |
| `OBJ-2` | `FR-ONB-002` | `US-ONB-002` | `GET /api/v1/journey/stages/KYC` | `test_planted_story_a_kyc_rework` | Journey Analytics |
| `OBJ-3` | `FR-RET-003` | `US-RET-003` | `GET /api/v1/retention/survival` | `test_retention_cohorts_maturity_and_survival_landmark` | Retention Studio |
| `OBJ-3` | `FR-RET-004` | `US-RET-004` | `GET /api/v1/clients/{id}/journey` | `test_client_explorer_and_sql_injection_resistance` | Client Explorer |
| `OBJ-4` | `FR-OPS-003` | `US-OPS-005` | `GET /api/v1/operations/workload` | `test_planted_story_b_t3_capacity_pressure` | Service Operations |
| `OBJ-4` | `FR-DEC-001` | `US-DEC-007` | `POST /api/v1/impact/excel` | `test_impact_simulator_and_excel_parity` | Impact Simulator |
