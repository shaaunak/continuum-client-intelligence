# 06 — Functional Requirements

| Req ID | Area | Functional Requirement | Linked Objective |
| --- | --- | --- | --- |
| `FR-EXEC-001` | Executive Overview | Display 6 core KPIs with period-over-period comparisons (pp / days / count) and clickable SQL lineage drawers. | OBJ-1 |
| `FR-ONB-001` | Journey Analytics | Reconstruct 7-stage lifecycle funnel using `journey_stage_episodes`, separating In Progress from Cancelled. | OBJ-2 |
| `FR-ONB-002` | Journey Analytics | Drill into KYC rework reasons, monthly rework/p90 trends, and affected client episodes. | OBJ-2 |
| `FR-RET-001` | Retention Studio | Render monthly activation cohort heatmap leaving unobserved future months blank/unavailable. | OBJ-3 |
| `FR-RET-003` | Retention Studio | Compute Day-90 landmark Kaplan-Meier survival curves and asset-tier-adjusted Cox PH hazard ratios. | OBJ-3 |
| `FR-RET-004` | Client Explorer | Filter and search clients by deterministic engagement status (`At Risk`, `Inactive`, `Engaged`) and render full event timeline. | OBJ-3 |
| `FR-OPS-003` | Service Operations | Calculate business-hours SLA attainment (`America/New_York`), backlog aging buckets, and team capacity utilization. | OBJ-4 |
| `FR-ADV-002` | Advisor Intelligence | Compute Observed-vs-Expected (O/E) breach ratios adjusted for case complexity mix. | OBJ-4 |
| `FR-DEC-001` | Impact Simulator | Synchronize web scenario calculations 1:1 with formula-driven Excel workbook (`.xlsx`). | OBJ-4 |
