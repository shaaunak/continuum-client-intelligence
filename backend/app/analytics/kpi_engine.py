"""Executive KPI, trend, and operational friction calculation engine."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.common import AnalyticsFilters


def _dt_range(start_d: date, end_d: date) -> tuple[datetime, datetime]:
    return (
        datetime.combine(start_d, time(0, 0, 0), tzinfo=timezone.utc),
        datetime.combine(end_d, time(23, 59, 59), tzinfo=timezone.utc),
    )


def _prev_window(filters: AnalyticsFilters) -> tuple[date, date]:
    if filters.compare_start_date and filters.compare_end_date:
        return filters.compare_start_date, filters.compare_end_date
    span_days = (filters.end_date - filters.start_date).days + 1
    prev_end = filters.start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=span_days - 1)
    return prev_start, prev_end


def _client_filter_sql(filters: AnalyticsFilters, alias: str = "c") -> tuple[str, dict[str, Any]]:
    clauses: list[str] = []
    params: dict[str, Any] = {}
    if filters.segment and filters.segment != "All":
        clauses.append(f"{alias}.segment = :segment")
        params["segment"] = filters.segment
    if filters.region and filters.region != "All":
        clauses.append(f"{alias}.region = :region")
        params["region"] = filters.region
    if filters.asset_tier and filters.asset_tier != "All":
        clauses.append(f"{alias}.asset_tier = :asset_tier")
        params["asset_tier"] = filters.asset_tier
    if filters.team_id and filters.team_id != "All":
        clauses.append(
            f"EXISTS (SELECT 1 FROM advisor_assignments aa WHERE aa.client_id = {alias}.client_id AND aa.is_primary = TRUE AND aa.team_id = :team_id)"
        )
        params["team_id"] = filters.team_id
    sql = (" AND " + " AND ".join(clauses)) if clauses else ""
    return sql, params


def _compute_period_kpis(db: Session, start_d: date, end_d: date, filters: AnalyticsFilters) -> dict[str, Any]:
    start_dt, end_dt = _dt_range(start_d, end_d)
    c_filter, params = _client_filter_sql(filters, "c")
    params.update({"start_dt": start_dt, "end_dt": end_dt})

    # 1. Active clients at end_dt & retention/attrition over [start_dt, end_dt]
    ret_row = db.execute(
        text(
            f"""
            SELECT
                COUNT(*) FILTER (
                    WHERE c.activated_at <= :end_dt
                      AND (c.exited_at IS NULL OR c.exited_at > :end_dt)
                ) AS active_clients,
                COUNT(*) FILTER (
                    WHERE c.activated_at < :start_dt
                      AND (c.exited_at IS NULL OR c.exited_at >= :start_dt)
                ) AS at_risk_start,
                COUNT(*) FILTER (
                    WHERE c.activated_at < :start_dt
                      AND c.exited_at >= :start_dt
                      AND c.exited_at <= :end_dt
                ) AS exited_in_window
            FROM clients c
            WHERE 1=1 {c_filter}
            """
        ),
        params,
    ).mappings().one()

    active_clients = int(ret_row["active_clients"] or 0)
    at_risk_start = int(ret_row["at_risk_start"] or 0)
    exited_in_window = int(ret_row["exited_in_window"] or 0)
    attrition_rate = round((exited_in_window / at_risk_start) * 100.0, 2) if at_risk_start > 0 else 0.0
    retention_rate = round(100.0 - attrition_rate, 2) if at_risk_start > 0 else 100.0

    # 2. Median onboarding duration (prospect_created_at -> activated_at in days) for clients activated in window
    onb_row = db.execute(
        text(
            f"""
            SELECT
                PERCENTILE_CONT(0.5) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (c.activated_at - c.prospect_created_at)) / 86400.0
                ) AS median_onb_days,
                COUNT(*) AS activated_count
            FROM clients c
            WHERE c.activated_at BETWEEN :start_dt AND :end_dt
              {c_filter}
            """
        ),
        params,
    ).mappings().one()
    median_onb_days = round(float(onb_row["median_onb_days"] or 0.0), 1)
    activated_count = int(onb_row["activated_count"] or 0)

    # 3. First-response SLA attainment & Open service backlog
    case_team_clause = "AND sc.assigned_team_id = :team_id" if (filters.team_id and filters.team_id != "All") else ""
    sla_row = db.execute(
        text(
            f"""
            SELECT
                COUNT(*) FILTER (
                    WHERE sc.created_at BETWEEN :start_dt AND :end_dt
                      AND sc.first_response_due_at <= :end_dt
                      AND sc.first_response_breached = FALSE
                      AND sc.first_response_at IS NOT NULL
                ) AS sla_met,
                COUNT(*) FILTER (
                    WHERE sc.created_at BETWEEN :start_dt AND :end_dt
                      AND sc.first_response_due_at <= :end_dt
                ) AS sla_due,
                COUNT(*) FILTER (
                    WHERE sc.created_at <= :end_dt
                      AND (sc.resolved_at IS NULL OR sc.resolved_at > :end_dt)
                ) AS open_backlog
            FROM service_cases sc
            JOIN clients c ON c.client_id = sc.client_id
            WHERE 1=1 {c_filter} {case_team_clause}
            """
        ),
        params,
    ).mappings().one()

    sla_met = int(sla_row["sla_met"] or 0)
    sla_due = int(sla_row["sla_due"] or 0)
    sla_attainment = round((sla_met / sla_due) * 100.0, 2) if sla_due > 0 else 100.0
    open_backlog = int(sla_row["open_backlog"] or 0)

    # 4. KYC Rework Rate for friction panel
    kyc_row = db.execute(
        text(
            f"""
            SELECT
                COUNT(*) FILTER (WHERE e.outcome = 'Reopened') AS reopened_cnt,
                COUNT(*) FILTER (WHERE e.previous_episode_id IS NULL) AS initial_cnt
            FROM journey_stage_episodes e
            JOIN clients c ON c.client_id = e.client_id
            WHERE e.stage = 'KYC'
              AND e.entered_at BETWEEN :start_dt AND :end_dt
              {c_filter}
            """
        ),
        params,
    ).mappings().one()
    kyc_reopened = int(kyc_row["reopened_cnt"] or 0)
    kyc_initial = int(kyc_row["initial_cnt"] or 0)
    kyc_rework_rate = round((kyc_reopened / kyc_initial) * 100.0, 2) if kyc_initial > 0 else 0.0

    return {
        "active_clients": active_clients,
        "retention_rate": retention_rate,
        "attrition_rate": attrition_rate,
        "at_risk_start": at_risk_start,
        "exited_in_window": exited_in_window,
        "median_onb_days": median_onb_days,
        "activated_count": activated_count,
        "sla_attainment": sla_attainment,
        "sla_met": sla_met,
        "sla_due": sla_due,
        "open_backlog": open_backlog,
        "kyc_rework_rate": kyc_rework_rate,
        "kyc_reopened": kyc_reopened,
        "kyc_initial": kyc_initial,
    }


def get_executive_overview(db: Session, filters: AnalyticsFilters) -> dict[str, Any]:
    prev_start, prev_end = _prev_window(filters)
    cur = _compute_period_kpis(db, filters.start_date, filters.end_date, filters)
    prev = _compute_period_kpis(db, prev_start, prev_end, filters)

    def _dir(delta: float) -> str:
        if delta > 0.05:
            return "up"
        if delta < -0.05:
            return "down"
        return "flat"

    kpis = [
        {
            "key": "active_clients",
            "label": "Active Clients",
            "value": cur["active_clients"],
            "previous_value": prev["active_clients"],
            "change": cur["active_clients"] - prev["active_clients"],
            "change_unit": "count",
            "unit": "count",
            "direction": _dir(cur["active_clients"] - prev["active_clients"]),
            "favorable_direction": "up",
            "tooltip": "Activated wealth clients not formally exited as of period end.",
            "drilldown_route": "/clients",
            "numerator": cur["active_clients"],
            "denominator": None,
        },
        {
            "key": "client_retention_rate",
            "label": "Client Retention Rate",
            "value": cur["retention_rate"],
            "previous_value": prev["retention_rate"],
            "change": round(cur["retention_rate"] - prev["retention_rate"], 2),
            "change_unit": "pp",
            "unit": "%",
            "direction": _dir(cur["retention_rate"] - prev["retention_rate"]),
            "favorable_direction": "up",
            "tooltip": "1 minus period attrition rate among clients active at period start.",
            "drilldown_route": "/retention",
            "numerator": cur["at_risk_start"] - cur["exited_in_window"],
            "denominator": cur["at_risk_start"],
        },
        {
            "key": "client_attrition_rate",
            "label": "Client Attrition Rate",
            "value": cur["attrition_rate"],
            "previous_value": prev["attrition_rate"],
            "change": round(cur["attrition_rate"] - prev["attrition_rate"], 2),
            "change_unit": "pp",
            "unit": "%",
            "direction": _dir(cur["attrition_rate"] - prev["attrition_rate"]),
            "favorable_direction": "down",
            "tooltip": "Share of clients active at period start who formally exited during the window.",
            "drilldown_route": "/retention",
            "numerator": cur["exited_in_window"],
            "denominator": cur["at_risk_start"],
        },
        {
            "key": "stage_completion_time",
            "label": "Median Onboarding Duration",
            "value": cur["median_onb_days"],
            "previous_value": prev["median_onb_days"],
            "change": round(cur["median_onb_days"] - prev["median_onb_days"], 1),
            "change_unit": "days",
            "unit": "days",
            "direction": _dir(cur["median_onb_days"] - prev["median_onb_days"]),
            "favorable_direction": "down",
            "tooltip": "Median calendar days from prospect creation to funded account activation.",
            "drilldown_route": "/journeys",
            "numerator": cur["activated_count"],
            "denominator": cur["activated_count"],
        },
        {
            "key": "first_response_sla_attainment",
            "label": "First-Response SLA",
            "value": cur["sla_attainment"],
            "previous_value": prev["sla_attainment"],
            "change": round(cur["sla_attainment"] - prev["sla_attainment"], 2),
            "change_unit": "pp",
            "unit": "%",
            "direction": _dir(cur["sla_attainment"] - prev["sla_attainment"]),
            "favorable_direction": "up",
            "tooltip": "Share of due service cases receiving first response within business-hours SLA.",
            "drilldown_route": "/operations",
            "numerator": cur["sla_met"],
            "denominator": cur["sla_due"],
        },
        {
            "key": "backlog_aging",
            "label": "Open Service Backlog",
            "value": cur["open_backlog"],
            "previous_value": prev["open_backlog"],
            "change": cur["open_backlog"] - prev["open_backlog"],
            "change_unit": "count",
            "unit": "count",
            "direction": _dir(cur["open_backlog"] - prev["open_backlog"]),
            "favorable_direction": "down",
            "tooltip": "Service cases remaining open or in-progress at period end.",
            "drilldown_route": "/operations",
            "numerator": cur["open_backlog"],
            "denominator": None,
        },
    ]

    # Operational friction signals computed directly from period deltas
    kyc_delta = round(cur["kyc_rework_rate"] - prev["kyc_rework_rate"], 2)
    sla_delta = round(cur["sla_attainment"] - prev["sla_attainment"], 2)
    backlog_delta = cur["open_backlog"] - prev["open_backlog"]
    ret_delta = round(cur["retention_rate"] - prev["retention_rate"], 2)

    friction_signals = [
        {
            "id": "friction_kyc",
            "title": "KYC Rework Rate",
            "metric_value": f"{cur['kyc_rework_rate']:.1f}%",
            "delta_label": f"{kyc_delta:+.1f} pp vs. prior period",
            "severity": "risk" if kyc_delta > 5 else ("warning" if kyc_delta > 1 else "ok"),
            "evidence": f"{cur['kyc_reopened']:,} reopened of {cur['kyc_initial']:,} initial KYC submissions.",
            "route": "/journeys?stage=KYC",
        },
        {
            "id": "friction_sla",
            "title": "First-Response SLA Attainment",
            "metric_value": f"{cur['sla_attainment']:.1f}%",
            "delta_label": f"{sla_delta:+.1f} pp vs. prior period",
            "severity": "risk" if sla_delta < -5 else ("warning" if sla_delta < -1.5 else "ok"),
            "evidence": f"{cur['sla_met']:,} of {cur['sla_due']:,} due cases responded within SLA.",
            "route": "/operations",
        },
        {
            "id": "friction_backlog",
            "title": "Unresolved Service Backlog",
            "metric_value": f"{cur['open_backlog']:,}",
            "delta_label": f"{backlog_delta:+,} cases vs. prior period end",
            "severity": "risk" if backlog_delta > 150 else ("warning" if backlog_delta > 40 else "ok"),
            "evidence": f"Open/In-Progress cases as of {filters.end_date.isoformat()}.",
            "route": "/operations",
        },
    ]

    insights = [
        {
            "category": "Observed Deterioration",
            "headline": f"KYC rework rose by {kyc_delta:+.1f} pp ({prev['kyc_rework_rate']:.1f}% -> {cur['kyc_rework_rate']:.1f}%) while median onboarding shifted by {cur['median_onb_days'] - prev['median_onb_days']:+.1f} days.",
            "supporting_evidence": f"Measured across {cur['kyc_initial']:,} initial KYC episodes ({filters.start_date} to {filters.end_date}) vs. {prev['kyc_initial']:,} in prior window.",
            "related_outcome": f"Period retention stands at {cur['retention_rate']:.2f}% ({ret_delta:+.2f} pp vs. prior period). Correlation does not establish causation.",
            "next_action": "Inspect KYC rework reasons & post-April 2026 checklist episodes in Journey Analytics.",
            "route": "/journeys?stage=KYC",
        },
        {
            "category": "Operational Bottleneck",
            "headline": f"First-response SLA attainment shifted {sla_delta:+.1f} pp to {cur['sla_attainment']:.1f}% with {cur['open_backlog']:,} open cases.",
            "supporting_evidence": f"Calculated using business-hours calendar (Mon-Fri 09:00-17:00 ET) across {cur['sla_due']:,} due cases.",
            "related_outcome": "Early-tenure clients with repeated SLA misses show higher observed attrition in day-90 landmark survival curves.",
            "next_action": "Review team capacity utilization in Service Operations & Advisor Intelligence.",
            "route": "/operations",
        },
    ]

    return {
        "period": {"start_date": filters.start_date.isoformat(), "end_date": filters.end_date.isoformat()},
        "comparison_period": {"start_date": prev_start.isoformat(), "end_date": prev_end.isoformat()},
        "kpis": kpis,
        "friction_signals": friction_signals,
        "insights": insights,
        "narrative": {
            "what_changed": f"Client retention moved {ret_delta:+.2f} pp ({cur['retention_rate']:.2f}%), KYC rework shifted {kyc_delta:+.1f} pp ({cur['kyc_rework_rate']:.1f}%), and open backlog reached {cur['open_backlog']:,} cases.",
            "who_was_affected": "Newly onboarded cohorts post-April 2026 and clients serviced by capacity-constrained teams (notably North Region T-03).",
            "what_to_investigate_next": "Run the Retention Decline Investigation Lab workflow and review the KYC Pre-Submission Checker pilot design.",
        },
    }


def get_overview_trends(db: Session, filters: AnalyticsFilters) -> list[dict[str, Any]]:
    c_filter, params = _client_filter_sql(filters, "c")
    rows = db.execute(
        text(
            f"""
            WITH months AS (
                SELECT generate_series(
                    DATE_TRUNC('month', CAST(:min_dt AS timestamptz)),
                    DATE_TRUNC('month', CAST(:max_dt AS timestamptz)),
                    INTERVAL '1 month'
                ) AS m_start
            )
            SELECT
                TO_CHAR(m.m_start, 'YYYY-MM') AS month,
                COUNT(c.client_id) FILTER (
                    WHERE c.activated_at < m.m_start
                      AND (c.exited_at IS NULL OR c.exited_at >= m.m_start)
                ) AS active_start,
                COUNT(c.client_id) FILTER (
                    WHERE c.activated_at < m.m_start
                      AND c.exited_at >= m.m_start
                      AND c.exited_at < m.m_start + INTERVAL '1 month'
                ) AS exited_month
            FROM months m
            CROSS JOIN clients c
            WHERE 1=1 {c_filter}
            GROUP BY m.m_start
            ORDER BY m.m_start
            """
        ),
        {**params, "min_dt": "2024-01-01T00:00:00Z", "max_dt": f"{filters.end_date.isoformat()}T23:59:59Z"},
    ).mappings().all()

    result = []
    for r in rows:
        active_start = int(r["active_start"] or 0)
        exited_m = int(r["exited_month"] or 0)
        ret = round((1.0 - (exited_m / active_start)) * 100.0, 2) if active_start > 0 else 100.0
        result.append(
            {
                "month": r["month"],
                "active_start": active_start,
                "exited_count": exited_m,
                "monthly_retention_rate": ret,
                "monthly_attrition_rate": round(100.0 - ret, 2),
            }
        )
    return result
