"""Client lifecycle & onboarding funnel analytics engine."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.analytics.kpi_engine import _client_filter_sql, _dt_range, _prev_window
from app.schemas.common import AnalyticsFilters

STAGE_ORDER = [
    "Prospect",
    "KYC",
    "Account Opening",
    "Funding",
    "First Advisor Meeting",
    "Portfolio Setup",
    "Ongoing Service",
]


def _compute_funnel_for_window(
    db: Session, start_d: date, end_d: date, filters: AnalyticsFilters
) -> dict[str, dict[str, Any]]:
    start_dt, end_dt = _dt_range(start_d, end_d)
    c_filter, params = _client_filter_sql(filters, "c")
    params.update({"start_dt": start_dt, "end_dt": end_dt})

    rows = db.execute(
        text(
            f"""
            SELECT
                e.stage,
                COUNT(DISTINCT e.client_id) AS entered_clients,
                COUNT(*) AS total_episodes,
                COUNT(*) FILTER (WHERE e.outcome = 'Completed') AS completed_count,
                COUNT(*) FILTER (WHERE e.outcome = 'Reopened') AS reopened_count,
                COUNT(*) FILTER (WHERE e.outcome = 'Cancelled') AS cancelled_count,
                COUNT(*) FILTER (WHERE e.outcome = 'In Progress') AS in_progress_count,
                COUNT(*) FILTER (
                    WHERE e.outcome = 'In Progress'
                      AND (:end_dt - e.entered_at) > INTERVAL '14 days'
                ) AS stalled_count,
                COUNT(*) FILTER (WHERE e.previous_episode_id IS NULL) AS initial_episodes,
                PERCENTILE_CONT(0.5) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (e.exited_at - e.entered_at)) / 86400.0
                ) FILTER (WHERE e.outcome = 'Completed' AND e.exited_at IS NOT NULL) AS median_days,
                PERCENTILE_CONT(0.9) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (e.exited_at - e.entered_at)) / 86400.0
                ) FILTER (WHERE e.outcome = 'Completed' AND e.exited_at IS NOT NULL) AS p90_days
            FROM journey_stage_episodes e
            JOIN clients c ON c.client_id = e.client_id
            WHERE e.entered_at BETWEEN :start_dt AND :end_dt
              {c_filter}
            GROUP BY e.stage
            """
        ),
        params,
    ).mappings().all()

    by_stage: dict[str, dict[str, Any]] = {}
    for r in rows:
        completed = int(r["completed_count"] or 0)
        cancelled = int(r["cancelled_count"] or 0)
        reopened = int(r["reopened_count"] or 0)
        in_prog = int(r["in_progress_count"] or 0)
        stalled = int(r["stalled_count"] or 0)
        initial = int(r["initial_episodes"] or 0)
        closed_denom = completed + cancelled
        conversion = round((completed / closed_denom) * 100.0, 2) if closed_denom > 0 else 100.0
        rework_rate = round((reopened / initial) * 100.0, 2) if initial > 0 else 0.0
        stall_rate = round((stalled / in_prog) * 100.0, 2) if in_prog > 0 else 0.0
        abandon_rate = round((cancelled / closed_denom) * 100.0, 2) if closed_denom > 0 else 0.0

        by_stage[r["stage"]] = {
            "stage": r["stage"],
            "entered_count": int(r["entered_clients"] or 0),
            "completed_count": completed,
            "in_progress_count": in_prog,
            "cancelled_count": cancelled,
            "conversion_rate": conversion,
            "median_days": round(float(r["median_days"] or 0.0), 1),
            "p90_days": round(float(r["p90_days"] or 0.0), 1),
            "stall_rate": stall_rate,
            "rework_rate": rework_rate,
            "abandonment_rate": abandon_rate,
        }
    return by_stage


def get_journey_funnel(db: Session, filters: AnalyticsFilters) -> dict[str, Any]:
    prev_start, prev_end = _prev_window(filters)
    cur_map = _compute_funnel_for_window(db, filters.start_date, filters.end_date, filters)
    prev_map = _compute_funnel_for_window(db, prev_start, prev_end, filters)

    stages = []
    for stg in STAGE_ORDER:
        c = cur_map.get(
            stg,
            {
                "stage": stg,
                "entered_count": 0,
                "completed_count": 0,
                "in_progress_count": 0,
                "cancelled_count": 0,
                "conversion_rate": 0.0,
                "median_days": 0.0,
                "p90_days": 0.0,
                "stall_rate": 0.0,
                "rework_rate": 0.0,
                "abandonment_rate": 0.0,
            },
        )
        p = prev_map.get(stg, {})
        c["prev_conversion_rate"] = p.get("conversion_rate", c["conversion_rate"])
        c["conversion_change_pp"] = round(c["conversion_rate"] - c["prev_conversion_rate"], 2)
        c["prev_median_days"] = p.get("median_days", c["median_days"])
        c["median_days_change"] = round(c["median_days"] - c["prev_median_days"], 1)
        c["prev_rework_rate"] = p.get("rework_rate", c["rework_rate"])
        c["rework_change_pp"] = round(c["rework_rate"] - c["prev_rework_rate"], 2)
        stages.append(c)

    process_changes = db.execute(
        text(
            "SELECT change_id, change_code, title, target_stage, effective_date, description FROM process_changes ORDER BY effective_date"
        )
    ).mappings().all()

    return {
        "period": {"start_date": filters.start_date.isoformat(), "end_date": filters.end_date.isoformat()},
        "comparison_period": {"start_date": prev_start.isoformat(), "end_date": prev_end.isoformat()},
        "stages": stages,
        "process_changes": [
            {
                "change_id": pc["change_id"],
                "change_code": pc["change_code"],
                "title": pc["title"],
                "target_stage": pc["target_stage"],
                "effective_date": pc["effective_date"].date().isoformat(),
                "description": pc["description"],
            }
            for pc in process_changes
        ],
    }


def get_stage_detail(db: Session, stage: str, filters: AnalyticsFilters) -> dict[str, Any]:
    start_dt, end_dt = _dt_range(filters.start_date, filters.end_date)
    c_filter, params = _client_filter_sql(filters, "c")
    params.update({"stage": stage, "start_dt": start_dt, "end_dt": end_dt})

    summary = _compute_funnel_for_window(db, filters.start_date, filters.end_date, filters).get(stage, {"stage": stage})

    # Rework reasons
    reasons = db.execute(
        text(
            f"""
            SELECT
                COALESCE(e.rework_reason, 'Unspecified') AS reason,
                COUNT(*) AS count
            FROM journey_stage_episodes e
            JOIN clients c ON c.client_id = e.client_id
            WHERE e.stage = :stage
              AND e.outcome = 'Reopened'
              AND e.entered_at BETWEEN :start_dt AND :end_dt
              {c_filter}
            GROUP BY 1
            ORDER BY 2 DESC
            """
        ),
        params,
    ).mappings().all()

    # Monthly trend for this stage
    monthly = db.execute(
        text(
            f"""
            SELECT
                TO_CHAR(DATE_TRUNC('month', e.entered_at), 'YYYY-MM') AS month,
                COUNT(*) FILTER (WHERE e.previous_episode_id IS NULL) AS initial_count,
                COUNT(*) FILTER (WHERE e.outcome = 'Reopened') AS reopened_count,
                PERCENTILE_CONT(0.5) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (e.exited_at - e.entered_at)) / 86400.0
                ) FILTER (WHERE e.outcome = 'Completed' AND e.exited_at IS NOT NULL) AS median_days,
                PERCENTILE_CONT(0.9) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (e.exited_at - e.entered_at)) / 86400.0
                ) FILTER (WHERE e.outcome = 'Completed' AND e.exited_at IS NOT NULL) AS p90_days
            FROM journey_stage_episodes e
            JOIN clients c ON c.client_id = e.client_id
            WHERE e.stage = :stage
              AND e.entered_at >= '2024-01-01T00:00:00Z'
              {c_filter}
            GROUP BY 1
            ORDER BY 1
            """
        ),
        params,
    ).mappings().all()

    # Segment breakdown
    by_segment = db.execute(
        text(
            f"""
            SELECT
                c.segment,
                COUNT(*) FILTER (WHERE e.previous_episode_id IS NULL) AS initial_count,
                COUNT(*) FILTER (WHERE e.outcome = 'Reopened') AS reopened_count,
                PERCENTILE_CONT(0.5) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (e.exited_at - e.entered_at)) / 86400.0
                ) FILTER (WHERE e.outcome = 'Completed' AND e.exited_at IS NOT NULL) AS median_days
            FROM journey_stage_episodes e
            JOIN clients c ON c.client_id = e.client_id
            WHERE e.stage = :stage
              AND e.entered_at BETWEEN :start_dt AND :end_dt
              {c_filter}
            GROUP BY c.segment
            ORDER BY c.segment
            """
        ),
        params,
    ).mappings().all()

    # Sample affected clients
    sample_episodes = db.execute(
        text(
            f"""
            SELECT
                e.episode_id,
                e.client_id,
                c.segment,
                c.asset_tier,
                e.entered_at,
                e.exited_at,
                e.outcome,
                e.rework_reason
            FROM journey_stage_episodes e
            JOIN clients c ON c.client_id = e.client_id
            WHERE e.stage = :stage
              AND e.entered_at BETWEEN :start_dt AND :end_dt
              {c_filter}
            ORDER BY CASE WHEN e.outcome = 'Reopened' THEN 0 ELSE 1 END, e.entered_at DESC
            LIMIT 15
            """
        ),
        params,
    ).mappings().all()

    return {
        "stage": stage,
        "summary": summary,
        "rework_reasons": [{"reason": r["reason"], "count": int(r["count"])} for r in reasons],
        "monthly_trend": [
            {
                "month": m["month"],
                "initial_count": int(m["initial_count"] or 0),
                "reopened_count": int(m["reopened_count"] or 0),
                "rework_rate": round(
                    (int(m["reopened_count"] or 0) / int(m["initial_count"])) * 100.0, 2
                )
                if int(m["initial_count"] or 0) > 0
                else 0.0,
                "median_days": round(float(m["median_days"] or 0.0), 1),
                "p90_days": round(float(m["p90_days"] or 0.0), 1),
            }
            for m in monthly
        ],
        "segment_breakdown": [
            {
                "segment": s["segment"],
                "initial_count": int(s["initial_count"] or 0),
                "rework_rate": round(
                    (int(s["reopened_count"] or 0) / int(s["initial_count"])) * 100.0, 2
                )
                if int(s["initial_count"] or 0) > 0
                else 0.0,
                "median_days": round(float(s["median_days"] or 0.0), 1),
            }
            for s in by_segment
        ],
        "sample_episodes": [
            {
                "episode_id": ep["episode_id"],
                "client_id": ep["client_id"],
                "segment": ep["segment"],
                "asset_tier": ep["asset_tier"],
                "entered_at": ep["entered_at"].isoformat(),
                "exited_at": ep["exited_at"].isoformat() if ep["exited_at"] else None,
                "outcome": ep["outcome"],
                "rework_reason": ep["rework_reason"],
            }
            for ep in sample_episodes
        ],
    }
