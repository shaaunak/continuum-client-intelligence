"""Guided 6-step Investigation Lab engine."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.analytics.journey_engine import get_journey_funnel, get_stage_detail
from app.analytics.kpi_engine import get_executive_overview
from app.analytics.operations_engine import get_operations_complaints, get_operations_sla, get_operations_workload
from app.analytics.retention_engine import get_adjusted_comparison, get_survival_analysis
from app.models.entities import Investigation
from app.schemas.common import AnalyticsFilters

INVESTIGATION_TEMPLATES = [
    {
        "template_key": "retention_decline",
        "title": "Why did client retention decline?",
        "business_question": "Our client retention has declined. Which stages of the client journey have deteriorated, what evidence supports the suspected drivers, and which operational improvements should we test?",
        "operational_area": "End-to-End Lifecycle & Retention",
        "recommended_initiatives": ["REC-001", "REC-002"],
    },
    {
        "template_key": "onboarding_slowdown",
        "title": "Which onboarding stage became slower?",
        "business_question": "Onboarding cycle times lengthened in recent quarters. Which stage accounts for the delay and what rework drivers are responsible?",
        "operational_area": "Onboarding & KYC",
        "recommended_initiatives": ["REC-001"],
    },
    {
        "template_key": "sla_attrition",
        "title": "Are SLA breaches associated with client exits?",
        "business_question": "Do clients with repeated early SLA breaches exhibit lower post-90-day retention after accounting for asset tier?",
        "operational_area": "Service SLA & Retention",
        "recommended_initiatives": ["REC-002", "REC-003"],
    },
    {
        "template_key": "team_backlog",
        "title": "Which service teams have growing backlogs?",
        "business_question": "Where is open service backlog concentrating, and which teams are operating above sustainable capacity?",
        "operational_area": "Service Operations & Advisor Capacity",
        "recommended_initiatives": ["REC-003", "REC-004"],
    },
    {
        "template_key": "complaint_spike",
        "title": "Are recurring complaints linked to a process change?",
        "business_question": "Which complaint categories spiked recently, and are they associated with a dated operational process change?",
        "operational_area": "Complaints & Process Quality",
        "recommended_initiatives": ["REC-003"],
    },
]


def run_investigation(
    db: Session,
    template_key: str,
    filters: AnalyticsFilters,
    created_by: str = "Lead Business Analyst",
) -> dict[str, Any]:
    tmpl = next((t for t in INVESTIGATION_TEMPLATES if t["template_key"] == template_key), INVESTIGATION_TEMPLATES[0])

    overview = get_executive_overview(db, filters)
    funnel = get_journey_funnel(db, filters)
    kyc_detail = get_stage_detail(db, "KYC", filters)
    workload = get_operations_workload(db, filters)
    sla = get_operations_sla(db, filters)
    complaints = get_operations_complaints(db, filters)
    survival = get_survival_analysis(db, filters)
    adjusted = get_adjusted_comparison(db, filters)

    # Extract computed KPIs
    kpi_map = {k["key"]: k for k in overview["kpis"]}
    kyc_stage = next((s for s in funnel["stages"] if s["stage"] == "KYC"), {})
    overloaded_teams = [t for t in workload["teams"] if (t["utilization_pct"] or 0) >= 95.0]
    top_complaint = complaints["pareto"][0] if complaints["pareto"] else None

    step2_changes = [
        {
            "metric": "Client Retention Rate",
            "current": f"{kpi_map['client_retention_rate']['value']}%",
            "previous": f"{kpi_map['client_retention_rate']['previous_value']}%",
            "delta": f"{kpi_map['client_retention_rate']['change']:+.2f} pp",
            "denominator": f"{kpi_map['client_retention_rate']['denominator']:,} clients at risk",
        },
        {
            "metric": "KYC Rework Rate",
            "current": f"{kyc_stage.get('rework_rate', 0)}%",
            "previous": f"{kyc_stage.get('prev_rework_rate', 0)}%",
            "delta": f"{kyc_stage.get('rework_change_pp', 0):+.2f} pp",
            "denominator": f"{kyc_stage.get('entered_count', 0):,} entered clients",
        },
        {
            "metric": "First-Response SLA Attainment",
            "current": f"{kpi_map['first_response_sla_attainment']['value']}%",
            "previous": f"{kpi_map['first_response_sla_attainment']['previous_value']}%",
            "delta": f"{kpi_map['first_response_sla_attainment']['change']:+.2f} pp",
            "denominator": f"{kpi_map['first_response_sla_attainment']['denominator']:,} due cases",
        },
        {
            "metric": "Open Service Backlog",
            "current": f"{int(kpi_map['backlog_aging']['value']):,}",
            "previous": f"{int(kpi_map['backlog_aging']['previous_value']):,}",
            "delta": f"{int(kpi_map['backlog_aging']['change']):+,} cases",
            "denominator": "Point-in-time open/in-progress cases",
        },
    ]

    step3_drivers = {
        "onboarding_kyc": {
            "top_rework_reasons": kyc_detail["rework_reasons"][:3],
            "median_days": kyc_stage.get("median_days"),
            "p90_days": kyc_stage.get("p90_days"),
            "related_process_change": "PC-001 (Enhanced KYC Documentation Checklist v2.4, effective 2026-04-01)",
        },
        "capacity_pressure": {
            "overloaded_teams": overloaded_teams,
            "aged_15plus_cases": next((b["count"] for b in workload["aging_buckets"] if b["bucket"] == "15+ days"), 0),
            "related_process_change": "PC-002 (North Region T-03 Staffing Reduction, effective 2026-05-15)",
        },
        "complaints": {
            "top_category": top_complaint,
            "related_process_change": "PC-003 (Custodial Transfer Automation Rollout, effective 2026-06-01)",
        },
    }

    step4_outcomes = {
        "landmark_eligible_clients": survival["eligible_clients"],
        "survival_groups": [
            {
                "group": g["group"],
                "n_at_risk_day0": g["n_at_risk_day0"],
                "events": g["events"],
                "day_365_survival_pct": next(
                    (p["survival_pct"] for p in g.get("points", []) if p["post_landmark_days"] == 365), None
                ),
            }
            for g in survival["groups"]
        ],
        "cox_model": adjusted.get("cox_model", {}),
    }

    step5_alternatives = [
        "Client Value Confounding: Higher-asset-tier clients receive faster SLA service AND have lower baseline attrition; unadjusted comparisons overstate the SLA-exit gap.",
        "Cohort Maturity: Recent 2026 cohorts have shorter post-activation follow-up and are right-censored at 2026-10-31.",
        "Reverse Causality: Disengaged clients may submit fewer inquiries or respond more slowly to KYC document requests.",
        "Unmeasured Factors: Market volatility, external advisor changes, and tax-season volume spikes are not fully captured.",
    ]

    findings = {
        "step_1_question": {
            "template_key": tmpl["template_key"],
            "title": tmpl["title"],
            "business_question": tmpl["business_question"],
            "operational_area": tmpl["operational_area"],
            "scope": {
                "start_date": filters.start_date.isoformat(),
                "end_date": filters.end_date.isoformat(),
                "comparison_period": overview["comparison_period"],
                "segment": filters.segment or "All",
                "team_id": filters.team_id or "All",
                "region": filters.region or "All",
            },
        },
        "step_2_changes": step2_changes,
        "step_3_drivers": step3_drivers,
        "step_4_outcomes": step4_outcomes,
        "step_5_alternatives": step5_alternatives,
        "step_6_summary": {
            "executive_conclusion": (
                f"During {filters.start_date} to {filters.end_date}, client retention measured {kpi_map['client_retention_rate']['value']}% "
                f"({kpi_map['client_retention_rate']['change']:+.2f} pp vs. prior window). "
                f"Operational deterioration is concentrated in KYC rework ({kyc_stage.get('rework_rate', 0)}%, "
                f"{kyc_stage.get('rework_change_pp', 0):+.2f} pp), service SLA attainment ({kpi_map['first_response_sla_attainment']['value']}%), "
                f"and capacity pressure in {len(overloaded_teams)} team(s)."
            ),
            "proposed_experiments": tmpl["recommended_initiatives"],
            "recommended_owners": ["Operations Lead", "Client Service Manager", "Compliance Representative"],
            "provenance_note": "All figures computed deterministically from PostgreSQL as of 2026-10-31.",
        },
    }

    inv_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
    inv = Investigation(
        investigation_id=inv_id,
        title=tmpl["title"],
        template_key=tmpl["template_key"],
        business_question=tmpl["business_question"],
        scope_json=findings["step_1_question"]["scope"],
        findings_json=findings,
        status="Completed",
        created_by=created_by,
    )
    db.add(inv)
    db.commit()

    return {
        "investigation_id": inv_id,
        "created_at": inv.created_at.isoformat() if inv.created_at else None,
        "findings": findings,
    }
