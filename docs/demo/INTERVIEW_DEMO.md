# CONTINUUM — 4-Minute Interview Walkthrough

## Minute 1 — Business Problem (`Executive Overview`)
- Open `/overview`.
- **Say:** *"Client retention declined, and top-line retention alone doesn't tell us why. Here we see retention, onboarding duration, SLA attainment, and open backlog side-by-side—each backed by live PostgreSQL queries and an inspectable SQL lineage drawer."*
- Point to the **Operational Friction Panel** showing KYC rework rising post-April 2026 and North Region `T-03` backlog pressure.

## Minute 2 — Investigate the Process (`Journey Analytics`)
- Click the **KYC** row in the funnel to open `/journeys?stage=KYC`.
- **Say:** *"Rather than storing a single timestamp per stage, CONTINUUM models stage episodes. After the v2.4 checklist rollout on 2026-04-01, KYC rework jumped sharply due to missing identity documentation and checklist clarification, stretching the p90 tail."*
- Click a sample `Reopened` client ID to show the reconstructed **Client Journey Timeline** (`/clients/{id}`).

## Minute 3 — Analytical Rigor (`Retention Studio`)
- Open `/retention`.
- **Say:** *"In Retention Studio, immature 2026 cohorts are left blank rather than zeroed. Below, our Kaplan-Meier curves use a Day-90 landmark—excluding anyone who exited before day 90—to avoid immortal-time bias. And because high-asset-tier clients receive faster service AND have lower baseline attrition, our Cox PH model adjusts for Asset Tier to separate confounding from operational signal without claiming unproven causation."*

## Minute 4 — Business Decision (`Improvement Roadmap` & `Impact Simulator`)
- Open `/roadmap` and `/simulator`.
- **Say:** *"We translate findings into prioritized, testable experiments—like the KYC Pre-Submission Checker (`REC-001`) with explicit guardrails—and model scenario ranges in the Impact Simulator, which reconciles 1:1 with the downloadable Excel workbook."*
- **Close:** *"The objective isn't just to report that retention declined. It's to build a traceable analytical process that helps stakeholders identify where to investigate, decide what to test, and measure whether an intervention works."*
