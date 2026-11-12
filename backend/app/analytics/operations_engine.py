"""Service operations, SLA, complaint, and fair advisor intelligence engine."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.analytics.business_hours import elapsed_business_hours
from app.analytics.kpi_engine import _client_filter_sql, _dt_range
from app.core.config import get_settings
from app.schemas.common import AnalyticsFilters


def _as_of_dt() -> datetime:
    settings = get_settings()
    return datetime.fromisoformat(f"{settings.AS_OF_DATE}T23:59:59+00:00")


def get_operations_workload(db: Session, filters: AnalyticsFilters) -> dict[str, Any]:
    as_of = _as_of_dt()
    start_dt, end_dt = _dt_range(filters.start_date, filters.end_date)
    c_filter, params = _client_filter_sql(filters, "c")
    team_clause = "AND sc.assigned_team_id = :team_id" if (filters.team_id and filters.team_id != "All") else ""
    params.update({"as_of": as_of, "start_dt": start_dt, "end_dt": end_dt})

    # 1. Team workload & capacity utilization (using active advisors' max_active_cases)
    teams = db.execute(
        text(
            f"""
            WITH team_cap AS (
                SELECT
                    t.team_id,
                    t.team_name,
                    t.region,
                    COUNT(a.advisor_id) FILTER (WHERE a.active = TRUE) AS active_advisors,
                    SUM(CASE WHEN a.active THEN a.max_active_cases ELSE 0 END) AS active_capacity
                FROM advisor_teams t
                LEFT JOIN advisors a ON a.team_id = t.team_id
                GROUP BY t.team_id, t.team_name, t.region
            ),
            team_cases AS (
                SELECT
                    sc.assigned_team_id AS team_id,
                    COUNT(*) FILTER (WHERE sc.status IN ('Open', 'In Progress')) AS open_cases,
                    COUNT(*) FILTER (
                        WHERE sc.status IN ('Open', 'In Progress')
                          AND EXTRACT(EPOCH FROM (:end_dt - sc.created_at)) / 86400.0 > 14
                    ) AS aged_15plus,
                    COUNT(*) FILTER (WHERE sc.created_at BETWEEN :start_dt AND :end_dt) AS intake_period,
                    COUNT(*) FILTER (WHERE sc.resolved_at BETWEEN :start_dt AND :end_dt) AS resolved_period
                FROM service_cases sc
                JOIN clients c ON c.client_id = sc.client_id
                WHERE 1=1 {c_filter} {team_clause}
                GROUP BY sc.assigned_team_id
            )
            SELECT
                tc.team_id,
                tc.team_name,
                tc.region,
                tc.active_advisors,
                tc.active_capacity,
                COALESCE(tca.open_cases, 0) AS open_cases,
                COALESCE(tca.aged_15plus, 0) AS aged_15plus,
                COALESCE(tca.intake_period, 0) AS intake_period,
                COALESCE(tca.resolved_period, 0) AS resolved_period
            FROM team_cap tc
            LEFT JOIN team_cases tca ON tca.team_id = tc.team_id
            ORDER BY tc.team_id
            """
        ),
        params,
    ).mappings().all()

    team_rows = []
    alerts = []
    for r in teams:
        cap = int(r["active_capacity"] or 0)
        open_c = int(r["open_cases"] or 0)
        util = round((open_c / cap) * 100.0, 1) if cap > 0 else None
        team_rows.append(
            {
                "team_id": r["team_id"],
                "team_name": r["team_name"],
                "region": r["region"],
                "active_advisors": int(r["active_advisors"] or 0),
                "active_capacity": cap,
                "open_cases": open_c,
                "utilization_pct": util,
                "aged_15plus": int(r["aged_15plus"] or 0),
                "intake_period": int(r["intake_period"] or 0),
                "resolved_period": int(r["resolved_period"] or 0),
            }
        )
        if util is not None and util >= 95.0:
            alerts.append(
                {
                    "severity": "risk" if util >= 105.0 else "warning",
                    "team_id": r["team_id"],
                    "title": f"{r['team_name']} at {util:.1f}% capacity utilization",
                    "detail": f"{open_c} open cases across {int(r['active_advisors'])} active advisors ({cap} capacity); {int(r['aged_15plus'])} aged 15+ days.",
                }
            )

    # 2. Backlog aging buckets
    aging_row = db.execute(
        text(
            f"""
            SELECT
                COUNT(*) FILTER (WHERE sc.status IN ('Open', 'In Progress')) AS total_open,
                COUNT(*) FILTER (
                    WHERE sc.status IN ('Open', 'In Progress')
                      AND EXTRACT(EPOCH FROM (:end_dt - sc.created_at)) / 86400.0 <= 2
                ) AS b_0_2,
                COUNT(*) FILTER (
                    WHERE sc.status IN ('Open', 'In Progress')
                      AND EXTRACT(EPOCH FROM (:end_dt - sc.created_at)) / 86400.0 > 2
                      AND EXTRACT(EPOCH FROM (:end_dt - sc.created_at)) / 86400.0 <= 7
                ) AS b_3_7,
                COUNT(*) FILTER (
                    WHERE sc.status IN ('Open', 'In Progress')
                      AND EXTRACT(EPOCH FROM (:end_dt - sc.created_at)) / 86400.0 > 7
                      AND EXTRACT(EPOCH FROM (:end_dt - sc.created_at)) / 86400.0 <= 14
                ) AS b_8_14,
                COUNT(*) FILTER (
                    WHERE sc.status IN ('Open', 'In Progress')
                      AND EXTRACT(EPOCH FROM (:end_dt - sc.created_at)) / 86400.0 > 14
                ) AS b_15_plus
            FROM service_cases sc
            JOIN clients c ON c.client_id = sc.client_id
            WHERE sc.created_at <= :end_dt {c_filter} {team_clause}
            """
        ),
        params,
    ).mappings().one()

    total_open = int(aging_row["total_open"] or 0)
    aging_buckets = []
    for label, key in [("0-2 days", "b_0_2"), ("3-7 days", "b_3_7"), ("8-14 days", "b_8_14"), ("15+ days", "b_15_plus")]:
        cnt = int(aging_row[key] or 0)
        aging_buckets.append(
            {
                "bucket": label,
                "count": cnt,
                "pct": round((cnt / total_open) * 100.0, 1) if total_open > 0 else 0.0,
            }
        )

    # 3. Monthly Intake vs Resolution
    monthly_flow = db.execute(
        text(
            f"""
            SELECT
                TO_CHAR(DATE_TRUNC('month', sc.created_at), 'YYYY-MM') AS month,
                COUNT(*) AS intake_count,
                COUNT(*) FILTER (WHERE sc.resolved_at IS NOT NULL) AS resolved_count
            FROM service_cases sc
            JOIN clients c ON c.client_id = sc.client_id
            WHERE sc.created_at >= '2024-01-01T00:00:00Z'
              AND sc.created_at <= :end_dt
              {c_filter} {team_clause}
            GROUP BY 1
            ORDER BY 1
            """
        ),
        params,
    ).mappings().all()

    return {
        "as_of_date": filters.end_date.isoformat(),
        "total_open_backlog": total_open,
        "capacity_assumption": "35 active cases per active advisor (documented operational baseline).",
        "teams": team_rows,
        "aging_buckets": aging_buckets,
        "monthly_flow": [
            {
                "month": m["month"],
                "intake_count": int(m["intake_count"]),
                "resolved_count": int(m["resolved_count"]),
            }
            for m in monthly_flow
        ],
        "alerts": alerts,
    }


def get_operations_sla(db: Session, filters: AnalyticsFilters) -> dict[str, Any]:
    start_dt, end_dt = _dt_range(filters.start_date, filters.end_date)
    c_filter, params = _client_filter_sql(filters, "c")
    team_clause = "AND sc.assigned_team_id = :team_id" if (filters.team_id and filters.team_id != "All") else ""
    params.update({"start_dt": start_dt, "end_dt": end_dt})

    summary = db.execute(
        text(
            f"""
            SELECT
                COUNT(*) FILTER (WHERE sc.first_response_due_at <= :end_dt) AS fr_due,
                COUNT(*) FILTER (
                    WHERE sc.first_response_due_at <= :end_dt
                      AND sc.first_response_breached = FALSE
                      AND sc.first_response_at IS NOT NULL
                ) AS fr_met,
                COUNT(*) FILTER (WHERE sc.resolution_due_at <= :end_dt) AS res_due,
                COUNT(*) FILTER (
                    WHERE sc.resolution_due_at <= :end_dt
                      AND sc.resolution_breached = FALSE
                      AND sc.resolved_at IS NOT NULL
                ) AS res_met,
                PERCENTILE_CONT(0.5) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (sc.first_response_at - sc.created_at)) / 3600.0
                ) FILTER (WHERE sc.first_response_at IS NOT NULL) AS p50_clock_hours,
                PERCENTILE_CONT(0.9) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (sc.first_response_at - sc.created_at)) / 3600.0
                ) FILTER (WHERE sc.first_response_at IS NOT NULL) AS p90_clock_hours
            FROM service_cases sc
            JOIN clients c ON c.client_id = sc.client_id
            WHERE sc.created_at BETWEEN :start_dt AND :end_dt
              {c_filter} {team_clause}
            """
        ),
        params,
    ).mappings().one()

    # Sample up to 800 responded cases to compute exact business-hours p50/p90
    bh_rows = db.execute(
        text(
            f"""
            SELECT sc.created_at, sc.first_response_at
            FROM service_cases sc
            JOIN clients c ON c.client_id = sc.client_id
            WHERE sc.created_at BETWEEN :start_dt AND :end_dt
              AND sc.first_response_at IS NOT NULL
              {c_filter} {team_clause}
            LIMIT 1000
            """
        ),
        params,
    ).mappings().all()

    bh_hours = sorted(elapsed_business_hours(r["created_at"], r["first_response_at"]) for r in bh_rows)
    p50_bh = round(bh_hours[len(bh_hours) // 2], 2) if bh_hours else 0.0
    p90_bh = round(bh_hours[int(len(bh_hours) * 0.9)], 2) if bh_hours else 0.0

    # By category
    by_cat = db.execute(
        text(
            f"""
            SELECT
                sc.request_category,
                COUNT(*) FILTER (WHERE sc.first_response_due_at <= :end_dt) AS fr_due,
                COUNT(*) FILTER (
                    WHERE sc.first_response_due_at <= :end_dt
                      AND sc.first_response_breached = FALSE
                      AND sc.first_response_at IS NOT NULL
                ) AS fr_met,
                COUNT(*) FILTER (WHERE sc.first_response_breached = TRUE) AS breaches
            FROM service_cases sc
            JOIN clients c ON c.client_id = sc.client_id
            WHERE sc.created_at BETWEEN :start_dt AND :end_dt
              {c_filter} {team_clause}
            GROUP BY sc.request_category
            ORDER BY breaches DESC
            """
        ),
        params,
    ).mappings().all()

    # Monthly SLA trend
    monthly_sla = db.execute(
        text(
            f"""
            SELECT
                TO_CHAR(DATE_TRUNC('month', sc.created_at), 'YYYY-MM') AS month,
                COUNT(*) FILTER (WHERE sc.first_response_due_at <= :end_dt) AS fr_due,
                COUNT(*) FILTER (
                    WHERE sc.first_response_due_at <= :end_dt
                      AND sc.first_response_breached = FALSE
                      AND sc.first_response_at IS NOT NULL
                ) AS fr_met,
                COUNT(*) FILTER (WHERE sc.first_response_breached = TRUE) AS fr_breaches
            FROM service_cases sc
            JOIN clients c ON c.client_id = sc.client_id
            WHERE sc.created_at >= '2024-01-01T00:00:00Z'
              AND sc.created_at <= :end_dt
              {c_filter} {team_clause}
            GROUP BY 1
            ORDER BY 1
            """
        ),
        params,
    ).mappings().all()

    fr_due = int(summary["fr_due"] or 0)
    fr_met = int(summary["fr_met"] or 0)
    res_due = int(summary["res_due"] or 0)
    res_met = int(summary["res_met"] or 0)

    return {
        "calendar_note": "SLA deadlines and business-hours response times use Mon-Fri 09:00-17:00 America/New_York.",
        "summary": {
            "first_response_sla_pct": round((fr_met / fr_due) * 100.0, 2) if fr_due > 0 else 100.0,
            "first_response_due": fr_due,
            "first_response_met": fr_met,
            "resolution_sla_pct": round((res_met / res_due) * 100.0, 2) if res_due > 0 else 100.0,
            "resolution_due": res_due,
            "resolution_met": res_met,
            "p50_business_hours": p50_bh,
            "p90_business_hours": p90_bh,
            "p50_clock_hours": round(float(summary["p50_clock_hours"] or 0.0), 1),
            "p90_clock_hours": round(float(summary["p90_clock_hours"] or 0.0), 1),
        },
        "by_category": [
            {
                "category": r["request_category"],
                "due_count": int(r["fr_due"] or 0),
                "met_count": int(r["fr_met"] or 0),
                "breach_count": int(r["breaches"] or 0),
                "attainment_pct": round((int(r["fr_met"] or 0) / int(r["fr_due"])) * 100.0, 1)
                if int(r["fr_due"] or 0) > 0
                else 100.0,
            }
            for r in by_cat
        ],
        "monthly_trend": [
            {
                "month": m["month"],
                "attainment_pct": round((int(m["fr_met"] or 0) / int(m["fr_due"])) * 100.0, 1)
                if int(m["fr_due"] or 0) > 0
                else 100.0,
                "breaches": int(m["fr_breaches"] or 0),
            }
            for m in monthly_sla
        ],
    }


def get_operations_complaints(
    db: Session, filters: AnalyticsFilters, category: str | None = None
) -> dict[str, Any]:
    start_dt, end_dt = _dt_range(filters.start_date, filters.end_date)
    c_filter, params = _client_filter_sql(filters, "c")
    team_clause = "AND cmp.assigned_team_id = :team_id" if (filters.team_id and filters.team_id != "All") else ""
    params.update({"start_dt": start_dt, "end_dt": end_dt})

    by_cat = db.execute(
        text(
            f"""
            SELECT
                cmp.category,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE cmp.reopened = TRUE) AS reopened,
                COUNT(*) FILTER (WHERE cmp.repeat_contact_flag = TRUE) AS repeat_contact,
                COUNT(*) FILTER (WHERE cmp.resolved_at IS NULL) AS unresolved,
                PERCENTILE_CONT(0.5) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (cmp.resolved_at - cmp.submitted_at)) / 86400.0
                ) FILTER (WHERE cmp.resolved_at IS NOT NULL) AS median_res_days
            FROM complaints cmp
            JOIN clients c ON c.client_id = cmp.client_id
            WHERE cmp.submitted_at BETWEEN :start_dt AND :end_dt
              {c_filter} {team_clause}
            GROUP BY cmp.category
            ORDER BY total DESC
            """
        ),
        params,
    ).mappings().all()

    total_all = sum(int(r["total"]) for r in by_cat)
    cum = 0
    pareto = []
    for r in by_cat:
        t = int(r["total"])
        cum += t
        pareto.append(
            {
                "category": r["category"],
                "count": t,
                "share_pct": round((t / total_all) * 100.0, 1) if total_all > 0 else 0.0,
                "cumulative_pct": round((cum / total_all) * 100.0, 1) if total_all > 0 else 0.0,
                "reopen_rate_pct": round((int(r["reopened"]) / t) * 100.0, 1) if t > 0 else 0.0,
                "repeat_contact_pct": round((int(r["repeat_contact"]) / t) * 100.0, 1) if t > 0 else 0.0,
                "unresolved": int(r["unresolved"]),
                "median_resolution_days": round(float(r["median_res_days"] or 0.0), 1),
            }
        )

    monthly = db.execute(
        text(
            f"""
            SELECT
                TO_CHAR(DATE_TRUNC('month', cmp.submitted_at), 'YYYY-MM') AS month,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE cmp.category = 'Transfer & Settlement') AS transfer_settlement
            FROM complaints cmp
            JOIN clients c ON c.client_id = cmp.client_id
            WHERE cmp.submitted_at >= '2024-01-01T00:00:00Z'
              AND cmp.submitted_at <= :end_dt
              {c_filter} {team_clause}
            GROUP BY 1
            ORDER BY 1
            """
        ),
        params,
    ).mappings().all()

    cat_clause = "AND cmp.category = :cmp_cat" if category else ""
    if category:
        params["cmp_cat"] = category

    recent_cases = db.execute(
        text(
            f"""
            SELECT
                cmp.complaint_id,
                cmp.client_id,
                cmp.case_id,
                cmp.category,
                cmp.severity,
                cmp.submitted_at,
                cmp.resolved_at,
                cmp.reopened,
                cmp.root_cause_process
            FROM complaints cmp
            JOIN clients c ON c.client_id = cmp.client_id
            WHERE cmp.submitted_at BETWEEN :start_dt AND :end_dt
              {c_filter} {team_clause} {cat_clause}
            ORDER BY cmp.submitted_at DESC
            LIMIT 25
            """
        ),
        params,
    ).mappings().all()

    return {
        "total_complaints": total_all,
        "pareto": pareto,
        "monthly_trend": [
            {
                "month": m["month"],
                "total": int(m["total"]),
                "transfer_settlement": int(m["transfer_settlement"]),
            }
            for m in monthly
        ],
        "recent_complaints": [
            {
                "complaint_id": rc["complaint_id"],
                "client_id": rc["client_id"],
                "case_id": rc["case_id"],
                "category": rc["category"],
                "severity": rc["severity"],
                "submitted_at": rc["submitted_at"].isoformat(),
                "resolved_at": rc["resolved_at"].isoformat() if rc["resolved_at"] else None,
                "reopened": rc["reopened"],
                "root_cause_process": rc["root_cause_process"],
            }
            for rc in recent_cases
        ],
    }


def get_advisor_intelligence(db: Session, filters: AnalyticsFilters) -> dict[str, Any]:
    start_dt, end_dt = _dt_range(filters.start_date, filters.end_date)
    params: dict[str, Any] = {"start_dt": start_dt, "end_dt": end_dt}
    team_clause = "AND a.team_id = :team_id" if (filters.team_id and filters.team_id != "All") else ""
    if filters.team_id and filters.team_id != "All":
        params["team_id"] = filters.team_id

    # Compute expected breach rate by complexity_level across all teams for Observed-vs-Expected adjustment
    exp_rows = db.execute(
        text(
            """
            SELECT
                complexity_level,
                COUNT(*) FILTER (WHERE first_response_due_at <= :end_dt) AS due_cnt,
                COUNT(*) FILTER (WHERE first_response_breached = TRUE) AS breach_cnt
            FROM service_cases
            WHERE created_at BETWEEN :start_dt AND :end_dt
            GROUP BY complexity_level
            """
        ),
        params,
    ).mappings().all()

    exp_rate_by_comp = {
        r["complexity_level"]: (int(r["breach_cnt"]) / int(r["due_cnt"])) if int(r["due_cnt"] or 0) > 0 else 0.1
        for r in exp_rows
    }

    rows = db.execute(
        text(
            f"""
            WITH adv_clients AS (
                SELECT advisor_id, COUNT(DISTINCT client_id) AS clients_managed
                FROM advisor_assignments
                WHERE is_primary = TRUE
                GROUP BY advisor_id
            ),
            adv_followups AS (
                SELECT
                    advisor_id,
                    COUNT(*) FILTER (WHERE due_at BETWEEN :start_dt AND :end_dt) AS fu_total,
                    COUNT(*) FILTER (WHERE due_at BETWEEN :start_dt AND :end_dt AND status = 'Completed') AS fu_done
                FROM follow_up_tasks
                GROUP BY advisor_id
            ),
            adv_cases AS (
                SELECT
                    assigned_advisor_id AS advisor_id,
                    COUNT(*) FILTER (WHERE status IN ('Open', 'In Progress')) AS open_requests,
                    COUNT(*) FILTER (WHERE resolved_at BETWEEN :start_dt AND :end_dt) AS cases_completed,
                    COUNT(*) FILTER (WHERE created_at BETWEEN :start_dt AND :end_dt AND first_response_due_at <= :end_dt) AS fr_due,
                    COUNT(*) FILTER (WHERE created_at BETWEEN :start_dt AND :end_dt AND first_response_due_at <= :end_dt AND first_response_breached = FALSE AND first_response_at IS NOT NULL) AS fr_met,
                    COUNT(*) FILTER (WHERE created_at BETWEEN :start_dt AND :end_dt AND first_response_breached = TRUE) AS fr_breached,
                    COUNT(*) FILTER (WHERE created_at BETWEEN :start_dt AND :end_dt AND complexity_level = 'High') AS high_comp_cases,
                    COUNT(*) FILTER (WHERE created_at BETWEEN :start_dt AND :end_dt AND complexity_level = 'Medium') AS med_comp_cases,
                    COUNT(*) FILTER (WHERE created_at BETWEEN :start_dt AND :end_dt AND complexity_level = 'Low') AS low_comp_cases,
                    COUNT(*) FILTER (WHERE created_at BETWEEN :start_dt AND :end_dt AND reopen_count > 0) AS reopened_cases,
                    PERCENTILE_CONT(0.9) WITHIN GROUP (
                        ORDER BY EXTRACT(EPOCH FROM (first_response_at - created_at)) / 3600.0
                    ) FILTER (WHERE created_at BETWEEN :start_dt AND :end_dt AND first_response_at IS NOT NULL) AS p90_resp_h
                FROM service_cases
                GROUP BY assigned_advisor_id
            )
            SELECT
                a.advisor_id,
                a.advisor_code,
                a.display_name,
                a.team_id,
                t.team_name,
                t.region,
                a.seniority_level,
                a.max_active_cases,
                a.active,
                COALESCE(ac.clients_managed, 0) AS clients_managed,
                COALESCE(cs.open_requests, 0) AS open_requests,
                COALESCE(cs.cases_completed, 0) AS cases_completed,
                COALESCE(cs.fr_due, 0) AS fr_due,
                COALESCE(cs.fr_met, 0) AS fr_met,
                COALESCE(cs.fr_breached, 0) AS fr_breached,
                COALESCE(cs.high_comp_cases, 0) AS high_comp_cases,
                COALESCE(cs.med_comp_cases, 0) AS med_comp_cases,
                COALESCE(cs.low_comp_cases, 0) AS low_comp_cases,
                COALESCE(cs.reopened_cases, 0) AS reopened_cases,
                COALESCE(cs.p90_resp_h, 0) AS p90_resp_h,
                COALESCE(fu.fu_total, 0) AS fu_total,
                COALESCE(fu.fu_done, 0) AS fu_done
            FROM advisors a
            JOIN advisor_teams t ON t.team_id = a.team_id
            LEFT JOIN adv_clients ac ON ac.advisor_id = a.advisor_id
            LEFT JOIN adv_cases cs ON cs.advisor_id = a.advisor_id
            LEFT JOIN adv_followups fu ON fu.advisor_id = a.advisor_id
            WHERE 1=1 {team_clause}
            ORDER BY t.team_id, a.advisor_id
            """
        ),
        params,
    ).mappings().all()

    advisors_out = []
    for r in rows:
        due = int(r["fr_due"] or 0)
        met = int(r["fr_met"] or 0)
        breached = int(r["fr_breached"] or 0)
        sla_pct = round((met / due) * 100.0, 1) if due > 0 else 100.0
        open_req = int(r["open_requests"] or 0)
        max_c = int(r["max_active_cases"] or 35)
        util_pct = round((open_req / max_c) * 100.0, 1) if r["active"] and max_c > 0 else None

        # Observed-vs-Expected (O/E) breach ratio adjusted for complexity mix
        total_period_cases = int(r["high_comp_cases"] or 0) + int(r["med_comp_cases"] or 0) + int(r["low_comp_cases"] or 0)
        expected_breaches = (
            int(r["high_comp_cases"] or 0) * exp_rate_by_comp.get("High", 0.1)
            + int(r["med_comp_cases"] or 0) * exp_rate_by_comp.get("Medium", 0.1)
            + int(r["low_comp_cases"] or 0) * exp_rate_by_comp.get("Low", 0.1)
        )
        oe_ratio = round(breached / expected_breaches, 2) if expected_breaches >= 3.0 else None

        fu_tot = int(r["fu_total"] or 0)
        fu_done = int(r["fu_done"] or 0)

        advisors_out.append(
            {
                "advisor_id": r["advisor_id"],
                "advisor_code": r["advisor_code"],
                "display_name": r["display_name"],
                "team_id": r["team_id"],
                "team_name": r["team_name"],
                "region": r["region"],
                "seniority_level": r["seniority_level"],
                "active": r["active"],
                "clients_managed": int(r["clients_managed"]),
                "open_requests": open_req,
                "cases_completed": int(r["cases_completed"]),
                "high_complexity_share_pct": round((int(r["high_comp_cases"]) / total_period_cases) * 100.0, 1)
                if total_period_cases > 0
                else 0.0,
                "sla_attainment_pct": sla_pct,
                "p90_response_hours": round(float(r["p90_resp_h"] or 0.0), 1),
                "followup_completion_pct": round((fu_done / fu_tot) * 100.0, 1) if fu_tot > 0 else 100.0,
                "reopen_rate_pct": round((int(r["reopened_cases"]) / max(1, int(r["cases_completed"]))) * 100.0, 1),
                "utilization_pct": util_pct,
                "oe_breach_ratio": oe_ratio,
                "support_needed": bool(util_pct is not None and util_pct >= 95.0),
            }
        )

    return {
        "fairness_note": (
            "Observed-vs-Expected (O/E) breach ratio adjusts for case complexity mix. "
            "Values > 1.0 indicate more breaches than expected given complexity; suppressed when expected breaches < 3. "
            "High utilization reflects team staffing pressure rather than individual advisor quality."
        ),
        "advisors": advisors_out,
    }


def get_advisor_detail(db: Session, advisor_id: str) -> dict[str, Any] | None:
    adv = db.execute(
        text(
            """
            SELECT a.*, t.team_name, t.region
            FROM advisors a
            JOIN advisor_teams t ON t.team_id = a.team_id
            WHERE a.advisor_id = :advisor_id
            """
        ),
        {"advisor_id": advisor_id},
    ).mappings().first()
    if not adv:
        return None

    case_dist = db.execute(
        text(
            """
            SELECT request_category, COUNT(*) AS count
            FROM service_cases
            WHERE assigned_advisor_id = :advisor_id
            GROUP BY request_category
            ORDER BY count DESC
            """
        ),
        {"advisor_id": advisor_id},
    ).mappings().all()

    monthly_resp = db.execute(
        text(
            """
            SELECT
                TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') AS month,
                COUNT(*) AS cases_created,
                COUNT(*) FILTER (WHERE first_response_breached = TRUE) AS breaches
            FROM service_cases
            WHERE assigned_advisor_id = :advisor_id
              AND created_at >= '2025-01-01T00:00:00Z'
            GROUP BY 1
            ORDER BY 1
            """
        ),
        {"advisor_id": advisor_id},
    ).mappings().all()

    return {
        "advisor": {
            "advisor_id": adv["advisor_id"],
            "advisor_code": adv["advisor_code"],
            "display_name": adv["display_name"],
            "team_id": adv["team_id"],
            "team_name": adv["team_name"],
            "region": adv["region"],
            "seniority_level": adv["seniority_level"],
            "active": adv["active"],
            "max_active_cases": adv["max_active_cases"],
        },
        "case_type_distribution": [
            {"category": r["request_category"], "count": int(r["count"])} for r in case_dist
        ],
        "monthly_workload": [
            {"month": m["month"], "cases_created": int(m["cases_created"]), "breaches": int(m["breaches"])}
            for m in monthly_resp
        ],
    }
