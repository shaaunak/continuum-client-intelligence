"""KPI Dictionary, SQL Lineage, Data Quality Reconciliation, and Requirements Hub engine."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings


def get_metric_dictionary(db: Session) -> list[dict[str, Any]]:
    rows = db.execute(
        text("SELECT * FROM metric_definitions ORDER BY kpi_name ASC")
    ).mappings().all()
    return [
        {
            "metric_key": r["metric_key"],
            "kpi_name": r["kpi_name"],
            "business_meaning": r["business_meaning"],
            "formula": r["formula"],
            "numerator": r["numerator"],
            "denominator": r["denominator"],
            "time_basis": r["time_basis"],
            "inclusion_criteria": r["inclusion_criteria"],
            "exclusions": r["exclusions"],
            "data_source": r["data_source"],
            "sql_template": r["sql_template"],
            "known_limitations": r["known_limitations"],
            "updated_at": r["updated_at"].isoformat() if r["updated_at"] else None,
        }
        for r in rows
    ]


def get_metric_lineage(db: Session, metric_key: str) -> dict[str, Any] | None:
    settings = get_settings()
    r = db.execute(
        text("SELECT * FROM metric_definitions WHERE metric_key = :mk"),
        {"mk": metric_key},
    ).mappings().first()
    if not r:
        return None
    return {
        "metric_key": r["metric_key"],
        "kpi_name": r["kpi_name"],
        "business_meaning": r["business_meaning"],
        "formula": r["formula"],
        "numerator": r["numerator"],
        "denominator": r["denominator"],
        "time_basis": r["time_basis"],
        "inclusion_criteria": r["inclusion_criteria"],
        "exclusions": r["exclusions"],
        "data_source": r["data_source"],
        "sql_query": r["sql_template"],
        "known_limitations": r["known_limitations"],
        "as_of_date": settings.AS_OF_DATE,
    }


def get_data_quality_report(db: Session) -> dict[str, Any]:
    settings = get_settings()
    checks = []

    def _add_check(name: str, query: str, expected_zero: bool = True, detail: str = "") -> None:
        val = int(db.execute(text(query)).scalar() or 0)
        passed = (val == 0) if expected_zero else (val > 0)
        checks.append(
            {
                "check_name": name,
                "observed_value": val,
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

    _add_check(
        "No Client Exits Before Activation",
        "SELECT COUNT(*) FROM clients WHERE exited_at IS NOT NULL AND (activated_at IS NULL OR exited_at < activated_at)",
        True,
        "Pre-activation drop-offs must be marked Abandoned, not Exited.",
    )
    _add_check(
        "No Future Exit Timestamps",
        f"SELECT COUNT(*) FROM clients WHERE exited_at > '{settings.AS_OF_DATE}T23:59:59Z'",
        True,
        f"All events must be <= as-of date ({settings.AS_OF_DATE}).",
    )
    _add_check(
        "No First Response Before Case Creation",
        "SELECT COUNT(*) FROM service_cases WHERE first_response_at IS NOT NULL AND first_response_at < created_at",
        True,
        "Chronological ordering of case lifecycle timestamps.",
    )
    _add_check(
        "No Resolution Before Case Creation",
        "SELECT COUNT(*) FROM service_cases WHERE resolved_at IS NOT NULL AND resolved_at < created_at",
        True,
        "Cases cannot close before opening.",
    )
    _add_check(
        "No Premature SLA Breaches on Open Cases",
        f"SELECT COUNT(*) FROM service_cases WHERE first_response_at IS NULL AND first_response_due_at > '{settings.AS_OF_DATE}T23:59:59Z' AND first_response_breached = TRUE",
        True,
        "Cases not yet due must not be treated as SLA failures.",
    )
    _add_check(
        "Advisor-Team Referential Integrity",
        "SELECT COUNT(*) FROM advisors a LEFT JOIN advisor_teams t ON t.team_id = a.team_id WHERE t.team_id IS NULL",
        True,
        "Every advisor must belong to a valid team.",
    )

    table_counts = {}
    for tbl in [
        "clients",
        "advisors",
        "advisor_teams",
        "journey_stage_episodes",
        "journey_events",
        "service_cases",
        "complaints",
        "client_interactions",
        "follow_up_tasks",
    ]:
        table_counts[tbl] = int(db.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar() or 0)

    return {
        "as_of_date": settings.AS_OF_DATE,
        "dataset_scale": settings.DATASET_SCALE,
        "seed": settings.DATA_SEED,
        "all_passed": all(c["status"] == "PASS" for c in checks),
        "checks": checks,
        "table_counts": table_counts,
    }


def get_requirements_hub() -> dict[str, Any]:
    return {
        "brd_summary": {
            "project_name": "CONTINUUM — Client Lifecycle & Retention Intelligence",
            "organization": "Meridian Private Wealth (Fictional)",
            "problem_statement": "Leadership observed declining client retention and lengthening onboarding times without a unified, evidence-based way to isolate process bottlenecks, evaluate early SLA exposure without statistical bias, or prioritize operational experiments.",
            "objectives": [
                "OBJ-1: Provide executive visibility into client retention, onboarding funnel health, and service SLA attainment.",
                "OBJ-2: Isolate onboarding rework drivers (specifically KYC v2.4 checklist impact).",
                "OBJ-3: Quantify post-90-day retention differences by early SLA experience while adjusting for client asset tier confounding.",
                "OBJ-4: Enable fair advisor workload balancing and evidence-backed operational experimentation.",
            ],
            "scope_in": [
                "7-stage event-sourced onboarding & ongoing service lifecycle analytics",
                "Monthly cohort retention & Day-90 landmark Kaplan-Meier / Cox PH survival analysis",
                "Business-hours SLA tracking & team capacity utilization",
                "Guided 6-step Investigation Lab, Improvement Roadmap, and Impact Simulator",
            ],
            "scope_out": [
                "Live core-banking / custodian API write-backs (synthetic batch environment)",
                "Automated individual client churn prediction scoring",
                "Production SSO / RBAC banking security",
            ],
            "sign_off_placeholders": [
                {"role": "Head of Wealth Management (Fictional)", "status": "Pending Review"},
                {"role": "Operations Lead (Fictional)", "status": "Pending Review"},
                {"role": "Compliance Representative (Fictional)", "status": "Pending Review"},
            ],
        },
        "raci_matrix": [
            {"workflow": "Onboarding KYC Process Governance", "R": "Operations Lead", "A": "Compliance Representative", "C": "Relationship Manager", "I": "Head of Wealth Management"},
            {"workflow": "Service SLA & Backlog Management", "R": "Client Service Manager", "A": "Operations Lead", "C": "Data Analyst", "I": "Relationship Manager"},
            {"workflow": "Retention & Survival Analytics", "R": "Data Analyst", "A": "Product Owner", "C": "Engineering Lead", "I": "Head of Wealth Management"},
            {"workflow": "Experiment Design & Rollout", "R": "Product Owner", "A": "Head of Wealth Management", "C": "Data Analyst, Compliance Representative", "I": "Client Service Manager"},
        ],
        "user_stories": [
            {
                "id": "US-EXEC-001",
                "epic": "Executive Intelligence",
                "title": "Compare Period Retention & Operational Friction",
                "priority": "Must Have",
                "status": "Implemented",
                "linked_req": "FR-EXEC-001",
                "screen": "/overview",
                "acceptance_criteria": "Given a selected date range and segment, when Executive Overview loads, then all 6 KPIs display current value, prior comparable window, pp/unit delta, and SQL View Calculation drawer.",
            },
            {
                "id": "US-ONB-002",
                "epic": "Journey Analytics",
                "title": "Diagnose KYC Rework & Stage Duration Tail",
                "priority": "Must Have",
                "status": "Implemented",
                "linked_req": "FR-ONB-002",
                "screen": "/journeys",
                "acceptance_criteria": "Given Journey Analytics, when clicking KYC stage, then rework rate, p50/p90 duration, frequent rework reasons, and post-2026-04-01 monthly trend render from PostgreSQL.",
            },
            {
                "id": "US-RET-003",
                "epic": "Retention Studio",
                "title": "Evaluate Post-90-Day Survival Without Immortal-Time Bias",
                "priority": "Must Have",
                "status": "Implemented",
                "linked_req": "FR-RET-003",
                "screen": "/retention",
                "acceptance_criteria": "Given Retention Studio, only clients active at day 90 are included in landmark Kaplan-Meier curves, and unadjusted vs. asset-tier-adjusted Cox hazard ratios are shown with caveats.",
            },
            {
                "id": "US-RET-004",
                "epic": "Client Explorer",
                "title": "Investigate Clients With Repeated Early SLA Breaches",
                "priority": "Must Have",
                "status": "Implemented",
                "linked_req": "FR-RET-004",
                "screen": "/clients",
                "acceptance_criteria": "Given Client Explorer, filtering by At Risk displays eligible client IDs, early SLA breach counts, advisor, and days since last contact; clicking opens full event timeline.",
            },
            {
                "id": "US-OPS-005",
                "epic": "Service Operations",
                "title": "Identify Overloaded Teams & Aged Backlog",
                "priority": "Should Have",
                "status": "Implemented",
                "linked_req": "FR-OPS-003",
                "screen": "/operations",
                "acceptance_criteria": "Given Service Operations, team utilization uses active advisor headcount * 35 and separates 0-2d, 3-7d, 8-14d, and 15+d backlog buckets.",
            },
        ],
        "uat_scenarios": [
            {"id": "UAT-01", "scenario": "Open cases not yet due for first response", "expected": "Excluded from SLA breach failures; first_response_breached = FALSE."},
            {"id": "UAT-02", "scenario": "Recently activated immature cohort (Oct 2026)", "expected": "Future cohort retention months are blank/null, never 0%."},
            {"id": "UAT-03", "scenario": "Client exiting before day 90 post-activation", "expected": "Excluded from Day-90 landmark survival cohort to prevent immortal-time bias."},
            {"id": "UAT-04", "scenario": "Multiple KYC rework loops on same client", "expected": "Each loop stored as separate journey_stage_episodes row linked via previous_episode_id."},
            {"id": "UAT-05", "scenario": "Impact Simulator vs Excel workbook reconciliation", "expected": "Base, Conservative, and Optimistic retained clients and assets match identically."},
        ],
        "traceability_matrix": [
            {"objective": "OBJ-1", "requirement": "FR-EXEC-001", "story": "US-EXEC-001", "api": "GET /api/v1/overview", "test": "test_overview_api", "screen": "Executive Overview"},
            {"objective": "OBJ-2", "requirement": "FR-ONB-002", "story": "US-ONB-002", "api": "GET /api/v1/journey/stages/KYC", "test": "test_planted_story_a_kyc_rework", "screen": "Journey Analytics"},
            {"objective": "OBJ-3", "requirement": "FR-RET-003", "story": "US-RET-003", "api": "GET /api/v1/retention/survival", "test": "test_survival_landmark_eligibility", "screen": "Retention Studio"},
            {"objective": "OBJ-4", "requirement": "FR-OPS-003", "story": "US-OPS-005", "api": "GET /api/v1/operations/workload", "test": "test_planted_story_b_t3_capacity_pressure", "screen": "Service Operations"},
        ],
    }
