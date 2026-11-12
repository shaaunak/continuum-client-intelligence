"""Tableau-ready CSV extract generator."""

from __future__ import annotations

import csv
from io import StringIO

from sqlalchemy import text
from sqlalchemy.orm import Session


def generate_csv_export(db: Session, report_type: str) -> tuple[str, str]:
    """Return (filename, csv_content) for the requested Tableau-ready dataset."""
    queries = {
        "executive_monthly_metrics": (
            "executive_monthly_metrics.csv",
            """
            WITH months AS (
                SELECT generate_series('2024-01-01'::timestamptz, '2026-10-01'::timestamptz, INTERVAL '1 month') AS m_start
            )
            SELECT
                TO_CHAR(m.m_start, 'YYYY-MM') AS month,
                COUNT(c.client_id) FILTER (WHERE c.activated_at < m.m_start AND (c.exited_at IS NULL OR c.exited_at >= m.m_start)) AS active_start,
                COUNT(c.client_id) FILTER (WHERE c.activated_at < m.m_start AND c.exited_at >= m.m_start AND c.exited_at < m.m_start + INTERVAL '1 month') AS exited_month
            FROM months m
            CROSS JOIN clients c
            GROUP BY m.m_start
            ORDER BY m.m_start
            """,
        ),
        "journey_stage_metrics": (
            "journey_stage_metrics.csv",
            """
            SELECT
                stage,
                TO_CHAR(DATE_TRUNC('month', entered_at), 'YYYY-MM') AS entered_month,
                COUNT(*) AS total_episodes,
                COUNT(*) FILTER (WHERE outcome = 'Completed') AS completed_count,
                COUNT(*) FILTER (WHERE outcome = 'Reopened') AS reopened_count,
                ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (exited_at - entered_at))/86400.0) FILTER (WHERE outcome = 'Completed')::numeric, 2) AS median_days,
                ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (exited_at - entered_at))/86400.0) FILTER (WHERE outcome = 'Completed')::numeric, 2) AS p90_days
            FROM journey_stage_episodes
            GROUP BY 1, 2
            ORDER BY 2, 1
            """,
        ),
        "service_sla_metrics": (
            "service_sla_metrics.csv",
            """
            SELECT
                TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') AS month,
                assigned_team_id,
                request_category,
                COUNT(*) AS total_cases,
                COUNT(*) FILTER (WHERE first_response_breached = TRUE) AS first_response_breaches,
                COUNT(*) FILTER (WHERE resolution_breached = TRUE) AS resolution_breaches
            FROM service_cases
            GROUP BY 1, 2, 3
            ORDER BY 1, 2, 3
            """,
        ),
        "advisor_workload_metrics": (
            "advisor_workload_metrics.csv",
            """
            SELECT
                a.advisor_id,
                a.display_name,
                a.team_id,
                a.active,
                a.max_active_cases,
                COUNT(sc.case_id) FILTER (WHERE sc.status IN ('Open', 'In Progress')) AS open_cases,
                COUNT(sc.case_id) FILTER (WHERE sc.first_response_breached = TRUE) AS total_fr_breaches
            FROM advisors a
            LEFT JOIN service_cases sc ON sc.assigned_advisor_id = a.advisor_id
            GROUP BY a.advisor_id, a.display_name, a.team_id, a.active, a.max_active_cases
            ORDER BY a.team_id, a.advisor_id
            """,
        ),
        "complaint_category_metrics": (
            "complaint_category_metrics.csv",
            """
            SELECT
                TO_CHAR(DATE_TRUNC('month', submitted_at), 'YYYY-MM') AS month,
                category,
                severity,
                COUNT(*) AS complaint_count,
                COUNT(*) FILTER (WHERE reopened = TRUE) AS reopened_count
            FROM complaints
            GROUP BY 1, 2, 3
            ORDER BY 1, 2, 3
            """,
        ),
    }

    if report_type not in queries:
        raise ValueError(f"Unsupported export type: {report_type}")

    filename, sql = queries[report_type]
    rows = db.execute(text(sql)).mappings().all()

    buf = StringIO()
    if rows:
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    return filename, buf.getvalue()
