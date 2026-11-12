# 01 — Business Requirements Document (BRD)

**Project:** CONTINUUM — Client Lifecycle & Retention Intelligence  
**Organization:** Meridian Private Wealth (Fictional)  
**Document Version:** 1.0  
**As-Of Observation Date:** 2026-10-31  

## 1. Executive Summary
Meridian Private Wealth experienced an observed decline in client retention and a lengthening of client onboarding cycle times following operational changes in 2026. Existing reporting only surfaces top-line retention percentages, leaving leadership unable to determine which lifecycle stages deteriorated, whether early service-level agreement (SLA) breaches are associated with attrition after accounting for client asset tier, or which operational improvements warrant investment. CONTINUUM provides an evidence-driven analytical platform connecting **observation → investigation → evidence → recommendation → experiment**.

## 2. Business Problem
- Top-line retention percentages mask stage-specific onboarding friction and post-activation service delays.
- Without stage-episode tracking, reopened KYC submissions and repeat service contacts are invisible.
- Naive comparisons between SLA performance and attrition are confounded by client asset tier (higher-value clients receive faster service and exhibit lower baseline attrition).

## 3. Objectives
- **OBJ-1:** Deliver executive visibility into active clients, retention/attrition, onboarding duration, SLA attainment, and open backlog with full SQL lineage.
- **OBJ-2:** Isolate onboarding stage deterioration and quantify rework drivers (e.g., KYC v2.4 checklist impact).
- **OBJ-3:** Evaluate post-90-day client retention by early SLA experience using a Day-90 landmark Kaplan-Meier and asset-tier-adjusted Cox proportional hazards framework.
- **OBJ-4:** Provide fair, case-mix-adjusted advisor workload intelligence and an interactive Impact Simulator to evaluate proposed operational pilots.

## 4. Scope
**In-Scope:**
- Event-sourced 7-stage client lifecycle funnel (`Prospect` → `KYC` → `Account Opening` → `Funding` → `First Advisor Meeting` → `Portfolio Setup` → `Ongoing Service`).
- Monthly cohort retention heatmap (respecting cohort maturity) and Day-90 landmark survival analysis.
- Business-hours SLA engine (`Mon–Fri 09:00–17:00 America/New_York`) and complaint Pareto analytics.
- Guided 6-step Investigation Lab, RICE-scored Improvement Roadmap, synchronized Web + Excel Impact Simulator, and Tableau-ready CSV extracts.

**Out-of-Scope:**
- Live production core-banking / custodian API integration (platform operates on a deterministic synthetic PostgreSQL dataset).
- Black-box predictive churn scoring on individual clients.
- Production banking SSO/RBAC.

## 5. Success Criteria
1. 100% of dashboard KPIs reconcile with PostgreSQL source queries and expose inspectable SQL lineage.
2. Survival analysis eliminates immortal-time bias via Day-90 landmarking and explicitly discloses confounding caveats.
3. All 4 starter operational recommendations link to measurable experiment designs, guardrails, and user stories.

## 6. Sign-Off Placeholders (Fictional)
| Role | Name (Fictional) | Status |
| --- | --- | --- |
| Head of Wealth Management | Executive Sponsor | Pending Review |
| Operations Lead | Operations Sponsor | Pending Review |
| Compliance Representative | Governance Reviewer | Pending Review |
| Product Owner | BA / Analytics Lead | Approved for Demo |
